#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "sectors"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        font_w = QFontMetrics(self.font).averageCharWidth()

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout_laptime = QHBoxLayout()
        layout_sector = QHBoxLayout()
        layout_laptime.setSpacing(bar_gap)
        layout_sector.setSpacing(bar_gap)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Speed
        if self.wcfg["show_speed"]:
            self.bar_width_speed = font_w * 5
            self.bar_speed_curr = QLabel("")
            self.bar_speed_curr.setAlignment(Qt.AlignCenter)
            self.bar_speed_curr.setStyleSheet(
                f"color: {self.wcfg['font_color_speed']};"
                f"background: {self.wcfg['bkg_color_speed']};"
                f"min-width: {self.bar_width_speed}px;"
            )
            self.bar_speed_best = QLabel("")
            self.bar_speed_best.setAlignment(Qt.AlignCenter)
            self.bar_speed_best.setStyleSheet(
                f"color: {self.wcfg['font_color_speed']};"
                f"background: {self.wcfg['bkg_color_speed']};"
                f"min-width: {self.bar_width_speed}px;"
            )

        # Target time
        self.bar_width_laptime = font_w * 11
        self.bar_time_target = QLabel("  --:--.---")
        self.bar_time_target.setAlignment(Qt.AlignCenter)
        self.bar_time_target.setStyleSheet(
            f"color: {self.wcfg['font_color_target_time']};"
            f"background: {self.wcfg['bkg_color_target_time']};"
            f"min-width: {self.bar_width_laptime}px;"
        )

        # Current time
        self.bar_time_curr = QLabel("  --:--.---")
        self.bar_time_curr.setAlignment(Qt.AlignCenter)
        self.bar_time_curr.setStyleSheet(
            f"color: {self.wcfg['font_color_current_time']};"
            f"background: {self.wcfg['bkg_color_current_time']};"
            f"min-width: {self.bar_width_laptime}px;"
        )

        # Gap to best lap laptime
        self.bar_width_gap = font_w * 7
        self.bar_time_gap = QLabel("--.---")
        self.bar_time_gap.setAlignment(Qt.AlignCenter)
        self.bar_time_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_laptime_gap']};"
            f"background: {self.wcfg['bkg_color_laptime_gap']};"
            f"min-width: {self.bar_width_gap}px;"
        )
        if not self.wcfg["always_show_laptime_gap"]:  # hide laptime gap
            self.bar_time_gap.hide()

        # Gap to best sector time
        self.bar_s1_gap = QLabel("S1")
        self.bar_s1_gap.setAlignment(Qt.AlignCenter)
        self.bar_s1_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"min-width: {self.bar_width_gap}px;"
        )

        self.bar_s2_gap = QLabel("S2")
        self.bar_s2_gap.setAlignment(Qt.AlignCenter)
        self.bar_s2_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"min-width: {self.bar_width_gap}px;"
        )

        self.bar_s3_gap = QLabel("S3")
        self.bar_s3_gap.setAlignment(Qt.AlignCenter)
        self.bar_s3_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"min-width: {self.bar_width_gap}px;"
        )

        # Set layout
        layout_laptime.addWidget(self.bar_time_target)
        layout_laptime.addWidget(self.bar_time_curr)
        layout_sector.addWidget(self.bar_s1_gap)
        layout_sector.addWidget(self.bar_s2_gap)
        layout_sector.addWidget(self.bar_s3_gap)

        if self.wcfg["show_speed"]:
            layout.addWidget(self.bar_speed_curr, 0, 0)
            layout.addWidget(self.bar_speed_best, 1, 0)

        if self.wcfg["layout"] == 0:
            # Default layout, sector time above delta
            layout.addWidget(self.bar_time_gap, 0, 2)
            layout.addLayout(layout_laptime, 0, 1)
            layout.addLayout(layout_sector, 1, 1)
        else:
            # Horizontal layout
            layout.addWidget(self.bar_time_gap, 1, 2)
            layout.addLayout(layout_laptime, 1, 1)
            layout.addLayout(layout_sector, 0, 1)
        self.setLayout(layout)

        # Last data
        self.verified = False  # load & save switch
        self.set_defaults()

        self.last_cb_topspeed = None
        self.last_ub_topspeed = None
        self.last_plr_place = None
        self.last_plr_laps = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    def set_defaults(self):
        """Initialize variables"""
        self.last_lap_stime = 0                  # last lap start time
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

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read current running laptime from delta_time module
            laptime_curr = mctrl.module_delta.output[0]

            # Read Sector data
            (sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime, speed
             ) = read_data.sector()
            lap_stime, lap_etime = read_data.lap_timestamp()

            # Save switch
            if not self.verified:
                self.verified = True
                self.set_defaults()  # reset data
                self.load_saved_sector_data()  # load saved sector data
                self.restore_best_sector(self.best_s)  # Restore best sector time

            # Speed update
            if self.wcfg["show_speed"]:
                # Lap start & finish detection
                if lap_stime != self.last_lap_stime:  # time stamp difference
                    self.cb_topspeed = speed  # reset current lap fastest speed
                    self.last_lap_stime = lap_stime  # reset
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

                    # Activate freeze & sector timer
                    self.freeze_timer_start = lap_etime

                    # Freeze best sector time
                    self.update_time_target(self.last_time_target_text)

                    # Freeze current sector time
                    self.update_time_curr(sector_idx, laptime_curr, True)

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
                        self.bar_time_gap.hide()
            else:
                # Update current sector time
                self.update_time_curr(sector_idx, laptime_curr)

        else:
            if self.verified:
                self.verified = False  # activate verification when enter track next time

                if not self.wcfg["always_show_laptime_gap"]:
                    self.bar_time_gap.hide()

                # Save only valid sector data
                if self.session_id and self.valid_sector(self.bestlap_s):
                    self.wcfg["last_sector_info"] = (
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

    # GUI update methods
    def update_speed_curr(self, curr, last):
        """Current lap best top speed"""
        if curr != last:
            self.bar_speed_curr.setText(
                f"{self.speed_units(curr):.01f}")

    def update_speed_best(self, curr, last, highlighted=False):
        """Session best top speed"""
        if curr != last:
            speed_text = f"{self.speed_units(curr):.01f}"
            if highlighted:
                color = (f"color: {self.wcfg['font_color_speed_highlighted']};"
                         f"background: {self.wcfg['bkg_color_speed_highlighted']};")
            else:
                color = (f"color: {self.wcfg['font_color_speed']};"
                         f"background: {self.wcfg['bkg_color_speed']};")

            self.bar_speed_best.setText(speed_text)
            self.bar_speed_best.setStyleSheet(
                f"{color}min-width: {self.bar_width_speed}px;")

    def update_time_gap(self, time_diff):
        """Gap to best lap laptime"""
        self.bar_time_gap.setText(f"{time_diff:+.03f}"[:7])
        self.bar_time_gap.setStyleSheet(
            f"color: {self.color_delta(time_diff, 1)};"
            f"background: {self.wcfg['bkg_color_laptime_gap']};"
            f"min-width: {self.bar_width_gap}px;"
        )
        self.bar_time_gap.show()

    def update_time_target(self, time_text):
        """Target sector time text"""
        self.bar_time_target.setText(time_text)

    def update_time_curr(self, sector_idx, laptime_curr, freeze=False):
        """Current sector time text"""
        sector_text = ("S1","S2","S3")[sector_idx]
        curr_sectortime = laptime_curr

        # Freeze current sector time
        if freeze:
            prev_sector_idx = (2,0,1)[sector_idx]
            if self.valid_sector(self.prev_s[prev_sector_idx]):  # valid previous sector time
                calc_sectortime = self.calc_sector_time(self.prev_s, prev_sector_idx)
                if calc_sectortime < MAGIC_NUM:  # bypass invalid value
                    curr_sectortime = calc_sectortime
                    sector_text = ("S1","S2","S3")[prev_sector_idx]

        # Update current sector time
        self.bar_time_curr.setText(
            f"{sector_text}{calc.sec2laptime(curr_sectortime)[:8].rjust(9)}")

    def update_sector_gap(self, suffix, time_delta, highlighted=False):
        """Gap to best sector time"""
        if highlighted:
            text = f"{time_delta:+.03f}"[:7]
            color = (f"color: {self.wcfg['font_color_sector_highlighted']};"
                     f"background: {self.color_delta(time_delta, 0)};")
        else:  # show previous sector time instead
            text = f"{time_delta:.03f}"[:7]
            color = (f"color: {self.wcfg['font_color_sector']};"
                     f"background: {self.wcfg['bkg_color_sector']};")
        getattr(self, f"bar_{suffix}").setText(text)
        getattr(self, f"bar_{suffix}").setStyleSheet(
            f"{color}min-width: {self.bar_width_gap}px;")

    def restore_best_sector(self, sector_time):
        """Restore best sector time"""
        for idx in range(3):
            text_s = f"S{idx+1}"
            if self.valid_sector(sector_time[idx]):
                text_s = f"{sector_time[idx]:.03f}"[:7]

            getattr(self, f"bar_s{idx+1}_gap").setText(text_s)
            getattr(self, f"bar_s{idx+1}_gap").setStyleSheet(
                f"color: {self.wcfg['font_color_sector']};"
                f"background: {self.wcfg['bkg_color_sector']};"
                f"min-width: {self.bar_width_gap}px;"
            )

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
                return f"TB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
        # Mode 1 - show personal best lap sector
        else:
            sector_time = self.calc_sector_time(sec_pb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                return f"PB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
        return "  --:--.---"

    # Additional methods
    def speed_units(self, value):
        """Speed units"""
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        if self.cfg.units["speed_unit"] == "m/s":
            return value
        return calc.mps2kph(value)

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
        if sec_index == 1:    # sector 2 sum
            return sec_time[0] + sec_time[1]
        if sec_index == 2:  # sector 3 sum
            return sum(sec_time)
        return sec_time[0]  # sector 1

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
        saved_data = self.parse_save_string(self.wcfg["last_sector_info"])
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

    def parse_save_string(self, save_data):
        """Parse last saved sector data"""
        rex_string = re.split(r"(\|)", save_data)
        data_gen = self.split_save_string(rex_string)
        data = list(data_gen)

        try:  # fill in data
            final_list = [
                data[0],                    # combo name, str
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

    @staticmethod
    def split_save_string(rex_string):
        """Split save string"""
        for index, val in enumerate(rex_string):
            if val != "|":
                if index <= 2:
                    yield val
                else:
                    yield float(val)
