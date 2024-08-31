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
Tyre Wear Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "tyre_wear"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = f"min-width: {font_m.width * 4 + bar_padx}px;"
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
        layout_twear = QGridLayout()
        layout_tdiff = QGridLayout()
        layout_tlaps = QGridLayout()
        layout_tmins = QGridLayout()
        layout_twear.setSpacing(0)
        layout_tdiff.setSpacing(0)
        layout_tlaps.setSpacing(0)
        layout_tmins.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_twear = self.wcfg["column_index_remaining"]
        column_tdiff = self.wcfg["column_index_wear_difference"]
        column_tlaps = self.wcfg["column_index_lifespan_laps"]
        column_tmins = self.wcfg["column_index_lifespan_minutes"]

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            )
            bar_desc_twear = QLabel("tyre wear")
            bar_desc_twear.setAlignment(Qt.AlignCenter)
            bar_desc_twear.setStyleSheet(bar_style_desc)
            layout_twear.addWidget(bar_desc_twear, 0, 0, 1, 0)

            bar_desc_tdiff = QLabel("wear diff")
            bar_desc_tdiff.setAlignment(Qt.AlignCenter)
            bar_desc_tdiff.setStyleSheet(bar_style_desc)
            layout_tdiff.addWidget(bar_desc_tdiff, 0, 0, 1, 0)

            bar_desc_tlaps = QLabel("est. laps")
            bar_desc_tlaps.setAlignment(Qt.AlignCenter)
            bar_desc_tlaps.setStyleSheet(bar_style_desc)
            layout_tlaps.addWidget(bar_desc_tlaps, 0, 0, 1, 0)

            bar_desc_tmins = QLabel("est. mins")
            bar_desc_tmins.setAlignment(Qt.AlignCenter)
            bar_desc_tmins.setStyleSheet(bar_style_desc)
            layout_tmins.addWidget(bar_desc_tmins, 0, 0, 1, 0)

        # Remaining tyre wear
        if self.wcfg["show_remaining"]:
            self.bar_style_twear = (
                (f"color: {self.wcfg['font_color_remaining']};"
                f"background: {self.wcfg['bkg_color_remaining']};{self.bar_width}"),
                (f"color: {self.wcfg['font_color_warning']};"
                f"background: {self.wcfg['bkg_color_remaining']};{self.bar_width}"),
            )
            self.bar_twear = tuple(QLabel(text_def) for _ in range(4))
            for _bar in self.bar_twear:
                _bar.setAlignment(Qt.AlignCenter)
                _bar.setStyleSheet(self.bar_style_twear[0])

            layout_twear.addWidget(self.bar_twear[0], 1, 0)
            layout_twear.addWidget(self.bar_twear[1], 1, 1)
            layout_twear.addWidget(self.bar_twear[2], 2, 0)
            layout_twear.addWidget(self.bar_twear[3], 2, 1)

        # Tyre wear difference
        if self.wcfg["show_wear_difference"]:
            self.bar_style_tdiff = (
                (f"color: {self.wcfg['font_color_wear_difference']};"
                f"background: {self.wcfg['bkg_color_wear_difference']};{self.bar_width}"),
                (f"color: {self.wcfg['font_color_warning']};"
                f"background: {self.wcfg['bkg_color_wear_difference']};{self.bar_width}"),
            )
            self.bar_tdiff = tuple(QLabel(text_def) for _ in range(4))
            for _bar in self.bar_tdiff:
                _bar.setAlignment(Qt.AlignCenter)
                _bar.setStyleSheet(self.bar_style_tdiff[0])

            layout_tdiff.addWidget(self.bar_tdiff[0], 1, 0)
            layout_tdiff.addWidget(self.bar_tdiff[1], 1, 1)
            layout_tdiff.addWidget(self.bar_tdiff[2], 2, 0)
            layout_tdiff.addWidget(self.bar_tdiff[3], 2, 1)

        # Estimated tyre lifespan in laps
        if self.wcfg["show_lifespan_laps"]:
            self.bar_style_tlaps = (
                (f"color: {self.wcfg['font_color_lifespan_laps']};"
                f"background: {self.wcfg['bkg_color_lifespan_laps']};{self.bar_width}"),
                (f"color: {self.wcfg['font_color_warning']};"
                f"background: {self.wcfg['bkg_color_lifespan_laps']};{self.bar_width}"),
            )
            self.bar_tlaps = tuple(QLabel(text_def) for _ in range(4))
            for _bar in self.bar_tlaps:
                _bar.setAlignment(Qt.AlignCenter)
                _bar.setStyleSheet(self.bar_style_tlaps[0])

            layout_tlaps.addWidget(self.bar_tlaps[0], 1, 0)
            layout_tlaps.addWidget(self.bar_tlaps[1], 1, 1)
            layout_tlaps.addWidget(self.bar_tlaps[2], 2, 0)
            layout_tlaps.addWidget(self.bar_tlaps[3], 2, 1)

        # Estimated tyre lifespan in minutes
        if self.wcfg["show_lifespan_minutes"]:
            self.bar_style_tmins = (
                (f"color: {self.wcfg['font_color_lifespan_minutes']};"
                f"background: {self.wcfg['bkg_color_lifespan_minutes']};{self.bar_width}"),
                (f"color: {self.wcfg['font_color_warning']};"
                f"background: {self.wcfg['bkg_color_lifespan_minutes']};{self.bar_width}"),
            )
            self.bar_tmins = tuple(QLabel(text_def) for _ in range(4))
            for _bar in self.bar_tmins:
                _bar.setAlignment(Qt.AlignCenter)
                _bar.setStyleSheet(self.bar_style_tmins[0])

            layout_tmins.addWidget(self.bar_tmins[0], 1, 0)
            layout_tmins.addWidget(self.bar_tmins[1], 1, 1)
            layout_tmins.addWidget(self.bar_tmins[2], 2, 0)
            layout_tmins.addWidget(self.bar_tmins[3], 2, 1)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_remaining"]:
                layout.addLayout(layout_twear, column_twear, 0)
            if self.wcfg["show_wear_difference"]:
                layout.addLayout(layout_tdiff, column_tdiff, 0)
            if self.wcfg["show_lifespan_laps"]:
                layout.addLayout(layout_tlaps, column_tlaps, 0)
            if self.wcfg["show_lifespan_minutes"]:
                layout.addLayout(layout_tmins, column_tmins, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_remaining"]:
                layout.addLayout(layout_twear, 0, column_twear)
            if self.wcfg["show_wear_difference"]:
                layout.addLayout(layout_tdiff, 0, column_tdiff)
            if self.wcfg["show_lifespan_laps"]:
                layout.addLayout(layout_tlaps, 0, column_tlaps)
            if self.wcfg["show_lifespan_minutes"]:
                layout.addLayout(layout_tmins, 0, column_tmins)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.last_lap_stime = 0        # last lap start time
        self.wear_prev = [0,0,0,0]     # previous moment remaining tyre wear
        self.wear_curr_lap = [0,0,0,0]  # live tyre wear update of current lap
        self.wear_last_lap = [0,0,0,0]  # total tyre wear of last lap

        self.last_wear_curr_lap = [None] * 4
        self.last_wear_last_lap = [None] * 4
        self.last_wear_laps = [None] * 4
        self.last_wear_mins = [None] * 4

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read tyre wear data
            lap_stime = api.read.timing.start()
            lap_etime = api.read.timing.elapsed()
            wear_curr = tuple(map(self.round2decimal, api.read.tyre.wear()))

            if lap_stime != self.last_lap_stime:
                self.wear_last_lap = self.wear_curr_lap
                self.wear_curr_lap = [0,0,0,0]  # reset real time wear
                self.last_lap_stime = lap_stime  # reset time stamp counter

            for idx in range(4):
                # Remaining tyre wear
                if self.wcfg["show_remaining"]:
                    self.update_wear(idx, wear_curr[idx], self.wear_prev[idx])

                # Update tyre wear differences
                self.wear_prev[idx], self.wear_curr_lap[idx] = calc.wear_difference(
                    wear_curr[idx], self.wear_prev[idx], self.wear_curr_lap[idx])

                # Tyre wear differences
                if self.wcfg["show_wear_difference"]:
                    if (self.wcfg["show_live_wear_difference"] and
                        lap_etime - lap_stime > self.freeze_duration):
                        self.update_diff(idx, self.wear_curr_lap[idx], self.last_wear_curr_lap[idx])
                        self.last_wear_curr_lap[idx] = self.wear_curr_lap[idx]
                    else:  # Last lap diff
                        self.update_diff(idx, self.wear_last_lap[idx], self.last_wear_last_lap[idx])
                        self.last_wear_last_lap[idx] = self.wear_last_lap[idx]

                # Estimated tyre lifespan in laps
                if self.wcfg["show_lifespan_laps"]:
                    wear_laps = calc.estimated_laps(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx])
                    self.update_laps(idx, wear_laps, self.last_wear_laps[idx])
                    self.last_wear_laps[idx] = wear_laps

                # Estimated tyre lifespan in minutes
                if self.wcfg["show_lifespan_minutes"]:
                    wear_mins = calc.estimated_mins(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx],
                        minfo.delta.lapTimePace)
                    self.update_mins(idx, wear_mins, self.last_wear_mins[idx])
                    self.last_wear_mins[idx] = wear_mins

        else:
            if self.checked:
                self.checked = False
                self.wear_prev = [0,0,0,0]
                self.wear_curr_lap = [0,0,0,0]
                self.wear_last_lap = [0,0,0,0]

    # GUI update methods
    def update_wear(self, idx, curr, last):
        """Remaining tyre wear"""
        if curr != last:
            self.bar_twear[idx].setText(self.format_num(curr))
            self.bar_twear[idx].setStyleSheet(
                self.bar_style_twear[(curr <= self.wcfg["warning_threshold_remaining"])]
            )

    def update_diff(self, idx, curr, last):
        """Tyre wear differences"""
        if curr != last:
            self.bar_tdiff[idx].setText(f"{curr:.2f}"[:4].rjust(4))
            self.bar_tdiff[idx].setStyleSheet(
                self.bar_style_tdiff[(curr > self.wcfg["warning_threshold_wear"])]
            )

    def update_laps(self, idx, curr, last):
        """Estimated tyre lifespan in laps"""
        if curr != last:
            self.bar_tlaps[idx].setText(self.format_num(curr))
            self.bar_tlaps[idx].setStyleSheet(
                self.bar_style_tlaps[(curr <= self.wcfg["warning_threshold_laps"])]
            )

    def update_mins(self, idx, curr, last):
        """Estimated tyre lifespan in minutes"""
        if curr != last:
            self.bar_tmins[idx].setText(self.format_num(curr))
            self.bar_tmins[idx].setStyleSheet(
                self.bar_style_tmins[(curr <= self.wcfg["warning_threshold_minutes"])]
            )

    # Additional methods
    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(value * 100, 2)

    @staticmethod
    def format_num(value):
        """Format number"""
        if value > 99.9:
            return f"{value:.0f}"
        return f"{value:.1f}"
