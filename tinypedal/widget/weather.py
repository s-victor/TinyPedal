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
Weather Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi
from ..base import Widget

WIDGET_NAME = "weather"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.sign_text = "%" if self.wcfg["show_percentage_sign"] else ""

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

        column_temp = self.wcfg["column_index_temperature"]
        column_rain = self.wcfg["column_index_rain"]
        column_wet = self.wcfg["column_index_wetness"]

        # Track temperature
        if self.wcfg["show_temperature"]:
            self.bar_temp = QLabel("TRACK")
            self.bar_temp.setAlignment(Qt.AlignCenter)
            self.bar_temp.setStyleSheet(
                f"color: {self.wcfg['font_color_temperature']};"
                f"background: {self.wcfg['bkg_color_temperature']};"
            )

        # Rain percentage
        if self.wcfg["show_rain"]:
            self.bar_rain = QLabel("RAIN")
            self.bar_rain.setAlignment(Qt.AlignCenter)
            self.bar_rain.setStyleSheet(
                f"color: {self.wcfg['font_color_rain']};"
                f"background: {self.wcfg['bkg_color_rain']};"
            )

        # Surface wetness
        if self.wcfg["show_wetness"]:
            self.bar_wetness = QLabel("WETNESS")
            self.bar_wetness.setAlignment(Qt.AlignCenter)
            self.bar_wetness.setStyleSheet(
                f"color: {self.wcfg['font_color_wetness']};"
                f"background: {self.wcfg['bkg_color_wetness']};"
            )

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

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and readapi.state():

            # Read Weather data
            track_temp, ambient_temp, rain_per, wet_road = readapi.weather()

            # Track temperature
            if self.wcfg["show_temperature"]:
                temp_d = self.temp_units(track_temp, ambient_temp)
                self.update_temp(temp_d, self.last_temp_d)
                self.last_temp_d = temp_d

            # Rain percentage
            if self.wcfg["show_rain"]:
                rain_per = int(rain_per)
                self.update_rain(rain_per, self.last_rain_per)
                self.last_rain_per = rain_per

            # Surface wetness
            if self.wcfg["show_wetness"]:
                wet_road = tuple(map(int, wet_road))
                self.update_wetness(wet_road, self.last_wet_road)
                self.last_wet_road = wet_road

    # GUI update methods
    def update_temp(self, curr, last):
        """Track & ambient temperature"""
        if curr != last:
            self.bar_temp.setText(curr)

    def update_rain(self, curr, last):
        """Rain percentage"""
        if curr != last:
            rain_text = f"Rain {curr}{self.sign_text}"
            self.bar_rain.setText(rain_text)

    def update_wetness(self, curr, last):
        """Surface wetness"""
        if curr != last:
            surface = "Wet" if curr[1] > 0 else "Dry"
            wet_text = f"{surface} {curr[0]}{self.sign_text} < {curr[1]}{self.sign_text} ≈ {curr[2]}{self.sign_text}"
            self.bar_wetness.setText(wet_text)

    # Additional methods
    def temp_units(self, track_temp, ambient_temp):
        """Track & ambient temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(track_temp):.01f}" \
                   f"({calc.celsius2fahrenheit(ambient_temp):.01f})°F"
        return f"{track_temp:.01f}({ambient_temp:.01f})°C"
