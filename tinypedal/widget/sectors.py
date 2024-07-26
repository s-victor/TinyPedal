#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QLabel

from .. import calculation as calc
from .. import validator as val
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "sectors"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width_laptime = f"min-width: {font_m.width * 11 + bar_padx}px;"
        self.bar_width_gap = f"min-width: {font_m.width * 7 + bar_padx}px;"

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_laptime = QHBoxLayout()
        layout_sector = QHBoxLayout()
        layout_laptime.setSpacing(bar_gap)
        layout_sector.setSpacing(bar_gap)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Target time
        self.bar_time_target = QLabel("  --:--.---")
        self.bar_time_target.setAlignment(Qt.AlignCenter)
        self.bar_time_target.setStyleSheet(
            f"color: {self.wcfg['font_color_target_time']};"
            f"background: {self.wcfg['bkg_color_target_time']};"
            f"{self.bar_width_laptime}"
        )

        # Current time
        self.bar_time_curr = QLabel("  --:--.---")
        self.bar_time_curr.setAlignment(Qt.AlignCenter)
        self.bar_time_curr.setStyleSheet(
            f"color: {self.wcfg['font_color_current_time']};"
            f"background: {self.wcfg['bkg_color_current_time']};"
            f"{self.bar_width_laptime}"
        )

        # Gap to best sector time
        self.bar_s1_gap = QLabel("S1")
        self.bar_s1_gap.setAlignment(Qt.AlignCenter)
        self.bar_s1_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"{self.bar_width_gap}"
        )

        self.bar_s2_gap = QLabel("S2")
        self.bar_s2_gap.setAlignment(Qt.AlignCenter)
        self.bar_s2_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"{self.bar_width_gap}"
        )

        self.bar_s3_gap = QLabel("S3")
        self.bar_s3_gap.setAlignment(Qt.AlignCenter)
        self.bar_s3_gap.setStyleSheet(
            f"color: {self.wcfg['font_color_sector']};"
            f"background: {self.wcfg['bkg_color_sector']};"
            f"{self.bar_width_gap}"
        )

        # Set layout
        layout_laptime.addWidget(self.bar_time_target)
        layout_laptime.addWidget(self.bar_time_curr)
        layout_sector.addWidget(self.bar_s1_gap)
        layout_sector.addWidget(self.bar_s2_gap)
        layout_sector.addWidget(self.bar_s3_gap)

        if self.wcfg["layout"] == 0:
            # Default layout, sector time above delta
            layout.addLayout(layout_laptime, 0, 1)
            layout.addLayout(layout_sector, 1, 1)
        else:
            # Horizontal layout
            layout.addLayout(layout_laptime, 1, 1)
            layout.addLayout(layout_sector, 0, 1)
        self.setLayout(layout)

        # Last data
        self.verified = False  # load & save switch

        # Set widget state & start update
        self.set_widget_state()

    def set_defaults(self):
        """Initialize variables"""
        self.last_sector_idx = -1                # previous recorded sector index value
        self.last_delta_s_pb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
        self.last_delta_s_tb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
        self.freeze_timer_start = 0              # sector timer start
        self.time_target_text = ""    # target time text
        self.update_time_target(self.time_target_text)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state and minfo.sectors.sectorPrev:

            # Read Sector data
            lap_stime = api.read.timing.start()
            lap_etime = api.read.timing.elapsed()
            laptime_curr = max(lap_etime - lap_stime, 0)

            # Save switch
            if not self.verified:
                self.verified = True
                self.set_defaults()  # reset data

            # Triggered when sector changed
            if self.last_sector_idx != minfo.sectors.sectorIndex:

                # Update (time target) best sector text
                self.time_target_text = self.set_target_time(
                    minfo.sectors.sectorBestTB,
                    minfo.sectors.sectorBestPB,
                    minfo.sectors.sectorIndex)

                # Activate freeze & sector timer
                self.freeze_timer_start = lap_etime

                # Freeze current sector time
                self.update_time_curr(
                    minfo.sectors.sectorIndex,
                    minfo.sectors.sectorPrev,
                    laptime_curr, True)

                # Update previous & best sector time
                prev_s_idx = (2,0,1)[minfo.sectors.sectorIndex]

                self.update_time_target(*self.update_time_gap(
                    minfo.sectors.deltaSectorBestPB,
                    minfo.sectors.deltaSectorBestTB,
                    prev_s_idx))

                if self.wcfg["target_laptime"] == "Theoretical":
                    self.update_sector_gap(
                        f"s{prev_s_idx + 1}_gap",
                        minfo.sectors.deltaSectorBestTB[prev_s_idx],
                        self.last_delta_s_tb[prev_s_idx],
                        minfo.sectors.noDeltaSector)
                else:
                    self.update_sector_gap(
                        f"s{prev_s_idx + 1}_gap",
                        minfo.sectors.deltaSectorBestPB[prev_s_idx],
                        self.last_delta_s_pb[prev_s_idx],
                        minfo.sectors.noDeltaSector)

                self.last_delta_s_pb[prev_s_idx] = minfo.sectors.deltaSectorBestPB[prev_s_idx]
                self.last_delta_s_tb[prev_s_idx] = minfo.sectors.deltaSectorBestTB[prev_s_idx]
                self.last_sector_idx = minfo.sectors.sectorIndex  # reset

            # Update freeze timer
            if self.freeze_timer_start:
                freeze_timer = lap_etime - self.freeze_timer_start

                # Stop freeze timer after duration
                if freeze_timer >= self.freeze_duration(
                    minfo.sectors.sectorPrev[minfo.sectors.sectorIndex]):
                    self.freeze_timer_start = 0  # stop timer
                    # Update best sector time
                    self.update_time_target(self.time_target_text)
                    # Restore best sector time when cross finish line
                    if minfo.sectors.sectorIndex == 0:
                        self.restore_best_sector()
            else:
                # Update current sector time
                self.update_time_curr(
                    minfo.sectors.sectorIndex,
                    minfo.sectors.sectorPrev,
                    laptime_curr)

        else:
            if self.verified:
                self.verified = False  # activate verification when enter track next time

    # GUI update methods
    def update_time_gap(self, delta_pb, delta_tb, sec_index):
        """Gap to best lap time"""
        if self.wcfg["target_laptime"] == "Theoretical":
            time_diff = self.calc_sector_time(delta_tb, sec_index)
            prefix = "TB"
        else:
            time_diff = self.calc_sector_time(delta_pb, sec_index)
            prefix = "PB"

        text = f"{time_diff:+.3f}"[:8].rjust(9)
        color = (f"color: {self.color_delta(time_diff, 1)};"
                 f"background: {self.wcfg['bkg_color_target_time']};")
        return f"{prefix}{text}", color

    def update_sector_gap(self, suffix, curr, last, no_time_set=True):
        """Gap to best sector time"""
        if curr != last and not no_time_set:
            text = f"{curr:+.3f}"[:7]
            color = (f"color: {self.wcfg['font_color_sector_highlighted']};"
                     f"background: {self.color_delta(curr, 0)};")
            getattr(self, f"bar_{suffix}").setText(text)
            getattr(self, f"bar_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_gap}")

    def update_time_curr(self, sector_idx, prev_s, laptime_curr, freeze=False):
        """Current sector time text"""
        curr_sectortime = laptime_curr
        # Freeze current sector time
        if freeze:
            prev_sector_idx = (2,0,1)[sector_idx]
            if val.sector_time(prev_s[prev_sector_idx]):  # valid previous sector time
                calc_sectortime = self.calc_sector_time(prev_s, prev_sector_idx)
                if calc_sectortime < MAGIC_NUM:  # bypass invalid value
                    curr_sectortime = calc_sectortime
        else:
            prev_sector_idx = sector_idx
        sector_text = ("S1","S2","S3")[prev_sector_idx]
        self.bar_time_curr.setText(
            f"{sector_text}{calc.sec2laptime(curr_sectortime)[:8].rjust(9)}")

    def update_time_target(self, time_text, gap_color=False):
        """Target sector time text"""
        if gap_color:
            color = gap_color
        else:
            color = (f"color: {self.wcfg['font_color_target_time']};"
                     f"background: {self.wcfg['bkg_color_target_time']};")

        self.bar_time_target.setText(time_text)
        self.bar_time_target.setStyleSheet(f"{color}{self.bar_width_laptime}")

    def restore_best_sector(self):
        """Restore best sector time"""
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = minfo.sectors.sectorBestTB
        else:
            sector_time = minfo.sectors.sectorBestPB
        for idx in range(3):
            text_s = f"S{idx+1}"
            if val.sector_time(sector_time[idx]):
                text_s = f"{sector_time[idx]:.3f}"[:7]

            getattr(self, f"bar_s{idx+1}_gap").setText(text_s)
            getattr(self, f"bar_s{idx+1}_gap").setStyleSheet(
                f"color: {self.wcfg['font_color_sector']};"
                f"background: {self.wcfg['bkg_color_sector']};"
                f"{self.bar_width_gap}"
            )

    # Sector data update methods
    def set_target_time(self, sec_tb, sec_pb, sec_index):
        """Set target sector time text"""
        # Mode 0 - show theoretical best sector, only update if all sector time is valid
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = self.calc_sector_time(sec_tb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                return f"TB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
            return "TB   --.---"
        # Mode 1 - show personal best lap sector
        sector_time = self.calc_sector_time(sec_pb, sec_index)
        if sector_time < MAGIC_NUM:  # bypass invalid value
            return f"PB{calc.sec2laptime(sector_time)[:8].rjust(9)}"
        return "PB   --.---"

    def freeze_duration(self, seconds):
        """Set freeze duration"""
        if val.sector_time(seconds):
            max_freeze = seconds * 0.5
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
