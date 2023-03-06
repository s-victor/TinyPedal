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
Flag Widget
"""

import tkinter as tk
import tkinter.font as tkfont

from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "flag"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        bar_padx = self.wcfg["font_size"] * self.wcfg["text_padding"]
        bar_gap = self.wcfg["bar_gap"]

        # Config style & variable
        font_flag = tkfont.Font(family=self.wcfg["font_name"],
                                size=-self.wcfg["font_size"],
                                weight=self.wcfg["font_weight"])

        column_ptim = self.wcfg["column_index_pit_timer"]
        column_fuel = self.wcfg["column_index_low_fuel"]
        column_slmt = self.wcfg["column_index_speed_limiter"]
        column_yllw = self.wcfg["column_index_yellow_flag"]
        column_blue = self.wcfg["column_index_blue_flag"]
        column_slit = self.wcfg["column_index_startlights"]
        column_cdwn = self.wcfg["column_index_countdown"]

        # Draw label

        # Pit status
        if self.wcfg["show_pit_timer"]:
            self.bar_pit_timer = tk.Label(self, width=7, bd=0, height=1,
                                          text="PITST0P",
                                          font=font_flag, padx=bar_padx, pady=0,
                                          fg=self.wcfg["font_color_pit_timer"],
                                          bg=self.wcfg["bkg_color_pit_timer"])
            self.bar_pit_timer.grid_remove()

        # Low fuel warning
        if self.wcfg["show_low_fuel"]:
            self.bar_lowfuel = tk.Label(self, width=7, bd=0, height=1,
                                        text="LOWFUEL",
                                        font=font_flag, padx=bar_padx, pady=0,
                                        fg=self.wcfg["font_color_low_fuel"],
                                        bg=self.wcfg["bkg_color_low_fuel"])
            self.bar_lowfuel.grid_remove()

        # Speed limiter
        if self.wcfg["show_speed_limiter"]:
            self.bar_limiter = tk.Label(self, width=7, bd=0, height=1,
                                        text=self.wcfg["speed_limiter_text"],
                                        font=font_flag, padx=bar_padx, pady=0,
                                        fg=self.wcfg["font_color_speed_limiter"],
                                        bg=self.wcfg["bkg_color_speed_limiter"])
            self.bar_limiter.grid_remove()

        # Yellow flag
        if self.wcfg["show_yellow_flag"]:
            self.bar_yellowflag = tk.Label(self, width=7, bd=0, height=1,
                                           text="YELLOW",
                                           font=font_flag, padx=bar_padx, pady=0,
                                           fg=self.wcfg["font_color_yellow_flag"],
                                           bg=self.wcfg["bkg_color_yellow_flag"])
            self.bar_yellowflag.grid_remove()

        # Blue flag
        if self.wcfg["show_blue_flag"]:
            self.bar_blueflag = tk.Label(self, width=7, bd=0, height=1,
                                         text="BLUE",
                                         font=font_flag, padx=bar_padx, pady=0,
                                         fg=self.wcfg["font_color_blue_flag"],
                                         bg=self.wcfg["bkg_color_blue_flag"])
            self.bar_blueflag.grid_remove()

        # Start lights
        if self.wcfg["show_startlights"]:
            self.bar_startlights = tk.Label(self, width=7, bd=0, height=1,
                                            text="SLIGHTS",
                                            font=font_flag, padx=bar_padx, pady=0,
                                            fg=self.wcfg["font_color_startlights"],
                                            bg=self.wcfg["bkg_color_red_lights"])
            self.bar_startlights.grid_remove()

        # Countdown
        if self.wcfg["show_start_countdown"]:
            self.bar_countdown = tk.Label(self, width=7, bd=0, height=1,
                                          text="CDTIMER",
                                          font=font_flag, padx=bar_padx, pady=0,
                                          fg=self.wcfg["font_color_countdown"],
                                          bg=self.wcfg["bkg_color_countdown"])
            self.bar_countdown.grid_remove()

        if self.wcfg["layout"] == "0":
            # Vertical layout
            if self.wcfg["show_pit_timer"]:
                self.bar_pit_timer.grid(row=column_ptim, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_low_fuel"]:
                self.bar_lowfuel.grid(row=column_fuel, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_speed_limiter"]:
                self.bar_limiter.grid(row=column_slmt, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_yellow_flag"]:
                self.bar_yellowflag.grid(row=column_yllw, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_blue_flag"]:
                self.bar_blueflag.grid(row=column_blue, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_startlights"]:
                self.bar_startlights.grid(row=column_slit, column=0, padx=0, pady=(0,bar_gap))
            if self.wcfg["show_start_countdown"]:
                self.bar_countdown.grid(row=column_cdwn, column=0, padx=0, pady=(0,bar_gap))
        else:
            # Horizontal layout
            if self.wcfg["show_pit_timer"]:
                self.bar_pit_timer.grid(row=0, column=column_ptim, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_low_fuel"]:
                self.bar_lowfuel.grid(row=0, column=column_fuel, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_speed_limiter"]:
                self.bar_limiter.grid(row=0, column=column_slmt, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_yellow_flag"]:
                self.bar_yellowflag.grid(row=0, column=column_yllw, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_blue_flag"]:
                self.bar_blueflag.grid(row=0, column=column_blue, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_startlights"]:
                self.bar_startlights.grid(row=0, column=column_slit, padx=(0,bar_gap), pady=0)
            if self.wcfg["show_start_countdown"]:
                self.bar_countdown.grid(row=0, column=column_cdwn, padx=(0,bar_gap), pady=0)

        # Last data
        self.checked = False

        self.last_inpits = None
        self.pit_timer_start = None
        self.last_pit_timer = None
        self.last_fuel_usage = [None] * 2
        self.last_pit_limiter = None
        self.last_blue_flag = None
        self.blue_flag_timer_start = None
        self.last_blue_flag_timer = None
        self.last_yellow_flag = None
        self.last_start_timer = None
        self.last_lap_stime = 0

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read flag data
            inpits, pit_limiter, curr_session, race_phase = read_data.pitting()
            lap_stime, lap_etime = read_data.lap_timestamp()

            # Pit timer
            if self.wcfg["show_pit_timer"]:
                pit_timer = -1
                pit_timer_highlight = False
                if inpits != self.last_inpits:
                    if inpits:
                        self.pit_timer_start = lap_etime
                    self.last_inpits = inpits

                if self.pit_timer_start:
                    if inpits:
                        pit_timer = min(lap_etime - self.pit_timer_start, 999.99)
                    elif (lap_etime - self.last_pit_timer - self.pit_timer_start
                          <= self.wcfg["pit_time_highlight_duration"]):
                        pit_timer = self.last_pit_timer + 0.000001
                        pit_timer_highlight = True
                    else:
                        self.pit_timer_start = 0  # stop timer

                self.update_pit_timer(pit_timer, self.last_pit_timer, pit_timer_highlight)
                self.last_pit_timer = pit_timer

            # Low fuel update
            if self.wcfg["show_low_fuel"]:
                fuel_usage = (min(round(module.fuel_usage.output_data[0], 2),  # amount_curr
                                  self.wcfg["low_fuel_volume_threshold"]),
                              min(round(module.fuel_usage.output_data[3], 1),  # est_runlaps
                                  self.wcfg["low_fuel_lap_threshold"]))

                if (not self.wcfg["low_fuel_for_race_only"]
                    or self.wcfg["low_fuel_for_race_only"] and curr_session > 9):
                    self.update_lowfuel(fuel_usage, self.last_fuel_usage)
                    self.last_fuel_usage = fuel_usage

            # Pit limiter
            if self.wcfg["show_speed_limiter"]:
                self.update_limiter(pit_limiter, self.last_pit_limiter)
                self.last_pit_limiter = pit_limiter

            # Blue flag
            if self.wcfg["show_blue_flag"]:
                #blue_flag = 6  # testing
                blue_flag = read_data.blue_flag()
                blue_flag_timer = -1

                if self.last_blue_flag != blue_flag and blue_flag == 6:
                    self.blue_flag_timer_start = lap_etime
                elif self.last_blue_flag != blue_flag and blue_flag != 6:
                    self.blue_flag_timer_start = 0
                self.last_blue_flag = blue_flag

                if self.blue_flag_timer_start:
                    blue_flag_timer = min(round(lap_etime - self.blue_flag_timer_start, 1), 999)

                if (not self.wcfg["blue_flag_for_race_only"]
                    or self.wcfg["blue_flag_for_race_only"] and curr_session > 9):
                    self.update_blueflag(blue_flag_timer, self.last_blue_flag_timer)
                    self.last_blue_flag_timer = blue_flag_timer

            # Yellow flag
            if self.wcfg["show_yellow_flag"]:
                #yellow_flag = [1,1,1, 1]# testing
                yellow_flag = read_data.yellow_flag()

                if (not self.wcfg["yellow_flag_for_race_only"]
                    or self.wcfg["yellow_flag_for_race_only"] and curr_session > 9):
                    self.update_yellowflag(yellow_flag, self.last_yellow_flag)
                self.last_yellow_flag = yellow_flag

            # Start lights & countdown timer
            if self.wcfg["show_startlights"] or self.wcfg["show_start_countdown"]:
                if race_phase == 4:
                    self.last_lap_stime = lap_stime  # record start time during countdown phase

                green = 1  # enable green flag
                start_timer = max(self.last_lap_stime - lap_etime,
                                  -self.wcfg["green_flag_duration"])

                if start_timer > 0:
                    green = 0  # enable red lights
                elif -start_timer == self.wcfg["green_flag_duration"]:
                    green = 2  # disable green flag

                if self.wcfg["show_startlights"]:
                    self.update_startlights(start_timer, self.last_start_timer, green)

                if self.wcfg["show_start_countdown"]:
                    self.update_countdown(start_timer, self.last_start_timer, green)

                self.last_start_timer = start_timer

        else:
            if self.checked:
                self.checked = False

                # Reset state
                self.last_inpits = None
                self.pit_timer_start = None
                self.last_pit_timer = None
                self.last_fuel_usage = [None] * 2
                self.last_pit_limiter = None
                self.last_blue_flag = None
                self.blue_flag_timer_start = None
                self.last_blue_flag_timer = None
                self.last_yellow_flag = None
                self.last_start_timer = None
                self.last_lap_stime = 0

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_pit_timer(self, curr, last, mode=0):
        """Pit timer"""
        if curr != last:  # timer
            if curr != -1:
                if mode == 0:
                    color = {"fg":self.wcfg["font_color_pit_timer"],
                             "bg":self.wcfg["bkg_color_pit_timer"]}
                    state = "P " + f"{curr:.02f}"[:5].rjust(5)
                else:  # highlight
                    color = {"fg":self.wcfg["font_color_pit_timer_stopped"],
                             "bg":self.wcfg["bkg_color_pit_timer_stopped"]}
                    state = "F " + f"{curr:.02f}"[:5].rjust(5)

                self.bar_pit_timer.config(color, text=state)
                self.bar_pit_timer.grid()
            else:
                self.bar_pit_timer.grid_remove()

    def update_lowfuel(self, curr, last):
        """Low fuel warning"""
        if curr != last:
            if (curr[0] < self.wcfg["low_fuel_volume_threshold"]
                and curr[1] < self.wcfg["low_fuel_lap_threshold"]):
                self.bar_lowfuel.config(text="LF" + f"{curr[0]:.02f}"[:4].rjust(5))
                self.bar_lowfuel.grid()
            else:
                self.bar_lowfuel.grid_remove()

    def update_limiter(self, curr, last):
        """Speed limiter"""
        if curr != last:
            if curr == 1:
                self.bar_limiter.grid()
            else:
                self.bar_limiter.grid_remove()

    def update_blueflag(self, curr, last):
        """Blue flag"""
        if curr != last:
            if curr != -1:
                self.bar_blueflag.grid()
                self.bar_blueflag.config(text=f"BLUE{curr:3.0f}")
            else:
                self.bar_blueflag.grid_remove()

    def update_yellowflag(self, curr, last):
        """Yellow flag"""
        if curr != last:
            if curr[3] == 0 and curr[0] == 1 or curr[1] == 1:
                y_text = f"{self.yflag_text(curr[0], 1)}{self.yflag_text(curr[1], 2)}"
                yellow = True
            elif curr[3] == 1 and curr[1] == 1 or curr[2] == 1:
                y_text = f"{self.yflag_text(curr[1], 2)}{self.yflag_text(curr[2], 3)}"
                yellow = True
            elif curr[3] == 2 and curr[2] == 1 or curr[0] == 1:
                y_text = f"{self.yflag_text(curr[2], 3)}{self.yflag_text(curr[0], 1)}"
                yellow = True
            else:
                yellow = False

            if yellow:
                self.bar_yellowflag.config(text=f"Y{y_text[:6].rjust(6)}")
                self.bar_yellowflag.grid()
            else:
                self.bar_yellowflag.grid_remove()

    def update_startlights(self, curr, last, green=0):
        """Start lights"""
        if curr != last:
            if green == 0:
                self.bar_startlights.config(
                    text=f"{self.wcfg['red_lights_text'][:6].ljust(6)}{read_data.startlights()}",
                    bg=self.wcfg["bkg_color_red_lights"])
                self.bar_startlights.grid()
            elif green == 1:
                self.bar_startlights.config(
                    text=self.wcfg["green_flag_text"],
                    bg=self.wcfg["bkg_color_green_flag"])
                self.bar_startlights.grid()
            else:
                self.bar_startlights.grid_remove()

    def update_countdown(self, curr, last, green=0):
        """Start countdown"""
        if curr != last:
            if green == 2:
                self.bar_countdown.grid_remove()
            else:
                self.bar_countdown.config(text="CD" + f"{max(curr, 0):.02f}"[:4].rjust(5))
                self.bar_countdown.grid()

    # Additional methods
    @staticmethod
    def yflag_text(value, sector):
        """Yellow flag text"""
        if value == 1:
            return f" S{sector}"
        return ""
