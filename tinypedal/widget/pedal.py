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
Pedal Widget
"""

import tkinter as tk

from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "pedal"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.pbar_uwidth = int(5 * self.wcfg["bar_width_scale"])  # 5 pixel
        self.pbar_cwidth = self.pbar_uwidth * 3  # 15 pixel combined
        self.pbar_extend = self.wcfg["full_pedal_height"] + 2  # full pedal indicator
        self.pbar_length = int(100 * self.wcfg["bar_length_scale"]) + self.pbar_extend  # 100 pixel
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Draw widget

        # Force feedback
        if self.wcfg["show_ffb_meter"]:
            self.bar_ffb = tk.Canvas(self, bd=0, highlightthickness=0,
                                     height=self.pbar_length, width=self.pbar_cwidth,
                                     bg=self.wcfg["bkg_color"])
            self.bar_ffb.grid(row=0, column=0, padx=(0, bar_gap), pady=0, sticky="we")

            self.rect_ffb = self.bar_ffb.create_rectangle(
                          0, 0, 0, 0, fill=self.wcfg["ffb_color"], outline="")

        # Clutch
        self.bar_clutch = tk.Canvas(self, bd=0, highlightthickness=0,
                                    height=self.pbar_length, width=self.pbar_cwidth,
                                    bg=self.wcfg["bkg_color"])
        self.bar_clutch.grid(row=0, column=1, columnspan=2,
                             padx=(0, bar_gap), pady=0, sticky="we")

        self.rect_raw_clutch = self.bar_clutch.create_rectangle(
                             0, 0, 0, 0, fill=self.wcfg["clutch_color"], outline="")
        self.rect_clutch = self.bar_clutch.create_rectangle(
                         0, 0, 0, 0, fill=self.wcfg["clutch_color"], outline="")

        self.max_clutch = self.bar_clutch.create_rectangle(
                        0, 0, self.pbar_cwidth, self.wcfg["full_pedal_height"],
                        fill=self.wcfg["bkg_color"], outline="")

        # Brake
        self.bar_brake = tk.Canvas(self, bd=0, highlightthickness=0,
                                   height=self.pbar_length, width=self.pbar_cwidth,
                                   bg=self.wcfg["bkg_color"])
        self.bar_brake.grid(row=0, column=3, columnspan=2,
                            padx=(0, bar_gap), pady=0, sticky="we")

        self.rect_raw_brake = self.bar_brake.create_rectangle(
                            0, 0, 0, 0, fill=self.wcfg["brake_color"], outline="")
        self.rect_brake = self.bar_brake.create_rectangle(
                        0, 0, 0, 0, fill=self.wcfg["brake_color"], outline="")

        self.max_brake = self.bar_brake.create_rectangle(
                       0, 0, self.pbar_cwidth, self.wcfg["full_pedal_height"],
                       fill=self.wcfg["bkg_color"], outline="")

        # Throttle
        self.bar_throttle = tk.Canvas(self, bd=0, highlightthickness=0,
                                      height=self.pbar_length, width=self.pbar_cwidth,
                                      bg=self.wcfg["bkg_color"])
        self.bar_throttle.grid(row=0, column=5, columnspan=2,
                               padx=0, pady=0, sticky="we")

        self.rect_raw_throttle = self.bar_throttle.create_rectangle(
                               0, 0, 0, 0, fill=self.wcfg["throttle_color"], outline="")
        self.rect_throttle = self.bar_throttle.create_rectangle(
                           0, 0, 0, 0, fill=self.wcfg["throttle_color"], outline="")

        self.max_throttle = self.bar_throttle.create_rectangle(
                          0, 0, self.pbar_cwidth, self.wcfg["full_pedal_height"],
                          fill=self.wcfg["bkg_color"], outline="")

        # Last data
        self.checked = False
        self.max_brake_pres = 0

        self.last_pedal_data = [None] * 7
        self.last_abs_brake = None

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read pedal data
            # Throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb
            pedal_data = tuple(map(self.scale_input, read_data.pedal()))

            # Throttle
            self.update_filtered_pos("throttle", pedal_data[0], self.last_pedal_data[0])

            # Brake
            if self.wcfg["show_average_brake_pressure"]:
                brake_pres = sum(read_data.brake_pressure()) / 4

                if brake_pres > self.max_brake_pres:
                    self.max_brake_pres = brake_pres

                abs_brake = self.scale_input(brake_pres / max(self.max_brake_pres, 0.001))
                self.update_filtered_pos("brake", abs_brake, self.last_abs_brake)
                self.last_abs_brake = None
            else:
                self.update_filtered_pos("brake", pedal_data[1], self.last_pedal_data[1])

            # Clutch
            self.update_filtered_pos("clutch", pedal_data[2], self.last_pedal_data[2])

            # Raw throttle
            self.update_raw_pos("throttle", pedal_data[3], self.last_pedal_data[3])
            self.update_max_pos("throttle", pedal_data[3], self.last_pedal_data[3])

            # Raw brake
            self.update_raw_pos("brake", pedal_data[4], self.last_pedal_data[4])
            self.update_max_pos("brake", pedal_data[4], self.last_pedal_data[4])

            # Raw clutch
            self.update_raw_pos("clutch", pedal_data[5], self.last_pedal_data[5])
            self.update_max_pos("clutch", pedal_data[5], self.last_pedal_data[5])

            # Force feedback
            if self.wcfg["show_ffb_meter"]:
                self.update_ffb_pos(pedal_data[6], self.last_pedal_data[6])

            self.last_pedal_data = pedal_data
        else:
            if self.checked:
                self.checked = False
                self.max_brake_pres = 0

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_filtered_pos(self, suffix, curr, last):
        """Filtered Pedal position"""
        if curr != last:
            getattr(self, f"bar_{suffix}").coords(
                getattr(self, f"rect_{suffix}"),
                self.pbar_uwidth, self.pbar_length, self.pbar_cwidth, curr)

    def update_raw_pos(self, suffix, curr, last):
        """Raw pedal position"""
        if curr != last:
            getattr(self, f"bar_{suffix}").coords(
                getattr(self, f"rect_raw_{suffix}"),
                0, self.pbar_length, self.pbar_uwidth, curr)

    def update_max_pos(self, suffix, curr, last):
        """Max pedal position indicator"""
        if curr != last:
            if last != self.pbar_extend and curr <= self.pbar_extend:  # only trigger on full
                getattr(self, f"bar_{suffix}").itemconfig(
                    getattr(self, f"max_{suffix}"), fill=self.wcfg[f"{suffix}_color"])
            elif last == self.pbar_extend and curr >= self.pbar_extend:
                getattr(self, f"bar_{suffix}").itemconfig(
                    getattr(self, f"max_{suffix}"), fill=self.wcfg["bkg_color"])

    def update_ffb_pos(self, curr, last):
        """FFB position"""
        if curr != last:
            if last != self.pbar_extend and curr <= self.pbar_extend:
                self.bar_ffb.itemconfig(self.rect_ffb, fill=self.wcfg["ffb_clipping_color"])
                curr = 0  # set to top position
            elif last == self.pbar_extend and curr >= self.pbar_extend:
                self.bar_ffb.itemconfig(self.rect_ffb, fill=self.wcfg["ffb_color"])
            self.bar_ffb.coords(self.rect_ffb,
                                0, self.pbar_length, self.pbar_cwidth, curr)

    # Additional methods
    def scale_input(self, value):
        """Convert input range to 100, and multiply scale"""
        return self.pbar_length - abs(int(value * 100)) * self.wcfg["bar_length_scale"]
