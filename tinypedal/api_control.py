#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
API control
"""

import logging
from abc import ABC, abstractmethod

# Import APIs
from pyRfactor2SharedMemory.sim_info_sync import SimInfoSync

from .setting import cfg

logger = logging.getLogger(__name__)


class Connector(ABC):
    """API Connector"""
    @abstractmethod
    def start(self):
        """Start API & load info access function"""

    @abstractmethod
    def stop(self):
        """Stop API"""

    @abstractmethod
    def setup(self, access_mode, process_id, player_override, player_index):
        """Setup API parameters"""

    @abstractmethod
    def state(self):
        """API state, whether paused or driving"""

    @abstractmethod
    def version(self):
        """API version"""


class SimRfactor2(Connector):
    """Connect to sim"""
    NAME = "rFactor 2"

    def __init__(self):
        self.info = SimInfoSync("tinypedal")
        self.read = None

    def start(self):
        self.info.start()
        from .adapter.rfactor2 import DataSet
        self.read = DataSet(self.info)

    def stop(self):
        self.info.stop()

    def setup(self, access_mode, process_id, player_override, player_index):
        self.info.setMode(access_mode)
        self.info.setPID(process_id)
        self.info.setPlayerOverride(player_override)
        self.info.setPlayerIndex(player_index)

    def state(self):
        return not self.info.paused and self.read.state.is_driving()

    def version(self):
        return self.read.identify.version()


class SimDummy(Connector):
    """Connect to sim"""
    NAME = "Dummy"

    def __init__(self):
        self.info = SimInfoSync("tinypedal")
        self.read = None

    def start(self):
        self.info.start()
        from .adapter.dummy import DataSet
        self.read = DataSet(self.info)

    def stop(self):
        self.info.stop()

    def setup(self, access_mode, process_id, player_override, player_index):
        self.info.setMode(access_mode)
        self.info.setPID(process_id)
        self.info.setPlayerOverride(player_override)
        self.info.setPlayerIndex(player_index)

    def state(self):
        return not self.info.paused and self.read.state.is_driving()

    def version(self):
        return self.read.identify.version()


class APIControl:
    """API Control"""
    API_PACK = (
        SimRfactor2,
        SimDummy,
    )

    def __init__(self):
        self._api = None

    def connect(self, index: int=0):
        """Connect API using index

        0 - rFactor 2.
        1 - Dummy.
        """
        self._api = self.API_PACK[min(max(index, 0), len(self.API_PACK) - 1)]()

    def start(self):
        """Start API"""
        self.setup()
        self._api.start()
        logger.info("activated API: %s (%s)", self._api.NAME, self.version)

    def stop(self):
        """Stop API"""
        self._api.stop()

    def restart(self):
        """Restart API"""
        self.stop()
        self.connect(cfg.shared_memory_api["api"])
        self.start()

    def setup(self):
        """Setup & apply API changes"""
        access_mode = cfg.shared_memory_api["access_mode"]
        process_id = cfg.shared_memory_api["process_id"]
        player_override = cfg.shared_memory_api["enable_player_index_override"]
        player_index = cfg.shared_memory_api["player_index"]
        self._api.setup(
            access_mode,
            process_id,
            player_override,
            player_index
        )

    @property
    def read(self):
        """API info reader"""
        return self._api.read

    @property
    def name(self):
        """API name output"""
        return self._api.NAME

    @property
    def state(self):
        """API state output"""
        if cfg.shared_memory_api["enable_active_state_override"]:
            return cfg.shared_memory_api["active_state"]
        return self._api.state()

    @property
    def version(self):
        """API version output"""
        version = self._api.version()
        return version if version else "unknown"


api = APIControl()
# api.connect(0)
