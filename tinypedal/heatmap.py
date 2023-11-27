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
Heatmap function
"""

from .setting import cfg
from . import validator as val


def select_color(heatmap: tuple, temperature: float) -> str:
    """Select color from heatmap"""
    last_color = heatmap[0][1]
    for temp in heatmap:
        if temperature < float(temp[0]):
            return last_color
        last_color = temp[1]
    return heatmap[-1][1]


def verify_heatmap(heatmap_dict: dict) -> bool:
    """Verify color in heatmap"""
    for color in tuple(heatmap_dict.values()):
        if not val.hex_color(color):
            return False
    return True


def load_heatmap(name: str, default: str) -> tuple:
    """Load heatmap preset and convert to tuple list"""
    if name in cfg.heatmap_user:
        heatmap = cfg.heatmap_user[name]
        if verify_heatmap(heatmap):
            return tuple(heatmap.items())
    return tuple(cfg.heatmap_default[default].items())
