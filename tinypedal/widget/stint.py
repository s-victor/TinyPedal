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
Stint Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent


class Draw(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "stint"

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self)
        self.cfg = config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        self.checked = False
        self.stint_running = False  # check whether current stint running
        self.reset_stint = True  # reset stint stats

        self.start_lap = 0
        self.start_time = 0
        self.start_fuel = 0
        self.start_wear = 0

        self.last_stint_lap = 0
        self.last_stint_time = 0
        self.last_stint_fuel = 0
        self.last_stint_wear = 0
        self.last_stint_cmpd = "--"

        self.last_fuel = 0  # last recorded remaining fuel
        self.last_wear = 0  # last recorded average tyre wear
        self.last_cmpd = "--"  # last recorded tyre compound

        # Config style & variable
        font_stint = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_stint}
        self.bar_laps = tk.Label(self, bar_style, text="LAPS", width=6,
                                 fg=self.wcfg["font_color_laps"],
                                 bg=self.wcfg["bkg_color_laps"])
        self.bar_time = tk.Label(self, bar_style, text="TIME", width=6,
                                 fg=self.wcfg["font_color_time"],
                                 bg=self.wcfg["bkg_color_time"])
        self.bar_fuel = tk.Label(self, bar_style, text="FUEL", width=6,
                                 fg=self.wcfg["font_color_fuel"],
                                 bg=self.wcfg["bkg_color_fuel"])
        self.bar_wear = tk.Label(self, bar_style, text="WEAR", width=4,
                                 fg=self.wcfg["font_color_wear"],
                                 bg=self.wcfg["bkg_color_wear"])

        self.bar_last_laps = tk.Label(self, bar_style, text="LAPS", width=6,
                                      fg=self.wcfg["font_color_last_stint_laps"],
                                      bg=self.wcfg["bkg_color_last_stint_laps"])
        self.bar_last_time = tk.Label(self, bar_style, text="TIME", width=6,
                                      fg=self.wcfg["font_color_last_stint_time"],
                                      bg=self.wcfg["bkg_color_last_stint_time"])
        self.bar_last_fuel = tk.Label(self, bar_style, text="FUEL", width=6,
                                      fg=self.wcfg["font_color_last_stint_fuel"],
                                      bg=self.wcfg["bkg_color_last_stint_fuel"])
        self.bar_last_wear = tk.Label(self, bar_style, text="WEAR", width=4,
                                      fg=self.wcfg["font_color_last_stint_wear"],
                                      bg=self.wcfg["bkg_color_last_stint_wear"])

        self.bar_laps.grid(row=0, column=1, padx=0, pady=0)
        self.bar_time.grid(row=0, column=2, padx=0, pady=0)
        self.bar_fuel.grid(row=0, column=3, padx=0, pady=0)
        self.bar_wear.grid(row=0, column=4, padx=0, pady=0)

        self.bar_last_laps.grid(row=1, column=1, padx=0, pady=(bar_gap, 0))
        self.bar_last_time.grid(row=1, column=2, padx=0, pady=(bar_gap, 0))
        self.bar_last_fuel.grid(row=1, column=3, padx=0, pady=(bar_gap, 0))
        self.bar_last_wear.grid(row=1, column=4, padx=0, pady=(bar_gap, 0))

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read stint data
            (lap_num, wear_avg, fuel_curr, time_curr, inpits, tire_idx, game_phase
             ) = read_data.stint()

            # Start updating
            fuel_curr = calc.conv_fuel(fuel_curr, self.wcfg["fuel_unit"])
            ftire_cmpd = self.wcfg["tyre_compound_list"][tire_idx[0]:(tire_idx[0]+1)]
            rtire_cmpd = self.wcfg["tyre_compound_list"][tire_idx[1]:(tire_idx[1]+1)]

            stint_lap = max(lap_num - self.start_lap, 0)
            stint_time = max(time_curr - self.start_time, 0)
            stint_fuel = max(self.start_fuel - fuel_curr, 0)
            stint_wear = max(wear_avg - self.start_wear, 0)
            stint_cmpd = f"{ftire_cmpd}{rtire_cmpd}"

            if not inpits:
                self.last_fuel = fuel_curr
                self.last_wear = stint_wear
                self.last_cmpd = stint_cmpd
                self.stint_running = True
            else:
                if self.stint_running:
                    if (self.last_wear > stint_wear) or (self.last_fuel < fuel_curr):
                        self.last_stint_lap = stint_lap
                        self.last_stint_time = stint_time
                        self.last_stint_fuel = stint_fuel
                        self.last_stint_wear = self.last_wear
                        self.last_stint_cmpd = self.last_cmpd
                        self.stint_running = False
                        self.reset_stint = True

            if self.reset_stint:
                self.start_lap = lap_num
                self.start_time = time_curr
                self.start_fuel = fuel_curr
                self.start_wear = wear_avg
                self.reset_stint = False

            if game_phase < 5:  # reset stint stats if session has not started
                self.reset_stint = True

            if self.wcfg["fuel_unit"] == 0:
                fuel_text = f"{stint_fuel:05.01f}"
                last_fuel_text = f"{self.last_stint_fuel:05.01f}"
            else:
                fuel_text = f"{stint_fuel:05.02f}"
                last_fuel_text = f"{self.last_stint_fuel:05.02f}"

            self.bar_laps.config(text=f"{stint_cmpd}{stint_lap: =03.0f}")
            self.bar_time.config(text=calc.sec2stinttime(stint_time))
            self.bar_fuel.config(text=fuel_text)
            self.bar_wear.config(text=f"{stint_wear:02.0f}%")

            self.bar_last_laps.config(text=f"{self.last_stint_cmpd}{self.last_stint_lap: =03.0f}")
            self.bar_last_time.config(text=calc.sec2stinttime(self.last_stint_time))
            self.bar_last_fuel.config(text=last_fuel_text)
            self.bar_last_wear.config(text=f"{self.last_stint_wear:02.0f}%")

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)
