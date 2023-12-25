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
Tyre pressure Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from . import Overlay

WIDGET_NAME = "tyre_pressure"


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
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_m.width * 4

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_tpres = QGridLayout()
        layout_tpres.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            )
            bar_desc_tpres = QLabel("tyre pres")
            bar_desc_tpres.setAlignment(Qt.AlignCenter)
            bar_desc_tpres.setStyleSheet(bar_style_desc)
            layout_tpres.addWidget(bar_desc_tpres, 0, 0, 1, 0)

        # Tyre pressure
        bar_style_tpres = (
            f"color: {self.wcfg['font_color_tyre_pressure']};"
            f"background: {self.wcfg['bkg_color_tyre_pressure']};"
            f"min-width: {self.bar_width}px;"
        )
        self.bar_tpres_fl = QLabel(text_def)
        self.bar_tpres_fl.setAlignment(Qt.AlignCenter)
        self.bar_tpres_fl.setStyleSheet(bar_style_tpres)
        self.bar_tpres_fr = QLabel(text_def)
        self.bar_tpres_fr.setAlignment(Qt.AlignCenter)
        self.bar_tpres_fr.setStyleSheet(bar_style_tpres)
        self.bar_tpres_rl = QLabel(text_def)
        self.bar_tpres_rl.setAlignment(Qt.AlignCenter)
        self.bar_tpres_rl.setStyleSheet(bar_style_tpres)
        self.bar_tpres_rr = QLabel(text_def)
        self.bar_tpres_rr.setAlignment(Qt.AlignCenter)
        self.bar_tpres_rr.setStyleSheet(bar_style_tpres)

        layout_tpres.addWidget(self.bar_tpres_fl, 1, 0)
        layout_tpres.addWidget(self.bar_tpres_fr, 1, 1)
        layout_tpres.addWidget(self.bar_tpres_rl, 2, 0)
        layout_tpres.addWidget(self.bar_tpres_rr, 2, 1)

        # Set layout
        layout.addLayout(layout_tpres, 0, 0)
        self.setLayout(layout)

        # Last data
        self.last_tpres = [None] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Tyre pressure
            tpres = tuple(map(self.tyre_pressure_units, api.read.tyre.pressure()))

            self.update_tpres("tpres_fl", tpres[0], self.last_tpres[0])
            self.update_tpres("tpres_fr", tpres[1], self.last_tpres[1])
            self.update_tpres("tpres_rl", tpres[2], self.last_tpres[2])
            self.update_tpres("tpres_rr", tpres[3], self.last_tpres[3])
            self.last_tpres = tpres

    # GUI update methods
    def update_tpres(self, suffix, curr, last):
        """Tyre pressure"""
        if curr != last:
            getattr(self, f"bar_{suffix}").setText(curr)

    # Additional methods
    def tyre_pressure_units(self, value):
        """Tyre pressure units"""
        if self.cfg.units["tyre_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(value):.01f}"
        if self.cfg.units["tyre_pressure_unit"] == "bar":
            return f"{calc.kpa2bar(value):.02f}"
        return f"{value:.0f}"  # kPa
