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
Wheel Alignment Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "wheel"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color = self.wcfg["font_color"]
        bg_color = self.wcfg["bkg_color"]
        fg_color_cap = self.wcfg["font_color_caption"]
        bg_color_cap = self.wcfg["bkg_color_caption"]
        font_wheel = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight"])
        font_desc = tkfont.Font(family=self.wcfg["font_name"],
                                size=-int(self.wcfg["font_size"] * 0.8),
                                weight=self.wcfg["font_weight"])

        # Draw label
        if self.wcfg["show_caption"]:
            bar_style_desc = {"bd":0, "height":1, "padx":0, "pady":0,
                              "font":font_desc, "fg":fg_color_cap, "bg":bg_color_cap}

            self.bar_camber_desc = tk.Label(self, bar_style_desc, text="camber")
            self.bar_toe_desc = tk.Label(self, bar_style_desc, text="toe in")
            self.bar_rideh_desc = tk.Label(self, bar_style_desc, text="ride height")
            self.bar_rake_desc = tk.Label(self, bar_style_desc, text="rake angle")

            self.bar_camber_desc.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="we")
            self.bar_toe_desc.grid(row=3, column=0, columnspan=2, padx=0, pady=0, sticky="we")
            self.bar_rideh_desc.grid(row=6, column=0, columnspan=2, padx=0, pady=0, sticky="we")
            self.bar_rake_desc.grid(row=9, column=0, columnspan=2, padx=0, pady=0, sticky="we")

        bar_style = {"text":text_def, "bd":0, "height":1, "width":7, "padx":0,
                     "pady":0, "font":font_wheel, "fg":fg_color, "bg":bg_color}

        self.bar_camber_fl = tk.Label(self, bar_style)
        self.bar_camber_fr = tk.Label(self, bar_style)
        self.bar_camber_rl = tk.Label(self, bar_style)
        self.bar_camber_rr = tk.Label(self, bar_style)

        self.bar_toe_fl = tk.Label(self, bar_style)
        self.bar_toe_fr = tk.Label(self, bar_style)
        self.bar_toe_rl = tk.Label(self, bar_style)
        self.bar_toe_rr = tk.Label(self, bar_style)

        self.bar_rideh_fl = tk.Label(self, bar_style)
        self.bar_rideh_fr = tk.Label(self, bar_style)
        self.bar_rideh_rl = tk.Label(self, bar_style)
        self.bar_rideh_rr = tk.Label(self, bar_style)

        self.bar_rake = tk.Label(self, bar_style)
        self.bar_rakeangle = tk.Label(self, bar_style)

        self.bar_camber_fl.grid(row=1, column=0, padx=0, pady=0)
        self.bar_camber_fr.grid(row=1, column=1, padx=0, pady=0)
        self.bar_camber_rl.grid(row=2, column=0, padx=0, pady=(0, bar_gap))
        self.bar_camber_rr.grid(row=2, column=1, padx=0, pady=(0, bar_gap))

        self.bar_toe_fl.grid(row=4, column=0, padx=0, pady=0)
        self.bar_toe_fr.grid(row=4, column=1, padx=0, pady=0)
        self.bar_toe_rl.grid(row=5, column=0, padx=0, pady=(0, bar_gap))
        self.bar_toe_rr.grid(row=5, column=1, padx=0, pady=(0, bar_gap))

        self.bar_rideh_fl.grid(row=7, column=0, padx=0, pady=0)
        self.bar_rideh_fr.grid(row=7, column=1, padx=0, pady=0)
        self.bar_rideh_rl.grid(row=8, column=0, padx=0, pady=(0, bar_gap))
        self.bar_rideh_rr.grid(row=8, column=1, padx=0, pady=(0, bar_gap))

        self.bar_rake.grid(row=10, column=0, padx=0, pady=0)
        self.bar_rakeangle.grid(row=10, column=1, padx=0, pady=0)

        # Last data
        self.last_camber = [-1] * 4
        self.last_toe = [-1] * 4
        self.last_ride_height = [-1] * 4
        self.last_rake = -1
        self.last_rake_angle = -1

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read camber data
            camber = tuple(map(calc.rad2deg, read_data.camber()))

            # Read toe data
            toe = tuple(map(calc.rad2deg, read_data.toe()))

            # Read ride height & rake data
            ride_height = tuple(map(calc.meter2millmeter, read_data.ride_height()))

            # Camber
            self.update_wheel("camber_fl", camber[0], self.last_camber[0])
            self.update_wheel("camber_fr", camber[1], self.last_camber[1])
            self.update_wheel("camber_rl", camber[2], self.last_camber[2])
            self.update_wheel("camber_rr", camber[3], self.last_camber[3])
            self.last_camber = camber

            # Toe in
            self.update_wheel("toe_fl", toe[0], self.last_toe[0])
            self.update_wheel("toe_fr", toe[1], self.last_toe[1])
            self.update_wheel("toe_rl", toe[2], self.last_toe[2])
            self.update_wheel("toe_rr", toe[3], self.last_toe[3])
            self.last_toe = toe

            # Ride height
            self.update_rideh("rideh_fl", ride_height[0], self.last_ride_height[0],
                              self.wcfg["rideheight_offset_front"])
            self.update_rideh("rideh_fr", ride_height[1], self.last_ride_height[1],
                              self.wcfg["rideheight_offset_front"])
            self.update_rideh("rideh_rl", ride_height[2], self.last_ride_height[2],
                              self.wcfg["rideheight_offset_rear"])
            self.update_rideh("rideh_rr", ride_height[3], self.last_ride_height[3],
                              self.wcfg["rideheight_offset_rear"])
            self.last_ride_height = ride_height

            # Rake
            rake = calc.rake(*ride_height)
            self.update_rideh("rake", rake, self.last_rake, 0)
            self.last_rake = rake

            # Rake angle
            rake_angle = calc.rake2angle(rake, self.wcfg["wheelbase"])
            self.update_rakeangle(rake_angle, self.last_rake_angle, 0)
            self.last_rake_angle = rake_angle

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_wheel(self, suffix, curr, last):
        """Wheel data"""
        if round(curr, 2) != round(last, 2):
            getattr(self, f"bar_{suffix}").config(text=f"{curr:+.02f}")

    def update_rideh(self, suffix, curr, last, offset):
        """Ride height data"""
        if round(curr, 1) != round(last, 1):
            getattr(self, f"bar_{suffix}").config(
                text=f"{curr:+.01f}",
                bg=self.color_rideh(curr, offset))

    def update_rakeangle(self, curr, last, offset):
        """Rake angle data"""
        if round(curr, 2) != round(last, 2):
            self.bar_rakeangle.config(
                text=f" {curr:+.02f}°",
                bg=self.color_rideh(curr, offset))

    # Additional methods
    def color_rideh(self, height, offset):
        """Ride height indicator color"""
        if height > offset:
            color = self.wcfg["bkg_color"]
        else:
            color = self.wcfg["bkg_color_bottoming"]
        return color
