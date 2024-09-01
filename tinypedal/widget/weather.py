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
Weather Widget
"""

from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "weather"


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
        self.sign_temp = "°F" if self.cfg.units["temperature_unit"] == "Fahrenheit" else "°C"
        self.sign_rain = "%" if self.wcfg["show_percentage_sign"] else ""

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        self.bar_min_width = partial(calc.qss_min_width, font_width=font_m.width, padding=bar_padx)

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_temp = self.wcfg["column_index_temperature"]
        column_rain = self.wcfg["column_index_rain"]
        column_wet = self.wcfg["column_index_wetness"]

        # Track temperature
        if self.wcfg["show_temperature"]:
            temp_text = self.format_temperature(0,0)
            bar_style_temp = self.bar_min_width(
                len(temp_text),
                f"color: {self.wcfg['font_color_temperature']};"
                f"background: {self.wcfg['bkg_color_temperature']};"
            )
            self.bar_temp = QLabel(temp_text)
            self.bar_temp.setAlignment(Qt.AlignCenter)
            self.bar_temp.setStyleSheet(bar_style_temp)

        # Rain percentage
        if self.wcfg["show_rain"]:
            rain_text = self.format_rain(0)
            bar_style_rain = self.bar_min_width(
                len(rain_text),
                f"color: {self.wcfg['font_color_rain']};"
                f"background: {self.wcfg['bkg_color_rain']};"
            )
            self.bar_rain = QLabel(rain_text)
            self.bar_rain.setAlignment(Qt.AlignCenter)
            self.bar_rain.setStyleSheet(bar_style_rain)

        # Surface wetness
        if self.wcfg["show_wetness"]:
            wetness_text = self.format_wetness(0,0,0)
            bar_style_wetness = self.bar_min_width(
                len(wetness_text),
                f"color: {self.wcfg['font_color_wetness']};"
                f"background: {self.wcfg['bkg_color_wetness']};"
            )
            self.bar_wetness = QLabel(wetness_text)
            self.bar_wetness.setAlignment(Qt.AlignCenter)
            self.bar_wetness.setStyleSheet(bar_style_wetness)

        # Set layout
        if self.wcfg["show_temperature"]:
            layout.addWidget(self.bar_temp, 0, column_temp)
        if self.wcfg["show_rain"]:
            layout.addWidget(self.bar_rain, 0, column_rain)
        if self.wcfg["show_wetness"]:
            layout.addWidget(self.bar_wetness, 0, column_wet)
        self.setLayout(layout)

        # Last data
        self.last_temp_d = None
        self.last_rain_per = None
        self.last_wet_road = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Track temperature
            if self.wcfg["show_temperature"]:
                temp_d = (api.read.session.track_temperature(),
                          api.read.session.ambient_temperature())
                self.update_temp(temp_d, self.last_temp_d)
                self.last_temp_d = temp_d

            # Rain percentage
            if self.wcfg["show_rain"]:
                rain_per = api.read.session.raininess()
                self.update_rain(rain_per, self.last_rain_per)
                self.last_rain_per = rain_per

            # Surface wetness
            if self.wcfg["show_wetness"]:
                wet_road = api.read.session.wetness()
                self.update_wetness(wet_road, self.last_wet_road)
                self.last_wet_road = wet_road

    # GUI update methods
    def update_temp(self, curr, last):
        """Track & ambient temperature"""
        if curr != last:
            temp_text = self.format_temperature(*curr)
            self.bar_temp.setText(temp_text)
            self.bar_temp.setStyleSheet(self.bar_min_width(
                len(temp_text),
                f"color: {self.wcfg['font_color_temperature']};"
                f"background: {self.wcfg['bkg_color_temperature']};"
            ))

    def update_rain(self, curr, last):
        """Rain percentage"""
        if curr != last:
            rain_text = self.format_rain(curr)
            self.bar_rain.setText(rain_text)
            self.bar_rain.setStyleSheet(self.bar_min_width(
                len(rain_text),
                f"color: {self.wcfg['font_color_rain']};"
                f"background: {self.wcfg['bkg_color_rain']};"
            ))

    def update_wetness(self, curr, last):
        """Surface wetness"""
        if curr != last:
            wetness_text = self.format_wetness(*curr)
            self.bar_wetness.setText(wetness_text)
            self.bar_wetness.setStyleSheet(self.bar_min_width(
                len(wetness_text),
                f"color: {self.wcfg['font_color_wetness']};"
                f"background: {self.wcfg['bkg_color_wetness']};"
            ))

    def format_temperature(self, track_deg, air_deg):
        """Format track & ambient temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(track_deg):.1f}({calc.celsius2fahrenheit(air_deg):.1f}){self.sign_temp}"
        return f"{track_deg:.1f}({air_deg:.1f}){self.sign_temp}"

    def format_rain(self, percentage):
        """Format rain percentage"""
        return f"Rain {percentage * 100:.0f}{self.sign_rain}"

    def format_wetness(self, min_wet, max_wet, avg_wet):
        """Format wetness"""
        surface = "Wet" if max_wet > 0.01 else "Dry"
        return (f"{surface} {min_wet * 100:.0f}{self.sign_rain}"
                f" < {max_wet * 100:.0f}{self.sign_rain}"
                f" ≈ {avg_wet * 100:.0f}{self.sign_rain}")
