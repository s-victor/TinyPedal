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

from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "steering"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        self.sbar_length = int(100 * self.wcfg["bar_length_scale"])  # 100 pixel base length
        self.sbar_height = int(15 * self.wcfg["bar_height_scale"])  # 15 pixel

        # Config style & variable
        self.configure(bg=self.wcfg["bar_edge_color"])
        self.mark_num = int(1440 / max(self.wcfg["scale_mark_degree"], 10) / 2) - 1

        # Draw widget
        self.bar_steering = tk.Canvas(self, bd=0, highlightthickness=0,
                                      height=self.sbar_height,
                                      width=self.sbar_length * 2,
                                      bg=self.wcfg["bkg_color"])
        self.bar_steering.grid(row=0, column=0, padx=self.wcfg["bar_edge_width"], pady=0)

        self.rect_steering_lt = self.bar_steering.create_rectangle(
                              0, 0, self.sbar_length, self.sbar_height,
                              fill=self.wcfg["steering_color"], outline="")
        self.rect_steering_rt = self.bar_steering.create_rectangle(
                              self.sbar_length, 0, self.sbar_length * 2, self.sbar_height,
                              fill=self.wcfg["steering_color"], outline="")
        # Recenter position
        self.bar_steering.coords(self.rect_steering_lt, self.sbar_length - 1,
                                 0, self.sbar_length, self.sbar_height)
        self.bar_steering.coords(self.rect_steering_rt, self.sbar_length,
                                 0, self.sbar_length + 1, self.sbar_height)

        if self.wcfg["show_scale_mark"]:
            tuple(map(self.create_mark, list(range(1, self.mark_num + 1)) * 2))

        # Last data
        self.last_sw_rot_range = 0
        self.last_raw_steering = 0

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read steering data
            raw_steering, sw_rot_range = read_data.steering()

            # Steering
            raw_steering = self.steering_pos(raw_steering, self.sbar_length)
            self.update_steering(raw_steering, self.last_raw_steering)
            self.last_raw_steering = raw_steering

            # Scale mark
            if self.wcfg["show_scale_mark"]:
                if sw_rot_range != self.last_sw_rot_range:  # recalc if changed
                    self.last_sw_rot_range = sw_rot_range
                    mark_gap = self.scale_mark_gap(max(self.wcfg["scale_mark_degree"], 10),
                                                   sw_rot_range, self.sbar_length)
                    tuple(map(self.move_mark,
                              [-mark_gap]*self.mark_num + [mark_gap]*self.mark_num,
                              list(range(1, self.mark_num + 1)) * 2))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_steering(self, curr, last):
        """Steering"""
        if curr != last:
            if curr <= self.sbar_length:
                self.bar_steering.coords(self.rect_steering_lt, curr,
                                         0, self.sbar_length, self.sbar_height)
                if last >= self.sbar_length:
                    self.bar_steering.coords(self.rect_steering_rt, self.sbar_length,
                                             0, self.sbar_length + 1, self.sbar_height)
            else:
                if last <= self.sbar_length:
                    self.bar_steering.coords(self.rect_steering_lt, self.sbar_length - 1,
                                             0, self.sbar_length, self.sbar_height)
                self.bar_steering.coords(self.rect_steering_rt, self.sbar_length,
                                         0, curr, self.sbar_height)

    def create_mark(self, index):
        """Create left & right side scale mark"""
        setattr(self, f"rect_mark_lt{index}", self.bar_steering.create_rectangle(
            0, 0, 0, 0, fill=self.wcfg["scale_mark_color"], outline=""))
        setattr(self, f"rect_mark_rt{index}", self.bar_steering.create_rectangle(
            0, 0, 0, 0, fill=self.wcfg["scale_mark_color"], outline=""))

    def move_mark(self, mark_gap, index):
        """Move scale mark"""
        if mark_gap < 0:
            offset = -1
            suffix = "lt"
        else:
            offset = 0
            suffix = "rt"
        pos = mark_gap * index + self.sbar_length + offset
        self.bar_steering.coords(
            getattr(self, f"rect_mark_{suffix}{index}"),
            pos, 0, pos, self.sbar_height)

    # Additional methods
    @staticmethod
    def steering_pos(steering, length):
        """Multiply scale, add offset"""
        return length * (1 + steering)

    @staticmethod
    def scale_mark_gap(degree, rot_range, scale):
        """mark gap(degree) divide half of full steering range (degree) and multiply scale"""
        if rot_range != 0:
            return degree / (rot_range / 2) * scale
        return 0
