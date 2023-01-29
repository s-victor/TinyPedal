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
        frame_laptime = tk.Frame(self, bd=0, highlightthickness=0, bg=self.cfg.overlay["transparent_color"])

        # Current position and current lap number
        if self.wcfg["show_position_lapnumber"]:
            self.bar_position = tk.Label(self, bar_style, text="P  ", width=4,
                                         fg=self.wcfg["font_color_position"],
                                         bg=self.wcfg["bkg_color_position"])

            self.bar_lap = tk.Label(self, bar_style, text="L  ", width=4,
                                    fg=self.wcfg["font_color_lapnumber"],
                                    bg=self.wcfg["bkg_color_lapnumber"])

        # Speed
        if self.wcfg["show_speed"]:
            self.bar_speed_cur = tk.Label(self, bar_style, text="", width=4,
                                          fg=self.wcfg["font_color_speed"],
                                          bg=self.wcfg["bkg_color_speed"])

            self.bar_speed_best = tk.Label(self, bar_style, text="", width=4,
                                           fg=self.wcfg["font_color_speed"],
                                           bg=self.wcfg["bkg_color_speed"])

        # Target time
        self.bar_time_target = tk.Label(frame_laptime, bar_style, text="", width=12,
                                        fg=self.wcfg["font_color_target_time"],
                                        bg=self.wcfg["bkg_color_target_time"])

        # Current time
        self.bar_time_curr = tk.Label(frame_laptime, bar_style, text="", width=12,
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
            self.bar_speed_cur.grid(row=0, column=0, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_speed_best.grid(row=1, column=0, padx=(0,bar_gap), pady=(0,bar_gap))

        if self.wcfg["show_position_lapnumber"]:
            self.bar_position.grid(row=0, column=1, padx=(0,bar_gap), pady=(0,bar_gap))
            self.bar_lap.grid(row=1, column=1, padx=(0,bar_gap), pady=(0,bar_gap))

        if not self.wcfg["always_show_laptime_gap"]:  # hide laptime gap
            self.bar_time_gap.grid_remove()

        # Initialize with default values
        self.set_defaults()

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def set_defaults(self):
        """Initialize variables"""
        self.last_sector = -1                    # previous recorded sector index value
        self.combo_name = "unknown"              # current car & track combo
        self.session_id = None                   # session identity

        self.best_laptime = MAGIC_NUM            # best laptime (seconds)
        self.curr_sectortime = 0                 # current sector times
        self.delta_s = [0,0,0]                   # deltabest sector times against all time best sector
        self.delta_bestlap_s = [0,0,0]           # deltabest sector times against best lap sector
        self.prev_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]           # previous sector times
        self.best_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]           # best sector times
        self.bestlap_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]        # best lap sector times

        self.best_speed = 0                      # fastest session top speed
        self.speed_timer_start = 0               # speed timer start
        self.speed_timer = 0                     # speed timer difference
        self.freeze_timer_start = 0              # sector timer start
        self.freeze_timer = 0                    # sector timer difference

        self.time_target_text = "  --:--.---"        # target time text
        self.freeze_time_target_text = "  --:--.---" # last recorded target time text for freeze
        self.bar_time_target.config(text=self.time_target_text)
        self.bar_time_curr.config(text=self.time_target_text)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Read current running laptime from delta_time module
            laptime_curr = module.delta_time.output_data[0]

            # Read Sector data
            (gSector, mCurSector1, mCurSector2, mLastSector2, mLastLapTime,
             mTotalLaps, mPlace, mElapsedTime, speed) = read_data.sector()

            mSector = (2,0,1)[gSector]  # convert game sector order to 0,1,2 for consistency

            # Start updating

            # Save switch
            if not self.verified:
                self.verified = True
                self.set_defaults()  # reset data
                self.load_saved_sector_data()  # load saved sector data
                self.update_sector_data()  # update sector data

            # Speed update
            if self.wcfg["show_speed"]:
                # Start timer if speed higher
                if speed >= self.best_speed:
                    self.best_speed = speed
                    self.speed_timer_start = mElapsedTime

                if self.speed_timer_start:
                    self.speed_timer = mElapsedTime - self.speed_timer_start

                    if self.speed_timer >= max(self.wcfg["speed_highlight_duration"], 0):
                        self.speed_timer_start = 0  # stop timer
                        self.bar_speed_best.config(fg=self.wcfg["font_color_speed"],
                                                   bg=self.wcfg["bkg_color_speed"])
                    else:  # update top speed when necessary
                        best_speed_d = calc.conv_speed(self.best_speed, self.wcfg["speed_unit"])
                        self.bar_speed_best.config(text=f"{best_speed_d:.0f}",
                                                   fg=self.wcfg["font_color_speed_highlighted"],
                                                   bg=self.wcfg["bkg_color_speed_highlighted"])

                # Update current speed
                speed_d = calc.conv_speed(speed, self.wcfg["speed_unit"])
                self.bar_speed_cur.config(text=f"{speed_d:.0f}")

            # Position & lap number update
            if self.wcfg["show_position_lapnumber"]:
                self.bar_position.config(text=f"P{mPlace}")
                self.bar_lap.config(text=f"L{mTotalLaps}")

            # Sector update

            # Update previous & best sector time
            if self.last_sector != mSector:  # keep checking until conditions met

                # While vehicle in sector 1
                if mSector == 0 and mLastLapTime > 0 and mLastSector2 > 0:
                    self.last_sector = mSector  # reset sector value and stop checking

                    # Save previous sector 3 time
                    self.prev_s[2] = mLastLapTime - mLastSector2

                    # Update (time gap) deltabest bestlap sector 3 text
                    if self.valid_sector(self.bestlap_s[2]):
                        self.delta_bestlap_s[2] = self.prev_s[2] - self.bestlap_s[2] + self.delta_bestlap_s[1]
                        self.bar_time_gap.config(text=f"{self.delta_bestlap_s[2]:+.03f}"[:7],
                                                 fg=self.color_delta(self.delta_bestlap_s[2], 1))
                        self.bar_time_gap.grid()

                    # Update deltabest sector 3 text
                    if self.valid_sector(self.best_s[2]):
                        self.delta_s[2] = self.prev_s[2] - self.best_s[2]
                        self.bar_s3_gap.config(text=f"{self.delta_s[2]:+.03f}"[:7],
                                               fg=self.wcfg["font_color_sector_highlighted"],
                                               bg=self.color_delta(self.delta_s[2], 0))
                    elif self.wcfg["show_best_sector_time"] and self.valid_sector(self.prev_s[2]):
                        # Show previous sector time if no best sector time set
                        self.bar_s3_gap.config(text=f"{self.prev_s[2]:.03f}"[:7])

                    # Save best sector 3 time
                    if self.prev_s[2] < self.best_s[2]:
                        self.best_s[2] = self.prev_s[2]

                    # Save sector time from personal best laptime
                    if mLastLapTime < self.best_laptime and self.valid_sector(self.prev_s):
                        self.best_laptime = mLastLapTime
                        self.bestlap_s = self.prev_s.copy()

                # While vehicle in sector 2
                elif mSector == 1 and mCurSector1 > 0:
                    self.last_sector = mSector  # reset

                    # Save previous sector 1 time
                    self.prev_s[0] = mCurSector1

                    # Update (time gap) deltabest bestlap sector 1 text
                    if self.valid_sector(self.bestlap_s[0]):
                        self.delta_bestlap_s[0] = self.prev_s[0] - self.bestlap_s[0]
                        self.bar_time_gap.config(text=f"{self.delta_bestlap_s[0]:+.03f}"[:7],
                                                 fg=self.color_delta(self.delta_bestlap_s[0], 1))
                        self.bar_time_gap.grid()

                    # Update deltabest sector 1 text
                    if self.valid_sector(self.best_s[0]):
                        self.delta_s[0] = self.prev_s[0] - self.best_s[0]
                        self.bar_s1_gap.config(text=f"{self.delta_s[0]:+.03f}"[:7],
                                               fg=self.wcfg["font_color_sector_highlighted"],
                                               bg=self.color_delta(self.delta_s[0], 0))
                    elif self.wcfg["show_best_sector_time"] and self.valid_sector(self.prev_s[0]):
                        # Show previous sector time if no best sector time set
                        self.bar_s1_gap.config(text=f"{self.prev_s[0]:.03f}"[:7])

                    # Save best sector 1 time
                    if self.prev_s[0] < self.best_s[0]:
                        self.best_s[0] = self.prev_s[0]

                # While vehicle in sector 3
                elif mSector == 2 and mCurSector2 > 0 and mCurSector1 > 0:
                    self.last_sector = mSector  # reset

                    # Save previous sector 2 time
                    self.prev_s[1] = mCurSector2 - mCurSector1

                    # Update (time gap) deltabest bestlap sector 2 text
                    if self.valid_sector(self.bestlap_s[1]):
                        self.delta_bestlap_s[1] = self.prev_s[1] - self.bestlap_s[1] + self.delta_bestlap_s[0]
                        self.bar_time_gap.config(text=f"{self.delta_bestlap_s[1]:+.03f}"[:7],
                                                 fg=self.color_delta(self.delta_bestlap_s[1], 1))
                        self.bar_time_gap.grid()

                    # Update deltabest sector 2 text
                    if self.valid_sector(self.best_s[1]):
                        self.delta_s[1] = self.prev_s[1] - self.best_s[1]
                        self.bar_s2_gap.config(text=f"{self.delta_s[1]:+.03f}"[:7],
                                               fg=self.wcfg["font_color_sector_highlighted"],
                                               bg=self.color_delta(self.delta_s[1], 0))
                    elif self.wcfg["show_best_sector_time"] and self.valid_sector(self.prev_s[1]):
                        # Show previous sector time if no best sector time set
                        self.bar_s2_gap.config(text=f"{self.prev_s[1]:.03f}"[:7])

                    # Save best sector 2 time
                    if self.prev_s[1] < self.best_s[1]:
                        self.best_s[1] = self.prev_s[1]

                # Triggered when sector values reset
                if self.last_sector == mSector:
                    # Store last time target text for freeze state before update
                    self.freeze_time_target_text = self.time_target_text

                    # Update (time target) best sector text
                    self.update_time_target(self.best_s, self.bestlap_s, mSector)

                    # Activate freeze & sector timer
                    self.freeze_timer_start = mElapsedTime

                # Triggered if no valid last laptime set & 8s after cross line
                # Necessary for correctly update target time for garage-pitout & app-restart
                if mLastLapTime < 0 and laptime_curr > 8:
                    self.last_sector = mSector  # reset
                    # Update (time target) best sector text
                    self.update_time_target(self.best_s, self.bestlap_s, mSector)
                    self.bar_time_target.config(text=self.time_target_text)

            # Update current sector time value
            sector_text = ("S1","S2","S3")[mSector]
            self.curr_sectortime = laptime_curr

            # Update freeze timer
            if self.freeze_timer_start:
                self.freeze_timer = mElapsedTime - self.freeze_timer_start

                # Set max freeze duration
                if self.valid_sector(self.prev_s[mSector]):
                    max_freeze = self.prev_s[mSector] / 2
                else:
                    max_freeze = 3

                # Stop freeze timer after duration
                if self.freeze_timer >= min(max(self.wcfg["freeze_duration"], 0), max_freeze):
                    self.freeze_timer_start = 0  # stop timer
                    # Update best sector time
                    self.bar_time_target.config(text=self.time_target_text)
                    # Reset deltabest sector data
                    if mSector == 0:
                        self.update_sector_data()
                    # Hide laptime gap
                    if not self.wcfg["always_show_laptime_gap"]:
                        self.bar_time_gap.grid_remove()
                else:
                    # Freeze best sector time
                    self.bar_time_target.config(text=self.freeze_time_target_text)
                    # Freeze current sector time value
                    prev_sector_idx = (2,0,1)[mSector]
                    if self.valid_sector(self.prev_s[prev_sector_idx]):  # valid previous sector time
                        calc_sectortime = self.calc_sector_time(self.prev_s, prev_sector_idx)
                        if calc_sectortime < MAGIC_NUM:  # bypass invalid value
                            self.curr_sectortime = calc_sectortime
                            sector_text = ("S1","S2","S3")[prev_sector_idx]

            # Update current sector time
            self.bar_time_curr.config(text=f"{sector_text}{calc.sec2laptime(self.curr_sectortime)[:8].rjust(9)}")

        else:
            if self.verified:
                self.verified = False  # activate verification when enter track next time

                if not self.wcfg["always_show_laptime_gap"]:
                    self.bar_time_gap.grid_remove()

                # Save only valid sector data
                if self.session_id and self.valid_sector(self.best_s) and self.valid_sector(self.bestlap_s):
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
                        + "|" + str(self.best_speed)
                        )
                    self.cfg.save()

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    @staticmethod
    def valid_sector(sec_time):
        """Validate sector time"""
        valid = False
        if isinstance(sec_time, list):
            if MAGIC_NUM not in sec_time:
                valid = True
        else:
            if MAGIC_NUM != sec_time:
                valid = True
        return valid

    def update_time_target(self, sec_tb, sec_pb, sec_index):
        """Update time target text based on target time mode setting"""
        # Mode 0 - show theoretical best sector, only update if all sector time is valid
        if self.wcfg["target_time_mode"] == 0:
            sector_time = self.calc_sector_time(sec_tb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                self.time_target_text = f"TB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
        # Mode 1 - show personal best lap sector
        else:
            sector_time = self.calc_sector_time(sec_pb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                self.time_target_text = f"PB{calc.sec2laptime(sector_time)[:8].rjust(9)}"

    def calc_sector_time(self, sec_time, sec_index):
        """Calculate accumulated sector time"""
        sector_time = sec_time[0]  # sector 1
        if sec_index == 1:    # sector 2 sum
            sector_time = sec_time[0] + sec_time[1]
        elif sec_index == 2:  # sector 3 sum
            sector_time = sum(sec_time)
        return sector_time

    def update_sector_data(self):
        """Update sector data and reset deltabest"""
        self.delta_s = [0,0,0]  # reset deltabest
        text_s1 = "S1"
        text_s2 = "S2"
        text_s3 = "S3"
        # Show best sector time instead of sector number
        if self.wcfg["show_best_sector_time"]:
            if self.valid_sector(self.best_s[0]):
                text_s1 = f"{self.best_s[0]:.03f}"[:7]
            if self.valid_sector(self.best_s[1]):
                text_s2 = f"{self.best_s[1]:.03f}"[:7]
            if self.valid_sector(self.best_s[2]):
                text_s3 = f"{self.best_s[2]:.03f}"[:7]
        bar_style = {"fg":self.wcfg["font_color_sector"], "bg":self.wcfg["bkg_color_sector"]}
        self.bar_s1_gap.config(bar_style, text=text_s1)
        self.bar_s2_gap.config(bar_style, text=text_s2)
        self.bar_s3_gap.config(bar_style, text=text_s3)

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
                self.best_speed = saved_data[7]

    @staticmethod
    def parse_save_data(save_data):
        """Parse last saved sector data"""
        data = []
        rex_string = re.split("(\|)", save_data)

        for index, val in enumerate(rex_string):
            if val != "|":
                data.append(val) if index <= 2 else data.append(float(val))

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
        except (IndexError):  # reset data
            final_list = ["None"]

        return final_list
