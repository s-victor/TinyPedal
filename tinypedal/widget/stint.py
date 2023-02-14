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
from ..module_control import module

WIDGET_NAME = "stint"


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
        font_stint = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":bar_padx, "pady":0, "font":font_stint}
        self.bar_laps = tk.Label(self, bar_style, text="LAPS", width=5,
                                 fg=self.wcfg["font_color_laps"],
                                 bg=self.wcfg["bkg_color_laps"])
        self.bar_time = tk.Label(self, bar_style, text="TIME", width=5,
                                 fg=self.wcfg["font_color_time"],
                                 bg=self.wcfg["bkg_color_time"])
        self.bar_fuel = tk.Label(self, bar_style, text="FUEL", width=5,
                                 fg=self.wcfg["font_color_fuel"],
                                 bg=self.wcfg["bkg_color_fuel"])
        self.bar_wear = tk.Label(self, bar_style, text="WEAR", width=3,
                                 fg=self.wcfg["font_color_wear"],
                                 bg=self.wcfg["bkg_color_wear"])

        self.bar_last_laps = tk.Label(self, bar_style, text="-- --", width=5,
                                      fg=self.wcfg["font_color_last_stint_laps"],
                                      bg=self.wcfg["bkg_color_last_stint_laps"])
        self.bar_last_time = tk.Label(self, bar_style, text="--:--", width=5,
                                      fg=self.wcfg["font_color_last_stint_time"],
                                      bg=self.wcfg["bkg_color_last_stint_time"])
        self.bar_last_fuel = tk.Label(self, bar_style, text="---.-", width=5,
                                      fg=self.wcfg["font_color_last_stint_fuel"],
                                      bg=self.wcfg["bkg_color_last_stint_fuel"])
        self.bar_last_wear = tk.Label(self, bar_style, text="--%", width=3,
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

        # Last data
        self.checked = False
        self.stint_running = False  # check whether current stint running
        self.reset_stint = True  # reset stint stats

        self.start_lap = 0
        self.start_time = 0
        self.start_fuel = 0
        self.start_wear = 0

        self.last_fuel = 0  # last recorded remaining fuel
        self.last_wear = 0  # last recorded average tyre wear
        self.last_cmpd = "--"  # last recorded tyre compound

        self.last_laps_text = None
        self.last_time_text = None
        self.last_fuel_text = None
        self.last_wear_text = None

        # Start updating
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
            lap_num, wear_curr, time_curr, inpits = read_data.stint()

            wear_avg = 100 - (sum(wear_curr) * 25)
            fuel_curr = module.fuel_usage.output_data[0]

            stint_cmpd = self.set_tyre_cmp(read_data.tyre_compound())
            stint_lap = max(lap_num - self.start_lap, 0)
            stint_time = max(time_curr - self.start_time, 0)
            stint_fuel = max(self.start_fuel - fuel_curr, 0)
            stint_wear = max(wear_avg - self.start_wear, 0)

            if not inpits:
                self.last_cmpd = stint_cmpd
                self.last_fuel = fuel_curr
                self.last_wear = stint_wear
                self.stint_running = True
            else:
                if self.stint_running:
                    if self.last_wear > stint_wear or self.last_fuel < fuel_curr:
                        self.bar_last_laps.config(text=f"{self.last_cmpd}{stint_lap: =03.0f}")
                        self.bar_last_time.config(text=calc.sec2stinttime(stint_time))
                        self.bar_last_fuel.config(text=f"{stint_fuel:05.01f}")
                        self.bar_last_wear.config(text=f"{self.last_wear:02.0f}%")
                        self.stint_running = False
                        self.reset_stint = True

            if self.reset_stint:
                self.start_lap = lap_num
                self.start_time = time_curr
                self.start_fuel = fuel_curr
                self.start_wear = wear_avg
                self.reset_stint = False

            if self.start_fuel < fuel_curr:
                self.start_fuel = fuel_curr

            laps_text = f"{stint_cmpd}{stint_lap: =03.0f}"
            self.update_stint("laps", laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2stinttime(stint_time)
            self.update_stint("time", time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{stint_fuel:05.01f}"
            self.update_stint("fuel", fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            wear_text = f"{stint_wear:02.0f}%"
            self.update_stint("wear", wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_stint(self, suffix, curr, last):
        """Stint data"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(text=curr)

    # Additional methods
    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        ftire = self.wcfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
        rtire = self.wcfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
        tire_cmpd = f"{ftire}{rtire}"
        return tire_cmpd
