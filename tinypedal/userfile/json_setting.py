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

import logging
import os
import time
import json
import shutil

from ..setting_validator import PresetValidator

logger = logging.getLogger(__name__)
preset_validator = PresetValidator()


def copy_setting(dict_user: dict) -> dict:
    """Copy setting"""
    for item in dict_user.values():
        if isinstance(item, dict):
            return {key: item.copy() for key, item in dict_user.items()}
        break
    return dict_user.copy()


def load_setting_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load setting json file & verify"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            setting_user = json.load(jsonfile)
        # Verify & assign setting
        setting_user = preset_validator.validate(setting_user, dict_def)
    except (FileNotFoundError, ValueError):
        logger.error("SETTING: %s failed loading, create backup & revert to default", filename)
        backup_invalid_json_file(filename, filepath)
        setting_user = copy_setting(dict_def)
    return setting_user


def load_style_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load style json file"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            style_user = json.load(jsonfile)
    except (FileNotFoundError, ValueError):
        style_user = copy_setting(dict_def)
        # Save to file if not found
        if not os.path.exists(f"{filepath}{filename}"):
            logger.info("SETTING: %s not found, create new default", filename)
            save_json_file(filename, filepath, style_user)
        else:
            logger.error("SETTING: %s failed loading, fall back to default", filename)
    return style_user


def save_json_file(filename: str, filepath: str, dict_user: dict) -> None:
    """Save setting to json file"""
    with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, indent=4)


def verify_json_file(filename: str, filepath: str, dict_user: dict) -> bool:
    """Verify saved json file"""
    try:
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile) == dict_user
    except (FileNotFoundError, ValueError):
        logger.error("SETTING: failed saving verification")
        return False


def backup_invalid_json_file(filename: str, filepath: str) -> None:
    """Backup invalid json file before revert to default"""
    try:
        time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        shutil.copyfile(
            f"{filepath}{filename}",
            f"{filepath}{filename[:-5]}-backup {time_stamp}.json"
        )
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed invalid preset backup")


def create_backup_file(filename: str, filepath: str, extension: str = ".bak") -> None:
    """Create backup file before saving"""
    try:
        shutil.copyfile(
            f"{filepath}{filename}",
            f"{filepath}{filename}{extension}"
        )
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed old preset backup")


def restore_backup_file(filename: str, filepath: str, extension: str = ".bak") -> None:
    """Restore backup file if saving failed"""
    try:
        shutil.copyfile(
            f"{filepath}{filename}{extension}",
            f"{filepath}{filename}"
        )
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed old preset restoration")


def delete_backup_file(filename: str, filepath: str, extension: str = ".bak") -> None:
    """Delete backup file"""
    try:
        file_path = f"{filepath}{filename}{extension}"
        if os.path.exists(file_path):
            os.remove(file_path)
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed removing backup file")
