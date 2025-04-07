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
Brake Wear Widget
"""

from .. import calculation as calc
from ..api_control import api
from ..const_common import TEXT_NA
from ..heatmap import select_brake_failure_thickness, set_predefined_brake_name
from ..module_info import minfo
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_width = font_m.width * 4 + bar_padx
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)
        self.failure_thickness = (0, 0, 0, 0)
        self.threshold_remaining = min(max(self.wcfg["warning_threshold_remaining"], 0), 100) * 0.01

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )
        bar_style_desc = self.set_qss(
            fg_color=self.wcfg["font_color_caption"],
            bg_color=self.wcfg["bkg_color_caption"],
            font_size=int(self.wcfg['font_size'] * 0.8)
        )

        # Remaining wear
        if self.wcfg["show_remaining"]:
            layout_wear = self.set_grid_layout()
            self.bar_style_wear = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_remaining"],
                    bg_color=self.wcfg["bkg_color_remaining"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_remaining"])
            )
            self.bars_wear = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_wear[0],
                width=bar_width,
                count=4,
                last=0,
            )
            self.set_grid_layout_quad(
                layout=layout_wear,
                targets=self.bars_wear,
            )
            self.set_primary_orient(
                target=layout_wear,
                column=self.wcfg["column_index_remaining"],
            )

            if self.wcfg["show_caption"]:
                cap_wear = self.set_qlabel(
                    text="brak wear",
                    style=bar_style_desc,
                )
                layout_wear.addWidget(cap_wear, 0, 0, 1, 0)

        # Wear difference
        if self.wcfg["show_wear_difference"]:
            layout_diff = self.set_grid_layout()
            self.bar_style_diff = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_wear_difference"],
                    bg_color=self.wcfg["bkg_color_wear_difference"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_wear_difference"])
            )
            self.bars_diff = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_diff[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_diff,
                targets=self.bars_diff,
            )
            self.set_primary_orient(
                target=layout_diff,
                column=self.wcfg["column_index_wear_difference"],
            )

            if self.wcfg["show_caption"]:
                cap_diff = self.set_qlabel(
                    text="brak diff",
                    style=bar_style_desc,
                )
                layout_diff.addWidget(cap_diff, 0, 0, 1, 0)

        # Estimated lifespan in laps
        if self.wcfg["show_lifespan_laps"]:
            layout_laps = self.set_grid_layout()
            self.bar_style_laps = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_lifespan_laps"],
                    bg_color=self.wcfg["bkg_color_lifespan_laps"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_lifespan_laps"])
            )
            self.bars_laps = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_laps[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_laps,
                targets=self.bars_laps,
            )
            self.set_primary_orient(
                target=layout_laps,
                column=self.wcfg["column_index_lifespan_laps"],
            )

            if self.wcfg["show_caption"]:
                cap_laps = self.set_qlabel(
                    text="est. laps",
                    style=bar_style_desc,
                )
                layout_laps.addWidget(cap_laps, 0, 0, 1, 0)

        # Estimated lifespan in minutes
        if self.wcfg["show_lifespan_minutes"]:
            layout_mins = self.set_grid_layout()
            self.bar_style_mins = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_lifespan_minutes"],
                    bg_color=self.wcfg["bkg_color_lifespan_minutes"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_warning"],
                    bg_color=self.wcfg["bkg_color_lifespan_minutes"])
            )
            self.bars_mins = self.set_qlabel(
                text=TEXT_NA,
                style=self.bar_style_mins[0],
                width=bar_width,
                count=4,
            )
            self.set_grid_layout_quad(
                layout=layout_mins,
                targets=self.bars_mins,
            )
            self.set_primary_orient(
                target=layout_mins,
                column=self.wcfg["column_index_lifespan_minutes"],
            )

            if self.wcfg["show_caption"]:
                cap_mins = self.set_qlabel(
                    text="est. mins",
                    style=bar_style_desc,
                )
                layout_mins.addWidget(cap_mins, 0, 0, 1, 0)

        # Last data
        self.checked = False
        self.last_class_name = None
        self.last_lap_stime = 0  # last lap start time
        self.wear_prev = [0] * 4  # previous moment remaining wear
        self.wear_curr_lap = [0] * 4  # live wear update of current lap
        self.wear_last_lap = [0] * 4  # total wear of last lap
        self.wear_stint_start = [0] * 4  # remaining wear at start of stint

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            lap_stime = api.read.timing.start()
            lap_etime = api.read.timing.elapsed()
            class_name = api.read.vehicle.class_name()

            # Brake thickness in millimeter
            wear_curr = [value * 1000 for value in minfo.restapi.brakeWear]

            # Update failure thickness
            if self.last_class_name != class_name:
                self.last_class_name = class_name
                self.update_failure_thickness = (class_name)

            if lap_stime != self.last_lap_stime:
                self.wear_last_lap = self.wear_curr_lap
                self.wear_curr_lap = [0] * 4  # reset real time wear
                self.last_lap_stime = lap_stime  # reset time stamp counter

            for idx in range(4):
                # Calculate effective thickness
                wear_curr[idx] -= self.failure_thickness[idx]

                # Calibrate max thickness
                if self.wear_stint_start[idx] < wear_curr[idx]:
                    self.wear_stint_start[idx] = wear_curr[idx]

                if not self.wear_stint_start[idx]:  # bypass invalid value
                    wear_curr[idx] = 0
                elif not self.wcfg["show_thickness"]:  # convert to percent
                    wear_curr[idx] *= 100 / self.wear_stint_start[idx]

                # Update wear differences & accumulated wear
                wear_diff = self.wear_prev[idx] - wear_curr[idx]
                self.wear_prev[idx] = wear_curr[idx]
                if wear_diff > 0:
                    self.wear_curr_lap[idx] += wear_diff

                # Remaining wear
                if self.wcfg["show_remaining"]:
                    if self.wcfg["show_thickness"]:
                        threshold_remaining = self.threshold_remaining * self.wear_stint_start[idx]
                    else:
                        threshold_remaining = self.threshold_remaining * 100
                    self.update_wear(self.bars_wear[idx], wear_curr[idx], threshold_remaining)

                # Wear differences
                if self.wcfg["show_wear_difference"]:
                    if (self.wcfg["show_live_wear_difference"] and
                        lap_etime - lap_stime > self.freeze_duration):
                        self.update_diff(self.bars_diff[idx], self.wear_curr_lap[idx])
                    else:  # Last lap diff
                        self.update_diff(self.bars_diff[idx], self.wear_last_lap[idx])

                # Estimated lifespan in laps
                if self.wcfg["show_lifespan_laps"]:
                    wear_laps = calc.wear_lifespan_in_laps(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx])
                    self.update_laps(self.bars_laps[idx], wear_laps)

                # Estimated lifespan in minutes
                if self.wcfg["show_lifespan_minutes"]:
                    wear_mins = calc.wear_lifespan_in_mins(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx],
                        minfo.delta.lapTimePace)
                    self.update_mins(self.bars_mins[idx], wear_mins)

        else:
            if self.checked:
                self.checked = False
                self.wear_prev = [0] * 4
                self.wear_curr_lap = [0] * 4
                self.wear_last_lap = [0] * 4
                self.wear_stint_start = [0] * 4

    # GUI update methods
    def update_wear(self, target, data, threshold_remaining):
        """Remaining wear"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_wear[data <= threshold_remaining]
            )

    def update_diff(self, target, data):
        """Wear differences"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_diff[data > self.wcfg["warning_threshold_wear"]]
            )

    def update_laps(self, target, data):
        """Estimated lifespan in laps"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_laps[data <= self.wcfg["warning_threshold_laps"]]
            )

    def update_mins(self, target, data):
        """Estimated lifespan in minutes"""
        if target.last != data:
            target.last = data
            target.setText(self.format_num(data))
            target.setStyleSheet(
                self.bar_style_mins[data <= self.wcfg["warning_threshold_minutes"]]
            )

    # Additional methods
    @staticmethod
    def format_num(value):
        """Format number"""
        return f"{value:.2f}"[:4].strip(".")

    def update_failure_thickness(self, class_name: str):
        """Update failure thickness"""
        failure_thickness_f = select_brake_failure_thickness(
            set_predefined_brake_name(class_name, True)
        )
        failure_thickness_r = select_brake_failure_thickness(
            set_predefined_brake_name(class_name, False)
        )
        self.failure_thickness = (
            failure_thickness_f,
            failure_thickness_f,
            failure_thickness_r,
            failure_thickness_r,
        )
