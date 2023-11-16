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
Heading Widget
"""

from PySide2.QtCore import Qt, Slot, QPointF, QRectF
from PySide2.QtGui import (
    QPainter,
    QPixmap,
    QPen,
    QBrush,
    QColor,
    QPolygonF,
    QFont,
    QFontMetrics
)

from .. import calculation as calc
from ..api_control import api
from ..base import Widget

WIDGET_NAME = "heading"


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
        self.area_size = max(int(self.wcfg["display_size"]), 20)
        self.area_center = self.area_size / 2
        self.dot_size = max(self.wcfg["dot_size"], 1)

        text_width = font_w * 5

        if self.wcfg["enable_auto_font_offset"]:
            self.font_offset = font_c + font_d * 2 + font_l * 2 - font_h
        else:
            self.font_offset = self.wcfg["font_offset_vertical"]

        self.rect_angle = QRectF(
            self.area_center - text_width / 2,
            self.area_center + self.area_center / 2 - font_h,
            text_width,
            font_h * 2
        )

        icon_source = QPixmap("images/icon_compass.png")
        self.icon_inst = icon_source.scaledToWidth(
            self.area_size * 2,
            mode=Qt.SmoothTransformation
        )

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_circle_background()

        # Last data
        self.direction_angle = 0
        self.last_direction_angle = None
        self.yaw_angle = 0
        self.last_yaw_angle = None
        self.last_pos = (0,0)

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Read yaw, position data
            self.yaw_angle = calc.rad2deg(api.read.vehicle.orientation_yaw_radians()) + 180
            pos_curr = (api.read.vehicle.pos_longitudinal(),
                        api.read.vehicle.pos_lateral())

            if self.last_pos != pos_curr and calc.distance(pos_curr, self.last_pos) > 1:
                self.direction_angle = self.yaw_angle - calc.rad2deg(calc.oriyaw2rad(
                     pos_curr[0] - self.last_pos[0], pos_curr[1] - self.last_pos[1])) + 180
                self.last_pos = pos_curr

            self.update_yaw(self.yaw_angle, self.last_yaw_angle)
            self.last_yaw_angle = self.yaw_angle

    # GUI update methods
    def update_yaw(self, curr, last):
        """Yaw update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)

        # Draw circle background
        painter.drawPixmap(
            0, 0, self.area_size, self.area_size, self.circle_background)

        # Draw compass bearing
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(self.yaw_angle)
        painter.drawPixmap(
            -self.area_center, -self.area_center,
            self.area_size, self.area_size,
            self.icon_inst)
        painter.resetTransform()

        # Draw yaw line
        if self.wcfg["show_yaw_line"]:
            self.draw_yaw_line(painter)
        # Draw direction line
        if self.wcfg["show_direction_line"]:
            self.draw_direction_line(painter)
        # Draw dot
        if self.wcfg["show_dot"]:
            self.draw_dot(painter)
        # Draw text
        if self.wcfg["show_yaw_angle_reading"]:
            self.draw_text(painter)

    def draw_circle_background(self):
        """Draw circle background"""
        self.circle_background = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.circle_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(Qt.NoPen)
        if self.wcfg["show_background"]:
            painter.fillRect(0, 0, self.area_size, self.area_size, self.wcfg["bkg_color"])
        else:
            painter.fillRect(0, 0, self.area_size, self.area_size, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        if self.wcfg["show_circle_background"]:
            self.brush.setColor(QColor(self.wcfg["bkg_color_circle"]))
            painter.setBrush(self.brush)
            painter.drawEllipse(
                0,
                0,
                self.area_size,
                self.area_size
            )

        # Draw center mark
        if self.wcfg["show_center_mark"]:
            if self.wcfg["center_mark_style"]:
                self.pen.setStyle(Qt.SolidLine)
            else:
                self.pen.setStyle(Qt.DashLine)
            mark_scale = self.area_center * min(
                self.wcfg["center_mark_length_scale"], 1
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

    def draw_direction_line(self, painter):
        """Draw direction line"""
        self.pen.setWidth(self.wcfg["direction_line_width"])
        self.pen.setColor(QColor(self.wcfg["direction_line_color"]))
        self.pen.setStyle(Qt.SolidLine)
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        line = [
            QPointF(0, -self.area_center * self.wcfg["direction_line_head_scale"]),
            QPointF(0, self.area_center * self.wcfg["direction_line_tail_scale"])
        ]
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(self.direction_angle)
        painter.drawPolyline(QPolygonF(line))
        painter.resetTransform()

    def draw_yaw_line(self, painter):
        """Draw yaw line"""
        self.pen.setWidth(self.wcfg["yaw_line_width"])
        self.pen.setColor(QColor(self.wcfg["yaw_line_color"]))
        self.pen.setStyle(Qt.SolidLine)
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        line = [
            QPointF(0, -self.area_center * self.wcfg["yaw_line_head_scale"]),
            QPointF(0, self.area_center * self.wcfg["yaw_line_tail_scale"])
        ]
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(0)
        painter.drawPolyline(QPolygonF(line))
        painter.resetTransform()

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
            (self.area_size - self.dot_size) / 2,
            (self.area_size - self.dot_size) / 2,
            self.dot_size,
            self.dot_size
        )

    def draw_text(self, painter):
        """Draw text"""
        painter.setFont(self.font)
        self.pen.setColor(QColor(self.wcfg["font_color"]))
        painter.setPen(self.pen)

        angle = self.direction_angle
        if angle < -180:
            angle = 360 + angle
        elif angle > 180:
            angle = 360 - angle

        if abs(angle) > 180:
            angle = 360 - abs(angle)

        if self.wcfg["show_degree_sign"]:
            text = f" {abs(angle):.0f}°"
        else:
            text = f"{abs(angle):.0f}"

        painter.drawText(
            self.rect_angle.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            text
        )
