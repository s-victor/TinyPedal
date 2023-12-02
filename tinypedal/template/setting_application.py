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
Default application setting template
"""


APPLICATION_DEFAULT = {
    "application": {
        "show_at_startup": True,
        "minimize_to_tray": True,
        "remember_position": True,
        "position_x": 0,
        "position_y": 0,
    },
    "compatibility": {
        "enable_bypass_window_manager": False,
        "enable_translucent_background": True,
        "global_bkg_color": "#000000",
        "grid_move_size": 8,
    },
    "overlay": {
        "fixed_position": False,
        "auto_hide": True,
        "enable_grid_move": False,
    },
    "shared_memory_api": {
        "api_name": "rFactor 2",
        "access_mode": 0,
        "process_id": "",
        "enable_active_state_override": False,
        "active_state": True,
        "enable_player_index_override": False,
        "player_index": -1,
    },
    "units": {
        "distance_unit": "Meter",
        "fuel_unit": "Liter",
        "odometer_unit": "Kilometer",
        "speed_unit": "KPH",
        "temperature_unit": "Celsius",
        "turbo_pressure_unit": "bar",
        "tyre_pressure_unit": "kPa",
        "tyre_compound_symbol": "ABCDEFGH",
    },
}
