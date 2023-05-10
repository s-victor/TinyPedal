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
Lap time history Widget
"""

import copy
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "lap_time_history"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Max display laps
        self.laps_count = max(self.wcfg["lap_time_history_count"], 1) + 1

        # Create layout
        layout = QGridLayout()
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_lp = self.wcfg["column_index_laps"]
        column_tm = self.wcfg["column_index_time"]
        column_fu = self.wcfg["column_index_fuel"]
        column_wr = self.wcfg["column_index_wear"]

        # Laps
        self.bar_laps = QLabel("---")
        self.bar_laps.setAlignment(Qt.AlignCenter)
        self.bar_laps.setStyleSheet(
            f"color: {self.wcfg['font_color_laps']};"
            f"background: {self.wcfg['bkg_color_laps']};"
        )
        # Time
        self.bar_time = QLabel("-:--.---")
        self.bar_time.setAlignment(Qt.AlignCenter)
        self.bar_time.setStyleSheet(
            f"color: {self.wcfg['font_color_time']};"
            f"background: {self.wcfg['bkg_color_time']};"
        )
        # Fuel
        self.bar_fuel = QLabel("-.--")
        self.bar_fuel.setAlignment(Qt.AlignCenter)
        self.bar_fuel.setStyleSheet(
            f"color: {self.wcfg['font_color_fuel']};"
            f"background: {self.wcfg['bkg_color_fuel']};"
        )
        # Tyre wear
        self.bar_wear = QLabel("---")
        self.bar_wear.setAlignment(Qt.AlignCenter)
        self.bar_wear.setStyleSheet(
            f"color: {self.wcfg['font_color_wear']};"
            f"background: {self.wcfg['bkg_color_wear']};"
        )
        layout.addWidget(self.bar_laps, self.set_row_index(0), column_lp)
        layout.addWidget(self.bar_time, self.set_row_index(0), column_tm)
        layout.addWidget(self.bar_fuel, self.set_row_index(0), column_fu)
        layout.addWidget(self.bar_wear, self.set_row_index(0), column_wr)

        # History laps
        for index in range(1, self.laps_count):
            setattr(self, f"bar_last_laps{index}", QLabel("---"))
            getattr(self, f"bar_last_laps{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_laps{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_laps']};"
                f"background: {self.wcfg['bkg_color_last_laps']};"
            )
            setattr(self, f"bar_last_time{index}", QLabel("-:--.---"))
            getattr(self, f"bar_last_time{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_time{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_time']};"
                f"background: {self.wcfg['bkg_color_last_time']};"
            )
            setattr(self, f"bar_last_fuel{index}", QLabel("-.--"))
            getattr(self, f"bar_last_fuel{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_fuel{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_fuel']};"
                f"background: {self.wcfg['bkg_color_last_fuel']};"
            )
            setattr(self, f"bar_last_wear{index}", QLabel("---"))
            getattr(self, f"bar_last_wear{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_wear{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_wear']};"
                f"background: {self.wcfg['bkg_color_last_wear']};"
            )

            if not self.wcfg["show_empty_history"]:
                getattr(self, f"bar_last_laps{index}").hide()
                getattr(self, f"bar_last_time{index}").hide()
                getattr(self, f"bar_last_fuel{index}").hide()
                getattr(self, f"bar_last_wear{index}").hide()

            layout.addWidget(
                getattr(self, f"bar_last_laps{index}"), self.set_row_index(index), column_lp)
            layout.addWidget(
                getattr(self, f"bar_last_time{index}"), self.set_row_index(index), column_tm)
            layout.addWidget(
                getattr(self, f"bar_last_fuel{index}"), self.set_row_index(index), column_fu)
            layout.addWidget(
                getattr(self, f"bar_last_wear{index}"), self.set_row_index(index), column_wr)

        # Set layout
        self.setLayout(layout)

        # Last data
        self.last_lap_stime = 0  # last lap start time
        self.laps_data = [[0,[0,0],0,0] for _ in range(self.laps_count)]
        self.last_data = copy.deepcopy(self.laps_data)

        self.last_wear = 0

        self.last_laps_text = None
        self.last_time_text = None
        self.last_fuel_text = None
        self.last_wear_text = None

        # Start updating
        self.update_data()

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    def set_row_index(self, index):
        """Set row index"""
        if self.wcfg["layout"] == 0:
            return index
        return self.laps_count - index

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read laps data
            lap_stime, lap_etime = read_data.lap_timestamp()
            wear_avg = 100 - (sum(read_data.wear()) * 25)

            if lap_stime != self.last_lap_stime:  # time stamp difference
                if 2 < lap_etime - lap_stime < 10:  # update 2s after cross line
                    self.last_wear = wear_avg
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.laps_data[0][1] = (mctrl.module_delta.output.LaptimeLast,
                                            mctrl.module_delta.output.IsValidLap)
                    self.laps_data[0][2] = mctrl.module_fuel.output.LastLapFuelConsumption
                    self.store_last_data()

            # Current laps data
            self.laps_data[0][0] = read_data.lap_number()
            self.laps_data[0][1] = mctrl.module_delta.output.LaptimeEstimated, 0
            self.laps_data[0][2] = mctrl.module_fuel.output.EstimatedFuelConsumption
            self.laps_data[0][3] = max(wear_avg - self.last_wear, 0)

            laps_text = f"{self.laps_data[0][0]:03.0f}"[:3].ljust(3)
            self.update_laps("laps", laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2laptime_full(self.laps_data[0][1][0])[:8].rjust(8)
            self.update_laps("time", time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{self.laps_data[0][2]:04.02f}"[:4].rjust(4)
            self.update_laps("fuel", fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            wear_text = f"{self.laps_data[0][3]:.01f}"[:3].rjust(3)
            self.update_laps("wear", wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

            # Lap time history
            for index in range(1, self.laps_count):
                self.update_laps_history(
                    self.laps_data[-index], self.last_data[-index], index)
            self.last_data = copy.deepcopy(self.laps_data)

    # GUI update methods
    def update_laps(self, suffix, curr, last):
        """Laps data"""
        if curr != last:
            getattr(self, f"bar_{suffix}").setText(curr)

    def update_laps_history(self, curr, last, index):
        """Laps history data"""
        if curr != last:
            if curr[1][0] and curr[0] != last[0]:
                getattr(self, f"bar_last_laps{index}").setText(
                    f"{max(curr[0] - 1, 0):03.0f}"[:3].ljust(3)
                )
                getattr(self, f"bar_last_time{index}").setText(
                    calc.sec2laptime_full(curr[1][0])[:8].rjust(8)
                )
                getattr(self, f"bar_last_fuel{index}").setText(
                    f"{curr[2]:04.02f}"[:4].rjust(4)
                )
                getattr(self, f"bar_last_wear{index}").setText(
                    f"{curr[3]:.01f}"[:3].rjust(3)
                )

                if curr[1][1]:
                    fgcolor = self.wcfg["font_color_last_time"]
                else:
                    fgcolor = self.wcfg["font_color_invalid_laptime"]
                getattr(self, f"bar_last_time{index}").setStyleSheet(
                    f"color: {fgcolor};"
                    f"background: {self.wcfg['bkg_color_last_time']};"
                )

                getattr(self, f"bar_last_laps{index}").show()
                getattr(self, f"bar_last_time{index}").show()
                getattr(self, f"bar_last_fuel{index}").show()
                getattr(self, f"bar_last_wear{index}").show()

            elif not self.wcfg["show_empty_history"]:
                getattr(self, f"bar_last_laps{index}").hide()
                getattr(self, f"bar_last_time{index}").hide()
                getattr(self, f"bar_last_fuel{index}").hide()
                getattr(self, f"bar_last_wear{index}").hide()

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def store_last_data(self):
        """Store last laps data"""
        self.laps_data.pop(1)  # remove old data
        self.laps_data.append(
            [self.laps_data[0][0],
             self.laps_data[0][1],
             self.laps_data[0][2],
             self.laps_data[0][3]
            ])
