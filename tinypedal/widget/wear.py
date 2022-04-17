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

import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Tyre Wear Widget")
        self.attributes("-alpha", cfg.wear["opacity"])

        # Config size & position
        bar_gap = cfg.wear["bar_gap"]
        self.geometry(f"+{cfg.wear['position_x']}+{cfg.wear['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color = cfg.wear["font_color"]
        bkg_color = cfg.wear["bkg_color"]
        font_wear = tkfont.Font(family=cfg.wear["font_name"],
                                size=-cfg.wear["font_size"],
                                weight=cfg.wear["font_weight"])

        self.start_last = 0.0  # last lap start time
        self.wear_fl_last = 0  # remaining tyre wear from last lap
        self.wear_fr_last = 0
        self.wear_rl_last = 0
        self.wear_rr_last = 0
        self.wear_fl_per = 0  # tyre wear of last lap
        self.wear_fr_per = 0
        self.wear_rl_per = 0
        self.wear_rr_per = 0

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

        if cfg.wear["layout"] == "0":
            # Vertical layout, wear above last lap wear
            self.bar_wear_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_wear_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_wearlast_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_wearlast_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_wearlast_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_wearlast_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.wear["layout"] == "1":
            # Vertical layout,  last lap wear above wear
            self.bar_wearlast_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_wearlast_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wearlast_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_wearlast_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_wear_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_wear_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.wear["layout"] == "2":
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

        self.update_wear()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.wear["position_x"] = str(self.winfo_x())
        cfg.wear["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_wear(self):
        """Update wear

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.wear["enable"]:
            # Read tyre wear data
            wear_fl, wear_fr, wear_rl, wear_rr = read_data.wear()
            start_curr = read_data.timing()[0]

            # Calculate last lap tyre wear
            if start_curr != self.start_last:  # time stamp difference
                self.wear_fl_per = max(self.wear_fl_last - wear_fl, 0)
                self.wear_fr_per = max(self.wear_fr_last - wear_fr, 0)
                self.wear_rl_per = max(self.wear_rl_last - wear_rl, 0)
                self.wear_rr_per = max(self.wear_rr_last - wear_rr, 0)
                self.start_last = start_curr  # reset time stamp counter
                self.wear_fl_last = wear_fl
                self.wear_fr_last = wear_fr
                self.wear_rl_last = wear_rl
                self.wear_rr_last = wear_rr

            # Tyre wear update
            self.bar_wear_fl.config(text=f"{wear_fl:.1f}", fg=self.color_wear(wear_fl))
            self.bar_wear_fr.config(text=f"{wear_fr:.1f}", fg=self.color_wear(wear_fr))
            self.bar_wear_rl.config(text=f"{wear_rl:.1f}", fg=self.color_wear(wear_rl))
            self.bar_wear_rr.config(text=f"{wear_rr:.1f}", fg=self.color_wear(wear_rr))

            # Last lap tyre wear update
            self.bar_wearlast_fl.config(text=f"{self.wear_fl_per:.2f}",
                                        fg=self.color_wear_last(self.wear_fl_per))
            self.bar_wearlast_fr.config(text=f"{self.wear_fr_per:.2f}",
                                        fg=self.color_wear_last(self.wear_fr_per))
            self.bar_wearlast_rl.config(text=f"{self.wear_rl_per:.2f}",
                                        fg=self.color_wear_last(self.wear_rl_per))
            self.bar_wearlast_rr.config(text=f"{self.wear_rr_per:.2f}",
                                        fg=self.color_wear_last(self.wear_rr_per))

        # Update rate
        self.after(cfg.wear["update_delay"], self.update_wear)

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
