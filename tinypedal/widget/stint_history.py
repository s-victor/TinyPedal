#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from .. import calculation as calc
from .. import heatmap as hmp
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap_vert=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        layout_reversed = self.wcfg["layout"] != 0
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        stint_slot = max(self.wcfg["stint_history_count"], 1)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
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
        self.bars_cmpd = self.set_qlabel(
            text="--",
            style=bar_style_cmpd[1],
            width=font_m.width * 2 + bar_padx,
            count=stint_slot + 1,
        )
        self.bars_cmpd[0].setStyleSheet(bar_style_cmpd[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_cmpd,
            column_index=self.wcfg["column_index_tyre"],
            bottom_to_top=layout_reversed,
        )

        # Laps
        bar_style_laps = (
            self.set_qss(
                fg_color=self.wcfg["font_color_laps"],
                bg_color=self.wcfg["bkg_color_laps"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_last_stint_laps"],
                bg_color=self.wcfg["bkg_color_last_stint_laps"])
        )
        self.bars_laps = self.set_qlabel(
            text="---",
            style=bar_style_laps[1],
            width=font_m.width * 3 + bar_padx,
            count=stint_slot + 1,
        )
        self.bars_laps[0].setStyleSheet(bar_style_laps[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_laps,
            column_index=self.wcfg["column_index_laps"],
            bottom_to_top=layout_reversed,
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
        self.bars_time = self.set_qlabel(
            text="--:--",
            style=bar_style_time[1],
            width=font_m.width * 5 + bar_padx,
            count=stint_slot + 1,
        )
        self.bars_time[0].setStyleSheet(bar_style_time[0])
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
                fg_color=self.wcfg["font_color_last_stint_fuel"],
                bg_color=self.wcfg["bkg_color_last_stint_fuel"])
        )
        self.bars_fuel = self.set_qlabel(
            text="---.-",
            style=bar_style_fuel[1],
            width=font_m.width * 5 + bar_padx,
            count=stint_slot + 1,
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
                fg_color=self.wcfg["font_color_last_stint_wear"],
                bg_color=self.wcfg["bkg_color_last_stint_wear"])
        )
        self.bars_wear = self.set_qlabel(
            text="---",
            style=bar_style_wear[1],
            width=font_m.width * 3 + bar_padx,
            count=stint_slot + 1,
        )
        self.bars_wear[0].setStyleSheet(bar_style_wear[0])
        self.set_grid_layout_table_column(
            layout=layout,
            targets=self.bars_wear,
            column_index=self.wcfg["column_index_wear"],
            bottom_to_top=layout_reversed,
        )

        # Last data
        self.checked = False
        self.stint_running = False
        self.reset_stint = True
        self.start_laps = 0
        self.start_time = 0
        self.start_fuel = 0
        self.start_wear = 0
        self.last_wear_avg = 0
        self.last_fuel_curr = 0
        # 0 - tyre compound, 1 - total laps, 2 - total time, 3 - total fuel, 4 - total tyre wear
        self.stint_data = ["--",0,0,0,0]
        self.history_data = deque([self.stint_data[:] for _ in range(stint_slot)], stint_slot)
        self.update_stint_history()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

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
                    self.update_stint_history()

            if in_garage:
                self.reset_stint = True

            if self.reset_stint:
                self.start_laps = lap_num
                self.start_time = time_curr
                self.start_fuel = fuel_curr
                self.start_wear = wear_avg
                self.reset_stint = False

            if self.start_fuel < fuel_curr:
                self.start_fuel = fuel_curr

            # Current stint data
            class_name = api.read.vehicle.class_name()
            self.stint_data[0] = "".join(
                hmp.select_compound_symbol(f"{class_name} - {tcmpd_name}")
                for tcmpd_name in api.read.tyre.compound_name()
            )
            self.stint_data[1] = max(lap_num - self.start_laps, 0)
            self.stint_data[2] = max(time_curr - self.start_time, 0)
            self.stint_data[3] = max(self.start_fuel - fuel_curr, 0)
            self.stint_data[4] = max(wear_avg - self.start_wear, 0)

            self.update_cmpd(self.bars_cmpd[0], self.stint_data[0])
            self.update_laps(self.bars_laps[0], self.stint_data[1])
            self.update_time(self.bars_time[0], self.stint_data[2])
            self.update_fuel(self.bars_fuel[0], self.stint_data[3])
            self.update_wear(self.bars_wear[0], self.stint_data[4])

        else:
            if self.checked:
                self.checked = False
                self.stint_running = False
                self.reset_stint = True

                if self.stint_data[2] >= self.wcfg["minimum_stint_threshold_minutes"] * 60:
                    self.history_data.appendleft(self.stint_data[:])
                    self.update_stint_history()

    # GUI update methods
    def update_cmpd(self, target, data):
        """Compound data"""
        if target.last != data:
            target.last = data
            target.setText(data)

    def update_laps(self, target, data):
        """Laps data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:03.0f}"[:3])

    def update_time(self, target, data):
        """Time data"""
        if target.last != data:
            target.last = data
            target.setText(calc.sec2stinttime(data)[:5])

    def update_fuel(self, target, data):
        """Fuel data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:05.1f}"[:5])

    def update_wear(self, target, data):
        """Wear data"""
        if target.last != data:
            target.last = data
            target.setText(f"{data:02.0f}%"[:3])

    def update_stint_history(self):
        """Stint history data"""
        for index, data in enumerate(self.history_data):
            index += 1
            unavailable = False

            if data[2]:
                self.update_cmpd(self.bars_cmpd[index], data[0])
                self.update_laps(self.bars_laps[index], data[1])
                self.update_time(self.bars_time[index], data[2])
                self.update_fuel(self.bars_fuel[index], data[3])
                self.update_wear(self.bars_wear[index], data[4])
            elif not self.wcfg["show_empty_history"]:
                unavailable = True

            self.bars_cmpd[index].setHidden(unavailable)
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
