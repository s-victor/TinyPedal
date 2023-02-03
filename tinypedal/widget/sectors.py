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
Sectors Widget
"""

import re
import tkinter as tk
import tkinter.font as tkfont

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "sectors"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        bar_gap = self.wcfg["bar_gap"]
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        font_sectors = tkfont.Font(family=self.wcfg["font_name"],
                                   size=-self.wcfg["font_size"],
                                   weight=self.wcfg["font_weight"])

        self.verified = False  # load & save switch

        # Draw label
        bar_style = {"bd":0, "height":1, "padx":0, "pady":0, "font":font_sectors}
        frame_laptime = tk.Frame(self, bd=0, highlightthickness=0,
                                 bg=self.cfg.overlay["transparent_color"])

        # Current position and current lap number
        if self.wcfg["show_position_lapnumber"]:
            self.bar_position = tk.Label(self, bar_style, text="P  ", width=4,
                                         fg=self.wcfg["font_color_position"],
                                         bg=self.wcfg["bkg_color_position"])

            self.bar_laps = tk.Label(self, bar_style, text="L  ", width=4,
                                    fg=self.wcfg["font_color_lapnumber"],
                                    bg=self.wcfg["bkg_color_lapnumber"])

        # Speed
        if self.wcfg["show_speed"]:
            self.bar_speed_curr = tk.Label(self, bar_style, text="", width=6,
                                          fg=self.wcfg["font_color_speed"],
                                          bg=self.wcfg["bkg_color_speed"])

            self.bar_speed_best = tk.Label(self, bar_style, text="", width=6,
                                           fg=self.wcfg["font_color_speed"],
                                           bg=self.wcfg["bkg_color_speed"])

        # Target time
        self.bar_time_target = tk.Label(frame_laptime, bar_style,
                                        text="  --:--.---", width=12,
                                        fg=self.wcfg["font_color_target_time"],
                                        bg=self.wcfg["bkg_color_target_time"])

        # Current time
        self.bar_time_curr = tk.Label(frame_laptime, bar_style,
                                      text="  --:--.---", width=12,
                                      fg=self.wcfg["font_color_current_time"],
                                      bg=self.wcfg["bkg_color_current_time"])

        # Gap to best lap laptime
        self.bar_time_gap = tk.Label(self, bar_style, text="--.---", width=8,
                                     fg=self.wcfg["font_color_laptime_gap"],
                                     bg=self.wcfg["bkg_color_laptime_gap"])

        # Gap to best sector time
        self.bar_s1_gap = tk.Label(self, bar_style, text="S1", width=8,
                                   fg=self.wcfg["font_color_sector"],
                                   bg=self.wcfg["bkg_color_sector"])
        self.bar_s2_gap = tk.Label(self, bar_style, text="S2", width=8,
                                   fg=self.wcfg["font_color_sector"],
                                   bg=self.wcfg["bkg_color_sector"])
        self.bar_s3_gap = tk.Label(self, bar_style, text="S3", width=8,
                                   fg=self.wcfg["font_color_sector"],
                                   bg=self.wcfg["bkg_color_sector"])

        # Default layout, sector time above delta
        if self.wcfg["layout"] == "0":
            frame_laptime.grid(row=0, column=2, columnspan=3, padx=0, pady=(0,bar_gap), sticky="we")
            self.bar_time_target.pack(side="left", fill="x", expand=1, padx=(0,bar_gap), pady=0)
            self.bar_time_curr.pack(side="right", fill="x", expand=1, padx=0, pady=0)

            self.bar_s1_gap.grid(row=1, column=2, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_s2_gap.grid(row=1, column=3, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_s3_gap.grid(row=1, column=4, padx=0, pady=(0,bar_gap))

            self.bar_time_gap.grid(row=0, column=5, padx=(bar_gap,0), pady=(0,bar_gap))
        # Alternative layout, delta time above sector
        else:
            self.bar_s1_gap.grid(row=0, column=2, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_s2_gap.grid(row=0, column=3, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_s3_gap.grid(row=0, column=4, padx=0, pady=(0,bar_gap))

            frame_laptime.grid(row=1, column=2, columnspan=3, padx=0, pady=(0,bar_gap), sticky="we")
            self.bar_time_target.pack(side="left", fill="x", expand=1, padx=(0,bar_gap), pady=0)
            self.bar_time_curr.pack(side="right", fill="x", expand=1, padx=0, pady=0)

            self.bar_time_gap.grid(row=1, column=5, padx=(bar_gap,0), pady=(0,bar_gap))

        if self.wcfg["show_speed"]:
            self.bar_speed_curr.grid(row=0, column=0, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_speed_best.grid(row=1, column=0, padx=(0,bar_gap), pady=(0,bar_gap))

        if self.wcfg["show_position_lapnumber"]:
            self.bar_position.grid(row=0, column=1, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_laps.grid(row=1, column=1, padx=(0,bar_gap), pady=(0,bar_gap))

        if not self.wcfg["always_show_laptime_gap"]:  # hide laptime gap
            self.bar_time_gap.grid_remove()

        # Initialize with default values
        self.set_defaults()

        # Last data
        self.last_cb_topspeed = 0
        self.last_ub_topspeed = 0
        self.last_plr_place = 0
        self.last_plr_laps = 0

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def set_defaults(self):
        """Initialize variables"""
        self.start_last = 0                      # last lap start time
        self.last_sector_idx = -1                # previous recorded sector index value
        self.combo_name = "unknown"              # current car & track combo
        self.session_id = None                   # session identity

        self.best_laptime = MAGIC_NUM            # best laptime (seconds)
        self.delta_s = [0,0,0]                   # deltabest times against all time best sector
        self.delta_bestlap_s = [0,0,0]           # deltabest times against best laptime sector
        self.prev_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]           # previous sector times
        self.best_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]           # best sector times
        self.bestlap_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]        # best lap sector times

        self.valid_topspeed = True
        self.cb_topspeed = 0                     # current-lap best top speed
        self.sb_topspeed = 0                     # session best top speed
        self.ub_topspeed = 0                     # unverified session best top speed
        self.speed_timer_start = 0               # speed timer start
        self.freeze_timer_start = 0              # sector timer start

        self.time_target_text = "  --:--.---"    # target time text
        self.last_time_target_text = ""          # last recorded target time text for freeze
        self.update_time_target(self.time_target_text)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read current running laptime from delta_time module
            laptime_curr = module.delta_time.output_data[0]

            # Read Sector data
            (sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime,
             plr_laps, plr_place, lap_etime, speed, start_curr) = read_data.sector()

            # Start updating

            # Save switch
            if not self.verified:
                self.verified = True
                self.set_defaults()  # reset data
                self.load_saved_sector_data()  # load saved sector data
                self.restore_best_sector(self.best_s)  # Restore best sector time

            # Speed update
            if self.wcfg["show_speed"]:
                # Lap start & finish detection
                if start_curr != self.start_last:  # time stamp difference
                    self.cb_topspeed = speed  # reset current lap fastest speed
                    self.start_last = start_curr  # reset
                    self.valid_topspeed = False

                # Validate fastest speed
                if not self.valid_topspeed and laptime_curr > 1:
                    if last_laptime > 0:  # valid last laptime
                        self.sb_topspeed = self.ub_topspeed
                    else:  # invalid last laptime
                        self.ub_topspeed = self.sb_topspeed  # restore session fastest speed
                        if self.cb_topspeed > self.ub_topspeed:
                            self.ub_topspeed = self.cb_topspeed
                    # Update session top speed display
                    self.update_speed_best(self.ub_topspeed, MAGIC_NUM)
                    self.valid_topspeed = True

                # Update current top speed display
                if speed > self.cb_topspeed:
                    self.cb_topspeed = speed
                self.update_speed_curr(self.cb_topspeed, self.last_cb_topspeed)
                self.last_cb_topspeed = self.cb_topspeed

                # Update session top speed display
                if speed > self.ub_topspeed:
                    self.ub_topspeed = speed
                    self.speed_timer_start = lap_etime  # start timer if speed higher

                if self.speed_timer_start:
                    speed_timer = lap_etime - self.speed_timer_start
                    if speed_timer >= max(self.wcfg["speed_highlight_duration"], 0):
                        self.speed_timer_start = 0  # stop timer
                        self.update_speed_best(self.ub_topspeed, MAGIC_NUM)
                    else:
                        self.update_speed_best(self.ub_topspeed, self.last_ub_topspeed, True)

                self.last_ub_topspeed = self.ub_topspeed

            # Position & lap number update
            if self.wcfg["show_position_lapnumber"]:
                self.update_position(plr_place, self.last_plr_place)
                self.last_plr_place = plr_place

                self.update_laps(plr_laps, self.last_plr_laps)
                self.last_plr_laps = plr_laps

            # Sector update

            # Update previous & best sector time
            if self.last_sector_idx != sector_idx:  # keep checking until conditions met

                # While vehicle in S1, update S3 data
                if sector_idx == 0 and last_laptime > 0 and last_sector2 > 0:
                    self.last_sector_idx = sector_idx  # reset & stop checking
                    self.update_sector3_data(last_laptime, last_sector2)

                # While vehicle in S2, update S1 data
                elif sector_idx == 1 and curr_sector1 > 0:
                    self.last_sector_idx = sector_idx  # reset
                    self.update_sector1_data(curr_sector1)

                # While vehicle in S3, update S2 data
                elif sector_idx == 2 and curr_sector2 > 0 and curr_sector1 > 0:
                    self.last_sector_idx = sector_idx  # reset
                    self.update_sector2_data(curr_sector2, curr_sector1)

                # Triggered when sector values reset
                if self.last_sector_idx == sector_idx:
                    # Store last time target text for freeze state before update
                    self.last_time_target_text = self.time_target_text

                    # Update (time target) best sector text
                    self.time_target_text = self.set_target_time(
                                                self.best_s, self.bestlap_s, sector_idx)

                    # Freeze best sector time text
                    self.update_time_target(self.last_time_target_text)

                    # Activate freeze & sector timer
                    self.freeze_timer_start = lap_etime

                # Triggered if no valid last laptime set & 8s after cross line
                # Necessary for correctly update target time for garage-pitout & app-restart
                if last_laptime < 0 and laptime_curr > 8:
                    self.last_sector_idx = sector_idx  # reset
                    # Update (time target) best sector text
                    self.time_target_text = self.set_target_time(
                                                self.best_s, self.bestlap_s, sector_idx)
                    self.update_time_target(self.time_target_text)

            # Update freeze timer
            if self.freeze_timer_start:
                freeze_timer = lap_etime - self.freeze_timer_start

                # Stop freeze timer after duration
                if freeze_timer >= self.freeze_duration(self.prev_s[sector_idx]):
                    self.freeze_timer_start = 0  # stop timer
                    # Update best sector time
                    self.update_time_target(self.time_target_text)
                    # Restore best sector time when cross finish line
                    if sector_idx == 0:
                        self.restore_best_sector(self.best_s)
                    # Hide laptime gap
                    if not self.wcfg["always_show_laptime_gap"]:
                        self.bar_time_gap.grid_remove()

            # Update current sector time
            self.update_time_curr(sector_idx, laptime_curr)

        else:
            if self.verified:
                self.verified = False  # activate verification when enter track next time

                if not self.wcfg["always_show_laptime_gap"]:
                    self.bar_time_gap.grid_remove()

                # Save only valid sector data
                if self.session_id and self.valid_sector(self.bestlap_s):
                    self.wcfg["last_saved_sector_data"] = (
                        str(self.combo_name)
                        + "|" + str(self.session_id[0])
                        + "|" + str(self.session_id[1])
                        + "|" + str(self.session_id[2])
                        + "|" + str(self.best_laptime)
                        + "|" + str(self.best_s[0])
                        + "|" + str(self.best_s[1])
                        + "|" + str(self.best_s[2])
                        + "|" + str(self.bestlap_s[0])
                        + "|" + str(self.bestlap_s[1])
                        + "|" + str(self.bestlap_s[2])
                        + "|" + str(self.sb_topspeed)
                        )
                    self.cfg.save()

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_speed_curr(self, curr, last):
        """Current lap best top speed"""
        if curr != last:
            self.bar_speed_curr.config(
                text=f"{calc.conv_speed(curr, self.wcfg['speed_unit']):.01f}")

    def update_speed_best(self, curr, last, highlighted=False):
        """Session best top speed"""
        if curr != last:
            display_text = f"{calc.conv_speed(curr, self.wcfg['speed_unit']):.01f}"
            if highlighted:
                self.bar_speed_best.config(text=display_text,
                                           fg=self.wcfg["font_color_speed_highlighted"],
                                           bg=self.wcfg["bkg_color_speed_highlighted"])
            else:
                self.bar_speed_best.config(text=display_text,
                                           fg=self.wcfg["font_color_speed"],
                                           bg=self.wcfg["bkg_color_speed"])

    def update_position(self, curr, last):
        """Driver position"""
        if curr != last:
            self.bar_position.config(text=f"P{curr}")

    def update_laps(self, curr, last):
        """Current lap number"""
        if curr != last:
            self.bar_laps.config(text=f"L{curr}")

    def update_time_gap(self, time_diff):
        """Gap to best lap laptime"""
        self.bar_time_gap.config(text=f"{time_diff:+.03f}"[:7], fg=self.color_delta(time_diff, 1))
        self.bar_time_gap.grid()

    def update_time_target(self, time_text):
        """Target sector time text"""
        self.bar_time_target.config(text=time_text)

    def update_time_curr(self, sector_idx, laptime_curr):
        """Current sector time text"""
        sector_text = ("S1","S2","S3")[sector_idx]
        curr_sectortime = laptime_curr

        # Freeze current sector time
        if self.freeze_timer_start:
            prev_sector_idx = (2,0,1)[sector_idx]
            if self.valid_sector(self.prev_s[prev_sector_idx]):  # valid previous sector time
                calc_sectortime = self.calc_sector_time(self.prev_s, prev_sector_idx)
                if calc_sectortime < MAGIC_NUM:  # bypass invalid value
                    curr_sectortime = calc_sectortime
                    sector_text = ("S1","S2","S3")[prev_sector_idx]

        # Update current sector time
        self.bar_time_curr.config(
            text=f"{sector_text}{calc.sec2laptime(curr_sectortime)[:8].rjust(9)}")

    def update_sector_gap(self, suffix, time_delta, highlighted=False):
        """Gap to best sector time"""
        if highlighted:
            getattr(self, f"bar_{suffix}").config(text=f"{time_delta:+.03f}"[:7],
                                                  fg=self.wcfg["font_color_sector_highlighted"],
                                                  bg=self.color_delta(time_delta, 0))
        else:  # show previous sector time instead
            getattr(self, f"bar_{suffix}").config(text=f"{time_delta:.03f}"[:7])

    def restore_best_sector(self, sector_time):
        """Restore best sector time"""
        for idx in range(3):
            text_s = f"S{idx+1}"
            if self.valid_sector(sector_time[idx]):
                text_s = f"{sector_time[idx]:.03f}"[:7]
            getattr(self, f"bar_s{idx+1}_gap").config(text=text_s,
                                                      fg=self.wcfg["font_color_sector"],
                                                      bg=self.wcfg["bkg_color_sector"])

    # Sector data update methods
    def update_sector3_data(self, last_laptime, last_sector2):
        """Save previous sector 3 time"""
        self.prev_s[2] = last_laptime - last_sector2

        # Update (time gap) deltabest bestlap sector 3 text
        if self.valid_sector(self.bestlap_s[2]):
            self.delta_bestlap_s[2] = self.prev_s[2] - self.bestlap_s[2] + self.delta_bestlap_s[1]
            self.update_time_gap(self.delta_bestlap_s[2])

        # Update deltabest sector 3 text
        if self.valid_sector(self.best_s[2]):
            self.delta_s[2] = self.prev_s[2] - self.best_s[2]
            self.update_sector_gap("s3_gap", self.delta_s[2], True)
        elif self.valid_sector(self.prev_s[2]):
            # Show previous sector time if no best sector time set
            self.update_sector_gap("s3_gap", self.prev_s[2])

        # Save best sector 3 time
        if self.prev_s[2] < self.best_s[2]:
            self.best_s[2] = self.prev_s[2]

        # Save sector time from personal best laptime
        if last_laptime < self.best_laptime and self.valid_sector(self.prev_s):
            self.best_laptime = last_laptime
            self.bestlap_s = self.prev_s.copy()

    def update_sector1_data(self, curr_sector1):
        """Save previous sector 1 time"""
        self.prev_s[0] = curr_sector1

        # Update (time gap) deltabest bestlap sector 1 text
        if self.valid_sector(self.bestlap_s[0]):
            self.delta_bestlap_s[0] = self.prev_s[0] - self.bestlap_s[0]
            self.update_time_gap(self.delta_bestlap_s[0])

        # Update deltabest sector 1 text
        if self.valid_sector(self.best_s[0]):
            self.delta_s[0] = self.prev_s[0] - self.best_s[0]
            self.update_sector_gap("s1_gap", self.delta_s[0], 1)
        elif self.valid_sector(self.prev_s[0]):
            # Show previous sector time if no best sector time set
            self.update_sector_gap("s1_gap", self.prev_s[0])

        # Save best sector 1 time
        if self.prev_s[0] < self.best_s[0]:
            self.best_s[0] = self.prev_s[0]

    def update_sector2_data(self, curr_sector2, curr_sector1):
        """Save previous sector 2 time"""
        self.prev_s[1] = curr_sector2 - curr_sector1

        # Update (time gap) deltabest bestlap sector 2 text
        if self.valid_sector(self.bestlap_s[1]):
            self.delta_bestlap_s[1] = self.prev_s[1] - self.bestlap_s[1] + self.delta_bestlap_s[0]
            self.update_time_gap(self.delta_bestlap_s[1])

        # Update deltabest sector 2 text
        if self.valid_sector(self.best_s[1]):
            self.delta_s[1] = self.prev_s[1] - self.best_s[1]
            self.update_sector_gap("s2_gap", self.delta_s[1], 1)
        elif self.valid_sector(self.prev_s[1]):
            # Show previous sector time if no best sector time set
            self.update_sector_gap("s2_gap", self.prev_s[1])

        # Save best sector 2 time
        if self.prev_s[1] < self.best_s[1]:
            self.best_s[1] = self.prev_s[1]

    def set_target_time(self, sec_tb, sec_pb, sec_index):
        """Set target sector time text"""
        # Mode 0 - show theoretical best sector, only update if all sector time is valid
        if self.wcfg["target_time_mode"] == 0:
            sector_time = self.calc_sector_time(sec_tb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                text = f"TB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
            else:
                text = "  --:--.---"
        # Mode 1 - show personal best lap sector
        else:
            sector_time = self.calc_sector_time(sec_pb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                text = f"PB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
            else:
                text = "  --:--.---"
        return text

    # Additional methods
    @staticmethod
    def valid_sector(sec_time):
        """Validate sector time"""
        if isinstance(sec_time, list):
            if MAGIC_NUM not in sec_time:
                return True
        else:
            if MAGIC_NUM != sec_time:
                return True
        return False

    def freeze_duration(self, seconds):
        """Set freeze duration"""
        if self.valid_sector(seconds):
            max_freeze = seconds / 2
        else:
            max_freeze = 3
        return min(max(self.wcfg["freeze_duration"], 0), max_freeze)

    @staticmethod
    def calc_sector_time(sec_time, sec_index):
        """Calculate accumulated sector time"""
        sector_time = sec_time[0]  # sector 1
        if sec_index == 1:    # sector 2 sum
            sector_time = sec_time[0] + sec_time[1]
        elif sec_index == 2:  # sector 3 sum
            sector_time = sum(sec_time)
        return sector_time

    def color_delta(self, seconds, types):
        """Sector delta color"""
        if types:  # 1 = foreground
            if seconds < 0:
                color = self.wcfg["font_color_time_gain"]
            else:
                color = self.wcfg["font_color_time_loss"]
        else:  # 0 = background
            if seconds < 0:
                color = self.wcfg["bkg_color_time_gain"]
            else:
                color = self.wcfg["bkg_color_time_loss"]
        return color

    def load_saved_sector_data(self):
        """Load and verify saved sector data"""
        saved_data = self.parse_save_data(self.wcfg["last_saved_sector_data"])
        # Check if saved data is from same session, car, track combo
        self.combo_name = read_data.combo_check()
        self.session_id = read_data.session_check()
        if self.combo_name == saved_data[0]:
            # Check if saved data belongs to current session, discard if not
            if (saved_data[1] == self.session_id[0]
                and saved_data[2] <= self.session_id[1]
                and saved_data[3] <= self.session_id[2]):
                # Assign loaded data
                self.best_laptime = saved_data[4]
                self.best_s = saved_data[5]
                self.bestlap_s = saved_data[6]
                self.ub_topspeed = self.sb_topspeed = saved_data[7]

    @staticmethod
    def parse_save_data(save_data):
        """Parse last saved sector data"""
        data = []
        rex_string = re.split(r"(\|)", save_data)

        for index, val in enumerate(rex_string):
            if val != "|":
                if index <= 2:
                    data.append(val)
                else:
                    data.append(float(val))

        try:  # fill in data
            final_list = [data[0],                    # combo name, str
                          data[1],                    # session stamp, str
                          data[2],                    # session elapsed time, float
                          data[3],                    # session total laps, float
                          data[4],                    # session PB laptime, float
                          [data[5],data[6],data[7]],  # session all time best sector, float
                          [data[8],data[9],data[10]], # session PB laptime sector, float
                          data[11]                    # session fastest top speed, float
                          ]
        except IndexError:  # reset data
            final_list = ["None"]

        return final_list
