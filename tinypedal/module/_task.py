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
from ..process.pitstop import estimate_pit_stop_time
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
    (minfo.restapi, "trackClockTime", -1.0, None, "sessionTime", "timeOfDay"),
    (minfo.restapi, "pitStopEstimate", PITEST_DEFAULT, estimate_pit_stop_time),
)
SET_WEATHERFORECAST = (
    (minfo.restapi, "forecastPractice", FORECAST_DEFAULT, forecast_rf2, "PRACTICE"),
    (minfo.restapi, "forecastQualify", FORECAST_DEFAULT, forecast_rf2, "QUALIFY"),
    (minfo.restapi, "forecastRace", FORECAST_DEFAULT, forecast_rf2, "RACE"),
)

# Define task set
# 0 - sim name pattern, 1 - url path, 2 - output set
TASK_RUNONCE = (
    ("LMU|RF2", "sessions/setting/SESSSET_race_timescale", SET_TIMESCALE),
    ("LMU|RF2", "sessions/setting/SESSSET_private_qual", SET_PRIVATEQUALIFY),
    ("LMU|RF2", "sessions/weather", SET_WEATHERFORECAST),
    ("LMU", "garage/chassis", SET_CHASSIS),
)
TASK_REPEATS = (
    ("LMU", "garage/UIScreen/RepairAndRefuel", SET_CURRENTSTINT),
)
