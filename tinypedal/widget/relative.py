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

from tinypedal.__init__ import cfg
import tinypedal.readapi as read_data
from tinypedal.base import relative_info, Widget, MouseEvent
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
        gap_width = self.cfg["bar_time_gap_width"]
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
        fg_color_tyrecmp = self.cfg["font_color_tyre_compound"]
        bg_color_tyrecmp = self.cfg["bkg_color_tyre_compound"]
        fg_color_pit = self.cfg["font_color_pit"]
        bg_color_pit = self.cfg["bkg_color_pit"]

        column_plc = self.cfg["column_index_place"]
        column_drv = self.cfg["column_index_driver"]
        column_lpt = self.cfg["column_index_laptime"]
        column_pic = self.cfg["column_index_position_in_class"]
        column_cls = self.cfg["column_index_class"]
        column_tcp = self.cfg["column_index_tyre_compound"]
        column_gap = self.cfg["column_index_time_gap"]
        column_pit = self.cfg["column_index_pit_status"]

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

        # Tyre compound index
        if self.cfg["show_tyre_compound"]:
            bar_style_m = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1, "width":2,
                           "fg":fg_color_tyrecmp, "bg":bg_color_tyrecmp}
            self.bar_row_1m = tk.Label(self, bar_style_m)
            self.bar_row_2m = tk.Label(self, bar_style_m)
            self.bar_row_3m = tk.Label(self, bar_style_m)
            self.bar_row_4m = tk.Label(self, bar_style_m)
            self.bar_row_5m = tk.Label(self, bar_style_m)
            self.bar_row_6m = tk.Label(self, bar_style_m)
            self.bar_row_7m = tk.Label(self, bar_style_m)
            self.bar_row_1m.grid(row=0, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_2m.grid(row=1, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_3m.grid(row=2, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_4m.grid(row=3, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_5m.grid(row=4, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_6m.grid(row=5, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.bar_row_7m.grid(row=6, column=column_tcp, padx=0, pady=0)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and relative_info.relative_list and self.cfg["enable"]:

            # Read relative data
            rel_idx, cls_info, plr_idx = relative_info.relative_list

            # Check isPlayer before update
            if read_data.is_local_player():

                # 0 place, 1 driver, 2 laptime, 3 pos_class, 4 veh_class, 5 time_gap, 6 num_lap, 7 in_pit
                veh_a = relative_info.relative_data(rel_idx[0], plr_idx, cls_info)
                veh_b = relative_info.relative_data(rel_idx[1], plr_idx, cls_info)
                veh_c = relative_info.relative_data(rel_idx[2], plr_idx, cls_info)
                veh_d = relative_info.relative_data(plr_idx, plr_idx, cls_info)
                veh_e = relative_info.relative_data(rel_idx[4], plr_idx, cls_info)
                veh_f = relative_info.relative_data(rel_idx[5], plr_idx, cls_info)
                veh_g = relative_info.relative_data(rel_idx[6], plr_idx, cls_info)

                # Relative update
                # Driver place
                self.bar_row_1p.config(text=veh_a[0], fg=self.color_lapdiff(veh_a[6], veh_d[6]))
                self.bar_row_2p.config(text=veh_b[0], fg=self.color_lapdiff(veh_b[6], veh_d[6]))
                self.bar_row_3p.config(text=veh_c[0], fg=self.color_lapdiff(veh_c[6], veh_d[6]))
                self.bar_row_4p.config(text=veh_d[0])
                self.bar_row_5p.config(text=veh_e[0], fg=self.color_lapdiff(veh_e[6], veh_d[6]))
                self.bar_row_6p.config(text=veh_f[0], fg=self.color_lapdiff(veh_f[6], veh_d[6]))
                self.bar_row_7p.config(text=veh_g[0], fg=self.color_lapdiff(veh_g[6], veh_d[6]))

                # Driver name
                self.bar_row_1n.config(text=veh_a[1][:self.drv_width], fg=self.color_lapdiff(veh_a[6], veh_d[6]))
                self.bar_row_2n.config(text=veh_b[1][:self.drv_width], fg=self.color_lapdiff(veh_b[6], veh_d[6]))
                self.bar_row_3n.config(text=veh_c[1][:self.drv_width], fg=self.color_lapdiff(veh_c[6], veh_d[6]))
                self.bar_row_4n.config(text=veh_d[1][:self.drv_width])
                self.bar_row_5n.config(text=veh_e[1][:self.drv_width], fg=self.color_lapdiff(veh_e[6], veh_d[6]))
                self.bar_row_6n.config(text=veh_f[1][:self.drv_width], fg=self.color_lapdiff(veh_f[6], veh_d[6]))
                self.bar_row_7n.config(text=veh_g[1][:self.drv_width], fg=self.color_lapdiff(veh_g[6], veh_d[6]))

                # Vehicle laptime
                if self.cfg["show_laptime"]:
                    self.bar_row_1t.config(text=veh_a[2])
                    self.bar_row_2t.config(text=veh_b[2])
                    self.bar_row_3t.config(text=veh_c[2])
                    self.bar_row_4t.config(text=veh_d[2])
                    self.bar_row_5t.config(text=veh_e[2])
                    self.bar_row_6t.config(text=veh_f[2])
                    self.bar_row_7t.config(text=veh_g[2])

                # Vehicle position in class
                if self.cfg["show_position_in_class"]:
                    self.bar_row_1i.config(text=veh_a[3])
                    self.bar_row_2i.config(text=veh_b[3])
                    self.bar_row_3i.config(text=veh_c[3])
                    self.bar_row_4i.config(text=veh_d[3])
                    self.bar_row_5i.config(text=veh_e[3])
                    self.bar_row_6i.config(text=veh_f[3])
                    self.bar_row_7i.config(text=veh_g[3])

                # Vehicle class
                if self.cfg["show_class"]:
                    self.bar_row_1c.config(self.set_class_style(veh_a[4]))
                    self.bar_row_2c.config(self.set_class_style(veh_b[4]))
                    self.bar_row_3c.config(self.set_class_style(veh_c[4]))
                    self.bar_row_4c.config(self.set_class_style(veh_d[4]))
                    self.bar_row_5c.config(self.set_class_style(veh_e[4]))
                    self.bar_row_6c.config(self.set_class_style(veh_f[4]))
                    self.bar_row_7c.config(self.set_class_style(veh_g[4]))

                # Tyre compound index
                if self.cfg["show_tyre_compound"]:
                    self.bar_row_1m.config(text=self.set_tyre_cmp(veh_a[8]))
                    self.bar_row_2m.config(text=self.set_tyre_cmp(veh_b[8]))
                    self.bar_row_3m.config(text=self.set_tyre_cmp(veh_c[8]))
                    self.bar_row_4m.config(text=self.set_tyre_cmp(veh_d[8]))
                    self.bar_row_5m.config(text=self.set_tyre_cmp(veh_e[8]))
                    self.bar_row_6m.config(text=self.set_tyre_cmp(veh_f[8]))
                    self.bar_row_7m.config(text=self.set_tyre_cmp(veh_g[8]))

                # Time gap
                self.bar_row_1g.config(text=veh_a[5], fg=self.color_lapdiff(veh_a[6], veh_d[6]))
                self.bar_row_2g.config(text=veh_b[5], fg=self.color_lapdiff(veh_b[6], veh_d[6]))
                self.bar_row_3g.config(text=veh_c[5], fg=self.color_lapdiff(veh_c[6], veh_d[6]))
                self.bar_row_4g.config(text=veh_d[5])
                self.bar_row_5g.config(text=veh_e[5], fg=self.color_lapdiff(veh_e[6], veh_d[6]))
                self.bar_row_6g.config(text=veh_f[5], fg=self.color_lapdiff(veh_f[6], veh_d[6]))
                self.bar_row_7g.config(text=veh_g[5], fg=self.color_lapdiff(veh_g[6], veh_d[6]))

                # Vehicle in pit
                if self.cfg["show_pit_status"]:
                    self.bar_row_1s.config(self.set_pitstatus(veh_a[7]))
                    self.bar_row_2s.config(self.set_pitstatus(veh_b[7]))
                    self.bar_row_3s.config(self.set_pitstatus(veh_c[7]))
                    self.bar_row_4s.config(self.set_pitstatus(veh_d[7]))
                    self.bar_row_5s.config(self.set_pitstatus(veh_e[7]))
                    self.bar_row_6s.config(self.set_pitstatus(veh_f[7]))
                    self.bar_row_7s.config(self.set_pitstatus(veh_g[7]))

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

    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        if tc_index:
            ftire = self.cfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
            rtire = self.cfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
            tire_cmpd = f"{ftire}{rtire}"
        else:
            tire_cmpd = ""
        return tire_cmpd

    def set_pitstatus(self, pits):
        """Compare lap differences & set color"""
        if pits > 0:
            status = {"text":self.cfg["pit_status_text"], "bg":self.cfg["bkg_color_pit"]}
        else:
            status = {"text":"", "bg":"#000002"}
        return status

    def set_class_style(self, vehclass_name):
        """Compare vehicle class name with user defined dictionary"""
        if vehclass_name == "":
            class_config = {"text":"", "bg":self.cfg["bkg_color_class"]}
        else:
            class_config = {"text":vehclass_name[:self.cls_width],
                            "bg":self.cfg["bkg_color_class"]}

        for key, value in self.vehcls.classdict_user.items():
            # If class name matches user defined class
            if vehclass_name == key:
                # Assign new class name from user defined value
                short_name = value
                for subkey, subvalue in short_name.items():
                    # Assign corresponding background color
                    class_config = {"text":subkey, "bg":subvalue}
                    break

        return class_config
