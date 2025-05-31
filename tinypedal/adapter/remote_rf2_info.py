import threading
import ctypes
from pyRfactor2SharedMemory.rF2MMap import rF2data
from .rf2_websocket import RF2WebSocket

class RemoteRF2Info:
    def __init__(self, session_uri: str, session_name: str):
        self._scor = rF2data.rF2Scoring()
        self._tele = rF2data.rF2Telemetry()
        self._ext = rF2data.rF2Extended()
        self._ffb = rF2data.rF2ForceFeedback()
        self._lock = threading.Lock()

        self._ws_client = RF2WebSocket(
            uri=session_uri,
            session_name=session_name,
            role="receiver",
            data_receiver=self
        )
        self._ws_client.start()

    def apply_segment_data(self, type_id: int, data: bytes):
        with self._lock:
            dst = None
            if type_id == 1:
                dst = self._scor
            elif type_id == 2:
                dst = self._tele
            elif type_id == 3:
                dst = self._ext
            elif type_id == 4:
                dst = self._ffb
            if dst:
                ctypes.memmove(ctypes.addressof(dst), data, ctypes.sizeof(dst))

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