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
Setting file function
"""

from __future__ import annotations
import logging
import os
import time
import json
import shutil
from typing import Callable

from ..file_constants import FileExt
from ..setting_validator import PresetValidator

logger = logging.getLogger(__name__)


def set_backup_timestamp(prefix: str = ".backup-", timestamp: bool = True) -> str:
    """Set backup timestamp"""
    if timestamp:
        time_stamp = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())
    else:
        time_stamp = ""
    return f"{prefix}{time_stamp}"


def copy_setting(dict_user: dict) -> dict:
    """Copy setting"""
    for item in dict_user.values():
        if isinstance(item, dict):
            return {key: item.copy() for key, item in dict_user.items()}
        break
    return dict_user.copy()


def load_setting_json_file(
    filename: str, filepath: str, dict_def: dict, is_global: bool = False
) -> dict:
    """Load setting json file & verify"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            setting_user = json.load(jsonfile)
        # Verify & assign setting
        setting_user = PresetValidator.validate(setting_user, dict_def)
        if is_global:
            logger.info("SETTING: %s loaded (global settings)", filename)
        else:
            logger.info("SETTING: %s loaded (user preset)", filename)
    except (FileNotFoundError, KeyError, ValueError):
        logger.error("SETTING: %s failed loading, fall back to default", filename)
        create_backup_file(filename, filepath, set_backup_timestamp(), show_log=True)
        setting_user = copy_setting(dict_def)
    return setting_user


def load_style_json_file(
    filename: str, filepath: str, dict_def: dict,
    check_missing: bool = False, validator: Callable | None = None
) -> dict:
    """Load style json file"""
    msg_text = "loaded"
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            style_user = json.load(jsonfile)

        # Whether to check and add missing style
        if check_missing:
            if PresetValidator.add_missing_key(tuple(dict_def), style_user, dict_def):
                msg_text = "updated"

        # Whether to validate style
        if validator is not None:
            if validator(style_user):
                create_backup_file(filename, filepath, set_backup_timestamp(), show_log=True)
                msg_text = "updated"

    except (FileNotFoundError, KeyError, ValueError):
        style_user = copy_setting(dict_def)
        if not os.path.exists(f"{filepath}{filename}"):
            logger.info("SETTING: %s not found, create new default", filename)
        else:
            logger.error("SETTING: %s failed loading, fall back to default", filename)
            create_backup_file(filename, filepath, set_backup_timestamp(), show_log=True)
        msg_text = "updated"

    if msg_text == "updated":
        save_json_file(style_user, filename, filepath)

    logger.info("SETTING: %s %s (user preset)", filename, msg_text)
    return style_user


def save_json_file(
    dict_user: dict, filename: str, filepath: str, extension: str = ""
) -> None:
    """Save setting to json file"""
    with open(f"{filepath}{filename}{extension}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, indent=4)


def save_compact_json_file(
    dict_user: dict, filename: str, filepath: str, extension: str = ""
) -> None:
    """Save compact setting to json file"""
    with open(f"{filepath}{filename}{extension}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, separators=(",", ":"))


def verify_json_file(
    dict_user: dict, filename: str, filepath: str, extension: str = ""
) -> bool:
    """Verify saved json file"""
    try:
        with open(f"{filepath}{filename}{extension}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile) == dict_user
    except FileNotFoundError:
        logger.error("SETTING: file not found")
    except (ValueError, OSError):
        logger.error("SETTING: unable to verify file")
    return False


def create_backup_file(
    filename: str, filepath: str, extension: str = FileExt.BAK, show_log: bool = False
) -> None:
    """Create backup file before saving"""
    try:
        shutil.copyfile(
            f"{filepath}{filename}",
            f"{filepath}{filename}{extension}",
        )
        if show_log:
            logger.info("SETTING: backup saved %s", f"{filepath}{filename}{extension}")
    except FileNotFoundError:
        logger.error("SETTING: source file not found")
    except OSError:
        logger.error("SETTING: unable to create backup file")


def restore_backup_file(
    filename: str, filepath: str, extension: str = FileExt.BAK
) -> None:
    """Restore backup file if saving failed"""
    try:
        shutil.copyfile(
            f"{filepath}{filename}{extension}",
            f"{filepath}{filename}",
        )
    except FileNotFoundError:
        logger.error("SETTING: backup file not found")
    except OSError:
        logger.error("SETTING: unable to restore backup file")


def delete_backup_file(
    filename: str, filepath: str, extension: str = FileExt.BAK
) -> None:
    """Delete backup file"""
    try:
        file_path = f"{filepath}{filename}{extension}"
        if os.path.exists(file_path):
            os.remove(file_path)
    except FileNotFoundError:
        logger.error("SETTING: backup file not found")
    except OSError:
        logger.error("SETTING: unable to delete backup file")
