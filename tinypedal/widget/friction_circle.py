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
Friction circle Widget
"""

from PySide2.QtCore import Qt, Slot, QPointF, QRectF
from PySide2.QtGui import (
    QPainter,
    QPixmap,
    QRadialGradient,
    QPen,
    QBrush,
    QColor,
    QPolygonF,
    QFont,
    QFontMetrics
)

from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "friction_circle"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        self.font.setWeight(getattr(QFont, self.wcfg['font_weight'].capitalize()))

        font_w = QFontMetrics(self.font).averageCharWidth()
        font_h = QFontMetrics(self.font).height()
        font_l = QFontMetrics(self.font).leading()
        font_c = QFontMetrics(self.font).capHeight()
        font_d = QFontMetrics(self.font).descent()

        # Config variable
        text_width = font_w * 4
        display_size = max(int(self.wcfg["display_size"]), 20)
        self.display_radius_g = max(self.wcfg["display_radius_g"], 1)
        self.global_scale = (display_size / 2) / self.display_radius_g
        self.area_size = display_size + font_h * 2
        self.area_center = self.area_size / 2
        self.dot_size = max(self.wcfg["dot_size"], 1)

        if self.wcfg["enable_auto_font_offset"]:
            self.font_offset = font_c + font_d * 2 + font_l * 2 - font_h
        else:
            self.font_offset = self.wcfg["font_offset_vertical"]

        self.rect_gforce_top = QRectF(
            self.area_center - text_width / 2,
            0,
            text_width,
            font_h
        )
        self.rect_gforce_bottom = QRectF(
            self.area_center - text_width / 2,
            self.area_size - font_h,
            text_width,
            font_h
        )
        self.rect_gforce_left = QRectF(
            0,
            self.area_center - font_h,
            text_width,
            font_h
        )
        self.rect_gforce_right = QRectF(
            self.area_size - text_width,
            self.area_center - font_h,
            text_width,
            font_h
        )

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_circle_background()

        # Last data
        self.checked = False

        self.gforce_raw = [0,0]
        self.last_gforce_raw = None
        self.gforce_trace = []

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read acceleration data
            self.gforce_raw = self.gforce_orientation(
                mctrl.module_force.output.LgtGForceRaw,
                mctrl.module_force.output.LatGForceRaw
            )
            self.update_gforce(self.gforce_raw, self.last_gforce_raw)
            self.last_gforce_raw = self.gforce_raw

        else:
            if self.checked:
                self.checked = False
                self.gforce_trace.clear()

    # GUI update methods
    def update_gforce(self, curr, last):
        """G force update"""
        if curr != last:
            if self.wcfg["show_trace"]:
                self.update_gforce_trace()
            self.update()

    def update_gforce_trace(self):
        """G force trace update"""
        if len(self.gforce_trace) > self.wcfg["trace_max_samples"]:
            self.gforce_trace.pop(0)
        self.gforce_trace.append(
            QPointF(
                self.scale_position(self.gforce_raw[1]),
                self.scale_position(self.gforce_raw[0])
            )
        )

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw g circle background
        painter.drawPixmap(
            0, 0, self.area_size, self.area_size, self.circle_background)

        # Draw max g circle
        if self.wcfg["show_max_average_lateral_g_circle"]:
            self.draw_circle_mark(
                painter,
                self.wcfg["max_average_lateral_g_circle_style"],
                mctrl.module_force.output.MaxAvgLatGForce,
                self.wcfg["max_average_lateral_g_circle_width"],
                self.wcfg["max_average_lateral_g_circle_color"]
            )
        # Draw trace
        if self.wcfg["show_trace"] and self.gforce_trace:
            self.draw_trace(painter)
        # Draw dot
        if self.wcfg["show_dot"]:
            self.draw_dot(painter)
        # Draw text
        if self.wcfg["show_readings"]:
            self.draw_text(painter)

    def draw_circle_background(self):
        """Draw g circle background"""
        self.circle_background = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.circle_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(Qt.NoPen)
        painter.fillRect(0, 0, self.area_size, self.area_size, QColor(0,0,0,0))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        if self.wcfg["show_background"]:
            circle_scale = round(self.display_radius_g * self.global_scale)
            if self.wcfg["background_style"]:
                self.brush.setColor(QColor(self.wcfg["bkg_color"]))
                painter.setBrush(self.brush)
            else:
                rad_gra = QRadialGradient(
                    self.area_center,
                    self.area_center,
                    circle_scale,
                    self.area_center,
                    self.area_center
                )
                rad_gra.setColorAt(0.5, QColor(self.wcfg["bkg_color"]))
                rad_gra.setColorAt(0.98, QColor(Qt.transparent))
                painter.setBrush(rad_gra)
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
            self.pen.setColor(QColor(self.wcfg["center_mark_color"]))
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
        if radius <= self.display_radius_g and width:
            circle_scale = round(radius * self.global_scale)
            if style:
                self.pen.setStyle(Qt.SolidLine)
            else:
                self.pen.setStyle(Qt.DashLine)
            self.pen.setWidth(width)
            self.pen.setColor(QColor(color))
            painter.setPen(self.pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(
                self.area_center - circle_scale,
                self.area_center - circle_scale,
                circle_scale * 2,
                circle_scale * 2
            )

    def draw_trace(self, painter):
        """Draw trace"""
        self.pen.setWidth(self.wcfg["trace_width"])
        self.pen.setColor(QColor(self.wcfg["trace_color"]))
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        if self.wcfg["trace_style"]:
            painter.drawPoints(QPolygonF(self.gforce_trace))
        else:
            painter.drawPolyline(QPolygonF(self.gforce_trace))

    def draw_dot(self, painter):
        """Draw dot"""
        if self.wcfg["dot_outline_width"]:
            self.pen.setWidth(self.wcfg["dot_outline_width"])
            self.pen.setColor(QColor(self.wcfg["dot_outline_color"]))
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        self.brush.setColor(QColor(self.wcfg["dot_color"]))
        painter.setBrush(self.brush)
        painter.drawEllipse(
            self.scale_position(self.gforce_raw[1]) - self.dot_size / 2,
            self.scale_position(self.gforce_raw[0]) - self.dot_size / 2,
            self.dot_size,
            self.dot_size
        )

    def draw_text(self, painter):
        """Draw text"""
        # Draw text
        painter.setFont(self.font)

        # Current G reading
        self.pen.setColor(QColor(self.wcfg["font_color"]))
        painter.setPen(self.pen)

        painter.drawText(
            self.rect_gforce_top.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{abs(self.gforce_raw[0]):.2f}"[:4]
        )
        painter.drawText(
            self.rect_gforce_right.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{abs(self.gforce_raw[1]):.2f}"[:4]
        )

        # Max G reading
        self.pen.setColor(QColor(self.wcfg["font_color_highlight"]))
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_gforce_bottom.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{mctrl.module_force.output.MaxLgtGForce:.2f}"[:4]
        )
        painter.drawText(
            self.rect_gforce_left.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{mctrl.module_force.output.MaxLatGForce:.2f}"[:4]
        )

    # Additional methods
    def gforce_orientation(self, lgt, lat):
        """G force orientation"""
        if self.wcfg["display_orientation"]:
            return (round(lgt, 3), round(-lat, 3),)  # accel top, brake bottom
        return (round(-lgt, 3), round(lat, 3),)

    def scale_position(self, position, offset=0):
        """Scale position coordinate to global scale"""
        return position * self.global_scale + self.area_center - offset
