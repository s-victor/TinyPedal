#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            text_width = 4 + len(self.sign_text)
        else:
            text_width = 3 + len(self.sign_text)

        # Base style
        self.heatmap = hmp.load_heatmap(self.wcfg["heatmap_name"], "tyre_default")

        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_ctemp = QGridLayout()
        layout.setSpacing(inner_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Tyre compound
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcmpd = (
                f"color: {self.wcfg['font_color_tyre_compound']};"
                f"background: {self.wcfg['bkg_color_tyre_compound']};"
                f"min-width: {font_m.width}px; max-width: {font_m.width}px;"
            )
            self.bar_tcmpd_f = QLabel("-")
            self.bar_tcmpd_f.setAlignment(Qt.AlignCenter)
            self.bar_tcmpd_f.setStyleSheet(bar_style_tcmpd)
            self.bar_tcmpd_r = QLabel("-")
            self.bar_tcmpd_r.setAlignment(Qt.AlignCenter)
            self.bar_tcmpd_r.setStyleSheet(bar_style_tcmpd)
            layout_ctemp.addWidget(self.bar_tcmpd_f, 0, 4)
            layout_ctemp.addWidget(self.bar_tcmpd_r, 1, 4)

        # Tyre carcass temperature
        self.ctemp_set = ("ctemp_fl", "ctemp_fr", "ctemp_rl", "ctemp_rr")

        self.bar_width_temp = font_m.width * text_width
        bar_style_ctemp = (
            f"color: {self.wcfg['font_color_carcass']};"
            f"background: {self.wcfg['bkg_color_carcass']};"
            f"min-width: {self.bar_width_temp}px;"
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

        # Set layout
        layout.addLayout(layout_ctemp, 0, 0)
        self.setLayout(layout)

        # Last data
        self.last_tcmpd = [None] * 2
        self.last_ctemp = [-273.15] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

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

            getattr(self, f"bar_{suffix}").setStyleSheet(
                f"{color}min-width: {self.bar_width_temp}px;")

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
