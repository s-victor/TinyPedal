#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
from functools import partial

# Import APIs
from pyRfactor2SharedMemory import rF2MMap
from .adapter import rfactor2
from .regex_pattern import API_NAME_RF2, API_NAME_LMU
from . import validator as val


class DataSet:
    """Data set"""

    __slots__ = (
        "check",
        "brake",
        "emotor",
        "engine",
        "input",
        "lap",
        "session",
        "switch",
        "timing",
        "tyre",
        "vehicle",
        "wheel",
    )

    def __init__(self, info, dataset: rfactor2):
        self.check = dataset.Check(info)
        self.brake = dataset.Brake(info)
        self.emotor = dataset.ElectricMotor(info)
        self.engine = dataset.Engine(info)
        self.input = dataset.Input(info)
        self.lap = dataset.Lap(info)
        self.session = dataset.Session(info)
        self.switch = dataset.Switch(info)
        self.timing = dataset.Timing(info)
        self.tyre = dataset.Tyre(info)
        self.vehicle = dataset.Vehicle(info)
        self.wheel = dataset.Wheel(info)


class Connector(ABC):
    """API Connector"""
    @abstractmethod
    def start(self):
        """Start API & load info access function"""

    @abstractmethod
    def stop(self):
        """Stop API"""

    @abstractmethod
    def dataset(self):
        """Dateset"""

    @abstractmethod
    def setup(self, *config):
        """Setup API parameters"""


class SimRF2(Connector):
    """rFactor 2"""
    NAME = API_NAME_RF2

    def __init__(self):
        rF2MMap.logger = logging.getLogger(__name__)
        self.info = rF2MMap.RF2SM()

    def start(self):
        self.info.start()

    def stop(self):
        self.info.stop()

    def dataset(self):
        return DataSet(self.info, rfactor2)

    def setup(self, *config):
        self.info.setMode(config[0])
        self.info.setPID(config[1])
        self.info.setPlayerOverride(config[2])
        self.info.setPlayerIndex(config[3])
        rfactor2.cs2py = partial(val.cbytes2str, char_encoding=config[4])


class SimLMU(Connector):
    """Le Mans Ultimate"""
    NAME = API_NAME_LMU

    def __init__(self):
        rF2MMap.logger = logging.getLogger(__name__)
        self.info = rF2MMap.RF2SM()

    def start(self):
        self.info.start()

    def stop(self):
        self.info.stop()

    def dataset(self):
        return DataSet(self.info, rfactor2)

    def setup(self, *config):
        self.info.setMode(config[0])
        self.info.setPID(config[1])
        self.info.setPlayerOverride(config[2])
        self.info.setPlayerIndex(config[3])
        rfactor2.cs2py = partial(val.cbytes2str, char_encoding=config[4])


# Add new API to API_PACK
API_PACK = (
    SimRF2,
    SimLMU,
)
