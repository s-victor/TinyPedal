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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "engine"


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
        bar_width = font_m.width * 8 + bar_padx

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Oil temperature
        if self.wcfg["show_oil_temperature"]:
            self.bar_style_oil = (
                self.set_qss(
                    self.wcfg["font_color_oil"],
                    self.wcfg["bkg_color_oil"]),
                self.set_qss(
                    self.wcfg["font_color_oil"],
                    self.wcfg["warning_color_overheat"])
            )
            self.bar_oil = self.set_qlabel(
                text="Oil T",
                style=self.bar_style_oil[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_oil,
                column=self.wcfg["column_index_oil"],
            )

        # Water temperature
        if self.wcfg["show_water_temperature"]:
            self.bar_style_water = (
                self.set_qss(
                    self.wcfg["font_color_water"],
                    self.wcfg["bkg_color_water"]),
                self.set_qss(
                    self.wcfg["font_color_water"],
                    self.wcfg["warning_color_overheat"])
            )
            self.bar_water = self.set_qlabel(
                text="Water T",
                style=self.bar_style_water[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_water,
                column=self.wcfg["column_index_water"],
            )

        # Turbo pressure
        if self.wcfg["show_turbo_pressure"]:
            bar_style_turbo = self.set_qss(
                self.wcfg["font_color_turbo"],
                self.wcfg["bkg_color_turbo"]
            )
            self.bar_turbo = self.set_qlabel(
                text="Turbo",
                style=bar_style_turbo,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_turbo,
                column=self.wcfg["column_index_turbo"],
            )

        # Engine RPM
        if self.wcfg["show_rpm"]:
            bar_style_rpm = self.set_qss(
                self.wcfg["font_color_rpm"],
                self.wcfg["bkg_color_rpm"]
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

        # Engine RPM maximum
        if self.wcfg["show_rpm_maximum"]:
            bar_style_rpm_max = self.set_qss(
                self.wcfg["font_color_rpm_maximum"],
                self.wcfg["bkg_color_rpm_maximum"]
            )
            self.bar_rpm_max = self.set_qlabel(
                text="MAX RPM",
                style=bar_style_rpm_max,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_rpm_max,
                column=self.wcfg["column_index_rpm_maximum"],
            )

        # Engine torque
        if self.wcfg["show_torque"]:
            bar_style_torque = self.set_qss(
                self.wcfg["font_color_torque"],
                self.wcfg["bkg_color_torque"]
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

        # Engine power
        if self.wcfg["show_power"]:
            bar_style_power = self.set_qss(
                self.wcfg["font_color_power"],
                self.wcfg["bkg_color_power"]
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
        self.last_temp_oil = None
        self.last_temp_water = None
        self.last_turbo = None
        self.last_rpm = None
        self.last_rpm_max = None
        self.last_torque = None
        self.last_power = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Oil temperature
            if self.wcfg["show_oil_temperature"]:
                temp_oil = round(api.read.engine.oil_temperature(), 2)
                self.update_oil(temp_oil, self.last_temp_oil)
                self.last_temp_oil = temp_oil

            # Water temperature
            if self.wcfg["show_water_temperature"]:
                temp_water = round(api.read.engine.water_temperature(), 2)
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

            # Engine power
            if self.wcfg["show_power"]:
                power = round(calc.engine_power(
                    api.read.engine.torque(), api.read.engine.rpm()), 2)
                self.update_power(power, self.last_power)
                self.last_power = power

    # GUI update methods
    def update_oil(self, curr, last):
        """Oil temperature"""
        if curr != last:
            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            self.bar_oil.setText(f"O{curr: >6.1f}°")
            self.bar_oil.setStyleSheet(
                self.bar_style_oil[curr >= self.wcfg["overheat_threshold_oil"]]
            )

    def update_water(self, curr, last):
        """Water temperature"""
        if curr != last:
            if self.cfg.units["temperature_unit"] == "Fahrenheit":
                curr = calc.celsius2fahrenheit(curr)

            self.bar_water.setText(f"W{curr: >6.1f}°")
            self.bar_water.setStyleSheet(
                self.bar_style_water[curr >= self.wcfg["overheat_threshold_water"]]
            )

    def update_turbo(self, curr, last):
        """Turbo pressure"""
        if curr != last:
            self.bar_turbo.setText(self.pressure_units(curr * 0.001))

    def update_rpm(self, curr, last):
        """Engine RPM"""
        if curr != last:
            self.bar_rpm.setText(f"{curr: >5}rpm")

    def update_rpm_max(self, curr, last):
        """Engine RPM maximum"""
        if curr != last:
            self.bar_rpm_max.setText(f"{curr: >5}max")

    def update_torque(self, curr, last):
        """Engine torque"""
        if curr != last:
            text = f"{curr: >6.2f}"[:6]
            self.bar_torque.setText(f"{text}Nm")

    def update_power(self, curr, last):
        """Engine power"""
        if curr != last:
            self.bar_power.setText(self.power_units(curr))

    # Additional methods
    def pressure_units(self, pres):
        """Pressure units"""
        if self.cfg.units["turbo_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(pres):03.2f}psi"
        if self.cfg.units["turbo_pressure_unit"] == "kPa":
            return f"{pres:03.1f}kPa"
        return f"{calc.kpa2bar(pres):03.3f}bar"

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
