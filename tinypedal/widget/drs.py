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

WIDGET_NAME = "drs"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

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

        # Last data
        self.last_drs_state = 0

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read DRS data
            drs_state = read_data.drs()

            # DRS update
            self.update_drs(drs_state, self.last_drs_state)
            self.last_drs_state = drs_state

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_drs(self, curr, last):
        """DRS"""
        if curr != last:
            self.bar_drs.config(self.color_drs(curr))

    # Additional methods
    def color_drs(self, drs_state):
        """DRS state color"""
        if drs_state[1] == 1:  # blue
            color = {"fg":self.wcfg['font_color_available'],
                     "bg":self.wcfg['bkg_color_available']}
        elif drs_state[1] == 2:
            if drs_state[0]:  # green
                color = {"fg":self.wcfg['font_color_activated'],
                         "bg":self.wcfg['bkg_color_activated']}
            else:  # orange
                color = {"fg":self.wcfg['font_color_allowed'],
                         "bg":self.wcfg['bkg_color_allowed']}
        else:  # grey
            color = {"fg":self.wcfg['font_color_not_available'],
                     "bg":self.wcfg['bkg_color_not_available']}
        return color
