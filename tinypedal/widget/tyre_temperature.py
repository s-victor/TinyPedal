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
Tyre temperature Widget
"""

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "tyre_temperature"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        text_width = 3 + len(self.sign_text) + (self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_ttemp = font_m.width * text_width + bar_padx
        bar_width_tcmpd = font_m.width + bar_padx

        # Base style
        self.heatmap_s = hmp.load_heatmap_style(
            heatmap_name=self.wcfg["heatmap_name"],
            default_name="tyre_default",
            swap_style=self.wcfg["swap_style"],
            fg_color=self.wcfg["font_color_surface"],
            bg_color=self.wcfg["bkg_color_surface"],
        )
        self.heatmap_i = hmp.load_heatmap_style(
            heatmap_name=self.wcfg["heatmap_name"],
            default_name="tyre_default",
            swap_style=self.wcfg["swap_style"],
            fg_color=self.wcfg["font_color_innerlayer"],
            bg_color=self.wcfg["bkg_color_innerlayer"],
        )
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )
        bar_style_tcmpd = self.set_qss(
            fg_color=self.wcfg["font_color_tyre_compound"],
            bg_color=self.wcfg["bkg_color_tyre_compound"]
        )
        bar_style_stemp = self.set_qss(
            fg_color=self.wcfg["font_color_surface"],
            bg_color=self.wcfg["bkg_color_surface"]
        )
        bar_style_itemp = self.set_qss(
            fg_color=self.wcfg["font_color_innerlayer"],
            bg_color=self.wcfg["bkg_color_innerlayer"]
        )

        # Tyre temperature
        layout_stemp = self.set_grid_layout(gap=inner_gap)
        self.bars_stemp = self.set_table(
            text=text_def,
            style=bar_style_stemp,
            width=bar_width_ttemp,
            layout=layout_stemp,
        )
        self.set_primary_orient(
            target=layout_stemp,
            column=self.wcfg["column_index_surface"],
        )

        if self.wcfg["show_tyre_compound"]:
            self.bars_tcmpd = self.set_qlabel(
                text="-",
                style=bar_style_tcmpd,
                width=bar_width_tcmpd,
                count=2,
            )
            self.set_grid_layout_vert(
                layout=layout_stemp,
                targets=self.bars_tcmpd,
            )

        # Tyre inner temperature
        if self.wcfg["show_innerlayer"]:
            layout_itemp = self.set_grid_layout(gap=inner_gap)
            self.bars_itemp = self.set_table(
                text=text_def,
                style=bar_style_itemp,
                width=bar_width_ttemp,
                layout=layout_itemp,
            )
            self.set_primary_orient(
                target=layout_itemp,
                column=self.wcfg["column_index_innerlayer"],
            )

            if self.wcfg["show_tyre_compound"]:
                bars_blank = self.set_qlabel(
                    text="",
                    style=bar_style_tcmpd,
                    width=bar_width_tcmpd,
                    count=2,
                )
                self.set_grid_layout_vert(
                    layout=layout_itemp,
                    targets=bars_blank,
                )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Tyre compound
            if self.wcfg["show_tyre_compound"]:
                tcmpd = api.read.tyre.compound()
                for cmpd_idx, bar_tcmpd in enumerate(self.bars_tcmpd):
                    self.update_tcmpd(bar_tcmpd, tcmpd[cmpd_idx])

            if self.wcfg["show_inner_center_outer"]:
                # Surface temperature: 0 - fl, 3 - fr, 6 - rl, 9 - rr
                stemp = api.read.tyre.surface_temperature_ico()
                for tyre_idx, bar_stemp in enumerate(self.bars_stemp):
                    self.update_stemp(bar_stemp, round(stemp[tyre_idx]))

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = api.read.tyre.inner_temperature_ico()
                    for tyre_idx, bar_itemp in enumerate(self.bars_itemp):
                        self.update_itemp(bar_itemp, round(itemp[tyre_idx]))
            else:
                # Surface temperature: 0 - fl, 1 - fr, 2 - rl, 3 - rr
                stemp = api.read.tyre.surface_temperature_avg()
                for tyre_idx, bar_stemp in enumerate(self.bars_stemp):
                    self.update_stemp(bar_stemp, round(stemp[tyre_idx]))

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = api.read.tyre.inner_temperature_avg()
                    for tyre_idx, bar_itemp in enumerate(self.bars_itemp):
                        self.update_itemp(bar_itemp, round(itemp[tyre_idx]))

    # GUI update methods
    def update_stemp(self, target, data):
        """Tyre surface temperature"""
        if target.last != data:
            target.last = data
            target.setText(self.format_temperature(data))
            target.setStyleSheet(hmp.select_color(self.heatmap_s, data))

    def update_itemp(self, target, data):
        """Tyre inner temperature"""
        if target.last != data:
            target.last = data
            target.setText(self.format_temperature(data))
            target.setStyleSheet(hmp.select_color(self.heatmap_i, data))

    def update_tcmpd(self, target, data):
        """Tyre compound"""
        if target.last != data:
            target.last = data
            target.setText(self.tyre_compound_string[data])

    # GUI generate methods
    def set_table(self, text, style, width, layout):
        """Set table"""
        if self.wcfg["show_inner_center_outer"]:
            bar_set = self.set_qlabel(
                text=text,
                style=style,
                width=width,
                count=12,  # 3 x 4 tyres
                last=0,
            )
            self.set_grid_layout_tri_quad(layout, bar_set)
        else:
            bar_set = self.set_qlabel(
                text=text,
                style=style,
                width=width,
                count=4,
                last=0,
            )
            self.set_grid_layout_quad(layout, bar_set)
        return bar_set

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"
