#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "cruise"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_cruise = tkfont.Font(family=self.wcfg["font_name"],
                                  size=-self.wcfg["font_size"],
                                  weight=self.wcfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_cruise}

        if self.wcfg["show_track_clock"]:
            self.bar_trackclock = tk.Label(self, bar_style, text="", width=7,
                                           fg=self.wcfg["font_color_track_clock"],
                                           bg=self.wcfg["bkg_color_track_clock"])
            self.bar_trackclock.grid(row=0, column=0, padx=(0, bar_gap), pady=0)

        self.bar_compass = tk.Label(self, bar_style, text="CRUISE", width=7,
                                    fg=self.wcfg["font_color_compass"],
                                    bg=self.wcfg["bkg_color_compass"])
        self.bar_compass.grid(row=0, column=1, padx=0, pady=0)

        if self.wcfg["show_elevation"]:
            self.bar_elevation = tk.Label(self, bar_style, text="", width=7,
                                          fg=self.wcfg["font_color_elevation"],
                                          bg=self.wcfg["bkg_color_elevation"])
            self.bar_elevation.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)

        if self.wcfg["show_odometer"]:
            self.bar_odometer = tk.Label(self, bar_style, text="", width=9,
                                         fg=self.wcfg["font_color_odometer"],
                                         bg=self.wcfg["bkg_color_odometer"])
            self.bar_odometer.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)

        # Last data
        self.last_dir_degree = 0
        self.last_time_curr = 0
        self.last_pos_y = 0
        self.last_traveled_distance = 0

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read cruise data
            ori_yaw, pos_y, time_start, time_curr = read_data.cruise()

            # Start updating

            # Compass
            dir_degree = round(180 - calc.rad2deg(calc.oriyaw2rad(*ori_yaw)), 0)
            self.update_compass(dir_degree, self.last_dir_degree)
            self.last_dir_degree = dir_degree

            # Track clock
            if self.wcfg["show_track_clock"]:
                self.update_trackclock(time_curr, self.last_time_curr, time_start)
                self.last_time_curr = time_curr

            # Elevation
            if self.wcfg["show_elevation"]:
                self.update_elevation(pos_y, self.last_pos_y)
                self.last_pos_y = pos_y

            # Odometer
            if self.wcfg["show_odometer"]:
                traveled_distance = module.delta_time.meters_driven
                self.update_odometer(traveled_distance, self.last_traveled_distance)
                self.last_traveled_distance = traveled_distance

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_compass(self, curr, last):
        """Compass"""
        if curr != last:
            self.bar_compass.config(text=f"{curr:03.0f}°{self.deg2direction(curr)}")

    def update_trackclock(self, curr, last, start):
        """Track clock"""
        if curr != last:
            time_offset = curr * self.wcfg["track_clock_time_scale"]

            time_diff = (1440 - start) + time_offset
            while time_diff <= -start:
                time_offset += time_diff

            track_clock = start + time_offset

            clock_text = time.strftime(self.wcfg["track_clock_format"], time.gmtime(track_clock))
            self.bar_trackclock.config(text=clock_text, width=len(clock_text)+1)

    def update_elevation(self, curr, last):
        """Elevation"""
        if curr != last:
            if self.wcfg["elevation_unit"] == "0":
                elev_text = f"↑ {curr: =03.0f}m"
            else:
                elev_text = f"↑ {curr * 3.2808399: =03.0f}ft"
            self.bar_elevation.config(text=elev_text, width=len(elev_text)+1)

    def update_odometer(self, curr, last):
        """Odometer"""
        if curr != last:
            if self.wcfg["odometer_unit"] == "0":  # kilometer
                dist_text = f"{curr * 0.001:06.01f}km"
            else:  # mile
                dist_text = f"{curr / 1609.344:06.01f}mi"
            self.bar_odometer.config(text=dist_text, width=len(dist_text)+1)

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
