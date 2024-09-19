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
from PySide2.QtWidgets import QGridLayout

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
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Max display stint
        self.stint_count = max(self.wcfg["stint_history_count"], 1)
        self.data_bar = {}

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Laps
        bar_style_laps = (
            self.set_qss(
                fg_color=self.wcfg["font_color_laps"],
                bg_color=self.wcfg["bkg_color_laps"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_laps"],
                bg_color=self.wcfg["bkg_color_last_stint_laps"])
        )
        self.set_table(
            name="laps",
            text="---",
            style=bar_style_laps,
            width=font_m.width * 3 + bar_padx,
            column=self.wcfg["column_index_laps"],
        )

        # Time
        bar_style_time = (
            self.set_qss(
                fg_color=self.wcfg["font_color_time"],
                bg_color=self.wcfg["bkg_color_time"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_time"],
                bg_color=self.wcfg["bkg_color_last_stint_time"])
        )
        self.set_table(
            name="time",
            text="--:--",
            style=bar_style_time,
            width=font_m.width * 5 + bar_padx,
            column=self.wcfg["column_index_time"],
        )

        # Fuel
        bar_style_fuel = (
            self.set_qss(
                fg_color=self.wcfg["font_color_fuel"],
                bg_color=self.wcfg["bkg_color_fuel"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_fuel"],
                bg_color=self.wcfg["bkg_color_last_stint_fuel"])
        )
        self.set_table(
            name="fuel",
            text="---.-",
            style=bar_style_fuel,
            width=font_m.width * 5 + bar_padx,
            column=self.wcfg["column_index_fuel"],
        )

        # Tyre compound
        bar_style_cmpd = (
            self.set_qss(
                fg_color=self.wcfg["font_color_tyre"],
                bg_color=self.wcfg["bkg_color_tyre"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_tyre"],
                bg_color=self.wcfg["bkg_color_last_stint_tyre"])
        )
        self.set_table(
            name="cmpd",
            text="--",
            style=bar_style_cmpd,
            width=font_m.width * 2 + bar_padx,
            column=self.wcfg["column_index_tyre"],
        )

        # Tyre wear
        bar_style_wear = (
            self.set_qss(
                fg_color=self.wcfg["font_color_wear"],
                bg_color=self.wcfg["bkg_color_wear"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_wear"],
                bg_color=self.wcfg["bkg_color_last_stint_wear"])
        )
        self.set_table(
            name="wear",
            text="---",
            style=bar_style_wear,
            width=font_m.width * 3 + bar_padx,
            column=self.wcfg["column_index_wear"],
        )

        # Last data
        self.checked = False
        self.stint_running = False  # check whether current stint running
        self.reset_stint = True  # reset stint stats
        # 0 - tyre compound, 1 - total laps, 2 - total time, 3 - total fuel, 4 - total tyre wear
        self.stint_data = ["--",0,0,0,0]
        self.history_data = deque(
            [self.stint_data[:] for _ in range(self.stint_count)], self.stint_count
        )
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

    # GUI generate methods
    def set_table(self, name: str, text: str, style: str, width: int, column: int):
        """Set table"""
        for idx in range(self.stint_count + 1):
            if idx == 0:
                style_idx = 0
            else:
                style_idx = 1
            bar_name = f"{idx}_{name}"
            self.data_bar[bar_name] = self.set_qlabel(
                text=text,
                style=style[style_idx],
                width=width,
            )
            if not self.wcfg["show_empty_history"] and idx > 0:
                self.data_bar[bar_name].hide()
            # Set layout
            if self.wcfg["layout"] == 0:
                row_index = idx
            else:
                row_index = self.stint_count - idx + 1
            self.layout().addWidget(
                self.data_bar[bar_name], row_index, column)

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
                    self.history_data.appendleft(self.stint_data[:])
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
            laps_text = f"{self.stint_data[1]:03.0f}"[:3]
            self.update_stint(self.data_bar["0_laps"], laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2stinttime(self.stint_data[2])[:5]
            self.update_stint(self.data_bar["0_time"], time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{self.stint_data[3]:05.1f}"[:5]
            self.update_stint(self.data_bar["0_fuel"], fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            cmpd_text = f"{self.stint_data[0]}"[:2]
            self.update_stint(self.data_bar["0_cmpd"], cmpd_text, self.last_cmpd_text)
            self.last_cmpd_text = cmpd_text

            wear_text = f"{self.stint_data[4]:02.0f}%"[:3]
            self.update_stint(self.data_bar["0_wear"], wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

                if self.stint_data[2] >= self.wcfg["minimum_stint_threshold_minutes"] * 60:
                    self.history_data.appendleft(self.stint_data[:])

    # GUI update methods
    def update_stint(self, target_bar, curr, last):
        """Stint data"""
        if curr != last:
            target_bar.setText(curr)

    def update_stint_history(self, curr, index):
        """Stint history data"""
        if curr[2]:
            self.data_bar[f"{index}_laps"].setText(f"{curr[1]:03.0f}"[:3])
            self.data_bar[f"{index}_time"].setText(calc.sec2stinttime(curr[2])[:5])
            self.data_bar[f"{index}_fuel"].setText(f"{curr[3]:05.1f}"[:5])
            self.data_bar[f"{index}_cmpd"].setText(f"{curr[0]}"[:2])
            self.data_bar[f"{index}_wear"].setText(f"{curr[4]:02.0f}%"[:3])
            self.data_bar[f"{index}_laps"].show()
            self.data_bar[f"{index}_time"].show()
            self.data_bar[f"{index}_fuel"].show()
            self.data_bar[f"{index}_cmpd"].show()
            self.data_bar[f"{index}_wear"].show()

        elif not self.wcfg["show_empty_history"]:
            self.data_bar[f"{index}_laps"].hide()
            self.data_bar[f"{index}_time"].hide()
            self.data_bar[f"{index}_fuel"].hide()
            self.data_bar[f"{index}_cmpd"].hide()
            self.data_bar[f"{index}_wear"].hide()

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def set_tyre_cmp(self, tc_indices):
        """Substitute tyre compound index with custom chars"""
        return "".join((self.tyre_compound_string[idx] for idx in tc_indices))
