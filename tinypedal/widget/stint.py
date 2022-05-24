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

from tinypedal.__init__ import info
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "stint"
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

        self.stint_running = 0  # check whether current stint running
        self.reset_stint = 1  # reset stint stats

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
        font_stint = tkfont.Font(family=self.cfg["font_name"],
                                 size=-self.cfg["font_size"],
                                 weight=self.cfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_stint}
        self.bar_laps = tk.Label(self, bar_style, text="LAPS", width=6,
                                 fg=self.cfg["font_color_laps"],
                                 bg=self.cfg["bkg_color_laps"])
        self.bar_time = tk.Label(self, bar_style, text="TIME", width=6,
                                 fg=self.cfg["font_color_time"],
                                 bg=self.cfg["bkg_color_time"])
        self.bar_fuel = tk.Label(self, bar_style, text="FUEL", width=6,
                                 fg=self.cfg["font_color_fuel"],
                                 bg=self.cfg["bkg_color_fuel"])
        self.bar_wear = tk.Label(self, bar_style, text="WEAR", width=4,
                                 fg=self.cfg["font_color_wear"],
                                 bg=self.cfg["bkg_color_wear"])

        self.bar_last_laps = tk.Label(self, bar_style, text="LAPS", width=6,
                                      fg=self.cfg["font_color_last_stint_laps"],
                                      bg=self.cfg["bkg_color_last_stint_laps"])
        self.bar_last_time = tk.Label(self, bar_style, text="TIME", width=6,
                                      fg=self.cfg["font_color_last_stint_time"],
                                      bg=self.cfg["bkg_color_last_stint_time"])
        self.bar_last_fuel = tk.Label(self, bar_style, text="FUEL", width=6,
                                      fg=self.cfg["font_color_last_stint_fuel"],
                                      bg=self.cfg["bkg_color_last_stint_fuel"])
        self.bar_last_wear = tk.Label(self, bar_style, text="WEAR", width=4,
                                      fg=self.cfg["font_color_last_stint_wear"],
                                      bg=self.cfg["bkg_color_last_stint_wear"])

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
        if read_data.state() and self.cfg["enable"]:
            pidx = info.players_index

            # Read stint data
            (lap_num, wear_avg, fuel_curr, time_curr, inpits, ftire_idx, rtire_idx, game_phase
             ) = read_data.stint()

            # Check isPlayer before update
            if pidx == info.players_index:

                fuel_curr = calc.conv_fuel(fuel_curr, self.cfg["fuel_unit"])
                ftire_cmpd = self.cfg["tyre_compound_list"][ftire_idx:(ftire_idx+1)]
                rtire_cmpd = self.cfg["tyre_compound_list"][rtire_idx:(rtire_idx+1)]

                stint_lap = max(lap_num - self.start_lap, 0)
                stint_time = max(time_curr - self.start_time, 0)
                stint_fuel = max(self.start_fuel - fuel_curr, 0)
                stint_wear = max(wear_avg - self.start_wear, 0)
                stint_cmpd = f"{ftire_cmpd}{rtire_cmpd}"

                if not inpits:
                    self.last_fuel = fuel_curr
                    self.last_wear = stint_wear
                    self.last_cmpd = stint_cmpd
                    self.stint_running = 1
                else:
                    if self.stint_running:
                        if (self.last_wear > stint_wear) or (self.last_fuel < fuel_curr):
                            self.last_stint_lap = stint_lap
                            self.last_stint_time = stint_time
                            self.last_stint_fuel = stint_fuel
                            self.last_stint_wear = self.last_wear
                            self.last_stint_cmpd = self.last_cmpd
                            self.stint_running = 0
                            self.reset_stint = 1

                if self.reset_stint:
                    self.start_lap = lap_num
                    self.start_time = time_curr
                    self.start_fuel = fuel_curr
                    self.start_wear = wear_avg
                    self.reset_stint = 0

                if game_phase < 5:  # reset stint stats if session has not started
                    self.reset_stint = 1

                if self.cfg["fuel_unit"] == 0:
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
            self.stint_running = 0
            self.reset_stint = 1

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
