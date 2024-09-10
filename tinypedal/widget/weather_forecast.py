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
Weather forecast Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPixmap, QPainter, QBrush
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from .. import weather as wthr
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "weather_forecast"
MAX_SLOT = 5
TEXT_NONE = "n/a"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        self.total_slot = min(max(self.wcfg["number_of_forecasts"], 1), 4) + 1
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        icon_size = int(max(self.wcfg["icon_size"], 16) * 0.5) * 2
        self.bar_width = max(font_m.width * 4 + bar_padx, icon_size)
        self.bar_rain_height = max(self.wcfg["rain_chance_bar_height"], 1)

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

        # Config canvas
        self.pixmap_weather = self.create_weather_icon_set(icon_size)
        self.pixmap_rainchance = QPixmap(self.bar_width, self.bar_rain_height)
        self.brush = QBrush(Qt.SolidPattern)

        self.data_bar = {}
        self.set_table(width=self.bar_width)

        # Last data
        self.unknown_estimated_time = [wthr.MAX_MINUTES] * MAX_SLOT
        self.estimated_time = [wthr.MAX_MINUTES] * MAX_SLOT
        self.last_estimated_time = [None] * MAX_SLOT
        self.last_estimated_temp = [None] * MAX_SLOT
        self.last_rain_chance = [None] * MAX_SLOT
        self.last_icon_index = [None] * MAX_SLOT

    # GUI generate methods
    def set_table(self, width: int):
        """Set table"""
        bar_style_time = self.set_qss(
            fg_color=self.wcfg["font_color_estimated_time"],
            bg_color=self.wcfg["bkg_color_estimated_time"]
        )
        bar_style_temp = self.set_qss(
            fg_color=self.wcfg["font_color_ambient_temperature"],
            bg_color=self.wcfg["bkg_color_ambient_temperature"]
        )
        bar_style_rain = self.set_qss(
            bg_color=self.wcfg["rain_chance_bar_bkg_color"]
        )
        bar_style_icon = self.set_qss(
            bg_color=self.wcfg["bkg_color"]
        )
        layout_inner = [None for _ in range(self.total_slot)]

        for index in range(self.total_slot):
            # Create column layout
            layout_inner[index] = QGridLayout()
            layout_inner[index].setSpacing(0)

            # Estimated time
            if self.wcfg["show_estimated_time"]:
                if index == 0:
                    time_text = "now"
                else:
                    time_text = TEXT_NONE
                name_time = f"time_{index}"
                self.data_bar[name_time] = self.set_qlabel(
                    text=time_text,
                    style=bar_style_time,
                    fixed_width=width,
                )
                layout_inner[index].addWidget(
                    self.data_bar[name_time], self.wcfg["column_index_estimated_time"], 0
                )

            # Ambient temperature
            if self.wcfg["show_ambient_temperature"]:
                name_temp = f"temp_{index}"
                self.data_bar[name_temp] = self.set_qlabel(
                    text=TEXT_NONE,
                    style=bar_style_temp,
                    fixed_width=width,
                )
                layout_inner[index].addWidget(
                    self.data_bar[name_temp], self.wcfg["column_index_ambient_temperature"], 0
                )

            # Rain chance
            if self.wcfg["show_rain_chance_bar"]:
                name_rain = f"rain_{index}"
                self.data_bar[name_rain] = self.set_qlabel(
                    style=bar_style_rain,
                    fixed_width=width,
                    fixed_height=self.bar_rain_height,
                )
                layout_inner[index].addWidget(
                    self.data_bar[name_rain], self.wcfg["column_index_rain_chance_bar"], 0
                )

            # Forecast icon
            name_icon = f"icon_{index}"
            self.data_bar[name_icon] = self.set_qlabel(
                style=bar_style_icon,
                fixed_width=width,
            )
            self.data_bar[name_icon].setPixmap(self.pixmap_weather[-1])
            layout_inner[index].addWidget(
                self.data_bar[name_icon], self.wcfg["column_index_weather_icon"], 0
            )

            # Set layout
            if self.wcfg["layout"] == 0:  # left to right layout
                self.layout().addLayout(
                    layout_inner[index], 0, index
                )
            else:  # right to left layout
                self.layout().addLayout(
                    layout_inner[index], 0, self.total_slot - 1 - index
                )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:
            self.update_weather_forecast_restapi()

    def update_weather_forecast_restapi(self):
        """Update weather forecast from restapi"""
        # Read weather data
        is_lap_type = api.read.session.lap_type()
        forecast_info = self.get_forecast_info(api.read.session.session_type())
        forecast_count = len(forecast_info)

        # Forecast
        if forecast_count > 0:
            index_offset = 0
            # Lap type race, no index offset, no estimated time
            if is_lap_type:
                if self.estimated_time != self.unknown_estimated_time:
                    for index in range(forecast_count):
                        self.estimated_time[index] = wthr.MAX_MINUTES
            # Time type race, index offset to ignore negative estimated time
            else:
                for index in range(forecast_count):
                    self.estimated_time[index] = min(round(
                        wthr.forecast_time_progress(
                            forecast_info[index][0],
                            api.read.session.end(),
                            api.read.session.elapsed()
                        ) / 60), wthr.MAX_MINUTES)
                    if self.estimated_time[index] <= 0 < index:
                        index_offset += 1

            for index in range(self.total_slot):
                index_bias = index + index_offset

                # Update slot 0 with live(now) weather condition
                if index == 0:
                    rain_chance = api.read.session.raininess() * 100
                    icon_index = wthr.sky_type_correction(forecast_info[index_bias][1], rain_chance)
                    estimated_temp = api.read.session.ambient_temperature()
                # Update slot with available forecast
                elif index_bias < forecast_count:
                    rain_chance = forecast_info[index_bias][3]
                    icon_index = forecast_info[index_bias][1]
                    estimated_time = self.estimated_time[index_bias]
                    estimated_temp = forecast_info[index_bias][2]
                # Update slot with unavailable forecast
                else:
                    rain_chance = 0
                    icon_index = -1
                    estimated_time = wthr.MAX_MINUTES
                    estimated_temp = wthr.MIN_TEMPERATURE

                self.update_weather_icon(
                    icon_index, self.last_icon_index[index], index)
                self.last_icon_index[index] = icon_index

                if self.wcfg["show_estimated_time"] and index > 0:
                    self.update_estimated_time(
                        estimated_time, self.last_estimated_time[index], index)
                    self.last_estimated_time[index] = estimated_time

                if self.wcfg["show_ambient_temperature"]:
                    self.update_estimated_temp(
                        estimated_temp, self.last_estimated_temp[index], index)
                    self.last_estimated_temp[index] = estimated_temp

                if self.wcfg["show_rain_chance_bar"]:
                    self.update_rain_chance_bar(
                        rain_chance, self.last_rain_chance[index], index)
                    self.last_rain_chance[index] = rain_chance

    # GUI update methods
    def update_estimated_time(self, curr, last, index):
        """Estimated time"""
        if curr != last:
            if curr >= wthr.MAX_MINUTES or curr < 0:
                time_text = TEXT_NONE
            elif curr >= 60:
                time_text = f"{curr / 60:.1f}h"
            else:
                time_text = f"{curr:.0f}m"
            self.data_bar[f"time_{index}"].setText(time_text)

    def update_estimated_temp(self, curr, last, index):
        """Estimated temperature"""
        if curr != last:
            if curr > wthr.MIN_TEMPERATURE:
                temp_text = self.format_temperature(curr)
            else:
                temp_text = TEXT_NONE
            self.data_bar[f"temp_{index}"].setText(temp_text)

    def update_rain_chance_bar(self, curr, last, index):
        """Rain chance bar"""
        if curr != last:
            self.pixmap_rainchance.fill(Qt.transparent)
            painter = QPainter(self.pixmap_rainchance)
            painter.setPen(Qt.NoPen)
            self.brush.setColor(self.wcfg["rain_chance_bar_color"])
            painter.setBrush(self.brush)
            painter.drawRect(0, 0, curr * 0.01 * self.bar_width, self.bar_rain_height)
            self.data_bar[f"rain_{index}"].setPixmap(self.pixmap_rainchance)

    def update_weather_icon(self, curr, last, index):
        """Weather icon, toggle visibility"""
        if curr != last:
            if 0 <= curr <= 10:
                self.data_bar[f"icon_{index}"].setPixmap(self.pixmap_weather[curr])
            else:
                self.data_bar[f"icon_{index}"].setPixmap(self.pixmap_weather[-1])

            if not self.wcfg["show_unavailable_data"] and index > 0:  # skip first slot
                self.toggle_visibility(curr, self.data_bar[f"icon_{index}"])
                if self.wcfg["show_estimated_time"]:
                    self.toggle_visibility(curr, self.data_bar[f"time_{index}"])
                if self.wcfg["show_ambient_temperature"]:
                    self.toggle_visibility(curr, self.data_bar[f"temp_{index}"])
                if self.wcfg["show_rain_chance_bar"]:
                    self.toggle_visibility(curr, self.data_bar[f"rain_{index}"])

    # Additional methods
    @staticmethod
    def toggle_visibility(icon_index, row_bar):
        """Hide row bar if data unavailable"""
        if icon_index >= 0:
            if row_bar.isHidden():
                row_bar.show()
        else:
            if not row_bar.isHidden():
                row_bar.hide()

    @staticmethod
    def get_forecast_info(session_type):
        """Get forecast info, 5 api data + 5 padding data"""
        if session_type <= 1:  # practice session
            info = minfo.restapi.forecastPractice
        elif session_type == 2:  # qualify session
            info = minfo.restapi.forecastQualify
        else:
            info = minfo.restapi.forecastRace  # race session
        if not info:  # get default if no valid data
            return wthr.DEFAULT
        return info

    def format_temperature(self, air_deg):
        """Format ambient temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(air_deg):.0f}°"
        return f"{air_deg:.0f}°"

    def create_weather_icon_set(self, icon_size):
        """Create weather icon set"""
        icon_source = QPixmap("images/icon_weather.png")
        pixmap_icon = icon_source.scaledToWidth(icon_size * 12, mode=Qt.SmoothTransformation)
        rect_size = QRectF(0, 0, icon_size, icon_size)
        rect_offset = QRectF(0, 0, icon_size, icon_size)
        return tuple(
            self.draw_weather_icon(pixmap_icon, icon_size, rect_size, rect_offset, index)
            for index in range(12))

    def draw_weather_icon(self, pixmap_icon, icon_size, rect_size, rect_offset, h_offset):
        """Draw weather icon"""
        pixmap = QPixmap(icon_size, icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        rect_offset.moveLeft(icon_size * h_offset)
        painter.drawPixmap(rect_size, pixmap_icon, rect_offset)
        return pixmap
