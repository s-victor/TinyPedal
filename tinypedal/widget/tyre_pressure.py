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

WIDGET_NAME = "tyre_pressure"


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

        column_pres = self.wcfg["column_index_pressure"]
        column_load = self.wcfg["column_index_load"]

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_pres}

        frame_pres = tk.Frame(self, bd=0, highlightthickness=0)
        self.bar_pres_fl = tk.Label(frame_pres, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_fr = tk.Label(frame_pres, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rl = tk.Label(frame_pres, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_rr = tk.Label(frame_pres, bar_style, fg=fg_color_pres, bg=bg_color_pres)
        self.bar_pres_fl.grid(row=0, column=0, padx=0, pady=0)
        self.bar_pres_fr.grid(row=0, column=1, padx=0, pady=0)
        self.bar_pres_rl.grid(row=1, column=0, padx=0, pady=0)
        self.bar_pres_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["show_tyre_load"]:
            frame_load = tk.Frame(self, bd=0, highlightthickness=0)
            self.bar_load_fl = tk.Label(frame_load, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_fr = tk.Label(frame_load, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rl = tk.Label(frame_load, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_rr = tk.Label(frame_load, bar_style, fg=fg_color_load, bg=bg_color_load)
            self.bar_load_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_load_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_load_rl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_load_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            frame_pres.grid(row=column_pres, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_tyre_load"]:
                frame_load.grid(row=column_load, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            frame_pres.grid(row=0, column=column_pres, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_tyre_load"]:
                frame_load.grid(row=0, column=column_load, padx=(0,bar_gap), pady=0)

        # Last data
        self.last_pressure = [None] * 4
        self.last_load_d = [None] * 4

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read tyre pressure data
            pressure = tuple(map(self.pressure_units, read_data.tyre_pressure()))

            # Tyre pressure
            self.update_tyre("pres_fl", pressure[0], self.last_pressure[0])
            self.update_tyre("pres_fr", pressure[1], self.last_pressure[1])
            self.update_tyre("pres_rl", pressure[2], self.last_pressure[2])
            self.update_tyre("pres_rr", pressure[3], self.last_pressure[3])
            self.last_pressure = pressure

            # Tyre load
            if self.wcfg["show_tyre_load"]:
                # Read tyre load data
                raw_load = read_data.tyre_load()

                if self.wcfg["show_tyre_load_ratio"]:
                    load_d = tuple(map(self.tyre_load_ratio, raw_load, [sum(raw_load)]*4))
                else:
                    load_d = tuple(map(self.tyre_load_n, raw_load))

                self.update_tyre("load_fl", load_d[0], self.last_load_d[0])
                self.update_tyre("load_fr", load_d[1], self.last_load_d[1])
                self.update_tyre("load_rl", load_d[2], self.last_load_d[2])
                self.update_tyre("load_rr", load_d[3], self.last_load_d[3])
                self.last_load_d = load_d

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_tyre(self, suffix, curr, last):
        """Tyre pressure"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(text=curr)

    # Additional methods
    @staticmethod
    def tyre_load_n(value):
        """Tyre load"""
        return f"{value:.0f}"

    @staticmethod
    def tyre_load_ratio(value, total):
        """Tyre load ratio"""
        return f"{calc.force_ratio(value, total):.01f}"

    def pressure_units(self, pres):
        """Pressure units"""
        if self.wcfg["pressure_unit"] == "0":
            pressure = f"{pres:03.0f}"  # kPa
        elif self.wcfg["pressure_unit"] == "1":
            pressure = f"{calc.kpa2psi(pres):03.01f}"  # psi
        else:
            pressure = f"{calc.kpa2bar(pres):03.02f}"  # bar
        return pressure
