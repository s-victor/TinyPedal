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
Validator function
"""

import logging
import os
import re
import math
from functools import wraps

logger = logging.getLogger(__name__)


# Value validate
def infnan2zero(value: any):
    """Convert invalid value to zero

    Some data from API may contain invalid value
    due to events such as game crash or freeze,
    use this to correct output value.
    """
    if isinstance(value, (float, int)) and math.isfinite(value):
        return value
    return 0


def cbytes2str(bytestring: any, char_encoding: str = "utf-8") -> str:
    """Convert bytes to string"""
    if isinstance(bytestring, bytes):
        return bytestring.decode(encoding=char_encoding, errors="replace").rstrip()
    return ""


def sector_time(sec_time: any, magic_num: int = 99999) -> bool:
    """Validate sector time"""
    if isinstance(sec_time, list):
        return magic_num not in sec_time
    return magic_num != sec_time


def allowed_filename(invalid_filename: str, filename: str) -> bool:
    """Validate setting filename"""
    return re.search(invalid_filename, filename.lower()) is None


# Folder validate
def is_folder_exist(folder_name: str) -> None:
    """Create folder if not exist"""
    if not os.path.exists(folder_name):
        logger.info("%s folder does not exist, attemp to create", folder_name)
        try:
            os.mkdir(folder_name)
        except (PermissionError, FileExistsError):
            logger.error("failed to create %s folder", folder_name)


# Delta list validate
def delta_list(data_list: list) -> bool:
    """Validate delta data list"""
    # Compare second column last 2 row values
    if data_list[-1][1] < data_list[-2][1]:
        raise ValueError
    # Remove distance greater than half of track length
    max_dist = data_list[-1][0] * 0.5  # half of track length
    pop_index = tuple(  # add invalid index in reverse order
        (idx for idx in range(11, 0, -1) if data_list[idx][0] > max_dist)
    )
    if pop_index:
        for idx in pop_index:
            data_list.pop(idx)  # del invalid row
        return False  # list modified
    return True  # list no change


# Color validate
def hex_color(color_str: any) -> bool:
    """Validate HEX color string"""
    if isinstance(color_str, str) and bool(re.match("#", color_str)):
        color = re.sub("#", "", color_str)
        if len(color) in [3,6,8]:
            return re.search(r'[^0-9A-F]', color, flags=re.IGNORECASE) is None
    return False


# Module validate
def is_valid_module(module: any, name: str) -> bool:
    """Validate module or widget"""
    try:
        return getattr(module, name)
    except AttributeError:
        logger.warning("detected invalid module file: %s.py", name)
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
