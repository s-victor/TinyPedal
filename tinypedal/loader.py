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
import signal

from .api_control import api
from .const_file import FileExt
from .module_control import mctrl, wctrl
from .overlay_control import octrl
from .setting import ConfigType, cfg

logger = logging.getLogger(__name__)


def start():
    """Start api, modules, widgets, etc. Call once per launch."""
    logger.info("STARTING............")
    # 1 load global
    cfg.load_global()
    cfg.save(cfg_type=ConfigType.CONFIG)
    # 2 load preset
    cfg.filename.setting = f"{cfg.preset_list[0]}{FileExt.JSON}"
    cfg.load()
    cfg.save()
    # 3 start api
    api.connect()
    api.start()
    # 4 start modules
    mctrl.start()
    # 5 start widgets
    wctrl.start()
    # 6 start main window
    from .ui.app import AppWindow
    config_window = AppWindow()
    signal.signal(signal.SIGINT, config_window.int_signal_handler)

    # Finalize loading after main GUI fully loaded
    logger.info("FINALIZING............")
    # 1 Enable overlay control
    octrl.enable()


def close():
    """Close api, modules, widgets. Call before quit APP."""
    logger.info("CLOSING............")
    # 1 unload modules
    unload_modules()
    # 2 stop api
    api.stop()


def reload():
    """Reload api, modules, widgets"""
    logger.info("RELOADING............")
    # 1 unload modules
    unload_modules()
    # 2 reload setting
    cfg.load()
    cfg.save(0)
    # 3 restart api
    api.restart()
    # 4 load modules
    load_modules()


def load_modules():
    """Load modules, widgets"""
    octrl.enable()  # 1 overlay control
    mctrl.start()  # 2 module
    wctrl.start()  # 3 widget


def unload_modules():
    """Unload modules, widgets"""
    wctrl.close()  # 1 widget
    mctrl.close()  # 2 module
    octrl.disable()  # 3 overlay control
