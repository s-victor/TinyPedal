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
Cruise Widget
"""

from functools import partial
from time import strftime, gmtime

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "cruise"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
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
            clock_text = self.format_clock(0)
            self.bar_track_clock = QLabel(clock_text)
            self.bar_track_clock.setAlignment(Qt.AlignCenter)
            self.bar_track_clock.setStyleSheet(
                f"color: {self.wcfg['font_color_track_clock']};"
                f"background: {self.wcfg['bkg_color_track_clock']};"
                f"min-width: {font_m.width * len(clock_text) + bar_padx}px;"
            )

        # Compass
        if self.wcfg["show_compass"]:
            compass_text = self.format_compass(0)
            self.bar_compass = QLabel(compass_text)
            self.bar_compass.setAlignment(Qt.AlignCenter)
            self.bar_compass.setStyleSheet(
                f"color: {self.wcfg['font_color_compass']};"
                f"background: {self.wcfg['bkg_color_compass']};"
                f"min-width: {font_m.width * len(compass_text) + bar_padx}px;"
            )

        # Elevation
        if self.wcfg["show_elevation"]:
            elevation_text = self.format_elevation(0)
            self.bar_elevation = QLabel(elevation_text)
            self.bar_elevation.setAlignment(Qt.AlignCenter)
            self.bar_elevation.setStyleSheet(
                f"color: {self.wcfg['font_color_elevation']};"
                f"background: {self.wcfg['bkg_color_elevation']};"
                f"min-width: {font_m.width * len(elevation_text) + bar_padx}px;"
            )

        # Odometer
        if self.wcfg["show_odometer"]:
            odometer_text = self.format_odometer(0)
            self.odometer_width = partial(
                calc.qss_min_width,
                style=f"color: {self.wcfg['font_color_odometer']};background: {self.wcfg['bkg_color_odometer']};",
                font_width=font_m.width,
                padding=bar_padx,
            )
            self.bar_odometer = QLabel(odometer_text)
            self.bar_odometer.setAlignment(Qt.AlignCenter)
            self.bar_odometer.setStyleSheet(self.odometer_width(len(odometer_text)))

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

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Track clock
            if self.wcfg["show_track_clock"]:
                if self.cfg.user.setting["module_restapi"]["enable"]:
                    time_scale = minfo.restapi.timeScale
                    if time_scale < 0:
                        time_scale = self.wcfg["track_clock_time_scale"]
                else:
                    time_scale = self.wcfg["track_clock_time_scale"]

                track_time = int(calc.clock_time(
                    api.read.session.elapsed(),
                    api.read.session.start(),
                    time_scale))
                self.update_track_clock(track_time, self.last_track_time)
                self.last_track_time = track_time

            # Compass
            if self.wcfg["show_compass"]:
                dir_degree = self.format_compass(180 - calc.rad2deg(api.read.vehicle.orientation_yaw_radians()))
                self.update_compass(dir_degree, self.last_dir_degree)
                self.last_dir_degree = dir_degree

            # Elevation
            if self.wcfg["show_elevation"]:
                elevation = self.format_elevation(api.read.vehicle.position_vertical())
                self.update_elevation(elevation, self.last_elevation)
                self.last_elevation = elevation

            # Odometer
            if self.wcfg["show_odometer"]:
                traveled_distance = self.format_odometer(minfo.delta.metersDriven)
                self.update_odometer(traveled_distance, self.last_traveled_distance)
                self.last_traveled_distance = traveled_distance

    # GUI update methods
    def update_track_clock(self, curr, last):
        """Track clock"""
        if curr != last:
            self.bar_track_clock.setText(self.format_clock(curr))

    def update_compass(self, curr, last):
        """Compass"""
        if curr != last:
            self.bar_compass.setText(curr)

    def update_elevation(self, curr, last):
        """Elevation"""
        if curr != last:
            self.bar_elevation.setText(curr)

    def update_odometer(self, curr, last):
        """Odometer"""
        if curr != last:
            self.bar_odometer.setText(curr)
            self.bar_odometer.setStyleSheet(self.odometer_width(len(curr)))

    # Additional methods
    def format_clock(self, second):
        """Format clock"""
        return strftime(self.wcfg["track_clock_format"], gmtime(second))

    def format_compass(self, degree):
        """Format compass"""
        return f"{degree:03.0f}°{self.deg2direction(degree)}"

    def format_elevation(self, meter):
        """Format elevation"""
        if self.cfg.units["distance_unit"] == "Feet":
            return f"↑{calc.meter2feet(meter):5.0f}ft".rjust(8)
        return f"↑{meter:4.0f}m".rjust(6)

    def format_odometer(self, meter):
        """Format odometer"""
        if self.cfg.units["odometer_unit"] == "Kilometer":
            return f"{calc.meter2kilometer(meter):6.1f}km"
        if self.cfg.units["odometer_unit"] == "Mile":
            return f"{calc.meter2mile(meter):6.1f}mi"
        return f"{meter:7.0f}m"

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
