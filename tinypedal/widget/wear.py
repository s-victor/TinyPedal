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
Tyre Wear Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "wear"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_wear = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        self.checked = False
        self.start_last = 0.0  # last lap start time
        self.wear_last = [0,0,0,0]  # remaining tyre wear from last lap
        self.wear_rlt = [0,0,0,0]  # realtime tyre wear difference since last lap
        self.wear_per = [0,0,0,0]  # total tyre wear of last lap
        self.wear_laps = [0,0,0,0]  # estimated tyre lifespan in laps

        # Draw label
        bar_style = {"text":"0.0", "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_wear, "bg":self.wcfg["bkg_color"]}

        frame_wear = tk.Frame(self, bd=0, highlightthickness=0)
        frame_last = tk.Frame(self, bd=0, highlightthickness=0)

        self.bar_wear_fl = tk.Label(frame_wear, bar_style, fg=self.wcfg["font_color_remaining"])
        self.bar_wear_fr = tk.Label(frame_wear, bar_style, fg=self.wcfg["font_color_remaining"])
        self.bar_wear_rl = tk.Label(frame_wear, bar_style, fg=self.wcfg["font_color_remaining"])
        self.bar_wear_rr = tk.Label(frame_wear, bar_style, fg=self.wcfg["font_color_remaining"])
        self.bar_wear_fl.grid(row=0, column=0, padx=0, pady=0)
        self.bar_wear_fr.grid(row=0, column=1, padx=0, pady=0)
        self.bar_wear_rl.grid(row=1, column=0, padx=0, pady=0)
        self.bar_wear_rr.grid(row=1, column=1, padx=0, pady=0)

        self.bar_last_fl = tk.Label(frame_last, bar_style, fg=self.wcfg["font_color_last_wear"])
        self.bar_last_fr = tk.Label(frame_last, bar_style, fg=self.wcfg["font_color_last_wear"])
        self.bar_last_rl = tk.Label(frame_last, bar_style, fg=self.wcfg["font_color_last_wear"])
        self.bar_last_rr = tk.Label(frame_last, bar_style, fg=self.wcfg["font_color_last_wear"])
        self.bar_last_fl.grid(row=0, column=0, padx=0, pady=0)
        self.bar_last_fr.grid(row=0, column=1, padx=0, pady=0)
        self.bar_last_rl.grid(row=1, column=0, padx=0, pady=0)
        self.bar_last_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["show_lifespan"]:
            frame_laps = tk.Frame(self, bd=0, highlightthickness=0)
            self.bar_laps_fl = tk.Label(frame_laps, bar_style, fg=self.wcfg["font_color_lifespan"])
            self.bar_laps_fr = tk.Label(frame_laps, bar_style, fg=self.wcfg["font_color_lifespan"])
            self.bar_laps_rl = tk.Label(frame_laps, bar_style, fg=self.wcfg["font_color_lifespan"])
            self.bar_laps_rr = tk.Label(frame_laps, bar_style, fg=self.wcfg["font_color_lifespan"])
            self.bar_laps_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_laps_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_laps_rl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_laps_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            frame_wear.grid(row=self.wcfg["column_index_remaining"], column=0, padx=0, pady=(0,bar_gap))
            frame_last.grid(row=self.wcfg["column_index_last_wear"], column=0, padx=0, pady=(0,bar_gap))

            if self.wcfg["show_lifespan"]:
                frame_laps.grid(row=self.wcfg["column_index_lifespan"], column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            frame_wear.grid(row=0, column=self.wcfg["column_index_remaining"], padx=(0,bar_gap), pady=0)
            frame_last.grid(row=0, column=self.wcfg["column_index_last_wear"], padx=(0,bar_gap), pady=0)

            if self.wcfg["show_lifespan"]:
                frame_laps.grid(row=0, column=self.wcfg["column_index_lifespan"], padx=(0,bar_gap), pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read tyre wear data
            start_curr, lap_etime, wear_curr = read_data.wear()

            # Start updating
            # Recording tyre wear differences
            self.wear_diff(wear_curr)

            # Remaining tyre update
            self.bar_wear_fl.config(text=self.format_num(wear_curr[0]),
                                    fg=self.color_wear(wear_curr[0], self.wcfg["warning_threshold_remaining"]))
            self.bar_wear_fr.config(text=self.format_num(wear_curr[1]),
                                    fg=self.color_wear(wear_curr[1], self.wcfg["warning_threshold_remaining"]))
            self.bar_wear_rl.config(text=self.format_num(wear_curr[2]),
                                    fg=self.color_wear(wear_curr[2], self.wcfg["warning_threshold_remaining"]))
            self.bar_wear_rr.config(text=self.format_num(wear_curr[3]),
                                    fg=self.color_wear(wear_curr[3], self.wcfg["warning_threshold_remaining"]))

            # Last lap tyre wear update
            if start_curr != self.start_last:  # time stamp difference
                # Calculate last lap tyre wear
                self.wear_per = self.wear_rlt
                self.wear_rlt = [0,0,0,0]
                self.start_last = start_curr  # reset time stamp counter

                self.bar_last_fl.config(text=f"{self.wear_per[0]:.2f}",
                                        fg=self.color_last(self.wear_per[0], self.wcfg["warning_threshold_wear"]))
                self.bar_last_fr.config(text=f"{self.wear_per[1]:.2f}",
                                        fg=self.color_last(self.wear_per[1], self.wcfg["warning_threshold_wear"]))
                self.bar_last_rl.config(text=f"{self.wear_per[2]:.2f}",
                                        fg=self.color_last(self.wear_per[2], self.wcfg["warning_threshold_wear"]))
                self.bar_last_rr.config(text=f"{self.wear_per[3]:.2f}",
                                        fg=self.color_last(self.wear_per[3], self.wcfg["warning_threshold_wear"]))

            # Show realtime tyre wear
            if self.wcfg["show_realtime_wear"]:
                if lap_etime - start_curr > self.wcfg["seconds_before_showing_realtime_wear"]:
                    self.bar_last_fl.config(text=f"{self.wear_rlt[0]:.2f}",
                                            fg=self.color_last(self.wear_rlt[0], self.wcfg["warning_threshold_wear"]))
                    self.bar_last_fr.config(text=f"{self.wear_rlt[1]:.2f}",
                                            fg=self.color_last(self.wear_rlt[1], self.wcfg["warning_threshold_wear"]))
                    self.bar_last_rl.config(text=f"{self.wear_rlt[2]:.2f}",
                                            fg=self.color_last(self.wear_rlt[2], self.wcfg["warning_threshold_wear"]))
                    self.bar_last_rr.config(text=f"{self.wear_rlt[3]:.2f}",
                                            fg=self.color_last(self.wear_rlt[3], self.wcfg["warning_threshold_wear"]))

            # Show estimated tyre lifespan update
            if self.wcfg["show_lifespan"]:
                if self.wear_per[0] > 0:
                    self.wear_laps[0] = min(wear_curr[0] / self.wear_per[0], 999)
                if self.wear_per[1] > 0:
                    self.wear_laps[1] = min(wear_curr[1] / self.wear_per[1], 999)
                if self.wear_per[2] > 0:
                    self.wear_laps[2] = min(wear_curr[2] / self.wear_per[2], 999)
                if self.wear_per[3] > 0:
                    self.wear_laps[3] = min(wear_curr[3] / self.wear_per[3], 999)

                self.bar_laps_fl.config(text=self.format_num(self.wear_laps[0]),
                                        fg=self.color_laps(self.wear_laps[0], self.wcfg["warning_threshold_laps"]))
                self.bar_laps_fr.config(text=self.format_num(self.wear_laps[1]),
                                        fg=self.color_laps(self.wear_laps[1], self.wcfg["warning_threshold_laps"]))
                self.bar_laps_rl.config(text=self.format_num(self.wear_laps[2]),
                                        fg=self.color_laps(self.wear_laps[2], self.wcfg["warning_threshold_laps"]))
                self.bar_laps_rr.config(text=self.format_num(self.wear_laps[3]),
                                        fg=self.color_laps(self.wear_laps[3], self.wcfg["warning_threshold_laps"]))

        else:
            if self.checked:
                self.checked = False
                self.wear_last = [0,0,0,0]
                self.wear_rlt = [0,0,0,0]
                self.wear_per = [0,0,0,0]
                self.wear_laps = [0,0,0,0]

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def wear_diff(self, value):
        """Recording tyre wear differences"""
        for index in range(4):
            if self.wear_last[index] < value[index]:
                self.wear_last[index] = value[index]
            elif self.wear_last[index] > value[index]:
                self.wear_rlt[index] += self.wear_last[index] - value[index]
                self.wear_last[index] = value[index]

    def color_wear(self, tyre_wear, threshold):
        """Warning color for remaining tyre"""
        if tyre_wear <= threshold:
            color = self.wcfg["font_color_warning"]
        else:
            color = self.wcfg["font_color_remaining"]
        return color

    def color_last(self, tyre_wear, threshold):
        """Warning color for last lap tyre wear"""
        if tyre_wear >= threshold:
            color = self.wcfg["font_color_warning"]
        else:
            color = self.wcfg["font_color_last_wear"]
        return color

    def color_laps(self, tyre_wear, threshold):
        """Warning color for estimated tyre lifespan"""
        if tyre_wear <= threshold:
            color = self.wcfg["font_color_warning"]
        else:
            color = self.wcfg["font_color_lifespan"]
        return color

    @staticmethod
    def format_num(value):
        """Format number"""
        if value > 99.9:
            value = f"{value:.0f}"
        else:
            value = f"{value:.1f}"
        return value
