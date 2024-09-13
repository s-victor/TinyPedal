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
Validator function
"""

from __future__ import annotations
import logging
import os
import re
import time
from functools import wraps
from math import isfinite

TYPE_NUMBER = float, int

logger = logging.getLogger(__name__)


# Value validate
def infnan2zero(value: any) -> (float | int):
    """Convert invalid value to zero

    Some data from API may contain invalid value
    due to events such as game crash or freeze,
    use this to correct output value.
    """
    if isinstance(value, TYPE_NUMBER) and isfinite(value):
        return value
    return 0


def cbytes2str(bytestring: any, char_encoding: str = "utf-8") -> str:
    """Convert bytes to string"""
    if isinstance(bytestring, bytes):
        return bytestring.decode(encoding=char_encoding, errors="replace").rstrip()
    return ""


def allowed_filename(invalid_filename: str, filename: str) -> bool:
    """Validate setting filename"""
    return re.search(invalid_filename, filename.lower()) is None


def string_number(value: str) -> bool:
    """Validate string number"""
    try:
        float(value)
        return True
    except ValueError:
        return False


def sector_time(sec_time: any, magic_num: int = 99999) -> bool:
    """Validate sector time"""
    if isinstance(sec_time, list):
        return magic_num not in sec_time
    return magic_num != sec_time


def same_session(combo_id, session_id, last_session_id) -> bool:
    """Check if same session, car, track combo"""
    return (
        combo_id == last_session_id[0] and
        last_session_id[1] == session_id[0] and
        last_session_id[2] <= session_id[1] and
        last_session_id[3] <= session_id[2]
    )


def value_type(value, default):
    """Validate if value is same type as default, return default value if False"""
    if type(value) == type(default):
        return value
    return default


# Folder validate
def user_data_path(folder_name: str) -> str:
    """Set user data path, create if not exist"""
    if not os.path.exists(folder_name):
        logger.info("%s folder does not exist, attemp to create", folder_name)
        try:
            os.mkdir(folder_name)
        except (PermissionError, FileExistsError, FileNotFoundError):
            logger.error("failed to create %s folder", folder_name)
            return ""
    return folder_name


# Delta list validate
def delta_list(data_list: list) -> list:
    """Validate delta data list"""
    # Final row value(second column) must be higher than previous row
    if data_list[-1][1] < data_list[-2][1]:
        raise ValueError
    # Remove distance greater than half of track length
    half_distance = data_list[-1][0] * 0.5
    for idx in range(11, 0, -1):
        if data_list[idx][0] > half_distance:
            data_list.pop(idx)
    # Delta list must have at least 10 lines of samples
    if len(data_list) < 10:
        raise ValueError
    return data_list


# Color validate
def hex_color(color_str: any) -> bool:
    """Validate HEX color string"""
    if isinstance(color_str, str) and re.match("#", color_str):
        color = color_str[1:]  # remove left-most sharp sign
        if len(color) in [3,6,8]:
            return re.search(r'[^0-9A-F]', color, flags=re.IGNORECASE) is None
    return False


# Module validate
def is_imported_module(module: object, name: str) -> bool:
    """Validate module or widget"""
    try:
        if not name.startswith("_") and getattr(module, name):
            return True
    except AttributeError:
        logger.warning("found unimported file in %s: %s.py", module.__name__, name)
    return False


# Time format validate
def clock_format(_format: str) -> bool:
    """Validate clock time format"""
    try:
        time.strftime(_format, time.gmtime(0))
        return True
    except ValueError:
        return False


# Decorator
def numeric_filter(func):
    """Numeric filter decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if isinstance(value, (list, tuple)):
            return tuple(map(infnan2zero, value))
        return infnan2zero(value)
    return wrapper


def string_filter(func):
    """String filter decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        string = func(*args, **kwargs)
        if isinstance(string, (list, tuple)):
            return list(map(cbytes2str, string))
        return cbytes2str(string)
    return wrapper
