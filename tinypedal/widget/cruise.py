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

from time import strftime, gmtime

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

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
        self.odm_digits = max(int(self.wcfg["odometer_maximum_digits"]), 1)
        self.odm_range = float(self.odm_digits * "9") + 0.9

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
        self.setLayout(layout)

        # Track clock
        if self.wcfg["show_track_clock"]:
            text_clock = self.format_clock(0)
            bar_style_track_clock = self.set_qss(
                self.wcfg["font_color_track_clock"],
                self.wcfg["bkg_color_track_clock"]
            )
            self.bar_track_clock = self.set_qlabel(
                text=text_clock,
                style=bar_style_track_clock,
                width=font_m.width * len(text_clock) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_track_clock,
                column=self.wcfg["column_index_track_clock"],
            )

        # Compass
        if self.wcfg["show_compass"]:
            text_compass = self.format_compass(0)
            bar_style_compass = self.set_qss(
                self.wcfg["font_color_compass"],
                self.wcfg["bkg_color_compass"]
            )
            self.bar_compass = self.set_qlabel(
                text=text_compass,
                style=bar_style_compass,
                width=font_m.width * len(text_compass) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_compass,
                column=self.wcfg["column_index_compass"],
            )

        # Elevation
        if self.wcfg["show_elevation"]:
            text_elevation = self.format_elevation(0)
            bar_style_elevation = self.set_qss(
                self.wcfg["font_color_elevation"],
                self.wcfg["bkg_color_elevation"]
            )
            self.bar_elevation = self.set_qlabel(
                text=text_elevation,
                style=bar_style_elevation,
                width=font_m.width * len(text_elevation) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_elevation,
                column=self.wcfg["column_index_elevation"],
            )

        # Odometer
        if self.wcfg["show_odometer"]:
            text_odometer = self.format_odometer(0)
            bar_style_odometer = self.set_qss(
                self.wcfg["font_color_odometer"],
                self.wcfg["bkg_color_odometer"]
            )
            self.bar_odometer = self.set_qlabel(
                text=text_odometer,
                style=bar_style_odometer,
                width=font_m.width * len(text_odometer) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_odometer,
                column=self.wcfg["column_index_odometer"],
            )

        # Last data
        self.last_track_time = None
        self.last_orientation = None
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

                track_time = calc.clock_time(
                    api.read.session.elapsed(), api.read.session.start(), time_scale)
                self.update_track_clock(track_time, self.last_track_time)
                self.last_track_time = track_time

            # Compass
            if self.wcfg["show_compass"]:
                orientation = api.read.vehicle.orientation_yaw_radians()
                self.update_compass(orientation, self.last_orientation)
                self.last_orientation = orientation

            # Elevation
            if self.wcfg["show_elevation"]:
                elevation = api.read.vehicle.position_vertical()
                self.update_elevation(elevation, self.last_elevation)
                self.last_elevation = elevation

            # Odometer
            if self.wcfg["show_odometer"]:
                traveled_distance = int(minfo.delta.metersDriven)
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
            self.bar_compass.setText(self.format_compass(curr))

    def update_elevation(self, curr, last):
        """Elevation"""
        if curr != last:
            self.bar_elevation.setText(self.format_elevation(curr))

    def update_odometer(self, curr, last):
        """Odometer"""
        if curr != last:
            self.bar_odometer.setText(self.format_odometer(curr))

    # Additional methods
    def format_clock(self, second):
        """Format clock"""
        return strftime(self.wcfg["track_clock_format"], gmtime(second))

    def format_compass(self, yaw):
        """Format compass"""
        degree = 180 - calc.rad2deg(yaw)
        return f"{degree:03.0f}°{self.deg2direction(degree)}"

    def format_elevation(self, meter):
        """Format elevation"""
        if self.cfg.units["distance_unit"] == "Feet":
            return f"↑{calc.meter2feet(meter): >5.0f}ft"
        return f"↑{meter: >4.0f}m"

    def format_odometer(self, meter):
        """Format odometer"""
        if self.cfg.units["odometer_unit"] == "Kilometer":
            distance = min(calc.meter2kilometer(meter), self.odm_range)
            return f"{distance: >{self.odm_digits + 2}.1f}km"
        if self.cfg.units["odometer_unit"] == "Mile":
            distance = min(calc.meter2mile(meter), self.odm_range)
            return f"{distance: >{self.odm_digits + 2}.1f}mi"
        return f"{min(meter, int(self.odm_range)): >{self.odm_digits}d}m"

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
