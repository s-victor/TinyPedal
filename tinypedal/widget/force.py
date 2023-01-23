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
        self.bar_gforce_lgt.grid(row=0, column=0, padx=0, pady=0)
        self.bar_gforce_lat.grid(row=1, column=0, padx=0, pady=(bar_gap, 0))

        if self.wcfg["show_downforce_ratio"]:
            self.bar_dforce = tk.Label(self, bar_style, fg=fg_color_df, bg=bg_color_df)
            self.bar_dforce.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read g-force & downforce data
            gf_lgt, gf_lat, df_ratio = read_data.force()

            # Start updating
            # Force update
            self.bar_gforce_lgt.config(text=calc.gforce_lgt(gf_lgt) + f" {abs(gf_lgt):.2f}")
            self.bar_gforce_lat.config(text=f"{abs(gf_lat):.2f} " + calc.gforce_lat(gf_lat))

            if self.wcfg["show_downforce_ratio"]:
                self.bar_dforce.config(text=f"{df_ratio:04.02f}%")

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)
