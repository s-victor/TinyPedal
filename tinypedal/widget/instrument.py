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
Instrument Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap, QPainter

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config variable
        self.icon_size = int(max(self.wcfg["icon_size"], 16) * 0.5) * 2
        self.warning_color = (
            self.wcfg["bkg_color"],                 # 0
            self.wcfg["warning_color_stalling"],    # 1
            self.wcfg["warning_color_clutch"],      # 2
            self.wcfg["warning_color_wheel_lock"],  # 3
            self.wcfg["warning_color_wheel_slip"],  # 4
        )

        # Config canvas
        self.pixmap_common = QPixmap(self.icon_size, self.icon_size)
        self.pixmap_icon = QPixmap("images/icon_instrument.png").scaledToWidth(
            self.icon_size * 2, mode=Qt.SmoothTransformation
        )

        # Headlights
        if self.wcfg["show_headlights"]:
            self.bar_headlights = self.set_qlabel(
                fixed_width=self.icon_size,
                fixed_height=self.icon_size,
            )
            self.set_primary_orient(
                target=self.bar_headlights,
                column=self.wcfg["column_index_headlights"],
            )
            self.draw_instrument(self.bar_headlights, 1, 0)

        # Ignition
        if self.wcfg["show_ignition"]:
            self.bar_ignition = self.set_qlabel(
                fixed_width=self.icon_size,
                fixed_height=self.icon_size,
            )
            self.set_primary_orient(
                target=self.bar_ignition,
                column=self.wcfg["column_index_ignition"],
            )
            self.draw_instrument(self.bar_ignition, 1, 1)

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = self.set_qlabel(
                fixed_width=self.icon_size,
                fixed_height=self.icon_size,
            )
            self.set_primary_orient(
                target=self.bar_clutch,
                column=self.wcfg["column_index_clutch"],
            )
            self.draw_instrument(self.bar_clutch, 1, 2)

        # Lock
        if self.wcfg["show_wheel_lock"]:
            self.bar_wlock = self.set_qlabel(
                fixed_width=self.icon_size,
                fixed_height=self.icon_size,
            )
            self.set_primary_orient(
                target=self.bar_wlock,
                column=self.wcfg["column_index_wheel_lock"],
            )
            self.draw_instrument(self.bar_wlock, 1, 3)

        # Slip
        if self.wcfg["show_wheel_slip"]:
            self.bar_wslip = self.set_qlabel(
                fixed_width=self.icon_size,
                fixed_height=self.icon_size,
            )
            self.set_primary_orient(
                target=self.bar_wslip,
                column=self.wcfg["column_index_wheel_slip"],
            )
            self.draw_instrument(self.bar_wslip, 1, 4)

        # Last data
        self.flicker = False

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            self.flicker = not self.flicker

            # Headlights
            if self.wcfg["show_headlights"]:
                headlights = api.read.switch.headlights()
                self.update_headlights(self.bar_headlights, headlights)

            # Ignition
            # 0 ignition & engine off, 1 ignition on & engine off, 2 ignition & engine on
            if self.wcfg["show_ignition"]:
                ignition = api.read.switch.ignition_starter() * (
                    1 + (api.read.engine.rpm() > self.wcfg["stalling_rpm_threshold"]))
                self.update_ignition(self.bar_ignition, ignition)

            # Clutch
            # 2+ = auto clutch on, 1 or 3 = clutch activated
            if self.wcfg["show_clutch"]:
                clutch = (api.read.switch.auto_clutch() << 1) + (api.read.inputs.clutch() > 0.01)
                self.update_clutch(self.bar_clutch, clutch)

            # Wheel lock
            if self.wcfg["show_wheel_lock"]:
                wlock = (
                    self.flicker and
                    api.read.inputs.brake_raw() > 0 and
                    min(minfo.wheels.slipRatio) < -self.wcfg["wheel_lock_threshold"]
                )
                self.update_wlock(self.bar_wlock, wlock)

            # Wheel slip
            if self.wcfg["show_wheel_slip"]:
                wslip = (
                    self.flicker and
                    api.read.inputs.throttle_raw() > 0 and
                    max(minfo.wheels.slipRatio) >= self.wcfg["wheel_slip_threshold"]
                )
                self.update_wslip(self.bar_wslip, wslip)

    # GUI update methods
    def update_headlights(self, target, data):
        """Headlights update"""
        if target.last != data:
            target.last = data
            self.draw_instrument(target, data == 0, 0, 0)

    def update_ignition(self, target, data):
        """Ignition update"""
        if target.last != data:
            target.last = data
            self.draw_instrument(target, data == 0, 1, data == 1)

    def update_clutch(self, target, data):
        """Clutch update"""
        if target.last != data:
            target.last = data
            self.draw_instrument(target, data < 2, 2, 2 * (data % 2))

    def update_wlock(self, target, data):
        """Wheel lock update"""
        if target.last != data:
            target.last = data
            self.draw_instrument(target, data == 0, 3, 3 * data)

    def update_wslip(self, target, data):
        """Wheel slip update"""
        if target.last != data:
            target.last = data
            self.draw_instrument(target, data == 0, 4, 4 * data)

    def draw_instrument(self, target, h_offset: int, v_offset: int, color_index: int = 0):
        """Draw instrument

        Args:
            h_offset: 0 = enabled icon state, 1 = disabled icon state.
            v_offset: 0 headlights, 1 ignition, 2 clutch, 3 wheel lock, 4 wheel slip.
        """
        self.pixmap_common.fill(self.warning_color[color_index])
        painter = QPainter(self.pixmap_common)
        painter.drawPixmap(
            0, 0, self.pixmap_icon,
            self.icon_size * h_offset, self.icon_size * v_offset, 0, 0
        )
        target.setPixmap(self.pixmap_common)
