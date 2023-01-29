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

from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module
from ..setting import VehicleClass

WIDGET_NAME = "relative"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * 0.3
        bar_gap = self.wcfg["bar_gap"]
        num_width = 3
        gap_width = self.wcfg["bar_time_gap_width"]
        self.drv_width = self.wcfg["bar_driver_name_width"]
        self.cls_width = self.wcfg["bar_class_name_width"]

        # Config style & variable
        text_def = ""
        fg_color = "#FFF"  # placeholder, font color for place, name, gap changes dynamically
        fg_color_plr = self.wcfg["font_color_player"]
        bg_color_place = self.wcfg["bkg_color_place"]
        bg_color_place_plr = self.wcfg["bkg_color_player_place"]
        bg_color_name = self.wcfg["bkg_color_name"]
        bg_color_name_plr = self.wcfg["bkg_color_player_name"]
        bg_color_gap = self.wcfg["bkg_color_gap"]
        bg_color_gap_plr = self.wcfg["bkg_color_player_gap"]
        fg_color_classplace = self.wcfg["font_color_position_in_class"]
        bg_color_classplace = self.wcfg["bkg_color_position_in_class"]
        fg_color_tyrecmp = self.wcfg["font_color_tyre_compound"]
        bg_color_tyrecmp = self.wcfg["bkg_color_tyre_compound"]
        fg_color_pit = self.wcfg["font_color_pit"]
        bg_color_pit = self.wcfg["bkg_color_pit"]

        column_plc = self.wcfg["column_index_place"]
        column_drv = self.wcfg["column_index_driver"]
        column_lpt = self.wcfg["column_index_laptime"]
        column_pic = self.wcfg["column_index_position_in_class"]
        column_cls = self.wcfg["column_index_class"]
        column_tcp = self.wcfg["column_index_tyre_compound"]
        column_gap = self.wcfg["column_index_time_gap"]
        column_pit = self.wcfg["column_index_pit_status"]

        font_relative = tkfont.Font(family=self.wcfg["font_name"],
                                    size=-self.wcfg["font_size"],
                                    weight=self.wcfg["font_weight"])
        plr_row = 9  # set player row number

        # Max display players
        self.rel_add_front = min(max(self.wcfg["additional_players_front"], 0), 3)
        self.rel_add_behind = min(max(self.wcfg["additional_players_behind"], 0), 3)

        # Draw label
        # Driver place number
        bar_style_p = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                       "height":1, "width":num_width, "fg":fg_color, "bg":bg_color_place}

        self.row_plrp = tk.Label(self, text=text_def, bd=0, padx=0, pady=0,
                                 font=font_relative, height=1, width=num_width,
                                 fg=fg_color_plr, bg=bg_color_place_plr)
        self.row_plrp.grid(row=plr_row, column=column_plc, padx=0, pady=(0, bar_gap))

        self.row_f_03p = tk.Label(self, bar_style_p)
        self.row_f_02p = tk.Label(self, bar_style_p)
        self.row_f_01p = tk.Label(self, bar_style_p)
        self.row_r_01p = tk.Label(self, bar_style_p)
        self.row_r_02p = tk.Label(self, bar_style_p)
        self.row_r_03p = tk.Label(self, bar_style_p)
        self.row_f_03p.grid(row=plr_row - 3, column=column_plc, padx=0, pady=(0, bar_gap))
        self.row_f_02p.grid(row=plr_row - 2, column=column_plc, padx=0, pady=(0, bar_gap))
        self.row_f_01p.grid(row=plr_row - 1, column=column_plc, padx=0, pady=(0, bar_gap))
        self.row_r_01p.grid(row=plr_row + 1, column=column_plc, padx=0, pady=(0, bar_gap))
        self.row_r_02p.grid(row=plr_row + 2, column=column_plc, padx=0, pady=(0, bar_gap))
        self.row_r_03p.grid(row=plr_row + 3, column=column_plc, padx=0, pady=(0, bar_gap))

        if self.rel_add_front > 0:
            self.row_f_04p = tk.Label(self, bar_style_p)
            self.row_f_04p.grid(row=plr_row - 4, column=column_plc, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 0:
            self.row_r_04p = tk.Label(self, bar_style_p)
            self.row_r_04p.grid(row=plr_row + 4, column=column_plc, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 1:
            self.row_f_05p = tk.Label(self, bar_style_p)
            self.row_f_05p.grid(row=plr_row - 5, column=column_plc, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 1:
            self.row_r_05p = tk.Label(self, bar_style_p)
            self.row_r_05p.grid(row=plr_row + 5, column=column_plc, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 2:
            self.row_f_06p = tk.Label(self, bar_style_p)
            self.row_f_06p.grid(row=plr_row - 6, column=column_plc, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 2:
            self.row_r_06p = tk.Label(self, bar_style_p)
            self.row_r_06p.grid(row=plr_row + 6, column=column_plc, padx=0, pady=(0, bar_gap))

        # Driver name
        bar_style_n = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":self.drv_width,
                       "fg":fg_color, "bg":bg_color_name, "anchor":"w"}

        self.row_plrn = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                 font=font_relative, height=1, width=self.drv_width,
                                 fg=fg_color_plr, bg=bg_color_name_plr, anchor="w")
        self.row_plrn.grid(row=plr_row, column=column_drv, padx=0, pady=(0, bar_gap))

        self.row_f_03n = tk.Label(self, bar_style_n)
        self.row_f_02n = tk.Label(self, bar_style_n)
        self.row_f_01n = tk.Label(self, bar_style_n)
        self.row_r_01n = tk.Label(self, bar_style_n)
        self.row_r_02n = tk.Label(self, bar_style_n)
        self.row_r_03n = tk.Label(self, bar_style_n)
        self.row_f_03n.grid(row=plr_row - 3, column=column_drv, padx=0, pady=(0, bar_gap))
        self.row_f_02n.grid(row=plr_row - 2, column=column_drv, padx=0, pady=(0, bar_gap))
        self.row_f_01n.grid(row=plr_row - 1, column=column_drv, padx=0, pady=(0, bar_gap))
        self.row_r_01n.grid(row=plr_row + 1, column=column_drv, padx=0, pady=(0, bar_gap))
        self.row_r_02n.grid(row=plr_row + 2, column=column_drv, padx=0, pady=(0, bar_gap))
        self.row_r_03n.grid(row=plr_row + 3, column=column_drv, padx=0, pady=(0, bar_gap))

        if self.rel_add_front > 0:
            self.row_f_04n = tk.Label(self, bar_style_n)
            self.row_f_04n.grid(row=plr_row - 4, column=column_drv, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 0:
            self.row_r_04n = tk.Label(self, bar_style_n)
            self.row_r_04n.grid(row=plr_row + 4, column=column_drv, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 1:
            self.row_f_05n = tk.Label(self, bar_style_n)
            self.row_f_05n.grid(row=plr_row - 5, column=column_drv, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 1:
            self.row_r_05n = tk.Label(self, bar_style_n)
            self.row_r_05n.grid(row=plr_row + 5, column=column_drv, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 2:
            self.row_f_06n = tk.Label(self, bar_style_n)
            self.row_f_06n.grid(row=plr_row - 6, column=column_drv, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 2:
            self.row_r_06n = tk.Label(self, bar_style_n)
            self.row_r_06n.grid(row=plr_row + 6, column=column_drv, padx=0, pady=(0, bar_gap))

        # Time gap
        bar_style_g = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                       "font":font_relative, "height":1, "width":gap_width,
                       "fg":fg_color, "bg":bg_color_gap, "anchor":"e"}

        self.row_plrg = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                 font=font_relative, height=1, width=gap_width,
                                 fg=fg_color_plr, bg=bg_color_gap_plr, anchor="e")
        self.row_plrg.grid(row=plr_row, column=column_gap, padx=0, pady=(0, bar_gap))

        self.row_f_03g = tk.Label(self, bar_style_g)
        self.row_f_02g = tk.Label(self, bar_style_g)
        self.row_f_01g = tk.Label(self, bar_style_g)
        self.row_r_01g = tk.Label(self, bar_style_g)
        self.row_r_02g = tk.Label(self, bar_style_g)
        self.row_r_03g = tk.Label(self, bar_style_g)
        self.row_f_03g.grid(row=plr_row - 3, column=column_gap, padx=0, pady=(0, bar_gap))
        self.row_f_02g.grid(row=plr_row - 2, column=column_gap, padx=0, pady=(0, bar_gap))
        self.row_f_01g.grid(row=plr_row - 1, column=column_gap, padx=0, pady=(0, bar_gap))
        self.row_r_01g.grid(row=plr_row + 1, column=column_gap, padx=0, pady=(0, bar_gap))
        self.row_r_02g.grid(row=plr_row + 2, column=column_gap, padx=0, pady=(0, bar_gap))
        self.row_r_03g.grid(row=plr_row + 3, column=column_gap, padx=0, pady=(0, bar_gap))

        if self.rel_add_front > 0:
            self.row_f_04g = tk.Label(self, bar_style_g)
            self.row_f_04g.grid(row=plr_row - 4, column=column_gap, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 0:
            self.row_r_04g = tk.Label(self, bar_style_g)
            self.row_r_04g.grid(row=plr_row + 4, column=column_gap, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 1:
            self.row_f_05g = tk.Label(self, bar_style_g)
            self.row_f_05g.grid(row=plr_row - 5, column=column_gap, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 1:
            self.row_r_05g = tk.Label(self, bar_style_g)
            self.row_r_05g.grid(row=plr_row + 5, column=column_gap, padx=0, pady=(0, bar_gap))
        if self.rel_add_front > 2:
            self.row_f_06g = tk.Label(self, bar_style_g)
            self.row_f_06g.grid(row=plr_row - 6, column=column_gap, padx=0, pady=(0, bar_gap))
        if self.rel_add_behind > 2:
            self.row_r_06g = tk.Label(self, bar_style_g)
            self.row_r_06g.grid(row=plr_row + 6, column=column_gap, padx=0, pady=(0, bar_gap))

        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            fg_color_lpt = self.wcfg["font_color_laptime"]
            bg_color_lpt = self.wcfg["bkg_color_laptime"]
            bar_style_t = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1, "width":9,
                           "fg":fg_color_lpt, "bg":bg_color_lpt}

            self.row_plrt = tk.Label(self, text=text_def, bd=0, padx=bar_padx, pady=0,
                                     font=font_relative, height=1, width=9,
                                     fg=fg_color_plr, bg=bg_color_name_plr)
            self.row_plrt.grid(row=plr_row, column=column_lpt, padx=0, pady=(0, bar_gap))

            self.row_f_03t = tk.Label(self, bar_style_t)
            self.row_f_02t = tk.Label(self, bar_style_t)
            self.row_f_01t = tk.Label(self, bar_style_t)
            self.row_r_01t = tk.Label(self, bar_style_t)
            self.row_r_02t = tk.Label(self, bar_style_t)
            self.row_r_03t = tk.Label(self, bar_style_t)
            self.row_f_03t.grid(row=plr_row - 3, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.row_f_02t.grid(row=plr_row - 2, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.row_f_01t.grid(row=plr_row - 1, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.row_r_01t.grid(row=plr_row + 1, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.row_r_02t.grid(row=plr_row + 2, column=column_lpt, padx=0, pady=(0, bar_gap))
            self.row_r_03t.grid(row=plr_row + 3, column=column_lpt, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > 0:
                self.row_f_04t = tk.Label(self, bar_style_t)
                self.row_f_04t.grid(row=plr_row - 4, column=column_lpt, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 0:
                self.row_r_04t = tk.Label(self, bar_style_t)
                self.row_r_04t.grid(row=plr_row + 4, column=column_lpt, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 1:
                self.row_f_05t = tk.Label(self, bar_style_t)
                self.row_f_05t.grid(row=plr_row - 5, column=column_lpt, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 1:
                self.row_r_05t = tk.Label(self, bar_style_t)
                self.row_r_05t.grid(row=plr_row + 5, column=column_lpt, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 2:
                self.row_f_06t = tk.Label(self, bar_style_t)
                self.row_f_06t.grid(row=plr_row - 6, column=column_lpt, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 2:
                self.row_r_06t = tk.Label(self, bar_style_t)
                self.row_r_06t.grid(row=plr_row + 6, column=column_lpt, padx=0, pady=(0, bar_gap))

        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_i = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                           "height":1, "width":num_width,
                           "fg":fg_color_classplace, "bg":bg_color_classplace}

            self.row_plri = tk.Label(self, bar_style_i)
            self.row_plri.grid(row=plr_row, column=column_pic, padx=0, pady=(0, bar_gap))

            self.row_f_03i = tk.Label(self, bar_style_i)
            self.row_f_02i = tk.Label(self, bar_style_i)
            self.row_f_01i = tk.Label(self, bar_style_i)
            self.row_r_01i = tk.Label(self, bar_style_i)
            self.row_r_02i = tk.Label(self, bar_style_i)
            self.row_r_03i = tk.Label(self, bar_style_i)
            self.row_f_03i.grid(row=plr_row - 3, column=column_pic, padx=0, pady=(0, bar_gap))
            self.row_f_02i.grid(row=plr_row - 2, column=column_pic, padx=0, pady=(0, bar_gap))
            self.row_f_01i.grid(row=plr_row - 1, column=column_pic, padx=0, pady=(0, bar_gap))
            self.row_r_01i.grid(row=plr_row + 1, column=column_pic, padx=0, pady=(0, bar_gap))
            self.row_r_02i.grid(row=plr_row + 2, column=column_pic, padx=0, pady=(0, bar_gap))
            self.row_r_03i.grid(row=plr_row + 3, column=column_pic, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > 0:
                self.row_f_04i = tk.Label(self, bar_style_i)
                self.row_f_04i.grid(row=plr_row - 4, column=column_pic, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 0:
                self.row_r_04i = tk.Label(self, bar_style_i)
                self.row_r_04i.grid(row=plr_row + 4, column=column_pic, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 1:
                self.row_f_05i = tk.Label(self, bar_style_i)
                self.row_f_05i.grid(row=plr_row - 5, column=column_pic, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 1:
                self.row_r_05i = tk.Label(self, bar_style_i)
                self.row_r_05i.grid(row=plr_row + 5, column=column_pic, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 2:
                self.row_f_06i = tk.Label(self, bar_style_i)
                self.row_f_06i.grid(row=plr_row - 6, column=column_pic, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 2:
                self.row_r_06i = tk.Label(self, bar_style_i)
                self.row_r_06i.grid(row=plr_row + 6, column=column_pic, padx=0, pady=(0, bar_gap))

        # Vehicle class
        if self.wcfg["show_class"]:
            self.vehcls = VehicleClass()  # load VehicleClass config
            fg_color_cls = self.wcfg["font_color_class"]
            bg_color_cls = self.wcfg["bkg_color_class"]
            bar_style_c = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1,
                           "width":self.cls_width,
                           "fg":fg_color_cls, "bg":bg_color_cls}

            self.row_plrc = tk.Label(self, bar_style_c)
            self.row_plrc.grid(row=plr_row, column=column_cls, padx=0, pady=(0, bar_gap))

            self.row_f_03c = tk.Label(self, bar_style_c)
            self.row_f_02c = tk.Label(self, bar_style_c)
            self.row_f_01c = tk.Label(self, bar_style_c)
            self.row_r_01c = tk.Label(self, bar_style_c)
            self.row_r_02c = tk.Label(self, bar_style_c)
            self.row_r_03c = tk.Label(self, bar_style_c)
            self.row_f_03c.grid(row=plr_row - 3, column=column_cls, padx=0, pady=(0, bar_gap))
            self.row_f_02c.grid(row=plr_row - 2, column=column_cls, padx=0, pady=(0, bar_gap))
            self.row_f_01c.grid(row=plr_row - 1, column=column_cls, padx=0, pady=(0, bar_gap))
            self.row_r_01c.grid(row=plr_row + 1, column=column_cls, padx=0, pady=(0, bar_gap))
            self.row_r_02c.grid(row=plr_row + 2, column=column_cls, padx=0, pady=(0, bar_gap))
            self.row_r_03c.grid(row=plr_row + 3, column=column_cls, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > 0:
                self.row_f_04c = tk.Label(self, bar_style_c)
                self.row_f_04c.grid(row=plr_row - 4, column=column_cls, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 0:
                self.row_r_04c = tk.Label(self, bar_style_c)
                self.row_r_04c.grid(row=plr_row + 4, column=column_cls, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 1:
                self.row_f_05c = tk.Label(self, bar_style_c)
                self.row_f_05c.grid(row=plr_row - 5, column=column_cls, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 1:
                self.row_r_05c = tk.Label(self, bar_style_c)
                self.row_r_05c.grid(row=plr_row + 5, column=column_cls, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 2:
                self.row_f_06c = tk.Label(self, bar_style_c)
                self.row_f_06c.grid(row=plr_row - 6, column=column_cls, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 2:
                self.row_r_06c = tk.Label(self, bar_style_c)
                self.row_r_06c.grid(row=plr_row + 6, column=column_cls, padx=0, pady=(0, bar_gap))

        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            bar_style_s = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                           "height":1, "width":len(self.wcfg["pit_status_text"])+1,
                           "fg":fg_color_pit, "bg":bg_color_pit}

            self.row_plrs = tk.Label(self, bar_style_s)
            self.row_plrs.grid(row=plr_row, column=column_pit, padx=0, pady=(0, bar_gap))

            self.row_f_03s = tk.Label(self, bar_style_s)
            self.row_f_02s = tk.Label(self, bar_style_s)
            self.row_f_01s = tk.Label(self, bar_style_s)
            self.row_r_01s = tk.Label(self, bar_style_s)
            self.row_r_02s = tk.Label(self, bar_style_s)
            self.row_r_03s = tk.Label(self, bar_style_s)
            self.row_f_03s.grid(row=plr_row - 3, column=column_pit, padx=0, pady=(0, bar_gap))
            self.row_f_02s.grid(row=plr_row - 2, column=column_pit, padx=0, pady=(0, bar_gap))
            self.row_f_01s.grid(row=plr_row - 1, column=column_pit, padx=0, pady=(0, bar_gap))
            self.row_r_01s.grid(row=plr_row + 1, column=column_pit, padx=0, pady=(0, bar_gap))
            self.row_r_02s.grid(row=plr_row + 2, column=column_pit, padx=0, pady=(0, bar_gap))
            self.row_r_03s.grid(row=plr_row + 3, column=column_pit, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > 0:
                self.row_f_04s = tk.Label(self, bar_style_s)
                self.row_f_04s.grid(row=plr_row - 4, column=column_pit, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 0:
                self.row_r_04s = tk.Label(self, bar_style_s)
                self.row_r_04s.grid(row=plr_row + 4, column=column_pit, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 1:
                self.row_f_05s = tk.Label(self, bar_style_s)
                self.row_f_05s.grid(row=plr_row - 5, column=column_pit, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 1:
                self.row_r_05s = tk.Label(self, bar_style_s)
                self.row_r_05s.grid(row=plr_row + 5, column=column_pit, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 2:
                self.row_f_06s = tk.Label(self, bar_style_s)
                self.row_f_06s.grid(row=plr_row - 6, column=column_pit, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 2:
                self.row_r_06s = tk.Label(self, bar_style_s)
                self.row_r_06s.grid(row=plr_row + 6, column=column_pit, padx=0, pady=(0, bar_gap))

        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_m = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                           "font":font_relative, "height":1, "width":2,
                           "fg":fg_color_tyrecmp, "bg":bg_color_tyrecmp}

            self.row_plrm = tk.Label(self, bar_style_m)
            self.row_plrm.grid(row=plr_row, column=column_tcp, padx=0, pady=(0, bar_gap))

            self.row_f_03m = tk.Label(self, bar_style_m)
            self.row_f_02m = tk.Label(self, bar_style_m)
            self.row_f_01m = tk.Label(self, bar_style_m)
            self.row_r_01m = tk.Label(self, bar_style_m)
            self.row_r_02m = tk.Label(self, bar_style_m)
            self.row_r_03m = tk.Label(self, bar_style_m)
            self.row_f_03m.grid(row=plr_row - 3, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.row_f_02m.grid(row=plr_row - 2, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.row_f_01m.grid(row=plr_row - 1, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.row_r_01m.grid(row=plr_row + 1, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.row_r_02m.grid(row=plr_row + 2, column=column_tcp, padx=0, pady=(0, bar_gap))
            self.row_r_03m.grid(row=plr_row + 3, column=column_tcp, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > 0:
                self.row_f_04m = tk.Label(self, bar_style_m)
                self.row_f_04m.grid(row=plr_row - 4, column=column_tcp, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 0:
                self.row_r_04m = tk.Label(self, bar_style_m)
                self.row_r_04m.grid(row=plr_row + 4, column=column_tcp, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 1:
                self.row_f_05m = tk.Label(self, bar_style_m)
                self.row_f_05m.grid(row=plr_row - 5, column=column_tcp, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 1:
                self.row_r_05m = tk.Label(self, bar_style_m)
                self.row_r_05m.grid(row=plr_row + 5, column=column_tcp, padx=0, pady=(0, bar_gap))
            if self.rel_add_front > 2:
                self.row_f_06m = tk.Label(self, bar_style_m)
                self.row_f_06m.grid(row=plr_row - 6, column=column_tcp, padx=0, pady=(0, bar_gap))
            if self.rel_add_behind > 2:
                self.row_r_06m = tk.Label(self, bar_style_m)
                self.row_r_06m.grid(row=plr_row + 6, column=column_tcp, padx=0, pady=(0, bar_gap))

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and module.relative_info.relative_list and self.wcfg["enable"]:

            # Read relative data
            rel_idx, cls_info, plr_idx = module.relative_info.relative_list
            veh_center = int(3 + self.rel_add_front)

            # Start updating
            # 0 place, 1 driver, 2 laptime, 3 pos_class, 4 veh_f_01lass, 5 time_gap, 6 num_lap, 7 in_pit
            veh_plr = module.relative_info.relative_data(plr_idx, plr_idx, cls_info)

            veh_f_03 = module.relative_info.relative_data(rel_idx[veh_center - 3], plr_idx, cls_info)
            veh_f_02 = module.relative_info.relative_data(rel_idx[veh_center - 2], plr_idx, cls_info)
            veh_f_01 = module.relative_info.relative_data(rel_idx[veh_center - 1], plr_idx, cls_info)
            veh_r_01 = module.relative_info.relative_data(rel_idx[veh_center + 1], plr_idx, cls_info)
            veh_r_02 = module.relative_info.relative_data(rel_idx[veh_center + 2], plr_idx, cls_info)
            veh_r_03 = module.relative_info.relative_data(rel_idx[veh_center + 3], plr_idx, cls_info)

            if self.rel_add_front > 0:
                veh_f_04 = module.relative_info.relative_data(rel_idx[veh_center - 4], plr_idx, cls_info)
            if self.rel_add_behind > 0:
                veh_r_04 = module.relative_info.relative_data(rel_idx[veh_center + 4], plr_idx, cls_info)
            if self.rel_add_front > 1:
                veh_f_05 = module.relative_info.relative_data(rel_idx[veh_center - 5], plr_idx, cls_info)
            if self.rel_add_behind > 1:
                veh_r_05 = module.relative_info.relative_data(rel_idx[veh_center + 5], plr_idx, cls_info)
            if self.rel_add_front > 2:
                veh_f_06 = module.relative_info.relative_data(rel_idx[veh_center - 6], plr_idx, cls_info)
            if self.rel_add_behind > 2:
                veh_r_06 = module.relative_info.relative_data(rel_idx[veh_center + 6], plr_idx, cls_info)

            # Relative update
            # Driver place
            self.row_plrp.config(text=veh_plr[0])

            self.row_f_03p.config(text=veh_f_03[0], fg=self.color_lapdiff(veh_f_03[6], veh_plr[6]))
            self.row_f_02p.config(text=veh_f_02[0], fg=self.color_lapdiff(veh_f_02[6], veh_plr[6]))
            self.row_f_01p.config(text=veh_f_01[0], fg=self.color_lapdiff(veh_f_01[6], veh_plr[6]))
            self.row_r_01p.config(text=veh_r_01[0], fg=self.color_lapdiff(veh_r_01[6], veh_plr[6]))
            self.row_r_02p.config(text=veh_r_02[0], fg=self.color_lapdiff(veh_r_02[6], veh_plr[6]))
            self.row_r_03p.config(text=veh_r_03[0], fg=self.color_lapdiff(veh_r_03[6], veh_plr[6]))

            if self.rel_add_front > 0:
                self.row_f_04p.config(text=veh_f_04[0], fg=self.color_lapdiff(veh_f_04[6], veh_plr[6]))
            if self.rel_add_behind > 0:
                self.row_r_04p.config(text=veh_r_04[0], fg=self.color_lapdiff(veh_r_04[6], veh_plr[6]))
            if self.rel_add_front > 1:
                self.row_f_05p.config(text=veh_f_05[0], fg=self.color_lapdiff(veh_f_05[6], veh_plr[6]))
            if self.rel_add_behind > 1:
                self.row_r_05p.config(text=veh_r_05[0], fg=self.color_lapdiff(veh_r_05[6], veh_plr[6]))
            if self.rel_add_front > 2:
                self.row_f_06p.config(text=veh_f_06[0], fg=self.color_lapdiff(veh_f_06[6], veh_plr[6]))
            if self.rel_add_behind > 2:
                self.row_r_06p.config(text=veh_r_06[0], fg=self.color_lapdiff(veh_r_06[6], veh_plr[6]))

            # Driver name
            self.row_plrn.config(text=veh_plr[1][:self.drv_width])

            self.row_f_03n.config(text=veh_f_03[1][:self.drv_width], fg=self.color_lapdiff(veh_f_03[6], veh_plr[6]))
            self.row_f_02n.config(text=veh_f_02[1][:self.drv_width], fg=self.color_lapdiff(veh_f_02[6], veh_plr[6]))
            self.row_f_01n.config(text=veh_f_01[1][:self.drv_width], fg=self.color_lapdiff(veh_f_01[6], veh_plr[6]))
            self.row_r_01n.config(text=veh_r_01[1][:self.drv_width], fg=self.color_lapdiff(veh_r_01[6], veh_plr[6]))
            self.row_r_02n.config(text=veh_r_02[1][:self.drv_width], fg=self.color_lapdiff(veh_r_02[6], veh_plr[6]))
            self.row_r_03n.config(text=veh_r_03[1][:self.drv_width], fg=self.color_lapdiff(veh_r_03[6], veh_plr[6]))

            if self.rel_add_front > 0:
                self.row_f_04n.config(text=veh_f_04[1][:self.drv_width], fg=self.color_lapdiff(veh_f_04[6], veh_plr[6]))
            if self.rel_add_behind > 0:
                self.row_r_04n.config(text=veh_r_04[1][:self.drv_width], fg=self.color_lapdiff(veh_r_04[6], veh_plr[6]))
            if self.rel_add_front > 1:
                self.row_f_05n.config(text=veh_f_05[1][:self.drv_width], fg=self.color_lapdiff(veh_f_05[6], veh_plr[6]))
            if self.rel_add_behind > 1:
                self.row_r_05n.config(text=veh_r_05[1][:self.drv_width], fg=self.color_lapdiff(veh_r_05[6], veh_plr[6]))
            if self.rel_add_front > 2:
                self.row_f_06n.config(text=veh_f_06[1][:self.drv_width], fg=self.color_lapdiff(veh_f_06[6], veh_plr[6]))
            if self.rel_add_behind > 2:
                self.row_r_06n.config(text=veh_r_06[1][:self.drv_width], fg=self.color_lapdiff(veh_r_06[6], veh_plr[6]))

            # Vehicle laptime
            if self.wcfg["show_laptime"]:
                self.row_plrt.config(text=veh_plr[2])

                self.row_f_03t.config(text=veh_f_03[2])
                self.row_f_02t.config(text=veh_f_02[2])
                self.row_f_01t.config(text=veh_f_01[2])
                self.row_r_01t.config(text=veh_r_01[2])
                self.row_r_02t.config(text=veh_r_02[2])
                self.row_r_03t.config(text=veh_r_03[2])

                if self.rel_add_front > 0:
                    self.row_f_04t.config(text=veh_f_04[2])
                if self.rel_add_behind > 0:
                    self.row_r_04t.config(text=veh_r_04[2])
                if self.rel_add_front > 1:
                    self.row_f_05t.config(text=veh_f_05[2])
                if self.rel_add_behind > 1:
                    self.row_r_05t.config(text=veh_r_05[2])
                if self.rel_add_front > 2:
                    self.row_f_06t.config(text=veh_f_06[2])
                if self.rel_add_behind > 2:
                    self.row_r_06t.config(text=veh_r_06[2])

            # Vehicle position in class
            if self.wcfg["show_position_in_class"]:
                self.row_plri.config(text=veh_plr[3])

                self.row_f_03i.config(text=veh_f_03[3])
                self.row_f_02i.config(text=veh_f_02[3])
                self.row_f_01i.config(text=veh_f_01[3])
                self.row_r_01i.config(text=veh_r_01[3])
                self.row_r_02i.config(text=veh_r_02[3])
                self.row_r_03i.config(text=veh_r_03[3])

                if self.rel_add_front > 0:
                    self.row_f_04i.config(text=veh_f_04[3])
                if self.rel_add_behind > 0:
                    self.row_r_04i.config(text=veh_r_04[3])
                if self.rel_add_front > 1:
                    self.row_f_05i.config(text=veh_f_05[3])
                if self.rel_add_behind > 1:
                    self.row_r_05i.config(text=veh_r_05[3])
                if self.rel_add_front > 2:
                    self.row_f_06i.config(text=veh_f_06[3])
                if self.rel_add_behind > 2:
                    self.row_r_06i.config(text=veh_r_06[3])

            # Vehicle class
            if self.wcfg["show_class"]:
                self.row_plrc.config(self.set_class_style(veh_plr[4]))

                self.row_f_03c.config(self.set_class_style(veh_f_03[4]))
                self.row_f_02c.config(self.set_class_style(veh_f_02[4]))
                self.row_f_01c.config(self.set_class_style(veh_f_01[4]))
                self.row_r_01c.config(self.set_class_style(veh_r_01[4]))
                self.row_r_02c.config(self.set_class_style(veh_r_02[4]))
                self.row_r_03c.config(self.set_class_style(veh_r_03[4]))

                if self.rel_add_front > 0:
                    self.row_f_04c.config(self.set_class_style(veh_f_04[4]))
                if self.rel_add_behind > 0:
                    self.row_r_04c.config(self.set_class_style(veh_r_04[4]))
                if self.rel_add_front > 1:
                    self.row_f_05c.config(self.set_class_style(veh_f_05[4]))
                if self.rel_add_behind > 1:
                    self.row_r_05c.config(self.set_class_style(veh_r_05[4]))
                if self.rel_add_front > 2:
                    self.row_f_06c.config(self.set_class_style(veh_f_06[4]))
                if self.rel_add_behind > 2:
                    self.row_r_06c.config(self.set_class_style(veh_r_06[4]))

            # Tyre compound index
            if self.wcfg["show_tyre_compound"]:
                self.row_plrm.config(text=self.set_tyre_cmp(veh_plr[8]))

                self.row_f_03m.config(text=self.set_tyre_cmp(veh_f_03[8]))
                self.row_f_02m.config(text=self.set_tyre_cmp(veh_f_02[8]))
                self.row_f_01m.config(text=self.set_tyre_cmp(veh_f_01[8]))
                self.row_r_01m.config(text=self.set_tyre_cmp(veh_r_01[8]))
                self.row_r_02m.config(text=self.set_tyre_cmp(veh_r_02[8]))
                self.row_r_03m.config(text=self.set_tyre_cmp(veh_r_03[8]))

                if self.rel_add_front > 0:
                    self.row_f_04m.config(text=self.set_tyre_cmp(veh_f_04[8]))
                if self.rel_add_behind > 0:
                    self.row_r_04m.config(text=self.set_tyre_cmp(veh_r_04[8]))
                if self.rel_add_front > 1:
                    self.row_f_05m.config(text=self.set_tyre_cmp(veh_f_05[8]))
                if self.rel_add_behind > 1:
                    self.row_r_05m.config(text=self.set_tyre_cmp(veh_r_05[8]))
                if self.rel_add_front > 2:
                    self.row_f_06m.config(text=self.set_tyre_cmp(veh_f_06[8]))
                if self.rel_add_behind > 2:
                    self.row_r_06m.config(text=self.set_tyre_cmp(veh_r_06[8]))

            # Time gap
            self.row_plrg.config(text=veh_plr[5])

            self.row_f_03g.config(text=veh_f_03[5], fg=self.color_lapdiff(veh_f_03[6], veh_plr[6]))
            self.row_f_02g.config(text=veh_f_02[5], fg=self.color_lapdiff(veh_f_02[6], veh_plr[6]))
            self.row_f_01g.config(text=veh_f_01[5], fg=self.color_lapdiff(veh_f_01[6], veh_plr[6]))
            self.row_r_01g.config(text=veh_r_01[5], fg=self.color_lapdiff(veh_r_01[6], veh_plr[6]))
            self.row_r_02g.config(text=veh_r_02[5], fg=self.color_lapdiff(veh_r_02[6], veh_plr[6]))
            self.row_r_03g.config(text=veh_r_03[5], fg=self.color_lapdiff(veh_r_03[6], veh_plr[6]))

            if self.rel_add_front > 0:
                self.row_f_04g.config(text=veh_f_04[5], fg=self.color_lapdiff(veh_f_04[6], veh_plr[6]))
            if self.rel_add_behind > 0:
                self.row_r_04g.config(text=veh_r_04[5], fg=self.color_lapdiff(veh_r_04[6], veh_plr[6]))
            if self.rel_add_front > 1:
                self.row_f_05g.config(text=veh_f_05[5], fg=self.color_lapdiff(veh_f_05[6], veh_plr[6]))
            if self.rel_add_behind > 1:
                self.row_r_05g.config(text=veh_r_05[5], fg=self.color_lapdiff(veh_r_05[6], veh_plr[6]))
            if self.rel_add_front > 2:
                self.row_f_06g.config(text=veh_f_06[5], fg=self.color_lapdiff(veh_f_06[6], veh_plr[6]))
            if self.rel_add_behind > 2:
                self.row_r_06g.config(text=veh_r_06[5], fg=self.color_lapdiff(veh_r_06[6], veh_plr[6]))

            # Vehicle in pit
            if self.wcfg["show_pit_status"]:
                self.row_plrs.config(self.set_pitstatus(veh_plr[7]))

                self.row_f_03s.config(self.set_pitstatus(veh_f_03[7]))
                self.row_f_02s.config(self.set_pitstatus(veh_f_02[7]))
                self.row_f_01s.config(self.set_pitstatus(veh_f_01[7]))
                self.row_r_01s.config(self.set_pitstatus(veh_r_01[7]))
                self.row_r_02s.config(self.set_pitstatus(veh_r_02[7]))
                self.row_r_03s.config(self.set_pitstatus(veh_r_03[7]))

                if self.rel_add_front > 0:
                    self.row_f_04s.config(self.set_pitstatus(veh_f_04[7]))
                if self.rel_add_behind > 0:
                    self.row_r_04s.config(self.set_pitstatus(veh_r_04[7]))
                if self.rel_add_front > 1:
                    self.row_f_05s.config(self.set_pitstatus(veh_f_05[7]))
                if self.rel_add_behind > 1:
                    self.row_r_05s.config(self.set_pitstatus(veh_r_05[7]))
                if self.rel_add_front > 2:
                    self.row_f_06s.config(self.set_pitstatus(veh_f_06[7]))
                if self.rel_add_behind > 2:
                    self.row_r_06s.config(self.set_pitstatus(veh_r_06[7]))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def color_lapdiff(self, nlap, player_nlap):
        """Compare lap differences & set color"""
        if nlap > player_nlap:
            color = self.wcfg["font_color_laps_ahead"]
        elif nlap < player_nlap:
            color = self.wcfg["font_color_laps_behind"]
        else:
            color = self.wcfg["font_color_same_lap"]
        return color

    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        if tc_index:
            ftire = self.wcfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
            rtire = self.wcfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
            tire_cmpd = f"{ftire}{rtire}"
        else:
            tire_cmpd = ""
        return tire_cmpd

    def set_pitstatus(self, pits):
        """Compare lap differences & set color"""
        if pits > 0:
            status = {"text":self.wcfg["pit_status_text"], "bg":self.wcfg["bkg_color_pit"]}
        else:
            status = {"text":"", "bg":self.cfg.overlay["transparent_color"]}
        return status

    def set_class_style(self, vehclass_name):
        """Compare vehicle class name with user defined dictionary"""
        if vehclass_name == "":
            class_config = {"text":"", "bg":self.wcfg["bkg_color_class"]}
        else:
            class_config = {"text":vehclass_name[:self.cls_width],
                            "bg":self.wcfg["bkg_color_class"]}

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
