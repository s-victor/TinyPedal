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
Formatter function
"""

from __future__ import annotations
import random
import re
from functools import lru_cache

from . import regex_pattern as rxp


def uppercase_abbr(name: str) -> str:
    """Convert abbreviation name to uppercase"""
    for abbr in rxp.ABBR_LIST:
        if re.search(rxp.ABBR_PATTERN, name, flags=re.IGNORECASE):
            name = re.sub(abbr, abbr.upper(), name, flags=re.IGNORECASE)
    return name


def format_module_name(name: str) -> str:
    """Format widget & module name"""
    name = re.sub("module_", "", name)
    name = re.sub("_", " ", name)
    name = name.capitalize()
    return uppercase_abbr(name)


def format_option_name(name: str) -> str:
    """Format option name"""
    name = re.sub("bkg", "background", name)
    name = re.sub("_", " ", name)
    name = re.sub("units", "units and symbols", name)
    name = name.title()
    return uppercase_abbr(name)


def strip_filename_extension(name: str, extension: str) -> str:
    """Strip file name extension"""
    if name.lower().endswith(extension):
        return name[:-len(extension)]
    return name


def select_gear(index: int) -> str:
    """Select gear string"""
    return rxp.GEAR_SEQUENCE.get(index, "N")


@lru_cache(maxsize=20)
def random_color_class(name: str) -> str:
    """Generate random color for vehicle class"""
    random.seed(name)
    rgb = [30,180,random.randrange(30,180)]
    random.shuffle(rgb)
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


@lru_cache(maxsize=128)
def shorten_driver_name(name: str) -> str:
    """Shorten driver name"""
    rex_string = re.split(r"( )", name.strip(" "))
    if len(rex_string) > 2:
        return f"{rex_string[0][:1]}.{rex_string[-1]}".title()
    return rex_string[-1]


def pipe_join(*args: any) -> str:
    """Convert value to str & join with pipe symbol"""
    return "|".join(map(str, args))


def pipe_split(string: str) -> list:
    """Split string to list by pipe symbol"""
    rex_string = re.split(r"(\|)", string)
    return [value for value in rex_string if value != "|"]


def strip_invalid_char(name: str) -> str:
    """Strip invalid characters"""
    return re.sub('[\\\\/:*?"<>|]', "", name)


def strip_decimal_pt(value: str) -> str:
    """Strip decimal point"""
    if value and value[-1] == ".":
        return value[:-1]
    return value


def laptime_string_to_seconds(laptime: str) -> float:
    """Convert laptime "minutes:seconds" string to seconds"""
    rstring = re.split(r":", laptime)
    split = [0] * (2 - len(rstring)) + rstring
    return float(split[0]) * 60 + float(split[1])


def string_pair_to_int(string: str) -> tuple[int]:
    """Convert string pair "x,y" to int"""
    value = re.split(",", string)
    return int(value[0]), int(value[1])


def string_pair_to_float(string: str) -> tuple[float]:
    """Convert string pair "x,y" to float"""
    value = re.split(",", string)
    return float(value[0]), float(value[1])


def points_to_coords(points: str) -> tuple[tuple[float]]:
    """Convert svg points strings to raw coordinates

    Args:
        points: "x,y x,y ..." svg points strings.

    Returns:
        ((x,y),(x,y) ...) raw coordinates.
    """
    string = re.split(" ", points)
    return tuple(map(string_pair_to_float, string))


def coords_to_points(coords: tuple) -> str:
    """Convert raw coordinates to svg points strings

    Args:
        coords: ((x,y),(x,y) ...) raw coordinates.

    Returns:
        "x,y x,y ..." svg points strings.
    """
    output = ""
    for data in coords:
        if output:
            output += " "
        output += f"{data[0]},{data[1]}"
    return output
