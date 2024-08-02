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
from PySide2.QtWidgets import QLabel, QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "fuel_energy_saver"
MAGIC_NUM = 99999
TEXT_NONE = "-"


class Draw(Overlay):
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
        self.less_slot = min(max(self.wcfg["number_of_less_laps"], 0), 5) + 1  # plus 1 offset
        self.total_slot = min(max(self.wcfg["number_of_more_laps"], 0), 10) + 1 + self.less_slot
        self.lap_difference_set = [0] * self.total_slot
        self.decimals_consumption = max(self.wcfg["decimal_places_consumption"], 0)
        self.decimals_delta = max(self.wcfg["decimal_places_delta"], 0)
        self.min_reserve = max(self.wcfg["minimum_reserve"], 0)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        self.style_width = (f"min-width: {font_m.width * self.bar_width + bar_padx}px;"
                            f"max-width: {font_m.width * self.bar_width + bar_padx}px;")
        self.delta_color = (
            (f"color: {self.wcfg['font_color_delta_consumption']};"
            f"background: {self.wcfg['bkg_color_delta_consumption']};"),
            (f"color: {self.wcfg['font_color_lap_gain']};"
            f"background: {self.wcfg['bkg_color_delta_consumption']};"),
            (f"color: {self.wcfg['font_color_lap_loss']};"
            f"background: {self.wcfg['bkg_color_delta_consumption']};")
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.generate_bar(layout)

        # Set layout
        self.setLayout(layout)

        # Last data
        self.last_target_use = [-MAGIC_NUM] * self.total_slot
        self.last_delta = [-MAGIC_NUM] * self.total_slot
        self.last_target_laps = [-MAGIC_NUM] * self.total_slot
        self.stint_best_laptime = MAGIC_NUM
        self.stint_refer_consumption = 0

        self.reset_stint = True  # reset stint stats
        self.last_tyre_life = 0
        self.last_fuel_curr = 0
        self.start_fuel = 0  # fuel at start of current stint
        self.start_laps = 0  # laps number at start of current stint

        # Set widget state & start update
        self.set_widget_state()

    def generate_bar(self, layout):
        """Generate data bar"""
        bar_style_target_lap = (
            f"color: {self.wcfg['font_color_target_laps']};"
            f"background: {self.wcfg['bkg_color_target_laps']};"
            f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            f"{self.style_width}"
        )
        bar_style_current_lap = (
            f"color: {self.wcfg['font_color_current_laps']};"
            f"background: {self.wcfg['bkg_color_current_laps']};"
            f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            f"{self.style_width}"
        )
        bar_style_target_use = (
            f"color: {self.wcfg['font_color_target_consumption']};"
            f"background: {self.wcfg['bkg_color_target_consumption']};"
            f"{self.style_width}"
        )

        for index in range(self.total_slot):
            # Create column layout
            setattr(self, f"layout_{index}", QGridLayout())
            getattr(self, f"layout_{index}").setSpacing(0)

            # Target lap row
            if index == 0:
                lap_diff_text = "LAST"
            else:
                lap_diff_text = f"{self.lap_difference_set[index]:d}"
            setattr(self, f"bar_target_lap_{index}", QLabel(lap_diff_text))
            getattr(self, f"bar_target_lap_{index}").setAlignment(Qt.AlignCenter)
            if index == self.less_slot:
                getattr(self, f"bar_target_lap_{index}").setStyleSheet(bar_style_current_lap)
            else:
                getattr(self, f"bar_target_lap_{index}").setStyleSheet(bar_style_target_lap)
            getattr(self, f"layout_{index}").addWidget(
                getattr(self, f"bar_target_lap_{index}"), 0, 0)

            # Target consumption row
            setattr(self, f"bar_target_use_{index}", QLabel(TEXT_NONE))
            getattr(self, f"bar_target_use_{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_target_use_{index}").setStyleSheet(bar_style_target_use)
            getattr(self, f"layout_{index}").addWidget(
                getattr(self, f"bar_target_use_{index}"), 1, 0)

            # Delat consumption row
            setattr(self, f"bar_delta_{index}", QLabel(TEXT_NONE))
            getattr(self, f"bar_delta_{index}").setAlignment(Qt.AlignCenter)
            getattr(self, f"bar_delta_{index}").setStyleSheet(self.delta_color[0])
            getattr(self, f"layout_{index}").addWidget(
                getattr(self, f"bar_delta_{index}"), 2, 0)

            # Set layout
            if self.wcfg["layout"] == 0:  # left to right layout
                layout.addLayout(
                    getattr(self, f"layout_{index}"), 0, index)
            else:  # right to left layout
                layout.addLayout(
                    getattr(self, f"layout_{index}"), 0, self.total_slot - 1 - index)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:
            self.update_predication()
        else:
            if not self.reset_stint:
                self.reset_stint = True

    def update_predication(self):
        """Update predication"""
        in_pits = api.read.vehicle.in_pits()
        tyre_life = sum(api.read.tyre.wear())
        lap_num = api.read.lap.number()
        laptime_valid = api.read.timing.last_laptime()
        is_energy = minfo.restapi.maxVirtualEnergy

        if is_energy:
            fuel_curr = minfo.energy.amountCurrent
            fuel_est = minfo.energy.estimatedConsumption
            fuel_used_curr = minfo.energy.amountUsedCurrent
            fuel_used_last = minfo.energy.lastLapValidConsumption
            fuel_used_last_raw = minfo.energy.lastLapConsumption
        else:
            fuel_curr = minfo.fuel.amountCurrent
            fuel_est = minfo.fuel.estimatedConsumption
            fuel_used_curr = minfo.fuel.amountUsedCurrent
            fuel_used_last = minfo.fuel.lastLapValidConsumption
            fuel_used_last_raw = minfo.fuel.lastLapConsumption

        # Update reference consumption
        if 0 < fuel_used_last:  # wait for valid consumption data
            # Initialize
            if self.stint_refer_consumption <= 0:
                self.stint_refer_consumption = fuel_used_last
            # If set new stint best laptime
            elif 0 < laptime_valid < self.stint_best_laptime:
                self.stint_best_laptime = laptime_valid
                self.stint_refer_consumption = fuel_used_last

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
            self.start_fuel = fuel_curr
            self.start_laps = lap_num
            self.stint_best_laptime = MAGIC_NUM
            if 0 < fuel_used_last:
                self.stint_refer_consumption = fuel_used_last

        if self.start_fuel < fuel_curr:
            self.start_fuel = fuel_curr

        # Total fuel used count from start of current lap
        total_stint_laps = floor(calc.end_stint_laps(
            self.start_fuel - self.min_reserve, self.stint_refer_consumption))
        laps_done = max(lap_num - self.start_laps, 0)
        total_fuel_remaining = fuel_curr + fuel_used_curr
        # Round to 1 decimal to reduce sensitivity
        saved_laps = floor(round(calc.end_stint_laps(total_fuel_remaining, fuel_est), 1)) - self.less_slot

        # Update slots
        for index in range(self.total_slot):
            if index == 0:
                # Fuel or energy
                self.update_energy_type(is_energy, self.last_delta[index], index)
                self.last_delta[index] = is_energy
                # Last lap consumption
                self.update_target_use(fuel_used_last_raw, self.last_target_use[index], index, is_energy)
                self.last_target_use[index] = fuel_used_last_raw
                continue

            # Progressive fuel saving
            total_laps_target = saved_laps + index

            # Total laps + extra laps
            if index == self.less_slot:
                target_laps = f"{laps_done}/{laps_done + total_laps_target:d}"
            else:
                target_laps = f"{laps_done + total_laps_target:d}"
            self.update_total_laps(target_laps, self.last_target_laps[index], index)
            self.last_target_laps[index] = target_laps

            # Target consumption
            if total_laps_target > 0 and total_stint_laps > 0 and fuel_est > 0:
                target_use = total_fuel_remaining / total_laps_target
            else:
                target_use = -MAGIC_NUM
            self.update_target_use(target_use, self.last_target_use[index], index, is_energy)
            self.last_target_use[index] = target_use

            # Delta consumption
            if total_laps_target > 0 and total_stint_laps > 0 and fuel_est > 0:
                delta = fuel_est - target_use
            else:
                delta = -MAGIC_NUM
            self.update_delta(delta, self.last_delta[index], index, is_energy)
            self.last_delta[index] = delta

    # GUI update methods
    def update_target_use(self, curr, last, index, is_energy):
        """Target consumption"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not is_energy:
                    curr = self.fuel_units(curr)
                use_text = f"{curr:.{self.decimals_consumption}f}"[:self.bar_width]
            else:
                use_text = TEXT_NONE
            getattr(self, f"bar_target_use_{index}").setText(use_text)

    def update_delta(self, curr, last, index, is_energy):
        """Delta consumption between target & current"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not is_energy:
                    curr = self.fuel_units(curr)
                delta_text = f"{curr:+.{self.decimals_consumption}f}"[:self.bar_width]
                if curr >= 0:
                    style = f"{self.delta_color[-1]}{self.style_width}"
                else:
                    style = f"{self.delta_color[1]}{self.style_width}"
            else:
                delta_text = TEXT_NONE
                style = f"{self.delta_color[0]}{self.style_width}"

            getattr(self, f"bar_delta_{index}").setText(delta_text)
            getattr(self, f"bar_delta_{index}").setStyleSheet(style)

    def update_total_laps(self, curr, last, index):
        """Total laps"""
        if curr != last:
            getattr(self, f"bar_target_lap_{index}").setText(curr)

    def update_energy_type(self, curr, last, index):
        """Energy type"""
        if curr != last:
            if curr:
                type_text = "NRG"
            else:
                type_text = "FUEL"
            getattr(self, f"bar_delta_{index}").setText(type_text)
            getattr(self, f"bar_delta_{index}").setStyleSheet(
                f"{self.delta_color[0]}{self.style_width}")

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel
