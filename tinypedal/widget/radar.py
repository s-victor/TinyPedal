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
from ..api_control import api
from ..base import Widget
from ..module_info import minfo

WIDGET_NAME = "radar"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        self.global_scale = max(self.wcfg["global_scale"], 0.01)
        self.area_size = max(self.wcfg["radar_radius"], 5) * 2 * self.global_scale
        self.area_center = self.area_size / 2
        self.radar_range = self.wcfg["radar_radius"] * 2.5

        self.veh_width = max(self.wcfg["vehicle_width"], 0.01)
        self.veh_length = max(self.wcfg["vehicle_length"], 0.01)
        self.rect_veh = QRectF(
            -self.veh_width * self.global_scale / 2,
            -self.veh_length * self.global_scale / 2,
            self.veh_width * self.global_scale,
            self.veh_length * self.global_scale
        )
        self.indicator_dimention = self.calc_indicator_dimention(self.veh_width, self.veh_length)

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_radar_background()
        self.draw_radar_marks()
        self.draw_radar_mask()

        # Last data
        self.autohide_timer_start = 1
        self.show_radar = True

        self.vehicles_data = None
        self.last_veh_data_hash = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Auto hide radar if no nearby vehicles
            if self.wcfg["auto_hide"]:
                self.autohide_radar()

            # Vehicles
            veh_data_hash = minfo.vehicles.dataSetHash
            self.update_vehicle(veh_data_hash, self.last_veh_data_hash)
            self.last_veh_data_hash = veh_data_hash

    # GUI update methods
    def update_vehicle(self, curr, last):
        """Vehicle update"""
        if curr != last:
            self.vehicles_data = minfo.vehicles.dataSet
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        if self.show_radar:
            # Draw marks
            painter.drawPixmap(0, 0, self.area_size, self.area_size, self.radar_marks)

            # Draw vehicles
            if self.vehicles_data:
                if self.wcfg["show_overlap_indicator"]:
                    self.draw_warning_indicator(painter, *self.indicator_dimention)
                self.draw_vehicle(painter)

            # Apply mask
            if self.wcfg["show_fade_out"]:
                painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
                painter.drawPixmap(0, 0, self.area_size, self.area_size, self.radar_mask)
                #painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

            # Draw background
            if self.wcfg["show_background"] or self.wcfg["show_circle_background"]:
                # Insert below map & mask
                painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
                painter.drawPixmap(0, 0, self.area_size, self.area_size, self.radar_background)
                #painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def draw_radar_mask(self):
        """radar mask"""
        self.radar_mask = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.radar_mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw radar mask
        painter.fillRect(0, 0, self.area_size, self.area_size, Qt.black)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        rad_gra = QRadialGradient(
            self.area_center,
            self.area_center,
            self.area_center,
            self.area_center,
            self.area_center
        )
        rad_gra.setColorAt(calc.zero_one_range(self.wcfg["fade_in_radius"]), Qt.transparent)
        rad_gra.setColorAt(calc.zero_one_range(self.wcfg["fade_out_radius"]), Qt.black)
        painter.setBrush(rad_gra)
        painter.drawEllipse(0, 0, self.area_size, self.area_size)

    def draw_radar_background(self):
        """Draw radar background"""
        self.radar_background = QPixmap(self.area_size, self.area_size)
        if self.wcfg["show_background"]:
            self.radar_background.fill(QColor(self.wcfg["bkg_color"]))
        else:
            self.radar_background.fill(Qt.transparent)
        painter = QPainter(self.radar_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw circle background
        if self.wcfg["show_circle_background"]:
            painter.setPen(Qt.NoPen)
            self.brush.setColor(QColor(self.wcfg["bkg_color_circle"]))
            painter.setBrush(self.brush)
            painter.drawEllipse(0, 0, self.area_size, self.area_size)

    def draw_radar_marks(self):
        """Draw radar marks"""
        self.radar_marks = QPixmap(self.area_size, self.area_size)
        self.radar_marks.fill(Qt.transparent)
        painter = QPainter(self.radar_marks)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw center mark
        pen = QPen()
        pen.setCapStyle(Qt.FlatCap)
        if self.wcfg["show_center_mark"]:
            if not self.wcfg["center_mark_style"]:
                pen.setStyle(Qt.DashLine)
            else:
                pen.setStyle(Qt.SolidLine)
            mark_scale = self.wcfg["center_mark_radius"] * self.global_scale
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
            circle_scale1 = self.wcfg["distance_circle_1_radius"] * self.global_scale
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

            circle_scale2 = self.wcfg["distance_circle_2_radius"] * self.global_scale
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
        indicator_width, indicator_edge, center_offset):
        """Draw warning indicator"""
        painter.setPen(Qt.NoPen)
        # Real size in meters
        nearest_left = -max_range_x
        nearest_right = max_range_x

        for veh_info in self.vehicles_data:
            if not veh_info.isPlayer:
                raw_pos_x, raw_pos_y = veh_info.relativeRotatedPosXZ
                if abs(raw_pos_x) < max_range_x and abs(raw_pos_y) < max_range_y:
                    if -min_range_x > raw_pos_x > nearest_left:
                        nearest_left = raw_pos_x
                    if min_range_x < raw_pos_x < nearest_right:
                        nearest_right = raw_pos_x

        x_left = self.scale_veh_pos(nearest_left)
        x_right = self.scale_veh_pos(nearest_right)

        if nearest_left > -max_range_x:
            lin_gra = QLinearGradient(
                x_left - indicator_width + center_offset,
                0,
                x_left + center_offset,
                0
            )
            color_center = self.warning_color(
                abs(nearest_left), min_range_x, max_range_x)
            lin_gra.setColorAt(0, Qt.transparent)
            lin_gra.setColorAt(indicator_edge, color_center)
            lin_gra.setColorAt(1, Qt.transparent)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_left - indicator_width + center_offset,
                0, indicator_width, self.area_size
            )

        if nearest_right < max_range_x:
            lin_gra = QLinearGradient(
                x_right - center_offset,
                0,
                x_right + indicator_width - center_offset,
                0
            )
            color_center = self.warning_color(
                abs(nearest_right), min_range_x, max_range_x)
            lin_gra.setColorAt(0, Qt.transparent)
            lin_gra.setColorAt(1 - indicator_edge, color_center)
            lin_gra.setColorAt(1, Qt.transparent)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_right - center_offset,
                0, indicator_width, self.area_size
            )

    def draw_vehicle(self, painter):
        """Draw vehicles"""
        if self.wcfg["vehicle_outline_width"]:
            self.pen.setWidth(self.wcfg["vehicle_outline_width"])
            self.pen.setColor(QColor(self.wcfg["vehicle_outline_color"]))
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        # Draw opponent vehicle within radar range
        painter.resetTransform()
        for veh_info in self.vehicles_data:
            if not veh_info.isPlayer and veh_info.relativeStraightDistance < self.radar_range:
                # Rotated position relative to player
                pos_x, pos_y = (
                    self.scale_veh_pos(veh_info.relativeRotatedPosXZ[0]),
                    self.scale_veh_pos(veh_info.relativeRotatedPosXZ[1])
                )
                # Draw vehicle
                self.brush.setColor(
                    QColor(
                        self.color_lapdiff(
                            veh_info.position,
                            veh_info.inPit,
                            veh_info.isYellow,
                            veh_info.isLapped,
                            veh_info.inGarage,
                        )
                    )
                )
                painter.setBrush(self.brush)

                painter.translate(pos_x, pos_y)
                painter.rotate(calc.rad2deg(-veh_info.relativeOrientationXZRadians))
                self.draw_vehicle_shape(painter)
                painter.resetTransform()

        # Draw player vehicle
        self.brush.setColor(QColor(self.wcfg["vehicle_color_player"]))
        painter.setBrush(self.brush)
        painter.translate(self.area_center, self.area_center)
        self.draw_vehicle_shape(painter)
        painter.resetTransform()

    def draw_vehicle_shape(self, painter):
        """Draw vehicles shape"""
        painter.drawRoundedRect(
            self.rect_veh,
            self.wcfg["vehicle_border_radius"],
            self.wcfg["vehicle_border_radius"]
        )

    # Additional methods
    def scale_veh_pos(self, position):
        """Scale vehicle position coordinate to global scale"""
        return position * self.global_scale + self.area_center

    def warning_color(self, nearest_x, min_range_x, max_range_x):
        """Overtaking warning color"""
        alpha = 1 - (nearest_x - min_range_x) / max_range_x
        if nearest_x < min_range_x * 1.7:
            color = QColor(self.wcfg["indicator_color_critical"])
            color.setAlphaF(alpha)  # alpha changes with nearest distance
        else:
            color = QColor(self.wcfg["indicator_color"])
            color.setAlphaF(alpha)
        return color

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
        lap_etime = api.read.timing.elapsed()
        in_garage = api.read.vehicle.in_garage()

        if self.nearby() or in_garage:
            if not self.autohide_timer_start:
                self.show_radar = True
            self.autohide_timer_start = lap_etime

        if self.autohide_timer_start:
            autohide_timer = lap_etime - self.autohide_timer_start
            if autohide_timer > self.wcfg["auto_hide_time_threshold"]:
                self.show_radar = False
                self.autohide_timer_start = 0

    def nearby(self):
        """Check nearby vehicles, add 0 limit to ignore local player"""
        if self.wcfg["minimum_auto_hide_distance"] == -1:
            return 0 < minfo.vehicles.nearestStraight < self.wcfg["radar_radius"]
        return 0 < minfo.vehicles.nearestStraight < self.wcfg["minimum_auto_hide_distance"]

    def calc_indicator_dimention(self, veh_width, veh_length):
        """Calculate indicator dimention

        Range between player & opponents to show indicator.
        x is left to right range.
        y is forward to backward range.
        """
        min_range_x = veh_width * 0.9  # slightly overlapped
        max_range_x = veh_width * self.wcfg["overlap_detection_range_multiplier"]
        max_range_y = veh_length * 1.2  # safe range for ahead & behind opponents
        indicator_width = veh_width * self.wcfg["indicator_size_multiplier"] * self.global_scale
        indicator_edge = max((indicator_width - 3) / indicator_width, 0.001)  # for antialiasing
        center_offset = veh_width * self.global_scale / 2
        return min_range_x, max_range_x, max_range_y, indicator_width, indicator_edge, center_offset
