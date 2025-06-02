import threading
from typing import Literal, Callable
from .rf2_info import RF2Info
from .remote_rf2_info import RemoteRF2Info
from .rf2_websocket import RF2WebSocket
import time
import logging
try:
    from pyRfactor2SharedMemory.rF2MMap import MAX_VEHICLES
except ImportError:
    import sys
    sys.path.append(".")
    from pyRfactor2SharedMemory.rF2MMap import MAX_VEHICLES
from tinypedal.hook import on_role_change_hook
    

logger = logging.getLogger(__name__)

class RF2Syncer:
    def __init__(self, *,
                 websocket_uri: str | None = None,
                 session_name: str | None = None,
                 connect_to_remote: bool = False,
                 on_role_change: Callable[[], None] | None = None):
        self._lock = threading.Lock()
        self._uri = websocket_uri
        self._session_name = session_name

        self._local = RF2Info()
        self._local.setMode(0)
        self._local.start()

        self._remote = None
        self._ws_sender = None
        self._on_role_change = on_role_change

        if connect_to_remote and websocket_uri and session_name:
            for _ in range(20):
                if self._local.playerIndex != -1:
                    break
                time.sleep(0.1)

            index = self._local.playerIndex
            driving = False

            if 0 <= index < MAX_VEHICLES:
                try:
                    driving = self._local.isDriving(index)
                except Exception as e:
                    logger.warning(f"Could not determine driving state: {e}")

            if driving:
                logger.info(f"Connecting as sender, driving:{driving}")
                self._ws_sender = RF2WebSocket(
                    uri=websocket_uri,
                    session_name=session_name,
                    role="sender",
                    data_provider=self._local
                )
                self._ws_sender.start()
            else:
                logger.info(f"Connecting as receiver, driving:{driving}")
                self._remote = RemoteRF2Info(websocket_uri, session_name)

            self._monitor_running = True
            self._monitor_thread = threading.Thread(target=self._monitor_role_switch, daemon=True)
            self._monitor_thread.start()

    def _monitor_role_switch(self):
        last_state = None
        while self._monitor_running:
            index = self._local.playerIndex
            driving = False

            if 0 <= index < MAX_VEHICLES:
                try:
                    driving = self._local.isDriving(index)
                except Exception:
                    pass

            if driving != last_state:
                last_state = driving

                if driving:
                    logger.info("Switched to driving — starting sender")
                    if self._remote:
                        self._remote.stop()
                        self._remote = None
                    if not self._ws_sender:
                        self._ws_sender = RF2WebSocket(
                            uri=self._uri,
                            session_name=self._session_name,
                            role="sender",
                            data_provider=self._local
                        )
                        self._ws_sender.start()
                else:
                    logger.info("Switched to spectating — starting receiver")
                    if self._ws_sender:
                        self._ws_sender.stop()
                        self._ws_sender = None
                    if not self._remote:
                        self._remote = RemoteRF2Info(self._uri, self._session_name)

                if self._on_role_change:
                    logger.info("Triggering API restart due to role switch")
                    self._on_role_change()

            time.sleep(1.0)

    def get_data(self, source: Literal["local", "remote"] = "local") -> dict:
        if source == "remote" and self._remote:
            return {
                "scor": self._remote.rf2ScorVeh(),
                "tele": self._remote.rf2TeleVeh(),
                "ext": self._remote.rf2Ext,
                "ffb": self._remote.rf2Ffb,
            }
        logger.info(self._local.rf2Ext)
        return {
            "scor": self._local.rf2ScorVeh(),
            "tele": self._local.rf2TeleVeh(),
            "ext": self._local.rf2Ext,
            "ffb": self._local.rf2Ffb,
        }

    def rf2ScorVeh(self, index: int | None = None):
        return self._remote.rf2ScorVeh(index) if self._remote else self._local.rf2ScorVeh(index)

    def rf2TeleVeh(self, index: int | None = None):
        return self._remote.rf2TeleVeh(index) if self._remote else self._local.rf2TeleVeh(index)

    @property
    def rf2ScorInfo(self):
        return self._remote.rf2ScorInfo if self._remote else self._local.rf2ScorInfo

    @property
    def rf2Ext(self):
        return self._remote.rf2Ext if self._remote else self._local.rf2Ext

    @property
    def rf2Ffb(self):
        return self._remote.rf2Ffb if self._remote else self._local.rf2Ffb

    @property
    def playerIndex(self):
        return 0 if self._remote else self._local.playerIndex

    def isPlayer(self, index: int):
        return self._remote.isPlayer(index) if self._remote else self._local.isPlayer(index)

    @property
    def isPaused(self):
        return self._remote.isPaused if self._remote else self._local.isPaused

    def stop(self):
        self._local.stop()
        if self._ws_sender:
            self._ws_sender.stop()
            if self._ws_sender._thread.is_alive():
                self._ws_sender._thread.join(timeout=2)
        if self._remote:
            self._remote.stop()

    @property
    def _ws_client(self):
        return self._ws_sender or (self._remote._ws_client if self._remote else None)

def get_rf2_info(cfg) -> RF2Syncer:
    api_cfg = cfg.shared_memory_api

    return RF2Syncer(
        websocket_uri=api_cfg.get("websocket_uri"),
        session_name=api_cfg.get("websocket_session"),
        connect_to_remote=api_cfg.get("connect_to_remote", False),
        on_role_change=on_role_change_hook
    )
