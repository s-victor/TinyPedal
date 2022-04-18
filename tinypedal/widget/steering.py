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
Steering Widget
"""

import tkinter as tk

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "steering"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.configure(bg=self.cfg["bar_edge_color"])
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        self.sbar_length = int(100 * self.cfg["bar_length_scale"])  # 100 pixel base length
        self.sbar_height = int(15 * self.cfg["bar_height_scale"])  # 15 pixel
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        # Config style & variable
        self.last_rot_range = 0  # last recorded wheel rotation range

        # Draw widget
        self.bar_steering = tk.Canvas(self, bd=0, highlightthickness=0,
                                      height=self.sbar_height,
                                      width=self.sbar_length * 2,
                                      bg=self.cfg["bkg_color"])
        self.bar_steering.grid(row=0, column=0, padx=self.cfg["bar_edge_width"], pady=0)

        self.rect_steering_lt = self.bar_steering.create_rectangle(
                              0, 0, self.sbar_length, self.sbar_height,
                              fill=self.cfg["steering_color"], outline="")
        self.rect_steering_rt = self.bar_steering.create_rectangle(
                              self.sbar_length, 0, self.sbar_length * 2, self.sbar_height,
                              fill=self.cfg["steering_color"], outline="")

        if self.cfg["show_scale_mark"]:
            rect_style = {"fill":self.cfg["scale_mark_color"], "outline":""}
            self.rect_mark_lt1 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_lt2 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_lt3 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_lt4 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_lt5 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_rt1 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_rt2 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_rt3 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_rt4 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)
            self.rect_mark_rt5 = self.bar_steering.create_rectangle(0, 0, 0, 0, rect_style)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def create_mark(self, mark_label, mark_gap, mark_count, mark_offset):
        """Create scale mark"""
        pos = self.sbar_length + mark_gap * mark_count + mark_offset
        self.bar_steering.coords(mark_label, pos, 0, pos, self.sbar_height)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:
            # Read steering data
            raw_steering, steering_wheel_rot_range = read_data.steering()
            raw_steering = calc.steering_pos(raw_steering, self.sbar_length)

            # Steering update
            if raw_steering <= self.sbar_length:
                self.bar_steering.coords(self.rect_steering_lt, raw_steering,
                                         0, self.sbar_length, self.sbar_height)
                self.bar_steering.coords(self.rect_steering_rt, self.sbar_length,
                                         0, self.sbar_length + 1, self.sbar_height)
            else:
                self.bar_steering.coords(self.rect_steering_lt, self.sbar_length - 1,
                                         0, self.sbar_length, self.sbar_height)
                self.bar_steering.coords(self.rect_steering_rt, self.sbar_length,
                                         0, raw_steering, self.sbar_height)

            # Scale mark update
            if self.cfg["show_scale_mark"]:
                if steering_wheel_rot_range != self.last_rot_range:  # recalc if changed
                    self.last_rot_range = steering_wheel_rot_range

                    scale_mark_gap = calc.scale_mark_gap(
                                   90, steering_wheel_rot_range, self.sbar_length)

                    self.create_mark(self.rect_mark_lt1, -scale_mark_gap, 1, -1)
                    self.create_mark(self.rect_mark_lt2, -scale_mark_gap, 2, -1)
                    self.create_mark(self.rect_mark_lt3, -scale_mark_gap, 3, -1)
                    self.create_mark(self.rect_mark_lt4, -scale_mark_gap, 4, -1)
                    self.create_mark(self.rect_mark_lt5, -scale_mark_gap, 5, -1)
                    self.create_mark(self.rect_mark_rt1, scale_mark_gap, 1, 0)
                    self.create_mark(self.rect_mark_rt2, scale_mark_gap, 2, 0)
                    self.create_mark(self.rect_mark_rt3, scale_mark_gap, 3, 0)
                    self.create_mark(self.rect_mark_rt4, scale_mark_gap, 4, 0)
                    self.create_mark(self.rect_mark_rt5, scale_mark_gap, 5, 0)

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
