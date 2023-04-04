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
P2P Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "p2p"


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
        font_p2p = tkfont.Font(family=self.wcfg["font_name"],
                                  size=-self.wcfg["font_size"],
                                  weight=self.wcfg["font_weight"])

        column_bc = self.wcfg["column_index_battery_charge"]
        column_ms = self.wcfg["column_index_boost_motor_state"]

        # Draw label
        bar_style  = {"bd":0, "height":1,
                      "padx":bar_padx, "pady":0, "font":font_p2p}

        if self.wcfg["show_battery_charge"]:
            self.bar_battery_charge = tk.Label(
                self, bar_style, text="P2P",
                fg=self.wcfg["font_color_battery_charge"],
                bg=self.wcfg["bkg_color_battery_charge"])

        if self.wcfg["show_boost_motor_state"]:
            self.bar_motor_state = tk.Label(
                self, bar_style, text="TIMER",
                fg=self.wcfg["font_color_boost_motor_state"],
                bg=self.wcfg["bkg_color_boost_motor_state"])

        # Horizontal layout
        if self.wcfg["show_battery_charge"]:
            self.bar_battery_charge.grid(row=0, column=column_bc, padx=(0, bar_gap), pady=0)
        if self.wcfg["show_boost_motor_state"]:
            self.bar_motor_state.grid(row=0, column=column_ms, padx=(0, bar_gap), pady=0)

        # Last data
        self.last_battery_charge = None
        self.last_motor_active_timer = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read battery data from battery module
            (battery_charge, _, motor_active_timer, motor_inactive_timer, motor_state
             ) = module.battery_usage.output_data

            # Read p2p data
            mgear, speed, throttle = read_data.p2p()

            alt_active_state = (
                mgear >= self.wcfg["activation_threshold_gear"] and
                speed*3.6 > self.wcfg["activation_threshold_speed"] and
                throttle > 0
                )

            # Battery charge & usage
            if self.wcfg["show_battery_charge"]:
                battery_charge = [battery_charge, motor_state, alt_active_state,
                                  motor_active_timer, motor_inactive_timer]
                self.update_battery_charge(battery_charge, self.last_battery_charge)
                self.last_battery_charge = battery_charge

            # Motor state
            if self.wcfg["show_boost_motor_state"]:
                motor_active_timer = [motor_active_timer, motor_state]
                self.update_motor_state(motor_active_timer, self.last_motor_active_timer)
                self.last_motor_active_timer = motor_active_timer

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_battery_charge(self, curr, last):
        """Battery charge"""
        if curr != last:
            # State = active
            if curr[1] == 2:
                bgcolor = self.wcfg["bkg_color_battery_drain"]
            # State = regen
            elif curr[1] == 3:
                bgcolor = self.wcfg["bkg_color_battery_regen"]
            # alt_active_state True, motor_active_timer, motor_inactive_timer
            elif (curr[2] and
                  curr[4] >= self.wcfg["minimum_activation_time_delay"] and
                  curr[3] < self.wcfg["maximum_activation_time_per_lap"] - 0.05):
                bgcolor = self.wcfg["bkg_color_battery_charge"]
            else:
                bgcolor = self.wcfg["bkg_color_boost_motor_inactive"]

            if curr[0] < 99.5:
                format_text = f"±{curr[0]:02.0f}"
            else:
                format_text = "MAX"
            self.bar_battery_charge.config(
                text=format_text, bg=bgcolor)

    def update_motor_state(self, curr, last):
        """Motor state"""
        if curr != last:
            if curr[1] != 2:
                fgcolor = self.wcfg["font_color_boost_motor_inactive"]
            else:
                fgcolor = self.wcfg["font_color_boost_motor_state"]

            format_text = f"{curr[0]:.01f}"
            self.bar_motor_state.config(text=format_text, fg=fgcolor)
