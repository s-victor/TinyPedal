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
Constants
"""

import platform
from .validator import is_folder_exist


APP_NAME = "TinyPedal"
VERSION = "2.9.2"
PLATFORM = platform.system()
APP_ICON = "images/icon.png"
COPYRIGHT = "Copyright (C) 2022-2023 TinyPedal developers"
DESCRIPTION = "An open-source overlay application for racing simulation."
LICENSE = "Licensed under the GNU General Public License v3.0 or later."
WEBSITE = "https://github.com/s-victor/TinyPedal"


# User data path
if PLATFORM == "Windows":
    PATH_SETTINGS = "settings/"
    PATH_LOG = "./"
    PATH_DELTABEST = "deltabest/"
    PATH_FUEL = PATH_DELTABEST
    PATH_TRACKMAP = "trackmap/"
    is_folder_exist(PATH_SETTINGS)
    is_folder_exist(PATH_DELTABEST)
    is_folder_exist(PATH_TRACKMAP)
else:
    from xdg import BaseDirectory as BD
    PATH_SETTINGS = BD.save_config_path(APP_NAME) + "/"
    PATH_LOG = PATH_SETTINGS
    PATH_DELTABEST = BD.save_data_path(APP_NAME, "deltabest") + "/"
    PATH_FUEL = PATH_DELTABEST
    PATH_TRACKMAP = BD.save_data_path(APP_NAME, "trackmap") + "/"
