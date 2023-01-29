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
TopSpeed Widget
"""

import re
import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "topspeed"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_topspeed = tkfont.Font(family=self.wcfg["font_name"],
                                   size=-self.wcfg["font_size"],
                                   weight=self.wcfg["font_weight"])

        self.verified = False  # load & save switch

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_topspeed}
        #Current lap top speed
        self.bar_topspeed_cur = tk.Label(self, bar_style, text="", width=5,
                                      fg=self.wcfg["font_color_topspeed"],
                                      bg=self.wcfg["bkg_color_topspeed"])

        self.bar_topspeed_best = tk.Label(self, bar_style, text="", width=5,
                                       fg=self.wcfg["font_color_topspeed"],
                                       bg=self.wcfg["bkg_color_topspeed"])


        self.bar_topspeed_cur.grid(row=0, column=0, padx=(0,bar_gap), pady=(0,bar_gap))
        self.bar_topspeed_best.grid(row=0, column=1, padx=(0,bar_gap), pady=(0,bar_gap))


        # Initialize with default values
        self.set_defaults()

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def set_defaults(self):
        """Initialize variables"""
        self.combo_name = "unknown"              # current car & track combo
        self.session_id = None                   # session identity

        self.curlap = 0                          # the current lap in which we are
        self.topspeed_cur= 0                     # fastest lap top speed
        self.topspeed_best= 0                    # fastest total top speed


    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            (speed, lapNum) = read_data.topspeed()
            if not self.verified:
                self.verified = True
                if(lapNum == 0):
                    self.set_defaults()  # reset data
                else:
                    self.topspeed_cur= 0
            # Read Topspeed data
            if(lapNum != self.curlap):
                self.curlap = lapNum
                #Reset lap topspeed if new lap
                self.topspeed_cur = 0

            if speed > self.topspeed_cur:
                self.topspeed_cur= speed
                #Update current lap top speed
                topspeed_cur_d = calc.conv_speed(self.topspeed_cur, self.wcfg["speed_unit"])
                self.bar_topspeed_cur.config(text=f"{topspeed_cur_d:.0f}")
            if speed > self.topspeed_best:
                self.topspeed_best= speed
                #Update top speed
                topspeed_best_d = calc.conv_speed(self.topspeed_best, self.wcfg["speed_unit"])
                self.bar_topspeed_best.config(text=f"{topspeed_best_d:.0f}")
        else:
            if self.verified:
                self.verified = False  # activate verification when enter track next time

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)


