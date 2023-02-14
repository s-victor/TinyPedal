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
Suspension Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "suspension"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]

        # Config style & variable
        font_susp = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        column_rideh = self.wcfg["column_index_ride_height"]
        column_rake = self.wcfg["column_index_rake_angle"]

        # Draw label
        frame_rideh = tk.Frame(self, bd=0, highlightthickness=0)
        frame_rake = tk.Frame(self, bd=0, highlightthickness=0)

        if self.wcfg["show_caption"]:
            self.add_caption(frame=frame_rideh, toggle="show_ride_height", value="ride height")
            self.add_caption(frame=frame_rake, toggle="show_rake_angle", value="rake angle")

        if self.wcfg["show_ride_height"]:
            bar_style_rideh = {"text":"n/a", "bd":0, "height":1, "width":5,
                               "padx":bar_padx, "pady":0, "font":font_susp,
                               "fg":self.wcfg["font_color_ride_height"],
                               "bg":self.wcfg["bkg_color_ride_height"]}
            self.bar_rideh_fl = tk.Label(frame_rideh, bar_style_rideh)
            self.bar_rideh_fr = tk.Label(frame_rideh, bar_style_rideh)
            self.bar_rideh_rl = tk.Label(frame_rideh, bar_style_rideh)
            self.bar_rideh_rr = tk.Label(frame_rideh, bar_style_rideh)
            self.bar_rideh_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_rideh_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_rideh_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_rideh_rr.grid(row=2, column=1, padx=0, pady=0)

            frame_rideh.grid(row=column_rideh, column=0, padx=0, pady=(0,bar_gap))

        if self.wcfg["show_rake_angle"]:
            bar_style_rake = {"text":"n/a", "bd":0, "height":1, "width":5,
                              "padx":bar_padx, "pady":0, "font":font_susp,
                              "fg":self.wcfg["font_color_rake_angle"],
                              "bg":self.wcfg["bkg_color_rake_angle"]}
            self.bar_rake = tk.Label(frame_rake, bar_style_rake, width=10, padx=bar_padx*2)
            self.bar_rake.grid(row=1, column=0, columnspan=2, padx=0, pady=0)

            frame_rake.grid(row=column_rake, column=0, padx=0, pady=(0,bar_gap))

        # Last data
        self.last_ride_height = [-1] * 4
        self.last_rake = -1

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read ride height & rake data
            ride_height = tuple(map(calc.meter2millmeter, read_data.ride_height()))

            # Ride height
            if self.wcfg["show_ride_height"]:
                self.update_rideh("rideh_fl", ride_height[0], self.last_ride_height[0],
                                  self.wcfg["ride_height_offset_front_left"])
                self.update_rideh("rideh_fr", ride_height[1], self.last_ride_height[1],
                                  self.wcfg["ride_height_offset_front_right"])
                self.update_rideh("rideh_rl", ride_height[2], self.last_ride_height[2],
                                  self.wcfg["ride_height_offset_rear_left"])
                self.update_rideh("rideh_rr", ride_height[3], self.last_ride_height[3],
                                  self.wcfg["ride_height_offset_rear_right"])
                self.last_ride_height = ride_height

            # Rake angle
            if self.wcfg["show_rake_angle"]:
                rake = round(calc.rake(*ride_height), 2)
                self.update_rakeangle(rake, self.last_rake, 0)
                self.last_rake = rake

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_rideh(self, suffix, curr, last, offset):
        """Ride height data"""
        if round(curr, 1) != round(last, 1):
            getattr(self, f"bar_{suffix}").config(
                text=self.format_num(curr),
                bg=self.color_rideh(curr, offset))

    def update_rakeangle(self, curr, last, offset):
        """Rake angle data"""
        if curr != last:
            rake_angle = calc.rake2angle(curr, self.wcfg["wheelbase"])
            self.bar_rake.config(
                text=f"{rake_angle:+.02f}°({abs(curr):02.0f})",
                bg=self.color_rake(curr, offset))

    # Additional methods
    @staticmethod
    def format_num(value):
        """Format number"""
        if value > 99.9:
            return f"{value:+.0f}"
        return f"{value:+.01f}"

    def color_rideh(self, value, offset):
        """Ride height indicator color"""
        if value > offset:
            return self.wcfg["bkg_color_ride_height"]
        return self.wcfg["warning_color_bottoming"]

    def color_rake(self, value, offset):
        """Rake angle indicator color"""
        if value > offset:
            return self.wcfg["bkg_color_rake_angle"]
        return self.wcfg["warning_color_negative_rake"]
