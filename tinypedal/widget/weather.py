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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "weather"
TREND_SIGN = "●▲▼"


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
        self.sign_temp = "°F" if self.cfg.units["temperature_unit"] == "Fahrenheit" else "°C"

        prefix_wetness_just = max(
            len(self.wcfg["prefix_dry"]),
            len(self.wcfg["prefix_wet"]),
        )
        self.prefix_rain = self.wcfg["prefix_rain"]
        self.prefix_wetness = (
            self.wcfg["prefix_dry"].ljust(prefix_wetness_just),
            self.wcfg["prefix_wet"].ljust(prefix_wetness_just)
        )

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

        # Track temperature
        if self.wcfg["show_temperature"]:
            layout_temp = QGridLayout()
            layout_temp.setSpacing(0)

            text_temp = self.format_temperature(0, 0)
            bar_style_temp = self.set_qss(
                fg_color=self.wcfg["font_color_temperature"],
                bg_color=self.wcfg["bkg_color_temperature"]
            )
            self.bar_temp = self.set_qlabel(
                text=text_temp,
                style=bar_style_temp,
                width=font_m.width * len(text_temp) + bar_padx,
            )
            layout_temp.addWidget(self.bar_temp, 0, 0)

            self.bar_style_temp_trend = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_constant"],
                    bg_color=self.wcfg["bkg_color_temperature"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_increasing"],
                    bg_color=self.wcfg["bkg_color_temperature"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_decreasing"],
                    bg_color=self.wcfg["bkg_color_temperature"]),
            )
            self.bar_temp_trend = self.set_qlabel(
                text=TREND_SIGN[0],
                style=self.bar_style_temp_trend[0],
                width=font_m.width + bar_padx,
            )
            layout_temp.addWidget(self.bar_temp_trend, 0, 1)

            layout.addLayout(layout_temp, 0, self.wcfg["column_index_temperature"])

        # Rain precipitation
        if self.wcfg["show_rain"]:
            layout_rain = QGridLayout()
            layout_rain.setSpacing(0)

            text_rain = self.format_rain(0)
            bar_style_rain = self.set_qss(
                fg_color=self.wcfg["font_color_rain"],
                bg_color=self.wcfg["bkg_color_rain"]
            )
            self.bar_rain = self.set_qlabel(
                text=text_rain,
                style=bar_style_rain,
                width=font_m.width * len(text_rain) + bar_padx,
            )
            layout_rain.addWidget(self.bar_rain, 0, 0)

            self.bar_style_raininess_trend = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_constant"],
                    bg_color=self.wcfg["bkg_color_rain"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_increasing"],
                    bg_color=self.wcfg["bkg_color_rain"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_decreasing"],
                    bg_color=self.wcfg["bkg_color_rain"]),
            )
            self.bar_raininess_trend = self.set_qlabel(
                text=TREND_SIGN[0],
                style=self.bar_style_raininess_trend[0],
                width=font_m.width + bar_padx,
            )
            layout_rain.addWidget(self.bar_raininess_trend, 0, 1)

            layout.addLayout(layout_rain, 0, self.wcfg["column_index_rain"])

        # Surface wetness
        if self.wcfg["show_wetness"]:
            layout_wetness = QGridLayout()
            layout_wetness.setSpacing(0)

            text_wetness = self.format_wetness(0)
            bar_style_wetness = self.set_qss(
                fg_color=self.wcfg["font_color_wetness"],
                bg_color=self.wcfg["bkg_color_wetness"]
            )
            self.bar_wetness = self.set_qlabel(
                text=text_wetness,
                style=bar_style_wetness,
                width=font_m.width * len(text_wetness) + bar_padx,
            )
            layout_wetness.addWidget(self.bar_wetness, 0, 0)

            self.bar_style_wetness_trend = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_constant"],
                    bg_color=self.wcfg["bkg_color_wetness"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_increasing"],
                    bg_color=self.wcfg["bkg_color_wetness"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_trend_decreasing"],
                    bg_color=self.wcfg["bkg_color_wetness"]),
            )
            self.bar_wetness_trend = self.set_qlabel(
                text=TREND_SIGN[0],
                style=self.bar_style_wetness_trend[0],
                width=font_m.width + bar_padx,
            )
            layout_wetness.addWidget(self.bar_wetness_trend, 0, 1)

            layout.addLayout(layout_wetness, 0, self.wcfg["column_index_wetness"])

        # Last data
        self.last_temperature = 0
        self.last_temperature_trend = 0
        self.last_raininess = 0
        self.last_raininess_trend = 0
        self.last_wetness = 0
        self.last_wetness_trend = 0
        self.last_temp_timer = 0
        self.last_rain_timer = 0
        self.last_wet_timer = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            lap_etime = api.read.timing.elapsed()

            # Track temperature
            if self.wcfg["show_temperature"]:
                temp_track = api.read.session.track_temperature()
                temp_air = api.read.session.ambient_temperature()
                temperature = temp_track + temp_air

                if self.last_temperature < temperature:
                    self.last_temp_timer = lap_etime
                    temperature_trend = 1  # increased
                elif self.last_temperature > temperature:
                    self.last_temp_timer = lap_etime
                    temperature_trend = -1  # decreased
                elif lap_etime - self.last_temp_timer > self.wcfg["temperature_trend_interval"]:
                    self.last_temp_timer = lap_etime
                    temperature_trend = 0  # no change

                if self.last_temp_timer > lap_etime:
                    self.last_temp_timer = lap_etime
                elif self.last_temp_timer == lap_etime:
                    # Temperature
                    self.update_temperature(
                        temperature, self.last_temperature, temp_track, temp_air)
                    self.last_temperature = temperature
                    # Temperature trend
                    self.update_temperature_trend(temperature_trend, self.last_temperature_trend)
                    self.last_temperature_trend = temperature_trend

            # Rain precipitation
            if self.wcfg["show_rain"]:
                raininess = api.read.session.raininess()

                if self.last_raininess < raininess:
                    self.last_rain_timer = lap_etime
                    raininess_trend = 1  # increased
                elif self.last_raininess > raininess:
                    self.last_rain_timer = lap_etime
                    raininess_trend = -1  # decreased
                elif lap_etime - self.last_rain_timer > self.wcfg["raininess_trend_interval"]:
                    self.last_rain_timer = lap_etime
                    raininess_trend = 0  # no change

                if self.last_rain_timer > lap_etime:
                    self.last_rain_timer = lap_etime
                elif self.last_rain_timer == lap_etime:
                    # Rain percentage
                    self.update_raininess(raininess, self.last_raininess)
                    self.last_raininess = raininess
                    # Rain trend
                    self.update_raininess_trend(raininess_trend, self.last_raininess_trend)
                    self.last_raininess_trend = raininess_trend

            # Surface wetness
            if self.wcfg["show_wetness"]:
                wet_min, wet_max, wet_avg = api.read.session.wetness()
                wetness = wet_min + wet_max + wet_avg

                if self.last_wetness < wetness:
                    self.last_wet_timer = lap_etime
                    wetness_trend = 1  # increased
                elif self.last_wetness > wetness:
                    self.last_wet_timer = lap_etime
                    wetness_trend = -1  # decreased
                elif lap_etime - self.last_wet_timer > self.wcfg["wetness_trend_interval"]:
                    self.last_wet_timer = lap_etime
                    wetness_trend = 0  # no change

                if self.last_wet_timer > lap_etime:
                    self.last_wet_timer = lap_etime
                elif self.last_wet_timer == lap_etime:
                    # Wetness percentage
                    self.update_wetness(wetness, self.last_wetness, wet_avg)
                    self.last_wetness = wetness
                    # Wet trend
                    self.update_wetness_trend(wetness_trend, self.last_wetness_trend)
                    self.last_wetness_trend = wetness_trend

    # GUI update methods
    def update_temperature(self, curr, last, track, air):
        """Track & ambient temperature"""
        if curr != last:
            self.bar_temp.setText(self.format_temperature(track, air))

    def update_temperature_trend(self, curr, last):
        """Temperature trend"""
        if curr != last:
            self.bar_temp_trend.setText(TREND_SIGN[curr])
            self.bar_temp_trend.setStyleSheet(self.bar_style_temp_trend[curr])

    def update_raininess(self, curr, last):
        """Rain percentage"""
        if curr != last:
            self.bar_rain.setText(self.format_rain(curr))

    def update_raininess_trend(self, curr, last):
        """Raininess trend"""
        if curr != last:
            self.bar_raininess_trend.setText(TREND_SIGN[curr])
            self.bar_raininess_trend.setStyleSheet(self.bar_style_raininess_trend[curr])

    def update_wetness(self, curr, last, wet_average):
        """Surface wetness percentage"""
        if curr != last:
            self.bar_wetness.setText(self.format_wetness(wet_average))

    def update_wetness_trend(self, curr, last):
        """Surface wetness trend"""
        if curr != last:
            self.bar_wetness_trend.setText(TREND_SIGN[curr])
            self.bar_wetness_trend.setStyleSheet(self.bar_style_wetness_trend[curr])

    def format_temperature(self, track_deg, air_deg):
        """Format track & ambient temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            track = f"{calc.celsius2fahrenheit(track_deg):05.2f}"[:5]
            air = f"{calc.celsius2fahrenheit(air_deg):03.0f}"[:3]
        else:
            track = f"{track_deg: >4.2f}"[:4]
            air = f"{air_deg: >4.2f}"[:4]
        return f"{track}({air}){self.sign_temp}"

    def format_rain(self, rain):
        """Format rain percentage"""
        percentage = f"{rain: >3.0%}"[:3]
        return f"{self.prefix_rain} {percentage}"

    def format_wetness(self, wetness):
        """Format wetness percentage"""
        percentage = f"{wetness: >3.0%}"[:3]
        return f"{self.prefix_wetness[wetness > 0.01]} {percentage}"
