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
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]

        # Config style & variable
        font_wheel = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight"])

        column_camber = self.wcfg["column_index_camber"]
        column_toein = self.wcfg["column_index_toe_in"]

        # Draw label
        frame_camber = tk.Frame(self, bd=0, highlightthickness=0)
        frame_toein = tk.Frame(self, bd=0, highlightthickness=0)

        if self.wcfg["show_caption"]:
            self.add_caption(frame=frame_camber, toggle="show_camber", value="camber")
            self.add_caption(frame=frame_toein, toggle="show_toe_in", value="toe in")

        if self.wcfg["show_camber"]:
            bar_style_camber = {"text":"n/a", "bd":0, "height":1, "width":5,
                                "padx":bar_padx, "pady":0, "font":font_wheel,
                                "fg":self.wcfg["font_color_camber"],
                                "bg":self.wcfg["bkg_color_camber"]}
            self.bar_camber_fl = tk.Label(frame_camber, bar_style_camber)
            self.bar_camber_fr = tk.Label(frame_camber, bar_style_camber)
            self.bar_camber_rl = tk.Label(frame_camber, bar_style_camber)
            self.bar_camber_rr = tk.Label(frame_camber, bar_style_camber)
            self.bar_camber_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_camber_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_camber_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_camber_rr.grid(row=2, column=1, padx=0, pady=0)

            frame_camber.grid(row=column_camber, column=0, padx=0, pady=(0,bar_gap))

        if self.wcfg["show_toe_in"]:
            bar_style_toein = {"text":"n/a", "bd":0, "height":1, "width":5,
                               "padx":bar_padx, "pady":0, "font":font_wheel,
                               "fg":self.wcfg["font_color_toe_in"],
                               "bg":self.wcfg["bkg_color_toe_in"]}
            self.bar_toein_fl = tk.Label(frame_toein, bar_style_toein)
            self.bar_toein_fr = tk.Label(frame_toein, bar_style_toein)
            self.bar_toein_rl = tk.Label(frame_toein, bar_style_toein)
            self.bar_toein_rr = tk.Label(frame_toein, bar_style_toein)
            self.bar_toein_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_toein_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_toein_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_toein_rr.grid(row=2, column=1, padx=0, pady=0)

            frame_toein.grid(row=column_toein, column=0, padx=0, pady=(0,bar_gap))

        # Last data
        self.last_camber = [-1] * 4
        self.last_toein = [-1] * 4

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Camber
            if self.wcfg["show_camber"]:
                # Read camber data
                camber = tuple(map(calc.rad2deg, read_data.camber()))

                self.update_wheel("camber_fl", camber[0], self.last_camber[0])
                self.update_wheel("camber_fr", camber[1], self.last_camber[1])
                self.update_wheel("camber_rl", camber[2], self.last_camber[2])
                self.update_wheel("camber_rr", camber[3], self.last_camber[3])
                self.last_camber = camber

            # Toe in
            if self.wcfg["show_toe_in"]:
                # Read toe data
                toein = tuple(map(calc.rad2deg, read_data.toe()))

                self.update_wheel("toein_fl", toein[0], self.last_toein[0])
                self.update_wheel("toein_fr", toein[1], self.last_toein[1])
                self.update_wheel("toein_rl", toein[2], self.last_toein[2])
                self.update_wheel("toein_rr", toein[3], self.last_toein[3])
                self.last_toein = toein

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_wheel(self, suffix, curr, last):
        """Wheel data"""
        if round(curr, 2) != round(last, 2):
            getattr(self, f"bar_{suffix}").config(text=f"{curr:+.02f}"[:5].rjust(5))
