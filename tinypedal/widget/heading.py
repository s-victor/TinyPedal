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
Heading Widget
"""

from PySide2.QtCore import Qt, Slot, QPointF, QRectF
from PySide2.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QPolygonF

from .. import calculation as calc
from ..api_control import api
from . import Overlay

WIDGET_NAME = "heading"


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
        self.font_offset = self.calc_font_offset(font_m)

        # Config variable
        self.area_size = max(int(self.wcfg["display_size"]), 20)
        self.area_center = self.area_size / 2
        self.dot_size = max(self.wcfg["dot_size"], 1)

        icon_source = QPixmap("images/icon_compass.png")
        self.icon_inst = icon_source.scaledToWidth(
            self.area_size * 2,
            mode=Qt.SmoothTransformation
        )

        self.decimals = max(int(self.wcfg["decimal_places"]), 0)
        text_width = font_m.width * (5 + self.decimals)

        self.rect_yaw_angle = QRectF(
            self.area_size * self.wcfg["yaw_angle_offset_x"] - text_width / 2,
            self.area_size * self.wcfg["yaw_angle_offset_y"] - font_m.height / 2,
            text_width,
            font_m.height
        )
        self.rect_slip_angle = QRectF(
            self.area_size * self.wcfg["slip_angle_offset_x"] - text_width / 2,
            self.area_size * self.wcfg["slip_angle_offset_y"] - font_m.height / 2,
            text_width,
            font_m.height
        )
        self.dir_line = QPolygonF((
            QPointF(0, -self.area_center * self.wcfg["direction_line_head_scale"]),
            QPointF(0, self.area_center * self.wcfg["direction_line_tail_scale"])
        ))
        self.yaw_line = QPolygonF((
            QPointF(0, -self.area_center * self.wcfg["yaw_line_head_scale"]),
            QPointF(0, self.area_center * self.wcfg["yaw_line_tail_scale"])
        ))
        self.slip_angle_line = QPolygonF((
            QPointF(0, -self.area_center * self.wcfg["slip_angle_line_head_scale"]),
            QPointF(0, self.area_center * self.wcfg["slip_angle_line_tail_scale"])
        ))

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_circle_background()

        # Last data
        self.veh_ori_yaw = 0
        self.last_veh_ori_yaw = None
        self.last_pos = (0,0)
        self.yaw_angle = 0
        self.slip_angle = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Read speed, position data
            speed = api.read.vehicle.speed()
            pos_curr = (api.read.vehicle.pos_longitudinal(),
                        api.read.vehicle.pos_lateral())

            # Vehicle orientation yaw
            self.veh_ori_yaw = calc.rad2deg(api.read.vehicle.orientation_yaw_radians()) + 180

            # Direction of travel yaw angle
            if self.last_pos != pos_curr and speed > 1:
                self.yaw_angle = self.veh_ori_yaw - calc.rad2deg(calc.oriyaw2rad(
                     pos_curr[0] - self.last_pos[0], pos_curr[1] - self.last_pos[1])) + 180
                self.last_pos = pos_curr
            elif speed <= 1:
                self.yaw_angle = 0
                self.last_pos = pos_curr

            # Slip angle
            if speed > 1:
                self.slip_angle = calc.rad2deg(
                    (api.read.wheel.slip_angle_fl() + api.read.wheel.slip_angle_fr()) / 2)
            else:
                self.slip_angle = 0

            self.update_yaw(self.veh_ori_yaw, self.last_veh_ori_yaw)
            self.last_veh_ori_yaw = self.veh_ori_yaw

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
        painter.rotate(self.veh_ori_yaw)
        painter.drawPixmap(
            -self.area_center, -self.area_center,
            self.area_size, self.area_size,
            self.icon_inst)
        painter.resetTransform()

        # Draw yaw line
        if self.wcfg["show_yaw_line"]:
            self.draw_yaw_line(painter)
        # Draw slip angle line
        if self.wcfg["show_slip_angle_line"]:
            self.draw_slip_angle_line(painter)
        # Draw direction line
        if self.wcfg["show_direction_line"]:
            self.draw_direction_line(painter)
        # Draw dot
        if self.wcfg["show_dot"]:
            self.draw_dot(painter)
        # Draw text
        if self.wcfg["show_yaw_angle_reading"]:
            self.draw_yaw_text(painter)
        if self.wcfg["show_slip_angle_reading"]:
            self.draw_slip_angle_text(painter)

    def draw_circle_background(self):
        """Draw circle background"""
        self.circle_background = QPixmap(self.area_size, self.area_size)
        if self.wcfg["show_background"]:
            self.circle_background.fill(QColor(self.wcfg["bkg_color"]))
        else:
            self.circle_background.fill(Qt.transparent)
        painter = QPainter(self.circle_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw circle background
        if self.wcfg["show_circle_background"]:
            painter.setPen(Qt.NoPen)
            self.brush.setColor(QColor(self.wcfg["bkg_color_circle"]))
            painter.setBrush(self.brush)
            painter.drawEllipse(0, 0, self.area_size, self.area_size)

        # Draw center mark
        if self.wcfg["show_center_mark"]:
            if self.wcfg["center_mark_style"]:
                self.pen.setStyle(Qt.SolidLine)
            else:
                self.pen.setStyle(Qt.DashLine)
            mark_scale = self.area_center * min(self.wcfg["center_mark_length_scale"], 1)
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
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(self.yaw_angle)
        painter.drawPolyline(self.dir_line)
        painter.resetTransform()

    def draw_yaw_line(self, painter):
        """Draw yaw line"""
        self.pen.setWidth(self.wcfg["yaw_line_width"])
        self.pen.setColor(QColor(self.wcfg["yaw_line_color"]))
        self.pen.setStyle(Qt.SolidLine)
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(0)
        painter.drawPolyline(self.yaw_line)
        painter.resetTransform()

    def draw_slip_angle_line(self, painter):
        """Draw slip angle line"""
        self.pen.setWidth(self.wcfg["slip_angle_line_width"])
        self.pen.setColor(QColor(self.wcfg["slip_angle_line_color"]))
        self.pen.setStyle(Qt.SolidLine)
        painter.setPen(self.pen)
        painter.setBrush(Qt.NoBrush)
        painter.resetTransform()
        painter.translate(self.area_center, self.area_center)
        painter.rotate(self.slip_angle)
        painter.drawPolyline(self.slip_angle_line)
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

    def draw_yaw_text(self, painter):
        """Draw yaw text"""
        painter.setFont(self.font)
        self.pen.setColor(QColor(self.wcfg["font_color_yaw_angle"]))
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_yaw_angle.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            self.format_angle(self.display_yaw_angle(self.yaw_angle))
        )

    def draw_slip_angle_text(self, painter):
        """Draw slip angle text"""
        painter.setFont(self.font)
        self.pen.setColor(QColor(self.wcfg["font_color_slip_angle"]))
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_slip_angle.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            self.format_angle(self.slip_angle)
        )

    # Additional methods
    @staticmethod
    def display_yaw_angle(angle):
        """Set yaw angle display range"""
        if angle < -180:
            angle = 360 + angle
        elif angle > 180:
            angle = 360 - angle
        if abs(angle) > 180:
            angle = 360 - abs(angle)
        return angle

    def format_angle(self, angle):
        """Format angle text"""
        if self.wcfg["show_degree_sign"]:
            return f" {abs(angle):.0{self.decimals}f}°"
        return f"{abs(angle):.0{self.decimals}f}"
