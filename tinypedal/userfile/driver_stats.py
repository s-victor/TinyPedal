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
Driver stats file function
"""

from __future__ import annotations
import logging
import json
from dataclasses import dataclass
from typing import KeysView

from ..file_constants import FILE_EXT
from ..userfile.json_setting import (
    set_backup_timestamp,
    save_compact_json_file,
    verify_json_file,
    create_backup_file,
    delete_backup_file,
    restore_backup_file,
)

STATS_FILENAME = "driver"

logger = logging.getLogger(__name__)


@dataclass
class DriverStats:
    """Driver stats data"""

    pb: float = 99999.0  # personal best lap time
    meters: float = 0.0  # meters driven
    seconds: float = 0.0  # seconds spent
    liters: float = 0.0  # fuel consumed
    valid: int = 0  # valid laps
    invalid: int = 0  # invalid laps
    penalties: int = 0
    races: int = 0
    wins: int = 0
    podiums: int = 0

    @classmethod
    def keys(cls) -> KeysView[str]:
        """Get key name list"""
        return cls.__annotations__.keys()


def validate_stats_file(stats_user: dict) -> dict:
    """Validate stats file

    Full validation for every primary key (track name) and secondary key (vehicle name),
    Only required for loading file in Driver Stats Viewer.
    """
    for key in stats_user:
        if not isinstance(stats_user[key], dict):
            stats_user[key] = {}
        sub_value = stats_user[key]
        for sub_key in sub_value:
            if not isinstance(sub_value[sub_key], dict):
                sub_value[sub_key] = {}
    return stats_user


def purge_keys(target_dict: dict) -> dict:
    """Purge unwanted key name"""
    ref_keys = DriverStats.keys()
    for key in tuple(target_dict):
        if key not in ref_keys:
            target_dict.pop(key)
    return target_dict


def get_sub_dict(source: dict, key_name: str) -> dict:
    """Get sub dict, create new if not exist"""
    sub_dict = source.get(key_name, None)
    if not isinstance(sub_dict, dict):
        source[key_name] = {}
        sub_dict = source[key_name]
    return sub_dict


def load_driver_stats(
    key_list: tuple[str, ...], filepath: str
) -> DriverStats:
    """Load driver stats"""
    stats_user = load_stats_json_file(
        filepath=filepath,
        filename=STATS_FILENAME,
    )
    # Get data from matching key
    target_dict = stats_user
    for key in key_list:
        target_dict = target_dict.get(key, None)
        if not isinstance(target_dict, dict):  # not exist, set to default
            return DriverStats()
    # Add data to DriverStats
    try:
        return DriverStats(**purge_keys(target_dict))
    except (KeyError, ValueError, TypeError):
        return DriverStats()


def save_driver_stats(
    key_list: tuple[str, ...], stats_update: DriverStats, filepath: str
) -> None:
    """Save driver stats"""
    if not key_list or not all(key_list):  # ignore invalid key name
        return
    stats_user = load_stats_json_file(
        filepath=filepath,
        filename=STATS_FILENAME,
    )
    # Get data from matching key
    target_dict = stats_user
    for key in key_list:
        target_dict = get_sub_dict(target_dict, key)
    # Update & save new data
    purge_keys(target_dict).update(stats_update.__dict__)
    save_stats_json_file(
        stats_user=stats_user,
        filepath=filepath,
        filename=STATS_FILENAME,
    )


def load_stats_json_file(
    filename: str, filepath: str, extension: str = FILE_EXT.STATS
) -> dict:
    """Load stats json file & verify"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}{extension}", "r", encoding="utf-8") as jsonfile:
            stats_user = json.load(jsonfile)
            if not isinstance(stats_user, dict):
                raise TypeError
            return stats_user
    except FileNotFoundError:
        logger.info("MISSING: %s stats (%s) data", filename, extension)
    except (AttributeError, TypeError, KeyError, ValueError):
        logger.info("MISSING: invalid %s stats (%s) data", filename, extension)
        create_backup_file(f"{filename}{extension}", filepath, set_backup_timestamp(), show_log=True)
    stats_user = {}
    save_compact_json_file(stats_user, filename, filepath, extension)
    return stats_user


def save_stats_json_file(
    stats_user: dict, filename: str, filepath: str, extension: str = FILE_EXT.STATS
) -> None:
    """Save stats to json file"""
    create_backup_file(f"{filename}{extension}", filepath)
    save_compact_json_file(stats_user, filename, filepath, extension)
    if not verify_json_file(stats_user, filename, filepath, extension):
        restore_backup_file(f"{filename}{extension}", filepath)
    else:
        logger.info("USERDATA: %s%s saved", filename, extension)
    delete_backup_file(f"{filename}{extension}", filepath)
