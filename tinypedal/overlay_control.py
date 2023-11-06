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
Overlay Control
"""

import logging
import time
import threading

from PySide2.QtCore import QObject, Signal

from .setting import cfg
from . import readapi

logger = logging.getLogger(__name__)


class OverlayLock(QObject):
    """Overlay lock state"""
    locked = Signal(bool)

    def __init__(self, config):
        super().__init__()
        self.cfg = config

    def set_state(self):
        """Set lock state"""
        self.locked.emit(self.cfg.overlay["fixed_position"])

    def toggle(self):
        """Toggle lock state"""
        if not self.cfg.overlay["fixed_position"]:
            self.cfg.overlay["fixed_position"] = True
        else:
            self.cfg.overlay["fixed_position"] = False
        self.set_state()
        self.cfg.save()


class OverlayAutoHide(QObject):
    """Auto hide overlay"""
    hidden = Signal(bool)

    def __init__(self, config):
        super().__init__()
        self.cfg = config
        self.stopped = True
        self.running = False

    def start(self):
        """Start auto hide thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__autohide, daemon=True)
            _thread.start()
            logger.info("auto-hide module started")

    def __autohide(self):
        """Auto hide overlay"""
        while self.running:
            self.hidden.emit(self.__is_hidden())
            time.sleep(0.4)

        self.stopped = True
        logger.info("auto-hide module closed")

    def __is_hidden(self):
        """Check hide state"""
        if self.cfg.overlay["auto_hide"]:
            if readapi.state():
                return False
            return True
        return False

    def toggle(self):
        """Toggle hide state"""
        if not self.cfg.overlay["auto_hide"]:
            self.cfg.overlay["auto_hide"] = True
        else:
            self.cfg.overlay["auto_hide"] = False
        self.cfg.save()


class OverlayControl:
    """Overlay control"""

    def enable(self):
        """Enable overlay control"""
        self.overlay_lock = OverlayLock(cfg)
        self.overlay_hide = OverlayAutoHide(cfg)
        self.overlay_hide.start()

    def disable(self):
        """Disable overlay control"""
        self.overlay_hide.running = False
        while not self.overlay_hide.stopped:
            time.sleep(0.01)


octrl = OverlayControl()
