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

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Fuel Widget")
        self.attributes("-alpha", cfg.fuel["opacity"])

        # Config size & position
        bar_gap = cfg.fuel["bar_gap"]
        self.geometry(f"+{cfg.fuel['position_x']}+{cfg.fuel['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color_cap = cfg.fuel["font_color_caption"]
        bg_color_cap = cfg.fuel["bkg_color_caption"]
        font_fuel = tkfont.Font(family=cfg.fuel["font_name"],
                                size=-cfg.fuel["font_size"],
                                weight=cfg.fuel["font_weight"])
        font_desc = tkfont.Font(family=cfg.fuel["font_name"],
                                size=-int(cfg.fuel["font_size"] * 0.8),
                                weight=cfg.fuel["font_weight"])

        self.start_last = 0.0  # last lap start time
        self.laptime_last = 0.0  # last lap time calculated from time stamp difference
        self.amount_last = 0.0  # total fuel at end of last lap
        self.amount_need = 0.0  # total additional fuel required to finish race
        self.used_last = 0.0  # last lap fuel consumption
        self.est_runlaps = 0.0  # estimate laps current fuel can last
        self.est_runmins = 0.0  # estimate minutes current fuel can last
        self.pit_required = 0.0  # minimum pit stops to finish race

        # Draw label
        if cfg.fuel["show_caption"]:
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
                                   fg=cfg.fuel["font_color_fuel"],
                                   bg=cfg.fuel["bkg_color_fuel"])
        self.bar_fuel_2 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=cfg.fuel["font_color_fuel"],
                                   bg=cfg.fuel["bkg_color_fuel"])
        self.bar_fuel_3 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=cfg.fuel["font_color_consumption"],
                                   bg=cfg.fuel["bkg_color_consumption"])
        self.bar_fuel_4 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=cfg.fuel["font_color_estimate"],
                                   bg=cfg.fuel["bkg_color_estimate"])
        self.bar_fuel_5 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=7, padx=0, pady=0, bd=0,
                                   fg=cfg.fuel["font_color_estimate"],
                                   bg=cfg.fuel["bkg_color_estimate"])
        self.bar_fuel_6 = tk.Label(self, text=text_def, font=font_fuel,
                                   height=1, width=6, padx=0, pady=0, bd=0,
                                   fg=cfg.fuel["font_color_pits"],
                                   bg=cfg.fuel["bkg_color_pits"])
        self.bar_fuel_1.grid(row=1, column=0, padx=0, pady=0)
        self.bar_fuel_2.grid(row=1, column=1, padx=0, pady=0)
        self.bar_fuel_3.grid(row=1, column=2, padx=0, pady=0)
        self.bar_fuel_4.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_5.grid(row=2, column=1, padx=0, pady=(bar_gap, 0))
        self.bar_fuel_6.grid(row=2, column=2, padx=0, pady=(bar_gap, 0))

        self.update_fuel()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.fuel["position_x"] = str(self.winfo_x())
        cfg.fuel["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_fuel(self):
        """Update fuel

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.fuel["enable"]:
            # Read fuel data
            amount_curr, capacity = read_data.fuel()
            start_curr, laps_total, laps_left, time_left = read_data.timing()

            # Calc last lap fuel consumption
            if start_curr != self.start_last:  # time stamp difference
                if start_curr > self.start_last:
                    # Calc last laptime from lap difference to bypass empty invalid laptime
                    self.laptime_last = start_curr - self.start_last
                self.used_last = self.amount_last - amount_curr
                self.start_last = start_curr  # reset time stamp counter
                self.amount_last = amount_curr  # reset fuel counter
            self.used_last = max(self.used_last, 0)

            # Estimate laps current fuel can last
            try:
                # Total current fuel / last lap fuel consumption
                self.est_runlaps = amount_curr / self.used_last
            except ZeroDivisionError:
                self.est_runlaps = 0

            # Estimate minutes current fuel can last
            self.est_runmins = self.est_runlaps * self.laptime_last / 60

            # Total additional fuel required to finish race
            if laps_total < 100000:  # detected lap type race
                # Total laps left * last lap fuel consumption
                self.amount_need = laps_left * self.used_last - amount_curr
            else:  # detected time type race
                # Time left / last laptime * last lap fuel consumption - total current fuel
                self.amount_need = (math.ceil(time_left / (self.laptime_last + 0.001) + 0.001)
                                    * self.used_last - amount_curr)

            # Minimum required pitstops to finish race
            self.pit_required = max(self.amount_need / (capacity + 0.001), 0)

            # Limit display range of amount_need value
            if self.amount_need > 1000:
                self.amount_need = 999
            elif self.amount_need < -999:
                self.amount_need = -999

            amount_curr_d = calc.conv_fuel(amount_curr, cfg.fuel["fuel_unit"])
            amount_need_d = calc.conv_fuel(self.amount_need, cfg.fuel["fuel_unit"])
            used_last_d = calc.conv_fuel(self.used_last, cfg.fuel["fuel_unit"])

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

        # Update rate
        self.after(cfg.fuel["update_delay"], self.update_fuel)

    # Additional methods
    @staticmethod
    def color_lowfuel(fuel):
        """Low fuel warning color"""
        if fuel > 2:
            color = cfg.fuel["bkg_color_fuel"]
        else:
            color = cfg.fuel["bkg_color_low_fuel"]
        return color
