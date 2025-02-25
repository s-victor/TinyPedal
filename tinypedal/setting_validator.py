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
Setting validator function
"""

import re

from . import formatter as fmt
from . import regex_pattern as rxp
from . import validator as val
from .template.setting_heatmap import HEATMAP_DEFAULT_TYRE, HEATMAP_DEFAULT_BRAKE

COMMON_STRINGS = fmt.pipe_join(
    rxp.CFG_FONT_NAME,
    rxp.CFG_HEATMAP,
    rxp.CFG_USER_PATH,
    rxp.CFG_USER_IMAGE,
    rxp.CFG_STRING,
)


class StyleValidator:
    """Style validator"""

    __slots__ = ()

    @staticmethod
    def classes(style_user: dict) -> bool:
        """Vehicle class style validator"""
        save_change = False
        ALIAS = "alias"
        COLOR = "color"
        # Check first entry for old classes format
        for class_name, class_data in style_user.items():
            if not save_change:
                if set(class_data).issubset((ALIAS, COLOR)):
                    break
                else:
                    save_change = True
            # Update old classes format
            for key, value in class_data.items():
                class_data[ALIAS] = key
                class_data[COLOR] = value
                class_data.pop(key)
                break
        # Validate classes entry
        for class_name, class_data in style_user.items():
            if ALIAS not in class_data or not isinstance(class_data[ALIAS], str):
                class_data[ALIAS] = class_name
                save_change = True
            if COLOR not in class_data or not val.hex_color(class_data[COLOR]):
                class_data[COLOR] = fmt.random_color_class(class_name)
                save_change = True
        return save_change

    @staticmethod
    def brakes(style_user: dict) -> bool:
        """Brakes style validator"""
        save_change = False
        FAILURE = "failure_thickness"
        HEATMAP = "heatmap"
        # Validate brakes entry
        for brake_data in style_user.values():
            if FAILURE not in brake_data or not isinstance(brake_data[FAILURE], val.TYPE_NUMBER):
                brake_data[FAILURE] = 0.0
                save_change = True
            if HEATMAP not in brake_data or not isinstance(brake_data[HEATMAP], str):
                brake_data[HEATMAP] = HEATMAP_DEFAULT_BRAKE
                save_change = True
        return save_change

    @staticmethod
    def compounds(style_user: dict) -> bool:
        """Tyre compound style validator"""
        save_change = False
        SYMBOL = "symbol"
        HEATMAP = "heatmap"
        # Validate compound entry
        for compound_data in style_user.values():
            if SYMBOL not in compound_data or not isinstance(compound_data[SYMBOL], str):
                compound_data[SYMBOL] = "?"
                save_change = True
            if HEATMAP not in compound_data or not isinstance(compound_data[HEATMAP], str):
                compound_data[HEATMAP] = HEATMAP_DEFAULT_TYRE
                save_change = True
        return save_change


class ValueValidator:
    """Value validator"""

    __slots__ = ()

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
        if not val.hex_color(dict_user[key]):
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
        if not val.clock_format(dict_user[key]):
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

    __slots__ = (
        "_value_validators",
    )

    def __init__(self) -> None:
        """Set validator methods in ordered list"""
        self._value_validators = (
            ValueValidator.boolean,
            ValueValidator.color,
            ValueValidator.choice_units,
            ValueValidator.choice_common,
            ValueValidator.clock_format,
            ValueValidator.string,
            ValueValidator.integer,
            ValueValidator.numeric,
        )

    def remove_invalid_key(self, key_list_def: tuple, dict_user: dict) -> None:
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
            for _validator in self._value_validators:
                if _validator(key, dict_user):
                    break

    @staticmethod
    def add_missing_key(key_list_def: tuple, dict_user: dict, dict_def: dict) -> None:
        """Add missing default key to user list"""
        key_list_user = tuple(dict_user)  # create user key list

        for key in key_list_def:  # loop through default key list
            if key not in key_list_user:  # check each default key in user list
                dict_user[key] = dict_def[key]  # add missing item to user

    @staticmethod
    def sort_key_order(key_list_def: tuple, dict_user: dict) -> None:
        """Sort user key order according to default key list"""
        for d_key in key_list_def:  # loop through default key list
            temp_value = dict_user[d_key]  # store user value
            dict_user.pop(d_key)  # delete user key
            dict_user[d_key] = temp_value  # append user key at the end

    def validate_key_pair(self, dict_user: dict, dict_def: dict) -> None:
        """Create key-only check list, then validate key"""
        key_list_def = tuple(dict_def)
        self.remove_invalid_key(key_list_def, dict_user)
        self.add_missing_key(key_list_def, dict_user, dict_def)
        self.sort_key_order(key_list_def, dict_user)

    def validate(self, dict_user: dict, dict_def: dict) -> dict:
        """Validate setting"""
        # Check top-level key
        self.validate_key_pair(dict_user, dict_def)
        # Check sub-level key
        for item in dict_user.keys():  # list each key lists
            self.validate_key_pair(dict_user[item], dict_def[item])
        return dict_user
