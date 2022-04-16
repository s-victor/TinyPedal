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
Temperature Widget
"""

import tkinter as tk
import tkinter.font as tkfont

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import cfg, Widget, MouseEvent


class Temp(Widget, MouseEvent):
    """Draw temperature widget"""

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - Temperature Widget")
        self.attributes("-alpha", cfg.temp["opacity"])

        # Config size & position
        bar_gap = cfg.temp["bar_gap"]
        self.geometry(f"+{cfg.temp['position_x']}+{cfg.temp['position_y']}")

        # Config style & variable
        text_def = "n/a"
        fg_color_tyre = cfg.temp["font_color_tyre"]
        bg_color_tyre = cfg.temp["bkg_color_tyre"]
        fg_color_brake = cfg.temp["font_color_brake"]
        bg_color_brake = cfg.temp["bkg_color_brake"]
        font_temp = tkfont.Font(family=cfg.temp["font_name"],
                                size=-cfg.temp["font_size"],
                                weight=cfg.temp["font_weight"])

        # Draw label
        bar_style = {"text":text_def, "bd":0, "height":1, "width":5,
                     "padx":0, "pady":0, "font":font_temp}

        self.bar_ttemp_fl = tk.Label(self, bar_style, fg=fg_color_tyre, bg=bg_color_tyre)
        self.bar_ttemp_fr = tk.Label(self, bar_style, fg=fg_color_tyre, bg=bg_color_tyre)
        self.bar_ttemp_rl = tk.Label(self, bar_style, fg=fg_color_tyre, bg=bg_color_tyre)
        self.bar_ttemp_rr = tk.Label(self, bar_style, fg=fg_color_tyre, bg=bg_color_tyre)
        self.bar_btemp_fl = tk.Label(self, bar_style, fg=fg_color_brake, bg=bg_color_brake)
        self.bar_btemp_fr = tk.Label(self, bar_style, fg=fg_color_brake, bg=bg_color_brake)
        self.bar_btemp_rl = tk.Label(self, bar_style, fg=fg_color_brake, bg=bg_color_brake)
        self.bar_btemp_rr = tk.Label(self, bar_style, fg=fg_color_brake, bg=bg_color_brake)

        if cfg.temp["layout"] == "0":
            # Vertical layout, tyre above brake
            self.bar_ttemp_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_ttemp_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_ttemp_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_ttemp_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_btemp_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_btemp_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_btemp_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_btemp_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.temp["layout"] == "1":
            # Vertical layout, brake above tyre
            self.bar_btemp_fl.grid(row=0, column=0, padx=0, pady=0)
            self.bar_btemp_fr.grid(row=0, column=1, padx=0, pady=0)
            self.bar_btemp_rl.grid(row=1, column=0, padx=0, pady=(0, bar_gap))
            self.bar_btemp_rr.grid(row=1, column=1, padx=0, pady=(0, bar_gap))
            self.bar_ttemp_fl.grid(row=2, column=0, padx=0, pady=0)
            self.bar_ttemp_fr.grid(row=2, column=1, padx=0, pady=0)
            self.bar_ttemp_rl.grid(row=3, column=0, padx=0, pady=0)
            self.bar_ttemp_rr.grid(row=3, column=1, padx=0, pady=0)
        elif cfg.temp["layout"] == "2":
            # Horizontal layout, tyre outside of brake
            self.bar_ttemp_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_ttemp_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_ttemp_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_ttemp_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_btemp_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_btemp_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_btemp_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_btemp_rr.grid(row=1, column=2, padx=0, pady=0)
        else:
            # Horizontal layout, brake outside of tyre
            self.bar_btemp_fl.grid(row=0, column=0, padx=(0, bar_gap), pady=0)
            self.bar_btemp_fr.grid(row=0, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_btemp_rl.grid(row=1, column=0, padx=(0, bar_gap), pady=0)
            self.bar_btemp_rr.grid(row=1, column=3, padx=(bar_gap, 0), pady=0)
            self.bar_ttemp_fl.grid(row=0, column=1, padx=0, pady=0)
            self.bar_ttemp_fr.grid(row=0, column=2, padx=0, pady=0)
            self.bar_ttemp_rl.grid(row=1, column=1, padx=0, pady=0)
            self.bar_ttemp_rr.grid(row=1, column=2, padx=0, pady=0)

        self.update_temp()

        # Assign mouse event
        MouseEvent.__init__(self)

    def save_widget_position(self):
        """Save widget position"""
        cfg.temp["position_x"] = str(self.winfo_x())
        cfg.temp["position_y"] = str(self.winfo_y())
        cfg.save()

    def update_temp(self):
        """Update temperature

        Update only when vehicle on track, and widget is enabled.
        """
        if read_data.state() and cfg.temp["enable"]:
            # Read average tyre & brake temperature data
            (ttemp_fl, ttemp_fr, ttemp_rl, ttemp_rr, btemp_fl, btemp_fr, btemp_rl, btemp_rr
             ) = [calc.kelvin2celsius(data) for data in read_data.temp()]

            # Set up display temps
            ttemp_fl_d = calc.conv_temp(ttemp_fl, cfg.temp["temp_unit"])
            ttemp_fr_d = calc.conv_temp(ttemp_fr, cfg.temp["temp_unit"])
            ttemp_rl_d = calc.conv_temp(ttemp_rl, cfg.temp["temp_unit"])
            ttemp_rr_d = calc.conv_temp(ttemp_rr, cfg.temp["temp_unit"])

            btemp_fl_d = calc.conv_temp(btemp_fl, cfg.temp["temp_unit"])
            btemp_fr_d = calc.conv_temp(btemp_fr, cfg.temp["temp_unit"])
            btemp_rl_d = calc.conv_temp(btemp_rl, cfg.temp["temp_unit"])
            btemp_rr_d = calc.conv_temp(btemp_rr, cfg.temp["temp_unit"])

            # Temperature update
            if cfg.temp["color_swap_tyre"] == "0":
                self.bar_ttemp_fl["fg"] = self.color_ttemp(ttemp_fl)
                self.bar_ttemp_fr["fg"] = self.color_ttemp(ttemp_fr)
                self.bar_ttemp_rl["fg"] = self.color_ttemp(ttemp_rl)
                self.bar_ttemp_rr["fg"] = self.color_ttemp(ttemp_rr)
            else:
                self.bar_ttemp_fl["bg"] = self.color_ttemp(ttemp_fl)
                self.bar_ttemp_fr["bg"] = self.color_ttemp(ttemp_fr)
                self.bar_ttemp_rl["bg"] = self.color_ttemp(ttemp_rl)
                self.bar_ttemp_rr["bg"] = self.color_ttemp(ttemp_rr)

            if cfg.temp["color_swap_brake"] == "0":
                self.bar_btemp_fl["bg"] = self.color_btemp(btemp_fl)
                self.bar_btemp_fr["bg"] = self.color_btemp(btemp_fr)
                self.bar_btemp_rl["bg"] = self.color_btemp(btemp_rl)
                self.bar_btemp_rr["bg"] = self.color_btemp(btemp_rr)
            else:
                self.bar_btemp_fl["fg"] = self.color_btemp(btemp_fl)
                self.bar_btemp_fr["fg"] = self.color_btemp(btemp_fr)
                self.bar_btemp_rl["fg"] = self.color_btemp(btemp_rl)
                self.bar_btemp_rr["fg"] = self.color_btemp(btemp_rr)

            self.bar_ttemp_fl.config(text=f" {ttemp_fl_d:02.0f}°")
            self.bar_ttemp_fr.config(text=f" {ttemp_fr_d:02.0f}°")
            self.bar_ttemp_rl.config(text=f" {ttemp_rl_d:02.0f}°")
            self.bar_ttemp_rr.config(text=f" {ttemp_rr_d:02.0f}°")
            self.bar_btemp_fl.config(text=f" {btemp_fl_d:02.0f}°")
            self.bar_btemp_fr.config(text=f" {btemp_fr_d:02.0f}°")
            self.bar_btemp_rl.config(text=f" {btemp_rl_d:02.0f}°")
            self.bar_btemp_rr.config(text=f" {btemp_rr_d:02.0f}°")

        # Update rate
        self.after(cfg.temp["update_delay"], self.update_temp)

    # Additional methods
    @staticmethod
    def color_ttemp(temp):
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

    @staticmethod
    def color_btemp(temp):
        """Brake temperature color"""
        if temp < 100:
            color = "#44F"  # blue
        elif 100 <= temp < 200:
            color = "#48F"
        elif 200 <= temp < 300:
            color = "#4FF"  # cyan
        elif 300 <= temp < 400:
            color = "#4F8"
        elif 400 <= temp < 500:
            color = "#4F4"  # green
        elif 500 <= temp < 600:
            color = "#8F4"
        elif 600 <= temp < 700:
            color = "#FF4"  # yellow
        elif 700 <= temp < 800:
            color = "#F84"
        else:
            color = "#F44"  # red
        return color
