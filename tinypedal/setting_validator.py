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
from .api_connector import API_NAME_LIST

COMMON_STRINGS = fmt.pipe_join(rxp.CFG_FONT_NAME,rxp.CFG_HEATMAP,rxp.CFG_STRING)


class ValueValidator:
    """Value validator"""

    def __init__(self) -> None:
        """Set validator methods in ordered list"""
        self.types = (
            self.boolean,
            self.color,
            self.api_name,
            self.font_weight,
            self.encoding,
            self.deltabest,
            self.clock_format,
            self.string,
            self.integer,
            self.numeric,
        )

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
    def api_name(key: str, dict_user: dict) -> bool:
        """Value - API name string"""
        if not re.search(rxp.CFG_API_NAME, key):
            return False
        if dict_user[key] not in API_NAME_LIST:
            dict_user.pop(key)
        return True

    @staticmethod
    def font_weight(key: str, dict_user: dict) -> bool:
        """Value - font weight string"""
        if not re.search(rxp.CFG_FONT_WEIGHT, key):
            return False
        if dict_user[key].lower() not in rxp.FONT_WEIGHT_LIST:
            dict_user.pop(key)
        return True

    @staticmethod
    def encoding(key: str, dict_user: dict) -> bool:
        """Value - encoding string"""
        if not re.search(rxp.CFG_ENCODING, key):
            return False
        if dict_user[key] not in rxp.ENCODING_LIST:
            dict_user.pop(key)
        return True

    @staticmethod
    def deltabest(key: str, dict_user: dict) -> bool:
        """Value - deltabest string"""
        if not re.search(rxp.CFG_DELTABEST, key):
            return False
        if dict_user[key] not in rxp.DELTABEST_LIST:
            dict_user.pop(key)
        return True

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

    def __init__(self) -> None:
        self.value_validator = ValueValidator()

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
            for _validator in self.value_validator.types:
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


preset_validator = PresetValidator()
