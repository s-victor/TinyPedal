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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

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

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        inner_gap = self.wcfg["inner_gap"]
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        self.sign_text = "°" if self.wcfg["show_degree_sign"] else ""
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        text_width = 3 + len(self.sign_text) + int(self.cfg.units["temperature_unit"] == "Fahrenheit")
        bar_width_temp = font_m.width * text_width + bar_padx
        bar_width_caption = font_m.width + bar_padx

        # Base style
        self.heatmap = hmp.load_heatmap(self.wcfg["heatmap_name"], "tyre_default")
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        bar_style_tcmpd = (
            f"color: {self.wcfg['font_color_tyre_compound']};"
            f"background: {self.wcfg['bkg_color_tyre_compound']};"
        )
        bar_style_stemp = (
            f"color: {self.wcfg['font_color_surface']};"
            f"background: {self.wcfg['bkg_color_surface']};"
        )
        bar_style_itemp = (
            f"color: {self.wcfg['font_color_innerlayer']};"
            f"background: {self.wcfg['bkg_color_innerlayer']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Tyre temperature
        layout_stemp = QGridLayout()
        layout_stemp.setSpacing(inner_gap)
        self.bar_stemp = self.gen_bar_set(
            bar_style_stemp, bar_width_temp, text_def, layout_stemp)
        if self.wcfg["show_tyre_compound"]:
            self.bar_tcmpd = self.gen_bar_caption(
                bar_style_tcmpd, bar_width_caption, "-", layout_stemp)
        self.arrange_layout(layout, layout_stemp, self.wcfg["column_index_surface"])

        # Tyre inner temperature
        if self.wcfg["show_innerlayer"]:
            layout_itemp = QGridLayout()
            layout_itemp.setSpacing(inner_gap)
            self.bar_itemp = self.gen_bar_set(
                bar_style_itemp, bar_width_temp, text_def, layout_itemp)
            if self.wcfg["show_tyre_compound"]:
                self.gen_bar_caption(bar_style_tcmpd, bar_width_caption, "", layout_itemp)
            self.arrange_layout(layout, layout_itemp, self.wcfg["column_index_innerlayer"])

        # Last data
        self.last_tcmpd = [None] * 2
        self.last_stemp = self.create_last_data()
        self.last_itemp = self.create_last_data()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Tyre compound
            if self.wcfg["show_tyre_compound"]:
                tcmpd = api.read.tyre.compound()
                for cmpd_idx in range(2):
                    self.update_tcmpd(
                        self.bar_tcmpd[cmpd_idx],
                        tcmpd[cmpd_idx],
                        self.last_tcmpd[cmpd_idx]
                    )
                self.last_tcmpd = tcmpd

            if self.wcfg["show_inner_center_outer"]:
                # Surface temperature
                stemp = api.read.tyre.surface_temperature()
                for tyre_idx in range(4):  # 0 - fl, 1 - fr, 2 - rl, 3 - rr
                    for patch_idx in range(3):  # 0 1 2 / 7 8 9
                        self.update_stemp(
                            self.bar_stemp[tyre_idx][patch_idx],
                            stemp[tyre_idx][patch_idx],
                            self.last_stemp[tyre_idx][patch_idx]
                        )
                self.last_stemp = stemp

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = api.read.tyre.inner_temperature()
                    for tyre_idx in range(4):
                        for patch_idx in range(3):
                            self.update_itemp(
                                self.bar_itemp[tyre_idx][patch_idx],
                                itemp[tyre_idx][patch_idx],
                                self.last_itemp[tyre_idx][patch_idx]
                            )
                    self.last_itemp = itemp
            else:
                # Surface temperature
                stemp = tuple(map(calc.mean, api.read.tyre.surface_temperature()))
                for tyre_idx in range(4):  # 0 - fl, 1 - fr, 2 - rl, 3 - rr
                    self.update_stemp(
                        self.bar_stemp[tyre_idx],
                        stemp[tyre_idx],
                        self.last_stemp[tyre_idx]
                    )
                self.last_stemp = stemp

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = tuple(map(calc.mean, api.read.tyre.inner_temperature()))
                    for tyre_idx in range(4):
                        self.update_itemp(
                            self.bar_itemp[tyre_idx],
                            itemp[tyre_idx],
                            self.last_itemp[tyre_idx]
                        )
                    self.last_itemp = itemp

    # GUI update methods
    def update_stemp(self, target_bar, curr, last):
        """Tyre surface temperature"""
        if curr != last:
            if self.wcfg["swap_style"]:
                color = (f"color: {self.wcfg['font_color_surface']};"
                         f"background: {hmp.select_color(self.heatmap, curr)};")
            else:
                color = (f"color: {hmp.select_color(self.heatmap, curr)};"
                         f"background: {self.wcfg['bkg_color_surface']};")

            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(color)

    def update_itemp(self, target_bar, curr, last):
        """Tyre inner temperature"""
        if curr != last:
            if self.wcfg["swap_style"]:
                color = (f"color: {self.wcfg['font_color_innerlayer']};"
                         f"background: {hmp.select_color(self.heatmap, curr)};")
            else:
                color = (f"color: {hmp.select_color(self.heatmap, curr)};"
                         f"background: {self.wcfg['bkg_color_innerlayer']};")

            target_bar.setText(self.format_temperature(curr))
            target_bar.setStyleSheet(color)

    def update_tcmpd(self, target_bar, curr, last):
        """Tyre compound"""
        if curr != last:
            target_bar.setText(self.tyre_compound_string[curr])

    # GUI generate methods
    def gen_bar_set(self, bar_style, bar_width, text, layout):
        """Generate bar set"""
        if self.wcfg["show_inner_center_outer"]:
            return tuple(self.gen_bar_set_ico(bar_style, bar_width, text, layout, idx)
                         for idx in range(4))
        return self.gen_bar_set_avg(bar_style, bar_width, text, layout)

    @staticmethod
    def gen_bar_set_avg(bar_style, bar_width, text, layout):
        """Generate bar set (average)"""
        bar_set = tuple(QLabel(text) for _ in range(4))
        for outer_index, bar_temp in enumerate(bar_set):
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
            if outer_index == 0:  # 0
                layout.addWidget(bar_temp, 0, 0)
            elif outer_index == 1:  # 9
                layout.addWidget(bar_temp, 0, 9)
            elif outer_index == 2:  # 0
                layout.addWidget(bar_temp, 1, 0)
            elif outer_index == 3:  # 9
                layout.addWidget(bar_temp, 1, 9)
        return bar_set

    @staticmethod
    def gen_bar_set_ico(bar_style, bar_width, text, layout, outer_index):
        """Generate bar set (inner-center-outer)"""
        bar_set = tuple(QLabel(text) for _ in range(3))
        for index, bar_temp in enumerate(bar_set):
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
            if outer_index == 0:  # 2 1 0
                layout.addWidget(bar_temp, 0, index)
            elif outer_index == 1:  # 7 8 9
                layout.addWidget(bar_temp, 0, index + 7)
            elif outer_index == 2:  # 2 1 0
                layout.addWidget(bar_temp, 1, index)
            elif outer_index == 3:  # 7 8 9
                layout.addWidget(bar_temp, 1, index + 7)
        return bar_set

    @staticmethod
    def gen_bar_caption(bar_style, bar_width, text, layout):
        """Generate bar caption"""
        bar_set = tuple(QLabel(text) for _ in range(2))
        for index, bar_temp in enumerate(bar_set):
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
            layout.addWidget(bar_temp, index, 4)
        return bar_set

    def arrange_layout(self, layout_main, layout_sub, column_index):
        """Arrange layout"""
        if self.wcfg["layout"] == 0:  # Vertical layout
            layout_main.addLayout(layout_sub, column_index, 0)
        else:  # Horizontal layout
            layout_main.addLayout(layout_sub, 0, column_index)

    # Additional methods
    def format_temperature(self, value):
        """Format temperature"""
        if self.cfg.units["temperature_unit"] == "Fahrenheit":
            return f"{calc.celsius2fahrenheit(value):0{self.leading_zero}.0f}{self.sign_text}"
        return f"{value:0{self.leading_zero}.0f}{self.sign_text}"

    def create_last_data(self):
        """Create last data list"""
        if self.wcfg["show_inner_center_outer"]:
            return [[-273.15] * 3 for _ in range(4)]
        return [-273.15] * 4
