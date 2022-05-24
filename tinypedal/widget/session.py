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
Session Widget
"""

import time
import tkinter as tk
import tkinter.font as tkfont

from tinypedal.__init__ import info
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "session"
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
        font_session = tkfont.Font(family=self.cfg["font_name"],
                                   size=-self.cfg["font_size"],
                                   weight=self.cfg["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_session}
        self.bar_racelength = tk.Label(self, bar_style, text="RACELENGTH", width=11,
                                       fg=self.cfg["font_color_racelength"],
                                       bg=self.cfg["bkg_color_racelength"])
        self.bar_racelength.grid(row=0, column=1, padx=(bar_gap, 0), pady=0)

        if self.cfg["show_clock"]:
            self.bar_clock = tk.Label(self, bar_style, text="CLOCK", width=6,
                                      fg=self.cfg["font_color_clock"],
                                      bg=self.cfg["bkg_color_clock"])
            self.bar_clock.grid(row=0, column=0, padx=0, pady=0)

        if self.cfg["show_lapnumber"]:
            self.bar_lapnumber = tk.Label(self, bar_style, text="LAPS", width=5,
                                          fg=self.cfg["font_color_lapnumber"],
                                          bg=self.cfg["bkg_color_lapnumber"])
            self.bar_lapnumber.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)

        if self.cfg["show_place"]:
            self.bar_place = tk.Label(self, bar_style, text="PLACE", width=6,
                                      fg=self.cfg["font_color_place"],
                                      bg=self.cfg["bkg_color_place"])
            self.bar_place.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:
            pidx = info.players_index

            # Read session data
            time_left, lap_total, lap_num, plr_place, veh_total, lap_into = read_data.session()

            # Check isPlayer before update
            if pidx == info.players_index:

                clock = time.strftime(self.cfg["clock_format"])

                # Check race type
                if lap_total > 100000:  # none-lap race
                    lap_num_text = f"{self.cfg['lapnumber_text']}{lap_num}.{lap_into:02.0f}"
                else:
                    lap_num_text = f"{self.cfg['lapnumber_text']}{lap_num}.{lap_into:02.0f}/{lap_total}"

                # Session update
                self.bar_racelength.config(text=calc.sec2sessiontime(max(time_left, 0)))

                if self.cfg["show_clock"]:
                    self.bar_clock.config(text=f"{clock}", width=len(clock) + 1)

                if self.cfg["show_lapnumber"]:
                    if (lap_num + 1) >= lap_total:
                        bg_lapnumber = self.cfg["bkg_color_maxlap_warn"]
                    else:
                        bg_lapnumber = self.cfg["bkg_color_lapnumber"]
                    self.bar_lapnumber.config(text=lap_num_text,
                                              width=len(lap_num_text) + 1,
                                              bg=bg_lapnumber)

            if self.cfg["show_place"]:
                self.bar_place.config(text=f"{plr_place:02.0f}/{veh_total:02.0f}")

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
