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
import threading
from time import sleep, monotonic

from PySide2.QtCore import QObject, Signal

from .api_control import api
from .setting import cfg

logger = logging.getLogger(__name__)


class StateTimer:
    """State timer"""

    __slots__ = (
        "_interval",
        "_last",
    )

    def __init__(self, interval: float, last: float = 0) -> None:
        """
        Args:
            interval: time interval in seconds.
            last: last time stamp in seconds.
        """
        self._interval = interval
        self._last = last

    def timeout(self, seconds: float) -> bool:
        """Check time out"""
        if self._interval > seconds - self._last:
            return False
        self._last = seconds
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

    Attributes:
        active: check whether api state (on track) is active.
        hidden: signal for toggling auto hide state.
        locked: signal for toggling lock state.
        reload: signal for reloading preset, should only be emitted after app fully loaded.
        vr_compat: signal for toggling VR compatibility state.
    """
    hidden = Signal(bool)
    locked = Signal(bool)
    reload = Signal(bool)
    vr_compat = Signal(bool)

    def __init__(self):
        super().__init__()
        self.active = False
        self._stopped = True
        self._event = threading.Event()

        self._auto_hide_timer = StateTimer(interval=0.4)
        self._auto_load_preset_timer = StateTimer(interval=1.0)
        self._last_detected_sim = None

    def start(self):
        """Start state update thread"""
        if self._stopped:
            self._stopped = False
            self._event.clear()
            threading.Thread(target=self.__updating, daemon=True).start()
            logger.info("ENABLED: overlay control")

    def stop(self):
        """Stop thread"""
        self._event.set()
        while not self._stopped:
            sleep(0.01)

    def __updating(self):
        """Update global state"""
        while not self._event.wait(0.2):
            self.active = api.state
            self.__auto_hide_state()
            if cfg.application["enable_auto_load_preset"]:
                self.__auto_load_preset()

        self._stopped = True
        logger.info("DISABLED: overlay control")

    def __auto_hide_state(self):
        """Auto hide state"""
        if self._auto_hide_timer.timeout(monotonic()):
            self.hidden.emit(cfg.overlay["auto_hide"] and not self.active)

    def __auto_load_preset(self):
        """Auto load primary preset"""
        if self._auto_load_preset_timer.timeout(monotonic()):
            # Get sim_name, returns "" if no game running
            sim_name = api.read.check.sim_name()
            # Abort if game not found
            if not sim_name:
                # Clear detected name if no game found
                if self._last_detected_sim is not None:
                    self._last_detected_sim = None
                return
            # Abort if same as last found game
            if sim_name == self._last_detected_sim:
                return
            # Assign sim name to last detected, set preset name
            self._last_detected_sim = sim_name
            preset_name = cfg.get_primary_preset_name(sim_name)
            logger.info("USERDATA: %s detected, attempt loading %s (primary preset)", sim_name, preset_name)
            # Abort if preset file does not exist
            if preset_name == "":
                logger.info("USERDATA: %s (primary preset) not found, abort auto loading", preset_name)
                return
            # Check if already loaded
            if preset_name == cfg.filename.last_setting:
                logger.info("USERDATA: %s (primary preset) loaded", preset_name)
                return
            # Update preset name & signal reload
            cfg.filename.setting = preset_name
            self.reload.emit(True)


class OverlayControl:
    """Overlay control"""

    __slots__ = (
        "state",
    )

    def __init__(self):
        self.state = OverlayState()

    def enable(self):
        """Enable overlay control"""
        self.state.start()

    def disable(self):
        """Disable overlay control"""
        self.state.stop()

    def toggle_vr(self):
        """Toggle VR state"""
        self.__toggle_option("vr_compatibility")
        self.state.vr_compat.emit(cfg.overlay["vr_compatibility"])

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
