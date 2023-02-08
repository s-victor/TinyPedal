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

        column_wear = self.wcfg["column_index_remaining"]
        column_diff = self.wcfg["column_index_wear_difference"]
        column_laps = self.wcfg["column_index_lifespan"]

        # Draw label
        frame_wear = tk.Frame(self, bd=0, highlightthickness=0)
        frame_diff = tk.Frame(self, bd=0, highlightthickness=0)

        bar_style_wear = {"text":"0.0", "bd":0, "height":1, "width":5,
                          "padx":0, "pady":0, "font":font_wear,
                          "fg":self.wcfg["font_color_remaining"],
                          "bg":self.wcfg["bkg_color_remaining"]}
        self.bar_wear_fl = tk.Label(frame_wear, bar_style_wear)
        self.bar_wear_fr = tk.Label(frame_wear, bar_style_wear)
        self.bar_wear_rl = tk.Label(frame_wear, bar_style_wear)
        self.bar_wear_rr = tk.Label(frame_wear, bar_style_wear)
        self.bar_wear_fl.grid(row=0, column=0, padx=0, pady=0)
        self.bar_wear_fr.grid(row=0, column=1, padx=0, pady=0)
        self.bar_wear_rl.grid(row=1, column=0, padx=0, pady=0)
        self.bar_wear_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["show_wear_difference"]:
            bar_style_diff = {"text":"0.0", "bd":0, "height":1, "width":5,
                              "padx":0, "pady":0, "font":font_wear,
                              "fg":self.wcfg["font_color_wear_difference"],
                              "bg":self.wcfg["bkg_color_wear_difference"]}
            self.bar_diff_fl = tk.Label(frame_diff, bar_style_diff)
            self.bar_diff_fr = tk.Label(frame_diff, bar_style_diff)
            self.bar_diff_rl = tk.Label(frame_diff, bar_style_diff)
            self.bar_diff_rr = tk.Label(frame_diff, bar_style_diff)
            self.bar_diff_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_diff_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_diff_rl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_diff_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["show_lifespan"]:
            frame_laps = tk.Frame(self, bd=0, highlightthickness=0)

            bar_style_laps = {"text":"0.0", "bd":0, "height":1, "width":5,
                              "padx":0, "pady":0, "font":font_wear,
                              "fg":self.wcfg["font_color_lifespan"],
                              "bg":self.wcfg["bkg_color_lifespan"]}
            self.bar_laps_fl = tk.Label(frame_laps, bar_style_laps)
            self.bar_laps_fr = tk.Label(frame_laps, bar_style_laps)
            self.bar_laps_rl = tk.Label(frame_laps, bar_style_laps)
            self.bar_laps_rr = tk.Label(frame_laps, bar_style_laps)
            self.bar_laps_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_laps_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_laps_rl.grid(row=1, column=0, padx=0, pady=0)
            self.bar_laps_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            frame_wear.grid(row=column_wear, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_wear_difference"]:
                frame_diff.grid(row=column_diff, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_lifespan"]:
                frame_laps.grid(row=column_laps, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            frame_wear.grid(row=0, column=column_wear, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_wear_difference"]:
                frame_diff.grid(row=0, column=column_diff, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_lifespan"]:
                frame_laps.grid(row=0, column=column_laps, padx=(0,bar_gap), pady=0)

        # Last data
        self.checked = False
        self.start_last = 0.0  # last lap start time
        self.wear_last = [0,0,0,0]  # remaining tyre wear from last lap
        self.wear_rlt = [0,0,0,0]  # realtime tyre wear difference since last lap
        self.wear_per = [0,0,0,0]  # total tyre wear of last lap
        self.wear_laps = [0,0,0,0]  # estimated tyre lifespan in laps

        self.last_wear_curr = [None] * 4
        self.last_wear_rlt = [None] * 4
        self.last_wear_per = [None] * 4
        self.last_wear_laps = [None] * 4

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

            # Read tyre wear data
            start_curr, lap_etime, wear_curr = read_data.wear()

            # Remaining tyre wear
            wear_curr = tuple(map(self.round2decimal, wear_curr))
            self.update_wear("wear_fl", wear_curr[0], self.last_wear_curr[0], self.wcfg["warning_threshold_remaining"])
            self.update_wear("wear_fr", wear_curr[1], self.last_wear_curr[1], self.wcfg["warning_threshold_remaining"])
            self.update_wear("wear_rl", wear_curr[2], self.last_wear_curr[2], self.wcfg["warning_threshold_remaining"])
            self.update_wear("wear_rr", wear_curr[3], self.last_wear_curr[3], self.wcfg["warning_threshold_remaining"])
            self.last_wear_curr = wear_curr

            # Update tyre wear differences
            self.wear_last, self.wear_rlt = zip(*tuple(map(self.wear_diff, wear_curr, self.wear_last, self.wear_rlt)))

            if start_curr != self.start_last:  # time stamp difference
                self.wear_per = self.wear_rlt
                self.wear_rlt = [0,0,0,0]  # reset real time wear
                self.start_last = start_curr  # reset time stamp counter

            # Tyre wear differences
            if self.wcfg["show_wear_difference"]:
                # Realtime diff
                if self.wcfg["realtime_wear_difference"] and lap_etime - start_curr > self.wcfg["freeze_duration"]:
                    self.update_diff("diff_fl", self.wear_rlt[0], self.last_wear_rlt[0], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_fr", self.wear_rlt[1], self.last_wear_rlt[1], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_rl", self.wear_rlt[2], self.last_wear_rlt[2], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_rr", self.wear_rlt[3], self.last_wear_rlt[3], self.wcfg["warning_threshold_wear"])
                    self.last_wear_rlt = self.wear_rlt
                else:
                    # Last lap diff
                    self.update_diff("diff_fl", self.wear_per[0], self.last_wear_per[0], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_fr", self.wear_per[1], self.last_wear_per[1], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_rl", self.wear_per[2], self.last_wear_per[2], self.wcfg["warning_threshold_wear"])
                    self.update_diff("diff_rr", self.wear_per[3], self.last_wear_per[3], self.wcfg["warning_threshold_wear"])
                    self.last_wear_per = self.wear_per

            # Estimated tyre lifespan in laps
            if self.wcfg["show_lifespan"]:
                self.wear_laps = tuple(map(self.estimated_laps, wear_curr, self.wear_per))
                self.update_laps("laps_fl", self.wear_laps[0], self.last_wear_laps[0], self.wcfg["warning_threshold_laps"])
                self.update_laps("laps_fr", self.wear_laps[1], self.last_wear_laps[1], self.wcfg["warning_threshold_laps"])
                self.update_laps("laps_rl", self.wear_laps[2], self.last_wear_laps[2], self.wcfg["warning_threshold_laps"])
                self.update_laps("laps_rr", self.wear_laps[3], self.last_wear_laps[3], self.wcfg["warning_threshold_laps"])
                self.last_wear_laps = self.wear_laps
        else:
            if self.checked:
                self.checked = False
                self.wear_last = [0,0,0,0]
                self.wear_rlt = [0,0,0,0]
                self.wear_per = [0,0,0,0]
                self.wear_laps = [0,0,0,0]

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_wear(self, suffix, curr, last, color):
        """Remaining tyre wear"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(
                text=self.format_num(curr),
                fg=self.color_wear(curr, color))

    def update_diff(self, suffix, curr, last, color):
        """Tyre wear differences"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(
                text=f"{curr:.02f}",
                fg=self.color_diff(curr, color))

    def update_laps(self, suffix, curr, last, color):
        """Estimated tyre lifespan in laps"""
        if curr != last:
            getattr(self, f"bar_{suffix}").config(
                text=self.format_num(curr),
                fg=self.color_laps(curr, color))

    # Additional methods
    @staticmethod
    def wear_diff(value, wear_last, wear_rlt):
        """Tyre wear differences"""
        if wear_last < value:
            wear_last = value
        elif wear_last > value:
            wear_rlt += wear_last - value
            wear_last = value
        return wear_last, wear_rlt

    @staticmethod
    def estimated_laps(wear_curr, wear_per):
        """Estimated tyre lifespan in laps = remaining / last lap wear"""
        return min(wear_curr / max(wear_per, 0.001), 999)

    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(value * 100, 2)

    @staticmethod
    def format_num(value):
        """Format number"""
        if value > 99.9:
            return f"{value:.0f}"
        return f"{value:.01f}"

    def color_wear(self, tyre_wear, threshold):
        """Warning color for remaining tyre"""
        if tyre_wear <= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_remaining"]

    def color_diff(self, tyre_wear, threshold):
        """Warning color for tyre wear differences"""
        if tyre_wear >= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_wear_difference"]

    def color_laps(self, tyre_wear, threshold):
        """Warning color for estimated tyre lifespan"""
        if tyre_wear <= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_lifespan"]
