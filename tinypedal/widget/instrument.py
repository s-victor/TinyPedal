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

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPixmap, QPainter, QPen
from PySide2.QtWidgets import QGridLayout

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "instrument"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_gap = self.wcfg["bar_gap"]
        self.icon_size = int(max(self.wcfg["icon_size"], 16) * 0.5) * 2
        self.rect_size = QRectF(0, 0, self.icon_size, self.icon_size)
        self.rect_offset = QRectF(0, 0, self.icon_size, self.icon_size)
        self.warning_color = (
            self.wcfg["bkg_color"],                 # 0
            self.wcfg["warning_color_ignition"],    # 1
            self.wcfg["warning_color_clutch"],      # 2
            self.wcfg["warning_color_wheel_lock"],  # 3
            self.wcfg["warning_color_wheel_slip"],  # 4
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Config canvas
        self.pixmap_icon = QPixmap("images/icon_instrument.png").scaledToWidth(
            self.icon_size * 2, mode=Qt.SmoothTransformation
        )
        self.pen = QPen()

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
            self.pixmap_headlights = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_headlights, self.pixmap_headlights, 1, 0)

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
            self.pixmap_ignition = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_ignition, self.pixmap_ignition, 1, 1)

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
            self.pixmap_clutch = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_clutch, self.pixmap_clutch, 1, 2)

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
            self.pixmap_wlock = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_wlock, self.pixmap_wlock, 1, 3)

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
            self.pixmap_wslip = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_wslip, self.pixmap_wslip, 1, 4)

        # Last data
        self.flicker = False
        self.last_headlights = None
        self.last_ignition = None
        self.last_clutch = None
        self.last_wlock = None
        self.last_wslip = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            self.flicker = not self.flicker

            # Headlights
            if self.wcfg["show_headlights"]:
                headlights = api.read.switch.headlights()
                self.update_headlights(headlights, self.last_headlights)
                self.last_headlights = headlights

            # Ignition
            if self.wcfg["show_ignition"]:
                ignition = api.read.switch.ignition_starter(), api.read.engine.rpm()
                self.update_ignition(ignition, self.last_ignition)
                self.last_ignition = ignition

            # Clutch
            if self.wcfg["show_clutch"]:
                clutch = api.read.switch.auto_clutch(), api.read.input.clutch()
                self.update_clutch(clutch, self.last_clutch)
                self.last_clutch = clutch

            # Wheel lock
            if self.wcfg["show_wheel_lock"]:
                wlock = (
                    self.flicker and
                    api.read.input.brake_raw() > 0 and
                    min(minfo.wheels.slipRatio) < -self.wcfg["wheel_lock_threshold"]
                )
                self.update_wlock(wlock, self.last_wlock)
                self.last_wlock = wlock

            # Wheel slip
            if self.wcfg["show_wheel_slip"]:
                wslip = (
                    self.flicker and
                    api.read.input.throttle_raw() > 0 and
                    max(minfo.wheels.slipRatio) >= self.wcfg["wheel_slip_threshold"]
                )
                self.update_wslip(wslip, self.last_wslip)
                self.last_wslip = wslip

    # GUI update methods
    def update_headlights(self, curr, last):
        """Headlights update"""
        if curr != last:
            self.draw_instrument(self.bar_headlights, self.pixmap_headlights, curr == 0, 0)

    def update_ignition(self, curr, last):
        """Ignition update"""
        if curr != last:
            if curr[1] < 10:
                color = 1
            else:
                color = 0
            self.draw_instrument(self.bar_ignition, self.pixmap_ignition, curr[0] == 0, 1, color)

    def update_clutch(self, curr, last):
        """Clutch update"""
        if curr != last:
            if curr[1] > 0.01:
                color = 2
            else:
                color = 0
            self.draw_instrument(self.bar_clutch, self.pixmap_clutch, curr[0] == 0, 2, color)

    def update_wlock(self, curr, last):
        """Wheel lock update"""
        if curr != last:
            if curr:
                state = 0
                color = 3
            else:
                state = 1
                color = 0
            self.draw_instrument(self.bar_wlock, self.pixmap_wlock, state, 3, color)

    def update_wslip(self, curr, last):
        """Wheel slip update"""
        if curr != last:
            if curr:
                state = 0
                color = 4
            else:
                state = 1
                color = 0
            self.draw_instrument(self.bar_wslip, self.pixmap_wslip, state, 4, color)

    def draw_instrument(self, canvas, pixmap, h_offset, v_offset, color_index=0):
        """Instrument"""
        pixmap.fill(self.warning_color[color_index])
        painter = QPainter(pixmap)
        # Set size
        self.rect_offset.moveLeft(self.icon_size * h_offset)
        self.rect_offset.moveTop(self.icon_size * v_offset)
        # Icon
        painter.drawPixmap(self.rect_size, self.pixmap_icon, self.rect_offset)
        canvas.setPixmap(pixmap)
