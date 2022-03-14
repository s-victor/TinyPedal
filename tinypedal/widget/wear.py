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
Tyre Wear & Pressure Widget
"""

import tkinter as tk
import tkinter.font as tkfont

import tinypedal.calculation as calc
from tinypedal.base import cfg, read_data, Widget, MouseEvent


class Wear(Widget, MouseEvent):
    """Draw wear widget"""

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
        fg_color_pres = cfg.wear["font_color_pressure"]
        bg_color_wear = cfg.wear["bkg_color_wear"]
        bg_color_pres = cfg.wear["bkg_color_pressure"]
        font_wear = tkfont.Font(family=cfg.wear["font_name"],
                                size=-cfg.wear["font_size"],
                                weight=cfg.wear["font_weight"])

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_wear, "fg":fg_color_pres}

        self.bar_wear_fl = tk.Label(self, bar_style, bg=bg_color_wear)
        self.bar_wear_fr = tk.Label(self, bar_style, bg=bg_color_wear)
        self.bar_wear_rl = tk.Label(self, bar_style, bg=bg_color_wear)
        self.bar_wear_rr = tk.Label(self, bar_style, bg=bg_color_wear)
        self.bar_pres_fl = tk.Label(self, bar_style, bg=bg_color_pres)
        self.bar_pres_fr = tk.Label(self, bar_style, bg=bg_color_pres)
        self.bar_pres_rl = tk.Label(self, bar_style, bg=bg_color_pres)
        self.bar_pres_rr = tk.Label(self, bar_style, bg=bg_color_pres)

        if cfg.wear["layout"] == "0":
            # Vertical layout, wear above pressure
            self.bar_wear_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_wear_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_pres_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_pres_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_pres_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_pres_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.wear["layout"] == "1":
            # Vertical layout, pressure above wear
            self.bar_pres_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_pres_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_pres_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_pres_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_wear_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_wear_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_wear_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_wear_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.wear["layout"] == "2":
            # Horizontal layout, pressure outside of wear
            self.bar_pres_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_pres_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_pres_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_pres_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wear_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_wear_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_wear_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_wear_rr.grid(row=1, column=2, padx=0, pady=0)
        else:
            # Horizontal layout, wear outside of pressure
            self.bar_wear_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wear_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_wear_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_wear_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_pres_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_pres_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_pres_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_pres_rr.grid(row=1, column=2, padx=0, pady=0)

        self.update_wear()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.load()
        cfg.wear["position_x"] = str(self.winfo_x())
        cfg.wear["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_wear(self):
        """Update wear

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.wear["enable"]:
            # Read tyre wear & pressure data
            wear_fl, wear_fr, wear_rl, wear_rr = read_data.wear()

            (pres_fl, pres_fr, pres_rl, pres_rr
             ) = [calc.kpa2psi(data, cfg.wear["pressure_unit"]) for data in read_data.pressure()]

            # Tyre wear & pressure update
            self.bar_wear_fl.config(text=f"{wear_fl:.1f}", fg=self.color_wear(wear_fl))
            self.bar_wear_fr.config(text=f"{wear_fr:.1f}", fg=self.color_wear(wear_fr))
            self.bar_wear_rl.config(text=f"{wear_rl:.1f}", fg=self.color_wear(wear_rl))
            self.bar_wear_rr.config(text=f"{wear_rr:.1f}", fg=self.color_wear(wear_rr))
            self.bar_pres_fl.config(text=pres_fl)
            self.bar_pres_fr.config(text=pres_fr)
            self.bar_pres_rl.config(text=pres_rl)
            self.bar_pres_rr.config(text=pres_rr)

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
