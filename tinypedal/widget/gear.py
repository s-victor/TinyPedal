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

from tinypedal.__init__ import cfg
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "gear"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        # Config style & variable
        font_gear = tkfont.Font(family=self.cfg["font_name"],
                                size=-self.cfg["font_size"],
                                weight=self.cfg["font_weight_gear"])
        font_gauge = tkfont.Font(family=self.cfg["font_name"],
                                 size=-self.cfg["font_size"],
                                 weight=self.cfg["font_weight_gauge"])
        font_gauge_small = tkfont.Font(family=self.cfg["font_name"],
                                       size=-int(self.cfg["font_size"]*0.35),
                                       weight=self.cfg["font_weight_gauge"])

        # Set state for drawing optimization
        self.state_lm = True  # limiter

        # Draw label
        self.bar_gear_bg = tk.Canvas(self, bd=0, highlightthickness=0, height=0, width=0,
                                     bg=self.cfg["bkg_color"])
        self.bar_gear_bg.grid(row=0, column=0, columnspan=10, padx=0, pady=0, sticky="wens")

        self.bar_gear = tk.Label(self, text="N", bd=0, height=1, width=2,
                                 font=font_gear, padx=0, pady=0,
                                 fg=self.cfg["font_color_gear"],
                                 bg=self.cfg["bkg_color"])

        # Layout
        if self.cfg["layout"] == "0":
            self.bar_gear.grid(row=0, column=0, padx=0, pady=0)

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=4,
                                      font=font_gauge, padx=0, pady=0,
                                      fg=self.cfg["font_color_gauge"],
                                      bg=self.cfg["bkg_color"])
            self.bar_gauge.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

            self.rpm_width = self.bar_gear.winfo_reqwidth() + self.bar_gauge.winfo_reqwidth()
        else:
            self.bar_gear.grid(row=0, column=0,
                               padx=0, pady=(0, int(self.cfg["font_size"] * 0.45)))

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=3,
                                      font=font_gauge_small, padx=0, pady=0,
                                      fg=self.cfg["font_color_gauge"],
                                      bg=self.cfg["bkg_color"])
            self.bar_gauge.grid(row=0, column=0, sticky="wes",
                                padx=0, pady=(0, int(self.cfg["font_size"] * 0.15)))

            self.rpm_width = self.bar_gear.winfo_reqwidth()

        # RPM bar
        if self.cfg["show_rpm_bar"]:
            self.bar_rpm = tk.Canvas(self, bd=0, highlightthickness=0,
                                     height=self.cfg["rpm_bar_height"], width=self.rpm_width,
                                     bg=self.cfg["bkg_color_rpm_bar"])
            self.bar_rpm.grid(row=1, column=0, columnspan=2,
                              padx=0, pady=(self.cfg["rpm_bar_gap"], 0))
            # Used as transparent mask
            self.rect_rpm = self.bar_rpm.create_rectangle(
                            0, 0, 0, 0, fill="#000002", outline="")

        # Speed limiter
        self.bar_limiter = tk.Label(self, text=self.cfg["speed_limiter_text"], bd=0, height=1,
                                    width=len(self.cfg["speed_limiter_text"])+1,
                                    font=font_gear, padx=0, pady=0,
                                    fg="#111111", bg="#FF2200")
        self.bar_limiter.grid(row=0, column=5, padx=0, pady=0, sticky="ns")
        self.bar_limiter.grid_remove()  # hide limiter indicator at start

        # Countdown
        if self.cfg["show_countdown"]:
            self.bar_countdown = tk.Label(self, text="0.00", bd=0, height=1, width=5,
                                          font=font_gear, padx=0, pady=0,
                                          fg="#111111", bg="#FFFFFF")
            self.bar_countdown.grid(row=0, column=3, padx=0, pady=0, sticky="ns")
            self.bar_countdown.grid_remove()  # hide countdown indicator at start

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read gear data
            pit_limiter, gear, speed, rpm, rpm_max, race_phase = read_data.gear()

            # Check isPlayer before update
            if read_data.is_local_player():

                gear = calc.gear(gear)
                speed = calc.conv_speed(speed, self.cfg["speed_unit"])
                rpm_safe = int(rpm_max * self.cfg["rpm_safe_multiplier"])
                rpm_warn = int(rpm_max * self.cfg["rpm_warn_multiplier"])
                rpm_color = self.color_rpm(rpm, rpm_safe, rpm_warn, rpm_max)

                # Gear update
                self.bar_gear_bg.config(bg=rpm_color)
                self.bar_gear.config(text=gear, bg=rpm_color)
                self.bar_gauge.config(text=f"{speed:03.0f}", bg=rpm_color)

                # Pit limiter update
                if pit_limiter and self.state_lm:
                    self.bar_limiter.grid()
                    self.state_lm = False
                elif not pit_limiter and not self.state_lm:
                    self.bar_limiter.grid_remove()  # hide limiter indicator
                    self.state_lm = True

                # Countdown update
                if self.cfg["show_countdown"]:
                    if race_phase == 4:
                        start_countdown = read_data.lap_timer()
                        self.bar_countdown.config(text=f"{max(start_countdown, 0):.02f}")
                        self.bar_countdown.grid()
                    elif race_phase != 4:
                        self.bar_countdown.grid_remove()  # hide countdown indicator at start

                # RPM bar update
                if self.cfg["show_rpm_bar"]:
                    rpm_range = rpm_max - rpm_safe
                    if rpm_range != 0:
                        rpmscale = max(rpm - rpm_safe, 0) / rpm_range * self.rpm_width
                    else:
                        rpmscale = 0
                    self.bar_rpm.coords(self.rect_rpm,
                                        rpmscale, self.cfg["rpm_bar_edge_height"],
                                        rpm_range, self.cfg["rpm_bar_height"])

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    def color_rpm(self, rpm, rpm_safe, rpm_warn, rpm_max):
        """RPM indicator color"""
        if rpm < rpm_safe:
            color = self.cfg["bkg_color"]
        elif rpm_safe <= rpm < rpm_warn:
            color = self.cfg["bkg_color_rpm_safe"]
        elif rpm_warn <= rpm <= rpm_max:
            color = self.cfg["bkg_color_rpm_warn"]
        else:
            color = self.cfg["bkg_color_rpm_over_rev"]
        return color
