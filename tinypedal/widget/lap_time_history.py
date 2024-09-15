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
Lap time history Widget
"""

from collections import deque

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "lap_time_history"


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

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Max display laps
        self.laps_count = max(self.wcfg["lap_time_history_count"], 1)
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
                fg_color=self.wcfg["font_color_last_laps"],
                bg_color=self.wcfg["bkg_color_last_laps"])
        )
        self.set_table(
            name="laps",
            text="---",
            style=bar_style_laps,
            width=font_m.width * 3 + bar_padx,
            column=self.wcfg["column_index_laps"],
        )

        # Time
        self.bar_style_time = (
            self.set_qss(
                fg_color=self.wcfg["font_color_time"],
                bg_color=self.wcfg["bkg_color_time"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_time"],
                bg_color=self.wcfg["bkg_color_last_time"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_invalid_laptime"],
                bg_color=self.wcfg["bkg_color_last_time"])
        )
        self.set_table(
            name="time",
            text="-:--.---",
            style=self.bar_style_time,
            width=font_m.width * 8 + bar_padx,
            column=self.wcfg["column_index_time"],
        )

        # Fuel
        bar_style_fuel = (
            self.set_qss(
                fg_color=self.wcfg["font_color_fuel"],
                bg_color=self.wcfg["bkg_color_fuel"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_fuel"],
                bg_color=self.wcfg["bkg_color_last_fuel"])
        )
        self.set_table(
            name="fuel",
            text="-.--",
            style=bar_style_fuel,
            width=font_m.width * 4 + bar_padx,
            column=self.wcfg["column_index_fuel"],
        )

        # Tyre wear
        bar_style_wear = (
            self.set_qss(
                fg_color=self.wcfg["font_color_wear"],
                bg_color=self.wcfg["bkg_color_wear"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_wear"],
                bg_color=self.wcfg["bkg_color_last_wear"])
        )
        self.set_table(
            name="wear",
            text="---",
            style=bar_style_wear,
            width=font_m.width * 3 + bar_padx,
            column=self.wcfg["column_index_wear"],
        )

        # Last data
        # 0 - lap number, 1 - est lap time, 2 - is valid lap, 3 - last fuel usage, 4 - tyre wear
        self.laps_data = [0,0,0,0,0]
        self.history_data = deque(
            [self.laps_data[:] for _ in range(self.laps_count)], self.laps_count
        )
        self.last_wear = 0
        self.last_lap_stime = 0  # last lap start time
        self.last_laps_text = None
        self.last_time_text = None
        self.last_fuel_text = None
        self.last_wear_text = None

    # GUI generate methods
    def set_table(self, name: str, text: str, style: str, width: int, column: int):
        """Set table"""
        for idx in range(self.laps_count + 1):
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
                row_index = self.laps_count - idx + 1
            self.layout().addWidget(
                self.data_bar[bar_name], row_index, column)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read laps data
            lap_stime = api.read.timing.start()
            wear_avg = 100 - (sum(api.read.tyre.wear()) * 25)

            # Check if virtual energy available
            if self.wcfg["show_virtual_energy_if_available"] and minfo.restapi.maxVirtualEnergy:
                temp_fuel_last = minfo.energy.lastLapConsumption
                temp_fuel_est = minfo.energy.estimatedConsumption
            else:
                temp_fuel_last = self.fuel_units(minfo.fuel.lastLapConsumption)
                temp_fuel_est = self.fuel_units(minfo.fuel.estimatedConsumption)

            if lap_stime != self.last_lap_stime:  # time stamp difference
                if 2 < api.read.timing.elapsed() - lap_stime < 10:  # update 2s after cross line
                    self.last_wear = wear_avg
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.laps_data[1] = minfo.delta.lapTimeLast
                    self.laps_data[2] = minfo.delta.isValidLap
                    self.laps_data[3] = temp_fuel_last
                    # Update lap time history while on track
                    if not api.read.vehicle.in_garage():
                        self.history_data.appendleft(self.laps_data[:])
                        for index in range(self.laps_count):
                            self.update_laps_history(self.history_data[index], index + 1)

            # Current laps data
            self.laps_data[0] = api.read.lap.number()
            self.laps_data[1] = minfo.delta.lapTimeEstimated
            self.laps_data[3] = temp_fuel_est
            self.laps_data[4] = max(wear_avg - self.last_wear, 0)

            laps_text = f"{self.laps_data[0]:03.0f}"[:3]
            self.update_laps(self.data_bar["0_laps"], laps_text, self.last_laps_text)
            self.last_laps_text = laps_text

            time_text = calc.sec2laptime_full(self.laps_data[1])[:8]
            self.update_laps(self.data_bar["0_time"], time_text, self.last_time_text)
            self.last_time_text = time_text

            fuel_text = f"{self.laps_data[3]:04.2f}"[:4]
            self.update_laps(self.data_bar["0_fuel"], fuel_text, self.last_fuel_text)
            self.last_fuel_text = fuel_text

            wear_text = f"{self.laps_data[4]:03.1f}"[:3]
            self.update_laps(self.data_bar["0_wear"], wear_text, self.last_wear_text)
            self.last_wear_text = wear_text

    # GUI update methods
    def update_laps(self, target_bar, curr, last):
        """Laps data"""
        if curr != last:
            target_bar.setText(curr)

    def update_laps_history(self, curr, index):
        """Laps history data"""
        if curr[1]:
            self.data_bar[f"{index}_laps"].setText(f"{max(curr[0] - 1, 0):03.0f}"[:3])
            self.data_bar[f"{index}_time"].setText(calc.sec2laptime_full(curr[1])[:8])
            # Mark invalid lap time
            self.data_bar[f"{index}_time"].setStyleSheet(self.bar_style_time[2 - curr[2]])
            self.data_bar[f"{index}_fuel"].setText(f"{curr[3]:04.2f}"[:4])
            self.data_bar[f"{index}_wear"].setText(f"{curr[4]:03.1f}"[:3])
            self.data_bar[f"{index}_laps"].show()
            self.data_bar[f"{index}_time"].show()
            self.data_bar[f"{index}_fuel"].show()
            self.data_bar[f"{index}_wear"].show()

        elif not self.wcfg["show_empty_history"]:
            self.data_bar[f"{index}_laps"].hide()
            self.data_bar[f"{index}_time"].hide()
            self.data_bar[f"{index}_fuel"].hide()
            self.data_bar[f"{index}_wear"].hide()

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel
