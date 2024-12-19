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
Fuel energy saver Widget
"""

from math import floor

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

MAGIC_NUM = 99999
TEXT_NONE = "-"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap_hori=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        layout_reversed = self.wcfg["layout"] != 0
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.char_width = max(self.wcfg["bar_width"], 4)
        bar_width = font_m.width * self.char_width + bar_padx
        self.center_slot = min(max(self.wcfg["number_of_less_laps"], 0), 5) + 1  # +1 column offset
        self.total_slot = min(max(self.wcfg["number_of_more_laps"], 1), 10) + 1 + self.center_slot
        self.decimals_consumption = max(self.wcfg["decimal_places_consumption"], 0)
        self.decimals_delta = max(self.wcfg["decimal_places_delta"], 0)
        self.min_reserve = max(self.wcfg["minimum_reserve"], 0)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Target lap row
        bar_style_lap = (
            self.set_qss(
                fg_color=self.wcfg["font_color_target_laps"],
                bg_color=self.wcfg["bkg_color_target_laps"],
                font_size=int(self.wcfg['font_size'] * 0.8)),
            self.set_qss(
                fg_color=self.wcfg["font_color_current_laps"],
                bg_color=self.wcfg["bkg_color_current_laps"],
                font_size=int(self.wcfg['font_size'] * 0.8))
        )
        self.bars_target_lap = self.set_qlabel(
            text=TEXT_NONE,
            style=bar_style_lap[0],
            width=bar_width,
            count=self.total_slot,
            last=-MAGIC_NUM,
        )
        self.bars_target_lap[0].setText("LAST")
        self.bars_target_lap[self.center_slot].setStyleSheet(bar_style_lap[1])
        self.set_grid_layout_table_row(
            layout=layout,
            targets=self.bars_target_lap,
            row_index=0,
            right_to_left=layout_reversed,
        )

        # Target consumption row
        bar_style_target_use = self.set_qss(
            fg_color=self.wcfg["font_color_target_consumption"],
            bg_color=self.wcfg["bkg_color_target_consumption"]
        )
        self.bars_target_use = self.set_qlabel(
            text=TEXT_NONE,
            style=bar_style_target_use,
            width=bar_width,
            last=-MAGIC_NUM,
            count=self.total_slot,
        )
        self.set_grid_layout_table_row(
            layout=layout,
            targets=self.bars_target_use,
            row_index=1,
            right_to_left=layout_reversed,
        )

        # Delat consumption row
        self.delta_color = (
            self.set_qss(
                fg_color=self.wcfg["font_color_lap_gain"],
                bg_color=self.wcfg["bkg_color_delta_consumption"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_lap_loss"],
                bg_color=self.wcfg["bkg_color_delta_consumption"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_delta_consumption"],
                bg_color=self.wcfg["bkg_color_delta_consumption"])
        )
        self.bars_delta = self.set_qlabel(
            text=TEXT_NONE,
            style=self.delta_color[2],
            width=bar_width,
            count=self.total_slot,
            last=-MAGIC_NUM,
        )
        self.set_grid_layout_table_row(
            layout=layout,
            targets=self.bars_delta,
            row_index=2,
            right_to_left=layout_reversed,
        )

        # Last data
        self.reset_stint = True  # reset stint stats
        self.start_laps = 0  # laps number at start of current stint
        self.last_tyre_life = 0
        self.last_fuel_curr = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:
            self.update_predication()
        else:
            if not self.reset_stint:
                self.reset_stint = True

    def update_predication(self):
        """Update predication"""
        in_pits = api.read.vehicle.in_pits()
        tyre_life = sum(api.read.tyre.wear())
        lap_num = api.read.lap.number()
        energy_type = minfo.restapi.maxVirtualEnergy

        if energy_type:
            fuel_curr = minfo.energy.amountCurrent
            fuel_est = minfo.energy.estimatedConsumption
            fuel_used_curr = minfo.energy.amountUsedCurrent
            fuel_used_last_raw = minfo.energy.lastLapConsumption
        else:
            fuel_curr = minfo.fuel.amountCurrent
            fuel_est = minfo.fuel.estimatedConsumption
            fuel_used_curr = minfo.fuel.amountUsedCurrent
            fuel_used_last_raw = minfo.fuel.lastLapConsumption

        # Check stint status
        if not in_pits:
            self.last_fuel_curr = fuel_curr
            self.last_tyre_life = tyre_life
        # Reset stint if changed tyre or refueled or back in garage
        elif (self.last_tyre_life < tyre_life or
            self.last_fuel_curr < fuel_curr or api.read.vehicle.in_garage()):
            self.reset_stint = True

        if self.reset_stint:
            self.reset_stint = False
            self.start_laps = lap_num

        laps_done = max(lap_num - self.start_laps, 0)
        # Total fuel remaining count from start of current lap
        total_fuel_remaining = max(fuel_curr + fuel_used_curr - self.min_reserve, 0)
        # Estimate laps current fuel can last, minus center slot offset
        # Round to 1 decimal to reduce sensitivity
        est_runlaps = floor(round(calc.end_stint_laps(
            total_fuel_remaining, fuel_est), 1)) - self.center_slot

        # Update slots
        for index in range(self.total_slot):
            if index == 0:
                # Fuel or energy
                self.update_energy_type(self.bars_delta[index], energy_type)
                # Last lap consumption
                self.update_target_use(
                    self.bars_target_use[index], fuel_used_last_raw, energy_type)
                continue

            # Progressive fuel saving
            total_laps_target = est_runlaps + index

            # Total laps + extra laps
            if index == self.center_slot:
                target_laps = f"{laps_done}/{laps_done + total_laps_target:d}"
            else:
                target_laps = f"{laps_done + total_laps_target:d}"
            self.update_total_laps(self.bars_target_lap[index], target_laps)

            # Target consumption
            if total_laps_target > 0 and fuel_est > 0:
                target_use = total_fuel_remaining / total_laps_target
            else:
                target_use = -MAGIC_NUM
            self.update_target_use(
                self.bars_target_use[index], target_use, energy_type)

            # Delta consumption
            if total_laps_target > 0 and fuel_est > 0:
                delta = fuel_est - target_use
            else:
                delta = -MAGIC_NUM
            self.update_delta(self.bars_delta[index], delta, energy_type)

    # GUI update methods
    def update_target_use(self, target, data, energy_type):
        """Target consumption"""
        if target.last != data:
            target.last = data
            if data > -MAGIC_NUM:
                if not energy_type:
                    data = self.fuel_units(data)
                use_text = f"{data:.{self.decimals_consumption}f}"[:self.char_width]
            else:
                use_text = TEXT_NONE
            target.setText(use_text)

    def update_delta(self, target, data, energy_type):
        """Delta consumption between target & current"""
        if target.last != data:
            target.last = data
            if data > -MAGIC_NUM:
                if not energy_type:
                    data = self.fuel_units(data)
                delta_text = f"{data:+.{self.decimals_delta}f}"[:self.char_width]
                style = self.delta_color[data >= 0]
            else:
                delta_text = TEXT_NONE
                style = self.delta_color[2]
            target.setText(delta_text)
            target.setStyleSheet(style)

    def update_total_laps(self, target, data):
        """Total laps"""
        if target.last != data:
            target.last = data
            target.setText(data)

    def update_energy_type(self, target, data):
        """Energy type"""
        if target.last != data:
            target.last = data
            target.setText("NRG" if data > 0 else "FUEL")

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel
