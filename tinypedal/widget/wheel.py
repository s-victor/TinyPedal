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

from tinypedal.__init__ import info
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "wheel"
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
        text_def = "n/a"
        fg_color = self.cfg["font_color"]
        bg_color = self.cfg["bkg_color"]
        fg_color_cap = self.cfg["font_color_caption"]
        bg_color_cap = self.cfg["bkg_color_caption"]
        font_wheel = tkfont.Font(family=self.cfg["font_name"],
                                 size=-self.cfg["font_size"],
                                 weight=self.cfg["font_weight"])
        font_desc = tkfont.Font(family=self.cfg["font_name"],
                                size=-int(self.cfg["font_size"] * 0.8),
                                weight=self.cfg["font_weight"])

        # Draw label
        if self.cfg["show_caption"]:
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

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:
            pidx = info.players_index

            # Read camber data
            (camber_fl, camber_fr, camber_rl, camber_rr
             ) = [f"{calc.rad2deg(data):+.2f}" for data in read_data.camber()]

            # Read toe data
            (toe_fl, toe_fr, toe_rl, toe_rr
             ) = [f"{calc.rad2deg(data):+.2f}" for data in read_data.toe()]

            # Read ride height & rake data
            (rideh_fl, rideh_fr, rideh_rl, rideh_rr, rake
             ) = [calc.meter2millmeter(data) for data in read_data.ride_height()]

            # Check isPlayer before update
            if pidx == info.players_index:

                # Camber update
                self.bar_camber_fl.config(text=camber_fl)
                self.bar_camber_fr.config(text=camber_fr)
                self.bar_camber_rl.config(text=camber_rl)
                self.bar_camber_rr.config(text=camber_rr)

                # Toe update
                self.bar_toe_fl.config(text=toe_fl)
                self.bar_toe_fr.config(text=toe_fr)
                self.bar_toe_rl.config(text=toe_rl)
                self.bar_toe_rr.config(text=toe_rr)

                # Ride height update
                self.bar_rideh_fl.config(text=f"{rideh_fl:+.1f}",
                                         bg=self.color_rideh(
                                            rideh_fl, self.cfg["rideheight_offset_front"]))
                self.bar_rideh_fr.config(text=f"{rideh_fr:+.1f}",
                                         bg=self.color_rideh(
                                            rideh_fr, self.cfg["rideheight_offset_front"]))
                self.bar_rideh_rl.config(text=f"{rideh_rl:+.1f}",
                                         bg=self.color_rideh(
                                            rideh_rl, self.cfg["rideheight_offset_front"]))
                self.bar_rideh_rr.config(text=f"{rideh_rr:+.1f}",
                                         bg=self.color_rideh(
                                            rideh_rr, self.cfg["rideheight_offset_front"]))

                # Rake update
                rake_angle = calc.rake2angle(rake, self.cfg["wheelbase"])

                self.bar_rake.config(text=f"{rake:+.1f}", bg=self.color_rideh(rake, 0))
                self.bar_rakeangle.config(text=f" {rake_angle:.2f}°", bg=self.color_rideh(rake, 0))

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    def color_rideh(self, height, offset):
        """Ride height indicator color"""
        if height > offset:
            color = self.cfg["bkg_color"]
        else:
            color = self.cfg["bkg_color_bottoming"]
        return color
