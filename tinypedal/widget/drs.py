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

from tinypedal.base import cfg, read_data, Widget, MouseEvent


class DRS(Widget, MouseEvent):
    """Draw DRS widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - DRS Widget")
        self.attributes("-alpha", cfg.drs["opacity"])

        # Config size & position
        self.geometry(f"+{cfg.drs['position_x']}+{cfg.drs['position_y']}")

        # Config style & variable
        font_drs = tkfont.Font(family=cfg.drs["font_name"],
                               size=-cfg.drs["font_size"],
                               weight=cfg.drs["font_weight"])

        # Draw label
        self.bar_drs = tk.Label(self, text="DRS", bd=0, height=1, width=4,
                                padx=0, pady=0, font=font_drs,
                                fg=cfg.drs["font_color_not_available"],
                                bg=cfg.drs["bkg_color_not_available"])
        self.bar_drs.grid(row=0, column=0, padx=0, pady=0)

        self.update_drs()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.load()
        cfg.drs["position_x"] = str(self.winfo_x())
        cfg.drs["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_drs(self):
        """Update DRS

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.drs["enable"]:
            # Read DRS data
            drs_on, drs_status = read_data.drs()

            # DRS update
            if drs_status == 1:  # blue
                self.bar_drs.config(fg=cfg.drs["font_color_available"],
                                    bg=cfg.drs["bkg_color_available"])
            elif drs_status == 2:
                if drs_on:  # green
                    self.bar_drs.config(fg=cfg.drs["font_color_activated"],
                                        bg=cfg.drs["bkg_color_activated"])
                else:  # orange
                    self.bar_drs.config(fg=cfg.drs["font_color_allowed"],
                                        bg=cfg.drs["bkg_color_allowed"])
            else:  # grey
                self.bar_drs.config(fg=cfg.drs["font_color_not_available"],
                                    bg=cfg.drs["bkg_color_not_available"])

        # Update rate
        self.after(cfg.drs["update_delay"], self.update_drs)
