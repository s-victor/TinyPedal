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

from psutil import version_info
from PySide2.QtCore import qVersion

from . import version, set_global_user_path

# System info
PLATFORM = platform.system()

# App version
VERSION = version.__version__

# Library version
PYTHON_VERSION = ".".join(map(str, sys.version_info[0:3]))
QT_VERSION = qVersion()
PSUTIL_VERSION = ".".join(map(str, version_info))

# App info
APP_NAME = "TinyPedal"
COPYRIGHT = "Copyright (C) 2022-2025 TinyPedal developers"
DESCRIPTION = "A Free and Open Source telemetry overlay application for racing simulation."
LICENSE = "Licensed under the GNU General Public License v3.0 or later."

# URL
URL_WEBSITE = "https://github.com/s-victor/TinyPedal"
URL_USER_GUIDE = "https://github.com/s-victor/TinyPedal/wiki/User-Guide"
URL_FAQ = "https://github.com/s-victor/TinyPedal/wiki/Frequently-Asked-Questions"

# File name
EXE_FILE = "tinypedal.exe"
LOG_FILE = "tinypedal.log"
PID_FILE = "pid.log"

# Global path
PATH_GLOBAL = set_global_user_path(APP_NAME, PLATFORM)
