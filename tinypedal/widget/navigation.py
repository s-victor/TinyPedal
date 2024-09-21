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
Navigation Widget
"""

from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtGui import QPainterPath, QPainter, QPixmap, QRadialGradient, QPen, QBrush, QPolygonF

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "navigation"
POLYGON_NONE = QPolygonF((QPointF(-99999,-99999),QPointF(-99999,-99999)))


class Realtime(Overlay):
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
        self.area_size = max(int(self.wcfg["display_size"]), 20)
        self.global_scale = self.area_size / max(self.wcfg["view_radius"], 5)
        self.area_center = self.area_size * 0.5
        self.view_range = self.wcfg["view_radius"] * 2.5

        self.veh_offset_y = self.area_size * max(self.wcfg["vehicle_offset"], 0)
        self.veh_size = max(int(self.wcfg["vehicle_size"]), 1)
        if self.wcfg["show_circle_vehicle_shape"]:
            self.veh_shape = QRectF(
                self.veh_size * 0.5,
                self.veh_size * 0.5,
                self.veh_size,
                self.veh_size
            )
        else:
            self.veh_shape = (
                QPointF(self.veh_size, self.veh_size * 0.5),
                QPointF(self.veh_size * 1.5, self.veh_size * 1.5),
                QPointF(self.veh_size, self.veh_size * 1.3),
                QPointF(self.veh_size * 0.5, self.veh_size * 1.5),
            )
        self.veh_text_shape = QRectF(
            -self.veh_size * 0.5,
            -self.veh_size * 0.5 + font_offset,
            self.veh_size,
            self.veh_size
        )

        self.map_path = None
        self.sector_path_sfline = None
        self.sector_path_sector1 = None
        self.sector_path_sector2 = None
        self.create_map_path()

        # Config canvas
        self.resize(self.area_size, self.area_size)
        self.pixmap_background = QPixmap(self.area_size, self.area_size)
        self.pixmap_mask = QPixmap(self.area_size, self.area_size)

        self.pen = QPen()
        self.pen.setJoinStyle(Qt.RoundJoin)

        self.pixmap_veh_player = self.draw_vehicle_pixmap("player")
        self.pixmap_veh_leader = self.draw_vehicle_pixmap("leader")
        self.pixmap_veh_in_pit = self.draw_vehicle_pixmap("in_pit")
        self.pixmap_veh_yellow = self.draw_vehicle_pixmap("yellow")
        self.pixmap_veh_laps_ahead = self.draw_vehicle_pixmap("laps_ahead")
        self.pixmap_veh_laps_behind = self.draw_vehicle_pixmap("laps_behind")
        self.pixmap_veh_same_lap = self.draw_vehicle_pixmap("same_lap")

        # Last data
        self.last_veh_data_version = None

        self.last_coords_hash = -1
        self.map_scaled = None
        self.map_margin = self.wcfg["map_width"] + self.wcfg["map_outline_width"]
        self.map_size = 1,1
        self.map_offset = 0,0

        self.draw_background()
        self.draw_map_mask_pixmap()
        self.update_map(0, 1)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Vehicles
            veh_data_version = minfo.vehicles.dataSetVersion
            self.update_vehicle(veh_data_version, self.last_veh_data_version)
            self.last_veh_data_version = veh_data_version

            # Map
            coords_hash = minfo.mapping.coordinatesHash
            self.update_map(coords_hash, self.last_coords_hash)
            self.last_coords_hash = coords_hash

    # GUI update methods
    def update_vehicle(self, curr, last):
        """Vehicle sort & update"""
        if curr != last:
            self.update()

    def update_map(self, curr, last):
        """Map update"""
        if curr != last:
            self.create_map_path(minfo.mapping.coordinates)

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Draw map
        self.draw_map_image(painter)
        # Draw vehicles
        self.draw_vehicle(painter, minfo.vehicles.dataSet, minfo.vehicles.drawOrder)
        # Apply mask
        if self.wcfg["show_fade_out"]:
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
            painter.drawPixmap(0, 0, self.pixmap_mask)
        # Draw background below map & mask
        if self.wcfg["show_background"] or self.wcfg["show_circle_background"]:
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
            painter.drawPixmap(0, 0, self.pixmap_background)

    def draw_background(self):
        """Draw background"""
        if self.wcfg["show_background"]:
            self.pixmap_background.fill(self.wcfg["bkg_color"])
        else:
            self.pixmap_background.fill(Qt.transparent)

        # Draw circle background
        if self.wcfg["show_circle_background"]:
            painter = QPainter(self.pixmap_background)
            painter.setRenderHint(QPainter.Antialiasing, True)

            if self.wcfg["circle_outline_width"] > 0:
                pen = QPen()
                pen.setWidth(self.wcfg["circle_outline_width"])
                pen.setColor(self.wcfg["circle_outline_color"])
                painter.setPen(pen)
            else:
                painter.setPen(Qt.NoPen)

            brush = QBrush(Qt.SolidPattern)
            brush.setColor(self.wcfg["bkg_color_circle"])
            painter.setBrush(brush)
            painter.drawEllipse(
                self.wcfg["circle_outline_width"],
                self.wcfg["circle_outline_width"],
                (self.area_center - self.wcfg["circle_outline_width"]) * 2,
                (self.area_center - self.wcfg["circle_outline_width"]) * 2
            )

    def create_map_path(self, raw_coords=None):
        """Create map path"""
        map_path = QPainterPath()
        sector_path_sfline = QPainterPath()
        sector_path_sector1 = QPainterPath()
        sector_path_sector2 = QPainterPath()

        if raw_coords:
            dist = calc.distance(raw_coords[0], raw_coords[-1])
            (self.map_scaled, self.map_size, self.map_offset
             ) = calc.zoom_map(raw_coords, self.global_scale, self.map_margin)
            for index, coords in enumerate(self.map_scaled):
                if index == 0:
                    map_path.moveTo(*coords)
                else:
                    map_path.lineTo(*coords)
            # Close map loop if start & end distance less than 500 meters
            if dist < 500:
                map_path.closeSubpath()
            # Create start/finish path
            sector_path_sfline = self.create_sector_line(
                sector_path_sfline, self.wcfg["start_line_length"], 0, 1)
            # Create sectors paths
            sectors_index = minfo.mapping.sectors
            if sectors_index and all(sectors_index):
                sector_path_sector1 = self.create_sector_line(
                    sector_path_sector1, self.wcfg["sector_line_length"],
                    sectors_index[0], sectors_index[0] + 1)
                sector_path_sector2 = self.create_sector_line(
                    sector_path_sector2, self.wcfg["sector_line_length"],
                    sectors_index[1], sectors_index[1] + 1)
            else:
                sector_path_sector1.addPolygon(POLYGON_NONE)
                sector_path_sector2.addPolygon(POLYGON_NONE)
        else:
            self.map_scaled = None
            self.map_size = 1,1
            self.map_offset = 0,0
            map_path.addPolygon(POLYGON_NONE)
            sector_path_sfline.addPolygon(POLYGON_NONE)
            sector_path_sector1.addPolygon(POLYGON_NONE)
            sector_path_sector2.addPolygon(POLYGON_NONE)

        self.map_path = map_path
        self.sector_path_sfline = sector_path_sfline
        self.sector_path_sector1 = sector_path_sector1
        self.sector_path_sector2 = sector_path_sector2

    def draw_map_image(self, painter):
        """Draw map image"""
        # Transform map coordinates
        # Player vehicle orientation yaw radians + 180 deg rotation correction
        plr_ori_rad = api.read.vehicle.orientation_yaw_radians() + 3.14159265
        # x, y position & offset relative to player
        rot_pos_x, rot_pos_y = calc.rotate_coordinate(
            plr_ori_rad,   # plr_ori_rad, rotate view
            api.read.vehicle.position_longitudinal() * self.global_scale - self.map_offset[0],
            api.read.vehicle.position_lateral() * self.global_scale - self.map_offset[1]
        )
        plr_ori_deg = calc.rad2deg(plr_ori_rad)
        center_offset_x = self.area_center - rot_pos_x
        center_offset_y = self.veh_offset_y - rot_pos_y

        # Apply transform rotation
        painter.resetTransform()
        painter.translate(center_offset_x, center_offset_y)
        painter.rotate(plr_ori_deg)

        # Draw map outline
        if self.wcfg["map_outline_width"] > 0:
            self.pen.setWidth(self.map_margin)
            self.pen.setColor(self.wcfg["map_outline_color"])
            painter.setPen(self.pen)
            painter.drawPath(self.map_path)

        # Draw map
        self.pen.setWidth(self.wcfg["map_width"])
        self.pen.setColor(self.wcfg["map_color"])
        painter.setPen(self.pen)
        painter.drawPath(self.map_path)

        # Draw start/finish line
        if self.wcfg["show_start_line"]:
            self.pen.setWidth(self.wcfg["start_line_width"])
            self.pen.setColor(self.wcfg["start_line_color"])
            painter.setPen(self.pen)
            painter.drawPath(self.sector_path_sfline)

        # Draw sectors line
        if self.wcfg["show_sector_line"]:
            self.pen.setWidth(self.wcfg["sector_line_width"])
            self.pen.setColor(self.wcfg["sector_line_color"])
            painter.setPen(self.pen)
            painter.drawPath(self.sector_path_sector1)
            painter.drawPath(self.sector_path_sector2)

        painter.resetTransform()

    def draw_vehicle(self, painter, veh_info, veh_draw_order):
        """Draw vehicles"""
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        if self.wcfg["show_vehicle_standings"]:
            painter.setFont(self.font)
            self.pen.setColor(self.wcfg["font_color"])
            painter.setPen(self.pen)

        # Draw vehicle within view range
        for index in veh_draw_order:
            # Draw player vehicle
            if veh_info[index].isPlayer:
                painter.translate(self.area_center, self.veh_offset_y)
                painter.drawPixmap(-self.veh_size, -self.veh_size, self.pixmap_veh_player)

                if self.wcfg["show_vehicle_standings"]:
                    painter.drawText(
                        self.veh_text_shape, Qt.AlignCenter,
                        f"{veh_info[index].positionOverall}")
                painter.resetTransform()

            # Draw opponent vehicle in view range
            elif veh_info[index].relativeStraightDistance < self.view_range:
                # Rotated position relative to player
                pos_x, pos_y = (  # position = raw position * global scale + offset
                    veh_info[index].relativeRotatedPosXY[0] * self.global_scale + self.area_center,
                    veh_info[index].relativeRotatedPosXY[1] * self.global_scale + self.veh_offset_y
                )
                painter.translate(pos_x, pos_y)

                if not self.wcfg["show_circle_vehicle_shape"]:
                    painter.rotate(
                        calc.rad2deg(-veh_info[index].relativeOrientationXYRadians))
                painter.drawPixmap(
                    -self.veh_size, -self.veh_size,
                    self.color_veh_pixmap(veh_info[index]))

                if self.wcfg["show_vehicle_standings"]:
                    painter.resetTransform()
                    painter.translate(pos_x, pos_y)
                    painter.drawText(
                        self.veh_text_shape, Qt.AlignCenter,
                        f"{veh_info[index].positionOverall}")
                painter.resetTransform()

    def draw_map_mask_pixmap(self):
        """Map mask pixmap"""
        self.pixmap_mask.fill(Qt.black)
        painter = QPainter(self.pixmap_mask)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw map mask
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

    def draw_vehicle_pixmap(self, suffix):
        """Draw vehicles pixmap"""
        pixmap_veh = QPixmap(self.veh_size * 2, self.veh_size * 2)
        pixmap_veh.fill(Qt.transparent)
        painter = QPainter(pixmap_veh)
        painter.setRenderHint(QPainter.Antialiasing, True)
        if self.wcfg["vehicle_outline_width"] > 0:
            pen = QPen()
            pen.setWidth(self.wcfg["vehicle_outline_width"])
            pen.setColor(self.wcfg["vehicle_outline_color"])
            painter.setPen(pen)
        else:
            painter.setPen(Qt.NoPen)
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(self.wcfg[f"vehicle_color_{suffix}"])
        painter.setBrush(brush)
        if self.wcfg["show_circle_vehicle_shape"]:
            painter.drawEllipse(self.veh_shape)
        else:
            painter.drawPolygon(self.veh_shape)
        return pixmap_veh

    # Additional methods
    def color_veh_pixmap(self, veh_info):
        """Compare lap differences & set color"""
        if veh_info.positionOverall == 1:
            return self.pixmap_veh_leader
        if veh_info.inPit:
            return self.pixmap_veh_in_pit
        if veh_info.isYellow and not veh_info.inPit:
            return self.pixmap_veh_yellow
        if veh_info.isLapped > 0:
            return self.pixmap_veh_laps_ahead
        if veh_info.isLapped < 0:
            return self.pixmap_veh_laps_behind
        return self.pixmap_veh_same_lap

    def create_sector_line(self, sector_path, length, node_idx1, node_idx2):
        """Create sector line"""
        pos_x1, pos_y1, pos_x2, pos_y2 = calc.line_intersect_coords(
            self.map_scaled[node_idx1],  # point a
            self.map_scaled[node_idx2],  # point b
            1.57079633,  # 90 degree rotation
            length
        )
        sector_path.moveTo(pos_x1, pos_y1)
        sector_path.lineTo(pos_x2, pos_y2)
        return sector_path
