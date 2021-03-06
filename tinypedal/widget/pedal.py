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

from tinypedal.__init__ import cfg
import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "pedal"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        self.pbar_uwidth = int(5 * self.cfg["bar_width_scale"])  # 5 pixel
        self.pbar_cwidth = self.pbar_uwidth * 3  # 15 pixel combined
        self.pbar_extend = self.cfg["full_pedal_height"] + 2  # full pedal indicator
        self.pbar_length = int(100 * self.cfg["bar_length_scale"]) + self.pbar_extend  # 100 pixel
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        # Draw widget
        if self.cfg["show_ffb_meter"]:
            # Force feedback
            self.bar_ffb = tk.Canvas(self, bd=0, highlightthickness=0,
                                     height=self.pbar_length, width=self.pbar_cwidth,
                                     bg=self.cfg["bkg_color"])
            self.bar_ffb.grid(row=0, column=0, padx=(0, self.cfg["bar_gap"]), pady=0, sticky="we")

            self.rect_ffb = self.bar_ffb.create_rectangle(
                          0, 0, 0, 0, fill=self.cfg["ffb_color"], outline="")

        # Clutch
        self.bar_clutch = tk.Canvas(self, bd=0, highlightthickness=0,
                                    height=self.pbar_length, width=self.pbar_cwidth,
                                    bg=self.cfg["bkg_color"])
        self.bar_clutch.grid(row=0, column=1, columnspan=2,
                             padx=(0, self.cfg["bar_gap"]), pady=0, sticky="we")

        self.rect_raw_clutch = self.bar_clutch.create_rectangle(
                             0, 0, 0, 0, fill=self.cfg["clutch_color"], outline="")
        self.rect_clutch = self.bar_clutch.create_rectangle(
                         0, 0, 0, 0, fill=self.cfg["clutch_color"], outline="")

        self.max_clutch = self.bar_clutch.create_rectangle(
                        0, 0, self.pbar_cwidth, self.cfg["full_pedal_height"],
                        fill=self.cfg["clutch_color"], outline="")

        # Brake
        self.bar_brake = tk.Canvas(self, bd=0, highlightthickness=0,
                                   height=self.pbar_length, width=self.pbar_cwidth,
                                   bg=self.cfg["bkg_color"])
        self.bar_brake.grid(row=0, column=3, columnspan=2,
                            padx=(0, self.cfg["bar_gap"]), pady=0, sticky="we")

        self.rect_raw_brake = self.bar_brake.create_rectangle(
                            0, 0, 0, 0, fill=self.cfg["brake_color"], outline="")
        self.rect_brake = self.bar_brake.create_rectangle(
                        0, 0, 0, 0, fill=self.cfg["brake_color"], outline="")

        self.max_brake = self.bar_brake.create_rectangle(
                       0, 0, self.pbar_cwidth, self.cfg["full_pedal_height"],
                       fill=self.cfg["brake_color"], outline="")

        # Throttle
        self.bar_throttle = tk.Canvas(self, bd=0, highlightthickness=0,
                                      height=self.pbar_length, width=self.pbar_cwidth,
                                      bg=self.cfg["bkg_color"])
        self.bar_throttle.grid(row=0, column=5, columnspan=2, padx=0, pady=0, sticky="we")

        self.rect_raw_throttle = self.bar_throttle.create_rectangle(
                               0, 0, 0, 0, fill=self.cfg["throttle_color"], outline="")
        self.rect_throttle = self.bar_throttle.create_rectangle(
                           0, 0, 0, 0, fill=self.cfg["throttle_color"], outline="")

        self.max_throttle = self.bar_throttle.create_rectangle(
                          0, 0, self.pbar_cwidth, self.cfg["full_pedal_height"],
                          fill=self.cfg["throttle_color"], outline="")

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read pedal data
            (throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb
             ) = [calc.pedal_pos(data, self.pbar_length, self.cfg["bar_length_scale"])
                  for data in read_data.pedal()]

            # Check isPlayer before update
            if read_data.is_local_player():

                self.bar_throttle.coords(self.rect_raw_throttle, 0,
                                         self.pbar_length, self.pbar_uwidth,
                                         raw_throttle)
                self.bar_throttle.coords(self.rect_throttle, self.pbar_uwidth,
                                         self.pbar_length, self.pbar_cwidth,
                                         throttle)
                self.bar_brake.coords(self.rect_raw_brake, 0,
                                      self.pbar_length, self.pbar_uwidth,
                                      raw_brake)
                self.bar_brake.coords(self.rect_brake, self.pbar_uwidth,
                                      self.pbar_length, self.pbar_cwidth,
                                      brake)
                self.bar_clutch.coords(self.rect_raw_clutch, 0,
                                       self.pbar_length, self.pbar_uwidth,
                                       raw_clutch)
                self.bar_clutch.coords(self.rect_clutch, self.pbar_uwidth,
                                       self.pbar_length, self.pbar_cwidth,
                                       clutch)

                # Pedal update
                if raw_throttle <= self.pbar_extend:
                    self.bar_throttle.itemconfig(
                        self.max_throttle, fill=self.cfg["throttle_color"])
                else:
                    self.bar_throttle.itemconfig(
                        self.max_throttle, fill=self.cfg["bkg_color"])

                if raw_brake <= self.pbar_extend:
                    self.bar_brake.itemconfig(
                        self.max_brake, fill=self.cfg["brake_color"])
                else:
                    self.bar_brake.itemconfig(
                        self.max_brake, fill=self.cfg["bkg_color"])

                if raw_clutch <= self.pbar_extend:
                    self.bar_clutch.itemconfig(
                        self.max_clutch, fill=self.cfg["clutch_color"])
                else:
                    self.bar_clutch.itemconfig(
                        self.max_clutch, fill=self.cfg["bkg_color"])

                # Force feedback update
                if self.cfg["show_ffb_meter"]:
                    if ffb <= self.pbar_extend:
                        self.bar_ffb.coords(
                            self.rect_ffb, 0, self.pbar_length, self.pbar_cwidth, 0)
                        self.bar_ffb.itemconfig(
                            self.rect_ffb, fill=self.cfg["ffb_clipping_color"])
                    else:
                        self.bar_ffb.coords(
                            self.rect_ffb, 0, self.pbar_length, self.pbar_cwidth, ffb)
                        self.bar_ffb.itemconfig(
                            self.rect_ffb, fill=self.cfg["ffb_color"])

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)
