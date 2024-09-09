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
from PySide2.QtWidgets import QLabel, QGridLayout

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

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_hl = self.wcfg["column_index_headlights"]
        column_ig = self.wcfg["column_index_ignition"]
        column_cl = self.wcfg["column_index_clutch"]
        column_wl = self.wcfg["column_index_wheel_lock"]
        column_ws = self.wcfg["column_index_wheel_slip"]

        # Config canvas
        icon_source = QPixmap("images/icon_instrument.png")
        self.pixmap_icon = icon_source.scaledToWidth(
            self.icon_size * 2,
            mode=Qt.SmoothTransformation
        )

        self.pen = QPen()

        # Headlights
        if self.wcfg["show_headlights"]:
            self.bar_headlights = QLabel()
            self.bar_headlights.setFixedSize(self.icon_size, self.icon_size)
            self.pixmap_headlights = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_headlights, self.pixmap_headlights, 1, 0)

        # Ignition
        if self.wcfg["show_ignition"]:
            self.bar_ignition = QLabel()
            self.bar_ignition.setFixedSize(self.icon_size, self.icon_size)
            self.pixmap_ignition = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_ignition, self.pixmap_ignition, 1, 1)

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = QLabel()
            self.bar_clutch.setFixedSize(self.icon_size, self.icon_size)
            self.pixmap_clutch = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_clutch, self.pixmap_clutch, 1, 2)

        # Lock
        if self.wcfg["show_wheel_lock"]:
            self.bar_wlock = QLabel()
            self.bar_wlock.setFixedSize(self.icon_size, self.icon_size)
            self.pixmap_wlock = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_wlock, self.pixmap_wlock, 1, 3)

        # Slip
        if self.wcfg["show_wheel_slip"]:
            self.bar_wslip = QLabel()
            self.bar_wslip.setFixedSize(self.icon_size, self.icon_size)
            self.pixmap_wslip = QPixmap(self.icon_size, self.icon_size)
            self.draw_instrument(self.bar_wslip, self.pixmap_wslip, 1, 4)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Horizontal layout
            if self.wcfg["show_headlights"]:
                layout.addWidget(self.bar_headlights, 0, column_hl)
            if self.wcfg["show_ignition"]:
                layout.addWidget(self.bar_ignition, 0, column_ig)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, 0, column_cl)
            if self.wcfg["show_wheel_lock"]:
                layout.addWidget(self.bar_wlock, 0, column_wl)
            if self.wcfg["show_wheel_slip"]:
                layout.addWidget(self.bar_wslip, 0, column_ws)
        else:
            # Vertical layout
            if self.wcfg["show_headlights"]:
                layout.addWidget(self.bar_headlights, column_hl, 0)
            if self.wcfg["show_ignition"]:
                layout.addWidget(self.bar_ignition, column_ig, 0)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, column_cl, 0)
            if self.wcfg["show_wheel_lock"]:
                layout.addWidget(self.bar_wlock, column_wl, 0)
            if self.wcfg["show_wheel_slip"]:
                layout.addWidget(self.bar_wslip, column_ws, 0)
        self.setLayout(layout)

        # Last data
        self.last_headlights = None
        self.last_ignition = None
        self.last_clutch = None
        self.last_wlock = None
        self.last_wslip = None
        self.flicker = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read instrument data
            headlights = api.read.switch.headlights()
            ignition = (api.read.switch.ignition_starter(),
                        api.read.engine.rpm())
            clutch = (api.read.switch.auto_clutch(),
                      api.read.input.clutch())
            is_braking = api.read.input.brake() > 0

            self.flicker = not self.flicker

            # Headlights
            if self.wcfg["show_headlights"]:
                self.update_headlights(headlights, self.last_headlights)
                self.last_headlights = headlights

            # Ignition
            if self.wcfg["show_ignition"]:
                self.update_ignition(ignition, self.last_ignition)
                self.last_ignition = ignition

            # Clutch
            if self.wcfg["show_clutch"]:
                self.update_clutch(clutch, self.last_clutch)
                self.last_clutch = clutch

            # Wheel lock
            if self.wcfg["show_wheel_lock"]:
                wlock = (is_braking, round(min(minfo.wheels.slipRatio), 3))
                self.update_wlock(wlock, self.last_wlock)
                self.last_wlock = wlock

            # Wheel slip
            if self.wcfg["show_wheel_slip"]:
                wslip = round(max(minfo.wheels.slipRatio), 3)
                self.update_wslip(wslip, self.last_wslip)
                self.last_wslip = wslip

    # GUI update methods
    def update_headlights(self, curr, last):
        """Headlights update"""
        if curr != last:
            state = 0 if curr == 1 else 1
            self.draw_instrument(self.bar_headlights, self.pixmap_headlights, state, 0)

    def update_ignition(self, curr, last):
        """Ignition update"""
        if curr != last:
            state = 0 if curr[0] > 0 else 1
            color = self.wcfg["warning_color_ignition"] if curr[1] < 10 else None
            self.draw_instrument(self.bar_ignition, self.pixmap_ignition, state, 1, color)

    def update_clutch(self, curr, last):
        """Clutch update"""
        if curr != last:
            state = 0 if curr[0] > 0 else 1
            color = self.wcfg["warning_color_clutch"] if curr[1] > 0.01 else None
            self.draw_instrument(self.bar_clutch, self.pixmap_clutch, state, 2, color)

    def update_wlock(self, curr, last):
        """Wheel lock update"""
        if curr != last:
            if self.flicker and curr[0] > 0 and curr[1] < -self.wcfg["wheel_lock_threshold"]:
                state = 0
                color = self.wcfg["warning_color_wheel_lock"]
            else:
                state = 1
                color = None
            self.draw_instrument(self.bar_wlock, self.pixmap_wlock, state, 3, color)

    def update_wslip(self, curr, last):
        """Wheel slip update"""
        if curr != last:
            if self.flicker and curr >= self.wcfg["wheel_slip_threshold"]:
                state = 0
                color = self.wcfg["warning_color_wheel_slip"]
            else:
                state = 1
                color = None
            self.draw_instrument(self.bar_wslip, self.pixmap_wslip, state, 4, color)

    def draw_instrument(self, canvas, pixmap, h_offset, v_offset, hicolor=None):
        """Instrument"""
        pixmap.fill(self.wcfg["bkg_color"] if not hicolor else hicolor)
        painter = QPainter(pixmap)

        # Set size
        self.rect_offset.moveLeft(self.icon_size * h_offset)
        self.rect_offset.moveTop(self.icon_size * v_offset)

        # Icon
        painter.drawPixmap(self.rect_size, self.pixmap_icon, self.rect_offset)
        canvas.setPixmap(pixmap)
