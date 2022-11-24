#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Load module & function
"""

import time

from tinypedal.setting import cfg
from tinypedal.realtime_delta import DeltaTime
from tinypedal.realtime_fuel import FuelUsage
from tinypedal.realtime_relative import RelativeInfo
from tinypedal.overlay_toggle import OverlayLock, OverlayAutoHide


class LoadModule:
    """Load Module"""

    def __init__(self):
        """Widget list"""
        self.delta_time = DeltaTime(cfg)  # delta module
        self.fuel_usage = FuelUsage(cfg)  # fuel module
        self.relative_info = RelativeInfo(cfg)  # relative module
        self.overlay_lock = OverlayLock(cfg)  # overlay lock
        self.overlay_hide = OverlayAutoHide(cfg)  # overlay auto hide

    def start(self):
        """Start module"""
        self.delta_time = DeltaTime(cfg)
        self.fuel_usage = FuelUsage(cfg)
        self.relative_info = RelativeInfo(cfg)
        self.overlay_lock = OverlayLock(cfg)
        self.overlay_hide = OverlayAutoHide(cfg)

        if cfg.overlay["delta_module"]:
            self.delta_time.start()
        if cfg.overlay["fuel_module"]:
            self.fuel_usage.start()
        if cfg.overlay["relative_module"]:
            self.relative_info.start()
        self.overlay_hide.start()

    def stop(self):
        """Stop modules"""
        self.delta_time.running = False
        self.fuel_usage.running = False
        self.relative_info.running = False
        self.overlay_hide.running = False
        while True:
            if all((
                self.delta_time.stopped,
                self.fuel_usage.stopped,
                self.relative_info.stopped,
                self.overlay_hide.stopped
                )):
                break
            time.sleep(0.1)

module = LoadModule()
