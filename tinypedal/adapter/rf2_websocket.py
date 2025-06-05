import asyncio
import json
import zlib
import struct
import threading
import logging
import contextlib
import httpx
import websockets
from typing import Callable
from ..setting import cfg

logger = logging.getLogger(__name__)

TYPE_IDS = {
    "scor": 0x01,
    "tele": 0x02,
    "ext":  0x03,
    "ffb":  0x04,
}

GET_PIT_MENU_URL = "http://localhost:6397/rest/garage/PitMenu/receivePitMenu"
POST_PIT_MENU_URL = "http://localhost:6397/rest/garage/PitMenu/loadPitMenu"


class RF2WebSocket:
    def __init__(self, uri: str, session_name: str, role: str, data_provider=None, data_receiver=None):
        if not uri.startswith("ws://") and not uri.startswith("wss://"):
            uri = f"wss://{uri}"
        elif uri.startswith("ws://"):
            uri = uri.replace("ws://", "wss://", 1)
        

        self._uri = uri 
        self._session_name = session_name
        self._role = role
        self._data_provider = data_provider
        self._data_receiver = data_receiver
        self._running = True
        self._loop = None
        self._ws = None
        self._thread = threading.Thread(target=self._start_loop, daemon=True)
        self._callbacks: dict[str, Callable[[dict], None]] = {}
        self._pending_requests: dict[str, Callable[[dict], None]] = {}
        

    def start(self):
        self._thread.start()

    def stop(self):
        self._running = False
        if self._loop and self._loop.is_running():
            def stopper():
                for task in asyncio.all_tasks(loop=self._loop):
                    task.cancel()
            self._loop.call_soon_threadsafe(stopper)

    def join(self):
        if self._thread.is_alive():
            self._thread.join(timeout=3)

    def register_callback(self, msg_type: str, callback: Callable[[dict], None]):
        self._callbacks[msg_type] = callback

    def send_request(self, request_type: str, payload: dict | None, callback: Callable[[dict], None], response_type: str = None):
        # Use response_type if provided, else fallback to request_type
        key = response_type if response_type else request_type
        self._pending_requests[key] = callback
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(
                self._send_json({"type": request_type, **(payload or {})}),
                self._loop
            )
        else:
            logger.warning("WebSocket loop is not running — cannot send request")

    def request_session_list(self, callback):
        self.send_request("list_sessions", None, callback, response_type="session_list")


    def _start_loop(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        try:
            self._loop.run_until_complete(self._run())
        except asyncio.CancelledError:
            pass
        finally:
            with contextlib.suppress(Exception):
                self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    async def _run(self, max_retries=5):
        retry_count = 0
        backoff = 1

        while retry_count < max_retries or max_retries == 0:
            logger.info(f"Key: {cfg.auth_key}")
            try:
                if not cfg.auth_key:
                    logger.error("❌ No auth key configured — cannot initiate WebSocket connection")
                    return
                async with websockets.connect(self._uri) as ws:
                    self._ws = ws
                    handshake = json.dumps({
                                                "session": self._session_name,
                                                "role": self._role,
                                                "activation_key": cfg.auth_key  # <- uses the updated config value
                                            })
                    await ws.send(handshake)

                    retry_count = 0
                    backoff = 1

                    tasks = [self._recv_loop(ws)]
                    if self._role == "sender":
                        tasks.append(self._send_loop(ws))

                    await asyncio.gather(*tasks)

            except Exception as e:
                retry_count += 1
                logger.warning(f"WebSocket {self._role} connection failed (attempt {retry_count}): {e}")
                if retry_count >= max_retries:
                    logger.error("Max retry attempts reached, giving up.")
                    break
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
            finally:
                self._ws = None

    async def _send_loop(self, ws):
        ws_interval = cfg.websocket_interval
        
        while self._running:
            try:
                if self._data_provider and self._data_provider.isPaused:
                    await asyncio.sleep(ws_interval)
                    continue

                frames = []
                for key in TYPE_IDS:
                    raw_bytes = bytes(getattr(self._data_provider, f"_{key}").data)
                    compressed = zlib.compress(raw_bytes)
                    frame = struct.pack("!BI", TYPE_IDS[key], len(compressed)) + compressed
                    frames.append(frame)

                await ws.send(b"".join(frames))
                await asyncio.sleep(ws_interval)
            except Exception as e:
                logger.error(f"Send loop error: {e}")
                break

    async def _recv_loop(self, ws):
        while self._running:
            try:
                msg = await ws.recv()

                if isinstance(msg, str):
                    logger.debug(f"📩 Text message received: {msg}")
                    await self._handle_json_message(msg)
                    continue

                offset = 0
                parts = []
                while offset < len(msg):
                    if offset + 5 > len(msg):
                        raise ValueError("Invalid header")
                    type_id = msg[offset]
                    length = struct.unpack("!I", msg[offset + 1:offset + 5])[0]
                    offset += 5
                    compressed = msg[offset:offset + length]
                    decompressed = zlib.decompress(compressed)
                    parts.append((type_id, decompressed))
                    offset += length

                self._apply_data(parts)

            except Exception as e:
                logger.warning(f"Receive loop error: {e}")
                break

    async def _handle_json_message(self, msg: str):
        try:
            data = json.loads(msg)
            msg_type = data.get("type")
            logger.info(f"✅ Received JSON message: {msg_type}")
            logger.info(f"Raw JSON message received: {msg!r}")

            # Handle session_list messages explicitly
            if msg_type == "session_list":
                sessions = data.get("sessions", [])
                if isinstance(sessions, list):
                    logger.info(f"Session list received with {len(sessions)} sessions:")
                    for session in sessions:
                        if isinstance(session, dict):
                            logger.info(f"  - Name: {session.get('name')}, Sender: {session.get('sender')}, Receivers: {session.get('receivers')}")
                        else:
                            logger.warning(f"Invalid session entry (not a dict): {session}")
                else:
                    logger.warning(f"Invalid sessions data (not a list): {sessions}")

                callback = self._pending_requests.pop("session_list", None)
                if callback:
                    logger.info(f"✅ Dispatching one-time callback for type: session_list")
                    callback(sessions)  # <-- pass the list here, not the whole dict
                else:
                    logger.warning("⚠ No one-time callback registered for 'session_list'")

                return

            if msg_type == "fetch_pit_menu" and self._role == "sender":
                logger.info("Fetching pit menu from local API...")
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(GET_PIT_MENU_URL, timeout=5)
                        response.raise_for_status()
                        payload = {
                            "type": "pit_menu_data",
                            "result": response.json()
                        }
                        await self._send_json(payload)
                    except Exception as e:
                        logger.error(f"Failed to fetch pit menu: {e}")
                return

            if msg_type == "send_pit_menu" and self._role == "sender":
                logger.info("Posting new pit menu to local API...")
                json_payload = data.get("payload")
                async with httpx.AsyncClient() as client:
                    try:
                        await client.post(POST_PIT_MENU_URL, json=json_payload, timeout=5)
                    except Exception as e:
                        logger.error(f"Failed to post pit menu: {e}")
                return

            # Dispatch one-time request callback
            callback = self._pending_requests.pop(msg_type, None)
            if callback:
                logger.info(f"✅ Dispatching one-time callback for type: {msg_type}")
                callback(data)
                return

            '''# Dispatch persistent callback
            callback = self._callbacks.get(msg_type)
            if callback:
                logger.info(f"📌 Dispatching persistent callback for type: {msg_type}")
                callback(data)
            else:
                logger.warning(f"⚠ No callback registered for type: {msg_type}")'''

        except Exception as e:
            logger.error(f"Invalid JSON message received: {e}")

    def _apply_data(self, parts):
        for type_id, data in parts:
            if self._data_receiver:
                self._data_receiver.apply_segment_data(type_id, data)

    async def _send_json(self, payload: dict):
        try:
            if self._ws:
                message = json.dumps(payload)
                logger.info(f"⬆ Sending JSON to server: {message}")
                await self._ws.send(message)
            else:
                logger.warning("❌ Cannot send JSON: self._ws is None")
        except Exception as e:
            logger.error(f"Failed to send JSON message: {e}")
