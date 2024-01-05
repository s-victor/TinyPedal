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
Track map Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF, QLineF
from PySide2.QtGui import QPainterPath, QPainter, QPixmap, QPen, QBrush

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "track_map"


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
        self.veh_size = self.wcfg["font_size"] + round(font_m.width * self.wcfg["bar_padding"])
        self.veh_shape = QRectF(
            self.veh_size / 2,
            self.veh_size / 2,
            self.veh_size,
            self.veh_size
        )
        self.veh_text_shape = QRectF(
            self.veh_size / 2,
            self.veh_size / 2 + font_offset,
            self.veh_size,
            self.veh_size
        )

        # Config canvas
        self.area_size = max(self.wcfg["area_size"], 100)
        self.area_margin = min(max(self.wcfg["area_margin"], 0), int(self.area_size/4))
        self.temp_map_size = self.area_size - self.area_margin * 2

        self.resize(self.area_size, self.area_size)
        self.pixmap_map = QPixmap(self.area_size, self.area_size)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)
        self.draw_map_image(self.create_map_path())

        self.pixmap_veh_player = self.draw_vehicle_pixmap("player")
        self.pixmap_veh_leader = self.draw_vehicle_pixmap("leader")
        self.pixmap_veh_in_pit = self.draw_vehicle_pixmap("in_pit")
        self.pixmap_veh_yellow = self.draw_vehicle_pixmap("yellow")
        self.pixmap_veh_laps_ahead = self.draw_vehicle_pixmap("laps_ahead")
        self.pixmap_veh_laps_behind = self.draw_vehicle_pixmap("laps_behind")
        self.pixmap_veh_same_lap = self.draw_vehicle_pixmap("same_lap")

        # Last data
        self.map_scaled = None
        self.map_range = (0,10,0,10)
        self.map_scale = 1
        self.map_offset = (0,0)

        self.vehicles_data = None
        self.last_coords_hash = -1
        self.last_veh_data_version = None
        self.circular_map = True

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Map
            coords_hash = minfo.mapping.coordinatesHash
            self.update_map(coords_hash, self.last_coords_hash)
            self.last_coords_hash = coords_hash

            # Vehicles
            veh_data_version = minfo.vehicles.dataSetVersion
            self.update_vehicle(veh_data_version, self.last_veh_data_version)
            self.last_veh_data_version = veh_data_version

    # GUI update methods
    def update_map(self, curr, last):
        """Map update"""
        if curr != last:
            self.draw_map_image(
                self.create_map_path(minfo.mapping.coordinates), self.circular_map)

    def update_vehicle(self, curr, last):
        """Vehicle sort & update"""
        if curr != last:
            self.vehicles_data = sorted(minfo.vehicles.dataSet, reverse=True)
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Draw map
        painter.drawPixmap(0, 0, self.pixmap_map)
        # Draw vehicles
        if self.vehicles_data:
            self.draw_vehicle(painter)

    def create_map_path(self, raw_coords=None):
        """Create map path"""
        map_path = QPainterPath()
        if raw_coords:
            dist = calc.distance(raw_coords[0], raw_coords[-1])
            (self.map_scaled, self.map_range, self.map_scale, self.map_offset
             ) = calc.scale_map(raw_coords, self.area_size, self.area_margin)

            for index, coords in enumerate(self.map_scaled):
                if index == 0:
                    map_path.moveTo(*coords)
                else:
                    map_path.lineTo(*coords)

            # Close map loop if start & end distance less than 500 meters
            if dist < 500:
                map_path.closeSubpath()
                self.circular_map = True
            else:
                self.circular_map = False

        # Temp map
        else:
            temp_coords = (
                (self.area_margin, self.area_margin),
                (self.temp_map_size, self.area_margin),
                (self.temp_map_size, self.temp_map_size),
                (self.area_margin, self.temp_map_size)
            )
            (_, self.map_range, self.map_scale, self.map_offset
             ) = calc.scale_map(temp_coords, self.area_size, self.area_margin)

            self.map_scaled = None

            map_path.addEllipse(
                QRectF(
                    self.area_margin,
                    self.area_margin,
                    self.temp_map_size,
                    self.temp_map_size,
                )
            )
            self.circular_map = True
        return map_path

    def draw_map_image(self, map_path, circular_map=True):
        """Draw map image separately"""
        if self.wcfg["show_background"]:
            self.pixmap_map.fill(self.wcfg["bkg_color"])
        else:
            self.pixmap_map.fill(Qt.transparent)
        painter = QPainter(self.pixmap_map)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Draw map inner background
        if self.wcfg["show_map_background"] and circular_map:
            brush = QBrush(Qt.SolidPattern)
            brush.setColor(self.wcfg["bkg_color_map"])
            painter.setBrush(brush)
            painter.drawPath(map_path)
            painter.setBrush(Qt.NoBrush)

        # Set pen style
        pen = QPen()
        pen.setJoinStyle(Qt.RoundJoin)

        # Draw map outline
        if self.wcfg["map_outline_width"] > 0:
            pen.setWidth(self.wcfg["map_width"] + self.wcfg["map_outline_width"])
            pen.setColor(self.wcfg["map_outline_color"])
            painter.setPen(pen)
            painter.drawPath(map_path)

        # Draw map
        pen.setWidth(self.wcfg["map_width"])
        pen.setColor(self.wcfg["map_color"])
        painter.setPen(pen)
        painter.drawPath(map_path)

        # Draw sector
        if self.map_scaled:
            # SF line
            if self.wcfg["show_start_line"]:
                pen.setWidth(self.wcfg["start_line_width"])
                pen.setColor(self.wcfg["start_line_color"])
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
                pen.setColor(self.wcfg["sector_line_color"])
                painter.setPen(pen)

                for idx in range(2):
                    pos_x1, pos_y1, pos_x2, pos_y2 = calc.line_intersect_coords(
                        self.map_scaled[sectors_index[idx]],  # point a
                        self.map_scaled[sectors_index[idx] + 1],  # point b
                        1.57079633,  # 90 degree rotation
                        self.wcfg["sector_line_length"]
                    )
                    painter.drawLine(QLineF(pos_x1, pos_y1, pos_x2, pos_y2))
        else:
            # SF line
            if self.wcfg["show_start_line"]:
                pen.setWidth(self.wcfg["start_line_width"])
                pen.setColor(self.wcfg["start_line_color"])
                painter.setPen(pen)
                painter.drawLine(
                    QLineF(
                        self.area_margin - self.wcfg["start_line_length"],
                        self.area_size / 2,
                        self.area_margin + self.wcfg["start_line_length"],
                        self.area_size / 2
                    )
                )

    def draw_vehicle(self, painter):
        """Draw vehicles"""
        if self.wcfg["show_vehicle_standings"]:
            painter.setFont(self.font)
            self.pen.setColor(self.wcfg["font_color"])
            painter.setPen(self.pen)

        for veh_info in self.vehicles_data:
            if self.last_coords_hash:
                pos_x, pos_y = self.vehicle_coords_scale(*veh_info.posXZ)
                offset = -self.veh_size
            else:  # vehicles on temp map
                inpit_offset = self.wcfg["font_size"] if veh_info.inPit else 0

                pos_x, pos_y = calc.rotate_pos(
                    6.2831853 * veh_info.percentageDistance,
                    self.temp_map_size / -2 + inpit_offset,  # x pos
                    0  # y pos
                )
                offset = self.area_size / 2 - self.veh_size

            painter.translate(offset + pos_x, offset + pos_y)
            painter.drawPixmap(0, 0, self.color_veh_pixmap(veh_info))

            # Draw text standings
            if self.wcfg["show_vehicle_standings"]:
                painter.drawText(
                    self.veh_text_shape,
                    Qt.AlignCenter,
                    f"{veh_info.position}"
                )
            painter.resetTransform()

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
        painter.drawEllipse(self.veh_shape)
        return pixmap_veh

    # Additional methods
    @staticmethod
    def coords_scale(coords, min_range, scale, offset):
        """Coordinates scale & offset"""
        return (coords - min_range) * scale + offset

    def vehicle_coords_scale(self, raw_pos_x, raw_pos_y):
        """Vehicle coordinates scale, round to prevent bouncing"""
        veh_pos_x = round(
            self.coords_scale(
                raw_pos_x,
                self.map_range[0],  # min range x
                self.map_scale,
                self.map_offset[0]  # offset x
            )
        )
        veh_pos_y = round(
            self.coords_scale(
                raw_pos_y,
                self.map_range[2],  # min range y
                self.map_scale,
                self.map_offset[1]  # offset y
            )
        )
        return veh_pos_x, veh_pos_y

    def color_veh_pixmap(self, veh_info):
        """Compare lap differences & set color"""
        if veh_info.isPlayer:
            return self.pixmap_veh_player
        if veh_info.position == 1:
            return self.pixmap_veh_leader
        if veh_info.inPit:
            return self.pixmap_veh_in_pit
        if veh_info.isYellow and not veh_info.inPit + veh_info.inGarage:
            return self.pixmap_veh_yellow
        if veh_info.isLapped > 0:
            return self.pixmap_veh_laps_ahead
        if veh_info.isLapped < 0:
            return self.pixmap_veh_laps_behind
        return self.pixmap_veh_same_lap
