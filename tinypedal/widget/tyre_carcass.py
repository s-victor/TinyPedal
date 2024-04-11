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
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "tyre_carcass"


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
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            text_width = 4 + len(self.sign_text)
        else:
            text_width = 3 + len(self.sign_text)

        self.bar_width_temp = f"min-width: {font_m.width * text_width + bar_padx}px;"

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

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_ctemp = QGridLayout()
        layout_rtemp = QGridLayout()
        layout_ctemp.setSpacing(inner_gap)
        layout_rtemp.setSpacing(inner_gap)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_ctemp = self.wcfg["column_index_carcass"]
        column_rtemp = self.wcfg["column_index_rate_of_change"]

        # Tyre compound
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcmpd = (
                f"color: {self.wcfg['font_color_tyre_compound']};"
                f"background: {self.wcfg['bkg_color_tyre_compound']};"
                f"min-width: {font_m.width + bar_padx}px;"
            )
            self.bar_tcmpd_f = QLabel("-")
            self.bar_tcmpd_f.setAlignment(Qt.AlignCenter)
            self.bar_tcmpd_f.setStyleSheet(bar_style_tcmpd)
            self.bar_tcmpd_r = QLabel("-")
            self.bar_tcmpd_r.setAlignment(Qt.AlignCenter)
            self.bar_tcmpd_r.setStyleSheet(bar_style_tcmpd)
            layout_ctemp.addWidget(self.bar_tcmpd_f, 0, 4)
            layout_ctemp.addWidget(self.bar_tcmpd_r, 1, 4)

            if self.wcfg["show_rate_of_change"]:
                bar_blank_1 = QLabel("")
                bar_blank_1.setStyleSheet(bar_style_tcmpd)
                bar_blank_2 = QLabel("")
                bar_blank_2.setStyleSheet(bar_style_tcmpd)
                layout_rtemp.addWidget(bar_blank_1, 0, 4)
                layout_rtemp.addWidget(bar_blank_2, 1, 4)

        # Tyre carcass temperature
        self.ctemp_set = ("ctemp_fl", "ctemp_fr", "ctemp_rl", "ctemp_rr")

        bar_style_ctemp = (
            f"color: {self.wcfg['font_color_carcass']};"
            f"background: {self.wcfg['bkg_color_carcass']};"
            f"{self.bar_width_temp}"
        )

        for suffix in self.ctemp_set:
            setattr(self, f"bar_{suffix}", QLabel(text_def))
            getattr(self, f"bar_{suffix}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_{suffix}").setStyleSheet(bar_style_ctemp)
            if suffix == "ctemp_fl":  # 0
                layout_ctemp.addWidget(
                    getattr(self, f"bar_{suffix}"), 0, 0)
            if suffix == "ctemp_fr":  # 9
                layout_ctemp.addWidget(
                    getattr(self, f"bar_{suffix}"), 0, 9)
            if suffix == "ctemp_rl":  # 0
                layout_ctemp.addWidget(
                    getattr(self, f"bar_{suffix}"), 1, 0)
            if suffix == "ctemp_rr":  # 9
                layout_ctemp.addWidget(
                    getattr(self, f"bar_{suffix}"), 1, 9)

        # Rate of change
        if self.wcfg["show_rate_of_change"]:
            self.rtemp_set = ("rtemp_fl", "rtemp_fr", "rtemp_rl", "rtemp_rr")
            bar_style_rtemp = (
                f"color: {self.wcfg['font_color_rate_of_change']};"
                f"background: {self.wcfg['bkg_color_rate_of_change']};"
                f"{self.bar_width_temp}"
            )
            for suffix in self.rtemp_set:
                setattr(self, f"bar_{suffix}", QLabel(text_def))
                getattr(self, f"bar_{suffix}").setAlignment(Qt.AlignCenter)
                getattr(self, f"bar_{suffix}").setStyleSheet(bar_style_rtemp)
                if suffix == "rtemp_fl":  # 0
                    layout_rtemp.addWidget(
                        getattr(self, f"bar_{suffix}"), 0, 0)
                if suffix == "rtemp_fr":  # 9
                    layout_rtemp.addWidget(
                        getattr(self, f"bar_{suffix}"), 0, 9)
                if suffix == "rtemp_rl":  # 0
                    layout_rtemp.addWidget(
                        getattr(self, f"bar_{suffix}"), 1, 0)
                if suffix == "rtemp_rr":  # 9
                    layout_rtemp.addWidget(
                        getattr(self, f"bar_{suffix}"), 1, 9)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            layout.addLayout(layout_ctemp, column_ctemp, 0)
            if self.wcfg["show_rate_of_change"]:
                layout.addLayout(layout_rtemp, column_rtemp, 0)
        else:
            # Horizontal layout
            layout.addLayout(layout_ctemp, 0, column_ctemp)
            if self.wcfg["show_rate_of_change"]:
                layout.addLayout(layout_rtemp, 0, column_rtemp)
        self.setLayout(layout)

        # Last data
        self.last_tcmpd = [None] * 2
        self.last_ctemp = [-273.15] * 4
        self.last_rtemp = [0] * 4
        self.last_lap_etime = 0
        self.rtemp_samples = deque([(0,0,0,0) for _ in range(max_samples)], max_samples)

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Tyre compound
            if self.wcfg["show_tyre_compound"]:
                tcmpd = [self.tyre_compound_string[idx] for idx in api.read.tyre.compound()]
                self.update_tcmpd(tcmpd, self.last_tcmpd)
                self.last_tcmpd = tcmpd

            # Tyre carcass temperature
            ctemp = api.read.tyre.carcass_temperature()
            for idx, suffix in enumerate(self.ctemp_set):
                self.update_ctemp(suffix, ctemp[idx], self.last_ctemp[idx])
            self.last_ctemp = ctemp

            # Rate of change
            if self.wcfg["show_rate_of_change"]:
                lap_etime = api.read.timing.elapsed()

                if lap_etime != self.last_lap_etime:  # time stamp difference
                    self.last_lap_etime = lap_etime  # reset time stamp counter
                    self.rtemp_samples.append(ctemp)

                rtemp = tuple(map(self.temp_difference, ctemp, self.rtemp_samples[0]))
                for idx, suffix in enumerate(self.rtemp_set):
                    self.update_rtemp(suffix, rtemp[idx], self.last_rtemp[idx])
                self.last_rtemp = rtemp

    # GUI update methods
    def update_ctemp(self, suffix, curr, last):
        """Tyre carcass temperature"""
        if round(curr) != round(last):
            if self.wcfg["swap_style"]:
                color = (f"color: {self.wcfg['font_color_carcass']};"
                         f"background: {hmp.select_color(self.heatmap, curr)};")
            else:
                color = (f"color: {hmp.select_color(self.heatmap, curr)};"
                         f"background: {self.wcfg['bkg_color_carcass']};")

            getattr(self, f"bar_{suffix}").setText(
                f"{self.temp_units(curr):0{self.leading_zero}.0f}{self.sign_text}")
            getattr(self, f"bar_{suffix}").setStyleSheet(f"{color}{self.bar_width_temp}")

    def update_rtemp(self, suffix, curr, last):
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

            temp = abs(curr)
            if temp < 10:
                temp_text = f"{self.temp_units(temp):.01f}"
            else:
                temp_text = f"{self.temp_units(temp):.0f}"

            getattr(self, f"bar_{suffix}").setText(
                f"{temp_text}{self.sign_text}")
            getattr(self, f"bar_{suffix}").setStyleSheet(f"{color}{self.bar_width_temp}")

    def update_tcmpd(self, curr, last):
        """Tyre compound"""
        if curr != last:
            self.bar_tcmpd_f.setText(curr[0])
            self.bar_tcmpd_r.setText(curr[1])

    # Additional methods
    def temp_units(self, value):
        """Temperature units"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return calc.celsius2fahrenheit(value)
        return value

    @staticmethod
    def temp_difference(value1, value2):
        """Temperature difference"""
        return value1 - value2
