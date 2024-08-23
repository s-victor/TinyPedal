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
Stint history Widget
"""

from collections import deque

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "stint_history"


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
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")
        self.bar_width_laps = f"min-width: {font_m.width * 3 + bar_padx}px;"
        self.bar_width_time = f"min-width: {font_m.width * 5 + bar_padx}px;"
        self.bar_width_fuel = f"min-width: {font_m.width * 5 + bar_padx}px;"
        self.bar_width_cmpd = f"min-width: {font_m.width * 2 + bar_padx}px;"
        self.bar_width_wear = f"min-width: {font_m.width * 3 + bar_padx}px;"

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Max display stint
        self.stint_count = max(self.wcfg["stint_history_count"], 1)

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
            f"{self.bar_width_laps}"
        )
        # Time
        self.bar_time = QLabel("--:--")
        self.bar_time.setAlignment(Qt.AlignCenter)
        self.bar_time.setStyleSheet(
            f"color: {self.wcfg['font_color_time']};"
            f"background: {self.wcfg['bkg_color_time']};"
            f"{self.bar_width_time}"
        )
        # Fuel
        self.bar_fuel = QLabel("---.-")
        self.bar_fuel.setAlignment(Qt.AlignCenter)
        self.bar_fuel.setStyleSheet(
            f"color: {self.wcfg['font_color_fuel']};"
            f"background: {self.wcfg['bkg_color_fuel']};"
            f"{self.bar_width_fuel}"
        )
        # Tyre compound
        self.bar_cmpd = QLabel("--")
        self.bar_cmpd.setAlignment(Qt.AlignCenter)
        self.bar_cmpd.setStyleSheet(
            f"color: {self.wcfg['font_color_tyre']};"
            f"background: {self.wcfg['bkg_color_tyre']};"
            f"{self.bar_width_cmpd}"
        )
        # Tyre wear
        self.bar_wear = QLabel("--%")
        self.bar_wear.setAlignment(Qt.AlignCenter)
        self.bar_wear.setStyleSheet(
            f"color: {self.wcfg['font_color_wear']};"
            f"background: {self.wcfg['bkg_color_wear']};"
            f"{self.bar_width_wear}"
        )
        layout.addWidget(self.bar_laps, self.set_row_index(0), column_lp)
        layout.addWidget(self.bar_time, self.set_row_index(0), column_tm)
        layout.addWidget(self.bar_fuel, self.set_row_index(0), column_fu)
        layout.addWidget(self.bar_cmpd, self.set_row_index(0), column_tr)
        layout.addWidget(self.bar_wear, self.set_row_index(0), column_wr)

        # History stint
        for index in range(1, self.stint_count + 1):
            setattr(self, f"bar_last_laps{index}", QLabel("---"))
            getattr(self, f"bar_last_laps{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_laps{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_laps']};"
                f"background: {self.wcfg['bkg_color_last_stint_laps']};"
                f"{self.bar_width_laps}"
            )
            setattr(self, f"bar_last_time{index}", QLabel("--:--"))
            getattr(self, f"bar_last_time{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_time{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_time']};"
                f"background: {self.wcfg['bkg_color_last_stint_time']};"
                f"{self.bar_width_time}"
            )
            setattr(self, f"bar_last_fuel{index}", QLabel("---.-"))
            getattr(self, f"bar_last_fuel{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_fuel{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_fuel']};"
                f"background: {self.wcfg['bkg_color_last_stint_fuel']};"
                f"{self.bar_width_fuel}"
            )
            setattr(self, f"bar_last_cmpd{index}", QLabel("--"))
            getattr(self, f"bar_last_cmpd{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_cmpd{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_tyre']};"
                f"background: {self.wcfg['bkg_color_last_stint_tyre']};"
                f"{self.bar_width_cmpd}"
            )
            setattr(self, f"bar_last_wear{index}", QLabel("---"))
            getattr(self, f"bar_last_wear{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_last_wear{index}").setStyleSheet(
                f"color: {self.wcfg['font_color_last_stint_wear']};"
                f"background: {self.wcfg['bkg_color_last_stint_wear']};"
                f"{self.bar_width_wear}"
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
        # 0 - tyre compound, 1 - total laps, 2 - total time, 3 - total fuel, 4 - total tyre wear
        self.stint_data = ["--",0,0,0,0]
        self.history_data = deque([["--",0,0,0,0] for _ in range(self.stint_count)], self.stint_count)

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

    def set_row_index(self, index):
        """Set row index"""
        if self.wcfg["layout"] == 0:
            return index
        return self.stint_count - index + 1

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True
                for index in range(self.stint_count):
                    self.update_stint_history(self.history_data[index], index + 1)

            # Read stint data
            lap_num = api.read.lap.number()
            time_curr = api.read.session.elapsed()
            in_pits = api.read.vehicle.in_pits()
            in_garage = api.read.vehicle.in_garage()

            wear_avg = 100 - sum(api.read.tyre.wear()) * 25

            # Check if virtual energy available
            if self.wcfg["show_virtual_energy_if_available"] and minfo.restapi.maxVirtualEnergy:
                fuel_curr = minfo.energy.amountCurrent
            else:
                fuel_curr = self.fuel_units(minfo.fuel.amountCurrent)

            if not in_pits:
                self.last_fuel_curr = fuel_curr
                self.last_wear_avg = wear_avg
                self.stint_running = True
            elif in_pits and self.stint_running:
                if self.last_wear_avg > wear_avg or self.last_fuel_curr < fuel_curr:
                    self.stint_running = False
                    self.reset_stint = True
                    # Update stint history
                    self.history_data.appendleft(self.stint_data.copy())
                    for index in range(self.stint_count):
                        self.update_stint_history(self.history_data[index], index + 1)

            if in_garage:
                self.reset_stint = True

            # Current stint data
            self.stint_data[0] = self.set_tyre_cmp(api.read.tyre.compound())
            self.stint_data[1] = max(lap_num - self.start_laps, 0)
            self.stint_data[2] = max(time_curr - self.start_time, 0)
            self.stint_data[3] = max(self.start_fuel - fuel_curr, 0)
            self.stint_data[4] = max(wear_avg - self.start_wear, 0)

            if self.reset_stint:
                self.start_laps = lap_num
                self.start_time = time_curr
                self.start_fuel = fuel_curr
                self.start_wear = wear_avg
                self.reset_stint = False

            if self.start_fuel < fuel_curr:
                self.start_fuel = fuel_curr

            # Stint current
            laps_text = f"{self.stint_data[1]:03.0f}"[:3].ljust(3)
            self.update_stint("laps", laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2stinttime(self.stint_data[2])[:5].ljust(5)
            self.update_stint("time", time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{self.stint_data[3]:05.1f}"[:5].ljust(5)
            self.update_stint("fuel", fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            cmpd_text = f"{self.stint_data[0]}"[:2].ljust(2)
            self.update_stint("cmpd", cmpd_text, self.last_cmpd_text)
            self.last_cmpd_text = cmpd_text

            wear_text = f"{self.stint_data[4]:02.0f}%"[:3].ljust(3)
            self.update_stint("wear", wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

                if self.stint_data[2] >= self.wcfg["minimum_stint_threshold_minutes"] * 60:
                    self.history_data.appendleft(self.stint_data.copy())

    # GUI update methods
    def update_stint(self, suffix, curr, last):
        """Stint data"""
        if curr != last:
            getattr(self, f"bar_{suffix}").setText(curr)

    def update_stint_history(self, curr, index):
        """Stint history data"""
        if curr[2]:
            getattr(self, f"bar_last_laps{index}").setText(
                f"{curr[1]:03.0f}"[:3].ljust(3)
            )
            getattr(self, f"bar_last_time{index}").setText(
                calc.sec2stinttime(curr[2])[:5].ljust(5)
            )
            getattr(self, f"bar_last_fuel{index}").setText(
                f"{curr[3]:05.1f}"[:5].ljust(5)
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

    def set_tyre_cmp(self, tc_indices):
        """Substitute tyre compound index with custom chars"""
        return "".join((self.tyre_compound_string[idx] for idx in tc_indices))
