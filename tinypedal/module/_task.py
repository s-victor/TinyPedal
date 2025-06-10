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
Web API task
"""

from __future__ import annotations

from typing import Any, Callable, NamedTuple

from ..const_common import PITEST_DEFAULT
from ..module_info import minfo
from ..process.pitstop import EstimatePitTime
from ..process.vehicle import steerlock_to_number
from ..process.weather import FORECAST_DEFAULT, forecast_rf2


class HttpSetup(NamedTuple):
    """Http connection setup"""

    host: str
    port: int
    retry: int
    timeout: float
    delay: float


class ResRawOutput(NamedTuple):
    """URI resource raw output"""

    output: object
    name: str
    default: Any
    keys: tuple[str, ...]

    def reset(self):
        """Reset data"""
        setattr(self.output, self.name, self.default)

    def update(self, data: Any) -> bool:
        """Update data"""
        for key in self.keys:  # get data from dict
            if not isinstance(data, dict):  # not exist, set to default
                setattr(self.output, self.name, self.default)
                return False
            data = data.get(key)
        # Not exist, set to default
        if data is None:
            setattr(self.output, self.name, self.default)
            return False
        # Reset to default if value is not same type as default
        if not isinstance(data, type(self.default)):
            data = self.default
        setattr(self.output, self.name, data)
        return True


class ResParOutput(NamedTuple):
    """URI resource parsed output"""

    output: object
    name: str
    default: Any
    parser: Callable
    keys: tuple[str, ...]

    def reset(self):
        """Reset data"""
        setattr(self.output, self.name, self.default)

    def update(self, data: Any) -> bool:
        """Update data"""
        for key in self.keys:  # get data from dict
            if not isinstance(data, dict):  # not exist, set to default
                setattr(self.output, self.name, self.default)
                return False
            data = data.get(key)
        # Not exist, set to default
        if data is None:
            setattr(self.output, self.name, self.default)
            return False
        # Parse and output
        setattr(self.output, self.name, self.parser(data))
        return True


EMPTY_KEYS: tuple[str, ...] = tuple()

# Define output set
SET_TIMESCALE = (
    ResRawOutput(minfo.restapi, "timeScale", 1, ("currentValue",)),
)
SET_PRIVATEQUALIFY = (
    ResRawOutput(minfo.restapi, "privateQualifying", 0, ("currentValue",)),
)
SET_CHASSIS = (
    ResParOutput(minfo.restapi, "steeringWheelRange", 0.0, steerlock_to_number, ("VM_STEER_LOCK", "stringValue")),
)
SET_CURRENTSTINT = (
    ResRawOutput(minfo.restapi, "currentVirtualEnergy", 0.0, ("fuelInfo", "currentVirtualEnergy")),
    ResRawOutput(minfo.restapi, "maxVirtualEnergy", 0.0, ("fuelInfo", "maxVirtualEnergy")),
    ResRawOutput(minfo.restapi, "aeroDamage", -1.0, ("wearables", "body", "aero")),
    ResRawOutput(minfo.restapi, "brakeWear", [-1] * 4, ("wearables", "brakes")),
    ResRawOutput(minfo.restapi, "suspensionDamage", [-1] * 4, ("wearables", "suspension")),
)
SET_GAMESTATE = (
    ResRawOutput(minfo.restapi, "trackClockTime", -1.0, ("timeOfDay",)),
)
SET_PITMENUINFO = (
    ResParOutput(minfo.restapi, "pitStopEstimate", PITEST_DEFAULT, EstimatePitTime(), EMPTY_KEYS),
)
SET_PITSTOPTIME = (
    ResRawOutput(minfo.restapi, "pitTimeReference", dict(), ("pitStopTimes", "times")),
)
SET_WEATHERFORECAST = (
    ResParOutput(minfo.restapi, "forecastPractice", FORECAST_DEFAULT, forecast_rf2, ("PRACTICE",)),
    ResParOutput(minfo.restapi, "forecastQualify", FORECAST_DEFAULT, forecast_rf2, ("QUALIFY",)),
    ResParOutput(minfo.restapi, "forecastRace", FORECAST_DEFAULT, forecast_rf2, ("RACE",)),
)
SET_SESSIONSINFO = (
    ResRawOutput(minfo.restapi, "timeScale", 1, ("SESSSET_race_timescale", "currentValue")),
    ResRawOutput(minfo.restapi, "privateQualifying", 0, ("SESSSET_private_qual", "currentValue")),
)

# Define task set
# 0 - sim name pattern, 1 - uri path, 2 - output set, 3 - enabling condition
TASK_RUNONCE = (
    ("LMU|RF2", "/rest/sessions/weather", SET_WEATHERFORECAST, None),
    ("RF2", "/rest/sessions/setting/SESSSET_race_timescale", SET_TIMESCALE, None),
    ("RF2", "/rest/sessions/setting/SESSSET_private_qual", SET_PRIVATEQUALIFY, None),
    ("LMU", "/rest/sessions/?", SET_SESSIONSINFO, None),
    ("LMU", "/rest/garage/chassis", SET_CHASSIS, None),
    ("LMU", "/rest/garage/UIScreen/RepairAndRefuel", SET_PITSTOPTIME, "enable_pit_strategy_access"),
)
TASK_REPEATS = (
    ("LMU", "/rest/garage/UIScreen/DriverHandOffStintEnd", SET_CURRENTSTINT, None),
    ("LMU", "/rest/sessions/GetGameState", SET_GAMESTATE, None),
    ("LMU", "/rest/garage/PitMenu/receivePitMenu", SET_PITMENUINFO, "enable_pit_strategy_access"),
)
