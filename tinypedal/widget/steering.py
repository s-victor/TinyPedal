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
Steering Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPixmap, QPen, QBrush

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "steering"


class Draw(Overlay):
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
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        text_height = int(font_m.capital + pady * 2) if self.wcfg["show_steering_angle"] else 0
        self.bar_width = max(self.wcfg["bar_width"], 20)
        self.bar_height = max(self.wcfg["bar_height"], text_height)
        self.bar_edge = max(self.wcfg["bar_edge_width"], 0)
        self.full_width = (self.bar_width + self.bar_edge) * 2

        self.rect_edge_l = QRectF(
            0,
            0,
            self.bar_edge,
            self.bar_height
        )
        self.rect_edge_r = QRectF(
            self.bar_edge + self.bar_width * 2,
            0,
            self.bar_edge,
            self.bar_height
        )
        self.rect_text_bg_l = QRectF(
            self.bar_edge + padx,
            font_offset,
            self.bar_width,
            self.bar_height
        )
        self.rect_text_bg_r = QRectF(
            self.bar_edge + self.bar_width,
            font_offset,
            self.bar_width - padx,
            self.bar_height
        )

        # Config canvas
        self.resize(self.full_width, self.bar_height)
        self.pixmap_background = QPixmap(self.full_width, self.bar_height)
        self.pixmap_mark = QPixmap(self.full_width, self.bar_height)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_background()
        self.draw_scale_mark()

        # Last data
        self.raw_steering = 0
        self.last_raw_steering = None
        self.sw_rot_range = 1
        self.last_sw_rot_range = 0

        # Set widget state & start update
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read steering data
            self.raw_steering = api.read.input.steering_raw()
            if self.wcfg["manual_steering_range"] > 0:
                self.sw_rot_range = self.wcfg["manual_steering_range"]
            else:
                self.sw_rot_range = api.read.input.steering_range_physical()
                if minfo.restapi.steeringWheelRange > 0 >= self.sw_rot_range:
                    self.sw_rot_range = minfo.restapi.steeringWheelRange

            # Recalculate scale mark
            if self.wcfg["show_scale_mark"] and self.sw_rot_range != self.last_sw_rot_range:
                self.last_sw_rot_range = self.sw_rot_range
                mark_gap, mark_num = self.scale_mark(
                    max(self.wcfg["scale_mark_degree"], 10),
                    self.sw_rot_range,
                    self.bar_width
                )
                self.draw_scale_mark(mark_gap, mark_num)

            # Steering
            self.update_steering(self.raw_steering, self.last_raw_steering)
            self.last_raw_steering = self.raw_steering

    # GUI update methods
    def update_steering(self, curr, last):
        """Steering update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap_background)
        # Draw steering
        self.draw_steering(painter)
        # Draw scale marks
        if self.wcfg["show_scale_mark"]:
            painter.drawPixmap(0, 0, self.pixmap_mark)
        # Draw readings
        if self.wcfg["show_steering_angle"]:
            self.draw_readings(painter)

    def draw_background(self):
        """Draw background"""
        self.pixmap_background.fill(self.wcfg["bkg_color"])
        painter = QPainter(self.pixmap_background)
        painter.setPen(Qt.NoPen)
        # Edge mark
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(self.wcfg["bar_edge_color"])
        painter.setBrush(brush)
        painter.drawRect(self.rect_edge_l)
        painter.drawRect(self.rect_edge_r)
        # Center mark
        painter.drawRect(self.bar_edge + self.bar_width - 1, 0, 2, self.bar_height)

    def draw_scale_mark(self, mark_gap=90, mark_num=0):
        """Draw scale mark"""
        self.pixmap_mark.fill(Qt.transparent)
        painter = QPainter(self.pixmap_mark)
        painter.setPen(Qt.NoPen)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(self.wcfg["scale_mark_color"])
        painter.setBrush(brush)
        if mark_num:
            for idx in range(mark_num):
                painter.drawRect(
                    self.bar_edge + self.bar_width - mark_gap * (idx + 1),
                    0, 1, self.bar_height
                )
                painter.drawRect(
                    self.bar_edge + self.bar_width + mark_gap * (idx + 1),
                    0, 1, self.bar_height
                )

    def draw_steering(self, painter):
        """Draw steering"""
        painter.setPen(Qt.NoPen)
        self.brush.setColor(self.wcfg["steering_color"])
        painter.setBrush(self.brush)
        painter.drawRect(
            self.bar_edge + self.bar_width + min(self.raw_steering, 0) * self.bar_width,
            0,
            -min(self.raw_steering, 0) * self.bar_width,
            self.bar_height
        )
        painter.drawRect(
            self.bar_edge + self.bar_width,
            0,
            max(self.raw_steering, 0) * self.bar_width,
            self.bar_height
        )

    def draw_readings(self, painter):
        """Draw readings"""
        angle = round(self.raw_steering * self.sw_rot_range * 0.5)
        self.pen.setColor(self.wcfg["font_color"])
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            self.rect_text_bg_l,
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{abs(angle)}" if min(angle, 0) else ""
        )
        painter.drawText(
            self.rect_text_bg_r,
            Qt.AlignRight | Qt.AlignVCenter,
            f"{abs(angle)}" if max(angle, 0) else ""
        )

    # Additional methods
    @staticmethod
    def scale_mark(degree, rot_range, width):
        """mark gap(degree) divide half of full steering range (degree) and multiply scale"""
        mark_num = max(int(rot_range / max(degree, 10) * 0.5), 0)
        if rot_range != 0:
            return degree / (rot_range * 0.5) * width, mark_num
        return 0, mark_num
