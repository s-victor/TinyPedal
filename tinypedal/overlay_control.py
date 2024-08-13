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
Overlay Control
"""

import logging
import time
import threading

from PySide2.QtCore import QObject, Signal

from .setting import cfg
from .api_control import api

logger = logging.getLogger(__name__)


class StateTimer:
    """State timer"""

    def __init__(self, interval: float, last: float = 0) -> None:
        self._interval = interval
        self._last = last

    def timeout(self, now: float) -> bool:
        """Check time out"""
        if now - self._last < self._interval:
            return False
        self._last = now
        return True

    def reset(self, now: float = 0) -> None:
        """Reset timer"""
        self._last = now

    def set_interval(self, interval: float) -> None:
        """Set timer interval"""
        self._interval = interval

    @property
    def interval(self) -> float:
        """Timer interval"""
        return self._interval

    @property
    def last(self) -> float:
        """Timer last time stamp"""
        return self._last


class OverlayState(QObject):
    """Set and update overlay global state

    Available states:
        * Active: True if vehicle is on track
        * Lock position
        * Auto hide
        * Grid move
    """
    hidden = Signal(bool)
    locked = Signal(bool)

    def __init__(self):
        super().__init__()
        self.stopped = True
        self.active = False
        self.event = threading.Event()
        self._auto_hide_timer = StateTimer(0.4)

    def start(self):
        """Start state update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__updating, daemon=True).start()
            logger.info("ACTIVE: overlay control")

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __updating(self):
        """Update global state"""
        self._auto_hide_timer.reset()

        while not self.event.wait(0.01):
            self.active = api.state
            self.__auto_hide_state()

        self.stopped = True
        logger.info("CLOSED: overlay control")

    def __auto_hide_state(self):
        """Update auto hide state"""
        if self._auto_hide_timer.timeout(time.perf_counter()):
            self.hidden.emit(cfg.overlay["auto_hide"] and not self.active)


class OverlayControl:
    """Overlay control"""

    def __init__(self):
        self.state = OverlayState()

    def enable(self):
        """Enable overlay control"""
        self.state.start()

    def disable(self):
        """Disable overlay control"""
        self.state.stop()
        while not self.state.stopped:
            time.sleep(0.01)

    def toggle_lock(self):
        """Toggle lock state"""
        self.__toggle_option("fixed_position")
        self.state.locked.emit(cfg.overlay["fixed_position"])

    def toggle_hide(self):
        """Toggle hide state"""
        self.__toggle_option("auto_hide")

    def toggle_grid(self):
        """Toggle grid move state"""
        self.__toggle_option("enable_grid_move")

    @staticmethod
    def __toggle_option(option_name: str):
        """Toggle option"""
        cfg.overlay[option_name] = not cfg.overlay[option_name]
        cfg.save()

octrl = OverlayControl()
