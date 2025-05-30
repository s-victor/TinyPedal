#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
#
#  This file is part of TinyPedal.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
rF2 API connector
"""

from __future__ import annotations

import logging
import threading
from copy import copy
from time import monotonic, sleep
from typing import Sequence
import websockets
import asyncio
import json
import ctypes
import zlib
import struct

logger = logging.getLogger(__name__)

try:
    from pyRfactor2SharedMemory.rF2MMap import (
        INVALID_INDEX,
        MAX_VEHICLES,
        MMapControl,
        rF2data,
    )
except ImportError:
    import sys
    sys.path.append(".")
    from pyRfactor2SharedMemory.rF2MMap import (
        INVALID_INDEX,
        MAX_VEHICLES,
        MMapControl,
        rF2data,
    )

TYPE_IDS = {
    "scor": 0x01,
    "tele": 0x02,
    "ext":  0x03,
    "ffb":  0x04,
}


def local_scoring_index(scor_veh: Sequence[rF2data.rF2VehicleScoring]) -> int:
    """Find local player scoring index

    Args:
        scor_veh: scoring mVehicles array.
    """
    for scor_idx, veh_info in enumerate(scor_veh):
        if veh_info.mIsPlayer:
            return scor_idx
    return INVALID_INDEX


class MMapDataSet:
    """Create mmap data set"""

    __slots__ = (
        "scor",
        "tele",
        "ext",
        "ffb",
    )

    def __init__(self) -> None:
        self.scor = MMapControl(rF2data.rFactor2Constants.MM_SCORING_FILE_NAME, rF2data.rF2Scoring)
        self.tele = MMapControl(rF2data.rFactor2Constants.MM_TELEMETRY_FILE_NAME, rF2data.rF2Telemetry)
        self.ext = MMapControl(rF2data.rFactor2Constants.MM_EXTENDED_FILE_NAME, rF2data.rF2Extended)
        self.ffb = MMapControl(rF2data.rFactor2Constants.MM_FORCE_FEEDBACK_FILE_NAME, rF2data.rF2ForceFeedback)

    def __del__(self):
        logger.info("sharedmemory: GC: MMapDataSet")

    def create_mmap(self, access_mode: int, rf2_pid: str) -> None:
        """Create mmap instance

        Args:
            access_mode: 0 = copy access, 1 = direct access.
            rf2_pid: rF2 Process ID for accessing server data.
        """
        self.scor.create(access_mode, rf2_pid)
        self.tele.create(access_mode, rf2_pid)
        self.ext.create(1, rf2_pid)
        self.ffb.create(1, rf2_pid)

    def close_mmap(self) -> None:
        """Close mmap instance"""
        self.scor.close()
        self.tele.close()
        self.ext.close()
        self.ffb.close()

    def update_mmap(self) -> None:
        """Update mmap data"""
        self.scor.update()
        self.tele.update()


class SyncData:
    """Synchronize data with player ID

    Attributes:
        dataset: mmap data set.
        paused: Data update state (boolean).
        override_player_index: Player index override state (boolean).
        player_scor_index: Local player scoring index.
        player_scor: Local player scoring data.
        player_tele: Local player telemetry data.
    """

    __slots__ = (
        "_updating",
        "_update_thread",
        "_event",
        "_tele_indexes",
        "paused",
        "override_player_index",
        "player_scor_index",
        "player_scor",
        "player_tele",
        "dataset",
    )

    def __init__(self) -> None:
        self._updating = False
        self._update_thread = None
        self._event = threading.Event()
        self._tele_indexes = {_index: _index for _index in range(128)}

        self.paused = False
        self.override_player_index = False
        self.player_scor_index = INVALID_INDEX
        self.player_scor = None
        self.player_tele = None
        self.dataset = MMapDataSet()

    def __del__(self):
        logger.info("sharedmemory: GC: SyncData")

    def __sync_player_data(self) -> bool:
        """Sync local player data

        Returns:
            False, if no valid player scoring index found.
            True, set player data.
        """
        if not self.override_player_index:
            # Update scoring index
            scor_idx = local_scoring_index(self.dataset.scor.data.mVehicles)
            if scor_idx == INVALID_INDEX:
                return False  # index not found, not synced
            self.player_scor_index = scor_idx
        # Set player data
        self.player_scor = self.dataset.scor.data.mVehicles[self.player_scor_index]
        self.player_tele = self.dataset.tele.data.mVehicles[self.sync_tele_index(self.player_scor_index)]
        return True  # found index, synced

    @staticmethod
    def __update_tele_indexes(tele_data: rF2data.rF2Telemetry, tele_indexes: dict) -> None:
        """Update telemetry player index dictionary for quick reference

        Telemetry index can be different from scoring index.
        Use mID matching to match telemetry index.

        Args:
            tele_data: Telemetry data.
            tele_indexes: Telemetry mID:index reference dictionary.
        """
        for tele_idx, veh_info in zip(range(tele_data.mNumVehicles), tele_data.mVehicles):
            tele_indexes[veh_info.mID] = tele_idx

    def sync_tele_index(self, scor_idx: int) -> int:
        """Sync telemetry index

        Use scoring index to find scoring mID,
        then match with telemetry mID in reference dictionary
        to find telemetry index.

        Args:
            scor_idx: Player scoring index.

        Returns:
            Player telemetry index.
        """
        return self._tele_indexes.get(
            self.dataset.scor.data.mVehicles[scor_idx].mID, INVALID_INDEX)

    def start(self, access_mode: int, rf2_pid: str) -> None:
        """Update & sync mmap data copy in separate thread

        Args:
            access_mode: 0 = copy access, 1 = direct access.
            rf2_pid: rF2 Process ID for accessing server data.
        """
        if self._updating:
            logger.warning("sharedmemory: UPDATING: already started")
        else:
            self._updating = True
            # Initialize mmap data
            self.dataset.create_mmap(access_mode, rf2_pid)
            self.__update_tele_indexes(self.dataset.tele.data, self._tele_indexes)
            if not self.__sync_player_data():
                self.player_scor = self.dataset.scor.data.mVehicles[INVALID_INDEX]
                self.player_tele = self.dataset.tele.data.mVehicles[INVALID_INDEX]
            # Setup updating thread
            self._event.clear()
            self._update_thread = threading.Thread(target=self.__update, daemon=True)
            self._update_thread.start()
            logger.info("sharedmemory: UPDATING: thread started")
            logger.info("sharedmemory: player index override: %s", self.override_player_index)
            logger.info("sharedmemory: server process ID: %s", rf2_pid if rf2_pid else "DISABLED")

    def stop(self) -> None:
        """Join and stop updating thread, close mmap"""
        if self._updating:
            self._event.set()
            self._updating = False
            self._update_thread.join()
            # Make final copy before close, otherwise mmap won't close if using direct access
            self.player_scor = copy(self.player_scor)
            self.player_tele = copy(self.player_tele)
            self.dataset.close_mmap()
        else:
            logger.warning("sharedmemory: UPDATING: already stopped")

    def __update(self) -> None:
        """Update synced player data"""
        self.paused = False  # make sure initial pause state is false
        _event_wait = self._event.wait
        freezed_version = 0  # store freezed update version number
        last_version_update = 0  # store last update version number
        last_update_time = 0.0
        data_freezed = True  # whether data is freezed
        reset_counter = 0
        update_delay = 0.5  # longer delay while inactive

        while not _event_wait(update_delay):
            self.dataset.update_mmap()
            self.__update_tele_indexes(self.dataset.tele.data, self._tele_indexes)
            # Update player data & index
            if not data_freezed:
                # Get player data
                data_synced = self.__sync_player_data()
                # Pause if local player index no longer exists, 5 tries
                if data_synced:
                    reset_counter = 0
                    self.paused = False
                elif reset_counter < 6:
                    reset_counter += 1
                    if reset_counter == 5:
                        self.paused = True
                        logger.info("sharedmemory: UPDATING: player data paused")

            version_update = self.dataset.scor.data.mVersionUpdateEnd
            if last_version_update != version_update:
                last_version_update = version_update
                last_update_time = monotonic()

            if data_freezed:
                # Check while IN freeze state
                if freezed_version != last_version_update:
                    update_delay = 0.01
                    self.paused = data_freezed = False
                    logger.info(
                        "sharedmemory: UPDATING: resumed, data version %s",
                        last_version_update,
                    )
            # Check while NOT IN freeze state
            # Set freeze state if data stopped updating after 2s
            elif monotonic() - last_update_time > 2:
                update_delay = 0.5
                self.paused = data_freezed = True
                freezed_version = last_version_update
                logger.info(
                    "sharedmemory: UPDATING: paused, data version %s",
                    freezed_version,
                )

        logger.info("sharedmemory: UPDATING: thread stopped")

class SwitcherRF2Info:
    def __init__(self, cfg):
        self.cfg = cfg
        self.ws_uri = cfg.shared_memory_api.get("websocket_uri")
        self.session_name = cfg.shared_memory_api.get("websocket_session")
        self._is_remote = cfg.shared_memory_api.get("use_remote_memory")

        self._rf2 = None
        self._monitor_thread = None
        self._stop_monitor = threading.Event()

        self._start_info()

        # Only start monitor thread if switching behavior is needed
        if self.cfg.shared_memory_api.get("send_to_remote") or self._is_remote:
            self.start_monitoring()

    def _start_info(self):
        if self._rf2:
            self._rf2.stop()

        if self._is_remote:
            logger.info("Starting RemoteRF2Info")
            self._rf2 = RemoteRF2Info(self.ws_uri, self.session_name)
        else:
            logger.info("Starting RF2Info")
            self._rf2 = RF2Info()
            self._rf2.setMode(0)
            self._rf2.start()
            if self.cfg.shared_memory_api.get("send_to_remote"):
                self._rf2.start_sender(self.ws_uri, self.session_name)

    def switch_mode(self, use_remote: bool):
        if use_remote != self._is_remote:
            logger.info(f"SwitcherRF2Info: switching to {'remote' if use_remote else 'local'} mode")
            self._is_remote = use_remote
            self._start_info()

    def start_monitoring(self, interval=2):
        if self._monitor_thread and self._monitor_thread.is_alive():
            return  # Already running

        def monitor_loop():
            while not self._stop_monitor.is_set():
                try:
                    sleep(interval)
                    if hasattr(self._rf2, "isDriving"):
                        is_driving = self._rf2.isDriving
                        # Switch to remote if not driving, local if driving
                        self.switch_mode(not is_driving)
                except Exception as e:
                    logger.exception(f"[SwitcherRF2Info] Monitor thread failed: {e}")

        logger.info("Starting SwitcherRF2Info monitor thread")
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self):
        self._stop_monitor.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)

    def stop(self):
        self.stop_monitoring()
        if self._rf2:
            self._rf2.stop()

    def __getattr__(self, name):
        return getattr(self._rf2, name)

    
class RF2Info:
    """RF2 shared memory data output"""

    __slots__ = (
        "_sync",
        "_access_mode",
        "_rf2_pid",
        "_scor",
        "_tele",
        "_ext",
        "_ffb",
    )

    def __init__(self) -> None:
        self._sync = SyncData()
        self._access_mode = 0
        self._rf2_pid = ""
        # Assign mmap instance
        self._scor = self._sync.dataset.scor
        self._tele = self._sync.dataset.tele
        self._ext = self._sync.dataset.ext
        self._ffb = self._sync.dataset.ffb

    def __del__(self):
        logger.info("sharedmemory: GC: RF2SM")

    def start(self) -> None:
        """Start data updating thread"""
        self._sync.start(self._access_mode, self._rf2_pid)

    def stop(self) -> None:
        """Stop data updating thread"""
        self._sync.stop()

    def setPID(self, pid: str = "") -> None:
        """Set rF2 process ID for connecting to server data"""
        self._rf2_pid = str(pid)

    def setMode(self, mode: int = 0) -> None:
        """Set rF2 mmap access mode

        Args:
            mode: 0 = copy access, 1 = direct access
        """
        self._access_mode = mode

    def setPlayerOverride(self, state: bool = False) -> None:
        """Enable player index override state"""
        self._sync.override_player_index = state

    def setPlayerIndex(self, index: int = INVALID_INDEX) -> None:
        """Manual override player index"""
        self._sync.player_scor_index = min(max(index, INVALID_INDEX), MAX_VEHICLES - 1)

    @property
    def rf2ScorInfo(self) -> rF2data.rF2ScoringInfo:
        """rF2 scoring info data"""
        return self._scor.data.mScoringInfo

    def rf2ScorVeh(self, index: int | None = None) -> rF2data.rF2VehicleScoring:
        """rF2 scoring vehicle data

        Specify index for specific player.

        Args:
            index: None for local player.
        """
        if index is None:
            return self._sync.player_scor
        return self._scor.data.mVehicles[index]

    def rf2TeleVeh(self, index: int | None = None) -> rF2data.rF2VehicleTelemetry:
        """rF2 telemetry vehicle data

        Specify index for specific player.

        Args:
            index: None for local player.
        """
        if index is None:
            return self._sync.player_tele
        return self._tele.data.mVehicles[self._sync.sync_tele_index(index)]

    @property
    def rf2Ext(self) -> rF2data.rF2Extended:
        """rF2 extended data"""
        return self._ext.data

    @property
    def rf2Ffb(self) -> rF2data.rF2ForceFeedback:
        """rF2 force feedback data"""
        return self._ffb.data

    @property
    def playerIndex(self) -> int:
        """rF2 local player's scoring index"""
        return self._sync.player_scor_index

    def isPlayer(self, index: int) -> bool:
        """Check whether index is player"""
        if self._sync.override_player_index:
            return self._sync.player_scor_index == index
        return self._scor.data.mVehicles[index].mIsPlayer

    @property
    def isPaused(self) -> bool:
        """Check whether data stopped updating"""
        return self._sync.paused

    async def _send_batched_frames(self, ws):
        frames = []
        for type_str in ["scor", "tele", "ext", "ffb"]:
            type_id = TYPE_IDS[type_str]
            raw_bytes = bytes(getattr(self, f"_{type_str}").data)
            compressed = zlib.compress(raw_bytes)
            frame = struct.pack("!BI", type_id, len(compressed)) + compressed  # Network byte order
            frames.append(frame)
            logger.info(f"{type_str.upper()} {len(raw_bytes)} bytes → {len(compressed)} compressed bytes")
        
        batch_message = b"".join(frames)
        logger.info(f"Sending batch message of {len(batch_message)} bytes")
        await ws.send(batch_message)

    def start_sender(self, uri: str, session_name: str, max_retries=5):
        """Start WebSocket sender loop (for remote clients) with retry"""

        async def send_data():
            retry_count = 0
            backoff = 1  # start with 1 second backoff

            while retry_count < max_retries or max_retries == 0:
                try:
                    async with websockets.connect(uri) as ws:
                        handshake = json.dumps({"session": session_name, "role": "sender"})
                        await ws.send(handshake)

                        retry_count = 0
                        backoff = 1

                        while not self.isPaused:
                            try:
                                await self._send_batched_frames(ws)
                            except Exception as e:
                                logger.error("WebSocket send failed: %s", e)
                                break
                            await asyncio.sleep(0.2)  # Adjust frequency as needed

                except Exception as e:
                    retry_count += 1
                    logger.warning(f"WebSocket connection failed (attempt {retry_count}): {e}")

                    if max_retries != 0 and retry_count >= max_retries:
                        logger.error("Max retry attempts reached, giving up.")
                        break

                    logger.info(f"Retrying in {backoff} seconds...")
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 30)

        def run():
            asyncio.run(send_data())

        threading.Thread(target=run, daemon=True).start()


