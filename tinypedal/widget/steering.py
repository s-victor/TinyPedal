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
Steering Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush, QColor

from ..api_control import api
from ..base import Widget

WIDGET_NAME = "steering"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        font_m = self.get_font_metrics(self.font)
        self.font_offset = self.calc_font_offset(font_m)

        # Config variable
        self.padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        text_height = int(font_m.capital + pady * 2) if self.wcfg["show_steering_angle"] else 0
        self.bar_width = max(self.wcfg["bar_width"], 20)
        self.bar_height = max(self.wcfg["bar_height"], text_height)
        self.bar_edge = max(self.wcfg["bar_edge_width"], 0)

        # Config canvas
        self.resize((self.bar_width + self.bar_edge) * 2, self.bar_height)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        # Last data
        self.raw_steering = 0
        self.last_raw_steering = None
        self.sw_rot_range = 1
        self.last_sw_rot_range = 0
        self.mark_gap = 0
        self.mark_num = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Read steering data
            self.raw_steering = api.read.input.steering_raw()
            self.sw_rot_range = api.read.input.steering_range_physical()

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
        #painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw steering
        self.draw_steering(painter)

    def draw_steering(self, painter):
        """Steering"""
        # Background size
        rect_bg_l = QRectF(
            self.bar_edge,
            0,
            self.bar_width,
            self.bar_height
        )
        rect_bg_r = QRectF(
            self.bar_edge + self.bar_width,
            0,
            self.bar_width,
            self.bar_height
        )

        # Edge size
        rect_edge_l = QRectF(
            0,
            0,
            self.bar_edge,
            self.bar_height
        )
        rect_edge_r = QRectF(
            self.bar_edge + self.bar_width * 2,
            0,
            self.bar_edge,
            self.bar_height
        )

        # Steering size
        rect_steering_l = QRectF(
            self.bar_edge + self.bar_width + min(self.raw_steering, 0) * self.bar_width,
            0,
            -min(self.raw_steering, 0) * self.bar_width,
            self.bar_height
        )
        rect_steering_r = QRectF(
            self.bar_edge + self.bar_width,
            0,
            max(self.raw_steering, 0) * self.bar_width,
            self.bar_height
        )

        # Update background
        painter.setPen(Qt.NoPen)
        self.brush.setColor(QColor(self.wcfg["bkg_color"]))
        painter.setBrush(self.brush)
        painter.drawRect(rect_bg_l)
        painter.drawRect(rect_bg_r)

        # Edge mark
        self.brush.setColor(QColor(self.wcfg["bar_edge_color"]))
        painter.setBrush(self.brush)
        painter.drawRect(rect_edge_l)
        painter.drawRect(rect_edge_r)

        # Center mark
        painter.drawRect(self.bar_edge + self.bar_width - 1, 0, 2, self.bar_height)

        # Update steering
        self.brush.setColor(QColor(self.wcfg["steering_color"]))
        painter.setBrush(self.brush)
        painter.drawRect(rect_steering_l)
        painter.drawRect(rect_steering_r)

        # Scale mark
        if self.wcfg["show_scale_mark"]:
            if self.sw_rot_range != self.last_sw_rot_range:  # recalc if changed
                self.last_sw_rot_range = self.sw_rot_range
                self.mark_gap, self.mark_num = self.scale_mark(
                    max(self.wcfg["scale_mark_degree"], 10),
                    self.sw_rot_range,
                    self.bar_width
                )
            self.brush.setColor(QColor(self.wcfg["scale_mark_color"]))
            painter.setBrush(self.brush)
            if self.mark_num:
                for idx in range(self.mark_num):
                    painter.drawRect(
                        self.bar_edge + self.bar_width - self.mark_gap * (idx + 1),
                        0, 1, self.bar_height
                    )
                    painter.drawRect(
                        self.bar_edge + self.bar_width + self.mark_gap * (idx + 1),
                        0, 1, self.bar_height
                    )

        # Update text
        if self.wcfg["show_steering_angle"]:
            angle = round(self.raw_steering * self.sw_rot_range / 2)
            self.pen.setColor(QColor(self.wcfg["font_color"]))
            painter.setPen(self.pen)
            painter.setFont(self.font)
            painter.drawText(
                rect_bg_l.adjusted(self.padx, self.font_offset, 0, 0),
                Qt.AlignLeft | Qt.AlignVCenter,
                f"{abs(angle)}" if min(angle, 0) else ""
            )
            painter.drawText(
                rect_bg_r.adjusted(0, self.font_offset, -self.padx, 0),
                Qt.AlignRight | Qt.AlignVCenter,
                f"{abs(angle)}" if max(angle, 0) else ""
            )

    # Additional methods
    @staticmethod
    def scale_mark(degree, rot_range, width):
        """mark gap(degree) divide half of full steering range (degree) and multiply scale"""
        mark_num = max(int(rot_range / max(degree, 10) / 2), 0)
        if rot_range != 0:
            return degree / (rot_range / 2) * width, mark_num
        return 0, mark_num
