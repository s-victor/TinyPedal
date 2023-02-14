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
Fuel Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "fuel"


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
        font_fuel = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        # Draw label
        if self.wcfg["show_caption"]:
            font_desc = tkfont.Font(family=self.wcfg["font_name"],
                                    size=-int(self.wcfg["font_size"] * 0.8),
                                    weight=self.wcfg["font_weight"])
            bar_style_desc = {"bd":0, "height":1, "font":font_desc, "padx":0, "pady":0,
                              "fg":self.wcfg["font_color_caption"],
                              "bg":self.wcfg["bkg_color_caption"]}
            bar_desc_curr = tk.Label(self, bar_style_desc, text="fuel")
            bar_desc_need = tk.Label(self, bar_style_desc, text="refuel")
            bar_desc_used = tk.Label(self, bar_style_desc, text="used")
            bar_desc_laps = tk.Label(self, bar_style_desc, text="laps")
            bar_desc_mins = tk.Label(self, bar_style_desc, text="mins")
            bar_desc_pits = tk.Label(self, bar_style_desc, text="pits")
            bar_desc_curr.grid(row=0, column=0, padx=0, pady=0, sticky="we")
            bar_desc_need.grid(row=0, column=1, padx=0, pady=0, sticky="we")
            bar_desc_used.grid(row=0, column=2, padx=0, pady=0, sticky="we")
            bar_desc_laps.grid(row=3, column=0, padx=0, pady=0, sticky="we")
            bar_desc_mins.grid(row=3, column=1, padx=0, pady=0, sticky="we")
            bar_desc_pits.grid(row=3, column=2, padx=0, pady=0, sticky="we")

        bar_style_fuel = {"bd":0, "width":6, "height":1, "padx":bar_padx, "pady":0,
                          "font":font_fuel, "text":"-.--"}

        self.bar_fuel_curr = tk.Label(self, bar_style_fuel,
                                      fg=self.wcfg["font_color_fuel"],
                                      bg=self.wcfg["bkg_color_fuel"])
        self.bar_fuel_need = tk.Label(self, bar_style_fuel,
                                      fg=self.wcfg["font_color_fuel"],
                                      bg=self.wcfg["bkg_color_fuel"])
        self.bar_fuel_used = tk.Label(self, bar_style_fuel, width=5,
                                      fg=self.wcfg["font_color_consumption"],
                                      bg=self.wcfg["bkg_color_consumption"])
        self.bar_fuel_laps = tk.Label(self, bar_style_fuel,
                                      fg=self.wcfg["font_color_estimate"],
                                      bg=self.wcfg["bkg_color_estimate"])
        self.bar_fuel_mins = tk.Label(self, bar_style_fuel,
                                      fg=self.wcfg["font_color_estimate"],
                                      bg=self.wcfg["bkg_color_estimate"])
        self.bar_fuel_pits = tk.Label(self, bar_style_fuel, width=5,
                                      fg=self.wcfg["font_color_pits"],
                                      bg=self.wcfg["bkg_color_pits"])
        self.bar_fuel_curr.grid(row=1, column=0, padx=0, pady=0)
        self.bar_fuel_need.grid(row=1, column=1, padx=0, pady=0)
        self.bar_fuel_used.grid(row=1, column=2, padx=0, pady=0)
        self.bar_fuel_laps.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_mins.grid(row=2, column=1, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_pits.grid(row=2, column=2, padx=0, pady=(bar_gap, 0))

        # Last data
        self.last_amount_curr = None
        self.last_amount_need = None
        self.last_used_last = None
        self.last_est_runlaps = None
        self.last_est_runmins = None
        self.last_pit_required = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read fuel data from fuel usage module
            (amount_curr, amount_need, used_last, est_runlaps, est_runmins, pit_required
             ) = module.fuel_usage.output_data

            # Current remaining fuel
            amount_curr = f"{amount_curr:.2f}"
            self.update_fuel_data("curr", amount_curr, self.last_amount_curr, est_runlaps)
            self.last_amount_curr = amount_curr

            # Total needed fuel
            amount_need = f"{min(max(amount_need, -999.9), 999.9):+0.1f}"
            self.update_fuel_data("need", amount_need, self.last_amount_need, est_runlaps)
            self.last_amount_need = amount_need

            # Estimated fuel consumption
            used_last = f"{used_last:.2f}"
            self.update_fuel_data("used", used_last, self.last_used_last)
            self.last_used_last = used_last

            # Estimated laps current fuel can last
            est_runlaps = f"{min(est_runlaps, 9999):.1f}"
            self.update_fuel_data("laps", est_runlaps, self.last_est_runlaps)
            self.last_est_runlaps = est_runlaps

            # Estimated minutes current fuel can last
            est_runmins = f"{min(est_runmins, 9999):.1f}"
            self.update_fuel_data("mins", est_runmins, self.last_est_runmins)
            self.last_est_runmins = est_runmins

            # Estimated pitstops required to finish race
            pit_required = f"{min(max(pit_required, 0), 99.99):.2f}"
            self.update_fuel_data("pits", pit_required, self.last_pit_required)
            self.last_pit_required = pit_required

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_fuel_data(self, suffix, curr, last, state=None):
        """Update fuel data"""
        if curr != last:
            if state:  # low fuel warning
                getattr(self, f"bar_fuel_{suffix}").config(text=curr, bg=self.color_lowfuel(state))
            else:
                getattr(self, f"bar_fuel_{suffix}").config(text=curr)

    # Additional methods
    def color_lowfuel(self, fuel):
        """Low fuel warning color"""
        if fuel > self.wcfg["low_fuel_lap_threshold"]:
            color = self.wcfg["bkg_color_fuel"]
        else:
            color = self.wcfg["bkg_color_low_fuel"]
        return color
