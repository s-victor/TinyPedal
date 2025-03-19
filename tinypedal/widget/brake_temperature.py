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
Brake temperature Widget
"""

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ..const_common import TEXT_NA, TEXT_PLACEHOLDER
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
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""

        text_width = 3 + len(self.sign_text) + (self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_temp = font_m.width * text_width + bar_padx

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Heatmap style list: 0 - fl, 1 - fr, 2 - rl, 3 - rr
        self.heatmap_styles = 4 * [
            hmp.load_heatmap_style(
                heatmap_name=self.wcfg["heatmap_name"],
                default_name=hmp.HEATMAP_DEFAULT_BRAKE,
                swap_style=not self.wcfg["swap_style"],
                fg_color=self.wcfg["font_color_temperature"],
                bg_color=self.wcfg["bkg_color_temperature"],
            )
        ]

        # Brake temperature
        layout_btemp = self.set_grid_layout(gap=inner_gap)
        bar_style_btemp = self.set_qss(
            fg_color=self.wcfg["font_color_temperature"],
            bg_color=self.wcfg["bkg_color_temperature"]
        )
        self.bars_btemp = self.set_qlabel(
            text=TEXT_NA,
            style=bar_style_btemp,
            width=bar_width_temp,
            count=4,
            last=0,
        )
        self.set_grid_layout_quad(
            layout=layout_btemp,
            targets=self.bars_btemp,
        )
        self.set_primary_orient(
            target=layout_btemp,
            column=self.wcfg["column_index_temperature"],
        )

        # Average brake temperature
        if self.wcfg["show_average"]:
            layout_btavg = self.set_grid_layout(gap=inner_gap)
            self.bar_style_btavg = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_average"],
                    bg_color=self.wcfg["bkg_color_average"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_highlighted"],
                    bg_color=self.wcfg["bkg_color_highlighted"])
            )
            self.bars_btavg = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_btavg[0],
                width=bar_width_temp,
                count=4,
                last=0,
            )
            self.set_grid_layout_quad(
                layout=layout_btavg,
                targets=self.bars_btavg,
            )
            self.set_primary_orient(
                target=layout_btavg,
                column=self.wcfg["column_index_average"],
            )

        # Last data
        self.checked = False
        self.btavg = [0] * 4
        self.btavg_samples = 1  # number of temperature samples
        self.last_class_name = None
        self.last_lap_stime = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Update heatmap style
            if self.wcfg["enable_heatmap_auto_matching"]:
                class_name = api.read.vehicle.class_name()
                if self.last_class_name != class_name:
                    self.last_class_name = class_name
                    self.update_heatmap(class_name)

            # Brake temperature
            btemp = api.read.brake.temperature()
            for brake_idx, bar_btemp in enumerate(self.bars_btemp):
                self.update_btemp(bar_btemp, round(btemp[brake_idx]), brake_idx)

            # Brake average temperature
            if self.wcfg["show_average"]:
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()

                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.btavg_samples = 1
                    # Highlight reading, +0.000001 to un-highlight later in case no value change
                    for bar_btavg in self.bars_btavg:
                        self.update_btavg(bar_btavg, bar_btavg.last + 0.000001, True)

                # Update average reading
                not_highlight = lap_etime - self.last_lap_stime >= self.wcfg["highlight_duration"]
                for brake_idx, bar_btavg in enumerate(self.bars_btavg):
                    self.btavg[brake_idx] = calc.mean_iter(
                        self.btavg[brake_idx], btemp[brake_idx], self.btavg_samples)
                    if not_highlight:
                        self.update_btavg(bar_btavg, round(self.btavg[brake_idx]))
                self.btavg_samples += 1

        else:
            if self.checked:
                self.checked = False
                self.btavg = [0] * 4
                self.btavg_samples = 1

    # GUI update methods
    def update_btemp(self, target, data, index):
        """Brake temperature"""
        if target.last != data:
            target.last = data
            target.setText(self.format_temperature(data))
            target.setStyleSheet(calc.select_grade(self.heatmap_styles[index], data))

    def update_btavg(self, target, data, highlighted=False):
        """Brake average temperature"""
        if target.last != data or highlighted:
            target.last = data
            target.setText(self.format_temperature(data))
            target.setStyleSheet(self.bar_style_btavg[highlighted])

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if value < -100:
            return TEXT_PLACEHOLDER
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"

    def update_heatmap(self, class_name: str):
        """Update heatmap"""
        heatmap_f = hmp.select_brake_heatmap_name(
            hmp.set_predefined_brake_name(class_name, True)
        )
        heatmap_r = hmp.select_brake_heatmap_name(
            hmp.set_predefined_brake_name(class_name, False)
        )
        heatmap_style_f = hmp.load_heatmap_style(
            heatmap_name=heatmap_f,
            default_name=hmp.HEATMAP_DEFAULT_BRAKE,
            swap_style=not self.wcfg["swap_style"],
            fg_color=self.wcfg["font_color_temperature"],
            bg_color=self.wcfg["bkg_color_temperature"],
        )
        heatmap_style_r = hmp.load_heatmap_style(
            heatmap_name=heatmap_r,
            default_name=hmp.HEATMAP_DEFAULT_BRAKE,
            swap_style=not self.wcfg["swap_style"],
            fg_color=self.wcfg["font_color_temperature"],
            bg_color=self.wcfg["bkg_color_temperature"],
        )
        self.heatmap_styles[0] = heatmap_style_f
        self.heatmap_styles[1] = heatmap_style_f
        self.heatmap_styles[2] = heatmap_style_r
        self.heatmap_styles[3] = heatmap_style_r
