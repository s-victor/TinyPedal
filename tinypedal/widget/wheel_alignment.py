#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from ..api_control import api
from ..base import Widget

WIDGET_NAME = "wheel_alignment"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        font_w = self.calc_font_width(self.wcfg['font_name'], self.wcfg['font_size'])

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_w * 5

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
        layout_camber = QGridLayout()
        layout_toein = QGridLayout()
        layout_camber.setSpacing(0)
        layout_toein.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_camber = self.wcfg["column_index_camber"]
        column_toein = self.wcfg["column_index_toe_in"]

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            )
            bar_desc_camber = QLabel("camber")
            bar_desc_camber.setAlignment(Qt.AlignCenter)
            bar_desc_camber.setStyleSheet(bar_style_desc)
            layout_camber.addWidget(bar_desc_camber, 0, 0, 1, 0)

            bar_desc_toein = QLabel("toe in")
            bar_desc_toein.setAlignment(Qt.AlignCenter)
            bar_desc_toein.setStyleSheet(bar_style_desc)
            layout_toein.addWidget(bar_desc_toein, 0, 0, 1, 0)


        # Camber
        if self.wcfg["show_camber"]:
            bar_style_camber = (
                f"color: {self.wcfg['font_color_camber']};"
                f"background: {self.wcfg['bkg_color_camber']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_camber_fl = QLabel(text_def)
            self.bar_camber_fl.setAlignment(Qt.AlignCenter)
            self.bar_camber_fl.setStyleSheet(bar_style_camber)
            self.bar_camber_fr = QLabel(text_def)
            self.bar_camber_fr.setAlignment(Qt.AlignCenter)
            self.bar_camber_fr.setStyleSheet(bar_style_camber)
            self.bar_camber_rl = QLabel(text_def)
            self.bar_camber_rl.setAlignment(Qt.AlignCenter)
            self.bar_camber_rl.setStyleSheet(bar_style_camber)
            self.bar_camber_rr = QLabel(text_def)
            self.bar_camber_rr.setAlignment(Qt.AlignCenter)
            self.bar_camber_rr.setStyleSheet(bar_style_camber)

            layout_camber.addWidget(self.bar_camber_fl, 1, 0)
            layout_camber.addWidget(self.bar_camber_fr, 1, 1)
            layout_camber.addWidget(self.bar_camber_rl, 2, 0)
            layout_camber.addWidget(self.bar_camber_rr, 2, 1)

        # Toe in
        if self.wcfg["show_toe_in"]:
            bar_style_toein = (
                f"color: {self.wcfg['font_color_toe_in']};"
                f"background: {self.wcfg['bkg_color_toe_in']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_toein_fl = QLabel(text_def)
            self.bar_toein_fl.setAlignment(Qt.AlignCenter)
            self.bar_toein_fl.setStyleSheet(bar_style_toein)
            self.bar_toein_fr = QLabel(text_def)
            self.bar_toein_fr.setAlignment(Qt.AlignCenter)
            self.bar_toein_fr.setStyleSheet(bar_style_toein)
            self.bar_toein_rl = QLabel(text_def)
            self.bar_toein_rl.setAlignment(Qt.AlignCenter)
            self.bar_toein_rl.setStyleSheet(bar_style_toein)
            self.bar_toein_rr = QLabel(text_def)
            self.bar_toein_rr.setAlignment(Qt.AlignCenter)
            self.bar_toein_rr.setStyleSheet(bar_style_toein)

            layout_toein.addWidget(self.bar_toein_fl, 1, 0)
            layout_toein.addWidget(self.bar_toein_fr, 1, 1)
            layout_toein.addWidget(self.bar_toein_rl, 2, 0)
            layout_toein.addWidget(self.bar_toein_rr, 2, 1)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_camber"]:
                layout.addLayout(layout_camber, column_camber, 0)
            if self.wcfg["show_toe_in"]:
                layout.addLayout(layout_toein, column_toein, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_camber"]:
                layout.addLayout(layout_camber, 0, column_camber)
            if self.wcfg["show_toe_in"]:
                layout.addLayout(layout_toein, 0, column_toein)
        self.setLayout(layout)

        # Last data
        self.last_camber = [-1] * 4
        self.last_toein = [-1] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Camber
            if self.wcfg["show_camber"]:
                # Read camber data
                camber = tuple(map(self.round2decimal, api.read.wheel.camber()))

                self.update_wheel("camber_fl", camber[0], self.last_camber[0])
                self.update_wheel("camber_fr", camber[1], self.last_camber[1])
                self.update_wheel("camber_rl", camber[2], self.last_camber[2])
                self.update_wheel("camber_rr", camber[3], self.last_camber[3])
                self.last_camber = camber

            # Toe in
            if self.wcfg["show_toe_in"]:
                # Read toe data
                toein = tuple(map(self.round2decimal, api.read.wheel.toe()))

                self.update_wheel("toein_fl", toein[0], self.last_toein[0])
                self.update_wheel("toein_fr", -toein[1], self.last_toein[1])
                self.update_wheel("toein_rl", toein[2], self.last_toein[2])
                self.update_wheel("toein_rr", -toein[3], self.last_toein[3])
                self.last_toein = toein

    # GUI update methods
    def update_wheel(self, suffix, curr, last):
        """Wheel data"""
        if curr != last:
            getattr(self, f"bar_{suffix}").setText(f"{curr:+.02f}"[:5].rjust(5))

    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(calc.rad2deg(value), 2)
