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

import math
import tkinter as tk
import tkinter.font as tkfont

from tinypedal.__init__ import cfg
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import delta_time, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "fuel"
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
        fg_color_cap = self.cfg["font_color_caption"]
        bg_color_cap = self.cfg["bkg_color_caption"]
        font_fuel = tkfont.Font(family=self.cfg["font_name"],
                                size=-self.cfg["font_size"],
                                weight=self.cfg["font_weight"])
        font_desc = tkfont.Font(family=self.cfg["font_name"],
                                size=-int(self.cfg["font_size"] * 0.8),
                                weight=self.cfg["font_weight"])

        self.start_last = 0.0  # last lap start time
        self.amount_last = 0.0  # total fuel at end of last lap
        self.amount_need = 0.0  # total additional fuel required to finish race
        self.used_last = self.cfg["fuel_consumption"]  # last lap fuel consumption
        self.est_runlaps = 0.0  # estimate laps current fuel can last
        self.est_runmins = 0.0  # estimate minutes current fuel can last
        self.pit_required = 0.0  # minimum pit stops to finish race
        self.checked = False

        # Draw label
        if self.cfg["show_caption"]:
            bar_style_desc = {"bd":0, "height":1, "padx":0, "pady":0,
                              "font":font_desc, "fg":fg_color_cap, "bg":bg_color_cap}
            self.bar_desc_1 = tk.Label(self, bar_style_desc, text="fuel")
            self.bar_desc_2 = tk.Label(self, bar_style_desc, text="require")
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
                                   fg=self.cfg["font_color_fuel"],
                                   bg=self.cfg["bkg_color_fuel"])
        self.bar_fuel_2 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.cfg["font_color_fuel"],
                                   bg=self.cfg["bkg_color_fuel"])
        self.bar_fuel_3 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=self.cfg["font_color_consumption"],
                                   bg=self.cfg["bkg_color_consumption"])
        self.bar_fuel_4 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.cfg["font_color_estimate"],
                                   bg=self.cfg["bkg_color_estimate"])
        self.bar_fuel_5 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=self.cfg["font_color_estimate"],
                                   bg=self.cfg["bkg_color_estimate"])
        self.bar_fuel_6 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=self.cfg["font_color_pits"],
                                   bg=self.cfg["bkg_color_pits"])
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
        if read_data.state() and self.cfg["enable"]:

            # Save switch
            if not self.checked:
                self.checked = True

            # Read fuel data
            start_curr, laps_total, laps_left, time_left, amount_curr, capacity = read_data.fuel()

            # Read last laptime from delta module
            laptime_last = delta_time.output_data[1]

            # Check isPlayer before update
            if read_data.is_local_player():

                # Calc last lap fuel consumption
                if start_curr != self.start_last:  # time stamp difference
                    if start_curr > self.start_last:
                        # Calc last laptime from lap difference to bypass empty invalid laptime
                        self.used_last = max(self.amount_last - amount_curr, 0)
                    if self.used_last == 0:
                        self.used_last = self.cfg["fuel_consumption"]
                    self.amount_last = amount_curr  # reset fuel counter
                    self.start_last = start_curr  # reset time stamp counter

                # Estimate laps current fuel can last
                if self.used_last != 0:
                    # Total current fuel / last lap fuel consumption
                    self.est_runlaps = amount_curr / self.used_last
                else:
                    self.est_runlaps = 0

                # Estimate minutes current fuel can last
                self.est_runmins = self.est_runlaps * laptime_last / 60

                # Total additional fuel required to finish race
                if laps_total < 100000:  # detected lap type race
                    # Total laps left * last lap fuel consumption
                    self.amount_need = laps_left * self.used_last - amount_curr
                else:  # detected time type race
                    # Time left / last laptime * last lap fuel consumption - total current fuel
                    self.amount_need = (math.ceil(time_left / (laptime_last + 0.001) + 0.001)
                                        * self.used_last - amount_curr)

                # Minimum required pitstops to finish race
                self.pit_required = min(max(self.amount_need / (capacity + 0.001), 0), 99.99)

                amount_curr_d = calc.conv_fuel(amount_curr, self.cfg["fuel_unit"])
                amount_need_d = calc.conv_fuel(min(max(self.amount_need, -999.9), 999.9),
                                               self.cfg["fuel_unit"])
                used_last_d = calc.conv_fuel(self.used_last, self.cfg["fuel_unit"])

                # Low fuel warning
                lowfuel_color = self.color_lowfuel(self.est_runlaps)
                # Current fuel & total needed fuel
                self.bar_fuel_1.config(text=f"{amount_curr_d:.2f}", bg=lowfuel_color)
                self.bar_fuel_2.config(text=f"{amount_need_d:+0.1f}", bg=lowfuel_color)
                # Last lap fuel consumption
                self.bar_fuel_3.config(text=f"{used_last_d:.2f}")
                # Estimated laps & minutes current fuel can last
                self.bar_fuel_4.config(text=str(f"{self.est_runlaps:.1f}"))
                self.bar_fuel_5.config(text=str(f"{self.est_runmins:.1f}"))
                # Estimated pit stops
                self.bar_fuel_6.config(text=str(f"{self.pit_required:.2f}"))

        else:
            if self.checked:
                self.checked = False
                self.cfg["fuel_consumption"] = round(self.used_last, 6)
                cfg.save()

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    def color_lowfuel(self, fuel):
        """Low fuel warning color"""
        if fuel > 2:
            color = self.cfg["bkg_color_fuel"]
        else:
            color = self.cfg["bkg_color_low_fuel"]
        return color
