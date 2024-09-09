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
Deltabest extended Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "deltabest_extended"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "--.---"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)

        if self.wcfg["layout"] == 0:
            prefix_just = max(
                len(self.wcfg["prefix_all_time_deltabest"]),
                len(self.wcfg["prefix_session_deltabest"]),
                len(self.wcfg["prefix_stint_deltabest"]),
                len(self.wcfg["prefix_deltalast"]),
            )
        else:
            prefix_just = 0

        self.prefix_atbest = self.wcfg["prefix_all_time_deltabest"].ljust(prefix_just)
        self.prefix_ssbest = self.wcfg["prefix_session_deltabest"].ljust(prefix_just)
        self.prefix_stbest = self.wcfg["prefix_stint_deltabest"].ljust(prefix_just)
        self.prefix_labest = self.wcfg["prefix_deltalast"].ljust(prefix_just)

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

        # All time deltabest
        if self.wcfg["show_all_time_deltabest"]:
            text_atbest = f"{self.prefix_atbest}{text_def}"
            bar_style_atbest = self.set_qss(
                fg_color=self.wcfg["font_color_all_time_deltabest"],
                bg_color=self.wcfg["bkg_color_all_time_deltabest"]
            )
            self.bar_atbest = self.set_qlabel(
                text=text_atbest,
                style=bar_style_atbest,
                width=font_m.width * len(text_atbest) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_atbest,
                column=self.wcfg["column_index_all_time_deltabest"],
            )

        # Session deltabest
        if self.wcfg["show_session_deltabest"]:
            text_ssbest = f"{self.prefix_ssbest}{text_def}"
            bar_style_ssbest = self.set_qss(
                fg_color=self.wcfg["font_color_session_deltabest"],
                bg_color=self.wcfg["bkg_color_session_deltabest"]
            )
            self.bar_ssbest = self.set_qlabel(
                text=text_ssbest,
                style=bar_style_ssbest,
                width=font_m.width * len(text_ssbest) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_ssbest,
                column=self.wcfg["column_index_session_deltabest"],
            )

        # Stint deltabest
        if self.wcfg["show_stint_deltabest"]:
            text_stbest = f"{self.prefix_stbest}{text_def}"
            bar_style_stbest = self.set_qss(
                fg_color=self.wcfg["font_color_stint_deltabest"],
                bg_color=self.wcfg["bkg_color_stint_deltabest"]
            )
            self.bar_stbest = self.set_qlabel(
                text=text_stbest,
                style=bar_style_stbest,
                width=font_m.width * len(text_stbest) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_stbest,
                column=self.wcfg["column_index_stint_deltabest"],
            )

        # Deltalast
        if self.wcfg["show_deltalast"]:
            text_labest = f"{self.prefix_labest}{text_def}"
            bar_style_labest = self.set_qss(
                fg_color=self.wcfg["font_color_deltalast"],
                bg_color=self.wcfg["bkg_color_deltalast"]
            )
            self.bar_labest = self.set_qlabel(
                text=text_labest,
                style=bar_style_labest,
                width=font_m.width * len(text_labest) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_labest,
                column=self.wcfg["column_index_deltalast"],
            )

        # Last data
        self.last_all_time_deltabest = 0
        self.last_session_deltabest = 0
        self.last_stint_deltabest = 0
        self.last_deltalast = 0
        self.last_laptimes = [0,0,0,0]
        self.new_lap = True

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            if minfo.delta.lapTimeCurrent < self.freeze_duration:
                all_time_deltabest = minfo.delta.lapTimeLast - self.last_laptimes[0]
                session_deltabest = minfo.delta.lapTimeLast - self.last_laptimes[1]
                stint_deltabest = minfo.delta.lapTimeLast - self.last_laptimes[2]
                deltalast = minfo.delta.lapTimeLast - self.last_laptimes[3]
                self.new_lap = True
            else:
                if self.new_lap:
                    self.last_laptimes[0] = minfo.delta.lapTimeBest
                    self.last_laptimes[1] = minfo.delta.lapTimeSession
                    self.last_laptimes[2] = minfo.delta.lapTimeStint
                    self.last_laptimes[3] = minfo.delta.lapTimeLast
                    self.new_lap = False

                all_time_deltabest = minfo.delta.deltaBest
                session_deltabest = minfo.delta.deltaSession
                stint_deltabest = minfo.delta.deltaStint
                deltalast = minfo.delta.deltaLast

            # All time deltabest
            if self.wcfg["show_all_time_deltabest"]:
                self.update_deltabest(
                    self.bar_atbest, all_time_deltabest, self.last_all_time_deltabest,
                    self.prefix_atbest
                )
                self.last_all_time_deltabest = all_time_deltabest

            # Session deltabest
            if self.wcfg["show_session_deltabest"]:
                self.update_deltabest(
                    self.bar_ssbest, session_deltabest, self.last_session_deltabest,
                    self.prefix_ssbest
                )
                self.last_session_deltabest = session_deltabest

            # Stint deltabest
            if self.wcfg["show_stint_deltabest"]:
                self.update_deltabest(
                    self.bar_stbest, stint_deltabest, self.last_stint_deltabest,
                    self.prefix_stbest
                )
                self.last_stint_deltabest = stint_deltabest

            # Deltalast
            if self.wcfg["show_stint_deltabest"]:
                self.update_deltabest(
                    self.bar_labest, deltalast, self.last_deltalast,
                    self.prefix_labest
                )
                self.last_deltalast = deltalast

    # GUI update methods
    def update_deltabest(self, target_bar, curr, last, prefix):
        """Update deltabest"""
        if curr != last:
            text = f"{calc.sym_range(curr, self.wcfg['delta_display_range']): >+6.3f}"[:6]
            target_bar.setText(f"{prefix}{text}")
