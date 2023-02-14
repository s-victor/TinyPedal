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
Brake Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "brake"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]
        inner_gap = self.wcfg["inner_gap"]
        bar_width = 4 if self.wcfg["show_degree_sign"] else 3

        # Config style & variable
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        font_temp = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        column_btemp = self.wcfg["column_index_temperature"]
        column_btavg = self.wcfg["column_index_average"]

        # Draw label
        frame_btemp = tk.Frame(self, bd=0, highlightthickness=0,
                               bg=self.cfg.overlay["transparent_color"])
        frame_btavg = tk.Frame(self, bd=0, highlightthickness=0,
                               bg=self.cfg.overlay["transparent_color"])
        bar_style_btemp = {"text":"n/a", "bd":0, "height":1, "width":bar_width,
                           "padx":bar_padx, "pady":0, "font":font_temp,
                           "fg":self.wcfg["font_color_temperature"],
                           "bg":self.wcfg["bkg_color_temperature"]}
        bar_style_btavg = {"text":"n/a", "bd":0, "height":1, "width":bar_width,
                           "padx":bar_padx, "pady":0, "font":font_temp,
                           "fg":self.wcfg["font_color_average"],
                           "bg":self.wcfg["bkg_color_average"]}

        self.bar_btemp_fl = tk.Label(frame_btemp, bar_style_btemp)
        self.bar_btemp_fr = tk.Label(frame_btemp, bar_style_btemp)
        self.bar_btemp_rl = tk.Label(frame_btemp, bar_style_btemp)
        self.bar_btemp_rr = tk.Label(frame_btemp, bar_style_btemp)
        self.bar_btemp_fl.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))
        self.bar_btemp_fr.grid(row=0, column=1, padx=0, pady=(0,inner_gap))
        self.bar_btemp_rl.grid(row=1, column=0, padx=(0,inner_gap), pady=0)
        self.bar_btemp_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["show_average"]:
            self.bar_btavg_fl = tk.Label(frame_btavg, bar_style_btavg)
            self.bar_btavg_fr = tk.Label(frame_btavg, bar_style_btavg)
            self.bar_btavg_rl = tk.Label(frame_btavg, bar_style_btavg)
            self.bar_btavg_rr = tk.Label(frame_btavg, bar_style_btavg)
            self.bar_btavg_fl.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))
            self.bar_btavg_fr.grid(row=0, column=1, padx=0, pady=(0,inner_gap))
            self.bar_btavg_rl.grid(row=1, column=0, padx=(0,inner_gap), pady=0)
            self.bar_btavg_rr.grid(row=1, column=1, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            frame_btemp.grid(row=column_btemp, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_average"]:
                frame_btavg.grid(row=column_btavg, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            frame_btemp.grid(row=0, column=column_btemp, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_average"]:
                frame_btavg.grid(row=0, column=column_btavg, padx=(0,bar_gap), pady=0)

        # Last data
        self.checked = False
        self.last_lap_stime = 0
        self.last_lap_etime = 0
        self.btavg_samples = 1  # number of temperature samples
        self.highlight_timer_start = 0  # sector timer start

        self.last_btemp = [0] * 4
        self.last_btavg = [0] * 4

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read brake temperature data
            btemp = tuple(map(self.temp_units, read_data.brake_temp()))

            # Brake temperature
            self.update_btemp("btemp_fl", btemp[0], self.last_btemp[0])
            self.update_btemp("btemp_fr", btemp[1], self.last_btemp[1])
            self.update_btemp("btemp_rl", btemp[2], self.last_btemp[2])
            self.update_btemp("btemp_rr", btemp[3], self.last_btemp[3])
            self.last_btemp = btemp

            # Brake average temperature
            if self.wcfg["show_average"]:
                lap_stime, lap_etime = read_data.lap_timestamp()

                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.btavg_samples = 1
                    self.highlight_timer_start = lap_etime  # start timer

                    # Highlight reading
                    self.update_btavg("btavg_fl", self.last_btavg[0], 0, 1)
                    self.update_btavg("btavg_fr", self.last_btavg[1], 0, 1)
                    self.update_btavg("btavg_rl", self.last_btavg[2], 0, 1)
                    self.update_btavg("btavg_rr", self.last_btavg[3], 0, 1)

                # Update if time diff
                if lap_etime > self.last_lap_etime:
                    self.last_lap_etime = lap_etime
                    self.btavg_samples += 1
                    btavg = tuple(map(calc.average_value,
                                      self.last_btavg,
                                      btemp,
                                      [self.btavg_samples]*4
                                      ))
                else:
                    btavg = self.last_btavg

                # Update highlight timer
                if self.highlight_timer_start:
                    highlight_timer = lap_etime - self.highlight_timer_start
                    if highlight_timer >= self.wcfg["highlight_duration"]:
                        self.highlight_timer_start = 0  # stop timer
                else:
                    # Update average reading
                    self.update_btavg("btavg_fl", btavg[0], self.last_btavg[0])
                    self.update_btavg("btavg_fr", btavg[1], self.last_btavg[1])
                    self.update_btavg("btavg_rl", btavg[2], self.last_btavg[2])
                    self.update_btavg("btavg_rr", btavg[3], self.last_btavg[3])
                    self.last_btavg = btavg
        else:
            if self.checked:
                self.checked = False
                self.last_lap_stime = 0
                self.last_lap_etime = 0
                self.btavg_samples = 1
                self.highlight_timer_start = 0
                self.last_btavg = [0] * 4

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_btemp(self, suffix, curr, last):
        """Brake temperature"""
        if curr != last:
            if self.wcfg["color_swap_temperature"] == "0":
                btemp_color = {"bg":self.color_heatmap(curr)}
            else:
                btemp_color = {"fg":self.color_heatmap(curr)}

            sign = "°" if self.wcfg["show_degree_sign"] else ""

            getattr(self, f"bar_{suffix}").config(
                btemp_color, text=f"{curr:0{self.leading_zero}.0f}{sign}")

    def update_btavg(self, suffix, curr, last, highlighted=0):
        """Brake average temperature"""
        if curr != last:
            if highlighted:
                color = {"fg":self.wcfg["font_color_average_highlighted"],
                         "bg":self.wcfg["bkg_color_average_highlighted"]}
            else:
                color = {"fg":self.wcfg["font_color_average"],
                         "bg":self.wcfg["bkg_color_average"]}

            sign = "°" if self.wcfg["show_degree_sign"] else ""

            getattr(self, f"bar_{suffix}").config(
                color, text=f"{curr:02.0f}{sign}")

    # Additional methods
    def temp_units(self, value):
        """Temperature units"""
        if self.wcfg["temp_unit"] == "0":
            return round(value - 273.15)
        return round(calc.celsius2fahrenheit(value - 273.15))

    @staticmethod
    def color_heatmap(temp):
        """Brake temperature color"""
        if temp < 100:
            color = "#44F"  # blue
        elif 100 <= temp < 200:
            color = "#48F"
        elif 200 <= temp < 300:
            color = "#4FF"  # cyan
        elif 300 <= temp < 400:
            color = "#4F8"
        elif 400 <= temp < 500:
            color = "#4F4"  # green
        elif 500 <= temp < 600:
            color = "#8F4"
        elif 600 <= temp < 700:
            color = "#FF4"  # yellow
        elif 700 <= temp < 800:
            color = "#F84"
        else:
            color = "#F44"  # red
        return color
