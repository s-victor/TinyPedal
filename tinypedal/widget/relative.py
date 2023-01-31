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

        column_plc = self.wcfg["column_index_place"]
        column_drv = self.wcfg["column_index_driver"]
        column_lpt = self.wcfg["column_index_laptime"]
        column_pic = self.wcfg["column_index_position_in_class"]
        column_cls = self.wcfg["column_index_class"]
        column_tcp = self.wcfg["column_index_tyre_compound"]
        column_psc = self.wcfg["column_index_pitstop_count"]
        column_gap = self.wcfg["column_index_timegap"]
        column_pit = self.wcfg["column_index_pitstatus"]

        font_relative = tkfont.Font(family=self.wcfg["font_name"],
                                    size=-self.wcfg["font_size"],
                                    weight=self.wcfg["font_weight"])
        plr_row = 9  # set player row number

        # Max display players
        self.rel_add_front = min(max(self.wcfg["additional_players_front"], 0), 3)
        self.rel_add_behind = min(max(self.wcfg["additional_players_behind"], 0), 3)

        # Draw label
        # Driver place number
        bar_style_plc = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                         "height":1, "width":num_width, "fg":fg_color, "bg":self.wcfg['bkg_color_place']}

        self.row_plr_plc = tk.Label(self, bar_style_plc,
                                    fg=fg_color_plr, bg=self.wcfg["bkg_color_player_place"])
        self.row_plr_plc.grid(row=plr_row, column=column_plc, padx=0, pady=(0, bar_gap))

        self.generate_bar("plc", bar_style_plc, plr_row, column_plc, bar_gap)

        # Driver name
        bar_style_drv = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                         "font":font_relative, "height":1, "width":self.drv_width,
                         "fg":fg_color, "bg":self.wcfg['bkg_color_name'], "anchor":"w"}

        self.row_plr_drv = tk.Label(self, bar_style_drv,
                                    fg=fg_color_plr, bg=self.wcfg["bkg_color_player_name"])
        self.row_plr_drv.grid(row=plr_row, column=column_drv, padx=0, pady=(0, bar_gap))

        self.generate_bar("drv", bar_style_drv, plr_row, column_drv, bar_gap)

        # Time gap
        bar_style_gap = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                         "font":font_relative, "height":1, "width":gap_width,
                         "fg":fg_color, "bg":self.wcfg['bkg_color_gap'], "anchor":"e"}

        self.row_plr_gap = tk.Label(self, bar_style_gap,
                                    fg=fg_color_plr, bg=self.wcfg["bkg_color_player_gap"])
        self.row_plr_gap.grid(row=plr_row, column=column_gap, padx=0, pady=(0, bar_gap))

        self.generate_bar("gap", bar_style_gap, plr_row, column_gap, bar_gap)

        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            bar_style_lpt = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative, "height":1, "width":9,
                             "fg":self.wcfg['font_color_laptime'],
                             "bg":self.wcfg['bkg_color_laptime']}

            self.row_plr_lpt = tk.Label(self, bar_style_lpt,
                                        fg=fg_color_plr, bg=self.wcfg["bkg_color_player_laptime"])
            self.row_plr_lpt.grid(row=plr_row, column=column_lpt, padx=0, pady=(0, bar_gap))

            self.generate_bar("lpt", bar_style_lpt, plr_row, column_lpt, bar_gap)

        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_pic = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                             "height":1, "width":num_width,
                             "fg":self.wcfg['font_color_position_in_class'],
                             "bg":self.wcfg['bkg_color_position_in_class']}

            self.row_plr_pic = tk.Label(self, bar_style_pic)
            self.row_plr_pic.grid(row=plr_row, column=column_pic, padx=0, pady=(0, bar_gap))

            self.generate_bar("pic", bar_style_pic, plr_row, column_pic, bar_gap)

        # Vehicle class
        if self.wcfg["show_class"]:
            self.vehcls = VehicleClass()  # load VehicleClass setting
            bar_style_cls = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0, "font":font_relative,
                             "height":1, "width":self.cls_width,
                             "fg":self.wcfg['font_color_class'],
                             "bg":self.wcfg['bkg_color_class']}

            self.row_plr_cls = tk.Label(self, bar_style_cls)
            self.row_plr_cls.grid(row=plr_row, column=column_cls, padx=0, pady=(0, bar_gap))

            self.generate_bar("cls", bar_style_cls, plr_row, column_cls, bar_gap)

        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            bar_style_pit = {"text":text_def, "bd":0, "padx":0, "pady":0, "font":font_relative,
                             "height":1, "width":len(self.wcfg["pit_status_text"])+1,
                             "fg":self.wcfg['font_color_pit'],
                             "bg":self.wcfg['bkg_color_pit']}

            self.row_plr_pit = tk.Label(self, bar_style_pit)
            self.row_plr_pit.grid(row=plr_row, column=column_pit, padx=0, pady=(0, bar_gap))

            self.generate_bar("pit", bar_style_pit, plr_row, column_pit, bar_gap)

        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcp = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0, "font":font_relative,
                             "height":1, "width":2,
                             "fg":self.wcfg['font_color_tyre_compound'],
                             "bg":self.wcfg['bkg_color_tyre_compound']}

            self.row_plr_tcp = tk.Label(self, bar_style_tcp,
                                        fg=fg_color_plr, bg=self.wcfg["bkg_color_player_tyre_compound"])
            self.row_plr_tcp.grid(row=plr_row, column=column_tcp, padx=0, pady=(0, bar_gap))

            self.generate_bar("tcp", bar_style_tcp, plr_row, column_tcp, bar_gap)

        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            bar_style_psc = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0, "font":font_relative,
                             "height":1, "width":2,
                             "fg":self.wcfg['font_color_pitstop_count'],
                             "bg":self.wcfg['bkg_color_pitstop_count']}

            self.row_plr_psc = tk.Label(self, bar_style_psc,
                                        fg=fg_color_plr, bg=self.wcfg["bkg_color_player_pitstop_count"])
            self.row_plr_psc.grid(row=plr_row, column=column_psc, padx=0, pady=(0, bar_gap))

            self.generate_bar("psc", bar_style_psc, plr_row, column_psc, bar_gap)

        # Last vehicle data
        data_slots = 10
        self.last_veh_plr = [None] * data_slots
        self.last_veh_f_03 = [None] * data_slots
        self.last_veh_f_02 = [None] * data_slots
        self.last_veh_f_01 = [None] * data_slots
        self.last_veh_r_01 = [None] * data_slots
        self.last_veh_r_02 = [None] * data_slots
        self.last_veh_r_03 = [None] * data_slots
        if self.rel_add_front > 0:
            self.last_veh_f_04 = [None] * data_slots
        if self.rel_add_behind > 0:
            self.last_veh_r_04 = [None] * data_slots
        if self.rel_add_front > 1:
            self.last_veh_f_05 = [None] * data_slots
        if self.rel_add_behind > 1:
            self.last_veh_r_05 = [None] * data_slots
        if self.rel_add_front > 2:
            self.last_veh_f_06 = [None] * data_slots
        if self.rel_add_behind > 2:
            self.last_veh_r_06 = [None] * data_slots

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def generate_bar(self, suffix, style, row_idx, column_idx, bar_gap):
        """Generate data bar"""
        for idx in range(1,4):
            setattr(self, f"row_f_{idx:02.0f}_{suffix}", tk.Label(self, style))  # front row
            getattr(self, f"row_f_{idx:02.0f}_{suffix}").grid(
                row=row_idx - idx, column=column_idx, padx=0, pady=(0, bar_gap))

            setattr(self, f"row_r_{idx:02.0f}_{suffix}", tk.Label(self, style))  # rear row
            getattr(self, f"row_r_{idx:02.0f}_{suffix}").grid(
                row=row_idx + idx, column=column_idx, padx=0, pady=(0, bar_gap))

            if self.rel_add_front > (idx - 1):
                setattr(self, f"row_f_{idx+3:02.0f}_{suffix}", tk.Label(self, style))  # additional front row
                getattr(self, f"row_f_{idx+3:02.0f}_{suffix}").grid(
                    row=row_idx - idx - 3, column=column_idx, padx=0, pady=(0, bar_gap))

            if self.rel_add_behind > (idx - 1):
                setattr(self, f"row_r_{idx+3:02.0f}_{suffix}", tk.Label(self, style))  # additional rear row
                getattr(self, f"row_r_{idx+3:02.0f}_{suffix}").grid(
                    row=row_idx + idx + 3, column=column_idx, padx=0, pady=(0, bar_gap))

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
            self.update_plc("plr_plc", veh_plr[0], self.last_veh_plr[0])

            self.update_plc("f_03_plc", veh_f_03[0], self.last_veh_f_03[0], veh_f_03[6], veh_plr[6])
            self.update_plc("f_02_plc", veh_f_02[0], self.last_veh_f_02[0], veh_f_02[6], veh_plr[6])
            self.update_plc("f_01_plc", veh_f_01[0], self.last_veh_f_01[0], veh_f_01[6], veh_plr[6])
            self.update_plc("r_01_plc", veh_r_01[0], self.last_veh_r_01[0], veh_r_01[6], veh_plr[6])
            self.update_plc("r_02_plc", veh_r_02[0], self.last_veh_r_02[0], veh_r_02[6], veh_plr[6])
            self.update_plc("r_03_plc", veh_r_03[0], self.last_veh_r_03[0], veh_r_03[6], veh_plr[6])

            if self.rel_add_front > 0:
                self.update_plc("f_04_plc", veh_f_04[0], self.last_veh_f_04[0], veh_f_04[6], veh_plr[6])
            if self.rel_add_behind > 0:
                self.update_plc("r_04_plc", veh_r_04[0], self.last_veh_r_04[0], veh_r_04[6], veh_plr[6])
            if self.rel_add_front > 1:
                self.update_plc("f_05_plc", veh_f_05[0], self.last_veh_f_05[0], veh_f_05[6], veh_plr[6])
            if self.rel_add_behind > 1:
                self.update_plc("r_05_plc", veh_r_05[0], self.last_veh_r_05[0], veh_r_05[6], veh_plr[6])
            if self.rel_add_front > 2:
                self.update_plc("f_06_plc", veh_f_06[0], self.last_veh_f_06[0], veh_f_06[6], veh_plr[6])
            if self.rel_add_behind > 2:
                self.update_plc("r_06_plc", veh_r_06[0], self.last_veh_r_06[0], veh_r_06[6], veh_plr[6])

            # Driver name
            self.update_drv("plr_drv", veh_plr[1], self.last_veh_plr[1])

            self.update_drv("f_03_drv", veh_f_03[1], self.last_veh_f_03[1], veh_f_03[6], veh_plr[6])
            self.update_drv("f_02_drv", veh_f_02[1], self.last_veh_f_02[1], veh_f_02[6], veh_plr[6])
            self.update_drv("f_01_drv", veh_f_01[1], self.last_veh_f_01[1], veh_f_01[6], veh_plr[6])
            self.update_drv("r_01_drv", veh_r_01[1], self.last_veh_r_01[1], veh_r_01[6], veh_plr[6])
            self.update_drv("r_02_drv", veh_r_02[1], self.last_veh_r_02[1], veh_r_02[6], veh_plr[6])
            self.update_drv("r_03_drv", veh_r_03[1], self.last_veh_r_03[1], veh_r_03[6], veh_plr[6])

            if self.rel_add_front > 0:
                self.update_drv("f_04_drv", veh_f_04[1], self.last_veh_f_04[1], veh_f_04[6], veh_plr[6])
            if self.rel_add_behind > 0:
                self.update_drv("r_04_drv", veh_r_04[1], self.last_veh_r_04[1], veh_r_04[6], veh_plr[6])
            if self.rel_add_front > 1:
                self.update_drv("f_05_drv", veh_f_05[1], self.last_veh_f_05[1], veh_f_05[6], veh_plr[6])
            if self.rel_add_behind > 1:
                self.update_drv("r_05_drv", veh_r_05[1], self.last_veh_r_05[1], veh_r_05[6], veh_plr[6])
            if self.rel_add_front > 2:
                self.update_drv("f_06_drv", veh_f_06[1], self.last_veh_f_06[1], veh_f_06[6], veh_plr[6])
            if self.rel_add_behind > 2:
                self.update_drv("r_06_drv", veh_r_06[1], self.last_veh_r_06[1], veh_r_06[6], veh_plr[6])

            # Vehicle laptime
            if self.wcfg["show_laptime"]:
                self.update_lpt("plr_lpt", veh_plr[2], self.last_veh_plr[2])

                self.update_lpt("f_03_lpt", veh_f_03[2], self.last_veh_f_03[2])
                self.update_lpt("f_02_lpt", veh_f_02[2], self.last_veh_f_02[2])
                self.update_lpt("f_01_lpt", veh_f_01[2], self.last_veh_f_01[2])
                self.update_lpt("r_01_lpt", veh_r_01[2], self.last_veh_r_01[2])
                self.update_lpt("r_02_lpt", veh_r_02[2], self.last_veh_r_02[2])
                self.update_lpt("r_03_lpt", veh_r_03[2], self.last_veh_r_03[2])

                if self.rel_add_front > 0:
                    self.update_lpt("f_04_lpt", veh_f_04[2], self.last_veh_f_04[2])
                if self.rel_add_behind > 0:
                    self.update_lpt("r_04_lpt", veh_r_04[2], self.last_veh_r_04[2])
                if self.rel_add_front > 1:
                    self.update_lpt("f_05_lpt", veh_f_05[2], self.last_veh_f_05[2])
                if self.rel_add_behind > 1:
                    self.update_lpt("r_05_lpt", veh_r_05[2], self.last_veh_r_05[2])
                if self.rel_add_front > 2:
                    self.update_lpt("f_06_lpt", veh_f_06[2], self.last_veh_f_06[2])
                if self.rel_add_behind > 2:
                    self.update_lpt("r_06_lpt", veh_r_06[2], self.last_veh_r_06[2])

            # Vehicle position in class
            if self.wcfg["show_position_in_class"]:
                self.update_lpt("plr_pic", veh_plr[3], self.last_veh_plr[3])

                self.update_lpt("f_03_pic", veh_f_03[3], self.last_veh_f_03[3])
                self.update_lpt("f_02_pic", veh_f_02[3], self.last_veh_f_02[3])
                self.update_lpt("f_01_pic", veh_f_01[3], self.last_veh_f_01[3])
                self.update_lpt("r_01_pic", veh_r_01[3], self.last_veh_r_01[3])
                self.update_lpt("r_02_pic", veh_r_02[3], self.last_veh_r_02[3])
                self.update_lpt("r_03_pic", veh_r_03[3], self.last_veh_r_03[3])

                if self.rel_add_front > 0:
                    self.update_lpt("f_04_pic", veh_f_04[3], self.last_veh_f_04[3])
                if self.rel_add_behind > 0:
                    self.update_lpt("r_04_pic", veh_r_04[3], self.last_veh_r_04[3])
                if self.rel_add_front > 1:
                    self.update_lpt("f_05_pic", veh_f_05[3], self.last_veh_f_05[3])
                if self.rel_add_behind > 1:
                    self.update_lpt("r_05_pic", veh_r_05[3], self.last_veh_r_05[3])
                if self.rel_add_front > 2:
                    self.update_lpt("f_06_pic", veh_f_06[3], self.last_veh_f_06[3])
                if self.rel_add_behind > 2:
                    self.update_lpt("r_06_pic", veh_r_06[3], self.last_veh_r_06[3])

            # Vehicle class
            if self.wcfg["show_class"]:
                self.update_cls("plr_cls", veh_plr[4], self.last_veh_plr[4])

                self.update_cls("f_03_cls", veh_f_03[4], self.last_veh_f_03[4])
                self.update_cls("f_02_cls", veh_f_02[4], self.last_veh_f_02[4])
                self.update_cls("f_01_cls", veh_f_01[4], self.last_veh_f_01[4])
                self.update_cls("r_01_cls", veh_r_01[4], self.last_veh_r_01[4])
                self.update_cls("r_02_cls", veh_r_02[4], self.last_veh_r_02[4])
                self.update_cls("r_03_cls", veh_r_03[4], self.last_veh_r_03[4])

                if self.rel_add_front > 0:
                    self.update_cls("f_04_cls", veh_f_04[4], self.last_veh_f_04[4])
                if self.rel_add_behind > 0:
                    self.update_cls("r_04_cls", veh_r_04[4], self.last_veh_r_04[4])
                if self.rel_add_front > 1:
                    self.update_cls("f_05_cls", veh_f_05[4], self.last_veh_f_05[4])
                if self.rel_add_behind > 1:
                    self.update_cls("r_05_cls", veh_r_05[4], self.last_veh_r_05[4])
                if self.rel_add_front > 2:
                    self.update_cls("f_06_cls", veh_f_06[4], self.last_veh_f_06[4])
                if self.rel_add_behind > 2:
                    self.update_cls("r_06_cls", veh_r_06[4], self.last_veh_r_06[4])

            # Time gap
            self.update_plc("plr_gap", veh_plr[5], self.last_veh_plr[5])

            self.update_plc("f_03_gap", veh_f_03[5], self.last_veh_f_03[5], veh_f_03[6], veh_plr[6])
            self.update_plc("f_02_gap", veh_f_02[5], self.last_veh_f_02[5], veh_f_02[6], veh_plr[6])
            self.update_plc("f_01_gap", veh_f_01[5], self.last_veh_f_01[5], veh_f_01[6], veh_plr[6])
            self.update_plc("r_01_gap", veh_r_01[5], self.last_veh_r_01[5], veh_r_01[6], veh_plr[6])
            self.update_plc("r_02_gap", veh_r_02[5], self.last_veh_r_02[5], veh_r_02[6], veh_plr[6])
            self.update_plc("r_03_gap", veh_r_03[5], self.last_veh_r_03[5], veh_r_03[6], veh_plr[6])

            if self.rel_add_front > 0:
                self.update_plc("f_04_gap", veh_f_04[5], self.last_veh_f_04[5], veh_f_04[6], veh_plr[6])
            if self.rel_add_behind > 0:
                self.update_plc("r_04_gap", veh_r_04[5], self.last_veh_r_04[5], veh_r_04[6], veh_plr[6])
            if self.rel_add_front > 1:
                self.update_plc("f_05_gap", veh_f_05[5], self.last_veh_f_05[5], veh_f_05[6], veh_plr[6])
            if self.rel_add_behind > 1:
                self.update_plc("r_05_gap", veh_r_05[5], self.last_veh_r_05[5], veh_r_05[6], veh_plr[6])
            if self.rel_add_front > 2:
                self.update_plc("f_06_gap", veh_f_06[5], self.last_veh_f_06[5], veh_f_06[6], veh_plr[6])
            if self.rel_add_behind > 2:
                self.update_plc("r_06_gap", veh_r_06[5], self.last_veh_r_06[5], veh_r_06[6], veh_plr[6])

            # Vehicle in pit
            if self.wcfg["show_pit_status"]:
                self.update_pit("plr_pit", veh_plr[7], self.last_veh_plr[7])

                self.update_pit("f_03_pit", veh_f_03[7], self.last_veh_f_03[7])
                self.update_pit("f_02_pit", veh_f_02[7], self.last_veh_f_02[7])
                self.update_pit("f_01_pit", veh_f_01[7], self.last_veh_f_01[7])
                self.update_pit("r_01_pit", veh_r_01[7], self.last_veh_r_01[7])
                self.update_pit("r_02_pit", veh_r_02[7], self.last_veh_r_02[7])
                self.update_pit("r_03_pit", veh_r_03[7], self.last_veh_r_03[7])

                if self.rel_add_front > 0:
                    self.update_pit("f_04_pit", veh_f_04[7], self.last_veh_f_04[7])
                if self.rel_add_behind > 0:
                    self.update_pit("r_04_pit", veh_r_04[7], self.last_veh_r_04[7])
                if self.rel_add_front > 1:
                    self.update_pit("f_05_pit", veh_f_05[7], self.last_veh_f_05[7])
                if self.rel_add_behind > 1:
                    self.update_pit("r_05_pit", veh_r_05[7], self.last_veh_r_05[7])
                if self.rel_add_front > 2:
                    self.update_pit("f_06_pit", veh_f_06[7], self.last_veh_f_06[7])
                if self.rel_add_behind > 2:
                    self.update_pit("r_06_pit", veh_r_06[7], self.last_veh_r_06[7])

            # Tyre compound index
            if self.wcfg["show_tyre_compound"]:
                self.update_tcp("plr_tcp", veh_plr[8], self.last_veh_plr[8])

                self.update_tcp("f_03_tcp", veh_f_03[8], self.last_veh_f_03[8])
                self.update_tcp("f_02_tcp", veh_f_02[8], self.last_veh_f_02[8])
                self.update_tcp("f_01_tcp", veh_f_01[8], self.last_veh_f_01[8])
                self.update_tcp("r_01_tcp", veh_r_01[8], self.last_veh_r_01[8])
                self.update_tcp("r_02_tcp", veh_r_02[8], self.last_veh_r_02[8])
                self.update_tcp("r_03_tcp", veh_r_03[8], self.last_veh_r_03[8])

                if self.rel_add_front > 0:
                    self.update_tcp("f_04_tcp", veh_f_04[8], self.last_veh_f_04[8])
                if self.rel_add_behind > 0:
                    self.update_tcp("r_04_tcp", veh_r_04[8], self.last_veh_r_04[8])
                if self.rel_add_front > 1:
                    self.update_tcp("f_05_tcp", veh_f_05[8], self.last_veh_f_05[8])
                if self.rel_add_behind > 1:
                    self.update_tcp("r_05_tcp", veh_r_05[8], self.last_veh_r_05[8])
                if self.rel_add_front > 2:
                    self.update_tcp("f_06_tcp", veh_f_06[8], self.last_veh_f_06[8])
                if self.rel_add_behind > 2:
                    self.update_tcp("r_06_tcp", veh_r_06[8], self.last_veh_r_06[8])

            # Pitstop count
            if self.wcfg["show_pitstop_count"]:
                self.update_psc("plr_psc", veh_plr[9], self.last_veh_plr[9])

                self.update_psc("f_03_psc", veh_f_03[9], self.last_veh_f_03[9])
                self.update_psc("f_02_psc", veh_f_02[9], self.last_veh_f_02[9])
                self.update_psc("f_01_psc", veh_f_01[9], self.last_veh_f_01[9])
                self.update_psc("r_01_psc", veh_r_01[9], self.last_veh_r_01[9])
                self.update_psc("r_02_psc", veh_r_02[9], self.last_veh_r_02[9])
                self.update_psc("r_03_psc", veh_r_03[9], self.last_veh_r_03[9])

                if self.rel_add_front > 0:
                    self.update_psc("f_04_psc", veh_f_04[9], self.last_veh_f_04[9])
                if self.rel_add_behind > 0:
                    self.update_psc("r_04_psc", veh_r_04[9], self.last_veh_r_04[9])
                if self.rel_add_front > 1:
                    self.update_psc("f_05_psc", veh_f_05[9], self.last_veh_f_05[9])
                if self.rel_add_behind > 1:
                    self.update_psc("r_05_psc", veh_r_05[9], self.last_veh_r_05[9])
                if self.rel_add_front > 2:
                    self.update_psc("f_06_psc", veh_f_06[9], self.last_veh_f_06[9])
                if self.rel_add_behind > 2:
                    self.update_psc("r_06_psc", veh_r_06[9], self.last_veh_r_06[9])

            # Store last vehicle data reading for comparison
            self.last_veh_plr = veh_plr
            self.last_veh_f_03 = veh_f_03
            self.last_veh_f_02 = veh_f_02
            self.last_veh_f_01 = veh_f_01
            self.last_veh_r_01 = veh_r_01
            self.last_veh_r_02 = veh_r_02
            self.last_veh_r_03 = veh_r_03
            if self.rel_add_front > 0:
                self.last_veh_f_04 = veh_f_04
            if self.rel_add_behind > 0:
                self.last_veh_r_04 = veh_r_04
            if self.rel_add_front > 1:
                self.last_veh_f_05 = veh_f_05
            if self.rel_add_behind > 1:
                self.last_veh_r_05 = veh_r_05
            if self.rel_add_front > 2:
                self.last_veh_f_06 = veh_f_06
            if self.rel_add_behind > 2:
                self.last_veh_r_06 = veh_r_06

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Lazy GUI update methods
    def update_plc(self, suffix, curr, last, extra1=None, extra2=None):
        """Driver place & Time gap"""
        if curr != last:
            if extra1:
                getattr(self, f"row_{suffix}").config(text=curr, fg=self.color_lapdiff(extra1, extra2))
            else:
                getattr(self, f"row_{suffix}").config(text=curr)

    def update_drv(self, suffix, curr, last, extra1=None, extra2=None):
        """Driver name"""
        if curr != last:
            if extra1:
                getattr(self, f"row_{suffix}").config(
                    text=self.set_driver_name(curr)[:self.drv_width], fg=self.color_lapdiff(extra1, extra2))
            else:
                getattr(self, f"row_{suffix}").config(
                    text=self.set_driver_name(curr)[:self.drv_width])

    def update_lpt(self, suffix, curr, last):
        """Vehicle laptime & Vehicle position in class"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(text=curr)

    def update_cls(self, suffix, curr, last):
        """Vehicle class"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(self.set_class_style(curr))

    def update_pit(self, suffix, curr, last):
        """Vehicle in pit"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(self.set_pitstatus(curr))

    def update_tcp(self, suffix, curr, last):
        """Tyre compound index"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(text=self.set_tyre_cmp(curr))

    def update_psc(self, suffix, curr, last):
        """Pitstop count"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(text=self.set_pitcount(curr))

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

    def set_driver_name(self, name):
        """Set driver name"""
        if self.wcfg["driver_name_mode"] == 0:
            text = name[0]
        else:
            text = name[1]
        return text

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
        """Set pit status color"""
        if pits > 0:
            status = {"text":self.wcfg["pit_status_text"], "bg":self.wcfg["bkg_color_pit"]}
        else:
            status = {"text":"", "bg":self.cfg.overlay["transparent_color"]}
        return status

    @staticmethod
    def set_pitcount(pits):
        """Set pitstop count test"""
        if pits < 0:
            count = ""
        elif pits == 0:
            count = "-"
        else:
            count = pits
        return count

    def set_class_style(self, vehclass_name):
        """Compare vehicle class name with user defined dictionary"""
        if vehclass_name == "":
            class_setting = {"text":"", "bg":self.wcfg["bkg_color_class"]}
        else:
            class_setting = {"text":vehclass_name[:self.cls_width],
                             "bg":self.wcfg["bkg_color_class"]}

        for key, value in self.vehcls.classdict_user.items():
            # If class name matches user defined class
            if vehclass_name == key:
                # Assign new class name from user defined value
                short_name = value
                for subkey, subvalue in short_name.items():
                    # Assign corresponding background color
                    class_setting = {"text":subkey, "bg":subvalue}
                    break

        return class_setting
