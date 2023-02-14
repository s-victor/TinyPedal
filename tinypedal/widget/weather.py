#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "weather"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]

        # Config style & variable
        text_def = "n/a"
        font_weather = tkfont.Font(family=self.wcfg["font_name"],
                                   size=-self.wcfg["font_size"],
                                   weight=self.wcfg["font_weight"])

        column_temp = self.wcfg["column_index_temperature"]
        column_rain = self.wcfg["column_index_rain"]
        column_wet = self.wcfg["column_index_wetness"]

        # Draw label
        bar_style  = {"text":text_def, "bd":0, "height":1,
                      "padx":bar_padx, "pady":0, "font":font_weather}

        if self.wcfg["show_temperature"]:
            self.bar_temp = tk.Label(self, bar_style, width=12,
                                     fg=self.wcfg["font_color_temperature"],
                                     bg=self.wcfg["bkg_color_temperature"])
            self.bar_temp.grid(row=0, column=column_temp, padx=(0, bar_gap), pady=0)

        if self.wcfg["show_rain"]:
            self.bar_rain = tk.Label(self, bar_style, width=7,
                                     fg=self.wcfg["font_color_rain"],
                                     bg=self.wcfg["bkg_color_rain"])
            self.bar_rain.grid(row=0, column=column_rain, padx=(0, bar_gap), pady=0)

        if self.wcfg["show_wetness"]:
            self.bar_wetness = tk.Label(self, bar_style, width=15,
                                        fg=self.wcfg["font_color_wetness"],
                                        bg=self.wcfg["bkg_color_wetness"])
            self.bar_wetness.grid(row=0, column=column_wet, padx=(0, bar_gap), pady=0)

        # Last data
        self.last_temp_d = None
        self.last_rain_per = None
        self.last_wet_road = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read Weather data
            track_temp, ambient_temp, rain_per, wet_road = read_data.weather()

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

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    def temp_units(self, track_temp, ambient_temp):
        """Track & ambient temperature"""
        if self.wcfg["temp_unit"] == "0":
            return f"{track_temp:.01f}({ambient_temp:.01f})°C"
        return f"{calc.celsius2fahrenheit(track_temp):.01f}" \
               f"({calc.celsius2fahrenheit(ambient_temp):.01f})°F"

    # GUI update methods
    def update_temp(self, curr, last):
        """Track & ambient temperature"""
        if curr != last:
            self.bar_temp.config(text=curr, width=len(curr))

    def update_rain(self, curr, last):
        """Rain percentage"""
        if curr != last:
            sign = "%" if self.wcfg["show_percentage_sign"] else ""

            rain_text = f"Rain {curr}{sign}"
            self.bar_rain.config(text=rain_text, width=len(rain_text))

    def update_wetness(self, curr, last):
        """Surface wetness"""
        if curr != last:
            surface = "Wet" if curr[1] > 0 else "Dry"
            sign = "%" if self.wcfg["show_percentage_sign"] else ""

            wet_text = f"{surface} {curr[0]}{sign} < {curr[1]}{sign} ≈ {curr[2]}{sign}"
            self.bar_wetness.config(text=wet_text, width=len(wet_text))
