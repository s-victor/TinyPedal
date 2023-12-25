#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from . import Overlay
from ..module_info import minfo

WIDGET_NAME = "timing"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

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
                len(self.wcfg["prefix_session_personal_best"]),
            )
        else:
            prefix_w = None
            prefix_just = 0

        self.prefix_best = self.wcfg["prefix_best"][:prefix_w].ljust(prefix_just)
        self.prefix_last = self.wcfg["prefix_last"][:prefix_w].ljust(prefix_just)
        self.prefix_curr = self.wcfg["prefix_current"][:prefix_w].ljust(prefix_just)
        self.prefix_esti = self.wcfg["prefix_estimated"][:prefix_w].ljust(prefix_just)
        self.prefix_sbst = self.wcfg["prefix_session_best"][:prefix_w].ljust(prefix_just)
        self.prefix_spbt = self.wcfg["prefix_session_personal_best"][:prefix_w].ljust(prefix_just)

        time_none = "-:--.---"

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

        column_sbst = self.wcfg["column_index_session_best"]
        column_best = self.wcfg["column_index_best"]
        column_last = self.wcfg["column_index_last"]
        column_curr = self.wcfg["column_index_current"]
        column_esti = self.wcfg["column_index_estimated"]
        column_spbt = self.wcfg["column_index_session_personal_best"]

        # Session best laptime
        if self.wcfg["show_session_best"]:
            self.bar_time_sbst = QLabel(f"{self.prefix_sbst}{time_none}")
            self.bar_time_sbst.setAlignment(Qt.AlignCenter)
            self.bar_time_sbst.setStyleSheet(
                f"color: {self.wcfg['font_color_session_best']};"
                f"background: {self.wcfg['bkg_color_session_best']};"
            )

        # Personal best laptime
        if self.wcfg["show_best"]:
            self.bar_time_best = QLabel(f"{self.prefix_best}{time_none}")
            self.bar_time_best.setAlignment(Qt.AlignCenter)
            self.bar_time_best.setStyleSheet(
                f"color: {self.wcfg['font_color_best']};"
                f"background: {self.wcfg['bkg_color_best']};"
            )

        # Last laptime
        if self.wcfg["show_last"]:
            self.bar_time_last = QLabel(f"{self.prefix_last}{time_none}")
            self.bar_time_last.setAlignment(Qt.AlignCenter)
            self.bar_time_last.setStyleSheet(
                f"color: {self.wcfg['font_color_last']};"
                f"background: {self.wcfg['bkg_color_last']};"
            )

        # Current laptime
        if self.wcfg["show_current"]:
            self.bar_time_curr = QLabel(f"{self.prefix_curr}{time_none}")
            self.bar_time_curr.setAlignment(Qt.AlignCenter)
            self.bar_time_curr.setStyleSheet(
                f"color: {self.wcfg['font_color_current']};"
                f"background: {self.wcfg['bkg_color_current']};"
            )

        # Estimated laptime
        if self.wcfg["show_estimated"]:
            self.bar_time_esti = QLabel(f"{self.prefix_esti}{time_none}")
            self.bar_time_esti.setAlignment(Qt.AlignCenter)
            self.bar_time_esti.setStyleSheet(
                f"color: {self.wcfg['font_color_estimated']};"
                f"background: {self.wcfg['bkg_color_estimated']};"
            )

        # Session personal best laptime
        if self.wcfg["show_session_personal_best"]:
            self.bar_time_spbt = QLabel(f"{self.prefix_spbt}{time_none}")
            self.bar_time_spbt.setAlignment(Qt.AlignCenter)
            self.bar_time_spbt.setStyleSheet(
                f"color: {self.wcfg['font_color_session_personal_best']};"
                f"background: {self.wcfg['bkg_color_session_personal_best']};"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_session_best"]:
                layout.addWidget(self.bar_time_sbst, column_sbst, 0)
            if self.wcfg["show_best"]:
                layout.addWidget(self.bar_time_best, column_best, 0)
            if self.wcfg["show_last"]:
                layout.addWidget(self.bar_time_last, column_last, 0)
            if self.wcfg["show_current"]:
                layout.addWidget(self.bar_time_curr, column_curr, 0)
            if self.wcfg["show_estimated"]:
                layout.addWidget(self.bar_time_esti, column_esti, 0)
            if self.wcfg["show_session_personal_best"]:
                layout.addWidget(self.bar_time_spbt, column_spbt, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_session_best"]:
                layout.addWidget(self.bar_time_sbst, 0, column_sbst)
            if self.wcfg["show_best"]:
                layout.addWidget(self.bar_time_best, 0, column_best)
            if self.wcfg["show_last"]:
                layout.addWidget(self.bar_time_last, 0, column_last)
            if self.wcfg["show_current"]:
                layout.addWidget(self.bar_time_curr, 0, column_curr)
            if self.wcfg["show_estimated"]:
                layout.addWidget(self.bar_time_esti, 0, column_esti)
            if self.wcfg["show_session_personal_best"]:
                layout.addWidget(self.bar_time_spbt, 0, column_spbt)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.vehicle_counter = 0
        self.laptime_sbst = MAGIC_NUM

        self.last_laptime_sbst = 0
        self.last_laptime_best = 0
        self.last_laptime_last = (0,0)
        self.last_laptime_curr = 0
        self.last_laptime_esti = 0
        self.last_laptime_spbt = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Session best laptime
            if self.wcfg["show_session_best"]:
                veh_total = api.read.vehicle.total_vehicles()
                laptime_best_tmp = api.read.timing.best_laptime(self.vehicle_counter)
                same_vehicle_class = api.read.vehicle.same_class(self.vehicle_counter)

                if 0 < laptime_best_tmp < self.laptime_sbst:
                    if self.wcfg["show_session_best_from_same_class_only"] and same_vehicle_class:
                        self.laptime_sbst = laptime_best_tmp
                    elif not self.wcfg["show_session_best_from_same_class_only"]:
                        self.laptime_sbst = laptime_best_tmp

                if self.vehicle_counter < veh_total:
                    self.vehicle_counter += 1
                else:
                    self.vehicle_counter = 0

                self.update_laptime(self.laptime_sbst, self.last_laptime_sbst,
                                    self.prefix_sbst, "sbst")
                self.last_laptime_sbst = self.laptime_sbst

            # Personal best laptime
            if self.wcfg["show_best"]:
                laptime_best = minfo.delta.lapTimeBest
                self.update_laptime(laptime_best, self.last_laptime_best,
                                    self.prefix_best, "best")
                self.last_laptime_best = laptime_best

            # Last laptime
            if self.wcfg["show_last"]:
                laptime_last = (minfo.delta.lapTimeLast,
                                minfo.delta.isValidLap)
                self.update_last_laptime(laptime_last, self.last_laptime_last,
                                         self.prefix_last)
                self.last_laptime_last = laptime_last

            # Current laptime
            if self.wcfg["show_current"]:
                laptime_curr = minfo.delta.lapTimeCurrent
                self.update_laptime(laptime_curr, self.last_laptime_curr,
                                    self.prefix_curr, "curr")
                self.last_laptime_curr = laptime_curr

            # Estimated laptime
            if self.wcfg["show_estimated"]:
                laptime_esti = minfo.delta.lapTimeEstimated
                self.update_laptime(laptime_esti, self.last_laptime_esti,
                                    self.prefix_esti, "esti")
                self.last_laptime_esti = laptime_esti

            # Session personal best laptime
            if self.wcfg["show_session_personal_best"]:
                laptime_spbt = api.read.timing.best_laptime()
                self.update_laptime(laptime_spbt, self.last_laptime_spbt,
                                    self.prefix_spbt, "spbt")
                self.last_laptime_spbt = laptime_spbt

        else:
            if self.checked:
                self.checked = False
                self.laptime_sbst = MAGIC_NUM  # reset laptime

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
