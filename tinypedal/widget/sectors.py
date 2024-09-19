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
from PySide2.QtWidgets import QGridLayout, QHBoxLayout

from .. import calculation as calc
from .. import validator as val
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "sectors"
MAGIC_NUM = 99999
PREV_SECTOR_IDX = (2, 0, 1)
TEXT_SECTOR = ("S1", "S2", "S3")


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        if self.wcfg["target_laptime"] == "Theoretical":
            self.prefix_best = "TB"
        else:
            self.prefix_best = "PB"

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Target time
        layout_laptime = QHBoxLayout()
        layout_laptime.setSpacing(bar_gap)

        self.bar_style_time_target = (
            self.set_qss(
                fg_color=self.wcfg["font_color_time_loss"],
                bg_color=self.wcfg["bkg_color_target_time"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_time_gain"],
                bg_color=self.wcfg["bkg_color_target_time"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_target_time"],
                bg_color=self.wcfg["bkg_color_target_time"])
        )
        self.bar_time_target = self.set_qlabel(
            text="  --:--.---",
            style=self.bar_style_time_target[2],
            width=font_m.width * 11 + bar_padx,
        )
        layout_laptime.addWidget(self.bar_time_target)

        # Current time
        bar_style_time_curr = self.set_qss(
            fg_color=self.wcfg["font_color_current_time"],
            bg_color=self.wcfg["bkg_color_current_time"]
        )
        self.bar_time_curr = self.set_qlabel(
            text="  --:--.---",
            style=bar_style_time_curr,
            width=font_m.width * 11 + bar_padx,
        )
        layout_laptime.addWidget(self.bar_time_curr)

        # Gap to best sector time
        layout_sector = QHBoxLayout()
        layout_sector.setSpacing(bar_gap)

        self.bar_style_gap = (
            self.set_qss(
                fg_color=self.wcfg["font_color_sector_highlighted"],
                bg_color=self.wcfg["bkg_color_time_loss"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_sector_highlighted"],
                bg_color=self.wcfg["bkg_color_time_gain"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_sector"],
                bg_color=self.wcfg["bkg_color_sector"]),
        )

        self.bar_time_gap = self.set_qlabel(
            style=self.bar_style_gap[2],
            width=font_m.width * 7 + bar_padx,
            count=3
        )
        for idx in range(3):
            self.bar_time_gap[idx].setText(TEXT_SECTOR[idx])
            layout_sector.addWidget(self.bar_time_gap[idx])

        # Set layout
        if self.wcfg["layout"] == 0:
            # Default layout, sector time above delta
            layout.addLayout(layout_laptime, 0, 1)
            layout.addLayout(layout_sector, 1, 1)
        else:
            # Horizontal layout
            layout.addLayout(layout_laptime, 1, 1)
            layout.addLayout(layout_sector, 0, 1)

        # Last data
        self.verified = False  # load & save switch

    def set_defaults(self):
        """Initialize variables"""
        self.last_sector_idx = -1                # previous recorded sector index value
        self.last_delta_s_pb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
        self.last_delta_s_tb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
        self.freeze_timer_start = 0              # sector timer start
        self.time_target_text = ""    # target time text

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

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
                prev_s_idx = PREV_SECTOR_IDX[minfo.sectors.sectorIndex]

                self.update_time_target_gap(
                    minfo.sectors.deltaSectorBestPB, minfo.sectors.deltaSectorBestTB, prev_s_idx
                )

                if not minfo.sectors.noDeltaSector:
                    if self.wcfg["target_laptime"] == "Theoretical":
                        self.update_sector_gap(
                            self.bar_time_gap[prev_s_idx],
                            minfo.sectors.deltaSectorBestTB[prev_s_idx],
                            self.last_delta_s_tb[prev_s_idx])
                    else:
                        self.update_sector_gap(
                            self.bar_time_gap[prev_s_idx],
                            minfo.sectors.deltaSectorBestPB[prev_s_idx],
                            self.last_delta_s_pb[prev_s_idx])

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
    def update_sector_gap(self, target_bar, curr, last):
        """Gap to best sector time"""
        if curr != last:
            target_bar.setText(f"{curr:+.3f}"[:7])
            target_bar.setStyleSheet(self.bar_style_gap[curr < 0])

    def update_time_curr(self, sector_idx, prev_s, laptime_curr, freeze=False):
        """Current sector time text"""
        curr_sectortime = laptime_curr
        # Freeze current sector time
        if freeze:
            prev_sector_idx = PREV_SECTOR_IDX[sector_idx]
            if val.sector_time(prev_s[prev_sector_idx]):  # valid previous sector time
                sum_sectortime = calc.accumulated_sum(prev_s, prev_sector_idx)
                if sum_sectortime < MAGIC_NUM:  # bypass invalid value
                    curr_sectortime = sum_sectortime
        else:
            prev_sector_idx = sector_idx
        self.bar_time_curr.setText(
            f"{TEXT_SECTOR[prev_sector_idx]}{calc.sec2laptime(curr_sectortime)[:8]: >9}")

    def update_time_target(self, text_laptime):
        """Target sector time text"""
        self.bar_time_target.setText(text_laptime)
        self.bar_time_target.setStyleSheet(self.bar_style_time_target[2])

    def update_time_target_gap(self, delta_pb, delta_tb, sec_index):
        """Target sector time gap"""
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_gap = calc.accumulated_sum(delta_tb, sec_index)
        else:
            sector_gap = calc.accumulated_sum(delta_pb, sec_index)
        self.bar_time_target.setText(f"{self.prefix_best}{sector_gap: >+9.3f}"[:11])
        self.bar_time_target.setStyleSheet(self.bar_style_time_target[sector_gap < 0])

    def restore_best_sector(self):
        """Restore best sector time"""
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = minfo.sectors.sectorBestTB
        else:
            sector_time = minfo.sectors.sectorBestPB
        for idx in range(3):
            text_s = TEXT_SECTOR[idx]
            if val.sector_time(sector_time[idx]):
                text_s = f"{sector_time[idx]:.3f}"[:7]
            self.bar_time_gap[idx].setText(text_s)
            self.bar_time_gap[idx].setStyleSheet(self.bar_style_gap[2])

    # Sector data update methods
    def set_target_time(self, sec_tb, sec_pb, sec_index):
        """Set target sector time text"""
        # Mode 0 - show theoretical best sector, only update if all sector time is valid
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = calc.accumulated_sum(sec_tb, sec_index)
            if sector_time < MAGIC_NUM:  # bypass invalid value
                return f"TB{calc.sec2laptime(sector_time)[:8]: >9}"
            return "TB   --.---"
        # Mode 1 - show personal best lap sector
        sector_time = calc.accumulated_sum(sec_pb, sec_index)
        if sector_time < MAGIC_NUM:  # bypass invalid value
            return f"PB{calc.sec2laptime(sector_time)[:8]: >9}"
        return "PB   --.---"

    def freeze_duration(self, seconds):
        """Set freeze duration"""
        if val.sector_time(seconds):
            max_freeze = seconds * 0.5
        else:
            max_freeze = 3
        return min(max(self.wcfg["freeze_duration"], 0), max_freeze)
