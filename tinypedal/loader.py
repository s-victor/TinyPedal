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
Loader function
"""

import logging

from .setting import cfg
from .api_control import api
from .module_control import mctrl, wctrl
from .overlay_control import octrl

logger = logging.getLogger(__name__)


def load():
    """Load api, modules, widgets"""
    logger.info("STARTING............")
    api.connect()
    api.start()     # 1 start api
    load_modules()  # 2 load modules


def reload():
    """Reload api, modules, widgets"""
    logger.info("RELOADING............")
    unload_modules()  # 1 unload modules
    cfg.load()        # 2 reload setting
    api.restart()     # 3 restart api
    load_modules()    # 4 load modules


def unload():
    """unload api, modules, widgets"""
    logger.info("CLOSING............")
    unload_modules()  # 1 unload modules
    api.stop()        # 2 stop api


def load_modules():
    """Load modules, widgets"""
    octrl.enable()  # 1 overlay control
    mctrl.start()   # 2 module
    wctrl.start()   # 3 widget


def unload_modules():
    """Unload modules, widgets"""
    wctrl.close()    # 1 widget
    mctrl.close()    # 2 module
    octrl.disable()  # 3 overlay control
