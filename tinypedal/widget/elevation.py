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
Elevation Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainterPath, QPainter, QPixmap, QPen, QBrush

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "elevation"


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
        self.display_width = max(self.wcfg["display_width"], 20)
        self.display_height = max(self.wcfg["display_height"], 10)
        self.display_margin_top = min(max(self.wcfg["display_margin_top"], 0), int(self.display_height / 2))
        self.display_margin_bottom = min(max(self.wcfg["display_margin_bottom"], 0), int(self.display_height / 2))
        self.display_detail_level = max(self.wcfg["display_detail_level"], 0)

        text_width = font_m.width * 10
        self.rect_text_elevation = QRectF(
            self.display_width * self.wcfg["elevation_reading_offset_x"] - text_width * 0.5,
            self.display_height * self.wcfg["elevation_reading_offset_y"] - font_m.height * 0.5 + font_offset,
            text_width,
            font_m.height
        )
        self.rect_text_scale = QRectF(
            self.display_width * self.wcfg["elevation_scale_offset_x"] - text_width * 0.5,
            self.display_height * self.wcfg["elevation_scale_offset_y"] - font_m.height * 0.5 + font_offset,
            text_width,
            font_m.height
        )
        self.elevation_text_alignment = self.set_text_alignment(self.wcfg["elevation_reading_text_alignment"])
        self.scale_text_alignment = self.set_text_alignment(self.wcfg["elevation_scale_text_alignment"])

        # Config canvas
        self.resize(self.display_width, self.display_height)
        self.pixmap_background = QPixmap(self.display_width, self.display_height)
        self.pixmap_progress = QPixmap(self.display_width, self.display_height)
        self.pixmap_progress_line = QPixmap(self.display_width, self.display_height)
        self.pixmap_marks = QPixmap(self.display_width, self.display_height)

        self.pen = QPen()

        # Last data
        self.map_scaled = None
        self.map_range = (0,10,0,10)
        self.map_scale = 1,1

        self.last_elevation_hash = -1
        self.veh_pos = (0,0,0)
        self.last_veh_pos = None

        # Set widget state & start update
        self.update_elevation(0, 1)
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:

            # Elevation map
            elevation_hash = minfo.mapping.elevationsHash
            self.update_elevation(elevation_hash, self.last_elevation_hash)
            self.last_elevation_hash = elevation_hash

            # Vehicle position
            self.veh_pos = (
                api.read.lap.distance(),
                api.read.vehicle.position_vertical(),
                self.display_width * api.read.lap.progress()
            )
            self.update_vehicle(self.veh_pos, self.last_veh_pos)
            self.last_veh_pos = self.veh_pos

    # GUI update methods
    def update_elevation(self, curr, last):
        """Elevation map update"""
        if curr != last:
            map_path = self.create_elevation_path(minfo.mapping.elevations)
            self.draw_background(map_path)
            self.draw_progress(map_path)
            self.draw_progress_line(map_path)
            self.draw_marks(map_path)

    def update_vehicle(self, curr, last):
        """Vehicle position update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPixmap(0, 0, self.pixmap_background)

        # Draw elevation progress
        if self.wcfg["show_elevation_progress"]:
            painter.drawPixmap(0, 0, self.pixmap_progress, 0, 0, self.veh_pos[2], 0)

        # Draw marks
        painter.drawPixmap(0, 0, self.pixmap_marks)

        if self.wcfg["show_elevation_progress_line"]:
            painter.drawPixmap(0, 0, self.pixmap_progress_line, 0, 0, self.veh_pos[2], 0)

        if self.wcfg["show_position_mark"]:
            self.draw_position_mark(painter)

        # Draw readings
        if self.wcfg["show_elevation_reading"] or self.wcfg["show_elevation_scale"]:
            self.draw_readings(painter)

    def create_elevation_path(self, raw_coords=None):
        """Create elevation path"""
        map_path = QPainterPath()
        if raw_coords:
            self.map_scaled, self.map_range, self.map_scale = calc.scale_elevation(
                raw_coords,
                self.display_width,
                self.display_height - self.display_margin_top - self.display_margin_bottom)

            # Correct start & finish nodes position
            sf_y_average = (self.map_scaled[0][1] + self.map_scaled[-1][1]) * 0.5
            self.map_scaled[0] = 0, sf_y_average
            self.map_scaled[-1] = self.display_width, sf_y_average

            # Set boundary start node
            map_path.moveTo(-999, self.map_scaled[-2][1])  # 2nd last node y pos

            # Set middle nodes
            total_nodes = len(self.map_scaled)
            skip_node = total_nodes // self.display_width * self.display_detail_level
            skipped_last_node = (total_nodes - 1) % skip_node if skip_node else 0
            last_dist = 0
            last_skip = 0
            for coords in self.map_scaled:
                if coords[0] > last_dist and last_skip >= skip_node:
                    map_path.lineTo(*coords)
                    last_skip = 0
                last_dist = coords[0]
                last_skip += 1

            if skipped_last_node:  # set last node if skipped
                map_path.lineTo(*self.map_scaled[-1])

            # Set boundary end node
            map_path.lineTo(self.display_width + 999, self.map_scaled[1][1])  # 2nd node y pos
            map_path.lineTo(self.display_width + 999, -999)
            map_path.lineTo(-999, -999)
            map_path.closeSubpath()

        # Temp map
        else:
            self.map_scaled = None
            map_path.moveTo(-999, self.display_height * 0.5)
            map_path.lineTo(self.display_width + 999, self.display_height * 0.5)
            map_path.lineTo(self.display_width + 999, -999)
            map_path.lineTo(-999, -999)
            map_path.closeSubpath()

        return map_path

    def draw_background(self, map_path):
        """Draw background image"""
        if self.wcfg["show_background"]:
            self.pixmap_background.fill(self.wcfg["bkg_color"])
        else:
            self.pixmap_background.fill(Qt.transparent)
        painter = QPainter(self.pixmap_background)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Set vertical flip to correct elevation direction
        painter.setViewport(0, self.display_height, self.display_width, -self.display_height)

        # Add margin offset
        if self.map_scaled:
            painter.translate(0, self.display_margin_bottom)

        # Draw elevation background
        if self.wcfg["show_elevation_background"]:
            brush = QBrush(Qt.SolidPattern)
            brush.setColor(self.wcfg["bkg_color_elevation"])
            painter.setBrush(brush)
            painter.drawPath(map_path)

    def draw_progress(self, map_path):
        """Draw progress image"""
        self.pixmap_progress.fill(Qt.transparent)
        painter = QPainter(self.pixmap_progress)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Set vertical flip to correct elevation direction
        painter.setViewport(0, self.display_height, self.display_width, -self.display_height)

        # Add margin offset
        if self.map_scaled:
            painter.translate(0, self.display_margin_bottom)

        # Draw elevation progress
        brush = QBrush(Qt.SolidPattern)
        brush.setColor(self.wcfg["elevation_progress_color"])
        painter.setBrush(brush)
        painter.drawPath(map_path)

    def draw_progress_line(self, map_path):
        """Draw progress line image"""
        self.pixmap_progress_line.fill(Qt.transparent)
        painter = QPainter(self.pixmap_progress_line)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Set vertical flip to correct elevation direction
        painter.setViewport(0, self.display_height, self.display_width, -self.display_height)

        # Add margin offset
        if self.map_scaled:
            painter.translate(0, self.display_margin_bottom)

        # Draw elevation progress line
        pen = QPen()
        pen.setJoinStyle(Qt.RoundJoin)
        pen.setWidth(self.wcfg["elevation_progress_line_width"])
        pen.setColor(self.wcfg["elevation_progress_line_color"])
        painter.setPen(pen)
        painter.drawPath(map_path)

    def draw_marks(self, map_path):
        """Draw marks image"""
        self.pixmap_marks.fill(Qt.transparent)
        painter = QPainter(self.pixmap_marks)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Set vertical flip to correct elevation direction
        painter.setViewport(0, self.display_height, self.display_width, -self.display_height)

        # Add margin offset
        if self.map_scaled:
            painter.translate(0, self.display_margin_bottom)

        # Set pen style
        pen = QPen()
        pen.setJoinStyle(Qt.RoundJoin)

        # Draw elevation line
        if self.wcfg["show_elevation_line"]:
            pen.setWidth(self.wcfg["elevation_line_width"])
            pen.setColor(self.wcfg["elevation_line_color"])
            painter.setPen(pen)
            painter.drawPath(map_path)

        # Draw start line
        if self.wcfg["show_start_line"]:
            pen.setWidth(self.wcfg["start_line_width"])
            pen.setColor(self.wcfg["start_line_color"])
            painter.setPen(pen)
            painter.drawLine(0, -999, 0, 999)
            painter.drawLine(self.display_width, -999, self.display_width, 999)

        # Draw sector line
        sectors_index = minfo.mapping.sectors
        if self.wcfg["show_sector_line"] and self.map_scaled and sectors_index and all(sectors_index):
            pen.setWidth(self.wcfg["sector_line_width"])
            pen.setColor(self.wcfg["sector_line_color"])
            painter.setPen(pen)
            for idx in range(2):
                x = self.map_scaled[sectors_index[idx]][0]
                painter.drawLine(x, -999, x, 999)

        # Draw zero elevation line
        if self.wcfg["show_zero_elevation_line"] and self.map_scaled:
            pen.setWidth(self.wcfg["zero_elevation_line_width"])
            pen.setColor(self.wcfg["zero_elevation_line_color"])
            painter.setPen(pen)
            zero_elevation = self.coords_scale(0, self.map_range[2], self.map_scale[1], 0)
            painter.drawLine(0, zero_elevation, self.display_width, zero_elevation)

    def draw_position_mark(self, painter):
        """Draw position mark"""
        self.pen.setWidth(self.wcfg["position_mark_width"])
        self.pen.setColor(self.wcfg["position_mark_color"])
        painter.setPen(self.pen)
        painter.drawLine(self.veh_pos[2], 0, self.veh_pos[2], self.display_height)

    def draw_readings(self, painter):
        """Draw readings"""
        painter.setFont(self.font)
        self.pen.setColor(self.wcfg["font_color"])
        painter.setPen(self.pen)
        if self.wcfg["show_elevation_reading"]:
            painter.drawText(
                self.rect_text_elevation,
                self.elevation_text_alignment,
                self.format_elevation(api.read.vehicle.position_vertical())
            )
        if self.wcfg["show_elevation_scale"]:
            painter.drawText(
                self.rect_text_scale,
                self.scale_text_alignment,
                self.format_scale(self.map_scale[1])
            )

    # Additional methods
    @staticmethod
    def coords_scale(coords, min_range, scale, offset):
        """Coordinates scale & offset"""
        return (coords - min_range) * scale + offset

    def format_elevation(self, meter):
        """Format elevation"""
        if self.cfg.units["distance_unit"] == "Feet":
            return f"{calc.meter2feet(meter):.01f}ft"
        return f"{meter:.01f}m"

    def format_scale(self, scale):
        """Format elevation scale (meter or feet per pixel)"""
        if scale == 0:
            return "1:1"
        if self.cfg.units["distance_unit"] == "Feet":
            return f"1:{round(calc.meter2feet(1 / scale), 2)}"
        return f"1:{round(1 / scale, 2)}"
