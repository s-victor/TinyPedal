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
from ..load_func import module

WIDGET_NAME = "fuel"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config title & background
        self.title("TinyPedal - " + WIDGET_NAME.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color_cap = self.wcfg["font_color_caption"]
        bg_color_cap = self.wcfg["bkg_color_caption"]
        font_fuel = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])
        font_desc = tkfont.Font(family=self.wcfg["font_name"],
                                size=-int(self.wcfg["font_size"] * 0.8),
                                weight=self.wcfg["font_weight"])

        # Draw label
        if self.wcfg["show_caption"]:
            bar_style_desc = {"bd":0, "height":1, "padx":0, "pady":0,
                              "font":font_desc, "fg":fg_color_cap, "bg":bg_color_cap}
            self.bar_desc_1 = tk.Label(self, bar_style_desc, text="fuel")
            self.bar_desc_2 = tk.Label(self, bar_style_desc, text="refuel")
            self.bar_desc_3 = tk.Label(self, bar_style_desc, text="used")
            self.bar_desc_4 = tk.Label(self, bar_style_desc, text="laps")
            self.bar_desc_5 = tk.Label(self, bar_style_desc, text="mins")
            self.bar_desc_6 = tk.Label(self, bar_style_desc, text="pits")
            self.bar_desc_1.grid(row=0, column=0, padx=0, pady=0, sticky="we")
            self.bar_desc_2.grid(row=0, column=1, padx=0, pady=0, sticky="we")
            self.bar_desc_3.grid(row=0, column=2, padx=0, pady=0, sticky="we")
            self.bar_desc_4.grid(row=3, column=0, padx=0, pady=0, sticky="we")
            self.bar_desc_5.grid(row=3, column=1, padx=0, pady=0, sticky="we")
            self.bar_desc_6.grid(row=3, column=2, padx=0, pady=0, sticky="we")

        self.bar_fuel_1 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_fuel"],
                                   bg=self.wcfg["bkg_color_fuel"])
        self.bar_fuel_2 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_fuel"],
                                   bg=self.wcfg["bkg_color_fuel"])
        self.bar_fuel_3 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_consumption"],
                                   bg=self.wcfg["bkg_color_consumption"])
        self.bar_fuel_4 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_estimate"],
                                   bg=self.wcfg["bkg_color_estimate"])
        self.bar_fuel_5 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_estimate"],
                                   bg=self.wcfg["bkg_color_estimate"])
        self.bar_fuel_6 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=self.wcfg["font_color_pits"],
                                   bg=self.wcfg["bkg_color_pits"])
        self.bar_fuel_1.grid(row=1, column=0, padx=0, pady=0)
        self.bar_fuel_2.grid(row=1, column=1, padx=0, pady=0)
        self.bar_fuel_3.grid(row=1, column=2, padx=0, pady=0)
        self.bar_fuel_4.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_5.grid(row=2, column=1, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_6.grid(row=2, column=2, padx=0, pady=(bar_gap, 0))

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read fuel data from fuel usage module
            (amount_curr, amount_need, used_last, est_runlaps, est_runmins, pit_required
             ) = module.fuel_usage.output_data

            # Start updating
            # Low fuel warning
            lowfuel_color = self.color_lowfuel(est_runlaps)
            # Current fuel & total needed fuel
            self.bar_fuel_1.config(text=f"{amount_curr:.2f}", bg=lowfuel_color)
            self.bar_fuel_2.config(text=f"{min(max(amount_need, -999.9), 999.9):+0.1f}", bg=lowfuel_color)
            # Last lap fuel consumption
            self.bar_fuel_3.config(text=f"{used_last:.2f}")
            # Estimated laps & minutes current fuel can last
            self.bar_fuel_4.config(text=str(f"{min(est_runlaps, 9999):.1f}"))
            self.bar_fuel_5.config(text=str(f"{min(est_runmins, 9999):.1f}"))
            # Estimated pit stops
            self.bar_fuel_6.config(text=str(f"{min(max(pit_required, 0), 99.99):.2f}"))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def color_lowfuel(self, fuel):
        """Low fuel warning color"""
        if fuel > 2:
            color = self.wcfg["bkg_color_fuel"]
        else:
            color = self.wcfg["bkg_color_low_fuel"]
        return color
