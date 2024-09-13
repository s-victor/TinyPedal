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
Regular expression & pattern
"""


# Bool
CFG_BOOL = (
    # Exact match
    "^active_state$|"
    "^auto_hide$|"
    "^auto_hide_in_private_qualifying$|"
    "^fixed_position$|"
    "^minimize_to_tray$|"
    "^remember_position$|"
    # Partial match
    "align_center|"
    "enable|"
    "shorten|"
    "show|"
    "swap_upper_caption|"
    "swap_lower_caption|"
    "swap_style|"
    "uppercase"
)

# String with different validators
CFG_API_NAME = "api_name"
CFG_COLOR = "color"
CFG_FONT_WEIGHT = "font_weight"
CFG_ENCODING = "character_encoding"
CFG_DELTABEST = "deltabest_source"
CFG_TARGET_LAPTIME = "target_laptime"
CFG_TEXT_ALIGNMENT = "text_alignment"
CFG_CLOCK_FORMAT = "clock_format"

# String common
CFG_FONT_NAME = "font_name"
CFG_HEATMAP = "heatmap"
CFG_STRING = (
    # Exact match
    "^process_id$|"
    "^tyre_compound_symbol$|"
    "^url_host$|"
    "^LMU$|"
    "^RF2$|"
    # Partial match
    "_path|"
    "info|"
    "list|"
    "prefix|"
    "suffix|"
    "text|"
    "unit"
)

# Integer
CFG_INTEGER = (
    # Exact match
    "^access_mode$|"
    "^electric_braking_allocation$|"
    "^grid_move_size$|"
    "^lap_time_history_count$|"
    "^leading_zero$|"
    "^manual_steering_range$|"
    "^maximum_saving_attempts$|"
    "^player_index$|"
    "^parts_width$|"
    "^parts_max_height$|"
    "^parts_max_width$|"
    "^position_x$|"
    "^position_y$|"
    "^stint_history_count$|"
    # Partial match
    "area_margin|"
    "area_size|"
    "bar_edge_width|"
    "bar_gap|"
    "bar_height|"
    "bar_length|"
    "bar_width|"
    "column_index|"
    "decimal_places|"
    "display_detail_level|"
    "display_height|"
    "display_margin|"
    "display_size|"
    "display_width|"
    "draw_order_index|"
    "font_size|"
    "icon_size|"
    "inner_gap|"
    "layout|"
    "number_of|"
    "samples|"
    "split_gap|"
    "update_interval|"
    "url_port|"
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
    "lmu",
    "p2p",
    "rpm",
    "rf2",
    "url",
)
ABBR_PATTERN = "|".join(ABBR_LIST)

# Option list & dictionary
DELTABEST_LIST = ("Best", "Session", "Stint", "Last")
ENCODING_LIST = ("UTF-8", "ISO-8859-1")
FONT_WEIGHT_LIST = ("normal", "bold")
TARGET_LAPTIME_LIST = ("Theoretical", "Personal")
TEXT_ALIGNMENT_LIST = ("Left", "Center", "Right")
UNITS_DICT = {
    "distance_unit": ("Meter", "Feet"),
    "fuel_unit": ("Liter", "Gallon"),
    "odometer_unit": ("Kilometer", "Mile", "Meter"),
    "power_unit": ("Kilowatt", "Horsepower", "Metric Horsepower"),
    "speed_unit": ("KPH", "MPH", "m/s"),
    "temperature_unit": ("Celsius", "Fahrenheit"),
    "turbo_pressure_unit": ("bar", "psi", "kPa"),
    "tyre_pressure_unit": ("kPa", "psi", "bar"),
}
GEAR_SEQUENCE = "N123456789R"
