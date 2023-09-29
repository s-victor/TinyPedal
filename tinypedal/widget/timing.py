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
Timing Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget
from ..module_info import minfo

WIDGET_NAME = "timing"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        if self.wcfg["layout"] == 0:
            prefix_w = prefix_just = max(
                len(self.wcfg["prefix_best"]),
                len(self.wcfg["prefix_last"]),
                len(self.wcfg["prefix_current"]),
                len(self.wcfg["prefix_estimated"]),
                len(self.wcfg["prefix_session_best"]),
            )
        else:
            prefix_w = None
            prefix_just = 0

        self.prefix_best = self.wcfg["prefix_best"][:prefix_w].ljust(prefix_just)
        self.prefix_last = self.wcfg["prefix_last"][:prefix_w].ljust(prefix_just)
        self.prefix_curr = self.wcfg["prefix_current"][:prefix_w].ljust(prefix_just)
        self.prefix_esti = self.wcfg["prefix_estimated"][:prefix_w].ljust(prefix_just)
        self.prefix_sbst = self.wcfg["prefix_session_best"][:prefix_w].ljust(prefix_just)

        text_best = f"{self.prefix_best}-:--.---"
        text_last = f"{self.prefix_last}-:--.---"
        text_curr = f"{self.prefix_curr}-:--.---"
        text_est = f"{self.prefix_esti}-:--.---"
        text_sbest = f"{self.prefix_sbst}-:--.---"

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_sbest = self.wcfg["column_index_session_best"]
        column_best = self.wcfg["column_index_best"]
        column_last = self.wcfg["column_index_last"]
        column_curr = self.wcfg["column_index_current"]
        column_est = self.wcfg["column_index_estimated"]

        # Session best laptime
        if self.wcfg["show_session_best"]:
            self.bar_time_sbest = QLabel(text_sbest)
            self.bar_time_sbest.setAlignment(Qt.AlignCenter)
            self.bar_time_sbest.setStyleSheet(
                f"color: {self.wcfg['font_color_session_best']};"
                f"background: {self.wcfg['bkg_color_session_best']};"
            )

        # Personal best laptime
        if self.wcfg["show_best"]:
            self.bar_time_best = QLabel(text_best)
            self.bar_time_best.setAlignment(Qt.AlignCenter)
            self.bar_time_best.setStyleSheet(
                f"color: {self.wcfg['font_color_best']};"
                f"background: {self.wcfg['bkg_color_best']};"
            )

        # Last laptime
        if self.wcfg["show_last"]:
            self.bar_time_last = QLabel(text_last)
            self.bar_time_last.setAlignment(Qt.AlignCenter)
            self.bar_time_last.setStyleSheet(
                f"color: {self.wcfg['font_color_last']};"
                f"background: {self.wcfg['bkg_color_last']};"
            )

        # Current laptime
        if self.wcfg["show_current"]:
            self.bar_time_curr = QLabel(text_curr)
            self.bar_time_curr.setAlignment(Qt.AlignCenter)
            self.bar_time_curr.setStyleSheet(
                f"color: {self.wcfg['font_color_current']};"
                f"background: {self.wcfg['bkg_color_current']};"
            )

        # Estimated laptime
        if self.wcfg["show_estimated"]:
            self.bar_time_est = QLabel(text_est)
            self.bar_time_est.setAlignment(Qt.AlignCenter)
            self.bar_time_est.setStyleSheet(
                f"color: {self.wcfg['font_color_estimated']};"
                f"background: {self.wcfg['bkg_color_estimated']};"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_session_best"]:
                layout.addWidget(self.bar_time_sbest, column_sbest, 0)
            if self.wcfg["show_best"]:
                layout.addWidget(self.bar_time_best, column_best, 0)
            if self.wcfg["show_last"]:
                layout.addWidget(self.bar_time_last, column_last, 0)
            if self.wcfg["show_current"]:
                layout.addWidget(self.bar_time_curr, column_curr, 0)
            if self.wcfg["show_estimated"]:
                layout.addWidget(self.bar_time_est, column_est, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_session_best"]:
                layout.addWidget(self.bar_time_sbest, 0, column_sbest)
            if self.wcfg["show_best"]:
                layout.addWidget(self.bar_time_best, 0, column_best)
            if self.wcfg["show_last"]:
                layout.addWidget(self.bar_time_last, 0, column_last)
            if self.wcfg["show_current"]:
                layout.addWidget(self.bar_time_curr, 0, column_curr)
            if self.wcfg["show_estimated"]:
                layout.addWidget(self.bar_time_est, 0, column_est)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.vehicle_counter = 0
        self.laptime_sbest = MAGIC_NUM

        self.last_laptime_sbest = 0
        self.last_laptime_best = 0
        self.last_laptime_last = (0,0)
        self.last_laptime_curr = 0
        self.last_laptime_est = 0

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Reset switch
            if not self.checked:
                self.checked = True

            # Session best laptime
            if self.wcfg["show_session_best"]:
                veh_total, laptime_opt, is_same_class = read_data.timing(self.vehicle_counter)

                if 0 < laptime_opt < self.laptime_sbest:
                    if self.wcfg["show_session_best_from_same_class_only"] and is_same_class:
                        self.laptime_sbest = laptime_opt
                    elif not self.wcfg["show_session_best_from_same_class_only"]:
                        self.laptime_sbest = laptime_opt

                if self.vehicle_counter < max(veh_total, 1):
                    self.vehicle_counter += 1
                else:
                    self.vehicle_counter = 0

                self.update_laptime(self.laptime_sbest, self.last_laptime_sbest,
                                    self.prefix_sbst, "sbest")
                self.last_laptime_sbest = self.laptime_sbest

            # Personal best laptime
            if self.wcfg["show_best"]:
                laptime_best = minfo.delta.LaptimeBest
                self.update_laptime(laptime_best, self.last_laptime_best,
                                    self.prefix_best, "best")
                self.last_laptime_best = laptime_best

            # Last laptime
            if self.wcfg["show_last"]:
                laptime_last = (minfo.delta.LaptimeLast,
                                minfo.delta.IsValidLap)
                self.update_last_laptime(laptime_last, self.last_laptime_last,
                                         self.prefix_last)
                self.last_laptime_last = laptime_last

            # Current laptime
            if self.wcfg["show_current"]:
                laptime_curr = minfo.delta.LaptimeCurrent
                self.update_laptime(laptime_curr, self.last_laptime_curr,
                                    self.prefix_curr, "curr")
                self.last_laptime_curr = laptime_curr

            # Estimated laptime
            if self.wcfg["show_estimated"]:
                laptime_est = minfo.delta.LaptimeEstimated
                self.update_laptime(laptime_est, self.last_laptime_est,
                                    self.prefix_esti, "est")
                self.last_laptime_est = laptime_est

        else:
            if self.checked:
                self.checked = False
                self.laptime_sbest = MAGIC_NUM  # reset laptime

    # GUI update methods
    def update_laptime(self, curr, last, prefix, suffix):
        """Update laptime"""
        if curr != last:
            if 0 < curr < MAGIC_NUM:
                text = f"{prefix}{calc.sec2laptime(curr)[:8].rjust(8)}"
            else:
                text = f"{prefix}-:--.---"
            getattr(self, f"bar_time_{suffix}").setText(text)

    def update_last_laptime(self, curr, last, prefix):
        """Update last laptime"""
        if curr != last:
            if 0 < curr[0] < MAGIC_NUM:
                text = f"{prefix}{calc.sec2laptime(curr[0])[:8].rjust(8)}"
            else:
                text = f"{prefix}-:--.---"
            if curr[1]:
                color = (f"color: {self.wcfg['font_color_last']};"
                         f"background: {self.wcfg['bkg_color_last']};")
            else:
                color = (f"color: {self.wcfg['font_color_invalid_laptime']};"
                         f"background: {self.wcfg['bkg_color_last']};")
            self.bar_time_last.setText(text)
            self.bar_time_last.setStyleSheet(
                f"{color}")
