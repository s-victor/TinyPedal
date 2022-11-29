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
Deltabest Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..load_func import module


class Draw(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "deltabest"

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self)
        self.cfg = config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        self.dbar_length = int(100 * self.wcfg["bar_length_scale"])  # 100 pixel base length
        self.dbar_height = int(15 * self.wcfg["bar_height_scale"])  # 15 pixel
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_deltabest = tkfont.Font(family=self.wcfg["font_name"],
                                     size=-self.wcfg["font_size"],
                                     weight=self.wcfg["font_weight"])

        # Delta bar
        if self.wcfg["show_delta_bar"]:
            self.bar_deltabar = tk.Canvas(self, bd=0, highlightthickness=0,
                                          height=self.dbar_height,
                                          width=self.dbar_length * 2,
                                          bg=self.wcfg["bkg_color_deltabest"])
            self.bar_deltabar.grid(row=1, column=0, padx=0, pady=bar_gap)
            self.rect_pos_lt = self.bar_deltabar.create_rectangle(
                               0, 0, self.dbar_length, self.dbar_height,
                               fill=self.wcfg["bkg_color_time_loss"], outline="")
            self.rect_pos_rt = self.bar_deltabar.create_rectangle(
                               self.dbar_length, 0, self.dbar_length * 2, self.dbar_height,
                               fill=self.wcfg["bkg_color_time_gain"], outline="")

        # Delta label
        bar_style = {"bd":0, "height":1, "width":8, "padx":0, "pady":0, "font":font_deltabest}
        self.bar_deltabest = tk.Label(self, bar_style, text="---.---",
                                      fg=self.wcfg["font_color_deltabest"],
                                      bg=self.wcfg["bkg_color_deltabest"])

        if self.wcfg["layout"] == "0":
            self.bar_deltabest.grid(row=2, column=0, padx=0, pady=0)
        else:
            self.bar_deltabest.grid(row=0, column=0, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read delta best data
            delta_best = module.delta_time.output_data[4]

            # Start updating
            # Deltabest update
            if self.wcfg["color_swap"] == "0":
                self.bar_deltabest["fg"] = self.color_delta(delta_best)
            else:
                self.bar_deltabest["bg"] = self.color_delta(delta_best)
            self.bar_deltabest.config(text=f"{min(max(delta_best, -99.999), 99.999):+.03f}")

            # Delta bar update
            if self.wcfg["show_delta_bar"]:
                deltabar = self.deltabar_pos(self.wcfg["bar_display_range"],
                                             delta_best, self.dbar_length)
                if deltabar < self.dbar_length:  # loss
                    self.bar_deltabar.coords(self.rect_pos_lt,
                                             deltabar, 0, self.dbar_length, self.dbar_height)
                    self.bar_deltabar.coords(self.rect_pos_rt, 0, 0, 0, 0)
                else:  # gain
                    self.bar_deltabar.coords(self.rect_pos_lt, 0, 0, 0, 0)
                    self.bar_deltabar.coords(self.rect_pos_rt,
                                             self.dbar_length, 0, deltabar, self.dbar_height)

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    @staticmethod
    def deltabar_pos(rng, delta, length):
        """Delta position"""
        return (rng - min(max(delta, -rng), rng)) * length / rng

    def color_delta(self, delta):
        """Delta time color"""
        if delta <= 0:
            color = self.wcfg["bkg_color_time_gain"]
        else:
            color = self.wcfg["bkg_color_time_loss"]
        return color
