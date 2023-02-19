#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Overlay setting
"""

import os
import re
import time
import json
import shutil
import copy

from .const import PATH_SETTINGS, PATH_CLASSES
from .setting_template import SETTING_DEFAULT, CLASSES_DEFAULT


class Setting:
    """Overlay setting"""
    filepath = PATH_SETTINGS
    filename = "default.json"
    setting_default = SETTING_DEFAULT

    def __init__(self):
        self.active_widget_list = []  # create active widget list
        self.setting_user = {}
        self.overlay = {}

    def load_preset_list(self):
        """Load preset list"""
        raw_cfg_list = [(os.path.getmtime(f"{self.filepath}{data}"), data[:-5])
                        for data in os.listdir(self.filepath) if data.endswith(".json")]
        raw_cfg_list.sort(reverse=True)  # sort by file modified date

        if raw_cfg_list:
            cfg_list = [data[1] for data in raw_cfg_list
                        if re.search('backup', data[1].lower()) is None  # ignore backup file
                        and re.search('classes', data[1].lower()) is None  # ignore classes file
                        ]
            if cfg_list:
                return cfg_list
        return ["default"]

    def load(self):
        """Load & validate setting"""
        try:
            # Read JSON file
            with open(f"{self.filepath}{self.filename}", "r", encoding="utf-8") as jsonfile:
                setting_user_unsorted = json.load(jsonfile)

            # Verify setting
            verify_setting(setting_user_unsorted, self.setting_default)

            # Assign verified setting
            self.setting_user = setting_user_unsorted

            # Save setting to JSON file
            self.save()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.backup()
            self.create()
            self.save()

        # Assign base setting
        self.overlay = self.setting_user["overlay"]

    def save(self):
        """Save setting to file"""
        with open(f"{self.filepath}{self.filename}", "w", encoding="utf-8") as jsonfile:
            json.dump(self.setting_user, jsonfile, indent=4)

    def create(self):
        """Create default setting"""
        self.setting_user = copy.deepcopy(self.setting_default)

    def backup(self):
        """Backup invalid file"""
        try:
            time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
            shutil.copy(f"{self.filepath}{self.filename}",
                        f"{self.filepath}{self.filename[:-5]}-backup {time_stamp}.json")
        except FileNotFoundError:
            pass


class VehicleClass:
    """Vehicle class dictionary"""
    filepath = PATH_CLASSES
    filename = "classes.json"
    classdict_default = CLASSES_DEFAULT

    def __init__(self):
        self.classdict_user = {}
        self.load()

    def load(self):
        """Load dictionary file"""
        try:
            # Load file
            with open(f"{self.filepath}{self.filename}", "r", encoding="utf-8") as jsonfile:
                self.classdict_user = json.load(jsonfile)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # create a default copy if not found
            self.classdict_user = copy.deepcopy(self.classdict_default)
            self.save()

    def save(self):
        """Save dictionary to file"""
        with open(f"{self.filepath}{self.filename}", "w", encoding="utf-8") as jsonfile:
            json.dump(self.classdict_user, jsonfile, indent=4)


def check_invalid_key(key_list_def, key_list_user, dict_user):
    """First step, check & remove invalid key from user list"""
    for key in key_list_user:  # loop through user key list
        if key not in key_list_def:  # check each user key in default list
            dict_user.pop(key)  # remove invalid key


def check_missing_key(key_list_def, key_list_user, dict_user, dict_def):
    """Second step, adding missing default key to user list"""
    for key in key_list_def:  # loop through default key list
        if key not in key_list_user:  # check each default key in user list
            dict_user[key] = dict_def[key]  # add missing item to user


def sort_key_order(key_list_def, dict_user):
    """Third step, sort user key order according to default key list"""
    for d_key in key_list_def:  # loop through default key list
        for u_key in dict_user:  # loop through user key
            if u_key == d_key:
                temp_key = u_key  # store user key
                temp_value = dict_user[u_key]  # store user value
                dict_user.pop(u_key)  # delete user key
                dict_user[temp_key] = temp_value  # append user key at the end
                break


def check_key(dict_user, dict_def):
    """Create key-only check list to avoid error, then validate key"""
    key_list_def = tuple(dict_def)
    key_list_user = tuple(dict_user)
    check_invalid_key(key_list_def, key_list_user, dict_user)
    check_missing_key(key_list_def, key_list_user, dict_user, dict_def)
    sort_key_order(key_list_def, dict_user)


def verify_setting(dict_user, dict_def):
    """Verify setting"""
    # Check top-level key
    check_key(dict_user, dict_def)
    # Check sub-level key
    for item in dict_user.keys():  # list each key lists
        check_key(dict_user[item], dict_def[item])


# Assign setting
cfg = Setting()
cfg.filename = f"{cfg.load_preset_list()[0]}.json"
cfg.load()
