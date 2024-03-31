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

from __future__ import annotations
import logging
import os
import time
import threading
import json
import shutil
from dataclasses import dataclass

from .const import PLATFORM, PATH_SETTINGS, PATH_BRANDLOGO
from .template.setting_application import APPLICATION_DEFAULT
from .template.setting_module import MODULE_DEFAULT
from .template.setting_widget import WIDGET_DEFAULT
from .template.setting_classes import CLASSES_DEFAULT
from .template.setting_heatmap import HEATMAP_DEFAULT
from .setting_validator import validate_key_pair
from . import regex_pattern as rxp
from . import validator as val

logger = logging.getLogger(__name__)


@dataclass
class FileName:
    """File name"""
    setting: str = "default.json"
    classes: str = "classes.json"
    heatmap: str = "heatmap.json"
    brands: str = "brands.json"
    last_setting: str = "None.json"


class Preset:
    """Preset setting"""

    def __init__(self):
        self.setting: dict | None = None
        self.classes: dict | None = None
        self.heatmap: dict | None = None
        self.brands: dict | None = None

    def set_default(self):
        """Set default setting"""
        self.setting = {**APPLICATION_DEFAULT, **MODULE_DEFAULT, **WIDGET_DEFAULT}
        self.classes = CLASSES_DEFAULT
        self.heatmap = HEATMAP_DEFAULT
        self.brands = {}
        self.set_platform_default()

    def set_platform_default(self):
        """Platform default setting"""
        if PLATFORM != "Windows":
            self.setting["application"]["show_at_startup"] = True
            self.setting["application"]["minimize_to_tray"] = False
            self.setting["compatibility"]["enable_bypass_window_manager"] = True


class Setting:
    """Overlay setting"""
    filepath = PATH_SETTINGS

    def __init__(self):
        self.filename = FileName()
        self.default = Preset()
        self.default.set_default()
        self.user = Preset()

        self.active_widget_list = []
        self.active_module_list = []
        self.brands_logo_user = None

        self.is_saving = False
        self._save_delay = 0

    def load(self):
        """Load all setting files"""
        self.user.setting = load_setting_json_file(
            self.filename.setting, self.filepath, self.default.setting)
        # Save setting to JSON file
        self.save(0)
        # Assign base setting
        self.application = self.user.setting["application"]
        self.compatibility = self.user.setting["compatibility"]
        self.overlay = self.user.setting["overlay"]
        self.shared_memory_api = self.user.setting["shared_memory_api"]
        self.units = self.user.setting["units"]
        self.filename.last_setting = self.filename.setting
        # Load style JSON file
        self.user.brands = load_style_json_file(
            self.filename.brands, self.filepath, self.default.brands)
        self.user.classes = load_style_json_file(
            self.filename.classes, self.filepath, self.default.classes)
        self.user.heatmap = load_style_json_file(
            self.filename.heatmap, self.filepath, self.default.heatmap)
        self.brands_logo_user = self.load_brands_logo_list()
        logger.info("SETTING: %s preset loaded", self.filename.last_setting)

    @staticmethod
    def load_brands_logo_list():
        """Load brands logo list"""
        return [
            _filename[:-4] for _filename in os.listdir(PATH_BRANDLOGO)
            if _filename.lower().endswith(".png")
            and os.path.getsize(f"{PATH_BRANDLOGO}{_filename}") < 1024000
        ]

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
        self.user.setting = copy_setting(self.default.setting)

    def save(self, count: int = 66, file_type: str = "setting"):
        """Save trigger, limit to one save operation for a given period.

        Args:
            count:
                Set time delay(count) that can be refreshed before start saving thread.
                Default is roughly one sec delay, use 0 for instant saving.
            file_type:
                Available type: "setting", "brands", "classes", "heatmap".
        """
        self._save_delay = count

        if not self.is_saving:
            self.is_saving = True
            threading.Thread(
                target=self.__saving,
                args=(
                    getattr(self.filename, file_type),
                    self.filepath,
                    getattr(self.user, file_type)
                )
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
        logger.info("SETTING: %s saved", filename)


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
cfg.filename.setting = f"{cfg.load_preset_list()[0]}.json"
cfg.load()
