#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from .. import calculation as calc
from ..api_control import api
from ..const_common import TEXT_NA
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_width = font_m.width * 4 + bar_padx

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )
        bar_style_desc = self.set_qss(
            fg_color=self.wcfg["font_color_caption"],
            bg_color=self.wcfg["bkg_color_caption"],
            font_size=int(self.wcfg['font_size'] * 0.8)
        )

        # Tyre pressure
        layout_tpres = self.set_grid_layout()
        bar_style_tpres = self.set_qss(
            fg_color=self.wcfg["font_color_tyre_pressure"],
            bg_color=self.wcfg["bkg_color_tyre_pressure"]
        )
        self.bars_tpres = self.set_qlabel(
            text=TEXT_NA,
            style=bar_style_tpres,
            width=bar_width,
            count=4,
        )
        self.set_grid_layout_quad(
            layout=layout_tpres,
            targets=self.bars_tpres,
        )
        self.set_primary_orient(
            target=layout_tpres,
        )

        if self.wcfg["show_caption"]:
            cap_tpres = self.set_qlabel(
                text="tyre pres",
                style=bar_style_desc,
            )
            layout_tpres.addWidget(cap_tpres, 0, 0, 1, 0)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Tyre pressure
            tpres = api.read.tyre.pressure()
            for idx, bar_tpres in enumerate(self.bars_tpres):
                self.update_tpres(bar_tpres, tpres[idx])

    # GUI update methods
    def update_tpres(self, target, data):
        """Tyre pressure"""
        if target.last != data:
            target.last = data
            target.setText(self.tyre_pressure_units(data))

    # Additional methods
    def tyre_pressure_units(self, pres):
        """Tyre pressure units"""
        if self.cfg.units["tyre_pressure_unit"] == "psi":
            return f"{calc.kpa2psi(pres):.1f}"
        if self.cfg.units["tyre_pressure_unit"] == "bar":
            return f"{calc.kpa2bar(pres):.2f}"
        return f"{pres:.0f}"  # kPa
