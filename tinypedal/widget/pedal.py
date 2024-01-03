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
Pedal Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF, QSize
from PySide2.QtGui import QPixmap, QPainter
from PySide2.QtWidgets import QLabel, QGridLayout

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "pedal"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_gap = self.wcfg["bar_gap"]
        max_gap = max(self.wcfg["inner_gap"], 0)
        pedal_uwidth = max(int(self.wcfg["bar_width_unfiltered"]), 1)
        pedal_fwidth = max(int(self.wcfg["bar_width_filtered"]), 1)

        self.pedal_extend = max(int(self.wcfg["max_indicator_height"]), 0) + max_gap
        self.pedal_length = max(int(self.wcfg["bar_length"]), 10)
        self.pbar_width = pedal_uwidth + pedal_fwidth
        self.pbar_length = self.pedal_length + self.pedal_extend

        if self.wcfg["enable_horizontal_style"]:
            pedal_size = QSize(self.pbar_length, self.pbar_width)
            raw_size = (0, 0, 0, pedal_uwidth)
            filtered_size = (0, pedal_uwidth, 0, pedal_fwidth)
            ffb_size = (0, 0, 0, self.pbar_width)
            max_size = (self.pedal_length + max_gap, 0, self.pedal_extend - max_gap, self.pbar_width)
        else:
            pedal_size = QSize(self.pbar_width, self.pbar_length)
            raw_size = (0, 0, pedal_uwidth, self.pbar_length)
            filtered_size = (pedal_uwidth, 0, pedal_fwidth, self.pbar_length)
            ffb_size = (0, 0, self.pbar_width, self.pbar_length)
            max_size = (0, 0, self.pbar_width, self.pedal_extend - max_gap)

        self.rect_throttle_raw = QRectF(*raw_size)
        self.rect_throttle_filtered = QRectF(*filtered_size)
        self.rect_brake_raw = QRectF(*raw_size)
        self.rect_brake_filtered = QRectF(*filtered_size)
        self.rect_clutch_raw = QRectF(*raw_size)
        self.rect_clutch_filtered = QRectF(*filtered_size)
        self.rect_ffb = QRectF(*ffb_size)
        self.rect_max = QRectF(*max_size)

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_ffb = self.wcfg["column_index_ffb"]
        column_clt = self.wcfg["column_index_clutch"]
        column_brk = self.wcfg["column_index_brake"]
        column_tht = self.wcfg["column_index_throttle"]

        # Force feedback
        if self.wcfg["show_ffb_meter"]:
            self.bar_ffb = QLabel()
            self.bar_ffb.setFixedSize(pedal_size)
            self.pixmap_ffb = QPixmap(pedal_size)
            self.draw_ffb(self.bar_ffb, self.pixmap_ffb, 0)

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = QLabel()
            self.bar_clutch.setFixedSize(pedal_size)
            self.pixmap_clutch = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_clutch, self.pixmap_clutch,
                self.rect_clutch_raw, self.rect_clutch_filtered,
                0, 0, self.wcfg["clutch_color"])

        # Brake
        if self.wcfg["show_brake"]:
            self.bar_brake = QLabel()
            self.bar_brake.setFixedSize(pedal_size)
            self.pixmap_brake = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_brake, self.pixmap_brake,
                self.rect_brake_raw, self.rect_brake_filtered,
                0, 0, self.wcfg["brake_color"])

        # Throttle
        if self.wcfg["show_throttle"]:
            self.bar_throttle = QLabel()
            self.bar_throttle.setFixedSize(pedal_size)
            self.pixmap_throttle = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_throttle, self.pixmap_throttle,
                self.rect_throttle_raw, self.rect_throttle_filtered,
                0, 0, self.wcfg["throttle_color"])

        # Set layout & style
        if self.wcfg["enable_horizontal_style"]:
            if self.wcfg["show_ffb_meter"]:
                layout.addWidget(self.bar_ffb, column_ffb, 0)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, column_clt, 0)
            if self.wcfg["show_brake"]:
                layout.addWidget(self.bar_brake, column_brk, 0)
            if self.wcfg["show_throttle"]:
                layout.addWidget(self.bar_throttle, column_tht, 0)
        else:
            if self.wcfg["show_ffb_meter"]:
                layout.addWidget(self.bar_ffb, 0, column_ffb)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, 0, column_clt)
            if self.wcfg["show_brake"]:
                layout.addWidget(self.bar_brake, 0, column_brk)
            if self.wcfg["show_throttle"]:
                layout.addWidget(self.bar_throttle, 0, column_tht)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.max_brake_pres = 0

        self.last_throttle = None
        self.last_brake = None
        self.last_clutch = None
        self.last_ffb = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read pedal data
            f_throttle = self.scale_input(api.read.input.throttle())
            f_brake = self.scale_input(api.read.input.brake())
            f_clutch = self.scale_input(api.read.input.clutch())
            raw_throttle = self.scale_input(api.read.input.throttle_raw())
            raw_brake = self.scale_input(api.read.input.brake_raw())
            raw_clutch = self.scale_input(api.read.input.clutch_raw())
            ffb = self.scale_input(api.read.input.force_feedback())

            # Throttle
            if self.wcfg["show_throttle"]:
                throttle = (raw_throttle, f_throttle)
                self.update_throttle(throttle, self.last_throttle)
                self.last_throttle = throttle

            # Brake
            if self.wcfg["show_brake"]:
                if self.wcfg["show_brake_pressure"]:
                    brake_pres = sum(api.read.brake.pressure())
                    if brake_pres > self.max_brake_pres:
                        self.max_brake_pres = brake_pres
                    f_brake = self.scale_input(brake_pres / max(self.max_brake_pres, 0.001))

                brake = (raw_brake, f_brake)
                self.update_brake(brake, self.last_brake)
                self.last_brake = brake

            # Clutch
            if self.wcfg["show_clutch"]:
                clutch = (raw_clutch, f_clutch)
                self.update_clutch(clutch, self.last_clutch)
                self.last_clutch = clutch

            # Force feedback
            if self.wcfg["show_ffb_meter"]:
                self.update_ffb(ffb, self.last_ffb)
                self.last_ffb = ffb

        else:
            if self.checked:
                self.checked = False
                self.max_brake_pres = 0

    # GUI update methods
    def update_throttle(self, curr, last):
        """Throttle update"""
        if curr != last:
            self.draw_pedal(
                self.bar_throttle, self.pixmap_throttle,
                self.rect_throttle_raw, self.rect_throttle_filtered,
                curr[0], curr[1], self.wcfg["throttle_color"])

    def update_brake(self, curr, last):
        """Brake update"""
        if curr != last:
            self.draw_pedal(
                self.bar_brake, self.pixmap_brake,
                self.rect_brake_raw, self.rect_brake_filtered,
                curr[0], curr[1], self.wcfg["brake_color"])

    def update_clutch(self, curr, last):
        """Clutch update"""
        if curr != last:
            self.draw_pedal(
                self.bar_clutch, self.pixmap_clutch,
                self.rect_clutch_raw, self.rect_clutch_filtered,
                curr[0], curr[1], self.wcfg["clutch_color"])

    def update_ffb(self, curr, last):
        """FFB update"""
        if curr != last:
            self.draw_ffb(
                self.bar_ffb, self.pixmap_ffb, curr)

    def draw_pedal(
        self, canvas, pixmap, rect_raw, rect_filtered,
        input_raw, input_filter, color=None):
        """Instrument"""
        pixmap.fill(self.wcfg["bkg_color"])
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)

        if self.wcfg["enable_horizontal_style"]:
            rect_raw.setWidth(input_raw)
            rect_filtered.setWidth(input_filter)
            if input_raw >= self.pedal_length:
                painter.fillRect(self.rect_max, color)
        else:  # vertical scale
            rect_raw.setTop(input_raw)
            rect_filtered.setTop(input_filter)
            if input_raw <= self.pedal_extend:
                painter.fillRect(self.rect_max, color)

        painter.fillRect(rect_raw, color)
        painter.fillRect(rect_filtered, color)
        canvas.setPixmap(pixmap)

    def draw_ffb(self, canvas, pixmap, input_raw):
        """FFB"""
        pixmap.fill(self.wcfg["bkg_color"])
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)

        if self.wcfg["enable_horizontal_style"]:
            if input_raw < self.pedal_length:
                color = self.wcfg["ffb_color"]
                self.rect_ffb.setWidth(input_raw)
            else:
                color = self.wcfg["ffb_clipping_color"]
                self.rect_ffb.setWidth(self.pbar_length)
        else:  # vertical scale
            if input_raw > self.pedal_extend:
                color = self.wcfg["ffb_color"]
                self.rect_ffb.setTop(input_raw)
            else:
                color = self.wcfg["ffb_clipping_color"]
                self.rect_ffb.setTop(0)

        painter.fillRect(self.rect_ffb, color)
        canvas.setPixmap(pixmap)

    # Additional methods
    def scale_input(self, value):
        """Scale input to pedal bar length"""
        if self.wcfg["enable_horizontal_style"]:
            return abs(int(value * self.pedal_length))
        return self.pbar_length - abs(int(value * self.pedal_length))
