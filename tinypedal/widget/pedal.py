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
Pedal Widget
"""

from PySide2.QtCore import Qt, QRectF, QSize
from PySide2.QtGui import QPixmap, QPainter, QPen
from PySide2.QtWidgets import QLabel, QGridLayout

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "pedal"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        font_m = self.get_font_metrics(self.font)
        font_offset = self.calc_font_offset(font_m)

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
            reading_size = (
                self.pbar_length * self.wcfg["readings_offset"] - self.pbar_length * 0.5,
                self.pbar_width * 0.5 - font_m.height * 0.5 + font_offset,
                self.pbar_length,
                font_m.height
            )
        else:
            pedal_size = QSize(self.pbar_width, self.pbar_length)
            raw_size = (0, 0, pedal_uwidth, self.pbar_length)
            filtered_size = (pedal_uwidth, 0, pedal_fwidth, self.pbar_length)
            ffb_size = (0, 0, self.pbar_width, self.pbar_length)
            max_size = (0, 0, self.pbar_width, self.pedal_extend - max_gap)
            reading_size = (
                self.pbar_width * 0.5 - self.pbar_width * 0.5,
                self.pbar_length * self.wcfg["readings_offset"] - font_m.height * 0.5 + font_offset,
                self.pbar_width,
                font_m.height
            )

        self.rect_throttle_raw = QRectF(*raw_size)
        self.rect_throttle_filtered = QRectF(*filtered_size)
        self.rect_brake_raw = QRectF(*raw_size)
        self.rect_brake_filtered = QRectF(*filtered_size)
        self.rect_clutch_raw = QRectF(*raw_size)
        self.rect_clutch_filtered = QRectF(*filtered_size)
        self.rect_ffb = QRectF(*ffb_size)
        self.rect_max = QRectF(*max_size)
        self.rect_readings = QRectF(*reading_size)

        self.pen = QPen()

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
            self.draw_ffb(self.bar_ffb, self.pixmap_ffb, 0, 0)

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = QLabel()
            self.bar_clutch.setFixedSize(pedal_size)
            self.pixmap_clutch = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_clutch, self.pixmap_clutch,
                self.rect_clutch_raw, self.rect_clutch_filtered,
                0, 0, 0, self.wcfg["font_color_clutch"], self.wcfg["clutch_color"])

        # Brake
        if self.wcfg["show_brake"]:
            self.bar_brake = QLabel()
            self.bar_brake.setFixedSize(pedal_size)
            self.pixmap_brake = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_brake, self.pixmap_brake,
                self.rect_brake_raw, self.rect_brake_filtered,
                0, 0, 0, self.wcfg["font_color_brake"], self.wcfg["brake_color"])

        # Throttle
        if self.wcfg["show_throttle"]:
            self.bar_throttle = QLabel()
            self.bar_throttle.setFixedSize(pedal_size)
            self.pixmap_throttle = QPixmap(pedal_size)
            self.draw_pedal(
                self.bar_throttle, self.pixmap_throttle,
                self.rect_throttle_raw, self.rect_throttle_filtered,
                0, 0, 0, self.wcfg["font_color_throttle"], self.wcfg["throttle_color"])

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

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Throttle
            if self.wcfg["show_throttle"]:
                raw_throttle = api.read.input.throttle_raw()
                if self.wcfg["show_throttle_filtered"]:
                    throttle = raw_throttle, api.read.input.throttle()
                else:
                    throttle = raw_throttle, raw_throttle
                self.update_throttle(throttle, self.last_throttle)
                self.last_throttle = throttle

            # Brake
            if self.wcfg["show_brake"]:
                raw_brake = api.read.input.brake_raw()
                if self.wcfg["show_brake_filtered"]:
                    if self.wcfg["show_brake_pressure"]:
                        f_brake = self.filtered_brake_pressure(api.read.brake.pressure())
                    else:
                        f_brake = api.read.input.brake()
                    brake = raw_brake, f_brake
                else:
                    brake = raw_brake, raw_brake
                self.update_brake(brake, self.last_brake)
                self.last_brake = brake

            # Clutch
            if self.wcfg["show_clutch"]:
                raw_clutch = api.read.input.clutch_raw()
                if self.wcfg["show_clutch_filtered"]:
                    clutch = raw_clutch, api.read.input.clutch()
                else:
                    clutch = raw_clutch, raw_clutch
                self.update_clutch(clutch, self.last_clutch)
                self.last_clutch = clutch

            # Force feedback
            if self.wcfg["show_ffb_meter"]:
                ffb = api.read.input.force_feedback()
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
                self.scale_input(curr[0]), self.scale_input(curr[1]), max(curr),
                self.wcfg["font_color_throttle"], self.wcfg["throttle_color"])

    def update_brake(self, curr, last):
        """Brake update"""
        if curr != last:
            self.draw_pedal(
                self.bar_brake, self.pixmap_brake,
                self.rect_brake_raw, self.rect_brake_filtered,
                self.scale_input(curr[0]), self.scale_input(curr[1]), max(curr),
                self.wcfg["font_color_brake"], self.wcfg["brake_color"])

    def update_clutch(self, curr, last):
        """Clutch update"""
        if curr != last:
            self.draw_pedal(
                self.bar_clutch, self.pixmap_clutch,
                self.rect_clutch_raw, self.rect_clutch_filtered,
                self.scale_input(curr[0]), self.scale_input(curr[1]), max(curr),
                self.wcfg["font_color_clutch"], self.wcfg["clutch_color"])

    def update_ffb(self, curr, last):
        """FFB update"""
        if curr != last:
            self.draw_ffb(
                self.bar_ffb, self.pixmap_ffb,
                self.scale_input(curr), abs(curr))

    def draw_pedal(
        self, canvas, pixmap, rect_raw, rect_filtered,
        input_raw, input_filter, input_reading, fgcolor, bgcolor):
        """Instrument"""
        pixmap.fill(self.wcfg["bkg_color"])
        painter = QPainter(pixmap)
        painter.setPen(Qt.NoPen)

        if self.wcfg["enable_horizontal_style"]:
            rect_raw.setWidth(input_raw)
            rect_filtered.setWidth(input_filter)
            if input_raw >= self.pedal_length:
                painter.fillRect(self.rect_max, bgcolor)
        else:  # vertical scale
            rect_raw.setTop(input_raw)
            rect_filtered.setTop(input_filter)
            if input_raw <= self.pedal_extend:
                painter.fillRect(self.rect_max, bgcolor)

        painter.fillRect(rect_raw, bgcolor)
        painter.fillRect(rect_filtered, bgcolor)

        if self.wcfg["show_readings"]:
            self.draw_readings(painter, input_reading, fgcolor)

        canvas.setPixmap(pixmap)

    def draw_ffb(self, canvas, pixmap, input_raw, input_reading):
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

        if self.wcfg["show_readings"]:
            self.draw_readings(painter, input_reading, self.wcfg["font_color_ffb"])

        canvas.setPixmap(pixmap)

    def draw_readings(self, painter, value, fgcolor):
        """Draw readings"""
        self.pen.setColor(fgcolor)
        painter.setFont(self.font)
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_readings,
            Qt.AlignCenter,
            f"{value * 100:.0f}"
        )

    # Additional methods
    def scale_input(self, value):
        """Scale input to pedal bar length"""
        if self.wcfg["enable_horizontal_style"]:
            return abs(int(value * self.pedal_length))
        return self.pbar_length - abs(int(value * self.pedal_length))

    def filtered_brake_pressure(self, value):
        """Percentage filtered brake pressure"""
        brake_pres = sum(value)
        if brake_pres > self.max_brake_pres:
            self.max_brake_pres = brake_pres
        if self.max_brake_pres:
            return brake_pres / self.max_brake_pres
        return 0
