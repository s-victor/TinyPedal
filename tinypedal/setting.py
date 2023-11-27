#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
from . import validator as val

logger = logging.getLogger(__name__)


class Setting:
    """Overlay setting"""
    filepath = PATH_SETTINGS
    filename_setting = "default.json"
    filename_classes = "classes.json"
    filename_heatmap = "heatmap.json"
    last_loaded_setting = "None.json"
    setting_default = {**APPLICATION_DEFAULT, **MODULE_DEFAULT, **WIDGET_DEFAULT}
    heatmap_default = HEATMAP_DEFAULT
    classes_default = CLASSES_DEFAULT

    def __init__(self):
        self.platform_default()
        self.active_widget_list = []
        self.active_module_list = []
        self.setting_user = {}
        self.classes_user = {}
        self.heatmap_user = {}

        self.is_saving = False
        self._save_delay = 0

    def load(self):
        """Load all setting files"""
        self.__load_setting()
        self.classes_user = load_style_config(
            self.filepath, self.filename_classes, CLASSES_DEFAULT)
        self.heatmap_user = load_style_config(
            self.filepath, self.filename_heatmap, HEATMAP_DEFAULT)

    def load_preset_list(self):
        """Load preset list"""
        # Create json file list: modified date, filename
        raw_cfg_list = [(os.path.getmtime(f"{self.filepath}{fname}"), fname[:-5])
                        for fname in os.listdir(self.filepath) if fname.endswith(".json")]
        if raw_cfg_list:
            raw_cfg_list.sort(reverse=True)  # sort by file modified date
            cfg_list = [fname[1] for fname in raw_cfg_list if val.setting_filename(fname[1])]
            if cfg_list:
                return cfg_list
        return ["default"]

    def __load_setting(self):
        """Load & verify setting"""
        filename = self.filename_setting
        try:
            # Read JSON file
            with open(f"{self.filepath}{filename}", "r", encoding="utf-8") as jsonfile:
                temp_setting_user = json.load(jsonfile)
            # Verify & assign setting
            verify_setting(temp_setting_user, self.setting_default)
            self.setting_user = copy_setting(temp_setting_user)
            # Save setting to JSON file
            self.save(0)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.error("setting loading failed, create backup & revert to default")
            backup_json_file(filename, self.filepath)
            self.create()
            self.save(0)

        # Assign base setting
        self.application = self.setting_user["application"]
        self.compatibility = self.setting_user["compatibility"]
        self.overlay = self.setting_user["overlay"]
        self.shared_memory_api = self.setting_user["shared_memory_api"]
        self.units = self.setting_user["units"]
        self.last_loaded_setting = filename

    def create(self):
        """Create default setting"""
        self.setting_user = copy_setting(self.setting_default)

    def save(self, count=66, file_type="setting"):
        """Save trigger

        Limit to one save operation for a given period.
        Set time delay(count) that can be refreshed before trigger saving thread.
        Default is roughly one sec delay, use 0 for instant saving.
        """
        self._save_delay = count

        if not self.is_saving:
            self.is_saving = True
            if file_type == "classes":
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_classes, self.filepath, self.classes_user)
                ).start()
            else:
                threading.Thread(
                    target=self.__saving,
                    args=(self.filename_setting, self.filepath, self.setting_user)
                ).start()
            #logger.info("saving setting")

    def __saving(self, filename, filepath, dict_user):
        """Saving thread"""
        attempts = 5

        # Update save delay
        while self._save_delay > 0:
            self._save_delay -= 1
            #logger.info(f"saving time delay {self._save_delay}")
            time.sleep(0.01)

        # Start saving attempts
        while attempts > 0:
            save_json_file(filename, filepath, dict_user)
            if verify_json_file(filename, filepath, dict_user):
                attempts = 0
                #logger.info("verified save file")
            else:
                attempts -= 1
                logger.info("setting saving failed, %s attempt(s) left", attempts)
            time.sleep(0.05)

        self.is_saving = False
        logger.info("setting saved")

    def platform_default(self):
        """Platform specific default setting"""
        if PLATFORM != "Windows":
            self.setting_default["application"]["show_at_startup"] = True
            self.setting_default["application"]["minimize_to_tray"] = False
            self.setting_default["compatibility"]["enable_bypass_window_manager"] = True


def save_json_file(filename: str, filepath: str, dict_user: dict):
    """Save setting to json file"""
    with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, indent=4)


def verify_json_file(filename: str, filepath: str, dict_user: dict):
    """Verify saved json file"""
    try:
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile) == dict_user
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error("save file verification failed")
        return False


def backup_json_file(filename: str, filepath: str):
    """Backup invalid json file"""
    try:
        time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        shutil.copy(f"{filepath}{filename}",
                    f"{filepath}{filename[:-5]}-backup {time_stamp}.json")
    except FileNotFoundError:
        logger.error("setting backup failed")


def load_style_config(filepath: str, filename: str, default: dict) -> dict:
    """Load config file"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error("setting loading failed, fall back to default instead")
        new_dict = copy_setting(default)
        # Save to file if not found
        if not os.path.exists(f"{filepath}{filename}"):
            with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
                json.dump(new_dict, jsonfile, indent=4)
        return new_dict


def verify_setting(dict_user: dict, dict_def: dict) -> None:
    """Verify setting"""
    # Check top-level key
    val.setting_validator(dict_user, dict_def)
    # Check sub-level key
    for item in dict_user.keys():  # list each key lists
        val.setting_validator(dict_user[item], dict_def[item])


def copy_setting(dict_user: dict) -> dict:
    """Copy setting"""
    return {key: item.copy() for key, item in dict_user.items()}


# Assign config setting
cfg = Setting()
cfg.filename_setting = f"{cfg.load_preset_list()[0]}.json"
cfg.load()
