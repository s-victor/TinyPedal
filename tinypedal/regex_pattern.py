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
Regular expression & pattern
"""


# Bool
CFG_BOOL = (
    # Exact match
    "^active_state$|"
    "^auto_hide$|"
    "^fixed_position$|"
    "^minimize_to_tray$|"
    "^remember_position$|"
    # Partial match
    "align_center|"
    "enable|"
    "shorten|"
    "show|"
    "swap_style|"
    "uppercase"
)

# String
CFG_API_NAME = "^api_name$"
CFG_COLOR = "color"
CFG_FONT_NAME = "font_name"
CFG_FONT_WEIGHT = "font_weight"
CFG_ENCODING = "character_encoding"
CFG_HEATMAP = "heatmap"
CFG_STRING = (
    # Exact match
    "^process_id$|"
    "^tyre_compound_symbol$|"
    # Partial match
    "format|"
    "info|"
    "list|"
    "prefix|"
    "text|"
    "unit"
)

# Integer
CFG_INTEGER = (
    # Exact match
    "^access_mode$|"
    "^grid_move_size$|"
    "^lap_time_history_count$|"
    "^leading_zero$|"
    "^manual_steering_range$|"
    "^player_index$|"
    "^parts_width$|"
    "^parts_max_height$|"
    "^parts_max_width$|"
    "^position_x$|"
    "^position_y$|"
    "^stint_history_count$|"
    "^target_time_mode$|"
    # Partial match
    "bar_gap|"
    "bar_edge_width|"
    "bar_height|"
    "bar_length|"
    "bar_width|"
    "column_index|"
    "decimal_places|"
    "display_margin|"
    "display_size|"
    "font_size|"
    "icon_size|"
    "inner_gap|"
    "layout|"
    "samples|"
    "split_gap|"
    "update_interval|"
    "vehicles"
)

# Filename
CFG_INVALID_FILENAME = (
    # Exact match
    "^$|"
    "^brands$|"
    "^classes$|"
    "^heatmap$|"
    # Partial match
    "backup"
)

# Abbreviation
ABBR_LIST = (
    "api",
    "drs",
    "ffb",
    "p2p",
    "rpm",
)
ABBR_PATTERN = "|".join(ABBR_LIST)

# Option list & dictionary
ENCODING_LIST = "UTF-8", "ISO-8859-1"
FONT_WEIGHT_LIST = "normal", "bold"
UNITS_DICT = {
    "distance_unit": ("Meter", "Feet"),
    "fuel_unit": ("Liter", "Gallon"),
    "odometer_unit": ("Kilometer", "Mile", "Meter"),
    "speed_unit": ("KPH", "MPH", "m/s"),
    "temperature_unit": ("Celsius", "Fahrenheit"),
    "turbo_pressure_unit": ("bar", "psi", "kPa"),
    "tyre_pressure_unit": ("kPa", "psi", "bar"),
}
GEAR_SEQUENCE = {
    -1: "R",
    0: "N",
    1: "1",
    2: "2",
    3: "3",
    4: "4",
    5: "5",
    6: "6",
    7: "7",
    8: "8",
    9: "9",
}
