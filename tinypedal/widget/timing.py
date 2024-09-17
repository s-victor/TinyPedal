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
Timing Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "timing"
MAGIC_NUM = 99999


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "-:--.---"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]

        if self.wcfg["layout"] == 0:
            prefix_just = max(
                len(self.wcfg["prefix_best"]),
                len(self.wcfg["prefix_last"]),
                len(self.wcfg["prefix_current"]),
                len(self.wcfg["prefix_estimated"]),
                len(self.wcfg["prefix_session_best"]),
                len(self.wcfg["prefix_session_personal_best"]),
                len(self.wcfg["prefix_stint_best"]),
                len(self.wcfg["prefix_average_pace"]),
            )
        else:
            prefix_just = 0

        self.prefix_best = self.wcfg["prefix_best"].ljust(prefix_just)
        self.prefix_last = self.wcfg["prefix_last"].ljust(prefix_just)
        self.prefix_curr = self.wcfg["prefix_current"].ljust(prefix_just)
        self.prefix_esti = self.wcfg["prefix_estimated"].ljust(prefix_just)
        self.prefix_sbst = self.wcfg["prefix_session_best"].ljust(prefix_just)
        self.prefix_spbt = self.wcfg["prefix_session_personal_best"].ljust(prefix_just)
        self.prefix_stbt = self.wcfg["prefix_stint_best"].ljust(prefix_just)
        self.prefix_avpc = self.wcfg["prefix_average_pace"].ljust(prefix_just)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Session best laptime
        if self.wcfg["show_session_best"]:
            text_sbst = f"{self.prefix_sbst}{text_def}"
            bar_style_sbst = self.set_qss(
                fg_color=self.wcfg["font_color_session_best"],
                bg_color=self.wcfg["bkg_color_session_best"]
            )
            self.bar_sbst = self.set_qlabel(
                text=text_sbst,
                style=bar_style_sbst,
                width=font_m.width * len(text_sbst) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_sbst,
                column=self.wcfg["column_index_session_best"],
            )

        # Personal best laptime
        if self.wcfg["show_best"]:
            text_best = f"{self.prefix_best}{text_def}"
            bar_style_best = self.set_qss(
                fg_color=self.wcfg["font_color_best"],
                bg_color=self.wcfg["bkg_color_best"]
            )
            self.bar_best = self.set_qlabel(
                text=text_best,
                style=bar_style_best,
                width=font_m.width * len(text_best) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_best,
                column=self.wcfg["column_index_best"],
            )

        # Last laptime
        if self.wcfg["show_last"]:
            text_last = f"{self.prefix_last}{text_def}"
            self.bar_style_last = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_invalid_laptime"],
                    bg_color=self.wcfg["bkg_color_last"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_last"],
                    bg_color=self.wcfg["bkg_color_last"])
            )
            self.bar_last = self.set_qlabel(
                text=text_last,
                style=self.bar_style_last[1],
                width=font_m.width * len(text_last) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_last,
                column=self.wcfg["column_index_last"],
            )

        # Current laptime
        if self.wcfg["show_current"]:
            text_curr = f"{self.prefix_curr}{text_def}"
            bar_style_curr = self.set_qss(
                fg_color=self.wcfg["font_color_current"],
                bg_color=self.wcfg["bkg_color_current"]
            )
            self.bar_curr = self.set_qlabel(
                text=text_curr,
                style=bar_style_curr,
                width=font_m.width * len(text_curr) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_curr,
                column=self.wcfg["column_index_current"],
            )

        # Estimated laptime
        if self.wcfg["show_estimated"]:
            text_esti = f"{self.prefix_esti}{text_def}"
            bar_style_esti = self.set_qss(
                fg_color=self.wcfg["font_color_estimated"],
                bg_color=self.wcfg["bkg_color_estimated"]
            )
            self.bar_esti = self.set_qlabel(
                text=text_esti,
                style=bar_style_esti,
                width=font_m.width * len(text_esti) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_esti,
                column=self.wcfg["column_index_estimated"],
            )

        # Session personal best laptime
        if self.wcfg["show_session_personal_best"]:
            text_spbt = f"{self.prefix_spbt}{text_def}"
            bar_style_spbt = self.set_qss(
                fg_color=self.wcfg["font_color_session_personal_best"],
                bg_color=self.wcfg["bkg_color_session_personal_best"]
            )
            self.bar_spbt = self.set_qlabel(
                text=text_spbt,
                style=bar_style_spbt,
                width=font_m.width * len(text_spbt) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_spbt,
                column=self.wcfg["column_index_session_personal_best"],
            )

        # Stint personal best laptime
        if self.wcfg["show_stint_best"]:
            text_stbt = f"{self.prefix_stbt}{text_def}"
            bar_style_stbt = self.set_qss(
                fg_color=self.wcfg["font_color_stint_best"],
                bg_color=self.wcfg["bkg_color_stint_best"]
            )
            self.bar_stbt = self.set_qlabel(
                text=text_stbt,
                style=bar_style_stbt,
                width=font_m.width * len(text_stbt) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_stbt,
                column=self.wcfg["column_index_stint_best"],
            )

        # Average pace laptime
        if self.wcfg["show_average_pace"]:
            text_avpc = f"{self.prefix_avpc}{text_def}"
            bar_style_avpc = self.set_qss(
                fg_color=self.wcfg["font_color_average_pace"],
                bg_color=self.wcfg["bkg_color_average_pace"]
            )
            self.bar_avpc = self.set_qlabel(
                text=text_avpc,
                style=bar_style_avpc,
                width=font_m.width * len(text_avpc) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_avpc,
                column=self.wcfg["column_index_average_pace"],
            )

        # Last data
        self.checked = False
        self.player_index = 0
        self.laptime_sbst = MAGIC_NUM

        self.last_laptime_sbst = 0
        self.last_laptime_best = 0
        self.last_laptime_last = -1
        self.last_laptime_curr = 0
        self.last_laptime_esti = 0
        self.last_laptime_spbt = 0
        self.last_laptime_stbt = 0
        self.last_laptime_avpc = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Session best laptime
            if self.wcfg["show_session_best"]:
                laptime_best_tmp = api.read.timing.best_laptime(self.player_index)

                if 0 < laptime_best_tmp < self.laptime_sbst:
                    if self.wcfg["show_session_best_from_same_class_only"]:
                        if api.read.vehicle.same_class(self.player_index):
                            self.laptime_sbst = laptime_best_tmp
                    else:
                        self.laptime_sbst = laptime_best_tmp

                if self.player_index < api.read.vehicle.total_vehicles():
                    self.player_index += 1
                else:
                    self.player_index = 0

                self.update_laptime(
                    self.bar_sbst, self.laptime_sbst, self.last_laptime_sbst,
                    self.prefix_sbst
                )
                self.last_laptime_sbst = self.laptime_sbst

            # Personal best laptime
            if self.wcfg["show_best"]:
                laptime_best = minfo.delta.lapTimeBest
                self.update_laptime(
                    self.bar_best, laptime_best, self.last_laptime_best,
                    self.prefix_best
                )
                self.last_laptime_best = laptime_best

            # Last laptime
            if self.wcfg["show_last"]:
                laptime_last = minfo.delta.lapTimeLast
                # Convert invalid laptime to negative for state compare
                if not minfo.delta.isValidLap:
                    laptime_last *= -1
                self.update_laptime(
                    self.bar_last, laptime_last, self.last_laptime_last,
                    self.prefix_last, True
                )
                self.last_laptime_last = laptime_last

            # Current laptime
            if self.wcfg["show_current"]:
                laptime_curr = minfo.delta.lapTimeCurrent
                self.update_laptime(
                    self.bar_curr, laptime_curr, self.last_laptime_curr,
                    self.prefix_curr
                )
                self.last_laptime_curr = laptime_curr

            # Estimated laptime
            if self.wcfg["show_estimated"]:
                laptime_esti = minfo.delta.lapTimeEstimated
                self.update_laptime(
                    self.bar_esti, laptime_esti, self.last_laptime_esti,
                    self.prefix_esti
                )
                self.last_laptime_esti = laptime_esti

            # Session personal best laptime
            if self.wcfg["show_session_personal_best"]:
                laptime_spbt = api.read.timing.best_laptime()
                self.update_laptime(
                    self.bar_spbt, laptime_spbt, self.last_laptime_spbt,
                    self.prefix_spbt
                )
                self.last_laptime_spbt = laptime_spbt

            # Stint personal best laptime
            if self.wcfg["show_stint_best"]:
                laptime_stbt = minfo.delta.lapTimeStint
                self.update_laptime(
                    self.bar_stbt, laptime_stbt, self.last_laptime_stbt,
                    self.prefix_stbt
                )
                self.last_laptime_stbt = laptime_stbt

            # Average pace laptime
            if self.wcfg["show_average_pace"]:
                laptime_avpc = minfo.delta.lapTimePace
                self.update_laptime(
                    self.bar_avpc, laptime_avpc, self.last_laptime_avpc,
                    self.prefix_avpc
                )
                self.last_laptime_avpc = laptime_avpc

        else:
            if self.checked:
                self.checked = False
                self.laptime_sbst = MAGIC_NUM  # reset laptime

    # GUI update methods
    def update_laptime(self, target_bar, curr, last, prefix, check_laptime=False):
        """Update laptime"""
        if curr != last:
            if check_laptime:
                target_bar.setStyleSheet(self.bar_style_last[curr > 0])
                curr = abs(curr)

            if 0 < curr < MAGIC_NUM:
                text = f"{prefix}{calc.sec2laptime(curr)[:8]: >8}"
            else:
                text = f"{prefix}-:--.---"
            target_bar.setText(text)
