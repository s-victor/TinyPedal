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
Tyre carcass temperature Widget
"""

from collections import deque
from operator import sub as subtract

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "tyre_carcass"


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
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        text_width = 3 + len(self.sign_text) + int(self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_temp = font_m.width * text_width + bar_padx
        bar_width_caption = font_m.width + bar_padx

        max_samples = int(
            min(max(self.wcfg["rate_of_change_interval"], 1), 60)
            / (max(self.wcfg["update_interval"], 10) * 0.001)
        )

        # Base style
        self.heatmap = hmp.load_heatmap(self.wcfg["heatmap_name"], "tyre_default")
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        bar_style_tcmpd = (
            f"color: {self.wcfg['font_color_tyre_compound']};"
            f"background: {self.wcfg['bkg_color_tyre_compound']};"
        )
        bar_style_ctemp = (
            f"color: {self.wcfg['font_color_carcass']};"
            f"background: {self.wcfg['bkg_color_carcass']};"
        )
        bar_style_rtemp = (
            f"color: {self.wcfg['font_color_rate_of_change']};"
            f"background: {self.wcfg['bkg_color_rate_of_change']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Tyre carcass temperature
        layout_ctemp = QGridLayout()
        layout_ctemp.setSpacing(inner_gap)
        self.bar_ctemp = self.gen_bar_set(
            bar_style_ctemp, bar_width_temp, text_def, layout_ctemp)
        if self.wcfg["show_tyre_compound"]:
            self.bar_tcmpd = self.gen_bar_caption(
                bar_style_tcmpd, bar_width_caption, "-", layout_ctemp)
        self.arrange_layout(layout, layout_ctemp, self.wcfg["column_index_carcass"])

        # Rate of change
        if self.wcfg["show_rate_of_change"]:
            layout_rtemp = QGridLayout()
            layout_rtemp.setSpacing(inner_gap)
            self.bar_rtemp = self.gen_bar_set(
                bar_style_rtemp, bar_width_temp, text_def, layout_rtemp)
            if self.wcfg["show_tyre_compound"]:
                self.gen_bar_caption(bar_style_tcmpd, bar_width_caption, "", layout_rtemp)
            self.arrange_layout(layout, layout_rtemp, self.wcfg["column_index_rate_of_change"])

        # Last data
        self.last_tcmpd = [None] * 2
        self.last_ctemp = [-273.15] * 4
        self.last_rtemp = [0] * 4
        self.last_lap_etime = 0
        self.rtemp_samples = deque([(0,0,0,0) for _ in range(max_samples)], max_samples)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Tyre compound
            if self.wcfg["show_tyre_compound"]:
                tcmpd = api.read.tyre.compound()
                for cmpd_idx in range(2):
                    self.update_tcmpd(
                        self.bar_tcmpd[cmpd_idx],
                        tcmpd[cmpd_idx],
                        self.last_tcmpd[cmpd_idx]
                    )
                self.last_tcmpd = tcmpd

            # Tyre carcass temperature
            ctemp = api.read.tyre.carcass_temperature()
            for tyre_idx in range(4):  # 0 - fl, 1 - fr, 2 - rl, 3 - rr
                self.update_ctemp(
                    self.bar_ctemp[tyre_idx],
                    ctemp[tyre_idx],
                    self.last_ctemp[tyre_idx]
                )
            self.last_ctemp = ctemp

            # Rate of change
            if self.wcfg["show_rate_of_change"]:
                lap_etime = api.read.timing.elapsed()

                if lap_etime != self.last_lap_etime:  # time stamp difference
                    self.last_lap_etime = lap_etime  # reset time stamp counter
                    self.rtemp_samples.append(ctemp)

                rtemp = tuple(map(subtract, ctemp, self.rtemp_samples[0]))
                for tyre_idx in range(4):
                    self.update_rtemp(
                        self.bar_rtemp[tyre_idx],
                        rtemp[tyre_idx],
                        self.last_rtemp[tyre_idx]
                    )
                self.last_rtemp = rtemp

    # GUI update methods
    def update_ctemp(self, target_bar, curr, last):
        """Tyre carcass temperature"""
        if curr != last:
            if self.wcfg["swap_style"]:
                color = (f"color: {self.wcfg['font_color_carcass']};"
                         f"background: {hmp.select_color(self.heatmap, curr)};")
            else:
                color = (f"color: {hmp.select_color(self.heatmap, curr)};"
                         f"background: {self.wcfg['bkg_color_carcass']};")

            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(color)

    def update_rtemp(self, target_bar, curr, last):
        """Rate of change"""
        if curr != last:
            if curr > 0:
                hicolor = self.wcfg["font_color_rate_gain"]
            else:
                hicolor = self.wcfg["font_color_rate_loss"]

            if self.wcfg["swap_style"]:
                color = (f"color: {self.wcfg['font_color_rate_of_change']};"
                         f"background: {hicolor};")
            else:
                color = (f"color: {hicolor};"
                         f"background: {self.wcfg['bkg_color_rate_of_change']};")

            target_bar.setText(self.format_rate_change(curr))
            target_bar.setStyleSheet(color)

    def update_tcmpd(self, target_bar, curr, last):
        """Tyre compound"""
        if curr != last:
            target_bar.setText(self.tyre_compound_string[curr])

    # GUI generate methods
    @staticmethod
    def gen_bar_set(bar_style, bar_width, text, layout):
        """Generate bar set"""
        bar_set = tuple(QLabel(text) for _ in range(4))
        for outer_index, bar_temp in enumerate(bar_set):
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
            if outer_index == 0:  # 0
                layout.addWidget(bar_temp, 0, 0)
            elif outer_index == 1:  # 9
                layout.addWidget(bar_temp, 0, 9)
            elif outer_index == 2:  # 0
                layout.addWidget(bar_temp, 1, 0)
            elif outer_index == 3:  # 9
                layout.addWidget(bar_temp, 1, 9)
        return bar_set

    @staticmethod
    def gen_bar_caption(bar_style, bar_width, text, layout):
        """Generate bar caption"""
        bar_set = tuple(QLabel(text) for _ in range(2))
        for index, bar_temp in enumerate(bar_set):
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
            layout.addWidget(bar_temp, index, 4)
        return bar_set

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

    def format_rate_change(self, value):
        """Format temperature rate of change"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):.1f}"[:3].strip(".")
        return f"{value:.1f}"[:3].strip(".")
