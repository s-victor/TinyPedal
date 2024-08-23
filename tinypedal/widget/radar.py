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
Radar Widget
"""

from dataclasses import dataclass

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPixmap, QLinearGradient, QRadialGradient, QPen, QBrush, QColor

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "radar"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config variable
        self.global_scale = max(self.wcfg["global_scale"], 0.01)
        self.radar_radius = max(self.wcfg["radar_radius"], 5)
        self.area_size = self.radar_radius * 2 * self.global_scale
        self.area_center = self.area_size * 0.5

        self.veh_width = max(self.wcfg["vehicle_width"], 0.01)
        self.veh_length = max(self.wcfg["vehicle_length"], 0.01)
        self.veh_shape = QRectF(
            -self.veh_width * self.global_scale * 0.5,
            -self.veh_length * self.global_scale * 0.5,
            self.veh_width * self.global_scale,
            self.veh_length * self.global_scale
        )
        self.indicator_dimension = self.calc_indicator_dimension(self.veh_width, self.veh_length)
        self.indicator_color = QColor(self.wcfg["indicator_color"])
        self.indicator_color_critical = QColor(self.wcfg["indicator_color_critical"])
        self.vehicle_hide_range = self.set_range_dimension("vehicle_maximum_visible_distance")
        self.radar_hide_range = self.set_range_dimension("auto_hide_minimum_distance")

        # Config canvas
        self.resize(self.area_size, self.area_size)
        self.pixmap_background = QPixmap(self.area_size, self.area_size)
        self.pixmap_mask = QPixmap(self.area_size, self.area_size)
        self.pixmap_marks = QPixmap(self.area_size, self.area_size)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_background()
        self.draw_radar_marks()
        self.draw_radar_mask()

        # Last data
        self.autohide_timer_start = 1
        self.show_radar = True

        self.vehicles_data = None
        self.last_veh_data_version = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Auto hide radar if no nearby vehicles
            if self.wcfg["auto_hide"]:
                self.set_autohide_state()

            # Vehicles
            veh_data_version = minfo.vehicles.dataSetVersion
            self.update_vehicle(veh_data_version, self.last_veh_data_version)
            self.last_veh_data_version = veh_data_version

    # GUI update methods
    def update_vehicle(self, curr, last):
        """Vehicle update"""
        if curr != last:
            self.vehicles_data = minfo.vehicles.dataSet
            self.update()

    def paintEvent(self, event):
        """Draw"""
        if self.show_radar:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing, True)
            # Draw marks
            painter.drawPixmap(0, 0, self.pixmap_marks)
            # Draw vehicles
            if self.vehicles_data:
                self.draw_vehicle(painter, self.indicator_dimension)
            # Apply mask
            if self.wcfg["show_fade_out"]:
                painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
                painter.drawPixmap(0, 0, self.pixmap_mask)
            # Draw background below map & mask
            if self.wcfg["show_background"] or self.wcfg["show_circle_background"]:
                painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
                painter.drawPixmap(0, 0, self.pixmap_background)

    def draw_background(self):
        """Draw radar background"""
        if self.wcfg["show_background"]:
            self.pixmap_background.fill(self.wcfg["bkg_color"])
        else:
            self.pixmap_background.fill(Qt.transparent)
        painter = QPainter(self.pixmap_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw circle background
        if self.wcfg["show_circle_background"]:
            painter.setPen(Qt.NoPen)
            brush = QBrush(Qt.SolidPattern)
            brush.setColor(self.wcfg["bkg_color_circle"])
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.area_size, self.area_size)

    def draw_radar_mask(self):
        """radar mask"""
        self.pixmap_mask.fill(Qt.black)
        painter = QPainter(self.pixmap_mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw radar mask
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

    def draw_radar_marks(self):
        """Draw radar marks"""
        self.pixmap_marks.fill(Qt.transparent)
        painter = QPainter(self.pixmap_marks)
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
            pen.setColor(self.wcfg["center_mark_color"])
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
            for idx in range(1, 6):
                self.draw_circle_mark(
                    painter, pen,
                    self.wcfg[f"distance_circle_{idx}_style"],
                    self.wcfg[f"distance_circle_{idx}_radius"],
                    self.wcfg[f"distance_circle_{idx}_width"],
                    self.wcfg[f"distance_circle_{idx}_color"]
                )

    def draw_circle_mark(self, painter, pen, style, radius, width, color):
        """Draw circle mark"""
        if radius <= self.radar_radius and width > 0:
            circle_scale = round(radius * self.global_scale)
            circle_pos = self.area_center - circle_scale
            circle_size = circle_scale * 2
            if style:
                pen.setStyle(Qt.SolidLine)
            else:
                pen.setStyle(Qt.DashLine)
            pen.setWidth(width)
            pen.setColor(color)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawEllipse(circle_pos, circle_pos, circle_size, circle_size)

    def draw_warning_indicator(self, painter, indicator, nearest_left, nearest_right):
        """Draw warning indicator"""
        # Scale to display size
        x_left = self.scale_veh_pos(nearest_left)
        x_right = self.scale_veh_pos(nearest_right)

        painter.setPen(Qt.NoPen)
        # Draw left side indicator
        if nearest_left > -indicator.max_range_x:
            lin_gra = QLinearGradient(
                x_left - indicator.width + indicator.offset,
                0,
                x_left + indicator.offset,
                0
            )
            color_center = self.warning_color(
                abs(nearest_left), indicator.min_range_x, indicator.max_range_x)
            lin_gra.setColorAt(0, Qt.transparent)
            lin_gra.setColorAt(indicator.edge, color_center)
            lin_gra.setColorAt(1, Qt.transparent)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_left - indicator.width + indicator.offset,
                0, indicator.width, self.area_size
            )

        # Draw right side indicator
        if nearest_right < indicator.max_range_x:
            lin_gra = QLinearGradient(
                x_right - indicator.offset,
                0,
                x_right + indicator.width - indicator.offset,
                0
            )
            color_center = self.warning_color(
                abs(nearest_right), indicator.min_range_x, indicator.max_range_x)
            lin_gra.setColorAt(0, Qt.transparent)
            lin_gra.setColorAt(1 - indicator.edge, color_center)
            lin_gra.setColorAt(1, Qt.transparent)
            painter.setBrush(lin_gra)
            painter.drawRect(
                x_right - indicator.offset,
                0, indicator.width, self.area_size
            )

    def draw_vehicle(self, painter, indicator):
        """Draw vehicles"""
        if self.wcfg["vehicle_outline_width"] > 0:
            self.pen.setWidth(self.wcfg["vehicle_outline_width"])
            self.pen.setColor(self.wcfg["vehicle_outline_color"])
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        # Real size in meters
        nearest_left = -indicator.max_range_x
        nearest_right = indicator.max_range_x

        # Draw opponent vehicle within radar range
        for veh_info in self.vehicles_data:
            if veh_info.isPlayer:
                continue

            # -x = left, +x = right, -y = ahead, +y = behind
            raw_pos_x, raw_pos_y = veh_info.relativeRotatedPosXZ
            if (self.vehicle_hide_range.behind > raw_pos_y > -self.vehicle_hide_range.ahead and
                -self.vehicle_hide_range.side < raw_pos_x < self.vehicle_hide_range.side):

                # Find nearest vehicle coordinates
                if (self.wcfg["show_overlap_indicator"] and
                    abs(raw_pos_x) < indicator.max_range_x and
                    abs(raw_pos_y) < indicator.max_range_y):
                    if -indicator.min_range_x > raw_pos_x > nearest_left:
                        nearest_left = raw_pos_x
                    if indicator.min_range_x < raw_pos_x < nearest_right:
                        nearest_right = raw_pos_x

                # Rotated position relative to player
                pos_x = self.scale_veh_pos(raw_pos_x)
                pos_y = self.scale_veh_pos(raw_pos_y)
                angle_deg = round(calc.rad2deg(-veh_info.relativeOrientationXZRadians), 3)

                # Draw vehicle
                self.brush.setColor(self.color_lap_diff(veh_info))
                painter.setBrush(self.brush)
                painter.translate(pos_x, pos_y)
                painter.rotate(angle_deg)
                self.draw_vehicle_shape(painter)
                painter.resetTransform()

        # Draw player vehicle
        self.brush.setColor(self.wcfg["vehicle_color_player"])
        painter.setBrush(self.brush)
        painter.translate(self.area_center, self.area_center)
        self.draw_vehicle_shape(painter)
        painter.resetTransform()

        if self.wcfg["show_overlap_indicator"]:
            # Draw overlap indicator below vehicle shape
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
            self.draw_warning_indicator(painter, indicator, nearest_left, nearest_right)

    def draw_vehicle_shape(self, painter):
        """Draw vehicles shape"""
        painter.drawRoundedRect(
            self.veh_shape,
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
            self.indicator_color_critical.setAlphaF(alpha)  # alpha changes with nearest distance
            return self.indicator_color_critical
        self.indicator_color.setAlphaF(alpha)
        return self.indicator_color

    def color_lap_diff(self, veh_info):
        """Compare lap differences & set color"""
        if veh_info.position == 1:
            return self.wcfg["vehicle_color_leader"]
        if veh_info.inPit:
            return self.wcfg["vehicle_color_in_pit"]
        if veh_info.isYellow and not veh_info.inPit + veh_info.inGarage:
            return self.wcfg["vehicle_color_yellow"]
        if veh_info.isLapped > 0:
            return self.wcfg["vehicle_color_laps_ahead"]
        if veh_info.isLapped < 0:
            return self.wcfg["vehicle_color_laps_behind"]
        return self.wcfg["vehicle_color_same_lap"]

    def set_autohide_state(self):
        """Auto hide radar if in private qualifying or no nearby vehicles"""
        if (self.wcfg["auto_hide_in_private_qualifying"] and
            self.cfg.user.setting["module_restapi"]["enable"] and
            api.read.session.session_type() == 2 and
            minfo.restapi.privateQualifying == 1):
            self.show_radar = False
            return None

        lap_etime = api.read.timing.elapsed()
        in_garage = api.read.vehicle.in_garage()

        if self.is_nearby() or in_garage:
            if not self.show_radar:
                self.show_radar = True
            self.autohide_timer_start = lap_etime

        # Timer start should be smaller than elapsed time, reset if not
        if self.autohide_timer_start > lap_etime:
            self.autohide_timer_start = 1

        if self.autohide_timer_start:
            autohide_timer = lap_etime - self.autohide_timer_start
            if autohide_timer > self.wcfg["auto_hide_time_threshold"]:
                self.show_radar = False
                self.autohide_timer_start = 0
        return None

    def is_nearby(self):
        """Check nearby vehicles"""
        if not self.vehicles_data:
            return False
        for veh_info in self.vehicles_data:
            if not veh_info.isPlayer:
                # -x = left, +x = right, -y = ahead, +y = behind
                raw_pos_x, raw_pos_y = veh_info.relativeRotatedPosXZ
                if (self.radar_hide_range.behind > raw_pos_y > -self.radar_hide_range.ahead and
                    -self.radar_hide_range.side < raw_pos_x < self.radar_hide_range.side):
                    return True
        return False

    def calc_indicator_dimension(self, veh_width, veh_length):
        """Calculate indicator dimension

        Range between player & opponents to show indicator.
        x is left to right range.
        y is forward to backward range.
        """
        min_range_x = veh_width * 0.9  # slightly overlapped
        max_range_x = veh_width * max(self.wcfg["overlap_detection_range_multiplier"], 0.01)
        max_range_y = veh_length * 1.2  # safe range for ahead & behind opponents
        width = veh_width * max(self.wcfg["indicator_size_multiplier"], 0.01) * self.global_scale
        edge = max((width - 3) / width, 0.001)  # for antialiasing
        offset = veh_width * self.global_scale * 0.5
        return IndicatorDimension(
            min_range_x, max_range_x, max_range_y, width, edge, offset)

    def set_range_dimension(self, prefix):
        """Set range dimension for radar & autohide"""
        if self.wcfg[f"{prefix}_ahead"] < 0:
            min_ahead = self.radar_radius
        else:
            min_ahead = self.wcfg[f"{prefix}_ahead"]

        if self.wcfg[f"{prefix}_behind"] < 0:
            min_behind = self.radar_radius
        else:
            min_behind = self.wcfg[f"{prefix}_behind"]

        if self.wcfg[f"{prefix}_side"] < 0:
            min_side = self.radar_radius
        else:
            min_side = self.wcfg[f"{prefix}_side"]
        return DistanceRect(min_ahead, min_behind, min_side)


@dataclass
class IndicatorDimension:
    """Indicator dimension"""
    min_range_x: float = 0
    max_range_x: float = 0
    max_range_y: float = 0
    width: float = 0
    edge: float = 0
    offset: float = 0


@dataclass
class DistanceRect:
    """Distance rectangle"""
    ahead: float = 0
    behind: float = 0
    side: float = 0
