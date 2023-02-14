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
Tyre temperature Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent

WIDGET_NAME = "temperature"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]
        inner_gap = self.wcfg["inner_gap"]
        bar_width = 4 if self.wcfg["show_degree_sign"] else 3

        # Config style & variable
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3)
        font_temp = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        column_stemp = self.wcfg["column_index_surface"]
        column_itemp = self.wcfg["column_index_innerlayer"]

        # Draw label
        frame_stemp = tk.Frame(self, bd=0, highlightthickness=0,
                               bg=self.cfg.overlay["transparent_color"])
        frame_itemp = tk.Frame(self, bd=0, highlightthickness=0,
                               bg=self.cfg.overlay["transparent_color"])
        bar_style_stemp = {"text":"n/a", "bd":0, "height":1, "width":bar_width,
                           "padx":bar_padx, "pady":0, "font":font_temp,
                           "fg":self.wcfg["font_color_surface"],
                           "bg":self.wcfg["bkg_color_surface"]}
        bar_style_itemp = {"text":"n/a", "bd":0, "height":1, "width":bar_width,
                           "padx":bar_padx, "pady":0, "font":font_temp,
                           "fg":self.wcfg["font_color_innerlayer"],
                           "bg":self.wcfg["bkg_color_innerlayer"]}

        if self.wcfg["show_tyre_compound"]:
            bar_style_tcmpd = {"text":"-", "bd":0, "height":1, "width":1,
                               "padx":bar_padx, "pady":0, "font":font_temp,
                               "fg":self.wcfg["font_color_tyre_compound"],
                               "bg":self.wcfg["bkg_color_tyre_compound"]}
            self.bar_tcmpd_f = tk.Label(frame_stemp, bar_style_tcmpd)
            self.bar_tcmpd_f.grid(row=0, column=4, padx=(0,inner_gap), pady=(0,inner_gap))
            self.bar_tcmpd_r = tk.Label(frame_stemp, bar_style_tcmpd)
            self.bar_tcmpd_r.grid(row=1, column=4, padx=(0,inner_gap), pady=0)
            bar_phold1 = tk.Label(frame_itemp, bar_style_tcmpd, text="")
            bar_phold1.grid(row=0, column=4, padx=(0,inner_gap), pady=(0,inner_gap))
            bar_phold2 = tk.Label(frame_itemp, bar_style_tcmpd, text="")
            bar_phold2.grid(row=1, column=4, padx=(0,inner_gap), pady=0)

        if self.wcfg["ICO_mode"]:
            self.bar_stemp_fl_i = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fl_c = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fl_o = tk.Label(frame_stemp, bar_style_stemp)

            self.bar_stemp_fr_i = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fr_c = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fr_o = tk.Label(frame_stemp, bar_style_stemp)

            self.bar_stemp_rl_i = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rl_c = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rl_o = tk.Label(frame_stemp, bar_style_stemp)

            self.bar_stemp_rr_i = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rr_c = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rr_o = tk.Label(frame_stemp, bar_style_stemp)

            self.bar_stemp_fl_i.grid(row=0, column=2, padx=(0,inner_gap), pady=(0,inner_gap))
            self.bar_stemp_fl_c.grid(row=0, column=1, padx=(0,inner_gap), pady=(0,inner_gap))
            self.bar_stemp_fl_o.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))

            self.bar_stemp_fr_i.grid(row=0, column=7, padx=0, pady=(0,inner_gap))
            self.bar_stemp_fr_c.grid(row=0, column=8, padx=(inner_gap,0), pady=(0,inner_gap))
            self.bar_stemp_fr_o.grid(row=0, column=9, padx=(inner_gap,0), pady=(0,inner_gap))

            self.bar_stemp_rl_i.grid(row=1, column=2, padx=(0,inner_gap), pady=0)
            self.bar_stemp_rl_c.grid(row=1, column=1, padx=(0,inner_gap), pady=0)
            self.bar_stemp_rl_o.grid(row=1, column=0, padx=(0,inner_gap), pady=0)

            self.bar_stemp_rr_i.grid(row=1, column=7, padx=0, pady=0)
            self.bar_stemp_rr_c.grid(row=1, column=8, padx=(inner_gap,0), pady=0)
            self.bar_stemp_rr_o.grid(row=1, column=9, padx=(inner_gap,0), pady=0)

            if self.wcfg["show_innerlayer"]:
                self.bar_itemp_fl_i = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fl_c = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fl_o = tk.Label(frame_itemp, bar_style_itemp)

                self.bar_itemp_fr_i = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fr_c = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fr_o = tk.Label(frame_itemp, bar_style_itemp)

                self.bar_itemp_rl_i = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rl_c = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rl_o = tk.Label(frame_itemp, bar_style_itemp)

                self.bar_itemp_rr_i = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rr_c = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rr_o = tk.Label(frame_itemp, bar_style_itemp)

                self.bar_itemp_fl_i.grid(row=0, column=2, padx=(0,inner_gap), pady=(0,inner_gap))
                self.bar_itemp_fl_c.grid(row=0, column=1, padx=(0,inner_gap), pady=(0,inner_gap))
                self.bar_itemp_fl_o.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))

                self.bar_itemp_fr_i.grid(row=0, column=7, padx=0, pady=(0,inner_gap))
                self.bar_itemp_fr_c.grid(row=0, column=8, padx=(inner_gap,0), pady=(0,inner_gap))
                self.bar_itemp_fr_o.grid(row=0, column=9, padx=(inner_gap,0), pady=(0,inner_gap))

                self.bar_itemp_rl_i.grid(row=1, column=2, padx=(0,inner_gap), pady=0)
                self.bar_itemp_rl_c.grid(row=1, column=1, padx=(0,inner_gap), pady=0)
                self.bar_itemp_rl_o.grid(row=1, column=0, padx=(0,inner_gap), pady=0)

                self.bar_itemp_rr_i.grid(row=1, column=7, padx=0, pady=0)
                self.bar_itemp_rr_c.grid(row=1, column=8, padx=(inner_gap,0), pady=0)
                self.bar_itemp_rr_o.grid(row=1, column=9, padx=(inner_gap,0), pady=0)

        else:
            self.bar_stemp_fl = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fr = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rl = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_rr = tk.Label(frame_stemp, bar_style_stemp)
            self.bar_stemp_fl.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))
            self.bar_stemp_fr.grid(row=0, column=9, padx=0, pady=(0,inner_gap))
            self.bar_stemp_rl.grid(row=1, column=0, padx=(0,inner_gap), pady=0)
            self.bar_stemp_rr.grid(row=1, column=9, padx=0, pady=0)

            if self.wcfg["show_innerlayer"]:
                self.bar_itemp_fl = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fr = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rl = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_rr = tk.Label(frame_itemp, bar_style_itemp)
                self.bar_itemp_fl.grid(row=0, column=0, padx=(0,inner_gap), pady=(0,inner_gap))
                self.bar_itemp_fr.grid(row=0, column=9, padx=0, pady=(0,inner_gap))
                self.bar_itemp_rl.grid(row=1, column=0, padx=(0,inner_gap), pady=0)
                self.bar_itemp_rr.grid(row=1, column=9, padx=0, pady=0)

        if self.wcfg["layout"] == "0":
            # Vertical layout
            frame_stemp.grid(row=column_stemp, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_innerlayer"]:
                frame_itemp.grid(row=column_itemp, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            frame_stemp.grid(row=0, column=column_stemp, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_innerlayer"]:
                frame_itemp.grid(row=0, column=column_itemp, padx=(0,bar_gap), pady=0)

        # Last data
        self.last_tcmpd = [None] * 2
        if self.wcfg["ICO_mode"]:
            self.last_stemp = [[None] * 3] * 4
            self.last_itemp = [[None] * 3] * 4
        else:
            self.last_stemp = [None] * 4
            self.last_itemp = [None] * 4

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read tyre surface & inner temperature data
            stemp = tuple(map(self.temp_mode, read_data.tyre_temp_surface()))
            tcmpd = self.set_tyre_cmp(read_data.tyre_compound())

            if self.wcfg["show_tyre_compound"]:
                self.update_tcmpd(tcmpd, self.last_tcmpd)
                self.last_tcmpd = tcmpd

            # Inner, center, outer mode
            if self.wcfg["ICO_mode"]:
                # Surface temperature
                self.update_temp("stemp_fl_i", stemp[0][2], self.last_stemp[0][2])
                self.update_temp("stemp_fl_c", stemp[0][1], self.last_stemp[0][1])
                self.update_temp("stemp_fl_o", stemp[0][0], self.last_stemp[0][0])
                self.update_temp("stemp_fr_i", stemp[1][0], self.last_stemp[1][0])
                self.update_temp("stemp_fr_c", stemp[1][1], self.last_stemp[1][1])
                self.update_temp("stemp_fr_o", stemp[1][2], self.last_stemp[1][2])

                self.update_temp("stemp_rl_i", stemp[2][2], self.last_stemp[2][2])
                self.update_temp("stemp_rl_c", stemp[2][1], self.last_stemp[2][1])
                self.update_temp("stemp_rl_o", stemp[2][0], self.last_stemp[2][0])
                self.update_temp("stemp_rr_i", stemp[3][0], self.last_stemp[3][0])
                self.update_temp("stemp_rr_c", stemp[3][1], self.last_stemp[3][1])
                self.update_temp("stemp_rr_o", stemp[3][2], self.last_stemp[3][2])
                self.last_stemp = stemp

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = tuple(map(self.temp_mode, read_data.tyre_temp_innerlayer()))
                    self.update_temp("itemp_fl_i", itemp[0][2], self.last_itemp[0][2])
                    self.update_temp("itemp_fl_c", itemp[0][1], self.last_itemp[0][1])
                    self.update_temp("itemp_fl_o", itemp[0][0], self.last_itemp[0][0])
                    self.update_temp("itemp_fr_i", itemp[1][0], self.last_itemp[1][0])
                    self.update_temp("itemp_fr_c", itemp[1][1], self.last_itemp[1][1])
                    self.update_temp("itemp_fr_o", itemp[1][2], self.last_itemp[1][2])

                    self.update_temp("itemp_rl_i", itemp[2][2], self.last_itemp[2][2])
                    self.update_temp("itemp_rl_c", itemp[2][1], self.last_itemp[2][1])
                    self.update_temp("itemp_rl_o", itemp[2][0], self.last_itemp[2][0])
                    self.update_temp("itemp_rr_i", itemp[3][0], self.last_itemp[3][0])
                    self.update_temp("itemp_rr_c", itemp[3][1], self.last_itemp[3][1])
                    self.update_temp("itemp_rr_o", itemp[3][2], self.last_itemp[3][2])
                    self.last_itemp = itemp
            # Average mode
            else:
                # Surface temperature
                self.update_temp("stemp_fl", stemp[0], self.last_stemp[0])
                self.update_temp("stemp_fr", stemp[1], self.last_stemp[1])
                self.update_temp("stemp_rl", stemp[2], self.last_stemp[2])
                self.update_temp("stemp_rr", stemp[3], self.last_stemp[3])
                self.last_stemp = stemp

                # Inner layer temperature
                if self.wcfg["show_innerlayer"]:
                    itemp = tuple(map(self.temp_mode, read_data.tyre_temp_innerlayer()))
                    self.update_temp("itemp_fl", itemp[0], self.last_itemp[0])
                    self.update_temp("itemp_fr", itemp[1], self.last_itemp[1])
                    self.update_temp("itemp_rl", itemp[2], self.last_itemp[2])
                    self.update_temp("itemp_rr", itemp[3], self.last_itemp[3])
                    self.last_itemp = itemp

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_temp(self, suffix, curr, last):
        """Tyre temperature"""
        if curr != last:
            if self.wcfg["color_swap_temperature"] == "0":
                stemp_color = {"fg":self.color_heatmap(curr)}
            else:
                stemp_color = {"bg":self.color_heatmap(curr)}

            sign = "°" if self.wcfg["show_degree_sign"] else ""

            getattr(self, f"bar_{suffix}").config(
                stemp_color, text=f"{curr:0{self.leading_zero}.0f}{sign}")

    def update_tcmpd(self, curr, last):
        """Tyre compound"""
        if curr != last:
            self.bar_tcmpd_f.config(text=curr[0])
            self.bar_tcmpd_r.config(text=curr[1])

    # Additional methods
    def temp_mode(self, value):
        """Temperature inner/center/outer mode"""
        if self.wcfg["ICO_mode"]:
            return tuple(map(self.temp_units, value))
        return self.temp_units(sum(value) / 3)

    def temp_units(self, value):
        """Temperature units"""
        if self.wcfg["temp_unit"] == "0":
            return round(value - 273.15)
        return round(calc.celsius2fahrenheit(value - 273.15))

    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        ftire = self.wcfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
        rtire = self.wcfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
        return ftire, rtire

    @staticmethod
    def color_heatmap(temp):
        """Tyre temperature color"""
        if temp < 40:
            color = "#44F"  # blue
        elif 40 <= temp < 60:
            color = "#84F"
        elif 60 <= temp < 80:
            color = "#F4F"  # purple
        elif 80 <= temp < 100:
            color = "#F48"
        elif 100 <= temp < 120:
            color = "#F44"  # red
        elif 120 <= temp < 140:
            color = "#F84"
        else:
            color = "#FF4"  # yellow
        return color
