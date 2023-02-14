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
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]

        # Config style & variable
        font_pres = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        column_tpres = self.wcfg["column_index_tyre_pressure"]
        column_tload = self.wcfg["column_index_tyre_load"]
        column_bpres = self.wcfg["column_index_brake_pressure"]

        # Draw label
        frame_tpres = tk.Frame(self, bd=0, highlightthickness=0)
        frame_tload = tk.Frame(self, bd=0, highlightthickness=0)
        frame_bpres = tk.Frame(self, bd=0, highlightthickness=0)

        if self.wcfg["show_caption"]:
            self.add_caption(frame=frame_tpres, toggle="show_tyre_pressure", value="tyre pres")
            self.add_caption(frame=frame_tload, toggle="show_tyre_load", value="tyre load")
            self.add_caption(frame=frame_bpres, toggle="show_brake_pressure", value="brake pres")

        if self.wcfg["show_tyre_pressure"]:
            bar_style_tpres = {"text":"n/a", "bd":0, "height":1, "width":4,
                               "padx":bar_padx, "pady":0, "font":font_pres,
                               "fg":self.wcfg["font_color_tyre_pressure"],
                               "bg":self.wcfg["bkg_color_tyre_pressure"]}
            self.bar_tpres_fl = tk.Label(frame_tpres, bar_style_tpres)
            self.bar_tpres_fr = tk.Label(frame_tpres, bar_style_tpres)
            self.bar_tpres_rl = tk.Label(frame_tpres, bar_style_tpres)
            self.bar_tpres_rr = tk.Label(frame_tpres, bar_style_tpres)
            self.bar_tpres_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_tpres_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_tpres_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_tpres_rr.grid(row=2, column=1, padx=0, pady=0)

        if self.wcfg["show_tyre_load"]:
            bar_style_tload = {"text":"n/a", "bd":0, "height":1, "width":4,
                               "padx":bar_padx, "pady":0, "font":font_pres,
                               "fg":self.wcfg["font_color_tyre_load"],
                               "bg":self.wcfg["bkg_color_tyre_load"]}
            self.bar_tload_fl = tk.Label(frame_tload, bar_style_tload)
            self.bar_tload_fr = tk.Label(frame_tload, bar_style_tload)
            self.bar_tload_rl = tk.Label(frame_tload, bar_style_tload)
            self.bar_tload_rr = tk.Label(frame_tload, bar_style_tload)
            self.bar_tload_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_tload_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_tload_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_tload_rr.grid(row=2, column=1, padx=0, pady=0)

        if self.wcfg["show_brake_pressure"]:
            bar_style_bpres = {"text":"n/a", "bd":0, "height":1, "width":4,
                               "padx":bar_padx, "pady":0, "font":font_pres,
                               "fg":self.wcfg["font_color_brake_pressure"],
                               "bg":self.wcfg["bkg_color_brake_pressure"]}
            self.bar_bpres_fl = tk.Label(frame_bpres, bar_style_bpres)
            self.bar_bpres_fr = tk.Label(frame_bpres, bar_style_bpres)
            self.bar_bpres_rl = tk.Label(frame_bpres, bar_style_bpres)
            self.bar_bpres_rr = tk.Label(frame_bpres, bar_style_bpres)
            self.bar_bpres_fl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_bpres_fr.grid(row=1, column=1, padx=0, pady=0)
            self.bar_bpres_rl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_bpres_rr.grid(row=2, column=1, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            if self.wcfg["show_tyre_pressure"]:
                frame_tpres.grid(row=column_tpres, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_tyre_load"]:
                frame_tload.grid(row=column_tload, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_brake_pressure"]:
                frame_bpres.grid(row=column_bpres, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            if self.wcfg["show_tyre_pressure"]:
                frame_tpres.grid(row=0, column=column_tpres, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_tyre_load"]:
                frame_tload.grid(row=0, column=column_tload, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_brake_pressure"]:
                frame_bpres.grid(row=0, column=column_bpres, padx=(0,bar_gap), pady=0)

        # Last data
        self.last_tpres = [None] * 4
        self.last_tload = [None] * 4
        self.last_bpres = [None] * 4

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Tyre pressure
            if self.wcfg["show_tyre_pressure"]:
                # Read tyre pressure data
                tpres = tuple(map(self.tyre_pressure_units, read_data.tyre_pressure()))

                self.update_text("tpres_fl", tpres[0], self.last_tpres[0])
                self.update_text("tpres_fr", tpres[1], self.last_tpres[1])
                self.update_text("tpres_rl", tpres[2], self.last_tpres[2])
                self.update_text("tpres_rr", tpres[3], self.last_tpres[3])
                self.last_tpres = tpres

            # Tyre load
            if self.wcfg["show_tyre_load"]:
                # Read tyre load data
                raw_load = read_data.tyre_load()

                if self.wcfg["show_tyre_load_ratio"]:
                    tload = tuple(map(self.tyre_load_ratio, raw_load, [sum(raw_load)]*4))
                else:
                    tload = tuple(map(self.tyre_load_newtons, raw_load))

                self.update_text("tload_fl", tload[0], self.last_tload[0])
                self.update_text("tload_fr", tload[1], self.last_tload[1])
                self.update_text("tload_rl", tload[2], self.last_tload[2])
                self.update_text("tload_rr", tload[3], self.last_tload[3])
                self.last_tload = tload

            # Brake pressure
            if self.wcfg["show_brake_pressure"]:
                # Read brake pressure data
                bpres = tuple(map(self.brake_pressure_units, read_data.brake_pressure()))

                self.update_text("bpres_fl", bpres[0], self.last_bpres[0])
                self.update_text("bpres_fr", bpres[1], self.last_bpres[1])
                self.update_text("bpres_rl", bpres[2], self.last_bpres[2])
                self.update_text("bpres_rr", bpres[3], self.last_bpres[3])
                self.last_bpres = bpres

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_text(self, suffix, curr, last):
        """Text"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(text=curr)

    # Additional methods
    @staticmethod
    def tyre_load_newtons(value):
        """Tyre load"""
        return f"{value:.0f}"

    @staticmethod
    def tyre_load_ratio(value, total):
        """Tyre load ratio"""
        return f"{calc.force_ratio(value, total):.01f}"

    def tyre_pressure_units(self, value):
        """Tyre pressure units"""
        if self.wcfg["tyre_pressure_unit"] == "0":
            return f"{value:.0f}"  # kPa
        if self.wcfg["tyre_pressure_unit"] == "1":
            return f"{calc.kpa2psi(value):.01f}"  # psi
        return f"{calc.kpa2bar(value):.02f}"  # bar

    @staticmethod
    def brake_pressure_units(value):
        """Brake pressure percentage"""
        return f"{value * 100:.01f}"
