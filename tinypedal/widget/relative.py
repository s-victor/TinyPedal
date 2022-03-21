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
Relative Widget
"""

import tkinter as tk
import tkinter.font as tkfont

import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent
from tinypedal.setting import VehicleClass


class Relative(Widget, MouseEvent):
    """Draw relative widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Relative Widget")
        self.attributes("-alpha", cfg.relative["opacity"])

        # Config size & position
        num_width = 3
        drv_width = cfg.relative["bar_driver_name_width"]
        gap_width = 4
        bar_padx = cfg.relative["font_size"] * 0.3
        bar_gap = cfg.relative["bar_gap"]
        self.geometry(f"+{cfg.relative['position_x']}+{cfg.relative['position_y']}")

        # Config style & variable
        text_def = ""
        fg_color = "#FFF"
        fg_color_plr = cfg.relative["font_color_player"]
        bg_color_place = cfg.relative["bkg_color_place"]
        bg_color_place_plr = cfg.relative["bkg_color_player_place"]
        bg_color_name = cfg.relative["bkg_color_name"]
        bg_color_name_plr = cfg.relative["bkg_color_player_name"]
        bg_color_gap = cfg.relative["bkg_color_gap"]
        bg_color_gap_plr = cfg.relative["bkg_color_player_gap"]
        font_relative = tkfont.Font(family=cfg.relative["font_name"],
                                    size=-cfg.relative["font_size"],
                                    weight=cfg.relative["font_weight"])

        # Draw label
        # Driver place number
        bar_style_p = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                     "height":1, "width":num_width, "fg":fg_color, "bg":bg_color_place}
        self.bar_row_1p = tk.Label(self, bar_style_p)
        self.bar_row_2p = tk.Label(self, bar_style_p)
        self.bar_row_3p = tk.Label(self, bar_style_p)
        self.bar_row_4p = tk.Label(self, text=text_def, bd=0, padx=0, pady=0,
                                   font=font_relative, height=1, width=num_width,
                                   fg=fg_color_plr, bg=bg_color_place_plr)
        self.bar_row_5p = tk.Label(self, bar_style_p)
        self.bar_row_6p = tk.Label(self, bar_style_p)
        self.bar_row_7p = tk.Label(self, bar_style_p)
        self.bar_row_1p.grid(row=0, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_2p.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_3p.grid(row=2, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_4p.grid(row=3, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_5p.grid(row=4, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_6p.grid(row=5, column=1, padx=0, pady=(0, bar_gap))
        self.bar_row_7p.grid(row=6, column=1, padx=0, pady=0)

        # Driver name
        bar_style_n = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":drv_width,
                       "fg":fg_color, "bg":bg_color_name, "anchor":"w"}
        self.bar_row_1n = tk.Label(self, bar_style_n)
        self.bar_row_2n = tk.Label(self, bar_style_n)
        self.bar_row_3n = tk.Label(self, bar_style_n)
        self.bar_row_4n = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                   font=font_relative, height=1, width=drv_width,
                                   fg=fg_color_plr, bg=bg_color_name_plr, anchor="w")
        self.bar_row_5n = tk.Label(self, bar_style_n)
        self.bar_row_6n = tk.Label(self, bar_style_n)
        self.bar_row_7n = tk.Label(self, bar_style_n)
        self.bar_row_1n.grid(row=0, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_2n.grid(row=1, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_3n.grid(row=2, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_4n.grid(row=3, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_5n.grid(row=4, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_6n.grid(row=5, column=3, padx=0, pady=(0, bar_gap))
        self.bar_row_7n.grid(row=6, column=3, padx=0, pady=0)

        # Time gap
        bar_style_d = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":gap_width,
                       "fg":fg_color, "bg":bg_color_gap, "anchor":"e"}
        self.bar_row_1d = tk.Label(self, bar_style_d)
        self.bar_row_2d = tk.Label(self, bar_style_d)
        self.bar_row_3d = tk.Label(self, bar_style_d)
        self.bar_row_4d = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                   font=font_relative, height=1, width=gap_width,
                                   fg=fg_color_plr, bg=bg_color_gap_plr, anchor="e")
        self.bar_row_5d = tk.Label(self, bar_style_d)
        self.bar_row_6d = tk.Label(self, bar_style_d)
        self.bar_row_7d = tk.Label(self, bar_style_d)
        self.bar_row_1d.grid(row=0, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_2d.grid(row=1, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_3d.grid(row=2, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_4d.grid(row=3, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_5d.grid(row=4, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_6d.grid(row=5, column=6, padx=0, pady=(0, bar_gap))
        self.bar_row_7d.grid(row=6, column=6, padx=0, pady=0)

        # Vehicle laptime
        if cfg.relative["show_laptime"]:
            fg_color_lpt = cfg.relative["font_color_laptime"]
            bg_color_lpt = cfg.relative["bkg_color_laptime"]
            bar_style_t = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1, "width":9,
                           "fg":fg_color_lpt, "bg":bg_color_lpt}
            self.bar_row_1t = tk.Label(self, bar_style_t)
            self.bar_row_2t = tk.Label(self, bar_style_t)
            self.bar_row_3t = tk.Label(self, bar_style_t)
            self.bar_row_4t = tk.Label(self, bar_style_t)
            self.bar_row_5t = tk.Label(self, bar_style_t)
            self.bar_row_6t = tk.Label(self, bar_style_t)
            self.bar_row_7t = tk.Label(self, bar_style_t)
            self.bar_row_1t.grid(row=0, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_2t.grid(row=1, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_3t.grid(row=2, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_4t.grid(row=3, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_5t.grid(row=4, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_6t.grid(row=5, column=4, padx=0, pady=(0, bar_gap))
            self.bar_row_7t.grid(row=6, column=4, padx=0, pady=0)

        # Vehicle class
        if cfg.relative["show_class"]:
            self.vehcls = VehicleClass()  # load VehicleClass config
            fg_color_cls = cfg.relative["font_color_class"]
            bg_color_cls = cfg.relative["bkg_color_class"]
            bar_style_c = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1,
                           "width":cfg.relative["bar_class_name_width"],
                           "fg":fg_color_cls, "bg":bg_color_cls}
            self.bar_row_1c = tk.Label(self, bar_style_c)
            self.bar_row_2c = tk.Label(self, bar_style_c)
            self.bar_row_3c = tk.Label(self, bar_style_c)
            self.bar_row_4c = tk.Label(self, bar_style_c)
            self.bar_row_5c = tk.Label(self, bar_style_c)
            self.bar_row_6c = tk.Label(self, bar_style_c)
            self.bar_row_7c = tk.Label(self, bar_style_c)
            self.bar_row_1c.grid(row=0, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_2c.grid(row=1, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_3c.grid(row=2, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_4c.grid(row=3, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_5c.grid(row=4, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_6c.grid(row=5, column=5, padx=0, pady=(0, bar_gap))
            self.bar_row_7c.grid(row=6, column=5, padx=0, pady=0)

        self.update_relative()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.load()
        cfg.relative["position_x"] = str(self.winfo_x())
        cfg.relative["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_relative(self):
        """Update relative

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.relative["enable"]:
            # Read relative data
            rel_list = read_data.relative_list()
            plr = rel_list[3]

            v1_plc, v1_drv, v1_lpt, v1_cls, v1_gap, v1_lap = read_data.relative_data(rel_list[0], plr)
            v2_plc, v2_drv, v2_lpt, v2_cls, v2_gap, v2_lap = read_data.relative_data(rel_list[1], plr)
            v3_plc, v3_drv, v3_lpt, v3_cls, v3_gap, v3_lap = read_data.relative_data(rel_list[2], plr)
            v4_plc, v4_drv, v4_lpt, v4_cls, v4_gap, v4_lap = read_data.relative_data(plr, plr)
            v5_plc, v5_drv, v5_lpt, v5_cls, v5_gap, v5_lap = read_data.relative_data(rel_list[4], plr)
            v6_plc, v6_drv, v6_lpt, v6_cls, v6_gap, v6_lap = read_data.relative_data(rel_list[5], plr)
            v7_plc, v7_drv, v7_lpt, v7_cls, v7_gap, v7_lap = read_data.relative_data(rel_list[6], plr)

            # Relative update
            self.bar_row_1p.config(text=v1_plc, fg=self.color_lapdiff(v1_lap, v4_lap))
            self.bar_row_2p.config(text=v2_plc, fg=self.color_lapdiff(v2_lap, v4_lap))
            self.bar_row_3p.config(text=v3_plc, fg=self.color_lapdiff(v3_lap, v4_lap))
            self.bar_row_4p.config(text=v4_plc)
            self.bar_row_5p.config(text=v5_plc, fg=self.color_lapdiff(v5_lap, v4_lap))
            self.bar_row_6p.config(text=v6_plc, fg=self.color_lapdiff(v6_lap, v4_lap))
            self.bar_row_7p.config(text=v7_plc, fg=self.color_lapdiff(v7_lap, v4_lap))

            self.bar_row_1n.config(text=v1_drv, fg=self.color_lapdiff(v1_lap, v4_lap))
            self.bar_row_2n.config(text=v2_drv, fg=self.color_lapdiff(v2_lap, v4_lap))
            self.bar_row_3n.config(text=v3_drv, fg=self.color_lapdiff(v3_lap, v4_lap))
            self.bar_row_4n.config(text=v4_drv)
            self.bar_row_5n.config(text=v5_drv, fg=self.color_lapdiff(v5_lap, v4_lap))
            self.bar_row_6n.config(text=v6_drv, fg=self.color_lapdiff(v6_lap, v4_lap))
            self.bar_row_7n.config(text=v7_drv, fg=self.color_lapdiff(v7_lap, v4_lap))

            self.bar_row_1d.config(text=v1_gap, fg=self.color_lapdiff(v1_lap, v4_lap))
            self.bar_row_2d.config(text=v2_gap, fg=self.color_lapdiff(v2_lap, v4_lap))
            self.bar_row_3d.config(text=v3_gap, fg=self.color_lapdiff(v3_lap, v4_lap))
            self.bar_row_4d.config(text=v4_gap)
            self.bar_row_5d.config(text=v5_gap, fg=self.color_lapdiff(v5_lap, v4_lap))
            self.bar_row_6d.config(text=v6_gap, fg=self.color_lapdiff(v6_lap, v4_lap))
            self.bar_row_7d.config(text=v7_gap, fg=self.color_lapdiff(v7_lap, v4_lap))

            if cfg.relative["show_laptime"]:
                self.bar_row_1t.config(self.set_class(v1_lpt))
                self.bar_row_2t.config(self.set_class(v2_lpt))
                self.bar_row_3t.config(self.set_class(v3_lpt))
                self.bar_row_4t.config(self.set_class(v4_lpt))
                self.bar_row_5t.config(self.set_class(v5_lpt))
                self.bar_row_6t.config(self.set_class(v6_lpt))
                self.bar_row_7t.config(self.set_class(v7_lpt))

            if cfg.relative["show_class"]:
                self.bar_row_1c.config(self.set_class(v1_cls))
                self.bar_row_2c.config(self.set_class(v2_cls))
                self.bar_row_3c.config(self.set_class(v3_cls))
                self.bar_row_4c.config(self.set_class(v4_cls))
                self.bar_row_5c.config(self.set_class(v5_cls))
                self.bar_row_6c.config(self.set_class(v6_cls))
                self.bar_row_7c.config(self.set_class(v7_cls))

        # Update rate
        self.after(cfg.relative["update_delay"], self.update_relative)

    # Additional methods
    @staticmethod
    def color_lapdiff(nlap, player_nlap):
        """Compare lap differences & set color"""
        if nlap > player_nlap:
            color = cfg.relative["font_color_laps_ahead"]
        elif nlap < player_nlap:
            color = cfg.relative["font_color_laps_behind"]
        else:
            color = cfg.relative["font_color_same_lap"]
        return color

    def set_class(self, vehclass):
        """Compare vehicle class name with user defined dictionary"""
        short_name = vehclass
        class_config = {"text":short_name}
        for key, value in self.vehcls.classdict.items():
            # If class name matches user defined class
            if vehclass == key:
                # Assign new class name from user defined value
                short_name = value
                for subkey, subvalue in short_name.items():
                    # Assign corresponding background color
                    class_config = {"text":subkey, "bg":subvalue}
                    break
        return class_config
