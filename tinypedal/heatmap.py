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
        if temp[0] > temperature:
            if idx == 0:
                return temp[1]
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

    Args:
        heatmap_name: heatmap preset name.
        default_name: default preset name.

    Returns:
        list(tuple(temperature value, hex color string))
    """
    heatmap_dict = cfg.user.heatmap.get(heatmap_name, None)
    if not verify_heatmap(heatmap_dict):
        heatmap_dict = cfg.default.heatmap[default_name]
    return sorted(
        (float(temp), heatmap_color)
        for temp, heatmap_color in heatmap_dict.items()
    )


def load_heatmap_style(
    heatmap_name: str, default_name: str, swap_style: bool = False,
    fg_color: str = "", bg_color: str = "") -> list[tuple[float, str]]:
    """Load heatmap preset (dictionary) & set color style sheet

    key = temperature string, value = hex color string.
    Convert key to float, sort by key.

    Args:
        heatmap_name: heatmap preset name.
        default_name: default preset name.
        swap_style: assign heatmap color as background color if True, otherwise as foreground.
        fg_color: assign foreground color if swap_style True.
        bg_color: assign background color if swap_style False.

    Returns:
        list(tuple(temperature value, color style sheet string))
    """
    heatmap_dict = cfg.user.heatmap.get(heatmap_name, None)
    if not verify_heatmap(heatmap_dict):
        heatmap_dict = cfg.default.heatmap[default_name]
    if swap_style:
        return sorted(
            (float(temp), f"color:{fg_color};background:{heatmap_color};")
            for temp, heatmap_color in heatmap_dict.items()
        )
    return sorted(
        (float(temp), f"color:{heatmap_color};background:{bg_color};")
        for temp, heatmap_color in heatmap_dict.items()
    )
