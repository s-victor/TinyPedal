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
Engine Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget

WIDGET_NAME = "engine"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        font_w = QFontMetrics(self.font).averageCharWidth()

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_w * 8

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_oil = self.wcfg["column_index_oil"]
        column_water = self.wcfg["column_index_water"]
        column_turbo = self.wcfg["column_index_turbo"]
        column_rpm = self.wcfg["column_index_rpm"]

        # Oil temperature
        if self.wcfg["show_temperature"]:
            self.bar_oil = QLabel("Oil T")
            self.bar_oil.setAlignment(Qt.AlignCenter)
            self.bar_oil.setStyleSheet(
                f"color: {self.wcfg['font_color_oil']};"
                f"background: {self.wcfg['bkg_color_oil']};"
                f"min-width: {self.bar_width}px;"
            )

            # Water temperature
            self.bar_water = QLabel("Water T")
            self.bar_water.setAlignment(Qt.AlignCenter)
            self.bar_water.setStyleSheet(
                f"color: {self.wcfg['font_color_water']};"
                f"background: {self.wcfg['bkg_color_water']};"
                f"min-width: {self.bar_width}px;"
            )

        # Turbo pressure
        if self.wcfg["show_turbo_pressure"]:
            self.bar_turbo = QLabel("Turbo")
            self.bar_turbo.setAlignment(Qt.AlignCenter)
            self.bar_turbo.setStyleSheet(
                f"color: {self.wcfg['font_color_turbo']};"
                f"background: {self.wcfg['bkg_color_turbo']};"
                f"min-width: {self.bar_width}px;"
            )

        # RPM
        if self.wcfg["show_rpm"]:
            self.bar_rpm = QLabel("RPM")
            self.bar_rpm.setAlignment(Qt.AlignCenter)
            self.bar_rpm.setStyleSheet(
                f"color: {self.wcfg['font_color_rpm']};"
                f"background: {self.wcfg['bkg_color_rpm']};"
                f"min-width: {self.bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_temperature"]:
                layout.addWidget(self.bar_oil, column_oil, 0)
                layout.addWidget(self.bar_water, column_water, 0)
            if self.wcfg["show_turbo_pressure"]:
                layout.addWidget(self.bar_turbo, column_turbo, 0)
            if self.wcfg["show_rpm"]:
                layout.addWidget(self.bar_rpm, column_rpm, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_temperature"]:
                layout.addWidget(self.bar_oil, 0, column_oil)
                layout.addWidget(self.bar_water, 0, column_water)
            if self.wcfg["show_turbo_pressure"]:
                layout.addWidget(self.bar_turbo, 0, column_turbo)
            if self.wcfg["show_rpm"]:
                layout.addWidget(self.bar_rpm, 0, column_rpm)
        self.setLayout(layout)

        # Last data
        self.last_temp_oil = None
        self.last_temp_water = None
        self.last_e_turbo = None
        self.last_e_rpm = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read Engine data
            temp_oil, temp_water, e_turbo, e_rpm = read_data.engine()

            if self.wcfg["show_temperature"]:
                # Oil temperature
                temp_oil = round(temp_oil, 1)
                self.update_oil(temp_oil, self.last_temp_oil)
                self.last_temp_oil = temp_oil

                # Water temperature
                temp_water = round(temp_water, 1)
                self.update_water(temp_water, self.last_temp_water)
                self.last_temp_water = temp_water

            # Turbo pressure
            if self.wcfg["show_turbo_pressure"]:
                self.update_turbo(e_turbo, self.last_e_turbo)
                self.last_e_turbo = e_turbo

            # Engine RPM
            if self.wcfg["show_rpm"]:
                self.update_rpm(e_rpm, self.last_e_rpm)
                self.last_e_rpm = e_rpm

    # GUI update methods
    def update_oil(self, curr, last):
        """Oil temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_oil"]:
                color = (f"color: {self.wcfg['font_color_oil']};"
                         f"background: {self.wcfg['bkg_color_oil']};")
            else:
                color = (f"color: {self.wcfg['font_color_oil']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_oil.setText(f"O{format_text}")
            self.bar_oil.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_water(self, curr, last):
        """Water temperature"""
        if curr != last:
            if curr < self.wcfg["overheat_threshold_water"]:
                color = (f"color: {self.wcfg['font_color_water']};"
                         f"background: {self.wcfg['bkg_color_water']};")
            else:
                color = (f"color: {self.wcfg['font_color_water']};"
                         f"background: {self.wcfg['warning_color_overheat']};")

            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            format_text = f"{curr:.01f}°"[:7].rjust(7)
            self.bar_water.setText(f"W{format_text}")
            self.bar_water.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_turbo(self, curr, last):
        """Turbo pressure"""
        if curr != last:
            self.bar_turbo.setText(self.pressure_units(curr * 0.001))

    def update_rpm(self, curr, last):
        """Engine RPM"""
        if curr != last:
            self.bar_rpm.setText(f"{curr: =05.0f}rpm")

    # Additional methods
    def pressure_units(self, pres):
        """Pressure units"""
        if self.cfg.units["turbo_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(pres):03.02f}psi"
        if self.cfg.units["turbo_pressure_unit"] == "kPa":
            return f"{pres:03.01f}kPa"
        return f"{calc.kpa2bar(pres):03.03f}bar"
