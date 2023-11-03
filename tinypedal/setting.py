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
import copy

from .const import PLATFORM, PATH_SETTINGS
from .template.template_application import APPLICATION_DEFAULT
from .template.template_module import MODULE_DEFAULT
from .template.template_widget import WIDGET_DEFAULT
from .template.template_classes import CLASSES_DEFAULT
from .template.template_heatmap import HEATMAP_DEFAULT
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
        try:
            # Read JSON file
            with open(f"{self.filepath}{self.filename_setting}", "r", encoding="utf-8") as jsonfile:
                setting_user_unsorted = json.load(jsonfile)
            # Verify & assign setting
            verify_setting(setting_user_unsorted, self.setting_default)
            self.setting_user = copy.deepcopy(setting_user_unsorted)
            # Save setting to JSON file
            self.save(0)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.error("setting loading failed, create backup & revert to default")
            self.backup()
            self.create()
            self.save(0)

        # Assign base setting
        self.application = self.setting_user["application"]
        self.compatibility = self.setting_user["compatibility"]
        self.overlay = self.setting_user["overlay"]
        self.shared_memory_api = self.setting_user["shared_memory_api"]
        self.units = self.setting_user["units"]
        self.last_loaded_setting = self.filename_setting

    def save(self, count=66):
        """Save trigger

        Limit to one save operation for a given period.
        Set time delay(count) that can be refreshed before trigger saving thread.
        Default is roughly one sec delay, use 0 for instant saving.
        """
        self._save_delay = count

        if not self.is_saving:
            self.is_saving = True
            threading.Thread(target=self.__saving).start()
            #logger.info("saving setting")

    def __saving(self):
        """Saving thread"""
        attempts = 5

        # Update save delay
        while self._save_delay > 0:
            self._save_delay -= 1
            #logger.info(f"saving time delay {self._save_delay}")
            time.sleep(0.01)

        # Start saving attempts
        while attempts > 0:
            self.__save_file()
            if self.__verify_file():
                attempts = 0
                #logger.info("verified save file")
            else:
                attempts -= 1
                logger.info("setting saving failed, %s attempt(s) left", attempts)
            time.sleep(0.05)

        self.is_saving = False
        logger.info("setting saved")

    def __save_file(self):
        """Save setting to file"""
        with open(f"{self.filepath}{self.filename_setting}", "w", encoding="utf-8") as jsonfile:
            json.dump(self.setting_user, jsonfile, indent=4)

    def __verify_file(self):
        """Verify save file"""
        try:
            with open(f"{self.filepath}{self.filename_setting}", "r", encoding="utf-8") as jsonfile:
                return json.load(jsonfile) == self.setting_user
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            logger.error("setting verification failed")
            return False

    def create(self):
        """Create default setting"""
        self.setting_user = copy.deepcopy(self.setting_default)

    def backup(self):
        """Backup invalid file"""
        try:
            time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
            shutil.copy(f"{self.filepath}{self.filename_setting}",
                        f"{self.filepath}{self.filename_setting[:-5]}-backup {time_stamp}.json")
        except FileNotFoundError:
            logger.error("setting backup failed")

    def platform_default(self):
        """Platform specific default setting"""
        if PLATFORM != "Windows":
            self.setting_default["application"]["show_at_startup"] = True
            self.setting_default["application"]["minimize_to_tray"] = False


def load_style_config(filepath, filename, default):
    """Load config file"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        logger.error("setting loading failed, fall back to default instead")
        new_dict = copy.deepcopy(default)
        # Save to file if not found
        if not os.path.exists(f"{filepath}{filename}"):
            with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
                json.dump(new_dict, jsonfile, indent=4)
        return new_dict


def verify_setting(dict_user, dict_def):
    """Verify setting"""
    # Check top-level key
    val.setting_validator(dict_user, dict_def)
    # Check sub-level key
    for item in dict_user.keys():  # list each key lists
        val.setting_validator(dict_user[item], dict_def[item])


# Assign config setting
cfg = Setting()
cfg.filename_setting = f"{cfg.load_preset_list()[0]}.json"
cfg.load()
