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
Weather function
"""

from __future__ import annotations
from functools import lru_cache

MAX_MINUTES = 9999
MIN_TEMPERATURE = -273
DEFAULT = [(MAX_MINUTES, -1, MIN_TEMPERATURE, -1)]
WEATHER_NODES = ("START", "NODE_25", "NODE_50", "NODE_75", "FINISH")


def forecast_rf2(data: dict) -> list[tuple]:
    """Get value from weather forecast dictionary, output 5 api data + 5 padding data"""
    try:
        output = [
            (round(index * 0.2, 1),                                   # 0 - fraction start time
            data[weather]["WNV_SKY"]["currentValue"],                 # 1 - sky type index
            round(data[weather]["WNV_TEMPERATURE"]["currentValue"]),  # 2 - temperature
            round(data[weather]["WNV_RAIN_CHANCE"]["currentValue"]),  # 3 - rain chance
            ) for index, weather in enumerate(WEATHER_NODES)]
        output.extend(DEFAULT * 5)
    except (KeyError, TypeError):
        output = DEFAULT * 10
    return output


@lru_cache(maxsize=2)
def sky_type_correction(sky_type, raininess):
    """Correct current sky type index based on current raininess

    Rain percent:
        1-10 drizzle, 11-20 light rain, 21-40 rain, 41-60 heavy rain, 60-100 storm

    Sky type:
        0 Clear
        1 Light Clouds
        2 Partially Cloudy
        3 Mostly Cloudy
        4 Overcast
        5 Cloudy & Drizzle
        6 Cloudy & Light Rain
        7 Overcast & Light Rain
        8 Overcast & Rain
        9 Overcast & Heavy Rain
        10 Overcast & Storm
    """
    if raininess <= 0:
        if sky_type > 4:
            return 4
        return sky_type
    if 0 < raininess <= 10:
        return 5
    if 10 < raininess <= 15:
        return 6
    if 15 < raininess <= 20:
        return 7
    if 20 < raininess <= 40:
        return 8
    if 40 < raininess <= 60:
        return 9
    if 60 < raininess:
        return 10
    return sky_type
