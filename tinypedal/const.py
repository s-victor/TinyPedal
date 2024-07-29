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
Constants
"""

import sys
import platform
from .validator import is_folder_exist

from PySide2.QtCore import qVersion


VERSION = "2.16.0"
APP_NAME = "TinyPedal"
PLATFORM = platform.system()
APP_ICON = "images/icon.png"
COPYRIGHT = "Copyright (C) 2022-2024 TinyPedal developers"
DESCRIPTION = "A Free and Open Source telemetry overlay application for racing simulation."
LICENSE = "Licensed under the GNU General Public License v3.0 or later."
WEBSITE = "https://github.com/s-victor/TinyPedal"

# Library version
PYTHON_VERSION = ".".join(str(num) for num in sys.version_info[0:3])
QT_VERSION = qVersion()

# User data path
if PLATFORM == "Windows":
    PATH_SETTINGS = "settings/"
    PATH_LOG = "./"
    PATH_DELTABEST = "deltabest/"
    PATH_ENERGY = PATH_DELTABEST
    PATH_FUEL = PATH_DELTABEST
    PATH_SECTORBEST = PATH_DELTABEST
    PATH_TRACKMAP = "trackmap/"
    PATH_BRANDLOGO = "brandlogo/"
    is_folder_exist(PATH_SETTINGS)
    is_folder_exist(PATH_DELTABEST)
    is_folder_exist(PATH_TRACKMAP)
    is_folder_exist(PATH_BRANDLOGO)
else:
    from xdg import BaseDirectory as BD
    PATH_SETTINGS = BD.save_config_path(APP_NAME) + "/"
    PATH_LOG = PATH_SETTINGS
    PATH_DELTABEST = BD.save_data_path(APP_NAME, "deltabest") + "/"
    PATH_ENERGY = PATH_DELTABEST
    PATH_FUEL = PATH_DELTABEST
    PATH_SECTORBEST = PATH_DELTABEST
    PATH_TRACKMAP = BD.save_data_path(APP_NAME, "trackmap") + "/"
    PATH_BRANDLOGO = BD.save_data_path(APP_NAME, "brandlogo") + "/"
