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
Tyre Wear Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from tinypedal.__init__ import cfg
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "wear"
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
        bkg_color = self.cfg["bkg_color"]
        font_wear = tkfont.Font(family=self.cfg["font_name"],
                                size=-self.cfg["font_size"],
                                weight=self.cfg["font_weight"])

        self.start_last = 0.0  # last lap start time
        self.wear_last = [0,0,0,0]  # remaining tyre wear from last lap
        self.wear_per = [0,0,0,0]  # tyre wear of last lap

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_wear, "fg":fg_color}

        self.bar_wear_fl = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wear_fr = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wear_rl = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wear_rr = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wearlast_fl = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wearlast_fr = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wearlast_rl = tk.Label(self, bar_style, bg=bkg_color)
        self.bar_wearlast_rr = tk.Label(self, bar_style, bg=bkg_color)

        if self.cfg["layout"] == "0":
            # Vertical layout, wear above last lap wear
            self.bar_wear_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_wear_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_wearlast_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_wearlast_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_wearlast_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_wearlast_rr.grid(row=3, column=1, padx=0, pady=0)
        elif self.cfg["layout"] == "1":
            # Vertical layout,  last lap wear above wear
            self.bar_wearlast_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_wearlast_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wearlast_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_wearlast_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_wear_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_wear_rr.grid(row=3, column=1, padx=0, pady=0)
        elif self.cfg["layout"] == "2":
            # Horizontal layout, last lap wear outside of wear
            self.bar_wearlast_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wearlast_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wearlast_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wearlast_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wear_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wear_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_wear_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_wear_rr.grid(row=1, column=2, padx=0, pady=0)
        else:
            # Horizontal layout, wear outside of last lap wear
            self.bar_wear_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wear_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wear_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wear_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wearlast_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wearlast_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_wearlast_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_wearlast_rr.grid(row=1, column=2, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read tyre wear data
            start_curr, wear_curr = read_data.wear()

            # Check isPlayer before update
            if read_data.is_local_player():

                # Tyre wear update
                self.bar_wear_fl.config(text=f"{wear_curr[0]:.1f}",
                                        fg=self.color_wear(wear_curr[0]))
                self.bar_wear_fr.config(text=f"{wear_curr[1]:.1f}",
                                        fg=self.color_wear(wear_curr[1]))
                self.bar_wear_rl.config(text=f"{wear_curr[2]:.1f}",
                                        fg=self.color_wear(wear_curr[2]))
                self.bar_wear_rr.config(text=f"{wear_curr[3]:.1f}",
                                        fg=self.color_wear(wear_curr[3]))

                # Last lap tyre wear update
                if start_curr != self.start_last:  # time stamp difference
                    # Calculate last lap tyre wear
                    self.wear_per[0] = max(self.wear_last[0] - wear_curr[0], 0)
                    self.wear_per[1] = max(self.wear_last[1] - wear_curr[1], 0)
                    self.wear_per[2] = max(self.wear_last[2] - wear_curr[2], 0)
                    self.wear_per[3] = max(self.wear_last[3] - wear_curr[3], 0)
                    self.wear_last = wear_curr
                    self.start_last = start_curr  # reset time stamp counter

                    self.bar_wearlast_fl.config(text=f"{self.wear_per[0]:.2f}",
                                                fg=self.color_wear_last(self.wear_per[0]))
                    self.bar_wearlast_fr.config(text=f"{self.wear_per[1]:.2f}",
                                                fg=self.color_wear_last(self.wear_per[1]))
                    self.bar_wearlast_rl.config(text=f"{self.wear_per[2]:.2f}",
                                                fg=self.color_wear_last(self.wear_per[2]))
                    self.bar_wearlast_rr.config(text=f"{self.wear_per[3]:.2f}",
                                                fg=self.color_wear_last(self.wear_per[3]))

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    @staticmethod
    def color_wear(tyre_wear):
        """Tyre wear color"""
        if tyre_wear < 30:
            color = "#F44"  # red
        elif 30 <= tyre_wear < 60:
            color = "#F84"  # orange
        elif 60 <= tyre_wear < 80:
            color = "#FF4"  # yellow
        else:
            color = "#4F4"  # green
        return color

    @staticmethod
    def color_wear_last(tyre_wear):
        """Last lap tyre wear color"""
        if tyre_wear >= 3:
            color = "#F44"  # red
        elif 2 <= tyre_wear < 3:
            color = "#F84"  # orange
        elif 1 <= tyre_wear < 2:
            color = "#FF4"  # yellow
        else:
            color = "#FFF"  # white
        return color
