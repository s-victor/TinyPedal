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
Navigation Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF, QLineF, QPointF
from PySide2.QtGui import QPainterPath, QPainter, QPixmap, QRadialGradient, QPen, QBrush, QColor

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "navigation"


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
        self.global_scale = self.area_size / max(self.wcfg["view_radius"], 5)
        self.area_center = self.area_size / 2
        self.view_range = self.wcfg["view_radius"] * 2.5

        self.veh_offset_y = self.area_size * max(self.wcfg["vehicle_offset"], 0)
        self.veh_size = max(self.wcfg["vehicle_size"] / 2, 1)
        if self.wcfg["show_circle_vehicle_shape"]:
            self.veh_shape = QRectF(
                -self.veh_size,
                -self.veh_size,
                self.veh_size * 2,
                self.veh_size * 2
            )
        else:
            self.veh_shape = (
                QPointF(0,-self.veh_size),
                QPointF(self.veh_size,self.veh_size),
                QPointF(0,self.veh_size * 0.6),
                QPointF(-self.veh_size,self.veh_size),
            )

        # Config canvas
        self.resize(self.area_size, self.area_size)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_background()
        self.draw_map_mask()
        self.draw_map_image(self.create_map_path(None))

        # Last data
        self.vehicles_data = None
        self.last_veh_data_hash = None

        self.last_coords_hash = -1
        self.map_scaled = None
        self.map_margin = self.wcfg["map_width"] + self.wcfg["map_outline_width"]
        self.map_rect = 0,0,1,1
        self.map_offset = 0,0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Vehicles
            veh_data_hash = minfo.vehicles.dataSetHash
            self.update_vehicle(veh_data_hash, self.last_veh_data_hash)
            self.last_veh_data_hash = veh_data_hash

            # Map
            coords_hash = minfo.mapping.coordinatesHash
            self.update_map(coords_hash, self.last_coords_hash)
            self.last_coords_hash = coords_hash

    # GUI update methods
    def update_vehicle(self, curr, last):
        """Vehicle update"""
        if curr != last:
            self.vehicles_data = minfo.vehicles.dataSet
            self.update()

    def update_map(self, curr, last):
        """Map update"""
        if curr != last:
            self.draw_map_image(
                self.create_map_path(minfo.mapping.coordinates))

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw map
        self.rotate_map(painter)

        # Draw vehicles
        if self.vehicles_data:
            self.draw_vehicle(painter)

        # Apply mask
        if self.wcfg["show_fade_out"]:
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
            painter.drawPixmap(0, 0, self.area_size, self.area_size, self.map_mask)
            #painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Draw background
        if self.wcfg["show_background"] or self.wcfg["show_circle_background"]:
            # Insert below map & mask
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
            painter.drawPixmap(0, 0, self.area_size, self.area_size, self.rect_background)
            #painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

    def draw_background(self):
        """Draw background"""
        self.rect_background = QPixmap(self.area_size, self.area_size)
        if self.wcfg["show_background"]:
            self.rect_background.fill(QColor(self.wcfg["bkg_color"]))
        else:
            self.rect_background.fill(Qt.transparent)

        # Draw circle background
        if self.wcfg["show_circle_background"]:
            painter = QPainter(self.rect_background)
            painter.setRenderHint(QPainter.Antialiasing, True)

            if self.wcfg["circle_outline_width"] > 0:
                pen = QPen()
                pen.setWidth(self.wcfg["circle_outline_width"])
                pen.setColor(QColor(self.wcfg["circle_outline_color"]))
                painter.setPen(pen)
            else:
                painter.setPen(Qt.NoPen)

            self.brush.setColor(QColor(self.wcfg["bkg_color_circle"]))
            painter.setBrush(self.brush)
            painter.drawEllipse(
                self.wcfg["circle_outline_width"],
                self.wcfg["circle_outline_width"],
                (self.area_center - self.wcfg["circle_outline_width"]) * 2,
                (self.area_center - self.wcfg["circle_outline_width"]) * 2
            )

    def transform_map_coords(self):
        """Transform map coordinates"""
        # player vehicle orientation yaw radians + 180 deg rotation correction
        plr_ori_rad = api.read.vehicle.orientation_yaw_radians() + 3.14159265
        # x, y position & offset relative to player
        rot_pos_x, rot_pos_y = calc.rotate_pos(
            plr_ori_rad,   # plr_ori_rad, rotate view
            api.read.vehicle.pos_longitudinal() * self.global_scale - self.map_offset[0],
            api.read.vehicle.pos_lateral() * self.global_scale - self.map_offset[1]
        )
        plr_ori_deg = calc.rad2deg(plr_ori_rad)
        center_offset_x = self.area_center - rot_pos_x
        center_offset_y = self.veh_offset_y - rot_pos_y
        return plr_ori_deg, center_offset_x, center_offset_y

    def rotate_map(self, painter):
        """Rotate map"""
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        plr_ori_deg, center_offset_x, center_offset_y = self.transform_map_coords()
        painter.resetTransform()
        painter.translate(center_offset_x, center_offset_y)
        painter.rotate(plr_ori_deg)
        painter.drawPixmap(*self.map_rect, self.map_image)
        painter.resetTransform()

    def create_map_path(self, raw_coords):
        """Create map path"""
        map_path = QPainterPath()
        if raw_coords:
            dist = calc.distance(raw_coords[0], raw_coords[-1])
            (self.map_scaled, self.map_rect, self.map_offset
             ) = calc.zoom_map(raw_coords, self.global_scale, self.map_margin)
            for index, coords in enumerate(self.map_scaled):
                if index == 0:
                    map_path.moveTo(*coords)
                else:
                    map_path.lineTo(*coords)
            # Close map loop if start & end distance less than 500 meters
            if dist < 500:
                map_path.closeSubpath()
        else:
            self.map_scaled = None
            self.map_rect = 0,0,1,1
            self.map_offset = 0,0
            map_path.addRect(QRectF(-99999,-99999,0,0))
        return map_path

    def draw_map_image(self, map_path):
        """Draw map image separately"""
        self.map_image = QPixmap(self.map_rect[2], self.map_rect[3])
        self.map_image.fill(Qt.transparent)
        painter = QPainter(self.map_image)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Set pen style
        pen = QPen()
        pen.setJoinStyle(Qt.RoundJoin)

        # Draw map outline
        if self.wcfg["map_outline_width"]:
            pen.setWidth(self.wcfg["map_width"] + self.wcfg["map_outline_width"])
            pen.setColor(QColor(self.wcfg["map_outline_color"]))
            painter.setPen(pen)
            painter.drawPath(map_path)

        # Draw map
        pen.setWidth(self.wcfg["map_width"])
        pen.setColor(QColor(self.wcfg["map_color"]))
        painter.setPen(pen)
        painter.drawPath(map_path)

        # Draw sector
        if self.map_scaled:
            # SF line
            if self.wcfg["show_start_line"]:
                pen.setWidth(self.wcfg["start_line_width"])
                pen.setColor(QColor(self.wcfg["start_line_color"]))
                painter.setPen(pen)
                pos_x1, pos_y1, pos_x2, pos_y2 = calc.line_intersect_coords(
                    self.map_scaled[0],  # point a
                    self.map_scaled[1],  # point b
                    1.57079633,  # 90 degree rotation
                    self.wcfg["start_line_length"]
                )
                painter.drawLine(QLineF(pos_x1, pos_y1, pos_x2, pos_y2))

            # Sector lines
            sectors_index = minfo.mapping.sectors
            if self.wcfg["show_sector_line"] and sectors_index and all(sectors_index):
                pen.setWidth(self.wcfg["sector_line_width"])
                pen.setColor(QColor(self.wcfg["sector_line_color"]))
                painter.setPen(pen)

                for idx in range(2):
                    pos_x1, pos_y1, pos_x2, pos_y2 = calc.line_intersect_coords(
                        self.map_scaled[sectors_index[idx]],  # point a
                        self.map_scaled[sectors_index[idx] + 1],  # point b
                        1.57079633,  # 90 degree rotation
                        self.wcfg["sector_line_length"]
                    )
                    painter.drawLine(QLineF(pos_x1, pos_y1, pos_x2, pos_y2))

    def draw_map_mask(self):
        """Map mask"""
        self.map_mask = QPixmap(self.area_size, self.area_size)
        painter = QPainter(self.map_mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw map mask
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

    def draw_vehicle(self, painter):
        """Draw vehicles"""
        if self.wcfg["show_vehicle_standings"]:
            painter.setFont(self.font)

        if self.wcfg["vehicle_outline_width"]:
            self.pen.setWidth(self.wcfg["vehicle_outline_width"])
            self.pen.setColor(QColor(self.wcfg["vehicle_outline_color"]))
            painter.setPen(self.pen)
        else:
            painter.setPen(Qt.NoPen)

        # Draw vehicle within view range
        painter.resetTransform()
        for veh_info in sorted(self.vehicles_data, key=self.sort_vehicles):
            # Draw player vehicle
            if veh_info.isPlayer:
                self.brush.setColor(QColor(self.wcfg["vehicle_color_player"]))
                painter.setBrush(self.brush)
                painter.translate(self.area_center, self.veh_offset_y)
                self.draw_vehicle_shape(painter)
                painter.resetTransform()
                if self.wcfg["show_vehicle_standings"]:
                    self.draw_text_standings(
                        painter, self.area_center, self.veh_offset_y, veh_info.position)

            # Draw opponent vehicle
            elif veh_info.relativeStraightDistance < self.view_range:
                # Rotated position relative to player
                pos_x, pos_y = (
                    self.scale_veh_pos(veh_info.relativeRotatedPosXZ[0], self.area_center),
                    self.scale_veh_pos(veh_info.relativeRotatedPosXZ[1], self.veh_offset_y)
                )
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
                if self.wcfg["show_vehicle_standings"]:
                    self.draw_text_standings(
                        painter, pos_x, pos_y, veh_info.position)

    def draw_vehicle_shape(self, painter):
        """Draw vehicles shape"""
        if self.wcfg["show_circle_vehicle_shape"]:
            painter.drawEllipse(self.veh_shape)
        else:
            painter.drawPolygon(self.veh_shape)

    def draw_text_standings(self, painter, pos_x, pos_y, veh_pos):
        """Draw vehicles standings text"""
        rect_vehicle = QRectF(
            pos_x - self.veh_size,
            pos_y - self.veh_size,
            self.veh_size * 2,
            self.veh_size * 2
        )
        self.pen.setColor(QColor(self.wcfg["font_color"]))
        painter.setPen(self.pen)
        painter.drawText(
            rect_vehicle.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{veh_pos}"
        )

    # Additional methods
    def scale_veh_pos(self, position, offset):
        """Scale vehicle position coordinate to global scale"""
        return position * self.global_scale + offset

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

    @staticmethod
    def sort_vehicles(veh_info):
        """Sort vehicle standings for drawing order"""
        return (
            veh_info.isPlayer,
            -veh_info.inGarage,  # reversed
            -veh_info.inPit,     # reversed
            -veh_info.position,  # reversed
        )
