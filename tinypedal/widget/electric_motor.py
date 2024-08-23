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
from PySide2.QtWidgets import QGridLayout, QLabel

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
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        bar_width = f"min-width: {font_m.width * 8 + bar_padx}px;"

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"{bar_width}"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_motor = self.wcfg["column_index_motor_temperature"]
        column_water = self.wcfg["column_index_water_temperature"]
        column_rpm = self.wcfg["column_index_rpm"]
        column_torque = self.wcfg["column_index_torque"]
        column_power = self.wcfg["column_index_power"]

        # Motor temperature
        if self.wcfg["show_motor_temperature"]:
            self.bar_motor = QLabel("M TEMP")
            self.bar_motor.setAlignment(Qt.AlignCenter)
            self.bar_motor.setStyleSheet(
                f"color: {self.wcfg['font_color_motor_temperature']};"
                f"background: {self.wcfg['bkg_color_motor_temperature']};"
            )

        # Motor water temperature
        if self.wcfg["show_water_temperature"]:
            self.bar_water = QLabel("W TEMP")
            self.bar_water.setAlignment(Qt.AlignCenter)
            self.bar_water.setStyleSheet(
                f"color: {self.wcfg['font_color_water_temperature']};"
                f"background: {self.wcfg['bkg_color_water_temperature']};"
            )

        # Motor rpm
        if self.wcfg["show_rpm"]:
            self.bar_rpm = QLabel("RPM")
            self.bar_rpm.setAlignment(Qt.AlignCenter)
            self.bar_rpm.setStyleSheet(
                f"color: {self.wcfg['font_color_rpm']};"
                f"background: {self.wcfg['bkg_color_rpm']};"
            )

        # Motor torque
        if self.wcfg["show_torque"]:
            self.bar_torque = QLabel("TORQUE")
            self.bar_torque.setAlignment(Qt.AlignCenter)
            self.bar_torque.setStyleSheet(
                f"color: {self.wcfg['font_color_torque']};"
                f"background: {self.wcfg['bkg_color_torque']};"
            )

        # Motor power
        if self.wcfg["show_power"]:
            self.bar_power = QLabel("POWER")
            self.bar_power.setAlignment(Qt.AlignCenter)
            self.bar_power.setStyleSheet(
                f"color: {self.wcfg['font_color_power']};"
                f"background: {self.wcfg['bkg_color_power']};"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_motor_temperature"]:
                layout.addWidget(self.bar_motor, column_motor, 0)
            if self.wcfg["show_water_temperature"]:
                layout.addWidget(self.bar_water, column_water, 0)
            if self.wcfg["show_rpm"]:
                layout.addWidget(self.bar_rpm, column_rpm, 0)
            if self.wcfg["show_torque"]:
                layout.addWidget(self.bar_torque, column_torque, 0)
            if self.wcfg["show_power"]:
                layout.addWidget(self.bar_power, column_power, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_motor_temperature"]:
                layout.addWidget(self.bar_motor, 0, column_motor)
            if self.wcfg["show_water_temperature"]:
                layout.addWidget(self.bar_water, 0, column_water)
            if self.wcfg["show_rpm"]:
                layout.addWidget(self.bar_rpm, 0, column_rpm)
            if self.wcfg["show_torque"]:
                layout.addWidget(self.bar_torque, 0, column_torque)
            if self.wcfg["show_power"]:
                layout.addWidget(self.bar_power, 0, column_power)
        self.setLayout(layout)

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
                temp_motor = round(api.read.emotor.motor_temperature(), 1)
                self.update_motor(temp_motor, self.last_temp_motor)
                self.last_temp_motor = temp_motor

            # Water temperature
            if self.wcfg["show_water_temperature"]:
                temp_water = round(api.read.emotor.water_temperature(), 1)
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
            if curr < self.wcfg["overheat_threshold_motor"]:
                color = (f"color: {self.wcfg['font_color_motor_temperature']};"
                         f"background: {self.wcfg['bkg_color_motor_temperature']};")
            else:
                color = (f"color: {self.wcfg['font_color_motor_temperature']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.1f}°"[:7].rjust(7)
            self.bar_motor.setText(f"M{format_text}")
            self.bar_motor.setStyleSheet(color)

    def update_water(self, curr, last):
        """Water temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_water"]:
                color = (f"color: {self.wcfg['font_color_water_temperature']};"
                         f"background: {self.wcfg['bkg_color_water_temperature']};")
            else:
                color = (f"color: {self.wcfg['font_color_water_temperature']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.1f}°"[:7].rjust(7)
            self.bar_water.setText(f"W{format_text}")
            self.bar_water.setStyleSheet(color)

    def update_rpm(self, curr, last):
        """Motor rpm"""
        if curr != last:
            format_text = f"{curr}"[:5].rjust(5)
            self.bar_rpm.setText(f"{format_text}rpm")

    def update_torque(self, curr, last):
        """Motor torque"""
        if curr != last:
            format_text = f"{curr:.2f}"[:6].rjust(6)
            self.bar_torque.setText(f"{format_text}Nm")

    def update_power(self, curr, last):
        """Motor power"""
        if curr != last:
            self.bar_power.setText(self.power_units(curr))

    # Additional methods
    def power_units(self, power):
        """Power units"""
        if self.cfg.units["power_unit"] == "Kilowatt":
            text = f"{power:.2f}"[:6].rjust(6)
            return f"{text}kW"
        if self.cfg.units["power_unit"] == "Horsepower":
            text = f"{calc.kw2hp(power):.2f}"[:6].rjust(6)
            return f"{text}hp"
        text = f"{calc.kw2ps(power):.2f}"[:6].rjust(6)
        return f"{text}ps"
