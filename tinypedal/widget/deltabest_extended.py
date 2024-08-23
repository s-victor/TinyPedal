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
from PySide2.QtWidgets import QGridLayout, QLabel

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
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]

        if self.wcfg["layout"] == 0:
            prefix_w = prefix_just = max(
                len(self.wcfg["prefix_all_time_deltabest"]),
                len(self.wcfg["prefix_session_deltabest"]),
                len(self.wcfg["prefix_stint_deltabest"]),
                len(self.wcfg["prefix_deltalast"]),
            )
        else:
            prefix_w = None
            prefix_just = 0

        self.prefix_atbest = self.wcfg["prefix_all_time_deltabest"][:prefix_w].ljust(prefix_just)
        self.prefix_ssbest = self.wcfg["prefix_session_deltabest"][:prefix_w].ljust(prefix_just)
        self.prefix_stbest = self.wcfg["prefix_stint_deltabest"][:prefix_w].ljust(prefix_just)
        self.prefix_labest = self.wcfg["prefix_deltalast"][:prefix_w].ljust(prefix_just)

        time_none = "--.---"
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)

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

        column_atbest = self.wcfg["column_index_all_time_deltabest"]
        column_ssbest = self.wcfg["column_index_session_deltabest"]
        column_stbest = self.wcfg["column_index_stint_deltabest"]
        column_labest = self.wcfg["column_index_deltalast"]

        # All time deltabest
        if self.wcfg["show_all_time_deltabest"]:
            atbest_text = f"{self.prefix_atbest}{time_none}"
            self.bar_time_atbest = QLabel(atbest_text)
            self.bar_time_atbest.setAlignment(Qt.AlignCenter)
            self.bar_time_atbest.setStyleSheet(
                f"color: {self.wcfg['font_color_all_time_deltabest']};"
                f"background: {self.wcfg['bkg_color_all_time_deltabest']};"
                f"min-width: {font_m.width * len(atbest_text) + bar_padx}px;"
            )

        # Session deltabest
        if self.wcfg["show_session_deltabest"]:
            ssbest_text = f"{self.prefix_ssbest}{time_none}"
            self.bar_time_ssbest = QLabel(ssbest_text)
            self.bar_time_ssbest.setAlignment(Qt.AlignCenter)
            self.bar_time_ssbest.setStyleSheet(
                f"color: {self.wcfg['font_color_session_deltabest']};"
                f"background: {self.wcfg['bkg_color_session_deltabest']};"
                f"min-width: {font_m.width * len(ssbest_text) + bar_padx}px;"
            )

        # Stint deltabest
        if self.wcfg["show_stint_deltabest"]:
            stbest_text = f"{self.prefix_stbest}{time_none}"
            self.bar_time_stbest = QLabel(stbest_text)
            self.bar_time_stbest.setAlignment(Qt.AlignCenter)
            self.bar_time_stbest.setStyleSheet(
                f"color: {self.wcfg['font_color_stint_deltabest']};"
                f"background: {self.wcfg['bkg_color_stint_deltabest']};"
                f"min-width: {font_m.width * len(stbest_text) + bar_padx}px;"
            )

        # Deltalast
        if self.wcfg["show_deltalast"]:
            labest_text = f"{self.prefix_labest}{time_none}"
            self.bar_time_labest = QLabel(labest_text)
            self.bar_time_labest.setAlignment(Qt.AlignCenter)
            self.bar_time_labest.setStyleSheet(
                f"color: {self.wcfg['font_color_deltalast']};"
                f"background: {self.wcfg['bkg_color_deltalast']};"
                f"min-width: {font_m.width * len(labest_text) + bar_padx}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_all_time_deltabest"]:
                layout.addWidget(self.bar_time_atbest, column_atbest, 0)
            if self.wcfg["show_session_deltabest"]:
                layout.addWidget(self.bar_time_ssbest, column_ssbest, 0)
            if self.wcfg["show_stint_deltabest"]:
                layout.addWidget(self.bar_time_stbest, column_stbest, 0)
            if self.wcfg["show_deltalast"]:
                layout.addWidget(self.bar_time_labest, column_labest, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_all_time_deltabest"]:
                layout.addWidget(self.bar_time_atbest, 0, column_atbest)
            if self.wcfg["show_session_deltabest"]:
                layout.addWidget(self.bar_time_ssbest, 0, column_ssbest)
            if self.wcfg["show_stint_deltabest"]:
                layout.addWidget(self.bar_time_stbest, 0, column_stbest)
            if self.wcfg["show_deltalast"]:
                layout.addWidget(self.bar_time_labest, 0, column_labest)
        self.setLayout(layout)

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
                self.update_deltabest(all_time_deltabest, self.last_all_time_deltabest,
                                      self.prefix_atbest, "atbest")
                self.last_all_time_deltabest = all_time_deltabest

            # Session deltabest
            if self.wcfg["show_session_deltabest"]:
                self.update_deltabest(session_deltabest, self.last_session_deltabest,
                                      self.prefix_ssbest, "ssbest")
                self.last_session_deltabest = session_deltabest

            # Stint deltabest
            if self.wcfg["show_stint_deltabest"]:
                self.update_deltabest(stint_deltabest, self.last_stint_deltabest,
                                      self.prefix_stbest, "stbest")
                self.last_stint_deltabest = stint_deltabest

            # Deltalast
            if self.wcfg["show_stint_deltabest"]:
                self.update_deltabest(deltalast, self.last_deltalast,
                                      self.prefix_labest, "labest")
                self.last_deltalast = deltalast

    # GUI update methods
    def update_deltabest(self, curr, last, prefix, suffix):
        """Update deltabest"""
        if curr != last:
            text = f"{calc.sym_range(curr, self.wcfg['delta_display_range']):+.3f}"[:6].rjust(6)
            getattr(self, f"bar_time_{suffix}").setText(f"{prefix}{text}")
