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
Radar Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPixmap, QLinearGradient, QRadialGradient, QPen, QBrush, QColor

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "radar"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        self.area_size = max(self.wcfg["radar_radius"], 5) * 2 * self.wcfg["global_scale"]
        self.area_center = self.area_size / 2
        self.veh_width = max(self.wcfg["vehicle_width"], 0.01)
        self.veh_length = max(self.wcfg["vehicle_length"], 0.01)
        self.rect_veh = QRectF(
            -self.veh_width * self.wcfg["global_scale"] / 2,
            -self.veh_length * self.wcfg["global_scale"] / 2,
            self.veh_width * self.wcfg["global_scale"],
            self.veh_length * self.wcfg["global_scale"]
        )
        self.indicator_dimention = self.calc_indicator_dimention(self.veh_width, self.veh_length)

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_radar_background()
        self.draw_radar_mask()

        # Last data
        self.autohide_timer_start = 1
        self.show_radar = True

        self.standings_veh = None
        self.last_standings_veh = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Auto hide radar if no nearby vehicles
            if self.wcfg["auto_hide"]:
                self.autohide_radar()

            # Read orientation & position data
            self.standings_veh = mctrl.module_standings.vehicles
            self.update_radar(self.standings_veh, self.last_standings_veh)
            self.last_standings_veh = self.standings_veh

    # GUI update methods
    def update_radar(self, curr, last):
        """Vehicle update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.show_radar:
            # Draw radar background
            painter.drawPixmap(0, 0, self.area_size, self.area_size, self.radar_background)

            # Draw vehicles
            if self.standings_veh:
                if self.wcfg["show_overlap_indicator"]:
                    self.draw_warning_indicator(painter, *self.indicator_dimention)
                self.draw_vehicle(painter)

            # Apply radar mask
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
            painter.drawPixmap(0, 0, self.area_size, self.area_size, self.radar_mask)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def draw_radar_mask(self):
        """radar mask"""
        self.radar_mask = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.radar_mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw radar mask
        painter.fillRect(0, 0, self.area_size, self.area_size, QColor(0,0,0))
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        rad_gra = QRadialGradient(
            self.area_center,
            self.area_center,
            self.area_center,
            self.area_center,
            self.area_center
        )
        rad_gra.setColorAt(0.6, QColor(0,0,0,0))
        rad_gra.setColorAt(0.98, QColor(0,0,0))
        painter.setBrush(rad_gra)
        painter.drawEllipse(0, 0, self.area_size, self.area_size)

    def draw_radar_background(self):
        """Draw radar background"""
        self.radar_background = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.radar_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.setPen(Qt.NoPen)
        painter.fillRect(0, 0, self.area_size, self.area_size, QColor(0,0,0,0))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Draw center mark
        pen = QPen()
        pen.setCapStyle(Qt.FlatCap)
        if self.wcfg["show_center_mark"]:
            if not self.wcfg["center_mark_style"]:
                pen.setStyle(Qt.DashLine)
            else:
                pen.setStyle(Qt.SolidLine)
            mark_scale = self.wcfg["center_mark_radius"] * self.wcfg["global_scale"]
            pen.setWidth(self.wcfg["center_mark_width"])
            pen.setColor(QColor(self.wcfg["center_mark_color"]))
            painter.setPen(pen)
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
        if self.wcfg["show_distance_circle"]:
            if not self.wcfg["distance_circle_style"]:
                pen.setStyle(Qt.DashLine)
            else:
                pen.setStyle(Qt.SolidLine)
            circle_scale1 = self.wcfg["distance_circle_1_radius"] * self.wcfg["global_scale"]
            if self.wcfg["distance_circle_1_radius"] < self.wcfg["radar_radius"]:
                pen.setWidth(self.wcfg["distance_circle_1_width"])
                pen.setColor(QColor(self.wcfg["distance_circle_1_color"]))
                painter.setPen(pen)
                painter.drawEllipse(
                    self.area_center - circle_scale1,
                    self.area_center - circle_scale1,
                    circle_scale1 * 2,
                    circle_scale1 * 2
                )

            circle_scale2 = self.wcfg["distance_circle_2_radius"] * self.wcfg["global_scale"]
            if self.wcfg["distance_circle_2_radius"] < self.wcfg["radar_radius"]:
                pen.setWidth(self.wcfg["distance_circle_2_width"])
                pen.setColor(QColor(self.wcfg["distance_circle_2_color"]))
                painter.setPen(pen)
                painter.drawEllipse(
                    self.area_center - circle_scale2,
                    self.area_center - circle_scale2,
                    circle_scale2 * 2,
                    circle_scale2 * 2
                )

    def draw_warning_indicator(
        self, painter, min_range_x, max_range_x, max_range_y,
        indicator_width, indicator_edge, indicator_offset):
        """Draw warning indicator"""
        painter.setPen(Qt.NoPen)
        # Real size in meters
        nearest_left = -max_range_x
        nearest_right = max_range_x

        for veh_info in self.standings_veh:
            if not veh_info.IsPlayer:
                raw_pos_x, raw_pos_y = veh_info.RelativeRotatedPosXZ
                if abs(raw_pos_x) < max_range_x and abs(raw_pos_y) < max_range_y:
                    if -min_range_x > raw_pos_x > nearest_left:
                        nearest_left = raw_pos_x
                    if min_range_x < raw_pos_x < nearest_right:
                        nearest_right = raw_pos_x

        x_left = self.scale_veh_pos(nearest_left)
        x_right = self.scale_veh_pos(nearest_right)

        if nearest_left > -max_range_x:
            lin_gra = QLinearGradient(
                x_left - indicator_width + indicator_offset,
                0,
                x_left + indicator_offset,
                0
            )
            color_center, color_edge = self.warning_color(
                abs(nearest_left), min_range_x, max_range_x)
            lin_gra.setColorAt(0, color_edge)
            lin_gra.setColorAt(indicator_edge, color_center)
            lin_gra.setColorAt(1, color_edge)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_left - indicator_width + indicator_offset,
                0, indicator_width, self.area_size
            )

        if nearest_right < max_range_x:
            lin_gra = QLinearGradient(
                x_right - indicator_offset,
                0,
                x_right + indicator_width - indicator_offset,
                0
            )
            color_center, color_edge = self.warning_color(
                abs(nearest_right), min_range_x, max_range_x)
            lin_gra.setColorAt(0, color_edge)
            lin_gra.setColorAt(1 - indicator_edge, color_center)
            lin_gra.setColorAt(1, color_edge)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_right - indicator_offset,
                0, indicator_width, self.area_size
            )

    def draw_vehicle(self, painter):
        """Draw vehicles"""
        # Draw player vehicle
        if self.wcfg["vehicle_outline_width"]:
            self.pen.setWidth(self.wcfg["vehicle_outline_width"])
            self.pen.setColor(QColor(self.wcfg["vehicle_outline_color"]))
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        self.brush.setColor(QColor(self.wcfg["vehicle_color_player"]))
        painter.setBrush(self.brush)
        painter.setPen(self.pen)
        painter.translate(self.area_center, self.area_center)
        painter.drawRoundedRect(
            self.rect_veh,
            self.wcfg["vehicle_border_radius"],
            self.wcfg["vehicle_border_radius"]
        )

        # Draw opponent vehicle within radar_range
        radar_range = self.wcfg["radar_radius"] * 3

        for veh_info in self.standings_veh:
            if not veh_info.IsPlayer and veh_info.RelativeStraightLineDistance < radar_range:
                # Rotated position relative to player
                pos_x, pos_y = tuple(map(self.scale_veh_pos, veh_info.RelativeRotatedPosXZ))

                # Draw vehicle
                self.brush.setColor(
                    QColor(
                        self.color_lapdiff(
                            veh_info.Position,
                            veh_info.InPit,
                            veh_info.IsYellow,
                            veh_info.IsLapped,
                            veh_info.InGarage,
                        )
                    )
                )
                painter.setBrush(self.brush)

                painter.resetTransform()
                painter.translate(pos_x, pos_y)
                painter.rotate(calc.rad2deg(-veh_info.RelativeOrientationXZRadians) - 180)
                painter.drawRoundedRect(
                    self.rect_veh,
                    self.wcfg["vehicle_border_radius"],
                    self.wcfg["vehicle_border_radius"]
                )

        painter.resetTransform()

    # Additional methods
    def scale_veh_pos(self, position):
        """Scale vehicle position coordinate to radar scale"""
        return position * self.wcfg["global_scale"] + self.area_center

    def warning_color(self, nearest_x, min_range_x, max_range_x):
        """Overtaking warning color"""
        alpha = 1 - (nearest_x - min_range_x) / max_range_x
        if nearest_x < min_range_x * 1.7:
            color1 = QColor(self.wcfg["indicator_color_critical"])
            color1.setAlphaF(alpha)  # alpha changes with nearest distance
            color2 = QColor(self.wcfg["indicator_color_critical"])
            color2.setAlphaF(0)  # full transparent
        else:
            color1 = QColor(self.wcfg["indicator_color"])
            color1.setAlphaF(alpha)
            color2 = QColor(self.wcfg["indicator_color"])
            color2.setAlphaF(0)
        return color1, color2

    def color_lapdiff(self, position, in_pit, is_yellow, is_lapped, in_garage):
        """Compare lap differences & set color"""
        if position == 1:
            return self.wcfg["vehicle_color_leader"]
        if in_pit:
            return self.wcfg["vehicle_color_in_pit"]
        if is_yellow and not in_pit + in_garage:
            return self.wcfg["vehicle_color_yellow"]
        if is_lapped > 0:
            return self.wcfg["vehicle_color_laps_ahead"]
        if is_lapped < 0:
            return self.wcfg["vehicle_color_laps_behind"]
        return self.wcfg["vehicle_color_same_lap"]

    def autohide_radar(self):
        """Auto hide radar if no nearby vehicles"""
        lap_etime, ingarage = read_data.radar()

        if self.nearby() or ingarage:
            if not self.autohide_timer_start:
                self.show_radar = True
            self.autohide_timer_start = lap_etime

        if self.autohide_timer_start:
            autohide_timer = lap_etime - self.autohide_timer_start
            if autohide_timer > self.wcfg["auto_hide_time_threshold"]:
                self.show_radar = False
                self.autohide_timer_start = 0

    def nearby(self):
        """Check nearby vehicles"""
        if self.wcfg["minimum_auto_hide_distance"] == -1:
            return mctrl.module_standings.nearest.Straight < self.wcfg["radar_radius"]
        return mctrl.module_standings.nearest.Straight < self.wcfg["minimum_auto_hide_distance"]

    def calc_indicator_dimention(self, veh_width, veh_length):
        """Calculate indicator dimention"""
        min_range_x = veh_width * 0.9  # left to right range
        max_range_x = veh_width * self.wcfg["overlap_detection_range_multiplier"]
        max_range_y = veh_length * 1.2  # forward to backward range
        id_width = veh_width * self.wcfg["indicator_size_multiplier"] * self.wcfg["global_scale"]
        id_edge = max((id_width - 3) / id_width, 0.001)
        id_offset = veh_width * self.wcfg["global_scale"] / 2
        return min_range_x, max_range_x, max_range_y, id_width, id_edge, id_offset
