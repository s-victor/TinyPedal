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
from PySide2.QtWidgets import QLabel, QGridLayout

from .. import calculation as calc
from .. import weather as wthr
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "weather_forecast"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.icon_size = int(max(self.wcfg["icon_size"], 16) * 0.5) * 2
        bar_width = max(font_m.width * 4 + bar_padx, self.icon_size)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_0 = QGridLayout()
        layout_1 = QGridLayout()
        layout_2 = QGridLayout()
        layout_3 = QGridLayout()
        layout_4 = QGridLayout()
        layout_0.setSpacing(0)
        layout_1.setSpacing(0)
        layout_2.setSpacing(0)
        layout_3.setSpacing(0)
        layout_4.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Config canvas
        self.pixmap_weather = self.create_weather_icon_set()
        self.brush = QBrush(Qt.SolidPattern)

        # Estimated time
        if self.wcfg["show_estimated_time"]:
            bar_style_time = (
                f"color: {self.wcfg['font_color_estimated_time']};"
                f"background: {self.wcfg['bkg_color_estimated_time']};"
                f"min-width: {bar_width}px;"
            )
            self.bar_time_0 = QLabel("now")
            self.bar_time_0.setAlignment(Qt.AlignCenter)
            self.bar_time_0.setStyleSheet(bar_style_time)
            layout_0.addWidget(self.bar_time_0, 0, 0)

            self.bar_time_1 = QLabel(text_def)
            self.bar_time_1.setAlignment(Qt.AlignCenter)
            self.bar_time_1.setStyleSheet(bar_style_time)
            layout_1.addWidget(self.bar_time_1, 0, 0)

            self.bar_time_2 = QLabel(text_def)
            self.bar_time_2.setAlignment(Qt.AlignCenter)
            self.bar_time_2.setStyleSheet(bar_style_time)
            layout_2.addWidget(self.bar_time_2, 0, 0)

            self.bar_time_3 = QLabel(text_def)
            self.bar_time_3.setAlignment(Qt.AlignCenter)
            self.bar_time_3.setStyleSheet(bar_style_time)
            layout_3.addWidget(self.bar_time_3, 0, 0)

            self.bar_time_4 = QLabel(text_def)
            self.bar_time_4.setAlignment(Qt.AlignCenter)
            self.bar_time_4.setStyleSheet(bar_style_time)
            layout_4.addWidget(self.bar_time_4, 0, 0)

        # Ambient temperature
        if self.wcfg["show_ambient_temperature"]:
            bar_style_temp = (
                f"color: {self.wcfg['font_color_ambient_temperature']};"
                f"background: {self.wcfg['bkg_color_ambient_temperature']};"
                f"min-width: {bar_width}px;"
            )
            self.bar_temp_0 = QLabel(text_def)
            self.bar_temp_0.setAlignment(Qt.AlignCenter)
            self.bar_temp_0.setStyleSheet(bar_style_temp)
            layout_0.addWidget(self.bar_temp_0, 2, 0)

            self.bar_temp_1 = QLabel(text_def)
            self.bar_temp_1.setAlignment(Qt.AlignCenter)
            self.bar_temp_1.setStyleSheet(bar_style_temp)
            layout_1.addWidget(self.bar_temp_1, 2, 0)

            self.bar_temp_2 = QLabel(text_def)
            self.bar_temp_2.setAlignment(Qt.AlignCenter)
            self.bar_temp_2.setStyleSheet(bar_style_temp)
            layout_2.addWidget(self.bar_temp_2, 2, 0)

            self.bar_temp_3 = QLabel(text_def)
            self.bar_temp_3.setAlignment(Qt.AlignCenter)
            self.bar_temp_3.setStyleSheet(bar_style_temp)
            layout_3.addWidget(self.bar_temp_3, 2, 0)

            self.bar_temp_4 = QLabel(text_def)
            self.bar_temp_4.setAlignment(Qt.AlignCenter)
            self.bar_temp_4.setStyleSheet(bar_style_temp)
            layout_4.addWidget(self.bar_temp_4, 2, 0)

        # Rain chance
        if self.wcfg["show_rain_chance_bar"]:
            bar_style_rain = (
                f"background: {self.wcfg['rain_chance_bar_bkg_color']};"
                f"min-width: {bar_width}px;"
            )
            self.bar_rain_width = bar_width
            self.bar_rain_height = max(self.wcfg["rain_chance_bar_height"], 1)
            self.pixmap_rainchance = QPixmap(self.bar_rain_width, self.bar_rain_height)

            self.bar_rain_0 = QLabel()
            self.bar_rain_0.setFixedHeight(self.bar_rain_height)
            self.bar_rain_0.setStyleSheet(bar_style_rain)
            layout_0.addWidget(self.bar_rain_0, 3, 0)

            self.bar_rain_1 = QLabel()
            self.bar_rain_1.setFixedHeight(self.bar_rain_height)
            self.bar_rain_1.setStyleSheet(bar_style_rain)
            layout_1.addWidget(self.bar_rain_1, 3, 0)

            self.bar_rain_2 = QLabel()
            self.bar_rain_2.setFixedHeight(self.bar_rain_height)
            self.bar_rain_2.setStyleSheet(bar_style_rain)
            layout_2.addWidget(self.bar_rain_2, 3, 0)

            self.bar_rain_3 = QLabel()
            self.bar_rain_3.setFixedHeight(self.bar_rain_height)
            self.bar_rain_3.setStyleSheet(bar_style_rain)
            layout_3.addWidget(self.bar_rain_3, 3, 0)

            self.bar_rain_4 = QLabel()
            self.bar_rain_4.setFixedHeight(self.bar_rain_height)
            self.bar_rain_4.setStyleSheet(bar_style_rain)
            layout_4.addWidget(self.bar_rain_4, 3, 0)

        # Forecast icon
        bar_style_icon = (
            f"background: {self.wcfg['bkg_color']};"
            f"min-width: {bar_width}px;"
        )
        self.bar_icon_0 = QLabel()
        self.bar_icon_0.setAlignment(Qt.AlignCenter)
        self.bar_icon_0.setStyleSheet(bar_style_icon)
        self.bar_icon_0.setPixmap(self.pixmap_weather[-1])
        layout_0.addWidget(self.bar_icon_0, 1, 0)

        self.bar_icon_1 = QLabel()
        self.bar_icon_1.setAlignment(Qt.AlignCenter)
        self.bar_icon_1.setStyleSheet(bar_style_icon)
        self.bar_icon_1.setPixmap(self.pixmap_weather[-1])
        layout_1.addWidget(self.bar_icon_1, 1, 0)

        self.bar_icon_2 = QLabel()
        self.bar_icon_2.setAlignment(Qt.AlignCenter)
        self.bar_icon_2.setStyleSheet(bar_style_icon)
        self.bar_icon_2.setPixmap(self.pixmap_weather[-1])
        layout_2.addWidget(self.bar_icon_2, 1, 0)

        self.bar_icon_3 = QLabel()
        self.bar_icon_3.setAlignment(Qt.AlignCenter)
        self.bar_icon_3.setStyleSheet(bar_style_icon)
        self.bar_icon_3.setPixmap(self.pixmap_weather[-1])
        layout_3.addWidget(self.bar_icon_3, 1, 0)

        self.bar_icon_4 = QLabel()
        self.bar_icon_4.setAlignment(Qt.AlignCenter)
        self.bar_icon_4.setStyleSheet(bar_style_icon)
        self.bar_icon_4.setPixmap(self.pixmap_weather[-1])
        layout_4.addWidget(self.bar_icon_4, 1, 0)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Left to right layout
            layout.addLayout(layout_0, 0, 0)
            layout.addLayout(layout_1, 0, 1)
            layout.addLayout(layout_2, 0, 2)
            layout.addLayout(layout_3, 0, 3)
            layout.addLayout(layout_4, 0, 4)
        else:
            # Right to left layout
            layout.addLayout(layout_0, 0, 4)
            layout.addLayout(layout_1, 0, 3)
            layout.addLayout(layout_2, 0, 2)
            layout.addLayout(layout_3, 0, 1)
            layout.addLayout(layout_4, 0, 0)
        self.setLayout(layout)

        # Last data
        self.unknown_estimated_time = [wthr.MAX_MINUTES] * 10
        self.last_estimated_time = [None] * 10
        self.last_estimated_temp = [None] * 10
        self.last_rain_chance = [None] * 10
        self.last_icon_index = [None] * 10

        # Set widget state & start update
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:
            self.update_weather_forecast_restapi()

    def update_weather_forecast_restapi(self):
        """Update weather forecast from restapi"""
        # Read weather data
        is_lap_type = api.read.session.lap_type()
        forecast_info = self.get_forecast_info()
        raininess = api.read.session.raininess() * 100

        # Forecast
        if forecast_info and len(forecast_info) >= 10:
            index_offset = 0
            # Lap type race, no index offset, no estimated time
            if is_lap_type:
                estimated_time = self.unknown_estimated_time
            # Time type race, index offset to ignore negative estimated time
            else:
                estimated_time = [min(round(  # fraction start time * session duration - session elapsed time
                    (forecast_info[index][0] * api.read.session.end() - api.read.session.elapsed()) / 60),
                    wthr.MAX_MINUTES) for index in range(10)]

                for index, etime in enumerate(estimated_time):
                    if etime > 0:
                        if index > 0:
                            index_offset = index - 1
                        break

            for index in range(5):
                index_bias = index + index_offset

                if index == 0:
                    icon_index = wthr.sky_type_correction(forecast_info[index_bias][1], raininess)
                    self.update_weather_icon(icon_index, self.last_icon_index[index], index)
                    self.last_icon_index[index] = icon_index

                    if self.wcfg["show_ambient_temperature"]:
                        estimated_temp = api.read.session.ambient_temperature()
                        self.update_estimated_temp(estimated_temp, self.last_estimated_temp[index], index)
                        self.last_estimated_temp[index] = estimated_temp

                    if self.wcfg["show_rain_chance_bar"]:
                        rain_chance = raininess
                        self.update_rain_chance_bar(rain_chance, self.last_rain_chance[index], index)
                        self.last_rain_chance[index] = rain_chance

                else:
                    icon_index = forecast_info[index_bias][1]
                    self.update_weather_icon(icon_index, self.last_icon_index[index], index)
                    self.last_icon_index[index] = icon_index

                    if self.wcfg["show_estimated_time"]:
                        self.update_estimated_time(estimated_time[index_bias], self.last_estimated_time[index], index)
                        self.last_estimated_time[index] = estimated_time[index_bias]

                    if self.wcfg["show_ambient_temperature"]:
                        estimated_temp = forecast_info[index_bias][2]
                        self.update_estimated_temp(estimated_temp, self.last_estimated_temp[index], index)
                        self.last_estimated_temp[index] = estimated_temp

                    if self.wcfg["show_rain_chance_bar"]:
                        rain_chance = forecast_info[index_bias][3]
                        self.update_rain_chance_bar(rain_chance, self.last_rain_chance[index], index)
                        self.last_rain_chance[index] = rain_chance

    # GUI update methods
    def update_estimated_time(self, curr, last, index):
        """Estimated time"""
        if curr != last:
            if curr >= wthr.MAX_MINUTES or curr < 0:
                time_text = "n/a"
            elif curr >= 60:
                time_text = f"{curr / 60:.1f}h"
            else:
                time_text = f"{curr:.0f}m"
            getattr(self, f"bar_time_{index}").setText(time_text)

    def update_estimated_temp(self, curr, last, index):
        """Estimated temperature"""
        if curr != last:
            if curr > wthr.MIN_TEMPERATURE:
                temp_text = self.format_temperature(curr)
            else:
                temp_text = "n/a"
            getattr(self, f"bar_temp_{index}").setText(temp_text)

    def update_rain_chance_bar(self, curr, last, index):
        """Rain chance bar"""
        if curr != last:
            self.pixmap_rainchance.fill(Qt.transparent)
            painter = QPainter(self.pixmap_rainchance)
            painter.setPen(Qt.NoPen)
            self.brush.setColor(self.wcfg["rain_chance_bar_color"])
            painter.setBrush(self.brush)
            painter.drawRect(0, 0, curr * 0.01 * self.bar_rain_width, self.bar_rain_height)
            getattr(self, f"bar_rain_{index}").setPixmap(self.pixmap_rainchance)

    def update_weather_icon(self, curr, last, index):
        """Weather icon, toggle visibility"""
        if curr != last:
            if 0 <= curr <= 10:
                getattr(self, f"bar_icon_{index}").setPixmap(self.pixmap_weather[curr])
            else:
                getattr(self, f"bar_icon_{index}").setPixmap(self.pixmap_weather[-1])

            if not self.wcfg["show_unavailable_data"] and index > 0:  # skip first slot
                self.toggle_visibility(curr, getattr(self, f"bar_icon_{index}"))
                if self.wcfg["show_estimated_time"]:
                    self.toggle_visibility(curr, getattr(self, f"bar_time_{index}"))
                if self.wcfg["show_ambient_temperature"]:
                    self.toggle_visibility(curr, getattr(self, f"bar_temp_{index}"))
                if self.wcfg["show_rain_chance_bar"]:
                    self.toggle_visibility(curr, getattr(self, f"bar_rain_{index}"))

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
    def get_forecast_info():
        """Get forecast info, 5 api data + 5 padding data"""
        session_type = api.read.session.session_type()
        if session_type <= 1:  # practice session
            info = minfo.restapi.forecastPractice
        elif session_type == 2:  # qualify session
            info = minfo.restapi.forecastQualify
        else:  # race session
            info = minfo.restapi.forecastRace
        return info

    def format_temperature(self, air_deg):
        """Format ambient temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(air_deg):.0f}°"
        return f"{air_deg:.0f}°"

    def create_weather_icon_set(self):
        """Create weather icon set"""
        icon_source = QPixmap("images/icon_weather.png")
        pixmap_icon = icon_source.scaledToWidth(self.icon_size * 12, mode=Qt.SmoothTransformation)
        rect_size = QRectF(0, 0, self.icon_size, self.icon_size)
        rect_offset = QRectF(0, 0, self.icon_size, self.icon_size)
        return tuple(
            self.draw_weather_icon(pixmap_icon, rect_size, rect_offset, index)
            for index in range(12))

    def draw_weather_icon(self, pixmap_icon, rect_size, rect_offset, h_offset):
        """Draw weather icon"""
        pixmap = QPixmap(self.icon_size, self.icon_size)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        rect_offset.moveLeft(self.icon_size * h_offset)
        painter.drawPixmap(rect_size, pixmap_icon, rect_offset)
        return pixmap
