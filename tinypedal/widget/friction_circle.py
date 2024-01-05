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
Friction circle Widget
"""

from collections import deque
from PySide2.QtCore import Qt, Slot, QPointF, QRectF
from PySide2.QtGui import QPainter, QPixmap, QRadialGradient, QPen, QBrush

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "friction_circle"


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
        text_width = font_m.width * 4
        display_size = max(int(self.wcfg["display_size"]), 20)
        self.display_radius_g = max(self.wcfg["display_radius_g"], 1)
        self.global_scale = (display_size * 0.5) / self.display_radius_g
        self.area_size = display_size + font_m.height * 2
        self.area_center = self.area_size * 0.5

        self.dot_size = max(self.wcfg["dot_size"], 1)
        self.rect_dot = QRectF(
            self.dot_size * 0.5,
            self.dot_size * 0.5,
            self.dot_size,
            self.dot_size
        )
        self.rect_gforce_top = QRectF(
            self.area_center - text_width * 0.5,
            0,
            text_width,
            font_m.height
        )
        self.rect_gforce_bottom = QRectF(
            self.area_center - text_width * 0.5,
            self.area_size - font_m.height,
            text_width,
            font_m.height
        )
        self.rect_gforce_left = QRectF(
            0,
            self.area_center - font_m.height,
            text_width,
            font_m.height
        )
        self.rect_gforce_right = QRectF(
            self.area_size - text_width,
            self.area_center - font_m.height,
            text_width,
            font_m.height
        )
        self.rect_text_gforce_top = self.rect_gforce_top.adjusted(0, font_offset, 0, 0)
        self.rect_text_gforce_bottom = self.rect_gforce_bottom.adjusted(0, font_offset, 0, 0)
        self.rect_text_gforce_left = self.rect_gforce_left.adjusted(0, font_offset, 0, 0)
        self.rect_text_gforce_right = self.rect_gforce_right.adjusted(0, font_offset, 0, 0)

        # Config canvas
        self.resize(self.area_size, self.area_size)
        self.pixmap_background = QPixmap(self.area_size, self.area_size)
        self.pixmap_dot = QPixmap(self.dot_size * 2, self.dot_size * 2)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.draw_background()
        self.draw_dot()

        # Last data
        self.checked = False

        self.gforce_raw = 0,0
        self.last_gforce_raw = None
        self.data_gforce = deque([], max(self.wcfg["trace_max_samples"], 5))
        self.last_x = 0
        self.last_y = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read acceleration data
            self.gforce_raw = self.gforce_orientation(
                minfo.force.lgtGForceRaw,
                minfo.force.latGForceRaw
            )
            self.update_gforce(self.gforce_raw, self.last_gforce_raw)
            self.last_gforce_raw = self.gforce_raw

        else:
            if self.checked:
                self.checked = False
                self.data_gforce.clear()

    # GUI update methods
    def update_gforce(self, curr, last):
        """G force update"""
        if curr != last:
            self.last_x = self.scale_position(self.gforce_raw[1])
            self.last_y = self.scale_position(self.gforce_raw[0])
            if self.wcfg["show_trace"]:
                self.data_gforce.append(QPointF(self.last_x, self.last_y))
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Draw g circle background
        painter.drawPixmap(0, 0, self.pixmap_background)
        # Draw max g circle
        if self.wcfg["show_max_average_lateral_g_circle"]:
            self.draw_circle_mark(
                painter,
                self.wcfg["max_average_lateral_g_circle_style"],
                minfo.force.maxAvgLatGForce,
                self.wcfg["max_average_lateral_g_circle_width"],
                self.wcfg["max_average_lateral_g_circle_color"]
            )
        # Draw trace
        if self.wcfg["show_trace"] and self.data_gforce:
            self.draw_trace(painter)
        # Draw dot
        if self.wcfg["show_dot"]:
            painter.drawPixmap(
                self.last_x - self.dot_size, self.last_y - self.dot_size, self.pixmap_dot)
        # Draw text
        if self.wcfg["show_readings"]:
            self.draw_text(painter)

    def draw_background(self):
        """Draw g circle background"""
        if self.wcfg["show_background"]:
            self.pixmap_background.fill(self.wcfg["bkg_color"])
        else:
            self.pixmap_background.fill(Qt.transparent)
        painter = QPainter(self.pixmap_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.wcfg["show_circle_background"]:
            painter.setPen(Qt.NoPen)
            circle_scale = round(self.display_radius_g * self.global_scale)
            if self.wcfg["show_fade_out"]:
                rad_gra = QRadialGradient(
                    self.area_center,
                    self.area_center,
                    circle_scale,
                    self.area_center,
                    self.area_center
                )
                rad_gra.setColorAt(
                    calc.zero_one_range(self.wcfg["fade_in_radius"]),
                    self.wcfg["bkg_color_circle"])
                rad_gra.setColorAt(
                    calc.zero_one_range(self.wcfg["fade_out_radius"]),
                    Qt.transparent)
                painter.setBrush(rad_gra)
            else:
                brush = QBrush(Qt.SolidPattern)
                brush.setColor(self.wcfg["bkg_color_circle"])
                painter.setBrush(brush)
            painter.drawEllipse(
                self.area_center - circle_scale,
                self.area_center - circle_scale,
                circle_scale * 2,
                circle_scale * 2
            )

        # Draw center mark
        if self.wcfg["show_center_mark"]:
            if self.wcfg["center_mark_style"]:
                self.pen.setStyle(Qt.SolidLine)
            else:
                self.pen.setStyle(Qt.DashLine)
            mark_scale = self.global_scale * min(
                self.wcfg["center_mark_radius_g"], self.display_radius_g
            )
            self.pen.setWidth(self.wcfg["center_mark_width"])
            self.pen.setColor(self.wcfg["center_mark_color"])
            painter.setPen(self.pen)
            painter.drawLine(
                self.area_center,
                self.area_center,
                self.area_center - mark_scale,
                self.area_center
            )
            painter.drawLine(
                self.area_center,
                self.area_center,
                self.area_center,
                self.area_center + mark_scale
            )
            painter.drawLine(
                self.area_center,
                self.area_center,
                self.area_center,
                self.area_center - mark_scale
            )
            painter.drawLine(
                self.area_center,
                self.area_center,
                self.area_center + mark_scale,
                self.area_center
            )

        # Draw circle mark
        if self.wcfg["show_reference_circle"]:
            for idx in range(1, 6):
                self.draw_circle_mark(
                    painter,
                    self.wcfg[f"reference_circle_{idx}_style"],
                    self.wcfg[f"reference_circle_{idx}_radius_g"],
                    self.wcfg[f"reference_circle_{idx}_width"],
                    self.wcfg[f"reference_circle_{idx}_color"]
                )

    def draw_circle_mark(self, painter, style, radius, width, color):
        """Draw circle mark"""
        if radius <= self.display_radius_g and width > 0:
            circle_scale = round(radius * self.global_scale)
            circle_pos = self.area_center - circle_scale
            circle_size = circle_scale * 2
            if style:
                self.pen.setStyle(Qt.SolidLine)
            else:
                self.pen.setStyle(Qt.DashLine)
            self.pen.setWidth(width)
            self.pen.setColor(color)
            painter.setPen(self.pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(circle_pos, circle_pos, circle_size, circle_size)

    def draw_trace(self, painter):
        """Draw trace"""
        self.pen.setWidth(self.wcfg["trace_width"])
        self.pen.setColor(self.wcfg["trace_color"])
        self.pen.setStyle(Qt.SolidLine)
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        if self.wcfg["trace_style"]:
            painter.drawPoints(self.data_gforce)
        else:
            painter.drawPolyline(self.data_gforce)

    def draw_dot(self):
        """Draw dot"""
        self.pixmap_dot.fill(Qt.transparent)
        painter = QPainter(self.pixmap_dot)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.wcfg["dot_outline_width"] > 0:
            self.pen.setWidth(self.wcfg["dot_outline_width"])
            self.pen.setColor(self.wcfg["dot_outline_color"])
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        brush = QBrush(Qt.SolidPattern)
        brush.setColor(self.wcfg["dot_color"])
        painter.setBrush(brush)
        painter.drawEllipse(self.rect_dot)

    def draw_text(self, painter):
        """Draw text"""
        # Draw text
        painter.setFont(self.font)

        # Current G reading
        self.pen.setColor(self.wcfg["font_color"])
        painter.setPen(self.pen)

        painter.drawText(
            self.rect_text_gforce_top,
            Qt.AlignCenter,
            f"{abs(self.gforce_raw[0]):.2f}"[:4]
        )
        painter.drawText(
            self.rect_text_gforce_right,
            Qt.AlignCenter,
            f"{abs(self.gforce_raw[1]):.2f}"[:4]
        )

        # Max G reading
        self.pen.setColor(self.wcfg["font_color_highlight"])
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_text_gforce_bottom,
            Qt.AlignCenter,
            f"{minfo.force.maxLgtGForce:.2f}"[:4]
        )
        painter.drawText(
            self.rect_text_gforce_left,
            Qt.AlignCenter,
            f"{minfo.force.maxLatGForce:.2f}"[:4]
        )

    # Additional methods
    def gforce_orientation(self, lgt, lat):
        """G force orientation, round to 3 digits"""
        if self.wcfg["display_orientation"]:
            return round(lgt, 3), round(-lat, 3)  # accel top, brake bottom
        return round(-lgt, 3), round(lat, 3)

    def scale_position(self, position, offset=0):
        """Scale position coordinate to global scale"""
        return position * self.global_scale + self.area_center - offset
