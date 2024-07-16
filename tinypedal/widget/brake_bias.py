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
Brake bias Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "brake_bias"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        self.decimals = max(int(self.wcfg["decimal_places"]), 0)
        self.prefix_text = self.wcfg["prefix_brake_bias"]
        self.sign_text = "%" if self.wcfg["show_percentage_sign"] else ""

        if self.wcfg["show_front_and_rear"]:
            text_default = f"{self.prefix_text}{50:02.0{self.decimals}f}:{50:02.0{self.decimals}f}"
        else:
            text_default = f"{self.prefix_text}{50:02.0{self.decimals}f}{self.sign_text}"

        bar_width = f"min-width: {font_m.width * len(text_default) + bar_padx}px;"

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"{bar_width}"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Brake bias
        self.bar_bbias = QLabel(text_default)
        self.bar_bbias.setAlignment(Qt.AlignCenter)
        self.bar_bbias.setStyleSheet(
            f"color: {self.wcfg['font_color_brake_bias']};"
            f"background: {self.wcfg['bkg_color_brake_bias']};"
        )

        # Set layout
        layout.addWidget(self.bar_bbias, 0, 0)
        self.setLayout(layout)

        # Last data
        self.last_bbias = None

        # Set widget state & start update
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:

            # Brake bias
            bbias = api.read.brake.bias_front() * 100
            self.update_bbias(bbias, self.last_bbias)
            self.last_bbias = bbias

    # GUI update methods
    def update_bbias(self, curr, last):
        """Brake bias"""
        if curr != last:
            if self.wcfg["show_front_and_rear"]:
                text = f"{self.prefix_text}{curr:02.0{self.decimals}f}:{100 - curr:02.0{self.decimals}f}"
            else:
                text = f"{self.prefix_text}{curr:02.0{self.decimals}f}{self.sign_text}"

            self.bar_bbias.setText(text)
