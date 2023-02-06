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

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "pressure"


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
        fg_color_load = self.wcfg["font_color_load"]
        fg_color_pres = self.wcfg["font_color_pressure"]
        bg_color_load = self.wcfg["bkg_color_load"]
        bg_color_pres = self.wcfg["bkg_color_pressure"]
        font_pres = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_pres}

        self.bar_pres_fl = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_fr = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rl = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rr = tk.Label(self, bar_style, fg=fg_color_pres, bg=bg_color_pres)

        if self.wcfg["show_tyre_load"]:
            self.bar_load_fl = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_fr = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rl = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rr = tk.Label(self, bar_style, fg=fg_color_load, bg=bg_color_load)

            if self.wcfg["layout"] == "0":
                # Vertical layout, load above pressure
                self.bar_load_fl.grid(row=0, column=0, padx=0, pady=0)
                self.bar_load_fr.grid(row=0, column=1, padx=0, pady=0)
                self.bar_load_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
                self.bar_load_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
                self.bar_pres_fl.grid(row=2, column=0, padx=0, pady=0)
                self.bar_pres_fr.grid(row=2, column=1, padx=0, pady=0)
                self.bar_pres_rl.grid(row=3, column=0, padx=0, pady=0)
                self.bar_pres_rr.grid(row=3, column=1, padx=0, pady=0)
            elif self.wcfg["layout"] == "1":
                # Vertical layout, pressure above load
                self.bar_pres_fl.grid(row=0, column=0, padx=0, pady=0)
                self.bar_pres_fr.grid(row=0, column=1, padx=0, pady=0)
                self.bar_pres_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
                self.bar_pres_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
                self.bar_load_fl.grid(row=2, column=0, padx=0, pady=0)
                self.bar_load_fr.grid(row=2, column=1, padx=0, pady=0)
                self.bar_load_rl.grid(row=3, column=0, padx=0, pady=0)
                self.bar_load_rr.grid(row=3, column=1, padx=0, pady=0)
            elif self.wcfg["layout"] == "2":
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
        if read_data.state() and self.wcfg["enable"]:

            # Read tyre pressure data
            pressure = tuple(map(self.format_pressure, read_data.tyre_pressure()))

            # Start updating
            # Tyre load & pressure update
            if self.wcfg["show_tyre_load"]:
                # Read tyre load data
                raw_load = read_data.tyre_load()

                if self.wcfg["show_tyre_load_ratio"]:
                    load_ratio = [calc.force_ratio(raw_load[0], raw_load[1]),
                                  calc.force_ratio(raw_load[1], raw_load[0]),
                                  calc.force_ratio(raw_load[2], raw_load[3]),
                                  calc.force_ratio(raw_load[3], raw_load[2])]

                    self.bar_load_fl.config(text=f"{load_ratio[0]:.1f}")
                    self.bar_load_fr.config(text=f"{load_ratio[1]:.1f}")
                    self.bar_load_rl.config(text=f"{load_ratio[2]:.1f}")
                    self.bar_load_rr.config(text=f"{load_ratio[3]:.1f}")
                else:
                    self.bar_load_fl.config(text=f"{raw_load[0]:.0f}")
                    self.bar_load_fr.config(text=f"{raw_load[1]:.0f}")
                    self.bar_load_rl.config(text=f"{raw_load[2]:.0f}")
                    self.bar_load_rr.config(text=f"{raw_load[3]:.0f}")

            self.bar_pres_fl.config(text=pressure[0])
            self.bar_pres_fr.config(text=pressure[1])
            self.bar_pres_rl.config(text=pressure[2])
            self.bar_pres_rr.config(text=pressure[3])

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def format_pressure(self, pres):
        """Format pressure"""
        if self.wcfg["pressure_unit"] == "0":
            pressure = f"{pres:03.0f}"  # kPa
        elif self.wcfg["pressure_unit"] == "1":
            pressure = f"{calc.kpa2psi(pres):03.01f}"  # psi
        else:
            pressure = f"{calc.kpa2bar(pres):03.02f}"  # bar
        return pressure
