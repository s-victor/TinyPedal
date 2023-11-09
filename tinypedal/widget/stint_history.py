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
Stint history Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from ..api_control import api
from ..base import Widget
from ..module_info import minfo

WIDGET_NAME = "stint_history"


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

        # Max display stint
        self.stint_count = max(self.wcfg["stint_history_count"], 1) + 1

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_lp = self.wcfg["column_index_laps"]
        column_tm = self.wcfg["column_index_time"]
        column_fu = self.wcfg["column_index_fuel"]
        column_tr = self.wcfg["column_index_tyre"]
        column_wr = self.wcfg["column_index_wear"]

        # Laps
        self.bar_laps = QLabel("---")
        self.bar_laps.setAlignment(Qt.AlignCenter)
        self.bar_laps.setStyleSheet(
            f"color: {self.wcfg['font_color_laps']};"
            f"background: {self.wcfg['bkg_color_laps']};"
        )
        # Time
        self.bar_time = QLabel("--:--")
        self.bar_time.setAlignment(Qt.AlignCenter)
        self.bar_time.setStyleSheet(
            f"color: {self.wcfg['font_color_time']};"
            f"background: {self.wcfg['bkg_color_time']};"
        )
        # Fuel
        self.bar_fuel = QLabel("---.-")
        self.bar_fuel.setAlignment(Qt.AlignCenter)
        self.bar_fuel.setStyleSheet(
            f"color: {self.wcfg['font_color_fuel']};"
            f"background: {self.wcfg['bkg_color_fuel']};"
        )
        # Tyre compound
        self.bar_cmpd = QLabel("--")
        self.bar_cmpd.setAlignment(Qt.AlignCenter)
        self.bar_cmpd.setStyleSheet(
            f"color: {self.wcfg['font_color_tyre']};"
            f"background: {self.wcfg['bkg_color_tyre']};"
        )
        # Tyre wear
        self.bar_wear = QLabel("--%")
        self.bar_wear.setAlignment(Qt.AlignCenter)
        self.bar_wear.setStyleSheet(
            f"color: {self.wcfg['font_color_wear']};"
            f"background: {self.wcfg['bkg_color_wear']};"
        )
        layout.addWidget(self.bar_laps, self.set_row_index(0), column_lp)
        layout.addWidget(self.bar_time, self.set_row_index(0), column_tm)
        layout.addWidget(self.bar_fuel, self.set_row_index(0), column_fu)
        layout.addWidget(self.bar_cmpd, self.set_row_index(0), column_tr)
        layout.addWidget(self.bar_wear, self.set_row_index(0), column_wr)

        # History stint
        for index in range(1, self.stint_count):
            setattr(self, f"bar_last_laps{index}", QLabel("---"))
            getattr(self, f"bar_last_laps{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_laps{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_laps']};"
                f"background: {self.wcfg['bkg_color_last_stint_laps']};"
            )
            setattr(self, f"bar_last_time{index}", QLabel("--:--"))
            getattr(self, f"bar_last_time{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_time{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_time']};"
                f"background: {self.wcfg['bkg_color_last_stint_time']};"
            )
            setattr(self, f"bar_last_fuel{index}", QLabel("---.-"))
            getattr(self, f"bar_last_fuel{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_fuel{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_fuel']};"
                f"background: {self.wcfg['bkg_color_last_stint_fuel']};"
            )
            setattr(self, f"bar_last_cmpd{index}", QLabel("--"))
            getattr(self, f"bar_last_cmpd{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_cmpd{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_tyre']};"
                f"background: {self.wcfg['bkg_color_last_stint_tyre']};"
            )
            setattr(self, f"bar_last_wear{index}", QLabel("---"))
            getattr(self, f"bar_last_wear{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_wear{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_wear']};"
                f"background: {self.wcfg['bkg_color_last_stint_wear']};"
            )

            if not self.wcfg["show_empty_history"]:
                getattr(self, f"bar_last_laps{index}").hide()
                getattr(self, f"bar_last_time{index}").hide()
                getattr(self, f"bar_last_fuel{index}").hide()
                getattr(self, f"bar_last_cmpd{index}").hide()
                getattr(self, f"bar_last_wear{index}").hide()

            layout.addWidget(
                getattr(self, f"bar_last_laps{index}"),
                        self.set_row_index(index), column_lp)
            layout.addWidget(
                getattr(self, f"bar_last_time{index}"),
                        self.set_row_index(index), column_tm)
            layout.addWidget(
                getattr(self, f"bar_last_fuel{index}"),
                        self.set_row_index(index), column_fu)
            layout.addWidget(
                getattr(self, f"bar_last_cmpd{index}"),
                        self.set_row_index(index), column_tr)
            layout.addWidget(
                getattr(self, f"bar_last_wear{index}"),
                        self.set_row_index(index), column_wr)

        # Set layout
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.stint_running = False  # check whether current stint running
        self.reset_stint = True  # reset stint stats

        self.stint_data = [["--",0,0,0,0] for _ in range(self.stint_count)]
        self.last_stint_data = [data.copy() for data in self.stint_data]

        self.start_laps = 0
        self.start_time = 0
        self.start_fuel = 0
        self.start_wear = 0

        self.last_wear_avg = 0
        self.last_fuel_curr = 0

        self.last_laps_text = None
        self.last_time_text = None
        self.last_fuel_text = None
        self.last_cmpd_text = None
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
        return self.stint_count - index

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read stint data
            lap_num = api.read.lap.number()
            time_curr = api.read.session.elapsed()
            in_pits = api.read.vehicle.in_pits()
            in_garage = api.read.vehicle.in_garage()

            wear_avg = 100 - (sum(api.read.tyre.wear()) * 25)
            fuel_curr = self.fuel_units(minfo.fuel.amountFuelCurrent)

            if not in_pits:
                self.last_fuel_curr = fuel_curr
                self.last_wear_avg = wear_avg
                self.stint_running = True
            elif in_pits and self.stint_running:
                if self.last_wear_avg > wear_avg or self.last_fuel_curr < fuel_curr:
                    self.store_last_data()
                    self.stint_running = False
                    self.reset_stint = True

            if in_garage:
                self.reset_stint = True

            # Current stint data
            self.stint_data[0][0] = self.set_tyre_cmp(api.read.tyre.compound())
            self.stint_data[0][1] = max(lap_num - self.start_laps, 0)
            self.stint_data[0][2] = max(time_curr - self.start_time, 0)
            self.stint_data[0][3] = max(self.start_fuel - fuel_curr, 0)
            self.stint_data[0][4] = max(wear_avg - self.start_wear, 0)

            if self.reset_stint:
                self.start_laps = lap_num
                self.start_time = time_curr
                self.start_fuel = fuel_curr
                self.start_wear = wear_avg
                self.reset_stint = False

            if self.start_fuel < fuel_curr:
                self.start_fuel = fuel_curr

            # Stint current
            laps_text = f"{self.stint_data[0][1]:03.0f}"[:3].ljust(3)
            self.update_stint("laps", laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2stinttime(self.stint_data[0][2])[:5].ljust(5)
            self.update_stint("time", time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{self.stint_data[0][3]:05.01f}"[:5].ljust(5)
            self.update_stint("fuel", fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            cmpd_text = f"{self.stint_data[0][0]}"[:2].ljust(2)
            self.update_stint("cmpd", cmpd_text, self.last_cmpd_text)
            self.last_cmpd_text = cmpd_text

            wear_text = f"{self.stint_data[0][4]:02.0f}%"[:3].ljust(3)
            self.update_stint("wear", wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

            # Stint history
            for index in range(1, self.stint_count):
                self.update_stint_history(
                    self.stint_data[-index], self.last_stint_data[-index], index)
            self.last_stint_data = [data.copy() for data in self.stint_data]

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

                if self.stint_data[0][2] >= self.wcfg["minimum_stint_threshold_minutes"] * 60:
                    self.store_last_data()

    # GUI update methods
    def update_stint(self, suffix, curr, last):
        """Stint data"""
        if curr != last:
            getattr(self, f"bar_{suffix}").setText(curr)

    def update_stint_history(self, curr, last, index):
        """Stint history data"""
        if curr != last:
            if curr[2]:
                getattr(self, f"bar_last_laps{index}").setText(
                    f"{curr[1]:03.0f}"[:3].ljust(3)
                )
                getattr(self, f"bar_last_time{index}").setText(
                    calc.sec2stinttime(curr[2])[:5].ljust(5)
                )
                getattr(self, f"bar_last_fuel{index}").setText(
                    f"{curr[3]:05.01f}"[:5].ljust(5)
                )
                getattr(self, f"bar_last_cmpd{index}").setText(
                    f"{curr[0]}"[:2].ljust(2)
                )
                getattr(self, f"bar_last_wear{index}").setText(
                    f"{curr[4]:02.0f}%"[:3].ljust(3)
                )
                getattr(self, f"bar_last_laps{index}").show()
                getattr(self, f"bar_last_time{index}").show()
                getattr(self, f"bar_last_fuel{index}").show()
                getattr(self, f"bar_last_cmpd{index}").show()
                getattr(self, f"bar_last_wear{index}").show()

            elif not self.wcfg["show_empty_history"]:
                getattr(self, f"bar_last_laps{index}").hide()
                getattr(self, f"bar_last_time{index}").hide()
                getattr(self, f"bar_last_fuel{index}").hide()
                getattr(self, f"bar_last_cmpd{index}").hide()
                getattr(self, f"bar_last_wear{index}").hide()

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def set_tyre_cmp(self, tc_index):
        """Substitute tyre compound index with custom chars"""
        ftire = self.wcfg["tyre_compound_list"][tc_index[0]:(tc_index[0]+1)]
        rtire = self.wcfg["tyre_compound_list"][tc_index[1]:(tc_index[1]+1)]
        return f"{ftire}{rtire}"

    def store_last_data(self):
        """Store last stint data"""
        self.stint_data.pop(1)  # remove old data
        self.stint_data.append(self.stint_data[0].copy())
