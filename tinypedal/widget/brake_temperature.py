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
Brake temperature Widget
"""

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "brake_temperature"


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

        text_width = 3 + len(self.sign_text) + (self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_temp = font_m.width * text_width + bar_padx

        # Base style
        self.heatmap = hmp.load_heatmap(self.wcfg["heatmap_name"], "brake_default")
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Brake temperature
        layout_btemp = self.set_grid_layout(gap=inner_gap)
        bar_style_btemp = self.set_qss(
            fg_color=self.wcfg["font_color_temperature"],
            bg_color=self.wcfg["bkg_color_temperature"]
        )
        self.bars_btemp = self.set_qlabel(
            text=text_def,
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
                text=text_def,
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
        self.last_lap_stime = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Brake temperature
            btemp = api.read.brake.temperature()
            for idx, bar_btemp in enumerate(self.bars_btemp):
                self.update_btemp(bar_btemp, round(btemp[idx]))

            # Brake average temperature
            if self.wcfg["show_average"]:
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()

                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.btavg_samples = 1
                    # Highlight reading
                    for idx, bar_btavg in enumerate(self.bars_btavg):
                        self.update_btavg(bar_btavg, bar_btavg.last, True)

                # Update average reading
                not_highlight = lap_etime - self.last_lap_stime >= self.wcfg["highlight_duration"]
                for idx, bar_btavg in enumerate(self.bars_btavg):
                    self.btavg[idx] = calc.mean_iter(
                        self.btavg[idx], btemp[idx], self.btavg_samples)
                    if not_highlight:
                        self.update_btavg(bar_btavg, round(self.btavg[idx]))
                self.btavg_samples += 1

        else:
            if self.checked:
                self.checked = False
                self.btavg = [0] * 4
                self.btavg_samples = 1

    # GUI update methods
    def update_btemp(self, target, data):
        """Brake temperature"""
        if target.last != data:
            target.last = data
            color_temp = hmp.select_color(self.heatmap, data)
            if self.wcfg["swap_style"]:
                color = f"color: {color_temp};background: {self.wcfg['bkg_color_temperature']};"
            else:
                color = f"color: {self.wcfg['font_color_temperature']};background: {color_temp};"

            target.setText(self.format_temperature(data))
            target.setStyleSheet(color)

    def update_btavg(self, target, data, highlighted=False):
        """Brake average temperature"""
        if target.last != data or highlighted:
            target.last = data
            target.setText(self.format_temperature(data))
            target.setStyleSheet(self.bar_style_btavg[highlighted])

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"
