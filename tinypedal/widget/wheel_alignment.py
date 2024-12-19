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
Wheel alignment Widget
"""

from .. import calculation as calc
from ..api_control import api
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
        text_def = "n/a"
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_width = font_m.width * 5 + bar_padx

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

        # Camber
        if self.wcfg["show_camber"]:
            layout_camber = self.set_grid_layout()
            bar_style_camber = self.set_qss(
                fg_color=self.wcfg["font_color_camber"],
                bg_color=self.wcfg["bkg_color_camber"]
            )
            self.bars_camber = self.set_qlabel(
                text=text_def,
                style=bar_style_camber,
                width=bar_width,
                count=4,
                last=-1,
            )
            self.set_grid_layout_quad(
                layout=layout_camber,
                targets=self.bars_camber,
            )
            self.set_primary_orient(
                target=layout_camber,
                column=self.wcfg["column_index_camber"],
            )

            if self.wcfg["show_caption"]:
                cap_camber = self.set_qlabel(
                    text="camber",
                    style=bar_style_desc,
                )
                layout_camber.addWidget(cap_camber, 0, 0, 1, 0)

        # Toe in
        if self.wcfg["show_toe_in"]:
            layout_toein = self.set_grid_layout()
            bar_style_toein = self.set_qss(
                fg_color=self.wcfg["font_color_toe_in"],
                bg_color=self.wcfg["bkg_color_toe_in"]
            )
            self.bars_toein = self.set_qlabel(
                text=text_def,
                style=bar_style_toein,
                width=bar_width,
                count=4,
                last=-1,
            )
            self.set_grid_layout_quad(
                layout=layout_toein,
                targets=self.bars_toein,
            )
            self.set_primary_orient(
                target=layout_toein,
                column=self.wcfg["column_index_toe_in"],
            )

            if self.wcfg["show_caption"]:
                cap_toein = self.set_qlabel(
                    text="toe in",
                    style=bar_style_desc,
                )
                layout_toein.addWidget(cap_toein, 0, 0, 1, 0)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Camber
            if self.wcfg["show_camber"]:
                camber = api.read.wheel.camber()
                for idx, bar_camber in enumerate(self.bars_camber):
                    camber[idx] = round(calc.rad2deg(camber[idx]), 2)
                    self.update_wheel(bar_camber, camber[idx])

            # Toe in
            if self.wcfg["show_toe_in"]:
                toein = api.read.wheel.toe_symmetric()
                for idx, bar_toein in enumerate(self.bars_toein):
                    toein[idx] = round(calc.rad2deg(toein[idx]), 2)
                    self.update_wheel(bar_toein, toein[idx])

    # GUI update methods
    def update_wheel(self, target, data):
        """Wheel data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:+.2f}"[:5])
