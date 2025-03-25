#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from .regex_pattern import RE_INVALID_CHAR, ABBR_PATTERN


def uppercase_abbr(name: str) -> str:
    """Convert abbreviation name to uppercase"""
    return re.sub(ABBR_PATTERN, upper_matched_abbr, name, flags=re.IGNORECASE)


def upper_matched_abbr(matchobj: re.Match) -> str:
    """Convert abbreviation name to uppercase"""
    return matchobj.group().upper()


def format_module_name(name: str) -> str:
    """Format widget & module name"""
    return uppercase_abbr(
        name
        .replace("module_", "")
        .replace("_", " ")
        .capitalize()
    )


def format_option_name(name: str) -> str:
    """Format option name"""
    return uppercase_abbr(
        name
        .replace("bkg", "background")
        .replace("_", " ")
        .title()
    )


def strip_filename_extension(name: str, extension: str) -> str:
    """Strip file name extension"""
    if name.lower().endswith(extension):
        return name[:-len(extension)]
    return name


def rgb_to_gray(rgb: list[int]) -> int:
    """RGB value to gray (0-255)"""
    return (rgb[0] * 3 + rgb[1] * 6 + rgb[2]) // 10


@lru_cache(maxsize=20)
def random_color_class(name: str) -> str:
    """Generate random color for vehicle class"""
    max_value = 225
    min_value = 25
    target_brightness = 100
    # Generate random RGB color
    random.seed(name)
    rgb = [min_value + 10, max_value - 10, random.randint(min_value, max_value)]
    random.seed(name)
    random.shuffle(rgb)
    # Brightness correction
    brightness = rgb_to_gray(rgb)
    if brightness > target_brightness:
        while brightness > target_brightness:
            ran_index = random.randint(0, 2)
            if rgb[ran_index] >= min_value:
                rgb[ran_index] -= 5
            else:
                rgb[ran_index] += random.randint(10, 30)
            brightness = rgb_to_gray(rgb)
    elif brightness < target_brightness:
        while brightness < target_brightness:
            ran_index = random.randint(0, 2)
            if rgb[ran_index] <= max_value:
                rgb[ran_index] += 5
            else:
                rgb[ran_index] -= random.randint(10, 30)
            brightness = rgb_to_gray(rgb)
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


@lru_cache(maxsize=128)
def shorten_driver_name(name: str) -> str:
    """Shorten driver name"""
    name_split = name.strip(" ").split(" ")
    if len(name_split) > 1:
        return f"{name_split[0][:1]}.{name_split[-1]}".title()
    return name_split[-1]


def pipe_join(*args: str) -> str:
    """Convert value to str & join with pipe symbol"""
    return "|".join(args)


def pipe_split(string: str) -> list[str]:
    """Split string to list by pipe symbol"""
    return string.split("|")


def strip_invalid_char(name: str) -> str:
    """Strip invalid characters"""
    return re.sub(RE_INVALID_CHAR, "", name)


def strip_decimal_pt(value: str) -> str:
    """Strip decimal point"""
    return value.strip(".")


def laptime_string_to_seconds(laptime: str) -> float:
    """Convert laptime "minutes:seconds" string to seconds"""
    string = laptime.split(":")
    split = [0] * (2 - len(string)) + string
    return float(split[0]) * 60 + float(split[1])


def string_pair_to_int(string: str) -> tuple[int, int]:
    """Convert string pair "x,y" to int list"""
    value = string.split(",")
    return int(value[0]), int(value[1])


def string_pair_to_float(string: str) -> tuple[float, float]:
    """Convert string pair "x,y" to float list"""
    value = string.split(",")
    return float(value[0]), float(value[1])


def list_pair_to_string(data: tuple | list) -> str:
    """Convert list pair (x,y) to string pair"""
    return f"{data[0]},{data[1]}"


def points_to_coords(points: str) -> tuple[tuple[float, float], ...]:
    """Convert svg points strings to raw coordinates

    Args:
        points: "x,y x,y ..." svg points strings.

    Returns:
        ((x,y), (x,y), ...) raw coordinates.
    """
    return tuple(map(string_pair_to_float, points.split(" ")))


def coords_to_points(coords: tuple | list) -> str:
    """Convert raw coordinates to svg points strings

    Args:
        coords: ((x,y), (x,y), ...) raw coordinates.

    Returns:
        "x,y x,y ..." svg points strings.
    """
    return " ".join(map(list_pair_to_string, coords))


def steerlock_to_number(value: str) -> float:
    """Convert steerlock (degree) string to float value"""
    try:
        return float(re.split(r"[\D]", value)[0])
    except (AttributeError, TypeError, ValueError):
        return 0.0
