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
Heatmap function
"""

from __future__ import annotations

from .setting import cfg
from . import validator as val


def select_color(heatmap_list: list, temperature: float) -> str:
    """Select color from heatmap list"""
    for idx, temp in enumerate(heatmap_list):
        if temperature < temp[0]:
            if idx == 0:
                return heatmap_list[0][1]
            return heatmap_list[idx - 1][1]
    # Set color from last row if exceeded max range
    return heatmap_list[-1][1]


def verify_heatmap(heatmap_dict: dict) -> bool:
    """Verify color in heatmap"""
    if not heatmap_dict:
        return False
    for color in tuple(heatmap_dict.values()):
        if not val.hex_color(color):
            return False
    return True


def load_heatmap(heatmap_name: str, default_name: str) -> list[tuple[float, str]]:
    """Load heatmap preset (dictionary)

    key = temperature string, value = hex color string.
    Convert key to float, sort by key.

    Returns:
        list(tuple(temperature value, hex color string))
    """
    heatmap_dict = cfg.user.heatmap.get(heatmap_name, None)
    if not verify_heatmap(heatmap_dict):
        heatmap_dict = cfg.default.heatmap[default_name]
    return sorted((float(temp), color) for temp, color in heatmap_dict.items())