class RemoteRF2Info:
    """Remote rF2 info client receiving binary stream via WebSocket"""

    def __init__(self, session_uri: str, session_name):
        self._scor = rF2data.rF2Scoring()
        self._tele = rF2data.rF2Telemetry()
        self._ext = rF2data.rF2Extended()
        self._ffb = rF2data.rF2ForceFeedback()
        self._lock = threading.Lock()
        self._running = True
        self._session_uri = session_uri
        self._session_name = session_name
        threading.Thread(target=self._start_client, daemon=True).start()

    def _start_client(self):
        asyncio.run(self._recv_loop())

    async def _recv_loop(self, max_retries=5):
        retry_count = 0
        backoff = 1

        while retry_count < max_retries or max_retries == 0:
            try:
                async with websockets.connect(self._session_uri) as ws:
                    handshake = json.dumps({"session": self._session_name, "role": "receiver"})
                    await ws.send(handshake)

                    retry_count = 0
                    backoff = 1

                    while self._running:
                        msg = await ws.recv()
                        logger.info(f"Received message: {len(msg)} bytes")

                        offset = 0
                        expected_parts = 4
                        received_parts = []

                        try:
                            while offset < len(msg):
                                if offset + 5 > len(msg):
                                    raise ValueError("Invalid segment header")

                                type_id = msg[offset]
                                length = struct.unpack("!I", msg[offset + 1:offset + 5])[0]  # network byte order
                                offset += 5

                                if offset + length > len(msg):
                                    raise ValueError("Segment length exceeds message size")

                                compressed_segment = msg[offset:offset + length]
                                decompressed = zlib.decompress(compressed_segment)
                                received_parts.append((type_id, decompressed))

                                logger.info(f"Segment type {type_id}, compressed {length} bytes, decompressed {len(decompressed)} bytes")

                                offset += length

                            if len(received_parts) == expected_parts:
                                with self._lock:
                                    for type_id, data in received_parts:
                                        if type_id == 1:
                                            ctypes.memmove(ctypes.addressof(self._scor), data, ctypes.sizeof(self._scor))
                                        elif type_id == 2:
                                            ctypes.memmove(ctypes.addressof(self._tele), data, ctypes.sizeof(self._tele))
                                        elif type_id == 3:
                                            ctypes.memmove(ctypes.addressof(self._ext), data, ctypes.sizeof(self._ext))
                                        elif type_id == 4:
                                            ctypes.memmove(ctypes.addressof(self._ffb), data, ctypes.sizeof(self._ffb))
                                        else:
                                            logger.warning(f"Unknown segment type ID: {type_id}")
                            else:
                                logger.warning(f"Expected {expected_parts} segments but received {len(received_parts)}")

                        except Exception as ex:
                            logger.error(f"Error parsing message: {ex}")

            except Exception as e:
                retry_count += 1
                logger.warning(f"WebSocket receive connection failed (attempt {retry_count}): {e}")

                if max_retries != 0 and retry_count >= max_retries:
                    logger.error("Max retry attempts reached, giving up.")
                    break

                logger.info(f"Retrying receive connection in {backoff} seconds...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)

    def rf2ScorVeh(self, index: int | None = None):
        with self._lock:
            return self._scor.mVehicles[index if index is not None else 0]

    def rf2TeleVeh(self, index: int | None = None):
        with self._lock:
            return self._tele.mVehicles[index if index is not None else 0]

    @property
    def rf2ScorInfo(self):
        return self._scor.mScoringInfo

    @property
    def rf2Ext(self):
        return self._ext

    @property
    def rf2Ffb(self):
        return self._ffb

    @property
    def playerIndex(self):
        return 0

    def isPlayer(self, index: int) -> bool:
        return index == 0

    @property
    def isPaused(self) -> bool:
        return False

def get_rf2_info(cfg) -> SwitcherRF2Info:
    """Factory function to return a unified RF2Info wrapper that handles switching"""
    return SwitcherRF2Info(cfg)

def test_api():
    """API test run"""
    # Add logger
    test_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    logger.addHandler(test_handler)

    # Test run
    SEPARATOR = "=" * 50
    print("Test API - Start")
    info = RF2Info()
    info.setMode(1)  # set direct access
    info.setPID("")
    info.setPlayerOverride(True)  # enable player override
    info.setPlayerIndex(0)  # set player index to 0
    info.start()
    sleep(0.2)

    print(SEPARATOR)
    print("Test API - Restart")
    info.stop()
    info.setMode()  # set copy access
    info.setPlayerOverride()  # disable player override
    info.start()

    print(SEPARATOR)
    print("Test API - Read")
    version = info.rf2Ext.mVersion.decode()
    driver = info.rf2ScorVeh(0).mDriverName.decode(encoding="iso-8859-1")
    track = info.rf2ScorInfo.mTrackName.decode(encoding="iso-8859-1")
    print(f"plugin version: {version if version else 'not running'}")
    print(f"driver name   : {driver if version else 'not running'}")
    print(f"track name    : {track if version else 'not running'}")

    print(SEPARATOR)
    print("Test API - Close")
    info.stop()


if __name__ == "__main__":
    test_api()
