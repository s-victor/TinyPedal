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
Validator function
"""

import logging
import os
import re
import math
from functools import wraps

from . import regex_pattern as rxp

logger = logging.getLogger(__name__)


# Value validate
def infnan2zero(value):
    """Convert invalid value to zero

    Some data from API may contain invalid value
    due to events such as game crash or freeze,
    use this to correct output value.
    """
    if isinstance(value, (float, int)) and math.isfinite(value):
        return value
    return 0


def cbytes2str(bytestring):
    """Convert bytes to string"""
    if isinstance(bytestring, bytes):
        return bytestring.decode(encoding="iso-8859-1", errors="replace").rstrip()
    return ""


def numeric_filter(func):
    """Numeric filter decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if isinstance(value, (list, tuple)):
            return tuple(map(infnan2zero, value))
        return infnan2zero(value)
    return wrapper


def string_filter(func):
    """String filter decorator"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        string = func(*args, **kwargs)
        if isinstance(string, (list, tuple)):
            return list(map(cbytes2str, string))
        return cbytes2str(string)
    return wrapper


def sector_time(sec_time, magic_num=99999):
    """Validate sector time"""
    if isinstance(sec_time, list):
        if magic_num not in sec_time:
            return True
    else:
        if magic_num != sec_time:
            return True
    return False


# Folder validate
def is_folder_exist(folder_name):
    """Create folder if not exist"""
    if not os.path.exists(folder_name):
        logger.info("%s folder does not exist, attemp to create", folder_name)
        try:
            os.mkdir(folder_name)
        except (PermissionError, FileExistsError):
            logger.error("failed to create %s folder", folder_name)


# Delta list validate
def delta_list(listname):
    """Validate delta data list"""
    # Compare second column last 2 row values
    if listname[-1][1] < listname[-2][1]:
        raise ValueError
    # Remove distance greater than half of track length
    max_dist = listname[-1][0] * 0.5  # half of track length
    pop_index = tuple(  # add invalid index in reverse order
        (idx for idx in range(11, 0, -1) if listname[idx][0] > max_dist)
    )
    if pop_index:
        for idx in pop_index:
            listname.pop(idx)  # del invalid row
        return False  # list modified
    return True  # list no change


# Color validate
def color_validator(color_str):
    """Validate color value"""
    if isinstance(color_str, str) and bool(re.match("#", color_str)):
        color = re.sub("#", "", color_str)
        if len(color) in [3,6,8]:
            return re.search(r'[^0-9A-F]', color, re.I) is None
    return False


def verify_heatmap(heatmap_dict):
    """Create color list & verify"""
    for color in list(heatmap_dict.values()):
        if not color_validator(color):
            return False
    return True


# Setting validate
def setting_filename(filename):
    """Validate setting filename"""
    return re.search(rxp.INVALID_SETTING_FILENAME, filename.lower()) is None


def remove_invalid_setting(key_list_def, dict_user):
    """Remove invalid key & value from user dictionary"""
    key_list_user = tuple(dict_user)  # create user key list

    for key in key_list_user:  # loop through user key list
        if key not in key_list_def:  # check each user key in default list
            dict_user.pop(key)  # remove invalid key
            continue

        # Non-dict sub_level values
        if type(dict_user[key]) != dict:
            # Bool
            if re.search(rxp.BOOL, key):
                if type(dict_user[key]) != bool:
                    dict_user[key] = bool(dict_user[key])
                continue
            # Color string
            if re.search(rxp.COLOR, key):
                if not color_validator(dict_user[key]):
                    dict_user.pop(key)
                continue
            # Font weight string
            if re.search(rxp.FONTWEIGHT, key):
                if dict_user[key].lower() not in ("normal", "bold"):
                    dict_user.pop(key)
                continue
            # String
            if re.search(
                rxp.FONTNAME + "|" +
                rxp.HEATMAP + "|" +
                rxp.STRING,
                key):
                if type(dict_user[key]) != str:
                    dict_user.pop(key)
                continue
            # Int
            if re.search(rxp.INTEGER, key):
                if type(dict_user[key]) != int:
                    try:
                        dict_user[key] = int(dict_user[key])
                    except ValueError:
                        dict_user.pop(key)
                continue
            # Anything int or float
            if not isinstance(dict_user[key], float):
                if type(dict_user[key]) != int:  # exclude bool
                    #print(key, dict_user[key])
                    dict_user.pop(key)


def add_missing_setting(key_list_def, dict_user, dict_def):
    """Adding missing default key to user list"""
    key_list_user = tuple(dict_user)  # create user key list

    for key in key_list_def:  # loop through default key list
        if key not in key_list_user:  # check each default key in user list
            dict_user[key] = dict_def[key]  # add missing item to user


def sort_setting(key_list_def, dict_user):
    """Sort user key order according to default key list"""
    for d_key in key_list_def:  # loop through default key list
        for u_key in dict_user:  # loop through user key
            if u_key == d_key:
                temp_key = u_key  # store user key
                temp_value = dict_user[u_key]  # store user value
                dict_user.pop(u_key)  # delete user key
                dict_user[temp_key] = temp_value  # append user key at the end
                break


def setting_validator(dict_user, dict_def):
    """Create key-only check list to avoid error, then validate key"""
    key_list_def = tuple(dict_def)
    remove_invalid_setting(key_list_def, dict_user)
    add_missing_setting(key_list_def, dict_user, dict_def)
    sort_setting(key_list_def, dict_user)
