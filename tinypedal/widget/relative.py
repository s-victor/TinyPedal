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

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]
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

        # Max display players
        self.veh_add_front = min(max(self.wcfg["additional_players_front"], 0), 60)
        self.veh_add_behind = min(max(self.wcfg["additional_players_behind"], 0), 60)
        self.veh_range = max(4, self.veh_add_front + 4, self.veh_add_behind + 4)
        plr_row = self.veh_add_front + 3  # set player row number

        # Draw label
        # Driver place number
        bar_style_plc = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0, "font":font_relative,
                         "height":1, "width":2, "fg":fg_color, "bg":self.wcfg['bkg_color_place']}

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
                             "font":font_relative, "height":1, "width":8,
                             "fg":self.wcfg['font_color_laptime'],
                             "bg":self.wcfg['bkg_color_laptime']}

            self.row_plr_lpt = tk.Label(self, bar_style_lpt,
                                        fg=fg_color_plr,
                                        bg=self.wcfg["bkg_color_player_laptime"])
            self.row_plr_lpt.grid(row=plr_row, column=column_lpt, padx=0, pady=(0, bar_gap))

            self.generate_bar("lpt", bar_style_lpt, plr_row, column_lpt, bar_gap)

        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_pic = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative, "height":1, "width":2,
                             "fg":self.wcfg['font_color_position_in_class'],
                             "bg":self.wcfg['bkg_color_position_in_class']}

            self.row_plr_pic = tk.Label(self, bar_style_pic)
            self.row_plr_pic.grid(row=plr_row, column=column_pic, padx=0, pady=(0, bar_gap))

            self.generate_bar("pic", bar_style_pic, plr_row, column_pic, bar_gap)

        # Vehicle class
        if self.wcfg["show_class"]:
            self.vehcls = VehicleClass()  # load VehicleClass setting
            bar_style_cls = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative, "height":1, "width":self.cls_width,
                             "fg":self.wcfg['font_color_class'],
                             "bg":self.wcfg['bkg_color_class']}

            self.row_plr_cls = tk.Label(self, bar_style_cls)
            self.row_plr_cls.grid(row=plr_row, column=column_cls, padx=0, pady=(0, bar_gap))

            self.generate_bar("cls", bar_style_cls, plr_row, column_cls, bar_gap)

        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            bar_style_pit = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative,
                             "height":1, "width":len(self.wcfg["pit_status_text"]),
                             "fg":self.wcfg['font_color_pit'],
                             "bg":self.wcfg['bkg_color_pit']}

            self.row_plr_pit = tk.Label(self, bar_style_pit)
            self.row_plr_pit.grid(row=plr_row, column=column_pit, padx=0, pady=(0, bar_gap))

            self.generate_bar("pit", bar_style_pit, plr_row, column_pit, bar_gap)

        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcp = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative, "height":1, "width":2,
                             "fg":self.wcfg['font_color_tyre_compound'],
                             "bg":self.wcfg['bkg_color_tyre_compound']}

            self.row_plr_tcp = tk.Label(self, bar_style_tcp,
                                        fg=fg_color_plr,
                                        bg=self.wcfg["bkg_color_player_tyre_compound"])
            self.row_plr_tcp.grid(row=plr_row, column=column_tcp, padx=0, pady=(0, bar_gap))

            self.generate_bar("tcp", bar_style_tcp, plr_row, column_tcp, bar_gap)

        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            bar_style_psc = {"text":text_def, "bd":0, "padx":bar_padx, "pady":0,
                             "font":font_relative, "height":1, "width":2,
                             "fg":self.wcfg['font_color_pitstop_count'],
                             "bg":self.wcfg['bkg_color_pitstop_count']}

            self.row_plr_psc = tk.Label(self, bar_style_psc,
                                        fg=fg_color_plr,
                                        bg=self.wcfg["bkg_color_player_pitstop_count"])
            self.row_plr_psc.grid(row=plr_row, column=column_psc, padx=0, pady=(0, bar_gap))

            self.generate_bar("psc", bar_style_psc, plr_row, column_psc, bar_gap)

        # Last data
        data_slots = 10
        self.last_veh_plr = [None] * data_slots

        for idx in range(1, self.veh_range):
            if idx < self.veh_add_front + 4:
                setattr(self, f"last_veh_f_{idx}", [None] * data_slots)

            if idx < self.veh_add_behind + 4:
                setattr(self, f"last_veh_r_{idx}", [None] * data_slots)

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def generate_bar(self, suffix, style, row_idx, column_idx, bar_gap):
        """Generate data bar"""
        for idx in range(1, self.veh_range):
            if idx < self.veh_add_front + 4:
                setattr(self, f"row_f_{idx}_{suffix}", tk.Label(self, style))  # front row
                getattr(self, f"row_f_{idx}_{suffix}").grid(
                    row=row_idx - idx, column=column_idx, padx=0, pady=(0, bar_gap))

            if idx < self.veh_add_behind + 4:
                setattr(self, f"row_r_{idx}_{suffix}", tk.Label(self, style))  # rear row
                getattr(self, f"row_r_{idx}_{suffix}").grid(
                    row=row_idx + idx, column=column_idx, padx=0, pady=(0, bar_gap))

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and module.relative_info.relative_list and self.wcfg["enable"]:

            # Read relative data
            rel_idx, cls_info, plr_idx = module.relative_info.relative_list
            veh_center = int(3 + self.veh_add_front)

            # Data index reference:
            # 0 place, 1 driver, 2 laptime, 3 pos_class, 4 veh_class,
            # 5 time_gap, 6 num_lap, 7 in_pit, 8 tire_idx, 9 pit_count
            veh_plr = module.relative_info.relative_data(plr_idx, plr_idx, cls_info)

            # Set opponent vehicle data: veh_f_**
            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    setattr(self, f"veh_f_{idx}",
                            module.relative_info.relative_data(
                                rel_idx[veh_center - idx], plr_idx, cls_info)
                            )
                if idx < self.veh_add_behind + 4:
                    setattr(self, f"veh_r_{idx}",
                            module.relative_info.relative_data(
                                rel_idx[veh_center + idx], plr_idx, cls_info)
                            )

            # Relative update

            # Driver place
            self.update_plc("plr_plc", veh_plr[0], self.last_veh_plr[0], opt=False)

            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    self.update_plc(f"f_{idx}_plc",
                                    getattr(self, f"veh_f_{idx}")[0],
                                    getattr(self, f"last_veh_f_{idx}")[0]
                                    )
                if idx < self.veh_add_behind + 4:
                    self.update_plc(f"r_{idx}_plc",
                                    getattr(self, f"veh_r_{idx}")[0],
                                    getattr(self, f"last_veh_r_{idx}")[0]
                                    )

            # Driver name
            self.update_drv("plr_drv", veh_plr[1], self.last_veh_plr[1], opt=False)

            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    self.update_drv(f"f_{idx}_drv",
                                    getattr(self, f"veh_f_{idx}")[1],
                                    getattr(self, f"last_veh_f_{idx}")[1]
                                    )
                if idx < self.veh_add_behind + 4:
                    self.update_drv(f"r_{idx}_drv",
                                    getattr(self, f"veh_r_{idx}")[1],
                                    getattr(self, f"last_veh_r_{idx}")[1]
                                    )

            # Vehicle laptime
            if self.wcfg["show_laptime"]:
                self.update_lpt("plr_lpt", veh_plr[2], self.last_veh_plr[2])

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_lpt(f"f_{idx}_lpt",
                                        getattr(self, f"veh_f_{idx}")[2],
                                        getattr(self, f"last_veh_f_{idx}")[2]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_lpt(f"r_{idx}_lpt",
                                        getattr(self, f"veh_r_{idx}")[2],
                                        getattr(self, f"last_veh_r_{idx}")[2]
                                        )

            # Vehicle position in class
            if self.wcfg["show_position_in_class"]:
                self.update_pic("plr_pic", veh_plr[3], self.last_veh_plr[3])

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_pic(f"f_{idx}_pic",
                                        getattr(self, f"veh_f_{idx}")[3],
                                        getattr(self, f"last_veh_f_{idx}")[3]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_pic(f"r_{idx}_pic",
                                        getattr(self, f"veh_r_{idx}")[3],
                                        getattr(self, f"last_veh_r_{idx}")[3]
                                        )

            # Vehicle class
            if self.wcfg["show_class"]:
                self.update_cls("plr_cls", veh_plr[4], self.last_veh_plr[4])

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_cls(f"f_{idx}_cls",
                                        getattr(self, f"veh_f_{idx}")[4],
                                        getattr(self, f"last_veh_f_{idx}")[4]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_cls(f"r_{idx}_cls",
                                        getattr(self, f"veh_r_{idx}")[4],
                                        getattr(self, f"last_veh_r_{idx}")[4]
                                        )

            # Time gap
            self.update_plc("plr_gap", veh_plr[5], self.last_veh_plr[5], opt=False)

            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    self.update_plc(f"f_{idx}_gap",
                                    getattr(self, f"veh_f_{idx}")[5],
                                    getattr(self, f"last_veh_f_{idx}")[5]
                                    )
                if idx < self.veh_add_behind + 4:
                    self.update_plc(f"r_{idx}_gap",
                                    getattr(self, f"veh_r_{idx}")[5],
                                    getattr(self, f"last_veh_r_{idx}")[5]
                                    )

            # Vehicle in pit
            if self.wcfg["show_pit_status"]:
                self.update_pit("plr_pit", veh_plr[7], self.last_veh_plr[7])

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_pit(f"f_{idx}_pit",
                                        getattr(self, f"veh_f_{idx}")[7],
                                        getattr(self, f"last_veh_f_{idx}")[7]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_pit(f"r_{idx}_pit",
                                        getattr(self, f"veh_r_{idx}")[7],
                                        getattr(self, f"last_veh_r_{idx}")[7]
                                        )

            # Tyre compound index
            if self.wcfg["show_tyre_compound"]:
                self.update_tcp("plr_tcp", veh_plr[8], self.last_veh_plr[8])

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_tcp(f"f_{idx}_tcp",
                                        getattr(self, f"veh_f_{idx}")[8],
                                        getattr(self, f"last_veh_f_{idx}")[8]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_tcp(f"r_{idx}_tcp",
                                        getattr(self, f"veh_r_{idx}")[8],
                                        getattr(self, f"last_veh_r_{idx}")[8]
                                        )

            # Pitstop count
            if self.wcfg["show_pitstop_count"]:
                self.update_psc("plr_psc", veh_plr[9], self.last_veh_plr[9], True)

                for idx in range(1, self.veh_range):
                    if idx < self.veh_add_front + 4:
                        self.update_psc(f"f_{idx}_psc",
                                        getattr(self, f"veh_f_{idx}")[9],
                                        getattr(self, f"last_veh_f_{idx}")[9]
                                        )
                    if idx < self.veh_add_behind + 4:
                        self.update_psc(f"r_{idx}_psc",
                                        getattr(self, f"veh_r_{idx}")[9],
                                        getattr(self, f"last_veh_r_{idx}")[9]
                                        )

            # Store last data reading
            self.last_veh_plr = veh_plr

            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    setattr(self, f"last_veh_f_{idx}",
                            getattr(self, f"veh_f_{idx}"))

                if idx < self.veh_add_behind + 4:
                    setattr(self, f"last_veh_r_{idx}",
                            getattr(self, f"veh_r_{idx}"))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_plc(self, suffix, curr, last, opt=True):
        """Driver place & Time gap"""
        if curr != last:
            if opt:
                color = self.color_lapdiff(curr[1])
            else:
                color = self.wcfg["font_color_player"]
            getattr(self, f"row_{suffix}").config(text=curr[0], fg=color)

    def update_drv(self, suffix, curr, last, opt=True):
        """Driver & vehicle name"""
        if curr != last:
            if opt:
                color = self.color_lapdiff(curr[2])
            else:
                color = self.wcfg["font_color_player"]
            getattr(self, f"row_{suffix}").config(
                text=self.set_driver_name(curr[0:2])[:self.drv_width], fg=color)

    def update_lpt(self, suffix, curr, last):
        """Vehicle laptime"""
        if curr != last:
            getattr(self, f"row_{suffix}").config(text=curr)

    def update_pic(self, suffix, curr, last):
        """Vehicle position in class"""
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

    def update_psc(self, suffix, curr, last, plr=False):
        """Pitstop count"""
        if curr != last:
            if self.wcfg["show_pit_request"] and curr[1] == 1:
                color = {"fg":self.wcfg["font_color_pit_request"],
                         "bg":self.wcfg["bkg_color_pit_request"]}
            elif plr:
                color = {"fg":self.wcfg["font_color_player"],
                         "bg":self.wcfg["bkg_color_player_pitstop_count"]}
            else:
                color = {"fg":self.wcfg["font_color_pitstop_count"],
                         "bg":self.wcfg["bkg_color_pitstop_count"]}

            getattr(self, f"row_{suffix}").config(color, text=self.set_pitcount(curr[0]))

    # Additional methods
    def color_lapdiff(self, is_lapped):
        """Compare lap differences & set color"""
        if is_lapped > 0:
            return self.wcfg["font_color_laps_ahead"]
        if is_lapped < 0:
            return self.wcfg["font_color_laps_behind"]
        return self.wcfg["font_color_same_lap"]

    def set_driver_name(self, name):
        """Set driver name"""
        if self.wcfg["driver_name_mode"] == 0:
            return name[0]  # driver name
        if self.wcfg["driver_name_mode"] == 1:
            return name[1]  # vehicle name
        if name[1]:
            return f"{name[0]} [{name[1]}]"  # combined name
        return ""

    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        if tc_index:
            ftire = self.wcfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
            rtire = self.wcfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
            return f"{ftire}{rtire}"
        return ""

    def set_pitstatus(self, pits):
        """Set pit status color"""
        if pits > 0:
            return {"text":self.wcfg["pit_status_text"], "bg":self.wcfg["bkg_color_pit"]}
        return {"text":"", "bg":self.cfg.overlay["transparent_color"]}

    @staticmethod
    def set_pitcount(pits):
        """Set pitstop count test"""
        if pits == 0:
            return "-"
        if pits > 0:
            return pits
        return ""

    def set_class_style(self, vehclass_name):
        """Compare vehicle class name with user defined dictionary"""
        if not vehclass_name:
            return {"text":"", "bg":self.wcfg["bkg_color_class"]}

        for full_name, short_name in self.vehcls.classdict_user.items():
            if vehclass_name == full_name:
                for sub_name, sub_color in short_name.items():
                    return {"text":sub_name, "bg":sub_color}

        return {"text":vehclass_name[:self.cls_width], "bg":self.wcfg["bkg_color_class"]}
