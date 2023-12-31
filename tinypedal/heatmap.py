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
Heatmap function
"""

from operator import itemgetter

from .setting import cfg
from . import validator as val


def select_color(heatmap_list: list, temperature: float) -> str:
    """Select color from heatmap list"""
    last_color = heatmap_list[0][1]  # set color from 1st row
    for temp in heatmap_list:
        if temperature < temp[0]:
            return last_color
        last_color = temp[1]  # set color from next row
    return heatmap_list[-1][1]  # set color from last row if exceeded max range


def verify_heatmap(heatmap_dict: dict) -> bool:
    """Verify color in heatmap"""
    for color in tuple(heatmap_dict.values()):
        if not val.hex_color(color):
            return False
    return True


def sort_heatmap(heatmap_dict: dict) -> list:
    """Sort heatmap entries by first column (convert key string to float)"""
    #return sorted(heatmap_dict.items(), key=lambda col: float(col[0]))
    return sorted(
        ((float(value), color) for value, color in heatmap_dict.items()),
        key=itemgetter(0)
    )

def load_heatmap(heatmap_name: str, default_name: str) -> list:
    """Load heatmap preset"""
    if heatmap_name in cfg.heatmap_user:
        heatmap_dict = cfg.heatmap_user[heatmap_name]
        if verify_heatmap(heatmap_dict):
            return sort_heatmap(heatmap_dict)
    return sort_heatmap(cfg.heatmap_default[default_name])
