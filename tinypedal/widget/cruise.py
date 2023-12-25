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
Cruise Widget
"""

import time
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from . import Overlay
from ..module_info import minfo

WIDGET_NAME = "cruise"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_trkc = self.wcfg["column_index_track_clock"]
        column_comp = self.wcfg["column_index_compass"]
        column_evel = self.wcfg["column_index_elevation"]
        column_odom = self.wcfg["column_index_odometer"]

        # Track clock
        if self.wcfg["show_track_clock"]:
            self.bar_track_clock = QLabel("T CLOCK")
            self.bar_track_clock.setAlignment(Qt.AlignCenter)
            self.bar_track_clock.setStyleSheet(
                f"color: {self.wcfg['font_color_track_clock']};"
                f"background: {self.wcfg['bkg_color_track_clock']};"
            )

        # Compass
        if self.wcfg["show_compass"]:
            self.bar_compass = QLabel("COMPASS")
            self.bar_compass.setAlignment(Qt.AlignCenter)
            self.bar_compass.setStyleSheet(
                f"color: {self.wcfg['font_color_compass']};"
                f"background: {self.wcfg['bkg_color_compass']};"
            )

        # Elevation
        if self.wcfg["show_elevation"]:
            self.bar_elevation = QLabel("ELEVATION")
            self.bar_elevation.setAlignment(Qt.AlignCenter)
            self.bar_elevation.setStyleSheet(
                f"color: {self.wcfg['font_color_elevation']};"
                f"background: {self.wcfg['bkg_color_elevation']};"
            )

        # Odometer
        if self.wcfg["show_odometer"]:
            self.bar_odometer = QLabel("ODOMETER")
            self.bar_odometer.setAlignment(Qt.AlignCenter)
            self.bar_odometer.setStyleSheet(
                f"color: {self.wcfg['font_color_odometer']};"
                f"background: {self.wcfg['bkg_color_odometer']};"
            )

        # Set layout
        if self.wcfg["show_track_clock"]:
            layout.addWidget(self.bar_track_clock, 0, column_trkc)
        if self.wcfg["show_compass"]:
            layout.addWidget(self.bar_compass, 0, column_comp)
        if self.wcfg["show_elevation"]:
            layout.addWidget(self.bar_elevation, 0, column_evel)
        if self.wcfg["show_odometer"]:
            layout.addWidget(self.bar_odometer, 0, column_odom)
        self.setLayout(layout)

        # Last data
        self.last_track_time = None
        self.last_dir_degree = None
        self.last_elevation = None
        self.last_traveled_distance = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Track clock
            if self.wcfg["show_track_clock"]:
                track_time = int(api.read.session.elapsed())
                time_start = int(api.read.session.start())
                self.update_track_clock(track_time, self.last_track_time, time_start)
                self.last_track_time = track_time

            # Compass
            if self.wcfg["show_compass"]:
                dir_degree = round(180 - calc.rad2deg(api.read.vehicle.orientation_yaw_radians()))
                self.update_compass(dir_degree, self.last_dir_degree)
                self.last_dir_degree = dir_degree

            # Elevation
            if self.wcfg["show_elevation"]:
                elevation = round(api.read.vehicle.pos_vertical(), 3)
                self.update_elevation(elevation, self.last_elevation)
                self.last_elevation = elevation

            # Odometer
            if self.wcfg["show_odometer"]:
                traveled_distance = minfo.delta.metersDriven
                self.update_odometer(traveled_distance, self.last_traveled_distance)
                self.last_traveled_distance = traveled_distance

    # GUI update methods
    def update_track_clock(self, curr, last, start):
        """Track clock"""
        if curr != last:
            time_offset = curr * self.wcfg["track_clock_time_scale"]

            time_diff = (1440 - start) + time_offset
            while time_diff <= -start:
                time_offset += time_diff

            track_clock = start + time_offset

            clock_text = time.strftime(
                self.wcfg["track_clock_format"], time.gmtime(track_clock))
            self.bar_track_clock.setText(clock_text)

    def update_compass(self, curr, last):
        """Compass"""
        if curr != last:
            self.bar_compass.setText(f"{curr:03.0f}°{self.deg2direction(curr)}")

    def update_elevation(self, curr, last):
        """Elevation"""
        if curr != last:
            if self.cfg.units["distance_unit"] == "Feet":
                elev_text = "↑ " + f"{curr * 3.2808399:.0f}ft".rjust(5)
            else:  # meter
                elev_text = "↑ " + f"{curr:.0f}m".rjust(4)
            self.bar_elevation.setText(elev_text)

    def update_odometer(self, curr, last):
        """Odometer"""
        if curr != last:
            if self.cfg.units["odometer_unit"] == "Mile":
                dist_text = f"{curr / 1609.344:06.01f}mi"
            elif self.cfg.units["odometer_unit"] == "Meter":
                dist_text = f"{curr:07.0f}m"
            else:  # kilometer
                dist_text = f"{curr * 0.001:06.01f}km"
            self.bar_odometer.setText(dist_text)

    # Additional methods
    @staticmethod
    def deg2direction(degrees):
        """Convert degree to direction"""
        if degrees <= 22.5 or degrees >= 337.5:
            text = " N"
        elif 22.5 < degrees < 67.5:
            text = "NE"
        elif 67.5 <= degrees <= 112.5:
            text = " E"
        elif 112.5 < degrees < 157.5:
            text = "SE"
        elif 157.5 <= degrees <= 202.5:
            text = " S"
        elif 202.5 < degrees < 247.5:
            text = "SW"
        elif 247.5 <= degrees <= 292.5:
            text = " W"
        elif 292.5 < degrees < 337.5:
            text = "NW"
        return text
