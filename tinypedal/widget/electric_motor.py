#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ..base import Widget

WIDGET_NAME = "electric_motor"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_m.width * 8

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_mt = self.wcfg["column_index_boost_motor_temp"]
        column_wt = self.wcfg["column_index_boost_water_temp"]
        column_mr = self.wcfg["column_index_boost_motor_rpm"]
        column_tq = self.wcfg["column_index_boost_motor_torque"]

        # Motor temperature
        if self.wcfg["show_boost_motor_temp"]:
            self.bar_motor_temp = QLabel("M TEMP")
            self.bar_motor_temp.setAlignment(Qt.AlignCenter)
            self.bar_motor_temp.setStyleSheet(
                f"color: {self.wcfg['font_color_boost_motor_temp']};"
                f"background: {self.wcfg['bkg_color_boost_motor_temp']};"
                f"min-width: {self.bar_width}px;"
            )

        # Motor water temperature
        if self.wcfg["show_boost_water_temp"]:
            self.bar_water_temp = QLabel("W TEMP")
            self.bar_water_temp.setAlignment(Qt.AlignCenter)
            self.bar_water_temp.setStyleSheet(
                f"color: {self.wcfg['font_color_boost_water_temp']};"
                f"background: {self.wcfg['bkg_color_boost_water_temp']};"
                f"min-width: {self.bar_width}px;"
            )

        # Motor rpm
        if self.wcfg["show_boost_motor_rpm"]:
            self.bar_motor_rpm = QLabel("RPM")
            self.bar_motor_rpm.setAlignment(Qt.AlignCenter)
            self.bar_motor_rpm.setStyleSheet(
                f"color: {self.wcfg['font_color_boost_motor_rpm']};"
                f"background: {self.wcfg['bkg_color_boost_motor_rpm']};"
                f"min-width: {self.bar_width}px;"
            )

        # Motor torque
        if self.wcfg["show_boost_motor_torque"]:
            self.bar_motor_torque = QLabel("TORQUE")
            self.bar_motor_torque.setAlignment(Qt.AlignCenter)
            self.bar_motor_torque.setStyleSheet(
                f"color: {self.wcfg['font_color_boost_motor_torque']};"
                f"background: {self.wcfg['bkg_color_boost_motor_torque']};"
                f"min-width: {self.bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_boost_motor_temp"]:
                layout.addWidget(self.bar_motor_temp, column_mt, 0)
            if self.wcfg["show_boost_water_temp"]:
                layout.addWidget(self.bar_water_temp, column_wt, 0)
            if self.wcfg["show_boost_motor_rpm"]:
                layout.addWidget(self.bar_motor_rpm, column_mr, 0)
            if self.wcfg["show_boost_motor_torque"]:
                layout.addWidget(self.bar_motor_torque, column_tq, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_boost_motor_temp"]:
                layout.addWidget(self.bar_motor_temp, 0, column_mt)
            if self.wcfg["show_boost_water_temp"]:
                layout.addWidget(self.bar_water_temp, 0, column_wt)
            if self.wcfg["show_boost_motor_rpm"]:
                layout.addWidget(self.bar_motor_rpm, 0, column_mr)
            if self.wcfg["show_boost_motor_torque"]:
                layout.addWidget(self.bar_motor_torque, 0, column_tq)
        self.setLayout(layout)

        # Last data
        self.last_motor_torque = None
        self.last_motor_rpm = None
        self.last_motor_temp = None
        self.last_water_temp = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Motor temperature
            if self.wcfg["show_boost_motor_temp"]:
                motor_temp = round(api.read.emotor.motor_temperature(), 1)
                self.update_motor_temp(motor_temp, self.last_motor_temp)
                self.last_motor_temp = motor_temp

            # Water temperature
            if self.wcfg["show_boost_water_temp"]:
                water_temp = round(api.read.emotor.water_temperature(), 1)
                self.update_water_temp(water_temp, self.last_water_temp)
                self.last_water_temp = water_temp

            # Motor rpm
            if self.wcfg["show_boost_motor_rpm"]:
                motor_rpm = int(api.read.emotor.rpm())
                self.update_motor_rpm(motor_rpm, self.last_motor_rpm)
                self.last_motor_rpm = motor_rpm

            # Motor torque
            if self.wcfg["show_boost_motor_torque"]:
                motor_torque = round(api.read.emotor.torque(), 2)
                self.update_motor_torque(motor_torque, self.last_motor_torque)
                self.last_motor_torque = motor_torque

    # GUI update methods
    def update_motor_temp(self, curr, last):
        """Motor temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_motor"]:
                color = (f"color: {self.wcfg['font_color_boost_motor_temp']};"
                         f"background: {self.wcfg['bkg_color_boost_motor_temp']};")
            else:
                color = (f"color: {self.wcfg['font_color_boost_motor_temp']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_motor_temp.setText(f"M{format_text}")
            self.bar_motor_temp.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_water_temp(self, curr, last):
        """Water temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_water"]:
                color = (f"color: {self.wcfg['font_color_boost_water_temp']};"
                         f"background: {self.wcfg['bkg_color_boost_water_temp']};")
            else:
                color = (f"color: {self.wcfg['font_color_boost_water_temp']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_water_temp.setText(f"W{format_text}")
            self.bar_water_temp.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_motor_rpm(self, curr, last):
        """Motor rpm"""
        if curr != last:
            format_text = f"{curr}"[:5].rjust(5)
            self.bar_motor_rpm.setText(f"{format_text}rpm")

    def update_motor_torque(self, curr, last):
        """Motor torque"""
        if curr != last:
            format_text = f"{curr:.02f}"[:6].rjust(6)
            self.bar_motor_torque.setText(f"{format_text}Nm")
