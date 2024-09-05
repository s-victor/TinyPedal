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
from ..module_info import minfo
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

        text_width = 3 + len(self.sign_text) + (self.cfg.units["temperature_unit"] == "Fahrenheit")
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
        layout_btemp = QGridLayout()
        layout_btemp.setSpacing(inner_gap)
        bar_style_btemp = self.qss_color(
            self.wcfg["font_color_temperature"],
            self.wcfg["bkg_color_temperature"]
        )
        self.bar_btemp = self.gen_bar_set(4, bar_style_btemp, bar_width_temp, text_def)
        self.set_layout_quad(layout_btemp, self.bar_btemp)
        self.set_layout_orient(1, layout, layout_btemp, self.wcfg["column_index_temperature"])

        # Average brake temperature
        if self.wcfg["show_average"]:
            layout_btavg = QGridLayout()
            layout_btavg.setSpacing(inner_gap)
            self.bar_style_btavg = (
                self.qss_color(
                    self.wcfg["font_color_average"],
                    self.wcfg["bkg_color_average"]),
                self.qss_color(
                    self.wcfg["font_color_highlighted"],
                    self.wcfg["bkg_color_highlighted"])
            )
            self.bar_btavg = self.gen_bar_set(4, self.bar_style_btavg[0], bar_width_temp, text_def)
            self.set_layout_quad(layout_btavg, self.bar_btavg)
            self.set_layout_orient(1, layout, layout_btavg, self.wcfg["column_index_average"])

        # Last data
        self.checked = False
        self.last_lap_stime = 0
        self.btavg_samples = 1  # number of temperature samples

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

                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.btavg_samples = 1
                    # Highlight reading
                    for idx in range(4):
                        self.update_btavg(self.bar_btavg[idx], self.last_btavg[idx], 0, 1)

                # Update average reading
                self.btavg_samples += 1
                for idx in range(4):
                    btavg = calc.mean_iter(self.last_btavg[idx], btemp[idx], self.btavg_samples)
                    if minfo.delta.lapTimeCurrent >= self.wcfg["highlight_duration"]:
                        self.update_btavg(self.bar_btavg[idx], btavg, self.last_btavg[idx])
                    self.last_btavg[idx] = btavg

        else:
            if self.checked:
                self.checked = False
                self.btavg_samples = 1
                self.last_btavg = [0] * 4

    # GUI update methods
    def update_btemp(self, target_bar, curr, last):
        """Brake temperature"""
        if round(curr) != round(last):
            color_temp = hmp.select_color(self.heatmap, curr)
            if self.wcfg["swap_style"]:
                color = f"color: {color_temp};background: {self.wcfg['bkg_color_temperature']};"
            else:
                color = f"color: {self.wcfg['font_color_temperature']};background: {color_temp};"

            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(color)

    def update_btavg(self, target_bar, curr, last, highlighted=0):
        """Brake average temperature"""
        if round(curr) != round(last):
            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(self.bar_style_btavg[highlighted])

    # GUI generate methods
    @staticmethod
    def gen_bar_set(bar_count, bar_style, bar_width, text):
        """Generate bar set"""
        bar_set = tuple(QLabel(text) for _ in range(bar_count))
        for bar_temp in bar_set:
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
        return bar_set

    @staticmethod
    def set_layout_quad(layout, bar_set, row_start=1, column_left=0, column_right=9):
        """Set layout - quad

        Default row index start from 1; reserve row index 0 for caption.
        """
        for idx in range(4):
            layout.addWidget(bar_set[idx], row_start + (idx > 1),
                column_left + (idx % 2) * column_right)

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"
