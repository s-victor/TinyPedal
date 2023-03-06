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
Engine Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "engine"


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
        text_def = "n/a"
        font_engine = tkfont.Font(family=self.wcfg["font_name"],
                                  size=-self.wcfg["font_size"],
                                  weight=self.wcfg["font_weight"])

        column_oil = self.wcfg["column_index_oil"]
        column_water = self.wcfg["column_index_water"]
        column_turbo = self.wcfg["column_index_turbo"]
        column_rpm = self.wcfg["column_index_rpm"]

        # Draw label
        bar_style  = {"text":text_def, "bd":0, "height":1, "width":8,
                      "padx":bar_padx, "pady":0, "font":font_engine}

        if self.wcfg["show_temperature"]:
            self.bar_oil = tk.Label(self, bar_style,
                                    fg=self.wcfg["font_color_oil"],
                                    bg=self.wcfg["bkg_color_oil"])
            self.bar_water = tk.Label(self, bar_style,
                                      fg=self.wcfg["font_color_water"],
                                      bg=self.wcfg["bkg_color_water"])

        if self.wcfg["show_turbo_pressure"]:
            self.bar_turbo = tk.Label(self, bar_style,
                                      fg=self.wcfg["font_color_turbo"],
                                      bg=self.wcfg["bkg_color_turbo"])
        if self.wcfg["show_rpm"]:
            self.bar_rpm = tk.Label(self, bar_style,
                                    fg=self.wcfg["font_color_rpm"],
                                    bg=self.wcfg["bkg_color_rpm"])

        if self.wcfg["layout"] == "0":
            # Vertical layout
            if self.wcfg["show_temperature"]:
                self.bar_oil.grid(row=column_oil, column=0, padx=0, pady=(0, bar_gap))
                self.bar_water.grid(row=column_water, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_turbo_pressure"]:
                self.bar_turbo.grid(row=column_turbo, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_rpm"]:
                self.bar_rpm.grid(row=column_rpm, column=0, padx=0, pady=(0, bar_gap))
        else:
            # Horizontal layout
            if self.wcfg["show_temperature"]:
                self.bar_oil.grid(row=0, column=column_oil, padx=(0, bar_gap), pady=0)
                self.bar_water.grid(row=0, column=column_water, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_turbo_pressure"]:
                self.bar_turbo.grid(row=0, column=column_turbo, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_rpm"]:
                self.bar_rpm.grid(row=0, column=column_rpm, padx=(0, bar_gap), pady=0)

        # Last data
        self.last_temp_oil = None
        self.last_temp_water = None
        self.last_e_turbo = None
        self.last_e_rpm = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read Engine data
            temp_oil, temp_water, e_turbo, e_rpm = read_data.engine()

            if self.wcfg["show_temperature"]:
                # Oil temperature
                temp_oil = round(temp_oil, 1)
                self.update_oil(temp_oil, self.last_temp_oil)
                self.last_temp_oil = temp_oil

                # Water temperature
                temp_water = round(temp_water, 1)
                self.update_water(temp_water, self.last_temp_water)
                self.last_temp_water = temp_water

            # Turbo pressure
            if self.wcfg["show_turbo_pressure"]:
                self.update_turbo(e_turbo, self.last_e_turbo)
                self.last_e_turbo = e_turbo

            # Engine RPM
            if self.wcfg["show_rpm"]:
                self.update_rpm(e_rpm, self.last_e_rpm)
                self.last_e_rpm = e_rpm

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_oil(self, curr, last):
        """Oil temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_oil"]:
                bgcolor = self.wcfg["bkg_color_oil"]
            else:
                bgcolor = self.wcfg["warning_color_overheat"]

            if self.wcfg["temp_unit"] == "1":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_oil.config(text=f"O{format_text}", bg=bgcolor)

    def update_water(self, curr, last):
        """Water temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_water"]:
                bgcolor = self.wcfg["bkg_color_water"]
            else:
                bgcolor = self.wcfg["warning_color_overheat"]

            if self.wcfg["temp_unit"] == "1":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_water.config(text=f"W{format_text}", bg=bgcolor)

    def update_turbo(self, curr, last):
        """Turbo pressure"""
        if curr != last:
            self.bar_turbo.config(text=self.pressure_units(curr * 0.001))

    def update_rpm(self, curr, last):
        """Engine RPM"""
        if curr != last:
            self.bar_rpm.config(text=f"{curr: =05.0f}rpm")

    # Additional methods
    def pressure_units(self, pres):
        """Pressure units"""
        if self.wcfg["turbo_pressure_unit"] == "0":
            return f"{calc.kpa2bar(pres):03.03f}bar"
        if self.wcfg["turbo_pressure_unit"] == "1":
            return f"{calc.kpa2psi(pres):03.02f}psi"
        return f"{pres:03.01f}kPa"
