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
Timing Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "timing"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


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
        font_timing = tkfont.Font(family=self.wcfg["font_name"],
                                  size=-self.wcfg["font_size"],
                                  weight=self.wcfg["font_weight"])

        text_best = f"{self.wcfg['prefix_best']}--:--.---"
        text_last = f"{self.wcfg['prefix_last']}--:--.---"
        text_curr = f"{self.wcfg['prefix_current']}--:--.---"
        text_est = f"{self.wcfg['prefix_estimated']}--:--.---"
        text_sbest = f"{self.wcfg['prefix_session_best']}--:--.---"

        column_sbest = self.wcfg["column_index_session_best"]
        column_best = self.wcfg["column_index_best"]
        column_last = self.wcfg["column_index_last"]
        column_curr = self.wcfg["column_index_current"]
        column_est = self.wcfg["column_index_estimated"]

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":bar_padx, "pady":0, "font":font_timing}

        if self.wcfg["show_session_best"]:
            self.bar_time_sbest = tk.Label(self, bar_style, text=text_sbest,
                                           width=len(text_sbest),
                                           fg=self.wcfg["font_color_session_best"],
                                           bg=self.wcfg["bkg_color_session_best"])
        if self.wcfg["show_best"]:
            self.bar_time_best = tk.Label(self, bar_style, text=text_best,
                                          width=len(text_best),
                                          fg=self.wcfg["font_color_best"],
                                          bg=self.wcfg["bkg_color_best"])
        if self.wcfg["show_last"]:
            self.bar_time_last = tk.Label(self, bar_style, text=text_last,
                                          width=len(text_last),
                                          fg=self.wcfg["font_color_last"],
                                          bg=self.wcfg["bkg_color_last"])
        if self.wcfg["show_current"]:
            self.bar_time_curr = tk.Label(self, bar_style, text=text_curr,
                                          width=len(text_curr),
                                          fg=self.wcfg["font_color_current"],
                                          bg=self.wcfg["bkg_color_current"])
        if self.wcfg["show_estimated"]:
            self.bar_time_est = tk.Label(self, bar_style, text=text_est,
                                         width=len(text_est),
                                         fg=self.wcfg["font_color_estimated"],
                                         bg=self.wcfg["bkg_color_estimated"])

        if self.wcfg["layout"] == "0":
            if self.wcfg["show_session_best"]:
                self.bar_time_sbest.grid(row=column_sbest, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_best"]:
                self.bar_time_best.grid(row=column_best, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_last"]:
                self.bar_time_last.grid(row=column_last, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_current"]:
                self.bar_time_curr.grid(row=column_curr, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_estimated"]:
                self.bar_time_est.grid(row=column_est, column=0, padx=0, pady=(0, bar_gap))
        else:
            if self.wcfg["show_session_best"]:
                self.bar_time_sbest.grid(row=0, column=column_sbest, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_best"]:
                self.bar_time_best.grid(row=0, column=column_best, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_last"]:
                self.bar_time_last.grid(row=0, column=column_last, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_current"]:
                self.bar_time_curr.grid(row=0, column=column_curr, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_estimated"]:
                self.bar_time_est.grid(row=0, column=column_est, padx=(0, bar_gap), pady=0)

        # Last data
        self.checked = False
        self.vehicle_counter = 0
        self.laptime_sbest = MAGIC_NUM

        self.last_laptime_sbest = None
        self.last_laptime_best = None
        self.last_laptime_last = None
        self.last_laptime_curr = None
        self.last_laptime_est = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read Timing data
            (laptime_curr, laptime_last, laptime_best, laptime_est, _
             ) = module.delta_time.output_data

            # Reset switch
            if not self.checked:
                self.checked = True

            # Session best laptime
            if self.wcfg["show_session_best"]:
                veh_total, laptime_opt, is_same_class = read_data.timing(self.vehicle_counter)

                if 0 < laptime_opt < self.laptime_sbest:
                    if self.wcfg["session_best_from_same_class_only"] and is_same_class:
                        self.laptime_sbest = laptime_opt
                    elif not self.wcfg["session_best_from_same_class_only"]:
                        self.laptime_sbest = laptime_opt

                if self.vehicle_counter < max(veh_total, 1):
                    self.vehicle_counter += 1
                else:
                    self.vehicle_counter = 0

                self.update_laptime(self.laptime_sbest, self.last_laptime_sbest,
                                    self.wcfg["prefix_session_best"], "sbest")
                self.last_laptime_sbest = self.laptime_sbest

            # Personal best laptime
            if self.wcfg["show_best"]:
                self.update_laptime(laptime_best, self.last_laptime_best,
                                    self.wcfg["prefix_best"], "best")
                self.last_laptime_best = laptime_best

            # Last laptime
            if self.wcfg["show_last"]:
                self.update_laptime(laptime_last, self.last_laptime_last,
                                    self.wcfg["prefix_last"], "last")
                self.last_laptime_last = laptime_last

            # Current laptime
            if self.wcfg["show_current"]:
                self.update_laptime(laptime_curr, self.last_laptime_curr,
                                    self.wcfg["prefix_current"], "curr")
                self.last_laptime_curr = laptime_curr

            # Estimated laptime
            if self.wcfg["show_estimated"]:
                self.update_laptime(laptime_est, self.last_laptime_est,
                                    self.wcfg["prefix_estimated"], "est")
                self.last_laptime_est = laptime_est

        else:
            if self.checked:
                self.checked = False
                self.laptime_sbest = MAGIC_NUM  # reset laptime

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_laptime(self, curr, last, prefix, suffix):
        """Update laptime"""
        if curr != last:
            if 0 < curr < MAGIC_NUM:
                getattr(self, f"bar_time_{suffix}").config(
                    text=f"{prefix}{calc.sec2laptime(curr)[:9].rjust(9)}")
            else:
                getattr(self, f"bar_time_{suffix}").config(
                    text=f"{prefix}--:--.---")
