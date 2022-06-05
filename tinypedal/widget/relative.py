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

from tinypedal.__init__ import info, cfg
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent
from tinypedal.setting import VehicleClass


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "relative"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        bar_padx = self.cfg["font_size"] * 0.3
        bar_gap = self.cfg["bar_gap"]
        num_width = 3
        gap_width = 4
        self.drv_width = self.cfg["bar_driver_name_width"]
        self.cls_width = self.cfg["bar_class_name_width"]

        # Config style & variable
        text_def = ""
        fg_color = "#FFF"  # placeholder, font color for place, name, gap changes dynamically
        fg_color_plr = self.cfg["font_color_player"]
        bg_color_place = self.cfg["bkg_color_place"]
        bg_color_place_plr = self.cfg["bkg_color_player_place"]
        bg_color_name = self.cfg["bkg_color_name"]
        bg_color_name_plr = self.cfg["bkg_color_player_name"]
        bg_color_gap = self.cfg["bkg_color_gap"]
        bg_color_gap_plr = self.cfg["bkg_color_player_gap"]
        fg_color_classplace = self.cfg["font_color_position_in_class"]
        bg_color_classplace = self.cfg["bkg_color_position_in_class"]
        fg_color_pit = self.cfg["font_color_pit"]
        bg_color_pit = self.cfg["bkg_color_pit"]

        column_plc = self.cfg["column_index_place"]
        column_drv = self.cfg["column_index_driver"]
        column_lpt = self.cfg["column_index_laptime"]
        column_pic = self.cfg["column_index_position_in_class"]
        column_cls = self.cfg["column_index_class"]
        column_gap = self.cfg["column_index_gap"]
        column_pit = self.cfg["column_index_pit"]

        font_relative = tkfont.Font(family=self.cfg["font_name"],
                                    size=-self.cfg["font_size"],
                                    weight=self.cfg["font_weight"])

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
        self.bar_row_1p.grid(row=0, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_2p.grid(row=1, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_3p.grid(row=2, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_4p.grid(row=3, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_5p.grid(row=4, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_6p.grid(row=5, column=column_plc, padx=0, pady=(0, bar_gap))
        self.bar_row_7p.grid(row=6, column=column_plc, padx=0, pady=0)

        # Driver name
        bar_style_n = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":self.drv_width,
                       "fg":fg_color, "bg":bg_color_name, "anchor":"w"}
        self.bar_row_1n = tk.Label(self, bar_style_n)
        self.bar_row_2n = tk.Label(self, bar_style_n)
        self.bar_row_3n = tk.Label(self, bar_style_n)
        self.bar_row_4n = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                   font=font_relative, height=1, width=self.drv_width,
                                   fg=fg_color_plr, bg=bg_color_name_plr, anchor="w")
        self.bar_row_5n = tk.Label(self, bar_style_n)
        self.bar_row_6n = tk.Label(self, bar_style_n)
        self.bar_row_7n = tk.Label(self, bar_style_n)
        self.bar_row_1n.grid(row=0, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_2n.grid(row=1, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_3n.grid(row=2, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_4n.grid(row=3, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_5n.grid(row=4, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_6n.grid(row=5, column=column_drv, padx=0, pady=(0, bar_gap))
        self.bar_row_7n.grid(row=6, column=column_drv, padx=0, pady=0)

        # Time gap
        bar_style_g = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":gap_width,
                       "fg":fg_color, "bg":bg_color_gap, "anchor":"e"}
        self.bar_row_1g = tk.Label(self, bar_style_g)
        self.bar_row_2g = tk.Label(self, bar_style_g)
        self.bar_row_3g = tk.Label(self, bar_style_g)
        self.bar_row_4g = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                   font=font_relative, height=1, width=gap_width,
                                   fg=fg_color_plr, bg=bg_color_gap_plr, anchor="e")
        self.bar_row_5g = tk.Label(self, bar_style_g)
        self.bar_row_6g = tk.Label(self, bar_style_g)
        self.bar_row_7g = tk.Label(self, bar_style_g)
        self.bar_row_1g.grid(row=0, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_2g.grid(row=1, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_3g.grid(row=2, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_4g.grid(row=3, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_5g.grid(row=4, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_6g.grid(row=5, column=column_gap, padx=0, pady=(0, bar_gap))
        self.bar_row_7g.grid(row=6, column=column_gap, padx=0, pady=0)

        # Vehicle laptime
        if self.cfg["show_laptime"]:
            fg_color_lpt = self.cfg["font_color_laptime"]
            bg_color_lpt = self.cfg["bkg_color_laptime"]
            bar_style_t = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1, "width":9,
                           "fg":fg_color_lpt, "bg":bg_color_lpt}
            self.bar_row_1t = tk.Label(self, bar_style_t)
            self.bar_row_2t = tk.Label(self, bar_style_t)
            self.bar_row_3t = tk.Label(self, bar_style_t)
            self.bar_row_4t = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                       font=font_relative, height=1, width=9,
                                       fg=fg_color_plr, bg=bg_color_name_plr)
            self.bar_row_5t = tk.Label(self, bar_style_t)
            self.bar_row_6t = tk.Label(self, bar_style_t)
            self.bar_row_7t = tk.Label(self, bar_style_t)
            self.bar_row_1t.grid(row=0, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_2t.grid(row=1, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_3t.grid(row=2, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_4t.grid(row=3, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_5t.grid(row=4, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_6t.grid(row=5, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.bar_row_7t.grid(row=6, column=column_lpt, padx=0, pady=0)

        # Vehicle position in class
        if self.cfg["show_position_in_class"]:
            bar_style_i = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                           "height":1, "width":num_width,
                           "fg":fg_color_classplace, "bg":bg_color_classplace}
            self.bar_row_1i = tk.Label(self, bar_style_i)
            self.bar_row_2i = tk.Label(self, bar_style_i)
            self.bar_row_3i = tk.Label(self, bar_style_i)
            self.bar_row_4i = tk.Label(self, bar_style_i)
            self.bar_row_5i = tk.Label(self, bar_style_i)
            self.bar_row_6i = tk.Label(self, bar_style_i)
            self.bar_row_7i = tk.Label(self, bar_style_i)
            self.bar_row_1i.grid(row=0, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_2i.grid(row=1, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_3i.grid(row=2, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_4i.grid(row=3, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_5i.grid(row=4, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_6i.grid(row=5, column=column_pic, padx=0, pady=(0, bar_gap))
            self.bar_row_7i.grid(row=6, column=column_pic, padx=0, pady=0)

        # Vehicle class
        if self.cfg["show_class"]:
            self.vehcls = VehicleClass()  # load VehicleClass config
            fg_color_cls = self.cfg["font_color_class"]
            bg_color_cls = self.cfg["bkg_color_class"]
            bar_style_c = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1,
                           "width":self.cls_width,
                           "fg":fg_color_cls, "bg":bg_color_cls}
            self.bar_row_1c = tk.Label(self, bar_style_c)
            self.bar_row_2c = tk.Label(self, bar_style_c)
            self.bar_row_3c = tk.Label(self, bar_style_c)
            self.bar_row_4c = tk.Label(self, bar_style_c)
            self.bar_row_5c = tk.Label(self, bar_style_c)
            self.bar_row_6c = tk.Label(self, bar_style_c)
            self.bar_row_7c = tk.Label(self, bar_style_c)
            self.bar_row_1c.grid(row=0, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_2c.grid(row=1, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_3c.grid(row=2, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_4c.grid(row=3, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_5c.grid(row=4, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_6c.grid(row=5, column=column_cls, padx=0, pady=(0, bar_gap))
            self.bar_row_7c.grid(row=6, column=column_cls, padx=0, pady=0)

        # Vehicle in pit
        if self.cfg["show_pit_status"]:
            bar_style_s = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                           "height":1, "width":len(self.cfg["pit_status_text"])+1,
                           "fg":fg_color_pit, "bg":bg_color_pit}
            self.bar_row_1s = tk.Label(self, bar_style_s)
            self.bar_row_2s = tk.Label(self, bar_style_s)
            self.bar_row_3s = tk.Label(self, bar_style_s)
            self.bar_row_4s = tk.Label(self, bar_style_s)
            self.bar_row_5s = tk.Label(self, bar_style_s)
            self.bar_row_6s = tk.Label(self, bar_style_s)
            self.bar_row_7s = tk.Label(self, bar_style_s)
            self.bar_row_1s.grid(row=0, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_2s.grid(row=1, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_3s.grid(row=2, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_4s.grid(row=3, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_5s.grid(row=4, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_6s.grid(row=5, column=column_pit, padx=0, pady=(0, bar_gap))
            self.bar_row_7s.grid(row=6, column=column_pit, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.cfg["enable"]:

            # Read relative data
            rel_list, cls_info = read_data.relative_list()
            plr = rel_list[3]

            v1_plc, v1_drv, v1_lpt, v1_pic, v1_cls, v1_gap, v1_lap, v1_pit = read_data.relative_data(rel_list[0], plr, cls_info)
            v2_plc, v2_drv, v2_lpt, v2_pic, v2_cls, v2_gap, v2_lap, v2_pit = read_data.relative_data(rel_list[1], plr, cls_info)
            v3_plc, v3_drv, v3_lpt, v3_pic, v3_cls, v3_gap, v3_lap, v3_pit = read_data.relative_data(rel_list[2], plr, cls_info)
            v4_plc, v4_drv, v4_lpt, v4_pic, v4_cls, v4_gap, v4_lap, v4_pit = read_data.relative_data(plr, plr, cls_info)
            v5_plc, v5_drv, v5_lpt, v5_pic, v5_cls, v5_gap, v5_lap, v5_pit = read_data.relative_data(rel_list[4], plr, cls_info)
            v6_plc, v6_drv, v6_lpt, v6_pic, v6_cls, v6_gap, v6_lap, v6_pit = read_data.relative_data(rel_list[5], plr, cls_info)
            v7_plc, v7_drv, v7_lpt, v7_pic, v7_cls, v7_gap, v7_lap, v7_pit = read_data.relative_data(rel_list[6], plr, cls_info)

            # Check isPlayer before update
            if read_data.is_local_player():

                # Relative update
                # Driver place
                self.bar_row_1p.config(text=v1_plc, fg=self.color_lapdiff(v1_lap, v4_lap))
                self.bar_row_2p.config(text=v2_plc, fg=self.color_lapdiff(v2_lap, v4_lap))
                self.bar_row_3p.config(text=v3_plc, fg=self.color_lapdiff(v3_lap, v4_lap))
                self.bar_row_4p.config(text=v4_plc)
                self.bar_row_5p.config(text=v5_plc, fg=self.color_lapdiff(v5_lap, v4_lap))
                self.bar_row_6p.config(text=v6_plc, fg=self.color_lapdiff(v6_lap, v4_lap))
                self.bar_row_7p.config(text=v7_plc, fg=self.color_lapdiff(v7_lap, v4_lap))

                # Driver name
                self.bar_row_1n.config(text=v1_drv[:self.drv_width], fg=self.color_lapdiff(v1_lap, v4_lap))
                self.bar_row_2n.config(text=v2_drv[:self.drv_width], fg=self.color_lapdiff(v2_lap, v4_lap))
                self.bar_row_3n.config(text=v3_drv[:self.drv_width], fg=self.color_lapdiff(v3_lap, v4_lap))
                self.bar_row_4n.config(text=v4_drv[:self.drv_width])
                self.bar_row_5n.config(text=v5_drv[:self.drv_width], fg=self.color_lapdiff(v5_lap, v4_lap))
                self.bar_row_6n.config(text=v6_drv[:self.drv_width], fg=self.color_lapdiff(v6_lap, v4_lap))
                self.bar_row_7n.config(text=v7_drv[:self.drv_width], fg=self.color_lapdiff(v7_lap, v4_lap))

                # Time gap
                self.bar_row_1g.config(text=v1_gap, fg=self.color_lapdiff(v1_lap, v4_lap))
                self.bar_row_2g.config(text=v2_gap, fg=self.color_lapdiff(v2_lap, v4_lap))
                self.bar_row_3g.config(text=v3_gap, fg=self.color_lapdiff(v3_lap, v4_lap))
                self.bar_row_4g.config(text=v4_gap)
                self.bar_row_5g.config(text=v5_gap, fg=self.color_lapdiff(v5_lap, v4_lap))
                self.bar_row_6g.config(text=v6_gap, fg=self.color_lapdiff(v6_lap, v4_lap))
                self.bar_row_7g.config(text=v7_gap, fg=self.color_lapdiff(v7_lap, v4_lap))

                if self.cfg["show_laptime"]:
                    self.bar_row_1t.config(text=v1_lpt)
                    self.bar_row_2t.config(text=v2_lpt)
                    self.bar_row_3t.config(text=v3_lpt)
                    self.bar_row_4t.config(text=v4_lpt)
                    self.bar_row_5t.config(text=v5_lpt)
                    self.bar_row_6t.config(text=v6_lpt)
                    self.bar_row_7t.config(text=v7_lpt)

                if self.cfg["show_position_in_class"]:
                    self.bar_row_1i.config(text=v1_pic)
                    self.bar_row_2i.config(text=v2_pic)
                    self.bar_row_3i.config(text=v3_pic)
                    self.bar_row_4i.config(text=v4_pic)
                    self.bar_row_5i.config(text=v5_pic)
                    self.bar_row_6i.config(text=v6_pic)
                    self.bar_row_7i.config(text=v7_pic)

                if self.cfg["show_class"]:
                    self.bar_row_1c.config(self.set_class(v1_cls))
                    self.bar_row_2c.config(self.set_class(v2_cls))
                    self.bar_row_3c.config(self.set_class(v3_cls))
                    self.bar_row_4c.config(self.set_class(v4_cls))
                    self.bar_row_5c.config(self.set_class(v5_cls))
                    self.bar_row_6c.config(self.set_class(v6_cls))
                    self.bar_row_7c.config(self.set_class(v7_cls))

                if self.cfg["show_pit_status"]:
                    self.bar_row_1s.config(self.set_pitstatus(v1_pit))
                    self.bar_row_2s.config(self.set_pitstatus(v2_pit))
                    self.bar_row_3s.config(self.set_pitstatus(v3_pit))
                    self.bar_row_4s.config(self.set_pitstatus(v4_pit))
                    self.bar_row_5s.config(self.set_pitstatus(v5_pit))
                    self.bar_row_6s.config(self.set_pitstatus(v6_pit))
                    self.bar_row_7s.config(self.set_pitstatus(v7_pit))

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    def color_lapdiff(self, nlap, player_nlap):
        """Compare lap differences & set color"""
        if nlap > player_nlap:
            color = self.cfg["font_color_laps_ahead"]
        elif nlap < player_nlap:
            color = self.cfg["font_color_laps_behind"]
        else:
            color = self.cfg["font_color_same_lap"]
        return color

    def set_pitstatus(self, pits):
        """Compare lap differences & set color"""
        if pits > 0:
            status = {"text":self.cfg["pit_status_text"], "bg":self.cfg["bkg_color_pit"]}
        else:
            status = {"text":"", "bg":"#000002"}
        return status

    def set_class(self, vehclass):
        """Compare vehicle class name with user defined dictionary"""
        short_name = vehclass
        class_config = {"text":short_name[:self.cls_width]}
        for key, value in self.vehcls.classdict_user.items():
            # If class name matches user defined class
            if vehclass == key:
                # Assign new class name from user defined value
                short_name = value
                for subkey, subvalue in short_name.items():
                    # Assign corresponding background color
                    class_config = {"text":subkey, "bg":subvalue}
                    break
        return class_config
