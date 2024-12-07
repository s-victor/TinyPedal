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
Rake angle Widget
"""

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "rake_angle"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)
        layout = self.set_grid_layout()
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.prefix_text = self.wcfg["prefix_rake_angle"]
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Rake angle
        self.bar_style_rake = (
            self.set_qss(
                fg_color=self.wcfg["font_color_rake_angle"],
                bg_color=self.wcfg["bkg_color_rake_angle"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_rake_angle"],
                bg_color=self.wcfg["warning_color_negative_rake"])
        )
        text_rake = self.format_rake(0)
        self.bar_rake = self.set_qlabel(
            text=text_rake,
            style=self.bar_style_rake[0],
            width=font_m.width * len(text_rake) + bar_padx,
        )
        layout.addWidget(self.bar_rake, 0, 0)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Rake angle
            rake = round(calc.rake(*api.read.wheel.ride_height()), 2)
            self.update_rakeangle(self.bar_rake, rake)

    # GUI update methods
    def update_rakeangle(self, target, data):
        """Rake angle data"""
        if target.last != data:
            target.last = data
            target.setText(self.format_rake(data))
            target.setStyleSheet(self.bar_style_rake[data < 0])

    def format_rake(self, rake):
        """Format rake"""
        rake_angle = f"{calc.slope_angle(rake, self.wcfg['wheelbase']):+.2f}"[:5]
        if self.wcfg["show_ride_height_difference"]:
            ride_diff = f"({abs(rake):02.0f})"[:4]
        else:
            ride_diff = ""
        return f"{self.prefix_text}{rake_angle}{self.sign_text}{ride_diff}"
