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
Validator function
"""

from __future__ import annotations
import logging
import os
import re
import time
from math import isfinite
from typing import Any

from .const_common import MAX_SECONDS, TYPE_NUMBER
from .const_file import FileExt
from .regex_pattern import RE_HEX_COLOR

logger = logging.getLogger(__name__)


# Value validate
def infnan2zero(value: Any) -> float | int:
    """Convert invalid value to zero

    Some data from API may contain invalid value
    due to events such as game crash or freeze,
    use this to correct output value.
    """
    if isinstance(value, TYPE_NUMBER) and isfinite(value):
        return value
    return 0


def cbytes2str(bytestring: bytes | Any, char_encoding: str = "utf-8") -> str:
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


def sector_time(sector_time: list | Any, max_time: float = MAX_SECONDS) -> bool:
    """Validate sector time"""
    if isinstance(sector_time, list):
        return max_time not in sector_time
    return max_time != sector_time


def same_session(
    combo_id: str, session_id: tuple[int, int, int],
    last_session_id: tuple[str, int, int, int]) -> bool:
    """Check if same session, car, track combo"""
    return (
        combo_id == last_session_id[0] and
        last_session_id[1] == session_id[0] and
        last_session_id[2] <= session_id[1] and
        last_session_id[3] <= session_id[2]
    )


def value_type(value: Any, default: Any) -> Any:
    """Validate if value is same type as default, return default value if False"""
    if isinstance(value, type(default)):
        return value
    return default


# File validate
def file_last_modified(filepath: str = "", filename: str = "", extension: str = "") -> float:
    """Check file last modified time, 0 if file not exist"""
    filename_full = f"{filepath}{filename}{extension}"
    if os.path.exists(filename_full):
        return os.path.getmtime(filename_full)
    return 0


def image_file(filepath: str, extension: str = FileExt.PNG, max_size: int = 5120000) -> bool:
    """Validate image file path, file format (default PNG), max file size (default < 5MB)"""
    return (
        os.path.exists(filepath) and
        os.path.getsize(filepath) < max_size and
        filepath.lower().endswith(extension)
    )


# Delta list validate
def delta_list(data: list) -> list:
    """Validate delta data list"""
    # Final row value(second column) must be higher than previous row
    if data[-1][1] < data[-2][1]:
        raise ValueError
    # Remove distance greater than half of track length
    half_distance = data[-1][0] * 0.5
    for idx in range(11, 0, -1):
        if data[idx][0] > half_distance:
            data.pop(idx)
    # Delta list must have at least 10 lines of samples
    if len(data) < 10:
        raise ValueError
    return data


# Value type validate
def any_value_type(value: Any, default: Any, target_type: type) -> Any:
    """Convert any value type to target type, revert to default if fails"""
    try:
        return target_type(value)
    except (TypeError, ValueError, OverflowError):
        return default


def dict_value_type(data: dict, default_data: dict) -> dict:
    """Validate and correct dictionary value type"""
    for key, value in data.items():
        data[key] = type(default_data[key])(value)
    return data


# Color validate
def hex_color(color_str: str | Any) -> bool:
    """Validate HEX color string"""
    if isinstance(color_str, str):
        return re.search(RE_HEX_COLOR, color_str, flags=re.IGNORECASE) is not None
    return False


# Time format validate
def clock_format(_format: str) -> bool:
    """Validate clock time format"""
    try:
        time.strftime(_format, time.gmtime(0))
        return True
    except ValueError:
        return False


# Desync check
def position_sync(max_diff: float = 200, max_desync: int = 20):
    """Position synchronization

    Args:
        max_diff: max delta position (meters). Exceeding max delta counts as new lap.
        max_desync: max desync counts.

    Sends:
        pos_curr: current position (meters).

    Yields:
        Synchronized position (meters).
    """
    pos_synced = 0
    desync_count = 0

    while True:
        pos_curr = yield pos_synced
        if pos_curr is None:  # reset
            pos_curr = 0
            pos_synced = 0
            desync_count = 0
            continue
        if pos_synced > pos_curr:
            if desync_count > max_desync or pos_synced - pos_curr > max_diff:
                desync_count = 0  # reset
                pos_synced = pos_curr
            else:
                desync_count += 1
        elif pos_synced < pos_curr:
            pos_synced = pos_curr
            if desync_count:
                desync_count = 0
