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
Regex pattern
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
    "enable|"
    "show|"
    "swap_style|"
    "uppercase"
)
# String
CFG_API_NAME = "^api_name$"
CFG_COLOR = "color"
CFG_FONT_NAME = "font_name"
CFG_FONT_WEIGHT = "font_weight"
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
    "^player_index$|"
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
