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

from tinypedal.__init__ import cfg
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "weather"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        bar_gap = self.cfg["bar_gap"]
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color = self.cfg["font_color"]
        bg_color = self.cfg["bkg_color"]
        font_weather = tkfont.Font(family=self.cfg["font_name"],
                                   size=-self.cfg["font_size"],
                                   weight=self.cfg["font_weight"])

        # Draw label
        bar_style  = {"text":text_def, "bd":0, "height":1, "padx":0, "pady":0,
                      "font":font_weather, "fg":fg_color, "bg":bg_color}
        self.bar_temp = tk.Label(self, bar_style, width=13)
        self.bar_rain = tk.Label(self, bar_style, width=9)
        self.bar_wetness = tk.Label(self, bar_style, width=16)

        self.bar_temp.grid(row=0, column=0, padx=0, pady=0)
        self.bar_rain.grid(row=0, column=1, padx=(bar_gap, 0), pady=0)
        self.bar_wetness.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read Weather data
            amb_temp, trk_temp, rain, min_wet, max_wet, avg_wet = read_data.weather()

            # Check isPlayer before update
            if read_data.is_local_player():

                # set up display units
                amb_temp_d = calc.conv_temperature(amb_temp, self.cfg["temp_unit"])
                trk_temp_d = calc.conv_temperature(trk_temp, self.cfg["temp_unit"])

                if self.cfg["temp_unit"] == "0":
                    temp_unit = "C"
                elif self.cfg["temp_unit"] == "1":
                    temp_unit = "F"

                if max_wet > 0:
                    surface = "Wet"
                else:
                    surface = "Dry"

                temperature = f"{surface} {trk_temp_d:.1f}({amb_temp_d:.1f})??{temp_unit}"
                raining = f"Rain {rain:.0f}%"
                wetness = f"{min_wet:.0f}% < {max_wet:.0f}% ??? {avg_wet:.0f}%"

                # Weather update
                self.bar_temp.config(text=temperature, width=len(temperature)+1)
                self.bar_rain.config(text=raining, width=len(raining)+1)
                self.bar_wetness.config(text=wetness, width=len(wetness)+1)

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
