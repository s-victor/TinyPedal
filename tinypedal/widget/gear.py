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
from ..module_control import module

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

        self.state_lm = True  # limiter
        self.state_cd = False
        self.state_slight = False
        self.state_blue = True
        self.state_ys1 = True
        self.state_ys2 = True
        self.state_ys3 = True

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
        self.bar_limiter = tk.Label(self, text=self.wcfg["speed_limiter_text"], bd=0, height=1,
                                    width=len(self.wcfg["speed_limiter_text"])+1,
                                    font=font_indicator, padx=0, pady=0,
                                    fg=self.wcfg["font_color_speed_limiter"],
                                    bg=self.wcfg["bkg_color_speed_limiter"])
        self.bar_limiter.grid(row=0, column=4, padx=0, pady=0, sticky="ns")
        self.bar_limiter.grid_remove()  # hide indicator at start

        # Low fuel warning
        if self.wcfg["show_low_fuel"]:
            self.bar_lowfuel = tk.Label(self, text="-.--", bd=0, height=1, width=5,
                                        font=font_indicator, padx=0, pady=0,
                                        fg=self.wcfg["font_color_low_fuel"],
                                        bg=self.wcfg["bkg_color_low_fuel"])
            self.bar_lowfuel.grid(row=0, column=5, padx=0, pady=0, sticky="ns")
            self.bar_lowfuel.grid_remove()

        # Start lights
        if self.wcfg["show_startlights"]:
            self.bar_startlights = tk.Label(self, text="", bd=0, height=1, width=2,
                                            font=font_indicator, padx=0, pady=0,
                                            fg=self.wcfg["font_color_startlights"],
                                            bg=self.wcfg["bkg_color_red_lights"])
            self.bar_startlights.grid(row=0, column=6, padx=0, pady=0, sticky="ns")
            self.bar_startlights.grid_remove()

        # Countdown
        if self.wcfg["show_start_countdown"] == "THIS_MAY_CREATE_UNFAIR_ADVANTAGES":
            self.bar_countdown = tk.Label(self, text="-.--", bd=0, height=1, width=5,
                                          font=font_indicator, padx=0, pady=0,
                                          fg=self.wcfg["font_color_countdown"],
                                          bg=self.wcfg["bkg_color_countdown"])
            self.bar_countdown.grid(row=0, column=7, padx=0, pady=0, sticky="ns")
            self.bar_countdown.grid_remove()

        # Blue flag
        if self.wcfg["show_blue_flag"]:
            self.bar_blueflag = tk.Label(self, text=self.wcfg["blue_flag_text"], bd=0, height=1,
                                         width=len(self.wcfg["blue_flag_text"])+1,
                                         font=font_indicator, padx=0, pady=0,
                                         fg=self.wcfg["font_color_blue_flag"],
                                         bg=self.wcfg["bkg_color_blue_flag"])
            self.bar_blueflag.grid(row=0, column=8, padx=0, pady=0, sticky="ns")
            self.bar_blueflag.grid_remove()

        # Yellow flag
        if self.wcfg["show_yellow_flag"]:
            bar_style_y = {"font":font_indicator, "padx":0, "pady":0, "bd":0, "height":1, "width":3,
                           "fg":self.wcfg["font_color_yellow_flag"],
                           "bg":self.wcfg["bkg_color_yellow_flag"]}

            self.bar_yellow_s1 = tk.Label(self, bar_style_y, text="S1")
            self.bar_yellow_s1.grid(row=0, column=9, padx=0, pady=0, sticky="ns")
            self.bar_yellow_s1.grid_remove()
            self.bar_yellow_s2 = tk.Label(self, bar_style_y, text="S2")
            self.bar_yellow_s2.grid(row=0, column=10, padx=0, pady=0, sticky="ns")
            self.bar_yellow_s2.grid_remove()
            self.bar_yellow_s3 = tk.Label(self, bar_style_y, text="S3")
            self.bar_yellow_s3.grid(row=0, column=11, padx=0, pady=0, sticky="ns")
            self.bar_yellow_s3.grid_remove()

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
            pit_limiter, gear, speed, rpm, rpm_max, race_phase, curr_session = read_data.gear()

            # Start updating
            gear = calc.gear(gear)
            speed = calc.conv_speed(speed, self.wcfg["speed_unit"])
            rpm_safe = int(rpm_max * self.wcfg["rpm_safe_multiplier"])
            rpm_warn = int(rpm_max * self.wcfg["rpm_warn_multiplier"])
            rpm_color = self.color_rpm(rpm, rpm_safe, rpm_warn, rpm_max)

            # Gear update
            self.bar_gear_bg.config(bg=rpm_color)
            self.bar_gear.config(text=gear, bg=rpm_color)
            self.bar_gauge.config(text=f"{speed:03.0f}", bg=rpm_color)

            # RPM bar update
            if self.wcfg["show_rpm_bar"]:
                rpm_range = rpm_max - rpm_safe
                if rpm_range != 0:
                    rpmscale = max(rpm - rpm_safe, 0) / rpm_range * self.rpm_width
                else:
                    rpmscale = 0
                self.bar_rpm.coords(self.rect_rpm,
                                    rpmscale, self.wcfg["rpm_bar_edge_height"],
                                    rpm_range, self.wcfg["rpm_bar_height"])

            # Pit limiter update
            if pit_limiter and self.state_lm:
                self.bar_limiter.grid()
                self.state_lm = False
            elif not pit_limiter and not self.state_lm:
                self.bar_limiter.grid_remove()  # hide limiter indicator
                self.state_lm = True

            # Start lights update
            if self.wcfg["show_startlights"]:
                if race_phase == 4:
                    lap_stime, lap_etime = read_data.lap_timestamp()
                    self.bar_startlights.grid()
                    start_timer = max(lap_stime - lap_etime, 0)

                    if start_timer == 0:
                        self.bar_startlights.config(text=self.wcfg["green_flag_text"],
                                                    width=len(self.wcfg["green_flag_text"]) + 1,
                                                    bg=self.wcfg["bkg_color_green_flag"])
                    else:
                        self.bar_startlights.config(text=self.wcfg["red_lights_text"],
                                                    width=len(self.wcfg["red_lights_text"]) + 1,
                                                    bg=self.wcfg["bkg_color_red_lights"])
                    self.state_slight = True
                elif race_phase != 4:
                    if self.state_slight:
                        self.bar_startlights.config(text=self.wcfg["green_flag_text"],
                                                    width=len(self.wcfg["green_flag_text"]) + 1,
                                                    bg=self.wcfg["bkg_color_green_flag"])
                        if -(lap_stime - lap_etime) >= self.wcfg["green_flag_duration"]:
                            self.bar_startlights.grid_remove()
                            self.state_slight = False

            # Countdown update
            if self.wcfg["show_start_countdown"] == "THIS_MAY_CREATE_UNFAIR_ADVANTAGES":
                if race_phase == 4:
                    countdown_timer = max(read_data.lap_timestamp(), 0)
                    self.bar_countdown.config(text=f"{countdown_timer:.02f}")
                    self.bar_countdown.grid()
                    self.state_cd = True
                elif race_phase != 4:
                    if self.state_cd:
                        self.bar_countdown.grid_remove()  # hide countdown indicator at start
                        self.state_cd = False

            # Low fuel update
            if self.wcfg["show_low_fuel"]:
                if self.wcfg["low_fuel_for_race_only"] and curr_session > 9:
                    self.show_lowfuel()
                elif not self.wcfg["low_fuel_for_race_only"]:
                    self.show_lowfuel()

            # Flags update
            if self.wcfg["show_blue_flag"]:
                if self.wcfg["blue_flag_for_race_only"] and curr_session > 9:
                    self.show_blue()
                elif not self.wcfg["blue_flag_for_race_only"]:
                    self.show_blue()

            if self.wcfg["show_yellow_flag"]:
                if self.wcfg["yellow_flag_for_race_only"] and curr_session > 9:
                    self.show_yellow()
                elif not self.wcfg["yellow_flag_for_race_only"]:
                    self.show_yellow()

        else:
            if self.checked:
                self.checked = False
                # Reset state
                self.state_lm = True
                self.state_cd = False
                self.state_slight = False
                self.state_blue = True
                self.state_ys1 = True
                self.state_ys2 = True
                self.state_ys3 = True

                # Make sure all indicators are removed on ESC or hiding
                self.bar_limiter.grid_remove()
                if self.wcfg["show_startlights"]:
                    self.bar_startlights.grid_remove()
                if self.wcfg["show_start_countdown"] == "THIS_MAY_CREATE_UNFAIR_ADVANTAGES":
                    self.bar_countdown.grid_remove()
                if self.wcfg["show_low_fuel"]:
                    self.bar_lowfuel.grid_remove()
                if self.wcfg["show_blue_flag"]:
                    self.bar_blueflag.grid_remove()
                if self.wcfg["show_yellow_flag"]:
                    self.bar_yellow_s1.grid_remove()
                    self.bar_yellow_s2.grid_remove()
                    self.bar_yellow_s3.grid_remove()

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def color_rpm(self, rpm, rpm_safe, rpm_warn, rpm_max):
        """RPM indicator color"""
        if rpm < rpm_safe:
            color = self.wcfg["bkg_color"]
        elif rpm_safe <= rpm < rpm_warn:
            color = self.wcfg["bkg_color_rpm_safe"]
        elif rpm_warn <= rpm <= rpm_max:
            color = self.wcfg["bkg_color_rpm_warn"]
        else:
            color = self.wcfg["bkg_color_rpm_over_rev"]
        return color

    def show_lowfuel(self):
        """Show low fuel warning"""
        amount_curr, _, _, est_runlaps, _, _ = module.fuel_usage.output_data

        if amount_curr <= self.wcfg["low_fuel_volume_threshold"] and est_runlaps <= self.wcfg["low_fuel_lap_threshold"]:
            lowfuel_text = f"{amount_curr:.2f}"
            self.bar_lowfuel.config(text=lowfuel_text, width=len(lowfuel_text) + 1)
            self.bar_lowfuel.grid()
        else:
            self.bar_lowfuel.grid_remove()

    def show_blue(self):
        """Show blue flag"""
        blue = read_data.blue_flag()

        if blue == 6 and self.state_blue:
            self.bar_blueflag.grid()
            self.state_blue = False
        elif blue != 6 and not self.state_blue:
            self.bar_blueflag.grid_remove()
            self.state_blue = True

    def show_yellow(self):
        """Show yellow flag"""
        yellow_s1, yellow_s2, yellow_s3 = read_data.yellow_flag()

        if yellow_s1 == 1 and self.state_ys1:
            self.bar_yellow_s1.grid()
            self.state_ys1 = False
        elif yellow_s1 != 1 and not self.state_ys1:
            self.bar_yellow_s1.grid_remove()
            self.state_ys1 = True

        if yellow_s2 == 1 and self.state_ys2:
            self.bar_yellow_s2.grid()
            self.state_ys2 = False
        elif yellow_s2 != 1 and not self.state_ys2:
            self.bar_yellow_s2.grid_remove()
            self.state_ys2 = True

        if yellow_s3 == 1 and self.state_ys3:
            self.bar_yellow_s3.grid()
            self.state_ys3 = False
        elif yellow_s3 != 1 and not self.state_ys3:
            self.bar_yellow_s3.grid_remove()
            self.state_ys3 = True
