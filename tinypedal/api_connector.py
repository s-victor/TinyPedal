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
API connector
"""

import logging
from abc import ABC, abstractmethod

# Import APIs
from pyRfactor2SharedMemory.sim_info_sync import SimInfoSync

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


class SimRF2(Connector):
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
        return not self.info.paused and self.read.vehicle.is_driving()

    def version(self):
        return self.read.check.version()


class SimDummy(Connector):
    NAME = "Dummy"  # placeholder

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
        return not self.info.paused and self.read.vehicle.is_driving()

    def version(self):
        return "0.0.0"


# Add API to dict API_PACK
# Key = API Name, value = API class
# API_PACK is used to auto-generate API list
# for setting validator & config option
API_PACK = {
    SimRF2.NAME: SimRF2,
    SimDummy.NAME: SimDummy,
}
