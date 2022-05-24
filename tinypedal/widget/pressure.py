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
Tyre Load & Pressure Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from tinypedal.__init__ import info
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "pressure"
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
        fg_color_load = self.cfg["font_color_load"]
        fg_color_pres = self.cfg["font_color_pressure"]
        bg_color_load = self.cfg["bkg_color_load"]
        bg_color_pres = self.cfg["bkg_color_pressure"]
        font_pres = tkfont.Font(family=self.cfg["font_name"],
                                size=-self.cfg["font_size"],
                                weight=self.cfg["font_weight"])

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_pres}

        self.bar_pres_fl = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_fr = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rl = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rr = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)

        if self.cfg["show_tyre_load"]:
            self.bar_load_fl = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_fr = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rl = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rr = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)

            if self.cfg["layout"] == "0":
                # Vertical layout, load above pressure
                self.bar_load_fl.grid(row=0, column=0, padx=0, pady=0)
                self.bar_load_fr.grid(row=0, column=1, padx=0, pady=0)
                self.bar_load_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
                self.bar_load_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
                self.bar_pres_fl.grid(row=2, column=0, padx=0, pady=0)
                self.bar_pres_fr.grid(row=2, column=1, padx=0, pady=0)
                self.bar_pres_rl.grid(row=3, column=0, padx=0, pady=0)
                self.bar_pres_rr.grid(row=3, column=1, padx=0, pady=0)
            elif self.cfg["layout"] == "1":
                # Vertical layout, pressure above load
                self.bar_pres_fl.grid(row=0, column=0, padx=0, pady=0)
                self.bar_pres_fr.grid(row=0, column=1, padx=0, pady=0)
                self.bar_pres_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
                self.bar_pres_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
                self.bar_load_fl.grid(row=2, column=0, padx=0, pady=0)
                self.bar_load_fr.grid(row=2, column=1, padx=0, pady=0)
                self.bar_load_rl.grid(row=3, column=0, padx=0, pady=0)
                self.bar_load_rr.grid(row=3, column=1, padx=0, pady=0)
            elif self.cfg["layout"] == "2":
                # Horizontal layout, pressure outside of load
                self.bar_pres_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
                self.bar_pres_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
                self.bar_pres_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
                self.bar_pres_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
                self.bar_load_fl.grid(row=0, column=1, padx=0, pady=0)
                self.bar_load_fr.grid(row=0, column=2, padx=0, pady=0)
                self.bar_load_rl.grid(row=1, column=1, padx=0, pady=0)
                self.bar_load_rr.grid(row=1, column=2, padx=0, pady=0)
            else:
                # Horizontal layout, load outside of pressure
                self.bar_load_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
                self.bar_load_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
                self.bar_load_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
                self.bar_load_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
                self.bar_pres_fl.grid(row=0, column=1, padx=0, pady=0)
                self.bar_pres_fr.grid(row=0, column=2, padx=0, pady=0)
                self.bar_pres_rl.grid(row=1, column=1, padx=0, pady=0)
                self.bar_pres_rr.grid(row=1, column=2, padx=0, pady=0)
        else:
            self.bar_pres_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_pres_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_pres_rl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_pres_rr.grid(row=1, column=1, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:
            pidx = info.players_index

            # Read tyre pressure data
            (pres_fl, pres_fr, pres_rl, pres_rr
             ) = [calc.kpa2psi(data, self.cfg["pressure_unit"])
                  for data in read_data.tyre_pres()]

            # Check isPlayer before update
            if pidx == info.players_index:

                # Tyre load & pressure update
                if self.cfg["show_tyre_load"]:
                    # Read tyre load data
                    raw_load_fl, raw_load_fr, raw_load_rl, raw_load_rr = read_data.tyre_load()

                    if self.cfg["show_tyre_load_ratio"]:
                        load_fl = calc.force_ratio(raw_load_fl, raw_load_fr)
                        load_fr = calc.force_ratio(raw_load_fr, raw_load_fl)
                        load_rl = calc.force_ratio(raw_load_rl, raw_load_rr)
                        load_rr = calc.force_ratio(raw_load_rr, raw_load_rl)

                        self.bar_load_fl.config(text=f"{load_fl:.1f}")
                        self.bar_load_fr.config(text=f"{load_fr:.1f}")
                        self.bar_load_rl.config(text=f"{load_rl:.1f}")
                        self.bar_load_rr.config(text=f"{load_rr:.1f}")
                    else:
                        self.bar_load_fl.config(text=f"{raw_load_fl:.0f}")
                        self.bar_load_fr.config(text=f"{raw_load_fr:.0f}")
                        self.bar_load_rl.config(text=f"{raw_load_rl:.0f}")
                        self.bar_load_rr.config(text=f"{raw_load_rr:.0f}")

                self.bar_pres_fl.config(text=pres_fl)
                self.bar_pres_fr.config(text=pres_fr)
                self.bar_pres_rl.config(text=pres_rl)
                self.bar_pres_rr.config(text=pres_rr)

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
