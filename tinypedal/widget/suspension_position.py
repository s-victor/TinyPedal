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
Suspension position Widget
"""

from ..api_control import api
from ._base import Overlay
from ._painter import WheelGaugeBar

WIDGET_NAME = "suspension_position"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        self.setFont(font)
        font_m = self.get_font_metrics(font)
        font_offset = self.calc_font_offset(font_m)

        # Config variable
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])
        bar_width = max(self.wcfg["bar_width"], 20)
        bar_height = int(font_m.capital + pady * 2)
        max_range = max(int(self.wcfg["position_max_range"]), 10)

        # Suspension position
        self.bars_susp = tuple(
            WheelGaugeBar(
                padding_x=padx,
                bar_width=bar_width,
                bar_height=bar_height,
                font_offset=font_offset,
                max_range=max_range,
                input_color=self.wcfg["positive_position_color"],
                fg_color=self.wcfg["font_color"],
                bg_color=self.wcfg["bkg_color"],
                negative_color=self.wcfg["negative_position_color"],
                right_side=idx % 2,
            ) for idx in range(4)
        )
        self.set_grid_layout_quad(
            layout=layout,
            targets=self.bars_susp,
        )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            susp_set = api.read.wheel.suspension_deflection()
            for susp, bar_susp in zip(susp_set, self.bars_susp):
                self.update_susp(bar_susp, round(susp))

    # GUI update methods
    def update_susp(self, target, data):
        """Suspension position"""
        if target.last != data:
            target.last = data
            target.update_input(abs(data))
