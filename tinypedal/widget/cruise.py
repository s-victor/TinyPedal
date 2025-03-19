#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from .. import calculation as calc
from ..api_control import api
from ..const_common import COMPASS_BEARINGS
from ..module_info import minfo
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.odm_digits = max(int(self.wcfg["odometer_maximum_digits"]), 1)
        self.odm_range = float(self.odm_digits * "9") + 0.9

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Track clock
        if self.wcfg["show_track_clock"]:
            text_clock = self.format_clock(0)
            bar_style_track_clock = self.set_qss(
                fg_color=self.wcfg["font_color_track_clock"],
                bg_color=self.wcfg["bkg_color_track_clock"]
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
                fg_color=self.wcfg["font_color_compass"],
                bg_color=self.wcfg["bkg_color_compass"]
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
                fg_color=self.wcfg["font_color_elevation"],
                bg_color=self.wcfg["bkg_color_elevation"]
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
                fg_color=self.wcfg["font_color_odometer"],
                bg_color=self.wcfg["bkg_color_odometer"]
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

        # Distance into lap
        if self.wcfg["show_distance_into_lap"]:
            text_lap_distance = self.format_lap_distance(0)
            bar_style_lap_distance = self.set_qss(
                fg_color=self.wcfg["font_color_distance_into_lap"],
                bg_color=self.wcfg["bkg_color_distance_into_lap"]
            )
            self.bar_lap_distance = self.set_qlabel(
                text=text_lap_distance,
                style=bar_style_lap_distance,
                width=font_m.width * len(text_lap_distance) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_lap_distance,
                column=self.wcfg["column_index_distance_into_lap"],
            )

        # Cornering radius
        if self.wcfg["show_cornering_radius"]:
            text_cornering_radius = self.format_cornering_radius(0)
            bar_style_cornering_radius = self.set_qss(
                fg_color=self.wcfg["font_color_cornering_radius"],
                bg_color=self.wcfg["bkg_color_cornering_radius"]
            )
            self.bar_cornering_radius = self.set_qlabel(
                text=text_cornering_radius,
                style=bar_style_cornering_radius,
                width=font_m.width * len(text_cornering_radius) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_cornering_radius,
                column=self.wcfg["column_index_cornering_radius"],
            )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Track clock
            if self.wcfg["show_track_clock"]:
                if self.wcfg["enable_track_clock_synchronization"]:
                    time_scale = minfo.restapi.timeScale
                else:
                    time_scale = self.wcfg["track_clock_time_scale"]
                if time_scale < 0:
                    time_scale = 0
                track_time = calc.clock_time(
                    api.read.session.elapsed(), api.read.session.start(), time_scale)
                self.update_track_clock(self.bar_track_clock, track_time)

            # Compass
            if self.wcfg["show_compass"]:
                orientation = api.read.vehicle.orientation_yaw_radians()
                self.update_compass(self.bar_compass, orientation)

            # Elevation
            if self.wcfg["show_elevation"]:
                elevation = api.read.vehicle.position_vertical()
                self.update_elevation(self.bar_elevation, elevation)

            # Odometer
            if self.wcfg["show_odometer"]:
                traveled_distance = int(minfo.stats.metersDriven)
                self.update_odometer(self.bar_odometer, traveled_distance)

            # Distance into lap
            if self.wcfg["show_distance_into_lap"]:
                lap_distance = minfo.delta.lapDistance
                self.update_lap_distance(self.bar_lap_distance, lap_distance)

            # Cornering radius
            if self.wcfg["show_cornering_radius"]:
                cornering_radius = minfo.wheels.corneringRadius
                self.update_cornering_radius(self.bar_cornering_radius, cornering_radius)

    # GUI update methods
    def update_track_clock(self, target, data):
        """Track clock"""
        if target.last != data:
            target.last = data
            target.setText(self.format_clock(data))

    def update_compass(self, target, data):
        """Compass"""
        if target.last != data:
            target.last = data
            target.setText(self.format_compass(data))

    def update_elevation(self, target, data):
        """Elevation"""
        if target.last != data:
            target.last = data
            target.setText(self.format_elevation(data))

    def update_odometer(self, target, data):
        """Odometer"""
        if target.last != data:
            target.last = data
            target.setText(self.format_odometer(data))

    def update_lap_distance(self, target, data):
        """Distance into lap"""
        if target.last != data:
            target.last = data
            target.setText(self.format_lap_distance(data))

    def update_cornering_radius(self, target, data):
        """Cornering radius"""
        if target.last != data:
            target.last = data
            target.setText(self.format_cornering_radius(data))

    # Additional methods
    def format_clock(self, second):
        """Format clock"""
        return strftime(self.wcfg["track_clock_format"], gmtime(second))

    def format_compass(self, yaw):
        """Format compass"""
        degree = 180 - calc.rad2deg(yaw)
        return f"{degree:03.0f}°{calc.select_grade(COMPASS_BEARINGS, degree): >2}"

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

    def format_lap_distance(self, meter):
        """Format lap distance"""
        if self.cfg.units["distance_unit"] == "Feet":
            return f"{calc.meter2feet(meter): >7.0f}ft"
        return f"{meter: >6.0f}m"

    def format_cornering_radius(self, meter):
        """Format cornering radius"""
        if meter > 999:
            meter = 0
        if self.cfg.units["distance_unit"] == "Feet":
            return f"r{calc.meter2feet(meter): >4.0f}ft"
        return f"r{meter: >3.0f}m"
