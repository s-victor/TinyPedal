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
Default module setting template
"""


MODULE_DEFAULT = {
    "module_delta": {
        "enable": True,
        "update_interval": 10,
        "idle_update_interval": 400,
    },
    "module_force": {
        "enable": True,
        "update_interval": 10,
        "idle_update_interval": 400,
        "gravitational_acceleration": 9.80665,
        "max_g_force_freeze_duration": 5,
        "max_average_g_force_samples": 10,
        "max_average_g_force_differece": 0.2,
    },
    "module_fuel": {
        "enable": True,
        "update_interval": 10,
        "idle_update_interval": 400,
    },
    "module_hybrid": {
        "enable": True,
        "update_interval": 20,
        "idle_update_interval": 400,
    },
    "module_mapping": {
        "enable": True,
        "update_interval": 10,
        "idle_update_interval": 400,
    },
    "module_relative": {
        "enable": True,
        "update_interval": 100,
        "idle_update_interval": 400,
    },
    "module_sectors": {
        "enable": True,
        "update_interval": 10,
        "idle_update_interval": 400,
        "sector_info": "",
    },
    "module_vehicles": {
        "enable": True,
        "update_interval": 20,
        "idle_update_interval": 400,
    },
}
