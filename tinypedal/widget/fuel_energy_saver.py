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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "fuel_energy_saver"
MAGIC_NUM = 99999
TEXT_NONE = "-"


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
        self.bar_width = max(self.wcfg["bar_width"], 4)
        self.center_slot = min(max(self.wcfg["number_of_less_laps"], 0), 5) + 1  # +1 column offset
        self.total_slot = min(max(self.wcfg["number_of_more_laps"], 1), 10) + 1 + self.center_slot
        self.decimals_consumption = max(self.wcfg["decimal_places_consumption"], 0)
        self.decimals_delta = max(self.wcfg["decimal_places_delta"], 0)
        self.min_reserve = max(self.wcfg["minimum_reserve"], 0)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
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

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        self.data_bar = {}
        self.set_table(
            width=font_m.width * self.bar_width + bar_padx
        )

        # Last data
        self.reset_stint = True  # reset stint stats
        self.start_laps = 0  # laps number at start of current stint
        self.last_tyre_life = 0
        self.last_fuel_curr = 0
        self.last_target_use = [-MAGIC_NUM] * self.total_slot
        self.last_delta = [-MAGIC_NUM] * self.total_slot
        self.last_target_laps = [-MAGIC_NUM] * self.total_slot

    # GUI generate methods
    def set_table(self, width: int):
        """Set table"""
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
        bar_style_target_use = self.set_qss(
            fg_color=self.wcfg["font_color_target_consumption"],
            bg_color=self.wcfg["bkg_color_target_consumption"]
        )
        layout_inner = [None for _ in range(self.total_slot)]

        for index in range(self.total_slot):
            # Create column layout
            layout_inner[index] = QGridLayout()
            layout_inner[index].setSpacing(0)

            # Target lap row
            name_target_lap = f"target_lap_{index}"
            if index == 0:
                lap_diff_text = "LAST"
            else:
                lap_diff_text = TEXT_NONE
            self.data_bar[name_target_lap] = self.set_qlabel(
                text=lap_diff_text,
                style=bar_style_lap[index == self.center_slot],
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_target_lap], 0, 0
            )

            # Target consumption row
            name_target_use = f"target_use_{index}"
            self.data_bar[name_target_use] = self.set_qlabel(
                text=TEXT_NONE,
                style=bar_style_target_use,
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_target_use], 1, 0
            )

            # Delat consumption row
            name_delta = f"delta_{index}"
            self.data_bar[name_delta] = self.set_qlabel(
                text=TEXT_NONE,
                style=self.delta_color[2],
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_delta], 2, 0
            )

            # Set layout
            if self.wcfg["layout"] == 0:  # left to right layout
                self.layout().addLayout(
                    layout_inner[index], 0, index
                )
            else:  # right to left layout
                self.layout().addLayout(
                    layout_inner[index], 0, self.total_slot - 1 - index
                )

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
                self.update_energy_type(energy_type, self.last_delta[index], index)
                self.last_delta[index] = energy_type
                # Last lap consumption
                self.update_target_use(
                    fuel_used_last_raw, self.last_target_use[index], index, energy_type)
                self.last_target_use[index] = fuel_used_last_raw
                continue

            # Progressive fuel saving
            total_laps_target = est_runlaps + index

            # Total laps + extra laps
            if index == self.center_slot:
                target_laps = f"{laps_done}/{laps_done + total_laps_target:d}"
            else:
                target_laps = f"{laps_done + total_laps_target:d}"
            self.update_total_laps(target_laps, self.last_target_laps[index], index)
            self.last_target_laps[index] = target_laps

            # Target consumption
            if total_laps_target > 0 and fuel_est > 0:
                target_use = total_fuel_remaining / total_laps_target
            else:
                target_use = -MAGIC_NUM
            self.update_target_use(target_use, self.last_target_use[index], index, energy_type)
            self.last_target_use[index] = target_use

            # Delta consumption
            if total_laps_target > 0 and fuel_est > 0:
                delta = fuel_est - target_use
            else:
                delta = -MAGIC_NUM
            self.update_delta(delta, self.last_delta[index], index, energy_type)
            self.last_delta[index] = delta

    # GUI update methods
    def update_target_use(self, curr, last, index, energy_type):
        """Target consumption"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not energy_type:
                    curr = self.fuel_units(curr)
                use_text = f"{curr:.{self.decimals_consumption}f}"[:self.bar_width]
            else:
                use_text = TEXT_NONE
            self.data_bar[f"target_use_{index}"].setText(use_text)

    def update_delta(self, curr, last, index, energy_type):
        """Delta consumption between target & current"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not energy_type:
                    curr = self.fuel_units(curr)
                delta_text = f"{curr:+.{self.decimals_delta}f}"[:self.bar_width]
                style = self.delta_color[curr >= 0]
            else:
                delta_text = TEXT_NONE
                style = self.delta_color[2]

            self.data_bar[f"delta_{index}"].setText(delta_text)
            self.data_bar[f"delta_{index}"].setStyleSheet(style)

    def update_total_laps(self, curr, last, index):
        """Total laps"""
        if curr != last:
            self.data_bar[f"target_lap_{index}"].setText(curr)

    def update_energy_type(self, curr, last, index):
        """Energy type"""
        if curr != last:
            if curr > 0:
                type_text = "NRG"
            else:
                type_text = "FUEL"
            self.data_bar[f"delta_{index}"].setText(type_text)

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel
