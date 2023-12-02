#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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


def remove_invalid_key(key_list_def: tuple, dict_user: dict):
    """Remove invalid key & value from user dictionary"""
    key_list_user = tuple(dict_user)  # create user key list

    for key in key_list_user:  # loop through user key list
        if key not in key_list_def:  # check each user key in default list
            dict_user.pop(key)  # remove invalid key
            continue

        # Non-dict sub_level values
        if not isinstance(dict_user[key], dict):
            # Bool
            if re.search(rxp.CFG_BOOL, key):
                if not isinstance(dict_user[key], bool):
                    dict_user[key] = bool(dict_user[key])
                continue
            # Color string
            if re.search(rxp.CFG_COLOR, key):
                if not val.hex_color(dict_user[key]):
                    dict_user.pop(key)
                continue
            # API name string
            if re.search(rxp.CFG_API_NAME, key):
                if dict_user[key] not in API_NAME_LIST:
                    dict_user.pop(key)
                continue
            # Font weight string
            if re.search(rxp.CFG_FONT_WEIGHT, key):
                if dict_user[key].lower() not in rxp.FONT_WEIGHT_LIST:
                    dict_user.pop(key)
                continue
            # String
            if re.search(
                fmt.pipe_join(
                    rxp.CFG_FONT_NAME,
                    rxp.CFG_HEATMAP,
                    rxp.CFG_STRING
                ), key):
                if not isinstance(dict_user[key], str):
                    dict_user.pop(key)
                continue
            # Int
            if re.search(rxp.CFG_INTEGER, key):
                if not isinstance(dict_user[key], int) or isinstance(dict_user[key], bool):
                    try:
                        dict_user[key] = int(dict_user[key])
                    except ValueError:
                        dict_user.pop(key)
                continue
            # Anything int or float
            if not isinstance(dict_user[key], float):
                if not isinstance(dict_user[key], int) or isinstance(dict_user[key], bool):
                    #print(key, dict_user[key])
                    dict_user.pop(key)


def add_missing_key(key_list_def: tuple, dict_user: dict, dict_def: dict):
    """Add missing default key to user list"""
    key_list_user = tuple(dict_user)  # create user key list

    for key in key_list_def:  # loop through default key list
        if key not in key_list_user:  # check each default key in user list
            dict_user[key] = dict_def[key]  # add missing item to user


def sort_key_order(key_list_def: tuple, dict_user: dict):
    """Sort user key order according to default key list"""
    for d_key in key_list_def:  # loop through default key list
        for u_key in dict_user:  # loop through user key
            if u_key == d_key:
                temp_key = u_key  # store user key
                temp_value = dict_user[u_key]  # store user value
                dict_user.pop(u_key)  # delete user key
                dict_user[temp_key] = temp_value  # append user key at the end
                break


def validate_key_pair(dict_user: dict, dict_def: dict):
    """Create key-only check list, then validate key"""
    key_list_def = tuple(dict_def)
    remove_invalid_key(key_list_def, dict_user)
    add_missing_key(key_list_def, dict_user, dict_def)
    sort_key_order(key_list_def, dict_user)
