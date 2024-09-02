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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "wheel_alignment"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        bar_width = font_m.width * 5 + bar_padx

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        bar_style_desc = (
            f"color: {self.wcfg['font_color_caption']};"
            f"background: {self.wcfg['bkg_color_caption']};"
            f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Camber
        if self.wcfg["show_camber"]:
            layout_camber = QGridLayout()
            layout_camber.setSpacing(0)
            bar_style_camber = self.qss_color(self.wcfg["font_color_camber"], self.wcfg["bkg_color_camber"])
            self.bar_camber = self.gen_bar_set(4, bar_style_camber, bar_width, text_def)
            self.set_layout_quad(layout_camber, self.bar_camber)

            if self.wcfg["show_caption"]:
                self.gen_bar_caption(bar_style_desc, "camber", layout_camber)

            self.set_layout_orient(layout, layout_camber, self.wcfg["column_index_camber"])

        # Toe in
        if self.wcfg["show_toe_in"]:
            layout_toein = QGridLayout()
            layout_toein.setSpacing(0)
            bar_style_toein = self.qss_color(self.wcfg["font_color_toe_in"], self.wcfg["bkg_color_toe_in"])
            self.bar_toein = self.gen_bar_set(4, bar_style_toein, bar_width, text_def)
            self.set_layout_quad(layout_toein, self.bar_toein)

            if self.wcfg["show_caption"]:
                self.gen_bar_caption(bar_style_desc, "toe in", layout_toein)

            self.set_layout_orient(layout, layout_toein, self.wcfg["column_index_toe_in"])

        # Last data
        self.last_camber = [-1] * 4
        self.last_toein = [-1] * 4

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Camber
            if self.wcfg["show_camber"]:
                camber = tuple(map(self.round2decimal, api.read.wheel.camber()))
                for idx in range(4):
                    self.update_wheel(self.bar_camber[idx], camber[idx], self.last_camber[idx])
                self.last_camber = camber

            # Toe in
            if self.wcfg["show_toe_in"]:
                toein = tuple(map(self.round2decimal, api.read.wheel.toe_symmetric()))
                for idx in range(4):
                    self.update_wheel(self.bar_toein[idx], toein[idx], self.last_toein[idx])
                self.last_toein = toein

    # GUI update methods
    def update_wheel(self, target_bar, curr, last):
        """Wheel data"""
        if curr != last:
            target_bar.setText(f"{curr:+.2f}"[:5])

    # GUI generate methods
    @staticmethod
    def gen_bar_caption(bar_style, text, layout):
        """Generate caption"""
        bar_temp = QLabel(text)
        bar_temp.setAlignment(Qt.AlignCenter)
        bar_temp.setStyleSheet(bar_style)
        # Row index 0, row span 1
        layout.addWidget(bar_temp, 0, 0, 1, 0)
        return bar_temp

    @staticmethod
    def gen_bar_set(bar_count, bar_style, bar_width, text):
        """Generate bar set"""
        bar_set = tuple(QLabel(text) for _ in range(bar_count))
        for bar_temp in bar_set:
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
        return bar_set

    @staticmethod
    def set_layout_quad(layout, bar_set, row_start=1, column_left=0, column_right=9):
        """Set layout - quad

        Default row index start from 1; reserve row index 0 for caption.
        """
        for idx in range(4):
            layout.addWidget(bar_set[idx], row_start + (idx > 1),
                column_left + (idx % 2) * column_right)

    def set_layout_orient(self, layout_main, layout_sub, column_index):
        """Set primary layout orientation"""
        if self.wcfg["layout"] == 0:  # Vertical layout
            layout_main.addLayout(layout_sub, column_index, 0)
        else:  # Horizontal layout
            layout_main.addLayout(layout_sub, 0, column_index)

    # Additional methods
    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(calc.rad2deg(value), 2)
