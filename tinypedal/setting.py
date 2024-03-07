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
Setting
"""

import logging
import os
import time
import threading
import json
import shutil

from .const import PLATFORM, PATH_SETTINGS
from .template.setting_application import APPLICATION_DEFAULT
from .template.setting_module import MODULE_DEFAULT
from .template.setting_widget import WIDGET_DEFAULT
from .template.setting_classes import CLASSES_DEFAULT
from .template.setting_heatmap import HEATMAP_DEFAULT
from .setting_validator import validate_key_pair
from . import regex_pattern as rxp
from . import validator as val

logger = logging.getLogger(__name__)


class Setting:
    """Overlay setting"""
    filepath = PATH_SETTINGS
    filename_setting = "default.json"
    filename_classes = "classes.json"
    filename_heatmap = "heatmap.json"
    filename_brands = "brands.json"
    last_loaded_setting = "None.json"
    setting_default = {**APPLICATION_DEFAULT, **MODULE_DEFAULT, **WIDGET_DEFAULT}
    classes_default = CLASSES_DEFAULT
    heatmap_default = HEATMAP_DEFAULT
    brands_default = {}

    def __init__(self):
        self.platform_default()
        self.active_widget_list = []
        self.active_module_list = []
        self.setting_user = None
        self.classes_user = None
        self.heatmap_user = None
        self.brands_user = None

        self.is_saving = False
        self._save_delay = 0

    def load(self):
        """Load all setting files"""
        self.setting_user = load_setting_json_file(
            self.filename_setting, self.filepath, self.setting_default)
        # Save setting to JSON file
        self.save(0)
        # Assign base setting
        self.application = self.setting_user["application"]
        self.compatibility = self.setting_user["compatibility"]
        self.overlay = self.setting_user["overlay"]
        self.shared_memory_api = self.setting_user["shared_memory_api"]
        self.units = self.setting_user["units"]
        self.last_loaded_setting = self.filename_setting
        # Load style JSON file
        self.brands_user = load_style_json_file(
            self.filename_brands, self.filepath, self.brands_default)
        self.classes_user = load_style_json_file(
            self.filename_classes, self.filepath, self.classes_default)
        self.heatmap_user = load_style_json_file(
            self.filename_heatmap, self.filepath, self.heatmap_default)
        logger.info("SETTING: %s preset loaded", self.last_loaded_setting)

    def load_preset_list(self):
        """Load preset list

        JSON file list: modified date, filename
        """
        raw_cfg_list = [
            (os.path.getmtime(f"{self.filepath}{_filename}"), _filename[:-5])
            for _filename in os.listdir(self.filepath)
            if _filename.lower().endswith(".json")
        ]
        if raw_cfg_list:
            raw_cfg_list.sort(reverse=True)  # sort by file modified date
            cfg_list = [
                _filename[1] for _filename in raw_cfg_list
                if val.allowed_filename(rxp.CFG_INVALID_FILENAME, _filename[1])
            ]
            if cfg_list:
                return cfg_list
        return ["default"]

    def create(self):
        """Create default setting"""
        self.setting_user = copy_setting(self.setting_default)

    def save(self, count: int = 66, file_type: str = "setting"):
        """Save trigger, limit to one save operation for a given period.

        Args:
            count:
                Set time delay(count) that can be refreshed before start saving thread.
                Default is roughly one sec delay, use 0 for instant saving.
            file_type:
                Set type of setting file, either "setting" or "classes".
        """
        self._save_delay = count

        if not self.is_saving:
            self.is_saving = True
            if file_type == "classes":
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_classes, self.filepath, self.classes_user)
                ).start()
            elif file_type == "heatmap":
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_heatmap, self.filepath, self.heatmap_user)
                ).start()
            elif file_type == "brands":
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_brands, self.filepath, self.brands_user)
                ).start()
            else:
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_setting, self.filepath, self.setting_user)
                ).start()

    def __saving(self, filename: str, filepath: str, dict_user: dict):
        """Saving thread"""
        attempts = 5

        # Update save delay
        while self._save_delay > 0:
            self._save_delay -= 1
            time.sleep(0.01)

        # Start saving attempts
        while attempts > 0:
            save_json_file(filename, filepath, dict_user)
            if verify_json_file(filename, filepath, dict_user):
                attempts = 0
            else:
                attempts -= 1
                logger.error("SETTING: saving failed, %s attempt(s) left", attempts)
            time.sleep(0.05)

        self.is_saving = False
        logger.info("SETTING: preset saved")

    def platform_default(self):
        """Platform specific default setting"""
        if PLATFORM != "Windows":
            self.setting_default["application"]["show_at_startup"] = True
            self.setting_default["application"]["minimize_to_tray"] = False
            self.setting_default["compatibility"]["enable_bypass_window_manager"] = True


def save_json_file(filename: str, filepath: str, dict_user: dict) -> None:
    """Save setting to json file"""
    with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, indent=4)


def verify_json_file(filename: str, filepath: str, dict_user: dict) -> bool:
    """Verify saved json file"""
    try:
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile) == dict_user
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error("SETTING: saving verification failed")
        return False


def backup_json_file(filename: str, filepath: str) -> None:
    """Backup invalid json file"""
    try:
        time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        shutil.copy(f"{filepath}{filename}",
                    f"{filepath}{filename[:-5]}-backup {time_stamp}.json")
    except FileNotFoundError:
        logger.error("SETTING: backup failed")


def load_setting_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load setting json file & verify"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            temp_setting_user = json.load(jsonfile)
        # Verify & assign setting
        verify_setting(temp_setting_user, dict_def)
        setting_user = copy_setting(temp_setting_user)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error("SETTING: %s failed loading, create backup & revert to default", filename)
        backup_json_file(filename, filepath)
        setting_user = copy_setting(dict_def)
    return setting_user


def load_style_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load style json file"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            style_user = json.load(jsonfile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        style_user = copy_setting(dict_def)
        # Save to file if not found
        if not os.path.exists(f"{filepath}{filename}"):
            logger.info("SETTING: %s not found, create new default", filename)
            save_json_file(filename, filepath, style_user)
        else:
            logger.error("SETTING: %s failed loading, fall back to default", filename)
    return style_user


def verify_setting(dict_user: dict, dict_def: dict) -> None:
    """Verify setting"""
    # Check top-level key
    validate_key_pair(dict_user, dict_def)
    # Check sub-level key
    for item in dict_user.keys():  # list each key lists
        validate_key_pair(dict_user[item], dict_def[item])


def copy_setting(dict_user: dict) -> dict:
    """Copy setting"""
    for _, item in dict_user.items():
        if isinstance(item, dict):
            return {key: item.copy() for key, item in dict_user.items()}
        return dict_user.copy()
    return dict_user.copy()


# Assign config setting
cfg = Setting()
cfg.filename_setting = f"{cfg.load_preset_list()[0]}.json"
cfg.load()
