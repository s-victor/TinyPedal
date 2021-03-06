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

from tinypedal.__init__ import cfg
import tinypedal.readapi as read_data
from tinypedal.base import delta_time, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "cruise"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        bar_gap = self.cfg["bar_gap"]
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        # Config style & variable
        font_cruise = tkfont.Font(family=self.cfg["font_name"],
                                  size=-self.cfg["font_size"],
                                  weight=self.cfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_cruise}

        if self.cfg["show_track_clock"]:
            self.bar_trackclock = tk.Label(self, bar_style, text="", width=7,
                                            fg=self.cfg["font_color_track_clock"],
                                            bg=self.cfg["bkg_color_track_clock"])
            self.bar_trackclock.grid(row=0, column=0, padx=(0, bar_gap), pady=0)

        self.bar_compass = tk.Label(self, bar_style, text="CRUISE", width=7,
                                    fg=self.cfg["font_color_compass"],
                                    bg=self.cfg["bkg_color_compass"])
        self.bar_compass.grid(row=0, column=1, padx=0, pady=0)

        if self.cfg["show_elevation"]:
            self.bar_elevation = tk.Label(self, bar_style, text="", width=7,
                                          fg=self.cfg["font_color_elevation"],
                                          bg=self.cfg["bkg_color_elevation"])
            self.bar_elevation.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)

        if self.cfg["show_odometer"]:
            self.bar_odometer = tk.Label(self, bar_style, text="", width=9,
                                         fg=self.cfg["font_color_odometer"],
                                         bg=self.cfg["bkg_color_odometer"])
            self.bar_odometer.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read cruise data
            ori_yaw, pos_y, time_start, time_curr = read_data.cruise()

            # Check isPlayer before update
            if read_data.is_local_player():

                # Cruise update
                self.bar_compass.config(text=f"{ori_yaw:03.0f}??{self.deg2direction(ori_yaw)}")

                if self.cfg["show_track_clock"]:

                    time_curr *= self.cfg["track_clock_time_scale"]
                    time_offset = time_curr

                    while True:
                        time_diff = (1440 - time_start) - time_curr + time_offset

                        if time_diff <= -time_start:
                            time_offset += time_diff
                        elif time_diff > -time_start:
                            break

                    track_clock = time_start + time_offset
                    clock_text = time.strftime(self.cfg["track_clock_format"],
                                               time.gmtime(track_clock))
                    self.bar_trackclock.config(text=clock_text, width=len(clock_text)+1)

                if self.cfg["show_elevation"]:
                    if self.cfg["elevation_unit"] == "1":
                        pos_y *= 3.2808399
                        elev_text = f"??? {pos_y: =03.0f}ft"
                    else:
                        elev_text = f"??? {pos_y: =03.0f}m"

                    self.bar_elevation.config(text=elev_text, width=len(elev_text)+1)

                if self.cfg["show_odometer"]:
                    traveled_distance = delta_time.meters_driven * 0.001

                    if self.cfg["odometer_unit"] == "1":
                        traveled_distance /= 1.609344
                        dist_text = f"{traveled_distance:06.01f}mi"
                    else:
                        dist_text = f"{traveled_distance:06.01f}km"

                    self.bar_odometer.config(text=dist_text, width=len(dist_text)+1)

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

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
