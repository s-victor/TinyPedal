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
Gear Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "gear"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_gear = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight_gear"])
        font_gauge = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight_gauge"])
        font_gauge_small = tkfont.Font(family=self.wcfg["font_name"],
                                       size=-int(self.wcfg["font_size"]*0.35),
                                       weight=self.wcfg["font_weight_gauge"])
        font_indicator = tkfont.Font(family=self.wcfg["font_name"],
                                     size=-self.wcfg["font_size"],
                                     weight=self.wcfg["font_weight_indicator"])

        # Set state for drawing optimization
        self.checked = False

        # Draw label
        self.bar_gear_bg = tk.Canvas(self, bd=0, highlightthickness=0, height=0, width=0,
                                     bg=self.wcfg["bkg_color"])
        self.bar_gear_bg.grid(row=0, column=0, columnspan=10, padx=0, pady=0, sticky="wens")

        self.bar_gear = tk.Label(self, text="N", bd=0, height=1, width=2,
                                 font=font_gear, padx=0, pady=0,
                                 fg=self.wcfg["font_color_gear"],
                                 bg=self.wcfg["bkg_color"])

        # Layout
        if self.wcfg["layout"] == "0":
            self.bar_gear.grid(row=0, column=0, padx=0, pady=0)

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=4,
                                      font=font_gauge, padx=0, pady=0,
                                      fg=self.wcfg["font_color_gauge"],
                                      bg=self.wcfg["bkg_color"])
            self.bar_gauge.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

            self.rpm_width = self.bar_gear.winfo_reqwidth() + self.bar_gauge.winfo_reqwidth()
        else:
            self.bar_gear.grid(row=0, column=0,
                               padx=0, pady=(0, int(self.wcfg["font_size"] * 0.45)))

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=3,
                                      font=font_gauge_small, padx=0, pady=0,
                                      fg=self.wcfg["font_color_gauge"],
                                      bg=self.wcfg["bkg_color"])
            self.bar_gauge.grid(row=0, column=0, sticky="wes",
                                padx=0, pady=(0, int(self.wcfg["font_size"] * 0.15)))

            self.rpm_width = self.bar_gear.winfo_reqwidth()

        # RPM bar
        if self.wcfg["show_rpm_bar"]:
            self.bar_rpm = tk.Canvas(self, bd=0, highlightthickness=0,
                                     height=self.wcfg["rpm_bar_height"], width=self.rpm_width,
                                     bg=self.wcfg["bkg_color_rpm_bar"])
            self.bar_rpm.grid(row=1, column=0, columnspan=2,
                              padx=0, pady=(self.wcfg["rpm_bar_gap"], 0))
            # Used as transparent mask
            self.rect_rpm = self.bar_rpm.create_rectangle(
                            0, 0, 0, 0, fill=self.cfg.overlay["transparent_color"], outline="")

        # Speed limiter
        if self.wcfg["show_speed_limiter"]:
            self.bar_limiter = tk.Label(self, font=font_indicator, bd=0, height=1,
                                        padx=0, pady=0,
                                        text=self.wcfg["speed_limiter_text"],
                                        width=len(self.wcfg["speed_limiter_text"])+1,
                                        fg=self.wcfg["font_color_speed_limiter"],
                                        bg=self.wcfg["bkg_color_speed_limiter"])
            self.bar_limiter.grid(row=0, column=4, padx=0, pady=0, sticky="ns")
            self.bar_limiter.grid_remove()

        # Last data
        self.last_gear_data = [None] * 3
        self.last_pit_limiter = None
        self.last_rpm_pos = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Switch
            if not self.checked:
                self.checked = True

            # Read gear data
            pit_limiter, gear, speed, rpm, rpm_max = read_data.gear()
            rpm_safe = int(rpm_max * self.wcfg["rpm_safe_multiplier"])
            rpm_warn = int(rpm_max * self.wcfg["rpm_warn_multiplier"])

            # Gear update
            gear_data = (calc.gear(gear),
                         round(self.speed_units(speed)),
                         self.color_rpm(rpm, rpm_safe, rpm_warn, rpm_max, gear, speed))

            self.update_gear(gear_data, self.last_gear_data)
            self.last_gear_data = gear_data

            # RPM bar update
            if self.wcfg["show_rpm_bar"]:
                rpm_range = rpm_max - rpm_safe
                rpm_scale = max(rpm - rpm_safe, 0) / rpm_range * self.rpm_width if rpm_range else 0

                rpm_pos = (rpm_range, rpm_scale)
                self.update_rpm(rpm_pos, self.last_rpm_pos)
                self.last_rpm_pos = rpm_pos

            # Pit limiter
            if self.wcfg["show_speed_limiter"]:
                self.update_limiter(pit_limiter, self.last_pit_limiter)
                self.last_pit_limiter = pit_limiter

        else:
            if self.checked:
                self.checked = False

                # Reset state
                self.last_gear_data = [None] * 3
                self.last_pit_limiter = None
                self.last_rpm_pos = None

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_gear(self, curr, last):
        """Gear bar"""
        if curr != last:
            self.bar_gear_bg.config(bg=curr[2])
            self.bar_gear.config(text=curr[0], bg=curr[2])
            self.bar_gauge.config(text=f"{curr[1]:03.0f}", bg=curr[2])

    def update_rpm(self, curr, last):
        """RPM bar"""
        if curr != last:
            self.bar_rpm.coords(self.rect_rpm,
                                curr[1], self.wcfg["rpm_bar_edge_height"],
                                curr[0], self.wcfg["rpm_bar_height"])

    def update_limiter(self, curr, last):
        """Speed limiter"""
        if curr != last:
            if curr == 1:
                self.bar_limiter.grid()
            else:
                self.bar_limiter.grid_remove()

    # Additional methods
    def speed_units(self, value):
        """Speed units"""
        if self.wcfg["speed_unit"] == "0":
            return calc.mps2kph(value)
        if self.wcfg["speed_unit"] == "1":
            return calc.mps2mph(value)
        return value

    def color_rpm(self, rpm, rpm_safe, rpm_warn, rpm_max, gear, speed):
        """RPM indicator color"""
        if gear == 0 and speed > self.wcfg["neutral_warning_speed_threshold"]:
            return self.wcfg["bkg_color_rpm_over_rev"]
        if rpm < rpm_safe:
            color = self.wcfg["bkg_color"]
        elif rpm_safe <= rpm < rpm_warn:
            color = self.wcfg["bkg_color_rpm_safe"]
        elif rpm_warn <= rpm <= rpm_max:
            color = self.wcfg["bkg_color_rpm_warn"]
        else:
            color = self.wcfg["bkg_color_rpm_over_rev"]
        return color
