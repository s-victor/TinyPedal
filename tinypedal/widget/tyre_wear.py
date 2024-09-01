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
        bar_width = font_m.width * 4 + bar_padx
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        bar_style_desc = (
            f"color: {self.wcfg['font_color_caption']};"
            f"background: {self.wcfg['bkg_color_caption']};"
            f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Remaining tyre wear
        if self.wcfg["show_remaining"]:
            self.bar_style_twear = self.gen_bar_style(
                self.wcfg["font_color_remaining"], self.wcfg["bkg_color_remaining"],
                self.wcfg["font_color_warning"])
            self.bar_twear = self.gen_bar_set(self.bar_style_twear[0], bar_width, text_def)
            layout_twear = self.gen_layout(self.bar_twear)

            if self.wcfg["show_caption"]:
                bar_desc_twear = self.gen_bar_caption(bar_style_desc, "tyre wear")
                layout_twear.addWidget(bar_desc_twear, 0, 0, 1, 0)

            self.arrange_layout(layout, layout_twear, self.wcfg["column_index_remaining"])

        # Tyre wear difference
        if self.wcfg["show_wear_difference"]:
            self.bar_style_tdiff = self.gen_bar_style(
                self.wcfg["font_color_wear_difference"], self.wcfg["bkg_color_wear_difference"],
                self.wcfg["font_color_warning"])
            self.bar_tdiff = self.gen_bar_set(self.bar_style_tdiff[0], bar_width, text_def)
            layout_tdiff = self.gen_layout(self.bar_tdiff)

            if self.wcfg["show_caption"]:
                bar_desc_tdiff = self.gen_bar_caption(bar_style_desc, "wear diff")
                layout_tdiff.addWidget(bar_desc_tdiff, 0, 0, 1, 0)

            self.arrange_layout(layout, layout_tdiff, self.wcfg["column_index_wear_difference"])

        # Estimated tyre lifespan in laps
        if self.wcfg["show_lifespan_laps"]:
            self.bar_style_tlaps = self.gen_bar_style(
                self.wcfg["font_color_lifespan_laps"], self.wcfg["bkg_color_lifespan_laps"],
                self.wcfg["font_color_warning"])
            self.bar_tlaps = self.gen_bar_set(self.bar_style_tlaps[0], bar_width, text_def)
            layout_tlaps = self.gen_layout(self.bar_tlaps)

            if self.wcfg["show_caption"]:
                bar_desc_tlaps = self.gen_bar_caption(bar_style_desc, "est. laps")
                layout_tlaps.addWidget(bar_desc_tlaps, 0, 0, 1, 0)

            self.arrange_layout(layout, layout_tlaps, self.wcfg["column_index_lifespan_laps"])

        # Estimated tyre lifespan in minutes
        if self.wcfg["show_lifespan_minutes"]:
            self.bar_style_tmins = self.gen_bar_style(
                self.wcfg["font_color_lifespan_minutes"], self.wcfg["bkg_color_lifespan_minutes"],
                self.wcfg["font_color_warning"])
            self.bar_tmins = self.gen_bar_set(self.bar_style_tmins[0], bar_width, text_def)
            layout_tmins = self.gen_layout(self.bar_tmins)

            if self.wcfg["show_caption"]:
                bar_desc_tmins = self.gen_bar_caption(bar_style_desc, "est. mins")
                layout_tmins.addWidget(bar_desc_tmins, 0, 0, 1, 0)

            self.arrange_layout(layout, layout_tmins, self.wcfg["column_index_lifespan_minutes"])

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
                    self.update_wear(self.bar_twear[idx], wear_curr[idx], self.wear_prev[idx])

                # Update tyre wear differences
                self.wear_prev[idx], self.wear_curr_lap[idx] = calc.tyre_wear_difference(
                    wear_curr[idx], self.wear_prev[idx], self.wear_curr_lap[idx])

                # Tyre wear differences
                if self.wcfg["show_wear_difference"]:
                    if (self.wcfg["show_live_wear_difference"] and
                        lap_etime - lap_stime > self.freeze_duration):
                        self.update_diff(
                            self.bar_tdiff[idx], self.wear_curr_lap[idx],
                            self.last_wear_curr_lap[idx])
                        self.last_wear_curr_lap[idx] = self.wear_curr_lap[idx]
                    else:  # Last lap diff
                        self.update_diff(
                            self.bar_tdiff[idx], self.wear_last_lap[idx],
                            self.last_wear_last_lap[idx])
                        self.last_wear_last_lap[idx] = self.wear_last_lap[idx]

                # Estimated tyre lifespan in laps
                if self.wcfg["show_lifespan_laps"]:
                    wear_laps = calc.tyre_lifespan_in_laps(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx])
                    self.update_laps(self.bar_tlaps[idx], wear_laps, self.last_wear_laps[idx])
                    self.last_wear_laps[idx] = wear_laps

                # Estimated tyre lifespan in minutes
                if self.wcfg["show_lifespan_minutes"]:
                    wear_mins = calc.tyre_lifespan_in_mins(
                        wear_curr[idx], self.wear_last_lap[idx], self.wear_curr_lap[idx],
                        minfo.delta.lapTimePace)
                    self.update_mins(self.bar_tmins[idx], wear_mins, self.last_wear_mins[idx])
                    self.last_wear_mins[idx] = wear_mins

        else:
            if self.checked:
                self.checked = False
                self.wear_prev = [0,0,0,0]
                self.wear_curr_lap = [0,0,0,0]
                self.wear_last_lap = [0,0,0,0]

    # GUI update methods
    def update_wear(self, target_bar, curr, last):
        """Remaining tyre wear"""
        if curr != last:
            target_bar.setText(self.format_num(curr))
            target_bar.setStyleSheet(
                self.bar_style_twear[curr <= self.wcfg["warning_threshold_remaining"]]
            )

    def update_diff(self, target_bar, curr, last):
        """Tyre wear differences"""
        if curr != last:
            target_bar.setText(self.format_num(curr))
            target_bar.setStyleSheet(
                self.bar_style_tdiff[curr > self.wcfg["warning_threshold_wear"]]
            )

    def update_laps(self, target_bar, curr, last):
        """Estimated tyre lifespan in laps"""
        if curr != last:
            target_bar.setText(self.format_num(curr))
            target_bar.setStyleSheet(
                self.bar_style_tlaps[curr <= self.wcfg["warning_threshold_laps"]]
            )

    def update_mins(self, target_bar, curr, last):
        """Estimated tyre lifespan in minutes"""
        if curr != last:
            target_bar.setText(self.format_num(curr))
            target_bar.setStyleSheet(
                self.bar_style_tmins[curr <= self.wcfg["warning_threshold_minutes"]]
            )

    # GUI generate methods
    @staticmethod
    def gen_bar_style(fg_color, bg_color, highlight_color):
        """Generate bar style"""
        return ((f"color: {fg_color};background: {bg_color}"),
                (f"color: {highlight_color};background: {bg_color}"))

    @staticmethod
    def gen_bar_caption(bar_style, text):
        """Generate caption"""
        bar_temp = QLabel(text)
        bar_temp.setAlignment(Qt.AlignCenter)
        bar_temp.setStyleSheet(bar_style)
        return bar_temp

    @staticmethod
    def gen_bar_set(bar_style, bar_width, text):
        """Generate bar set"""
        bar_set = tuple(QLabel(text) for _ in range(4))
        for bar_temp in bar_set:
            bar_temp.setAlignment(Qt.AlignCenter)
            bar_temp.setStyleSheet(bar_style)
            bar_temp.setMinimumWidth(bar_width)
        return bar_set

    @staticmethod
    def gen_layout(target_bar):
        """Generate layout"""
        layout = QGridLayout()
        layout.setSpacing(0)
        # Start from row index 1; index 0 reserved for caption
        layout.addWidget(target_bar[0], 1, 0)
        layout.addWidget(target_bar[1], 1, 1)
        layout.addWidget(target_bar[2], 2, 0)
        layout.addWidget(target_bar[3], 2, 1)
        return layout

    def arrange_layout(self, layout_main, layout_sub, column_index):
        """Arrange layout"""
        if self.wcfg["layout"] == 0:  # Vertical layout
            layout_main.addLayout(layout_sub, column_index, 0)
        else:  # Horizontal layout
            layout_main.addLayout(layout_sub, 0, column_index)

    # Additional methods
    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(value * 100, 2)

    @staticmethod
    def format_num(value):
        """Format number"""
        return f"{value:.2f}"[:4].strip(".")
