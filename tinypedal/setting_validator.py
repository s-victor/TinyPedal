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
Setting validator function
"""

from __future__ import annotations

import re

from . import regex_pattern as rxp
from .const_common import TYPE_NUMBER
from .formatter import random_color_class
from .template.setting_heatmap import HEATMAP_DEFAULT_BRAKE, HEATMAP_DEFAULT_TYRE
from .validator import is_clock_format, is_hex_color

COMMON_STRINGS = "|".join((
    rxp.CFG_FONT_NAME,
    rxp.CFG_HEATMAP,
    rxp.CFG_USER_PATH,
    rxp.CFG_USER_IMAGE,
    rxp.CFG_STRING,
))


class StyleValidator:
    """Style validator"""

    @staticmethod
    def classes(style_user: dict) -> bool:
        """Vehicle class style validator"""
        save_change = False
        _alias = "alias"
        _color = "color"
        # Check first entry for old classes format
        for class_name, class_data in style_user.items():
            if not save_change:
                if set(class_data).issubset((_alias, _color)):
                    break
                else:
                    save_change = True
            # Update old classes format
            for key, value in class_data.items():
                class_data[_alias] = key
                class_data[_color] = value
                class_data.pop(key)
                break
        # Validate classes entry
        for class_name, class_data in style_user.items():
            if _alias not in class_data or not isinstance(class_data[_alias], str):
                class_data[_alias] = class_name
                save_change = True
            if _color not in class_data or not is_hex_color(class_data[_color]):
                class_data[_color] = random_color_class(class_name)
                save_change = True
        return save_change

    @staticmethod
    def brakes(style_user: dict) -> bool:
        """Brakes style validator"""
        save_change = False
        _failure = "failure_thickness"
        _heatmap = "heatmap"
        # Validate brakes entry
        for brake_data in style_user.values():
            if _failure not in brake_data or not isinstance(brake_data[_failure], TYPE_NUMBER):
                brake_data[_failure] = 0.0
                save_change = True
            if _heatmap not in brake_data or not isinstance(brake_data[_heatmap], str):
                brake_data[_heatmap] = HEATMAP_DEFAULT_BRAKE
                save_change = True
        return save_change

    @staticmethod
    def compounds(style_user: dict) -> bool:
        """Tyre compound style validator"""
        save_change = False
        _symbol = "symbol"
        _heatmap = "heatmap"
        # Validate compound entry
        for compound_data in style_user.values():
            if _symbol not in compound_data or not isinstance(compound_data[_symbol], str):
                compound_data[_symbol] = "?"
                save_change = True
            if _heatmap not in compound_data or not isinstance(compound_data[_heatmap], str):
                compound_data[_heatmap] = HEATMAP_DEFAULT_TYRE
                save_change = True
        return save_change

    @staticmethod
    def filelock(lock_user: dict) -> bool:
        """File lock validator"""
        save_change = False
        _version = "version"
        for file_name, file_info in lock_user.items():
            if not isinstance(file_info, dict):
                lock_user[file_name] = {_version: "unknown"}
                save_change = True
                continue
            if _version not in file_info or not isinstance(file_info[_version], str):
                lock_user[file_name] = {_version: "unknown"}
                save_change = True
        return save_change


class ValueValidator:
    """Value validator"""

    @staticmethod
    def boolean(key: str, dict_user: dict) -> bool:
        """Value - Boolean"""
        if not re.search(rxp.CFG_BOOL, key):
            return False
        if not isinstance(dict_user[key], bool):
            dict_user[key] = bool(dict_user[key])
        return True

    @staticmethod
    def color(key: str, dict_user: dict) -> bool:
        """Value - Color string"""
        if not re.search(rxp.CFG_COLOR, key):
            return False
        if not is_hex_color(dict_user[key]):
            dict_user.pop(key)
        return True

    @staticmethod
    def choice_units(key: str, dict_user: dict) -> bool:
        """Value - units choice list"""
        for ref_key, choice_list in rxp.CHOICE_UNITS.items():
            if re.search(ref_key, key):
                if dict_user[key] not in choice_list:
                    dict_user.pop(key)
                return True
        return False

    @staticmethod
    def choice_common(key: str, dict_user: dict) -> bool:
        """Value - common choice list"""
        for ref_key, choice_list in rxp.CHOICE_COMMON.items():
            if re.search(ref_key, key):
                if dict_user[key] not in choice_list:
                    dict_user.pop(key)
                return True
        return False

    @staticmethod
    def clock_format(key: str, dict_user: dict) -> bool:
        """Value - clock format string"""
        if not re.search(rxp.CFG_CLOCK_FORMAT, key):
            return False
        if not is_clock_format(dict_user[key]):
            dict_user.pop(key)
        return True

    @staticmethod
    def string(key: str, dict_user: dict) -> bool:
        """Value - string"""
        if not re.search(COMMON_STRINGS, key):
            return False
        if not isinstance(dict_user[key], str):
            dict_user.pop(key)
        return True

    @staticmethod
    def integer(key: str, dict_user: dict) -> bool:
        """Value - integer"""
        if not re.search(rxp.CFG_INTEGER, key):
            return False
        if not isinstance(dict_user[key], int) or isinstance(dict_user[key], bool):
            dict_user.pop(key)
        return True

    @staticmethod
    def numeric(key: str, dict_user: dict) -> bool:
        """Value - numeric"""
        if not isinstance(dict_user[key], (float, int)) or isinstance(dict_user[key], bool):
            dict_user.pop(key)
        return True


class PresetValidator:
    """Preset validator"""

    # Set validator methods in ordered list
    _value_validators = (
        ValueValidator.boolean,
        ValueValidator.color,
        ValueValidator.choice_units,
        ValueValidator.choice_common,
        ValueValidator.clock_format,
        ValueValidator.string,
        ValueValidator.integer,
        ValueValidator.numeric,
    )

    @classmethod
    def remove_invalid_key(cls, key_list_def: tuple[str, ...], dict_user: dict) -> None:
        """Remove invalid key & value from user dictionary"""
        key_list_user = tuple(dict_user)  # create user key list

        for key in key_list_user:  # loop through user key list
            if key not in key_list_def:  # check each user key in default list
                dict_user.pop(key)  # remove invalid key
                continue
            # Skip sub_level dict
            if isinstance(dict_user[key], dict):
                continue
            # Validate values
            for _validator in cls._value_validators:
                if _validator(key, dict_user):
                    break

    @staticmethod
    def add_missing_key(key_list_def: tuple[str, ...], dict_user: dict, dict_def: dict) -> bool:
        """Add missing default key to user list"""
        is_modified = False
        key_list_user = tuple(dict_user)  # create user key list

        for key in key_list_def:  # loop through default key list
            if key not in key_list_user:  # check each default key in user list
                dict_user[key] = dict_def[key]  # add missing item to user
                is_modified = True

        return is_modified

    @staticmethod
    def sort_key_order(key_list_def: tuple[str, ...], dict_user: dict) -> None:
        """Sort user key order according to default key list"""
        for d_key in key_list_def:  # loop through default key list
            temp_value = dict_user[d_key]  # store user value
            dict_user.pop(d_key)  # delete user key
            dict_user[d_key] = temp_value  # append user key at the end

    @classmethod
    def validate_key_pair(cls, dict_user: dict, dict_def: dict) -> None:
        """Create key-only check list, then validate key"""
        key_list_def = tuple(dict_def)
        cls.remove_invalid_key(key_list_def, dict_user)
        cls.add_missing_key(key_list_def, dict_user, dict_def)
        cls.sort_key_order(key_list_def, dict_user)

    @classmethod
    def validate(cls, dict_user: dict, dict_def: dict) -> dict:
        """Validate setting"""
        # Check top-level key
        cls.validate_key_pair(dict_user, dict_def)
        # Check sub-level key
        for item in dict_user.keys():  # list each key lists
            cls.validate_key_pair(dict_user[item], dict_def[item])
        return dict_user
