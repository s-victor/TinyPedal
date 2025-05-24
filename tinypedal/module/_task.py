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

from ..const_common import PITEST_DEFAULT
from ..module_info import minfo
from ..process.pitstop import EstimatePitTime
from ..process.vehicle import steerlock_to_number
from ..process.weather import FORECAST_DEFAULT, forecast_rf2

# Define output set
# 0 - minfo, 1 - output, 2 - default value, 3 - function, 4 - dict keys
SET_TIMESCALE = (
    (minfo.restapi, "timeScale", 1, None, "currentValue"),
)
SET_PRIVATEQUALIFY = (
    (minfo.restapi, "privateQualifying", 0, None, "currentValue"),
)
SET_CHASSIS = (
    (minfo.restapi, "steeringWheelRange", 0.0, steerlock_to_number, "VM_STEER_LOCK", "stringValue"),
)
SET_CURRENTSTINT = (
    (minfo.restapi, "currentVirtualEnergy", 0.0, None, "fuelInfo", "currentVirtualEnergy"),
    (minfo.restapi, "maxVirtualEnergy", 0.0, None, "fuelInfo", "maxVirtualEnergy"),
    (minfo.restapi, "aeroDamage", -1.0, None, "wearables", "body", "aero"),
    (minfo.restapi, "brakeWear", [-1] * 4, None, "wearables", "brakes"),
    (minfo.restapi, "suspensionDamage", [-1] * 4, None, "wearables", "suspension"),
)
SET_GAMESTATE = (
    (minfo.restapi, "trackClockTime", -1.0, None, "timeOfDay"),
)
SET_PITMENUINFO = (
    (minfo.restapi, "pitStopEstimate", PITEST_DEFAULT, EstimatePitTime()),
)
SET_PITSTOPTIME = (
    (minfo.restapi, "pitTimeReference", dict(), None),
)
SET_WEATHERFORECAST = (
    (minfo.restapi, "forecastPractice", FORECAST_DEFAULT, forecast_rf2, "PRACTICE"),
    (minfo.restapi, "forecastQualify", FORECAST_DEFAULT, forecast_rf2, "QUALIFY"),
    (minfo.restapi, "forecastRace", FORECAST_DEFAULT, forecast_rf2, "RACE"),
)

# Define task set
# 0 - sim name pattern, 1 - url path, 2 - output set, 3 - enabling condition
TASK_RUNONCE = (
    ("LMU|RF2", "sessions/setting/SESSSET_race_timescale", SET_TIMESCALE, None),
    ("LMU|RF2", "sessions/setting/SESSSET_private_qual", SET_PRIVATEQUALIFY, None),
    ("LMU|RF2", "sessions/weather", SET_WEATHERFORECAST, None),
    ("LMU", "garage/chassis", SET_CHASSIS, None),
)
TASK_REPEATS = (
    ("LMU", "garage/UIScreen/DriverHandOffStintEnd", SET_CURRENTSTINT, None),
    ("LMU", "sessions/GetGameState", SET_GAMESTATE, None),
    ("LMU", "garage/PitMenu/receivePitMenu", SET_PITMENUINFO, "enable_pit_strategy_access"),
    ("LMU", "garage/Pitstop/getPitstopTimes", SET_PITSTOPTIME, "enable_pit_strategy_access"),
)
