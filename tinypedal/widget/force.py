#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "force"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color_gf = self.wcfg["font_color_g_force"]
        bg_color_gf = self.wcfg["bkg_color_g_force"]
        fg_color_df = self.wcfg["font_color_downforce"]
        bg_color_df = self.wcfg["bkg_color_downforce"]
        font_force = tkfont.Font(family=self.wcfg["font_name"],
                                 size=-self.wcfg["font_size"],
                                 weight=self.wcfg["font_weight"])

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":7,
                     "padx":0, "pady":0, "font":font_force}
        self.bar_gforce_lgt = tk.Label(self, bar_style, fg=fg_color_gf, bg=bg_color_gf)
        self.bar_gforce_lat = tk.Label(self, bar_style, fg=fg_color_gf, bg=bg_color_gf)

        if self.wcfg["show_downforce_ratio"]:
            self.bar_dforce = tk.Label(self, bar_style, fg=fg_color_df, bg=bg_color_df)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            self.bar_gforce_lgt.grid(row=0, column=0, padx=0, pady=0)
            self.bar_gforce_lat.grid(row=1, column=0, padx=0, pady=(bar_gap, 0))

            if self.wcfg["show_downforce_ratio"]:
                self.bar_dforce.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))
        else:
            # Horizontal layout
            self.bar_gforce_lgt.grid(row=0, column=0, padx=0, pady=0)
            self.bar_gforce_lat.grid(row=0, column=1, padx=(bar_gap, 0), pady=0)

            if self.wcfg["show_downforce_ratio"]:
                self.bar_dforce.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)

        # Last data
        self.last_gf_lgt = None
        self.last_gf_lat = None
        self.last_df_ratio = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read acceleration & downforce data
            lgt_accel, lat_accel, downforce = read_data.force()

            # Longitudinal g-force
            gf_lgt = round(calc.gforce(lgt_accel), 2)
            self.update_gf_lgt(gf_lgt, self.last_gf_lgt)
            self.last_gf_lgt = gf_lgt

            # Lateral g-force
            gf_lat = round(calc.gforce(lat_accel), 2)
            self.update_gf_lat(gf_lat, self.last_gf_lat)
            self.last_gf_lat = gf_lat

            # Downforce ratio
            if self.wcfg["show_downforce_ratio"]:
                df_ratio = round(calc.force_ratio(downforce[0], sum(downforce)), 2)
                self.update_df_ratio(df_ratio, self.last_df_ratio)
                self.last_df_ratio = df_ratio

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_gf_lgt(self, curr, last):
        """Longitudinal g-force"""
        if curr != last:
            self.bar_gforce_lgt.config(text=f"{self.gforce_lgt(curr)} {abs(curr):.2f}")

    def update_gf_lat(self, curr, last):
        """Lateral g-force"""
        if curr != last:
            self.bar_gforce_lat.config(text=f"{abs(curr):.2f} {self.gforce_lat(curr)}")

    def update_df_ratio(self, curr, last):
        """Downforce ratio"""
        if curr != last:
            self.bar_dforce.config(text=f"{curr:04.02f}%")

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
