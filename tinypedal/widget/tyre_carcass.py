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
from PySide2.QtWidgets import QGridLayout

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

        text_width = 3 + len(self.sign_text) + (self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_ttemp = font_m.width * text_width + bar_padx
        bar_width_tcmpd = font_m.width + bar_padx

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
        bar_style_tcmpd = self.set_qss(
            self.wcfg["font_color_tyre_compound"],
            self.wcfg["bkg_color_tyre_compound"]
        )
        bar_style_ctemp = self.set_qss(
            self.wcfg["font_color_carcass"],
            self.wcfg["bkg_color_carcass"]
        )
        bar_style_rtemp = self.set_qss(
            self.wcfg["font_color_rate_of_change"],
            self.wcfg["bkg_color_rate_of_change"]
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
        self.bar_ctemp = self.set_qlabel(
            text=text_def,
            style=bar_style_ctemp,
            width=bar_width_ttemp,
            count=4,
        )
        self.set_layout_quad(layout_ctemp, self.bar_ctemp)
        self.set_primary_orient(
            target=layout_ctemp,
            column=self.wcfg["column_index_carcass"],
        )

        if self.wcfg["show_tyre_compound"]:
            self.bar_tcmpd = self.set_qlabel(
                text="-",
                style=bar_style_tcmpd,
                width=bar_width_tcmpd,
                count=2,
            )
            self.set_layout_vert(layout_ctemp, self.bar_tcmpd)

        # Rate of change
        if self.wcfg["show_rate_of_change"]:
            layout_rtemp = QGridLayout()
            layout_rtemp.setSpacing(inner_gap)
            self.bar_rtemp = self.set_qlabel(
                text=text_def,
                style=bar_style_rtemp,
                width=bar_width_ttemp,
                count=4,
            )
            self.set_layout_quad(layout_rtemp, self.bar_rtemp)
            self.set_primary_orient(
                target=layout_rtemp,
                column=self.wcfg["column_index_rate_of_change"],
            )

            if self.wcfg["show_tyre_compound"]:
                bar_blank = self.set_qlabel(
                    text="",
                    style=bar_style_tcmpd,
                    width=bar_width_tcmpd,
                    count=2,
                )
                self.set_layout_vert(layout_rtemp, bar_blank)

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
        if round(curr) != round(last):
            color_temp = hmp.select_color(self.heatmap, curr)
            if self.wcfg["swap_style"]:
                color = f"color: {self.wcfg['font_color_carcass']};background: {color_temp};"
            else:
                color = f"color: {color_temp};background: {self.wcfg['bkg_color_carcass']};"

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
                color = f"color: {self.wcfg['font_color_rate_of_change']};background: {hicolor};"
            else:
                color = f"color: {hicolor};background: {self.wcfg['bkg_color_rate_of_change']};"

            target_bar.setText(self.format_rate_change(curr))
            target_bar.setStyleSheet(color)

    def update_tcmpd(self, target_bar, curr, last):
        """Tyre compound"""
        if curr != last:
            target_bar.setText(self.tyre_compound_string[curr])

    # GUI generate methods
    @staticmethod
    def set_layout_quad(layout, bar_set, row_start=1, column_left=0, column_right=9):
        """Set layout - quad

        Default row index start from 1; reserve row index 0 for caption.
        """
        for idx in range(4):
            layout.addWidget(bar_set[idx], row_start + (idx > 1),
                column_left + (idx % 2) * column_right)

    @staticmethod
    def set_layout_vert(layout, bar_set, row_count=2):
        """Set layout - vertical

        Start from row index 1; reserve row index 0 for caption.
        """
        for index in range(row_count):
            layout.addWidget(bar_set[index], index + 1, 4)

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
