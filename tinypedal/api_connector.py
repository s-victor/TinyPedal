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
API connector
"""

from abc import ABC, abstractmethod
from functools import partial
from typing import NamedTuple

# Import APIs
from .adapter import rf2_connector, rf2_data
from .adapter.syncer import get_rf2_info
from .regex_pattern import API_NAME_LMU, API_NAME_RF2
from .validator import bytes_to_str
from .setting import cfg


class APIDataSet(NamedTuple):
    """API data set"""

    check: rf2_data.Check
    brake: rf2_data.Brake
    emotor: rf2_data.ElectricMotor
    engine: rf2_data.Engine
    inputs: rf2_data.Inputs
    lap: rf2_data.Lap
    session: rf2_data.Session
    switch: rf2_data.Switch
    timing: rf2_data.Timing
    tyre: rf2_data.Tyre
    vehicle: rf2_data.Vehicle
    wheel: rf2_data.Wheel


def set_dataset_rf2(info) -> APIDataSet:
    """Set API data set - RF2 or Remote"""
    return APIDataSet(
        rf2_data.Check(info),
        rf2_data.Brake(info),
        rf2_data.ElectricMotor(info),
        rf2_data.Engine(info),
        rf2_data.Inputs(info),
        rf2_data.Lap(info),
        rf2_data.Session(info),
        rf2_data.Switch(info),
        rf2_data.Timing(info),
        rf2_data.Tyre(info),
        rf2_data.Vehicle(info),
        rf2_data.Wheel(info),
    )


class Connector(ABC):
    """API Connector"""

    __slots__ = ("info",)

    @abstractmethod
    def start(self):
        """Start API & load info access function"""

    @abstractmethod
    def stop(self):
        """Stop API"""

    @abstractmethod
    def dataset(self) -> APIDataSet:
        """Dataset"""

    @abstractmethod
    def setup(self, *config):
        """Setup API parameters"""



class SimRF2(Connector):
    """rFactor 2"""

    __slots__ = ("_config",)
    NAME = API_NAME_RF2

    def __init__(self):
        self.info = None
        self._config = None

    def start(self):
        self.info = get_rf2_info(self._config)

    def stop(self):
        if hasattr(self.info, "stop"):
            self.info.stop()

    def dataset(self) -> APIDataSet:
        return set_dataset_rf2(self.info)

    def setup(self, *config):
        self._config = config[0]  # expects full config dict as first arg
        rf2_data.tostr = partial(bytes_to_str, char_encoding=config[1])


class SimLMU(Connector):
    """Le Mans Ultimate"""

    __slots__ = ("_config",)
    NAME = API_NAME_LMU

    def __init__(self):
        self.info = None
        self._config = None

    def start(self):
        self.info = get_rf2_info(self._config)

    def stop(self):
        self.info.stop()

    def dataset(self) -> APIDataSet:
        return set_dataset_rf2(self.info)

    def setup(self, *config):
        self._config = config[0]
        rf2_data.tostr = partial(bytes_to_str, char_encoding=config[1])



# Add new API to API_PACK
API_PACK = (
    SimRF2,
    SimLMU,
)
