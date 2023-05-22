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
Force Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "force"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        font_w = QFontMetrics(self.font).averageCharWidth()

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_w * 6

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_lg = self.wcfg["column_index_long_gforce"]
        column_lt = self.wcfg["column_index_lat_gforce"]
        column_df = self.wcfg["column_index_downforce"]

        # G force
        if self.wcfg["show_g_force"]:
            self.bar_gforce_lgt = QLabel("n/a")
            self.bar_gforce_lgt.setAlignment(Qt.AlignCenter)
            self.bar_gforce_lgt.setStyleSheet(
                f"color: {self.wcfg['font_color_g_force']};"
                f"background: {self.wcfg['bkg_color_g_force']};"
                f"min-width: {self.bar_width}px;"
            )

            self.bar_gforce_lat = QLabel("n/a")
            self.bar_gforce_lat.setAlignment(Qt.AlignCenter)
            self.bar_gforce_lat.setStyleSheet(
                f"color: {self.wcfg['font_color_g_force']};"
                f"background: {self.wcfg['bkg_color_g_force']};"
                f"min-width: {self.bar_width}px;"
            )

        # Downforce ratio
        if self.wcfg["show_downforce_ratio"]:
            self.bar_dforce = QLabel("n/a")
            self.bar_dforce.setAlignment(Qt.AlignCenter)
            self.bar_dforce.setStyleSheet(
                f"color: {self.wcfg['font_color_downforce']};"
                f"background: {self.wcfg['bkg_color_downforce']};"
                f"min-width: {self.bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_g_force"]:
                layout.addWidget(self.bar_gforce_lgt, column_lg, 0)
                layout.addWidget(self.bar_gforce_lat, column_lt, 0)
            if self.wcfg["show_downforce_ratio"]:
                layout.addWidget(self.bar_dforce, column_df, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_g_force"]:
                layout.addWidget(self.bar_gforce_lgt, 0, column_lg)
                layout.addWidget(self.bar_gforce_lat, 0, column_lt)
            if self.wcfg["show_downforce_ratio"]:
                layout.addWidget(self.bar_dforce, 0, column_df)
        self.setLayout(layout)

        # Last data
        self.last_gf_lgt = None
        self.last_gf_lat = None
        self.last_df_ratio = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # G force
            if self.wcfg["show_g_force"]:
                # Longitudinal g-force
                gf_lgt = round(mctrl.module_force.output.LgtGForceRaw, 2)
                self.update_gf_lgt(gf_lgt, self.last_gf_lgt)
                self.last_gf_lgt = gf_lgt

                # Lateral g-force
                gf_lat = round(mctrl.module_force.output.LatGForceRaw, 2)
                self.update_gf_lat(gf_lat, self.last_gf_lat)
                self.last_gf_lat = gf_lat

            # Downforce ratio
            if self.wcfg["show_downforce_ratio"]:
                df_ratio = round(mctrl.module_force.output.DownForceRatio, 2)
                self.update_df_ratio(df_ratio, self.last_df_ratio)
                self.last_df_ratio = df_ratio

    # GUI update methods
    def update_gf_lgt(self, curr, last):
        """Longitudinal g-force"""
        if curr != last:
            self.bar_gforce_lgt.setText(f"{self.gforce_lgt(curr)} {abs(curr):.2f}")

    def update_gf_lat(self, curr, last):
        """Lateral g-force"""
        if curr != last:
            self.bar_gforce_lat.setText(f"{abs(curr):.2f} {self.gforce_lat(curr)}")

    def update_df_ratio(self, curr, last):
        """Downforce ratio"""
        if curr != last:
            self.bar_dforce.setText(f"{curr:04.02f}%")

    # Additional methods
    @staticmethod
    def gforce_lgt(g_force):
        """Longitudinal g-force direction symbol"""
        if g_force > 0.1:
            text = "▼"
        elif g_force < -0.1:
            text = "▲"
        else:
            text = "●"
        return text

    @staticmethod
    def gforce_lat(g_force):
        """Lateral g-force direction symbol"""
        if g_force > 0.1:
            text = "◀"
        elif g_force < -0.1:
            text = "▶"
        else:
            text = "●"
        return text
