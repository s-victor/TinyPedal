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
Hybrid Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "hybrid"


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
        font_hybrid = tkfont.Font(family=self.wcfg["font_name"],
                                  size=-self.wcfg["font_size"],
                                  weight=self.wcfg["font_weight"])

        column_bc = self.wcfg["column_index_battery_charge"]
        column_bu = self.wcfg["column_index_battery_drain"]
        column_br = self.wcfg["column_index_battery_regen"]
        column_mt = self.wcfg["column_index_boost_motor_temp"]
        column_wt = self.wcfg["column_index_boost_water_temp"]
        column_mr = self.wcfg["column_index_boost_motor_rpm"]
        column_tq = self.wcfg["column_index_boost_motor_torque"]
        column_ms = self.wcfg["column_index_boost_motor_state"]

        # Draw label
        bar_style  = {"text":"n/a", "bd":0, "height":1, "width":8,
                      "padx":bar_padx, "pady":0, "font":font_hybrid}

        if self.wcfg["show_battery_charge"]:
            self.bar_battery_charge = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_battery_charge"],
                bg=self.wcfg["bkg_color_battery_charge"])

        if self.wcfg["show_battery_drain"]:
            self.bar_battery_drain = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_battery_drain"],
                bg=self.wcfg["bkg_color_battery_drain"])

        if self.wcfg["show_battery_regen"]:
            self.bar_battery_regen = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_battery_regen"],
                bg=self.wcfg["bkg_color_battery_regen"])

        if self.wcfg["show_boost_motor_temp"]:
            self.bar_motor_temp = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_boost_motor_temp"],
                bg=self.wcfg["bkg_color_boost_motor_temp"])

        if self.wcfg["show_boost_water_temp"]:
            self.bar_water_temp = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_boost_water_temp"],
                bg=self.wcfg["bkg_color_boost_water_temp"])

        if self.wcfg["show_boost_motor_rpm"]:
            self.bar_motor_rpm = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_boost_motor_rpm"],
                bg=self.wcfg["bkg_color_boost_motor_rpm"])

        if self.wcfg["show_boost_motor_torque"]:
            self.bar_motor_torque = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_boost_motor_torque"],
                bg=self.wcfg["bkg_color_boost_motor_torque"])

        if self.wcfg["show_boost_motor_state"]:
            self.bar_motor_state = tk.Label(
                self, bar_style,
                fg=self.wcfg["font_color_boost_motor_state"],
                bg=self.wcfg["bkg_color_boost_motor_state"])

        if self.wcfg["layout"] == "0":
            # Vertical layout
            if self.wcfg["show_battery_charge"]:
                self.bar_battery_charge.grid(row=column_bc, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_battery_drain"]:
                self.bar_battery_drain.grid(row=column_bu, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_battery_regen"]:
                self.bar_battery_regen.grid(row=column_br, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_boost_motor_temp"]:
                self.bar_motor_temp.grid(row=column_mt, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_boost_water_temp"]:
                self.bar_water_temp.grid(row=column_wt, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_boost_motor_rpm"]:
                self.bar_motor_rpm.grid(row=column_mr, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_boost_motor_torque"]:
                self.bar_motor_torque.grid(row=column_tq, column=0, padx=0, pady=(0, bar_gap))
            if self.wcfg["show_boost_motor_state"]:
                self.bar_motor_state.grid(row=column_ms, column=0, padx=0, pady=(0, bar_gap))
        else:
            # Horizontal layout
            if self.wcfg["show_battery_charge"]:
                self.bar_battery_charge.grid(row=0, column=column_bc, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_battery_drain"]:
                self.bar_battery_drain.grid(row=0, column=column_bu, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_battery_regen"]:
                self.bar_battery_regen.grid(row=0, column=column_br, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_boost_motor_temp"]:
                self.bar_motor_temp.grid(row=0, column=column_mt, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_boost_water_temp"]:
                self.bar_water_temp.grid(row=0, column=column_wt, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_boost_motor_rpm"]:
                self.bar_motor_rpm.grid(row=0, column=column_mr, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_boost_motor_torque"]:
                self.bar_motor_torque.grid(row=0, column=column_tq, padx=(0, bar_gap), pady=0)
            if self.wcfg["show_boost_motor_state"]:
                self.bar_motor_state.grid(row=0, column=column_ms, padx=(0, bar_gap), pady=0)

        # Last data
        self.last_lap_stime = 0  # last lap start time

        self.last_battery_charge = None
        self.last_battery_drain = None
        self.last_battery_regen = None
        self.last_motor_torque = None
        self.last_motor_rpm = None
        self.last_motor_temp = None
        self.last_water_temp = None
        self.last_motor_active_timer = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read boost motor data
            (motor_torque, motor_rpm, motor_temp, water_temp
             ) = read_data.electric()

            # Read battery data from battery module
            (battery_charge, battery_delta, motor_active_timer, _, _
             ) = module.battery_usage.output_data

            lap_stime, lap_etime = read_data.lap_timestamp()

            # Battery charge & usage
            if self.wcfg["show_battery_charge"]:
                self.update_battery_charge(battery_charge, self.last_battery_charge)

            if lap_stime != self.last_lap_stime:
                elapsed_time = lap_etime - lap_stime
                if elapsed_time >= self.wcfg["freeze_duration"] or elapsed_time < 0:
                    self.last_lap_stime = lap_stime
                battery_drain = battery_delta[2]
                battery_regen = battery_delta[3]
            else:
                battery_drain = battery_delta[0]
                battery_regen = battery_delta[1]

            if self.wcfg["show_battery_drain"]:
                self.update_battery_drain(battery_drain, self.last_battery_drain)
                self.last_battery_drain = battery_drain

            if self.wcfg["show_battery_regen"]:
                self.update_battery_regen(battery_regen, self.last_battery_regen)
                self.last_battery_regen = battery_regen

            self.last_battery_charge = battery_charge

            # Motor temperature
            if self.wcfg["show_boost_motor_temp"]:
                motor_temp = round(motor_temp, 1)
                self.update_motor_temp(motor_temp, self.last_motor_temp)
                self.last_motor_temp = motor_temp

            # Water temperature
            if self.wcfg["show_boost_water_temp"]:
                water_temp = round(water_temp, 1)
                self.update_water_temp(water_temp, self.last_water_temp)
                self.last_water_temp = water_temp

            # Motor rpm
            if self.wcfg["show_boost_motor_rpm"]:
                motor_rpm = int(motor_rpm)
                self.update_motor_rpm(motor_rpm, self.last_motor_rpm)
                self.last_motor_rpm = motor_rpm

            # Motor torque
            if self.wcfg["show_boost_motor_torque"]:
                motor_torque = round(motor_torque, 2)
                self.update_motor_torque(motor_torque, self.last_motor_torque)
                self.last_motor_torque = motor_torque

            # Motor state
            if self.wcfg["show_boost_motor_state"]:
                self.update_motor_state(motor_active_timer, self.last_motor_active_timer)
                self.last_motor_active_timer = motor_active_timer

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_battery_charge(self, curr, last):
        """Battery charge"""
        if curr != last:
            if curr > self.wcfg["low_battery_threshold"]:
                bgcolor = self.wcfg["bkg_color_battery_charge"]
            else:
                bgcolor = self.wcfg["warning_color_low_battery"]

            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_charge.config(text=f"B{format_text}", bg=bgcolor)

    def update_battery_drain(self, curr, last):
        """Battery drain"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_drain.config(text=f"U{format_text}")

    def update_battery_regen(self, curr, last):
        """Battery regen"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_regen.config(text=f"R{format_text}")

    def update_motor_temp(self, curr, last):
        """Motor temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_motor"]:
                bgcolor = self.wcfg["bkg_color_boost_motor_temp"]
            else:
                bgcolor = self.wcfg["warning_color_overheat"]

            if self.wcfg["temp_unit"] == "1":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_motor_temp.config(text=f"M{format_text}", bg=bgcolor)

    def update_water_temp(self, curr, last):
        """Water temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_water"]:
                bgcolor = self.wcfg["bkg_color_boost_water_temp"]
            else:
                bgcolor = self.wcfg["warning_color_overheat"]

            if self.wcfg["temp_unit"] == "1":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_water_temp.config(text=f"W{format_text}", bg=bgcolor)

    def update_motor_rpm(self, curr, last):
        """Motor rpm"""
        if curr != last:
            format_text = f"{curr}"[:5].rjust(5)
            self.bar_motor_rpm.config(text=f"{format_text}rpm")

    def update_motor_torque(self, curr, last):
        """Motor torque"""
        if curr != last:
            format_text = f"{curr:.02f}"[:6].rjust(6)
            self.bar_motor_torque.config(text=f"{format_text}Nm")

    def update_motor_state(self, curr, last):
        """Motor state"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_motor_state.config(text=f"{format_text}s")
