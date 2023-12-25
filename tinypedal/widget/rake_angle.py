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
Rake angle Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from . import Overlay

WIDGET_NAME = "rake_angle"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""

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
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Rake angle
        self.bar_rake = QLabel("RAKE")
        self.bar_rake.setAlignment(Qt.AlignCenter)
        self.bar_rake.setStyleSheet(
            f"color: {self.wcfg['font_color_rake_angle']};"
            f"background: {self.wcfg['bkg_color_rake_angle']};"
            f"min-width: {self.font_m.width * 8}px;"
            f"max-width: {self.font_m.width * 8}px;"
        )

        # Set layout
        layout.addWidget(self.bar_rake, 0, 0)
        self.setLayout(layout)

        # Last data
        self.last_rake = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Rake angle
            rake = round(calc.rake(*api.read.wheel.ride_height()), 2)
            self.update_rakeangle(rake, self.last_rake)
            self.last_rake = rake

    # GUI update methods
    def update_rakeangle(self, curr, last):
        """Rake angle data"""
        if curr != last:
            if curr >= 0:
                bgcolor = self.wcfg["bkg_color_rake_angle"]
            else:
                bgcolor = self.wcfg["warning_color_negative_rake"]

            rake_angle = calc.rake2angle(curr, self.wcfg["wheelbase"])
            ride_diff = f"({abs(curr):02.0f})" if self.wcfg["show_ride_height_difference"] else ""
            text = f"{self.wcfg['prefix_rake_angle']}{rake_angle:+.02f}{self.sign_text}{ride_diff}"

            self.bar_rake.setText(text)
            self.bar_rake.setStyleSheet(
                f"color: {self.wcfg['font_color_rake_angle']};"
                f"background: {bgcolor};"
                f"min-width: {self.font_m.width * len(text)}px;"
                f"max-width: {self.font_m.width * len(text)}px;"
            )
