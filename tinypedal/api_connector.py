#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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
from pyRfactor2SharedMemory import rF2MMap
from .adapter import rfactor2


class DataSet:
    """Data set"""

    def __init__(self, info, data_set=rfactor2):
        self.check = data_set.Check(info)
        self.brake = data_set.Brake(info)
        self.emotor = data_set.ElectricMotor(info)
        self.engine = data_set.Engine(info)
        self.input = data_set.Input(info)
        self.lap = data_set.Lap(info)
        self.session = data_set.Session(info)
        self.switch = data_set.Switch(info)
        self.timing = data_set.Timing(info)
        self.tyre = data_set.Tyre(info)
        self.vehicle = data_set.Vehicle(info)
        self.wheel = data_set.Wheel(info)


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
    """rFactor 2"""
    NAME = "rFactor 2"

    def __init__(self):
        rF2MMap.logger = logging.getLogger(__name__)
        self.info = rF2MMap.RF2SM()
        self.read = None

    def start(self):
        self.info.start()
        self.read = DataSet(self.info, rfactor2)

    def stop(self):
        self.info.stop()

    def setup(self, access_mode, process_id, player_override, player_index):
        self.info.setMode(access_mode)
        self.info.setPID(process_id)
        self.info.setPlayerOverride(player_override)
        self.info.setPlayerIndex(player_index)

    def state(self):
        return not self.info.isPaused and self.read.vehicle.is_driving()

    def version(self):
        return self.read.check.version()


class SimDummy(Connector):
    """Placeholder"""
    NAME = "Dummy"

    def __init__(self):
        rF2MMap.logger = logging.getLogger(__name__)
        self.info = rF2MMap.RF2SM()
        self.read = None

    def start(self):
        self.info.start()
        self.read = DataSet(self.info, rfactor2)

    def stop(self):
        self.info.stop()

    def setup(self, access_mode, process_id, player_override, player_index):
        self.info.setMode(access_mode)
        self.info.setPID(process_id)
        self.info.setPlayerOverride(player_override)
        self.info.setPlayerIndex(player_index)

    def state(self):
        return not self.info.isPaused and self.read.vehicle.is_driving()

    def version(self):
        return "0.0.1"


# Add new API to API_PACK
# API_PACK is used to generate API_NAME_LIST
# for API selection, setting validator, config option
API_PACK = (
    SimRF2,
    SimDummy,
)
API_NAME_LIST = tuple(_api.NAME for _api in API_PACK)
