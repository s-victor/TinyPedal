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
Engine Widget
"""

import tkinter as tk
import tkinter.font as tkfont

import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Engine Widget")
        self.attributes("-alpha", cfg.engine["opacity"])

        # Config size & position
        bar_gap = cfg.engine["bar_gap"]
        self.geometry(f"+{cfg.engine['position_x']}+{cfg.engine['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color = cfg.engine["font_color"]
        bg_color = cfg.engine["bkg_color"]
        font_engine = tkfont.Font(family=cfg.engine["font_name"],
                                  size=-cfg.engine["font_size"],
                                  weight=cfg.engine["font_weight"])

        # Draw label
        bar_style  = {"text":text_def, "bd":0, "height":1, "width":9, "padx":0, "pady":0,
                      "font":font_engine, "fg":fg_color, "bg":bg_color}
        self.bar_oil = tk.Label(self, bar_style)
        self.bar_water = tk.Label(self, bar_style)
        self.bar_oil.grid(row=0, column=0, padx=0, pady=0)
        self.bar_water.grid(row=1, column=0, padx=0, pady=(bar_gap, 0))

        if cfg.engine["show_turbo"]:
            self.bar_turbo = tk.Label(self, bar_style)
            self.bar_turbo.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))

        if cfg.engine["show_rpm"]:
            self.bar_rpm = tk.Label(self, bar_style)
            self.bar_rpm.grid(row=3, column=0, padx=0, pady=(bar_gap, 0))

        self.update_engine()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.engine["position_x"] = str(self.winfo_x())
        cfg.engine["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_engine(self):
        """Update engine

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.engine["enable"]:
            # Read Engine data
            temp_oil, temp_water, e_turbo, e_rpm = read_data.engine()

            # Engine update
            self.bar_oil.config(text=f"O {temp_oil:05.01f}°",
                                bg=self.color_overheat(
                                    temp_oil, cfg.engine["overheat_threshold_oil"]))
            self.bar_water.config(text=f"W {temp_water:05.01f}°",
                                bg=self.color_overheat(
                                    temp_water, cfg.engine["overheat_threshold_water"]))

            if cfg.engine["show_turbo"]:
                self.bar_turbo.config(text=f"{e_turbo*0.00001:04.03f}bar")

            if cfg.engine["show_rpm"]:
                self.bar_rpm.config(text=f"{e_rpm: =05.0f}rpm")

        # Update rate
        self.after(cfg.engine["update_delay"], self.update_engine)

    # Additional methods
    @staticmethod
    def color_overheat(temperature, threshold):
        """Overheat warning color"""
        if temperature < threshold:
            color = cfg.engine["bkg_color"]
        else:
            color = cfg.engine["bkg_color_overheat"]
        return color
