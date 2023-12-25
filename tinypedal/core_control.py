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
Core control
"""

import logging

from .setting import cfg
from .api_control import api
from .module_control import mctrl
from .widget_control import wctrl
from .overlay_control import octrl

logger = logging.getLogger(__name__)


class CoreControl:
    """Core application control"""

    @staticmethod
    def start():
        """Start modules & widgets"""
        logger.info("STARTING............")
        api.connect(cfg.shared_memory_api["api_name"])
        api.start()

        mctrl.start()  # 1 start module
        octrl.enable()  # 2 enable overlay control
        wctrl.start()  # 3 start widget

    @staticmethod
    def reload():
        """Reload current preset"""
        # Close modules & widgets in order
        logger.info("RELOADING............")
        mctrl.close()
        octrl.disable()
        wctrl.close()
        # Load new setting
        cfg.load()
        # Restart api
        api.restart()
        # Start modules & widgets
        mctrl.start()
        octrl.enable()
        wctrl.start()

    @staticmethod
    def quit():
        """Quit"""
        logger.info("CLOSING............")
        mctrl.close()  # stop module
        octrl.disable()  # disable overlay control
        wctrl.close()  # close widget
        api.stop()  # stop sharedmemory mapping


cctrl = CoreControl()
