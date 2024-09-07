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
Tyre pressure Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "tyre_pressure"


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
        bar_width = font_m.width * 4 + bar_padx

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        bar_style_desc = self.set_qss(
            fg_color=self.wcfg["font_color_caption"],
            bg_color=self.wcfg["bkg_color_caption"],
            font_size=int(self.wcfg['font_size'] * 0.8)
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Tyre pressure
        layout_tpres = QGridLayout()
        layout_tpres.setSpacing(0)
        layout.addLayout(layout_tpres, 0, 0)
        bar_style_tpres = self.set_qss(
            self.wcfg["font_color_tyre_pressure"],
            self.wcfg["bkg_color_tyre_pressure"]
        )
        self.bar_tpres = self.set_qlabel(
            text=text_def,
            style=bar_style_tpres,
            width=bar_width,
            count=4,
        )
        self.set_layout_quad(layout_tpres, self.bar_tpres)

        if self.wcfg["show_caption"]:
            cap_tpres = self.set_qlabel(
                text="tyre pres",
                style=bar_style_desc,
            )
            layout_tpres.addWidget(cap_tpres, 0, 0, 1, 0)

        # Last data
        self.last_tpres = [None] * 4

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Tyre pressure
            tpres = api.read.tyre.pressure()
            for idx in range(4):
                self.update_tpres(self.bar_tpres[idx], tpres[idx], self.last_tpres[idx])
            self.last_tpres = tpres

    # GUI update methods
    def update_tpres(self, target_bar, curr, last):
        """Tyre pressure"""
        if curr != last:
            target_bar.setText(self.tyre_pressure_units(curr))

    # GUI generate methods
    @staticmethod
    def set_layout_quad(layout, bar_set, row_start=1, column_left=0, column_right=9):
        """Set layout - quad

        Default row index start from 1; reserve row index 0 for caption.
        """
        for idx in range(4):
            layout.addWidget(bar_set[idx], row_start + (idx > 1),
                column_left + (idx % 2) * column_right)

    # Additional methods
    def tyre_pressure_units(self, value):
        """Tyre pressure units"""
        if self.cfg.units["tyre_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(value):.1f}"
        if self.cfg.units["tyre_pressure_unit"] == "bar":
            return f"{calc.kpa2bar(value):.2f}"
        return f"{value:.0f}"  # kPa
