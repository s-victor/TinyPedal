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
Brake temperature Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "brake_temperature"


class Realtime(Overlay):
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
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""

        text_width = 3 + len(self.sign_text) + int(self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_temp = font_m.width * text_width + bar_padx

        # Base style
        self.heatmap = hmp.load_heatmap(self.wcfg["heatmap_name"], "brake_default")
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

        # Brake temperature
        bar_style_btemp = self.gen_bar_style(
            self.wcfg["font_color_temperature"], self.wcfg["bkg_color_temperature"])
        self.bar_btemp = self.gen_bar_set(bar_style_btemp, bar_width_temp, text_def)
        layout_btemp = self.gen_layout(self.bar_btemp, inner_gap)
        self.arrange_layout(layout, layout_btemp, self.wcfg["column_index_temperature"])

        # Average brake temperature
        if self.wcfg["show_average"]:
            self.bar_style_btavg = self.gen_bar_style(
                self.wcfg["font_color_average"], self.wcfg["bkg_color_average"],
                self.wcfg["font_color_highlighted"], self.wcfg["bkg_color_highlighted"])
            self.bar_btavg = self.gen_bar_set(self.bar_style_btavg[0], bar_width_temp, text_def)
            layout_btavg = self.gen_layout(self.bar_btavg, inner_gap)
            self.arrange_layout(layout, layout_btavg, self.wcfg["column_index_average"])

        # Last data
        self.checked = False
        self.last_lap_stime = 0
        self.last_lap_etime = 0
        self.btavg_samples = 1  # number of temperature samples
        self.highlight_timer_start = 0  # sector timer start

        self.last_btemp = [-273.15] * 4
        self.last_btavg = [0] * 4

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Brake temperature
            btemp = api.read.brake.temperature()
            for idx in range(4):
                self.update_btemp(self.bar_btemp[idx], btemp[idx], self.last_btemp[idx])
            self.last_btemp = btemp

            # Brake average temperature
            if self.wcfg["show_average"]:
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()

                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.btavg_samples = 1
                    self.highlight_timer_start = lap_etime  # start timer

                    # Highlight reading
                    for idx in range(4):
                        self.update_btavg(self.bar_btavg[idx], self.last_btavg[idx], 0, 1)

                # Update highlight timer
                if self.highlight_timer_start:
                    if lap_etime - self.highlight_timer_start >= self.wcfg["highlight_duration"]:
                        self.highlight_timer_start = 0  # stop timer

                # Update average reading
                if lap_etime != self.last_lap_etime:
                    self.last_lap_etime = lap_etime
                    self.btavg_samples += 1
                    for idx in range(4):
                        btavg = calc.mean_iter(self.last_btavg[idx], btemp[idx], self.btavg_samples)
                        if not self.highlight_timer_start:
                            self.update_btavg(self.bar_btavg[idx], btavg, self.last_btavg[idx])
                        self.last_btavg[idx] = btavg

        else:
            if self.checked:
                self.checked = False
                self.btavg_samples = 1
                self.highlight_timer_start = 0
                self.last_btavg = [0] * 4

    # GUI update methods
    def update_btemp(self, target_bar, curr, last):
        """Brake temperature"""
        if curr != last:
            if self.wcfg["swap_style"]:
                color = (f"color: {hmp.select_color(self.heatmap, curr)};"
                         f"background: {self.wcfg['bkg_color_temperature']};")
            else:
                color = (f"color: {self.wcfg['font_color_temperature']};"
                         f"background: {hmp.select_color(self.heatmap, curr)};")

            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(color)

    def update_btavg(self, target_bar, curr, last, highlighted=0):
        """Brake average temperature"""
        if curr != last:
            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(self.bar_style_btavg[highlighted])

    # GUI generate methods
    @staticmethod
    def gen_bar_style(fg_color, bg_color, fg_color_hi="", bg_color_hi=""):
        """Generate bar style"""
        if fg_color_hi and bg_color_hi:
            return (f"color: {fg_color};background: {bg_color}",
                    f"color: {fg_color_hi};background: {bg_color_hi}")
        return f"color: {fg_color};background: {bg_color}"

    @staticmethod
    def gen_bar_set(bar_style, bar_width, text):
        """Generate bar set"""
        bar_set = tuple(QLabel(text) for _ in range(4))
        for bar_temp in bar_set:
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
        return bar_set

    @staticmethod
    def gen_layout(target_bar, inner_gap=0):
        """Generate layout"""
        layout = QGridLayout()
        layout.setSpacing(inner_gap)
        # Start from row index 1; index 0 reserved for caption
        layout.addWidget(target_bar[0], 1, 0)
        layout.addWidget(target_bar[1], 1, 1)
        layout.addWidget(target_bar[2], 2, 0)
        layout.addWidget(target_bar[3], 2, 1)
        return layout

    def arrange_layout(self, layout_main, layout_sub, column_index):
        """Arrange layout"""
        if self.wcfg["layout"] == 0:  # Vertical layout
            layout_main.addLayout(layout_sub, column_index, 0)
        else:  # Horizontal layout
            layout_main.addLayout(layout_sub, 0, column_index)

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"
