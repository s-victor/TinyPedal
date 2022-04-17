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
Timing Widget
"""

import tkinter as tk
import tkinter.font as tkfont

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, delta_time, Widget, MouseEvent


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Timing Widget")
        self.attributes("-alpha", cfg.timing["opacity"])

        # Config size & position
        bar_gap = cfg.timing["bar_gap"]
        self.geometry(f"+{cfg.timing['position_x']}+{cfg.timing['position_y']}")

        # Config style & variable
        font_timing = tkfont.Font(family=cfg.timing["font_name"],
                                  size=-cfg.timing["font_size"],
                                  weight=cfg.timing["font_weight"])

        # Draw label
        bar_style = {"bd":0, "height":1, "width":12, "padx":0, "pady":0, "font":font_timing}
        self.bar_time_best = tk.Label(self, bar_style, text="B --:--.---",
                                      fg=cfg.timing["font_color_best"],
                                      bg=cfg.timing["bkg_color_best"])
        self.bar_time_last = tk.Label(self, bar_style, text="L --:--.---",
                                      fg=cfg.timing["font_color_last"],
                                      bg=cfg.timing["bkg_color_last"])
        self.bar_time_curr = tk.Label(self, bar_style, text="C --:--.---",
                                      fg=cfg.timing["font_color_current"],
                                      bg=cfg.timing["bkg_color_current"])
        self.bar_time_est = tk.Label(self, bar_style, text="E --:--.---",
                                     fg=cfg.timing["font_color_estimated"],
                                     bg=cfg.timing["bkg_color_estimated"])

        if cfg.timing["layout"] == "0":
            self.bar_time_best.grid(row=0, column=0, padx=0, pady=0)
            self.bar_time_last.grid(row=1, column=0, padx=0, pady=(bar_gap, 0))
            self.bar_time_curr.grid(row=2, column=0, padx=0, pady=(bar_gap, 0))
            self.bar_time_est.grid(row=3, column=0, padx=0, pady=(bar_gap, 0))
        elif cfg.timing["layout"] == "1":
            self.bar_time_best.grid(row=0, column=0, padx=0, pady=0)
            self.bar_time_last.grid(row=1, column=0, padx=0, pady=(bar_gap, 0))
            self.bar_time_curr.grid(row=0, column=1, padx=(bar_gap, 0), pady=0)
            self.bar_time_est.grid(row=1, column=1, padx=(bar_gap, 0), pady=(bar_gap, 0))
        else:
            self.bar_time_best.grid(row=0, column=0, padx=0, pady=0)
            self.bar_time_last.grid(row=0, column=1, padx=(bar_gap, 0), pady=0)
            self.bar_time_curr.grid(row=0, column=2, padx=(bar_gap, 0), pady=0)
            self.bar_time_est.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)

        self.update_timing()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.timing["position_x"] = str(self.winfo_x())
        cfg.timing["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_timing(self):
        """Update timing

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.timing["enable"]:
            # Read Timing data
            (laptime_curr, laptime_last, laptime_best, laptime_est, _
             ) = [calc.sec2laptime(min(data, 5999.999)) for data in delta_time.output()]

            # Timing update
            self.bar_time_best.config(text=f"B {laptime_best}")
            self.bar_time_last.config(text=f"L {laptime_last}")
            self.bar_time_curr.config(text=f"C {laptime_curr}")
            self.bar_time_est.config(text=f"E {laptime_est}")

        # Update rate
        self.after(cfg.timing["update_delay"], self.update_timing)
