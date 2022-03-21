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

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class Gear(Widget, MouseEvent):
    """Draw gear widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Gear Widget")
        self.attributes("-alpha", cfg.gear["opacity"])

        # Config size & position
        self.geometry(f"+{cfg.gear['position_x']}+{cfg.gear['position_y']}")

        # Config style & variable
        font_gear = tkfont.Font(family=cfg.gear["font_name"],
                                size=-cfg.gear["font_size"],
                                weight=cfg.gear["font_weight_gear"])
        font_gauge = tkfont.Font(family=cfg.gear["font_name"],
                                 size=-cfg.gear["font_size"],
                                 weight=cfg.gear["font_weight_gauge"])
        font_gauge_small = tkfont.Font(family=cfg.gear["font_name"],
                                       size=-int(cfg.gear["font_size"]*0.35),
                                       weight=cfg.gear["font_weight_gauge"])

        # Draw label
        self.bar_gear_bg = tk.Canvas(self, bd=0, highlightthickness=0, height=0, width=0,
                                     bg=cfg.gear["bkg_color"])
        self.bar_gear_bg.grid(row=0, column=0, columnspan=10, padx=0, pady=0, sticky="wens")

        self.bar_gear = tk.Label(self, text="N", bd=0, height=1, width=2,
                                 font=font_gear, padx=0, pady=0,
                                 fg=cfg.gear["font_color_gear"],
                                 bg=cfg.gear["bkg_color"])

        self.bar_limiter = tk.Label(self, text=cfg.gear["speed_limiter_text"], bd=0, height=1,
                                    width=len(cfg.gear["speed_limiter_text"])+1,
                                    font=font_gear, padx=0, pady=0,
                                    fg="#111111", bg="#FF2200")
        self.bar_limiter.grid(row=0, column=5, padx=0, pady=0, sticky="ns")

        if cfg.gear["layout"] == "0":
            self.bar_gear.grid(row=0, column=0, padx=0, pady=0)

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=4,
                                      font=font_gauge, padx=0, pady=0,
                                      fg=cfg.gear["font_color_gauge"],
                                      bg=cfg.gear["bkg_color"])
            self.bar_gauge.grid(row=0, column=1, padx=0, pady=0, sticky="ns")

            self.rpm_width = self.bar_gear.winfo_reqwidth() + self.bar_gauge.winfo_reqwidth()
        else:
            self.bar_gear.grid(row=0, column=0,
                               padx=0, pady=(0, int(cfg.gear["font_size"] * 0.45)))

            self.bar_gauge = tk.Label(self, text="000", bd=0, height=1, width=3,
                                      font=font_gauge_small, padx=0, pady=0,
                                      fg=cfg.gear["font_color_gauge"],
                                      bg=cfg.gear["bkg_color"])
            self.bar_gauge.grid(row=0, column=0, sticky="wes",
                                padx=0, pady=(0, int(cfg.gear["font_size"] * 0.15)))

            self.rpm_width = self.bar_gear.winfo_reqwidth()

        if cfg.gear["show_rpm_bar"]:
            self.bar_rpm = tk.Canvas(self, bd=0, highlightthickness=0,
                                     height=cfg.gear["rpm_bar_height"], width=self.rpm_width,
                                     bg=cfg.gear["bkg_color_rpm_bar"])
            self.bar_rpm.grid(row=1, column=0, columnspan=2,
                              padx=0, pady=(cfg.gear["rpm_bar_gap"], 0))
            # Used as transparent mask
            self.rect_rpm = self.bar_rpm.create_rectangle(
                            0, 0, 0, 0, fill="#000002", outline="")

        self.update_gear()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.load()
        cfg.gear["position_x"] = str(self.winfo_x())
        cfg.gear["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_gear(self):
        """Update gear

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.gear["enable"]:
            # Read gear data
            pit_limiter, gear, speed, rpm, rpm_max = read_data.gear()
            gear = calc.gear(gear)
            speed = calc.conv_speed(speed, cfg.gear["speed_unit"])
            rpm_safe = int(rpm_max * cfg.gear["rpm_safe_multiplier"])
            rpm_warn = int(rpm_max * cfg.gear["rpm_warn_multiplier"])
            rpm_color = self.color_rpm(rpm, rpm_safe, rpm_warn, rpm_max)

            # Gear update
            self.bar_gear_bg.config(bg=rpm_color)
            self.bar_gear.config(text=gear, bg=rpm_color)
            self.bar_gauge.config(text=speed, bg=rpm_color)

            # Pit limiter update
            if pit_limiter:
                self.bar_limiter.grid()
            else:
                self.bar_limiter.grid_remove()  # hide limiter indicator

            if cfg.gear["show_rpm_bar"]:
                # RPM bar update
                rpm_range = rpm_max - rpm_safe
                try:
                    rpmscale = max(rpm - rpm_safe, 0) / rpm_range * self.rpm_width
                except ZeroDivisionError:
                    rpmscale = 0
                self.bar_rpm.coords(self.rect_rpm,
                                    rpmscale, cfg.gear["rpm_bar_edge_height"],
                                    rpm_range, cfg.gear["rpm_bar_height"])

        # Update rate
        self.after(cfg.gear["update_delay"], self.update_gear)

    # Additional methods
    @staticmethod
    def color_rpm(rpm, rpm_safe, rpm_warn, rpm_max):
        """RPM indicator color"""
        if rpm < rpm_safe:
            color = cfg.gear["bkg_color"]
        elif rpm_safe <= rpm < rpm_warn:
            color = cfg.gear["bkg_color_rpm_safe"]
        elif rpm_warn <= rpm <= rpm_max:
            color = cfg.gear["bkg_color_rpm_warn"]
        else:
            color = cfg.gear["bkg_color_rpm_over_rev"]
        return color
