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
Engine Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "engine"


class Draw(Overlay):
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

        column_oil = self.wcfg["column_index_oil"]
        column_water = self.wcfg["column_index_water"]
        column_turbo = self.wcfg["column_index_turbo"]
        column_rpm = self.wcfg["column_index_rpm"]
        column_rpm_max = self.wcfg["column_index_rpm_maximum"]
        column_torque = self.wcfg["column_index_torque"]

        # Oil temperature
        if self.wcfg["show_temperature"]:
            self.bar_oil = QLabel("Oil T")
            self.bar_oil.setAlignment(Qt.AlignCenter)
            self.bar_oil.setStyleSheet(
                f"color: {self.wcfg['font_color_oil']};"
                f"background: {self.wcfg['bkg_color_oil']};"
            )

            # Water temperature
            self.bar_water = QLabel("Water T")
            self.bar_water.setAlignment(Qt.AlignCenter)
            self.bar_water.setStyleSheet(
                f"color: {self.wcfg['font_color_water']};"
                f"background: {self.wcfg['bkg_color_water']};"
            )

        # Turbo pressure
        if self.wcfg["show_turbo_pressure"]:
            self.bar_turbo = QLabel("Turbo")
            self.bar_turbo.setAlignment(Qt.AlignCenter)
            self.bar_turbo.setStyleSheet(
                f"color: {self.wcfg['font_color_turbo']};"
                f"background: {self.wcfg['bkg_color_turbo']};"
            )

        # RPM
        if self.wcfg["show_rpm"]:
            self.bar_rpm = QLabel("RPM")
            self.bar_rpm.setAlignment(Qt.AlignCenter)
            self.bar_rpm.setStyleSheet(
                f"color: {self.wcfg['font_color_rpm']};"
                f"background: {self.wcfg['bkg_color_rpm']};"
            )

        # RPM maximum
        if self.wcfg["show_rpm_maximum"]:
            self.bar_rpm_max = QLabel("MAX RPM")
            self.bar_rpm_max.setAlignment(Qt.AlignCenter)
            self.bar_rpm_max.setStyleSheet(
                f"color: {self.wcfg['font_color_rpm_maximum']};"
                f"background: {self.wcfg['bkg_color_rpm_maximum']};"
            )

        # Torque
        if self.wcfg["show_torque"]:
            self.bar_torque = QLabel("TORQUE")
            self.bar_torque.setAlignment(Qt.AlignCenter)
            self.bar_torque.setStyleSheet(
                f"color: {self.wcfg['font_color_torque']};"
                f"background: {self.wcfg['bkg_color_torque']};"
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
            if self.wcfg["show_rpm_maximum"]:
                layout.addWidget(self.bar_rpm_max, column_rpm_max, 0)
            if self.wcfg["show_torque"]:
                layout.addWidget(self.bar_torque, column_torque, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_temperature"]:
                layout.addWidget(self.bar_oil, 0, column_oil)
                layout.addWidget(self.bar_water, 0, column_water)
            if self.wcfg["show_turbo_pressure"]:
                layout.addWidget(self.bar_turbo, 0, column_turbo)
            if self.wcfg["show_rpm"]:
                layout.addWidget(self.bar_rpm, 0, column_rpm)
            if self.wcfg["show_rpm_maximum"]:
                layout.addWidget(self.bar_rpm_max, 0, column_rpm_max)
            if self.wcfg["show_torque"]:
                layout.addWidget(self.bar_torque, 0, column_torque)
        self.setLayout(layout)

        # Last data
        self.last_temp_oil = None
        self.last_temp_water = None
        self.last_turbo = None
        self.last_rpm = None
        self.last_rpm_max = None
        self.last_torque = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Temperature
            if self.wcfg["show_temperature"]:
                # Oil temperature
                temp_oil = round(api.read.engine.oil_temperature(), 1)
                self.update_oil(temp_oil, self.last_temp_oil)
                self.last_temp_oil = temp_oil

                # Water temperature
                temp_water = round(api.read.engine.water_temperature(), 1)
                self.update_water(temp_water, self.last_temp_water)
                self.last_temp_water = temp_water

            # Turbo pressure
            if self.wcfg["show_turbo_pressure"]:
                turbo = int(api.read.engine.turbo())
                self.update_turbo(turbo, self.last_turbo)
                self.last_turbo = turbo

            # Engine RPM
            if self.wcfg["show_rpm"]:
                rpm = int(api.read.engine.rpm())
                self.update_rpm(rpm, self.last_rpm)
                self.last_rpm = rpm

            # Engine RPM maximum
            if self.wcfg["show_rpm_maximum"]:
                rpm_max = int(api.read.engine.rpm_max())
                self.update_rpm_max(rpm_max, self.last_rpm_max)
                self.last_rpm_max = rpm_max

            # Engine torque
            if self.wcfg["show_torque"]:
                torque = round(api.read.engine.torque(), 2)
                self.update_torque(torque, self.last_torque)
                self.last_torque = torque

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
            self.bar_oil.setStyleSheet(color)

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
            self.bar_water.setStyleSheet(color)

    def update_turbo(self, curr, last):
        """Turbo pressure"""
        if curr != last:
            self.bar_turbo.setText(self.pressure_units(curr * 0.001))

    def update_rpm(self, curr, last):
        """Engine RPM"""
        if curr != last:
            self.bar_rpm.setText(f"{curr: =05.0f}rpm")

    def update_rpm_max(self, curr, last):
        """Engine RPM maximum"""
        if curr != last:
            self.bar_rpm_max.setText(f"{curr: =05.0f}max")

    def update_torque(self, curr, last):
        """Engine torque"""
        if curr != last:
            format_text = f"{curr:.02f}"[:6].rjust(6)
            self.bar_torque.setText(f"{format_text}Nm")

    # Additional methods
    def pressure_units(self, pres):
        """Pressure units"""
        if self.cfg.units["turbo_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(pres):03.02f}psi"
        if self.cfg.units["turbo_pressure_unit"] == "kPa":
            return f"{pres:03.01f}kPa"
        return f"{calc.kpa2bar(pres):03.03f}bar"
