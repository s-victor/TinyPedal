import threading
import logging
from copy import copy
from pyRfactor2SharedMemory.rF2MMap import (
    INVALID_INDEX,
    MAX_VEHICLES,
    rF2data,
)
from .rf2_connector import SyncData

logger = logging.getLogger(__name__)

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
        self._scor = self._sync.dataset.scor
        self._tele = self._sync.dataset.tele
        self._ext = self._sync.dataset.ext
        self._ffb = self._sync.dataset.ffb

    def __del__(self):
        logger.info("sharedmemory: GC: RF2SM")

    def start(self) -> None:
        self._sync.start(self._access_mode, self._rf2_pid)

    def stop(self) -> None:
        self._sync.stop()

    def setPID(self, pid: str = "") -> None:
        self._rf2_pid = str(pid)

    def setMode(self, mode: int = 0) -> None:
        self._access_mode = mode

    def setPlayerOverride(self, state: bool = False) -> None:
        self._sync.override_player_index = state

    def setPlayerIndex(self, index: int = INVALID_INDEX) -> None:
        self._sync.player_scor_index = min(max(index, INVALID_INDEX), MAX_VEHICLES - 1)

    @property
    def rf2ScorInfo(self) -> rF2data.rF2ScoringInfo:
        return self._scor.data.mScoringInfo

    def rf2ScorVeh(self, index: int | None = None) -> rF2data.rF2VehicleScoring:
        return self._sync.player_scor if index is None else self._scor.data.mVehicles[index]

    def rf2TeleVeh(self, index: int | None = None) -> rF2data.rF2VehicleTelemetry:
        return self._sync.player_tele if index is None else self._tele.data.mVehicles[self._sync.sync_tele_index(index)]

    @property
    def rf2Ext(self) -> rF2data.rF2Extended:
        return self._ext.data

    @property
    def rf2Ffb(self) -> rF2data.rF2ForceFeedback:
        return self._ffb.data

    @property
    def playerIndex(self) -> int:
        return self._sync.player_scor_index
    
    def isDriving(self, index: int) -> bool:
        return self._scor.data.mVehicles[index].mControl == 0
            
    def isPlayer(self, index: int) -> bool:
        if self._sync.override_player_index:
            return self._sync.player_scor_index == index
        return self._scor.data.mVehicles[index].mIsPlayer

    @property
    def isPaused(self) -> bool:
        return self._sync.paused