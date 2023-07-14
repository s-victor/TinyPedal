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
Regex pattern
"""


# Bool
BOOL = (
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
COLOR = "color"
FONTNAME = "font_name"
FONTWEIGHT = "font_weight"
HEATMAP = "heatmap"
STRING = (
    # Exact match
    "^rF2_process_id$|"
    # Partial match
    "format|"
    "info|"
    "list|"
    "prefix|"
    "text|"
    "unit"
)
# Integer
INTEGER = (
    # Exact match
    "^access_mode$|"
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

# Formatting
UPPERCASE = (
    # Partial match
    "drs|"
    "p2p"
)
