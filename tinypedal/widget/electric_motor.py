#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
Electric motor Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "electric_motor"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        bar_width = font_m.width * 8 + bar_padx

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Motor temperature
        if self.wcfg["show_motor_temperature"]:
            self.bar_style_motor = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_motor_temperature"],
                    bg_color=self.wcfg["bkg_color_motor_temperature"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_motor_temperature"],
                    bg_color=self.wcfg["warning_color_overheat"])
            )
            self.bar_motor = self.set_qlabel(
                text="M TEMP",
                style=self.bar_style_motor[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_motor,
                column=self.wcfg["column_index_motor_temperature"],
            )

        # Motor water temperature
        if self.wcfg["show_water_temperature"]:
            self.bar_style_water = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_water_temperature"],
                    bg_color=self.wcfg["bkg_color_water_temperature"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_water_temperature"],
                    bg_color=self.wcfg["warning_color_overheat"])
            )
            self.bar_water = self.set_qlabel(
                text="W TEMP",
                style=self.bar_style_water[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_water,
                column=self.wcfg["column_index_water_temperature"],
            )

        # Motor rpm
        if self.wcfg["show_rpm"]:
            bar_style_rpm = self.set_qss(
                fg_color=self.wcfg["font_color_rpm"],
                bg_color=self.wcfg["bkg_color_rpm"]
            )
            self.bar_rpm = self.set_qlabel(
                text="RPM",
                style=bar_style_rpm,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_rpm,
                column=self.wcfg["column_index_rpm"],
            )

        # Motor torque
        if self.wcfg["show_torque"]:
            bar_style_torque = self.set_qss(
                fg_color=self.wcfg["font_color_torque"],
                bg_color=self.wcfg["bkg_color_torque"]
            )
            self.bar_torque = self.set_qlabel(
                text="TORQUE",
                style=bar_style_torque,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_torque,
                column=self.wcfg["column_index_torque"],
            )

        # Motor power
        if self.wcfg["show_power"]:
            bar_style_power = self.set_qss(
                fg_color=self.wcfg["font_color_power"],
                bg_color=self.wcfg["bkg_color_power"]
            )
            self.bar_power = self.set_qlabel(
                text="POWER",
                style=bar_style_power,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_power,
                column=self.wcfg["column_index_power"],
            )

        # Last data
        self.last_temp_motor = None
        self.last_temp_water = None
        self.last_rpm = None
        self.last_torque = None
        self.last_power = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Motor temperature
            if self.wcfg["show_motor_temperature"]:
                temp_motor = round(api.read.emotor.motor_temperature(), 2)
                self.update_motor(temp_motor, self.last_temp_motor)
                self.last_temp_motor = temp_motor

            # Water temperature
            if self.wcfg["show_water_temperature"]:
                temp_water = round(api.read.emotor.water_temperature(), 2)
                self.update_water(temp_water, self.last_temp_water)
                self.last_temp_water = temp_water

            # Motor rpm
            if self.wcfg["show_rpm"]:
                rpm = int(api.read.emotor.rpm())
                self.update_rpm(rpm, self.last_rpm)
                self.last_rpm = rpm

            # Motor torque
            if self.wcfg["show_torque"]:
                torque = round(api.read.emotor.torque(), 2)
                self.update_torque(torque, self.last_torque)
                self.last_torque = torque

            # Motor power
            if self.wcfg["show_power"]:
                power = round(calc.engine_power(
                    api.read.emotor.torque(), api.read.emotor.rpm()), 2)
                self.update_power(power, self.last_power)
                self.last_power = power

    # GUI update methods
    def update_motor(self, curr, last):
        """Motor temperature"""
        if curr != last:
            # Check overheat before conversion
            is_overheat = (curr >= self.wcfg["overheat_threshold_motor"])
            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            self.bar_motor.setText(f"M{curr: >6.1f}°")
            self.bar_motor.setStyleSheet(self.bar_style_motor[is_overheat])

    def update_water(self, curr, last):
        """Water temperature"""
        if curr != last:
            # Check overheat before conversion
            is_overheat = (curr >= self.wcfg["overheat_threshold_water"])
            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            self.bar_water.setText(f"W{curr: >6.1f}°")
            self.bar_water.setStyleSheet(self.bar_style_water[is_overheat])

    def update_rpm(self, curr, last):
        """Motor rpm"""
        if curr != last:
            self.bar_rpm.setText(f"{curr: >5}rpm")

    def update_torque(self, curr, last):
        """Motor torque"""
        if curr != last:
            text = f"{curr: >6.2f}"[:6]
            self.bar_torque.setText(f"{text}Nm")

    def update_power(self, curr, last):
        """Motor power"""
        if curr != last:
            self.bar_power.setText(self.power_units(curr))

    # Additional methods
    def power_units(self, power):
        """Power units"""
        if self.cfg.units["power_unit"] == "Kilowatt":
            text = f"{power: >6.2f}"[:6]
            return f"{text}kW"
        if self.cfg.units["power_unit"] == "Horsepower":
            text = f"{calc.kw2hp(power): >6.2f}"[:6]
            return f"{text}hp"
        text = f"{calc.kw2ps(power): >6.2f}"[:6]
        return f"{text}ps"
