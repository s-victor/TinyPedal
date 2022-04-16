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

import tinypedal.readapi as read_data
from tinypedal.base import cfg, delta_time, Widget, MouseEvent


class Deltabest(Widget, MouseEvent):
    """Draw deltabest widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Deltabest Widget")
        self.attributes("-alpha", cfg.deltabest["opacity"])

        # Config size & position
        self.dbar_length = int(100 * cfg.deltabest["bar_length_scale"])  # 100 pixel base length
        self.dbar_height = int(15 * cfg.deltabest["bar_height_scale"])  # 15 pixel
        bar_gap = cfg.deltabest["bar_gap"]
        self.geometry(f"+{cfg.deltabest['position_x']}+{cfg.deltabest['position_y']}")

        # Config style & variable
        font_deltabest = tkfont.Font(family=cfg.deltabest["font_name"],
                                     size=-cfg.deltabest["font_size"],
                                     weight=cfg.deltabest["font_weight"])

        # Delta bar
        if cfg.deltabest["show_delta_bar"]:
            self.bar_deltabar = tk.Canvas(self, bd=0, highlightthickness=0,
                                          height=self.dbar_height,
                                          width=self.dbar_length * 2,
                                          bg=cfg.deltabest["bkg_color_deltabest"])
            self.bar_deltabar.grid(row=1, column=0, padx=0, pady=bar_gap)
            self.rect_pos_lt = self.bar_deltabar.create_rectangle(
                               0, 0, self.dbar_length, self.dbar_height,
                               fill=cfg.deltabest["bkg_color_time_loss"], outline="")
            self.rect_pos_rt = self.bar_deltabar.create_rectangle(
                               self.dbar_length, 0, self.dbar_length * 2, self.dbar_height,
                               fill=cfg.deltabest["bkg_color_time_gain"], outline="")

        # Delta label
        bar_style = {"bd":0, "height":1, "width":8, "padx":0, "pady":0, "font":font_deltabest}
        self.bar_deltabest = tk.Label(self, bar_style, text="---.---",
                                      fg=cfg.deltabest["font_color_deltabest"],
                                      bg=cfg.deltabest["bkg_color_deltabest"])

        if cfg.deltabest["layout"] == "0":
            self.bar_deltabest.grid(row=2, column=0, padx=0, pady=0)
        else:
            self.bar_deltabest.grid(row=0, column=0, padx=0, pady=0)

        self.update_deltabest()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.deltabest["position_x"] = str(self.winfo_x())
        cfg.deltabest["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_deltabest(self):
        """Update deltabest

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.deltabest["enable"]:
            # Read delta best data
            delta_best = delta_time.output()[4]

            # Deltabest update
            if cfg.deltabest["color_swap"] == "0":
                self.bar_deltabest["fg"] = self.color_delta(delta_best)
            else:
                self.bar_deltabest["bg"] = self.color_delta(delta_best)
            self.bar_deltabest.config(text=f"{min(max(delta_best, -99.999), 99.999):+.03f}")

            # Delta bar update
            if cfg.deltabest["show_delta_bar"]:
                deltabar = self.deltabar_pos(cfg.deltabest["bar_display_range"],
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
        self.after(cfg.deltabest["update_delay"], self.update_deltabest)

    @staticmethod
    def deltabar_pos(rng, delta, length):
        """Delta position"""
        return (rng - min(max(delta, -rng), rng)) * length / rng

    @staticmethod
    def color_delta(delta):
        """Delta time color"""
        if delta <= 0:
            color = cfg.deltabest["bkg_color_time_gain"]
        else:
            color = cfg.deltabest["bkg_color_time_loss"]
        return color
