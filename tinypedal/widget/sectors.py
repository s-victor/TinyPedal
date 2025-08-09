#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from .. import calculation as calc
from ..api_control import api
from ..const_common import MAX_SECONDS, PREV_SECTOR_INDEX, SECTOR_ABBR_ID
from ..module_info import minfo
from ..validator import valid_sectors
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        bar_gap = self.wcfg["bar_gap"]
        layout = self.set_grid_layout(gap=bar_gap)
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        if self.wcfg["target_laptime"] == "Theoretical":
            self.prefix_best = "TB"
        else:
            self.prefix_best = "PB"

        # Base style
        self.set_base_style(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Target time
        layout_laptime = self.set_grid_layout(gap=bar_gap)
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
        layout_laptime.addWidget(self.bar_time_target, 0, 0)

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
        layout_laptime.addWidget(self.bar_time_curr, 0, 1)

        # Gap to best sector time
        layout_sector = self.set_grid_layout(gap=bar_gap)
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
        self.bars_time_gap = self.set_qlabel(
            style=self.bar_style_gap[2],
            width=font_m.width * 7 + bar_padx,
            count=3,
        )
        for idx, bar_time_gap in enumerate(self.bars_time_gap):
            bar_time_gap.setText(SECTOR_ABBR_ID[idx])
            layout_sector.addWidget(bar_time_gap, 0, idx)

        # Set layout
        if self.wcfg["layout"] == 0:  # sector time above delta
            layout.addLayout(layout_laptime, 0, 1)
            layout.addLayout(layout_sector, 1, 1)
        else:
            layout.addLayout(layout_laptime, 1, 1)
            layout.addLayout(layout_sector, 0, 1)

        # Last data
        self.last_sector_idx = -1  # previous recorded sector index value
        self.freeze_timer_start = 0  # sector timer start
        self.time_target_text = ""  # target time text

    def post_update(self):
        self.last_sector_idx = -1
        self.freeze_timer_start = 0
        self.time_target_text = ""

    def timerEvent(self, event):
        """Update when vehicle on track"""
        # Read Sector data
        lap_stime = api.read.timing.start()
        lap_etime = api.read.timing.elapsed()
        laptime_curr = max(lap_etime - lap_stime, 0)

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
            prev_s_idx = PREV_SECTOR_INDEX[minfo.sectors.sectorIndex]

            self.update_time_target_gap(
                minfo.sectors.deltaSectorBestPB, minfo.sectors.deltaSectorBestTB, prev_s_idx
            )

            if not minfo.sectors.noDeltaSector:
                if self.wcfg["target_laptime"] == "Theoretical":
                    self.update_sector_gap(
                        self.bars_time_gap[prev_s_idx],
                        minfo.sectors.deltaSectorBestTB[prev_s_idx])
                else:
                    self.update_sector_gap(
                        self.bars_time_gap[prev_s_idx],
                        minfo.sectors.deltaSectorBestPB[prev_s_idx])

            self.last_sector_idx = minfo.sectors.sectorIndex  # reset

        # Update freeze timer
        if self.freeze_timer_start:
            # Stop freeze timer after duration
            if lap_etime - self.freeze_timer_start >= self.freeze_duration(
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

    # GUI update methods
    def update_sector_gap(self, target, data):
        """Gap to best sector time"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:+.3f}"[:7])
            target.updateStyle(self.bar_style_gap[data < 0])

    def update_time_curr(self, sector_idx, prev_s, laptime_curr, freeze=False):
        """Current sector time text"""
        curr_sectortime = laptime_curr
        # Freeze current sector time
        if freeze:
            prev_sector_idx = PREV_SECTOR_INDEX[sector_idx]
            if valid_sectors(prev_s[prev_sector_idx]):  # valid previous sector time
                sum_sectortime = calc.accumulated_sum(prev_s, prev_sector_idx)
                if sum_sectortime < MAX_SECONDS:  # bypass invalid value
                    curr_sectortime = sum_sectortime
        else:
            prev_sector_idx = sector_idx
        self.bar_time_curr.setText(
            f"{SECTOR_ABBR_ID[prev_sector_idx]}{calc.sec2laptime(curr_sectortime)[:8]: >9}")

    def update_time_target(self, text_laptime):
        """Target sector time text"""
        self.bar_time_target.setText(text_laptime)
        self.bar_time_target.updateStyle(self.bar_style_time_target[2])

    def update_time_target_gap(self, delta_pb, delta_tb, sec_index):
        """Target sector time gap"""
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_gap = calc.accumulated_sum(delta_tb, sec_index)
        else:
            sector_gap = calc.accumulated_sum(delta_pb, sec_index)
        self.bar_time_target.setText(f"{self.prefix_best}{sector_gap: >+9.3f}"[:11])
        self.bar_time_target.updateStyle(self.bar_style_time_target[sector_gap < 0])

    def restore_best_sector(self):
        """Restore best sector time"""
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = minfo.sectors.sectorBestTB
        else:
            sector_time = minfo.sectors.sectorBestPB
        for idx, bar_time_gap in enumerate(self.bars_time_gap):
            text_s = SECTOR_ABBR_ID[idx]
            if valid_sectors(sector_time[idx]):
                text_s = f"{sector_time[idx]:.3f}"[:7]
            bar_time_gap.setText(text_s)
            bar_time_gap.updateStyle(self.bar_style_gap[2])

    # Sector data update methods
    def set_target_time(self, sec_tb, sec_pb, sec_index):
        """Set target sector time text"""
        # Mode 0 - show theoretical best sector, only update if all sector time is valid
        if self.wcfg["target_laptime"] == "Theoretical":
            sector_time = calc.accumulated_sum(sec_tb, sec_index)
            if sector_time < MAX_SECONDS:  # bypass invalid value
                return f"TB{calc.sec2laptime(sector_time)[:8]: >9}"
            return "TB   --.---"
        # Mode 1 - show personal best lap sector
        sector_time = calc.accumulated_sum(sec_pb, sec_index)
        if sector_time < MAX_SECONDS:  # bypass invalid value
            return f"PB{calc.sec2laptime(sector_time)[:8]: >9}"
        return "PB   --.---"

    def freeze_duration(self, seconds):
        """Set freeze duration"""
        if valid_sectors(seconds):
            max_freeze = seconds * 0.5
        else:
            max_freeze = 3
        return calc.zero_max(self.wcfg["freeze_duration"], max_freeze)
