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
DRS Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent


class Draw(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "drs"

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self)
        self.cfg = config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_drs = tkfont.Font(family=self.wcfg["font_name"],
                               size=-self.wcfg["font_size"],
                               weight=self.wcfg["font_weight"])

        # Draw label
        self.bar_drs = tk.Label(self, text="DRS", bd=0, height=1, width=4,
                                padx=0, pady=0, font=font_drs,
                                fg=self.wcfg["font_color_not_available"],
                                bg=self.wcfg["bkg_color_not_available"])
        self.bar_drs.grid(row=0, column=0, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read DRS data
            drs_on, drs_status = read_data.drs()

            # Start updating
            # DRS update
            if drs_status == 1:  # blue
                self.bar_drs.config(fg=self.wcfg["font_color_available"],
                                    bg=self.wcfg["bkg_color_available"])
            elif drs_status == 2:
                if drs_on:  # green
                    self.bar_drs.config(fg=self.wcfg["font_color_activated"],
                                        bg=self.wcfg["bkg_color_activated"])
                else:  # orange
                    self.bar_drs.config(fg=self.wcfg["font_color_allowed"],
                                        bg=self.wcfg["bkg_color_allowed"])
            else:  # grey
                self.bar_drs.config(fg=self.wcfg["font_color_not_available"],
                                    bg=self.wcfg["bkg_color_not_available"])

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)
