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
        layout = self.set_grid_layout(gap_vert=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        layout_reversed = self.wcfg["layout"] != 0
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        history_slot = max(self.wcfg["lap_time_history_count"], 1)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Laps
        bar_style_laps = (
            self.set_qss(
                fg_color=self.wcfg["font_color_laps"],
                bg_color=self.wcfg["bkg_color_laps"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_laps"],
                bg_color=self.wcfg["bkg_color_last_laps"])
        )
        self.bars_laps = self.set_qlabel(
            text="---",
            style=bar_style_laps[1],
            width=font_m.width * 3 + bar_padx,
            count=history_slot + 1,
        )
        self.bars_laps[0].setStyleSheet(bar_style_laps[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_laps,
            column_index=self.wcfg["column_index_laps"],
            bottom_to_top=layout_reversed,
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
        self.bars_time = self.set_qlabel(
            text="-:--.---",
            style=self.bar_style_time[1],
            width=font_m.width * 8 + bar_padx,
            count=history_slot + 1,
        )
        self.bars_time[0].setStyleSheet(self.bar_style_time[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_time,
            column_index=self.wcfg["column_index_time"],
            bottom_to_top=layout_reversed,
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
        self.bars_fuel = self.set_qlabel(
            text="-.--",
            style=bar_style_fuel[1],
            width=font_m.width * 4 + bar_padx,
            count=history_slot + 1,
        )
        self.bars_fuel[0].setStyleSheet(bar_style_fuel[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_fuel,
            column_index=self.wcfg["column_index_fuel"],
            bottom_to_top=layout_reversed,
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
        self.bars_wear = self.set_qlabel(
            text="---",
            style=bar_style_wear[1],
            width=font_m.width * 3 + bar_padx,
            count=history_slot + 1,
        )
        self.bars_wear[0].setStyleSheet(bar_style_wear[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_wear,
            column_index=self.wcfg["column_index_wear"],
            bottom_to_top=layout_reversed,
        )

        # Last data
        self.last_wear = 0
        self.last_lap_stime = 0
        # 0 - lap number, 1 - est lap time, 2 - is valid lap, 3 - last fuel usage, 4 - tyre wear
        self.laps_data = [0,0,0,0,0]
        self.history_data = deque([self.laps_data[:] for _ in range(history_slot)], history_slot)
        self.update_laps_history()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read laps data
            lap_stime = api.read.timing.start()
            wear_avg = 100 - sum(api.read.tyre.wear()) * 25

            # Check if virtual energy available
            if self.wcfg["show_virtual_energy_if_available"] and minfo.restapi.maxVirtualEnergy:
                temp_fuel_last = minfo.energy.lastLapConsumption
                temp_fuel_est = minfo.energy.estimatedConsumption
            else:
                temp_fuel_last = self.fuel_units(minfo.fuel.lastLapConsumption)
                temp_fuel_est = self.fuel_units(minfo.fuel.estimatedConsumption)

            if self.last_lap_stime != lap_stime:  # time stamp difference
                if 2 < api.read.timing.elapsed() - lap_stime < 10:  # update 2s after cross line
                    self.last_wear = wear_avg
                    self.last_lap_stime = lap_stime  # reset time stamp counter
                    self.laps_data[1] = minfo.delta.lapTimeLast
                    self.laps_data[2] = minfo.delta.isValidLap
                    self.laps_data[3] = temp_fuel_last
                    # Update lap time history while on track
                    if not api.read.vehicle.in_garage():
                        self.history_data.appendleft(self.laps_data[:])
                        self.update_laps_history()

            # Current laps data
            self.laps_data[0] = api.read.lap.number()
            self.laps_data[1] = minfo.delta.lapTimeEstimated
            self.laps_data[3] = temp_fuel_est
            self.laps_data[4] = max(wear_avg - self.last_wear, 0)

            self.update_laps(self.bars_laps[0], self.laps_data[0])
            self.update_time(self.bars_time[0], self.laps_data[1])
            self.update_fuel(self.bars_fuel[0], self.laps_data[3])
            self.update_wear(self.bars_wear[0], self.laps_data[4])

    # GUI update methods
    def update_laps(self, target, data):
        """Laps data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:03.0f}"[:3])

    def update_time(self, target, data):
        """Time data"""
        if target.last != data:
            target.last = data
            target.setText(calc.sec2laptime_full(data)[:8])

    def update_fuel(self, target, data):
        """Fuel data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:04.2f}"[:4])

    def update_wear(self, target, data):
        """Wear data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:03.1f}"[:3])

    def update_laps_history(self):
        """Laps history data"""
        for index, data in enumerate(self.history_data):
            index += 1
            unavailable = False

            if data[1]:
                self.update_laps(self.bars_laps[index], data[0])
                self.update_time(self.bars_time[index], data[1])
                self.update_fuel(self.bars_fuel[index], data[3])
                self.update_wear(self.bars_wear[index], data[4])
                # Highlight invalid lap time
                self.bars_time[index].setStyleSheet(self.bar_style_time[2 - data[2]])
            elif not self.wcfg["show_empty_history"]:
                unavailable = True

            self.bars_laps[index].setHidden(unavailable)
            self.bars_time[index].setHidden(unavailable)
            self.bars_fuel[index].setHidden(unavailable)
            self.bars_wear[index].setHidden(unavailable)

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel
