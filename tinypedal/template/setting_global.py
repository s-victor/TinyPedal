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
Default global (config) setting template
"""


GLOBAL_DEFAULT = {
    "application": {
        "show_at_startup": True,
        "minimize_to_tray": True,
        "remember_position": True,
        "position_x": 0,
        "position_y": 0,
        "enable_auto_load_preset": False,
        "minimum_update_interval": 10,
        "maximum_saving_attempts": 10,
    },
    "user_path": {
        "settings_path": "settings/",
        "brand_logo_path": "brandlogo/",
        "delta_best_path": "deltabest/",
        "sector_best_path": "deltabest/",
        "energy_delta_path": "deltabest/",
        "fuel_delta_path": "deltabest/",
        "track_map_path": "trackmap/",
    },
    "primary_preset": {
        "LMU": "",
        "RF2": "",
    },
}
