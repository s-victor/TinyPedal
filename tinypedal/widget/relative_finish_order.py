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
Relative finish order Widget
"""

from math import ceil as roundup

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "relative_finish_order"
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
        self.bar_width = max(self.wcfg["bar_width"], 3)
        self.range_start = max(self.wcfg["near_start_range"], 0)
        self.range_finish = max(self.wcfg["near_finish_range"], 0)
        self.total_slot = min(max(self.wcfg["number_of_predication"], 0), 10) + 3
        self.leader_pit_time_set = self.create_pit_time_set(self.total_slot, "leader")
        self.player_pit_time_set = self.create_pit_time_set(self.total_slot, "player")
        self.decimals_laps = max(self.wcfg["decimal_places_laps"], 0)
        self.decimals_refill = max(self.wcfg["decimal_places_refill"], 0)
        self.extra_laps = max(self.wcfg["number_of_extra_laps"], 1)

        self.leader_pace = LapTimePace(
            min(max(self.wcfg["leader_laptime_pace_samples"], 1), 20),
            max(self.wcfg["leader_laptime_pace_margin"], 0.1))

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        self.leader_lap_color = (
            self.set_qss(
                fg_color=self.wcfg["font_color_leader"],
                bg_color=self.wcfg["bkg_color_leader"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_near_start"],
                bg_color=self.wcfg["bkg_color_leader"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_near_finish"],
                bg_color=self.wcfg["bkg_color_leader"])
        )
        self.player_lap_color = (
            self.set_qss(
                fg_color=self.wcfg["font_color_player"],
                bg_color=self.wcfg["bkg_color_player"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_near_start"],
                bg_color=self.wcfg["bkg_color_player"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_near_finish"],
                bg_color=self.wcfg["bkg_color_player"])
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
        self.last_lap_int = -1
        self.last_session_type = None
        self.last_energy_type = None
        self.last_lap_leader = [(-MAGIC_NUM, 0, 0)] * self.total_slot
        self.last_lap_player = [(-MAGIC_NUM, 0, 0)] * self.total_slot
        self.last_refill_player = [-MAGIC_NUM] * self.total_slot
        self.last_refill_extra = [-MAGIC_NUM] * self.total_slot
        self.last_pit_time_leader = 0
        self.last_pit_time_player = 0

    def set_table(self, width: int):
        """Set table"""
        bar_style_pit_time = self.set_qss(
            fg_color=self.wcfg["font_color_pit_time"],
            bg_color=self.wcfg["bkg_color_pit_time"],
            font_size=int(self.wcfg['font_size'] * 0.8),
        )
        bar_style_refill = self.set_qss(
            fg_color=self.wcfg["font_color_refill"],
            bg_color=self.wcfg["bkg_color_refill"]
        )
        layout_inner = [None for _ in range(self.total_slot)]

        for index in range(self.total_slot):
            # Create column layout
            layout_inner[index] = QGridLayout()
            layout_inner[index].setSpacing(0)

            # Leader pit time row
            pit_time_text = f"{self.leader_pit_time_set[index]:.0f}s"
            name_pit_time = f"pit_leader_{index}"
            self.data_bar[name_pit_time] = self.set_qlabel(
                text=pit_time_text,
                style=bar_style_pit_time,
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_pit_time], 0, 0
            )

            # Leader row
            if index == 0:
                lap_leader_text = "LDR"
            else:
                lap_leader_text = TEXT_NONE
            name_lap_leader = f"lap_leader_{index}"
            self.data_bar[name_lap_leader] = self.set_qlabel(
                text=lap_leader_text,
                style=self.leader_lap_color[0],
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_lap_leader], 1, 0
            )

            # Player row
            name_lap_player = f"lap_player_{index}"
            self.data_bar[name_lap_player] = self.set_qlabel(
                text=TEXT_NONE,
                style=self.player_lap_color[0],
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_lap_player], 2, 0
            )

            # Player pit time row
            if index == 0:
                pit_time_text = "DIFF"
            else:
                pit_time_text = f"{self.player_pit_time_set[index]:.0f}s"
            name_pit_player = f"pit_player_{index}"
            self.data_bar[name_pit_player] = self.set_qlabel(
                text=pit_time_text,
                style=bar_style_pit_time,
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_pit_player], 3, 0
            )

            # Player refill row
            name_refill = f"refill_{index}"
            self.data_bar[name_refill] = self.set_qlabel(
                text=TEXT_NONE,
                style=bar_style_refill,
                width=width,
            )
            layout_inner[index].addWidget(
                self.data_bar[name_refill], 4, 0
            )

            # Player extra lap refill row
            if self.wcfg["show_extra_refilling"]:
                if index == 0:
                    refill_extra_text = f"EX+{self.extra_laps}"
                else:
                    refill_extra_text = TEXT_NONE
                name_refill_extra = f"refill_extra_{index}"
                self.data_bar[name_refill_extra] = self.set_qlabel(
                    text=refill_extra_text,
                    style=bar_style_refill,
                    width=width,
                )
                layout_inner[index].addWidget(
                    self.data_bar[name_refill_extra], 5, 0
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

    def update_predication(self):
        """Update predication"""
        is_lap_type_session = api.read.session.lap_type()
        in_formation = api.read.session.in_formation()
        energy_type = minfo.restapi.maxVirtualEnergy

        leader_index = self.find_leader_index()
        player_index = api.read.vehicle.player_index()
        leader_lap_into = api.read.lap.progress(leader_index)
        player_lap_into = api.read.lap.progress()

        leader_laptime_pace = self.leader_pace.update(leader_index)
        player_laptime_pace = minfo.delta.lapTimePace

        leader_valid = 0 < leader_laptime_pace < MAGIC_NUM
        player_valid = 0 < player_laptime_pace < MAGIC_NUM

        if is_lap_type_session and leader_valid and player_valid:
            laps_total = api.read.lap.maximum()
            leader_laps_left = laps_total - api.read.lap.completed_laps(leader_index) - leader_lap_into
            player_laps_left = laps_total - api.read.lap.completed_laps() - player_lap_into
            time_left = min(leader_laptime_pace, player_laptime_pace) * leader_laps_left
            laps_diff = player_laps_left - (time_left / player_laptime_pace)
        else:
            time_left = api.read.session.remaining()
            laps_diff = 0

        # Update last pit time slot
        self.leader_pit_time_set[-1] = minfo.vehicles.pitTimer[leader_index][2]
        self.update_pit_time_leader(self.leader_pit_time_set[-1], self.last_pit_time_leader)
        self.last_pit_time_leader = self.leader_pit_time_set[-1]

        self.player_pit_time_set[-1] = minfo.vehicles.pitTimer[player_index][2]
        self.update_pit_time_player(self.player_pit_time_set[-1], self.last_pit_time_player)
        self.last_pit_time_player = self.player_pit_time_set[-1]

        # Update slots
        for index in range(self.total_slot):
            # Update lap progress difference & refill type
            if index == 0:
                self.update_energy_type(energy_type, self.last_energy_type, index)
                self.last_energy_type = energy_type

                self.update_race_type(is_lap_type_session, self.last_session_type, index)
                self.last_session_type = is_lap_type_session

                lap_int = calc.lap_progress_difference(
                    leader_laptime_pace, player_laptime_pace)
                self.update_lap_int(lap_int, self.last_lap_int, index)
                self.last_lap_int = lap_int
                continue

            # Predicate player
            if player_valid:
                # lap_player, 0 - final lap frac, 1 - remaining laps, 2 highlight range
                lap_player = self.time_type_final_progress(
                    player_laptime_pace, player_lap_into, time_left,
                    self.player_pit_time_set[index])
                if is_lap_type_session and index > 1:  # for lap type race only
                    lap_offset = self.lap_type_final_progress(  # relative offset based on 0s
                        player_laptime_pace, self.last_lap_player[1][0],
                        self.player_pit_time_set[index])
                    lap_player = lap_offset[0], lap_player[1], lap_offset[2]
            else:
                lap_player = -MAGIC_NUM, 0, 0
            self.update_lap_player(lap_player, self.last_lap_player[index], index)
            self.last_lap_player[index] = lap_player

            # Player refill
            if is_lap_type_session and index != 1:  # disable refilling display in laps type
                refill_player = refill_extra = -MAGIC_NUM
            elif not in_formation and leader_valid and player_valid:
                consumption = minfo.energy if energy_type else minfo.fuel
                refill_player = calc.total_fuel_needed(lap_player[1],
                    consumption.estimatedValidConsumption, consumption.amountCurrent)
                if self.wcfg["show_extra_refilling"]:
                    refill_extra = calc.total_fuel_needed(lap_player[1] + self.extra_laps,  # add extra
                        consumption.estimatedValidConsumption, consumption.amountCurrent)
            else:
                refill_player = refill_extra = -MAGIC_NUM
            self.update_refill(refill_player, self.last_refill_player[index], index, energy_type)
            self.last_refill_player[index] = refill_player

            # Player refill extra
            if self.wcfg["show_extra_refilling"]:
                self.update_refill_extra(refill_extra, self.last_refill_extra[index], index, energy_type)
                self.last_refill_extra[index] = refill_extra

            # Predicate leader
            if leader_valid and player_index != leader_index:
                if is_lap_type_session:  # for lap type race only
                    # Round up laps difference for relative final lap progress against player
                    lap_leader = self.lap_type_final_progress(
                        leader_laptime_pace, roundup(laps_diff),
                        self.leader_pit_time_set[index])
                else:
                    lap_leader = self.time_type_final_progress(
                        leader_laptime_pace, leader_lap_into, time_left,
                        self.leader_pit_time_set[index])
            else:
                lap_leader = -MAGIC_NUM, 0, 0
            self.update_lap_leader(lap_leader, self.last_lap_leader[index], index)
            self.last_lap_leader[index] = lap_leader

    # GUI update methods
    def update_lap_leader(self, curr, last, index):
        """Leader final lap progress"""
        if curr != last:
            if curr[0] > -MAGIC_NUM:
                lap_text = f"{curr[0]:.{self.decimals_laps}f}"[:self.bar_width]
            else:
                lap_text = TEXT_NONE
            self.data_bar[f"lap_leader_{index}"].setText(lap_text)
            self.data_bar[f"lap_leader_{index}"].setStyleSheet(self.leader_lap_color[curr[2]])

    def update_lap_player(self, curr, last, index):
        """Player final lap progress"""
        if curr != last:
            if curr[0] > -MAGIC_NUM:
                lap_text = f"{curr[0]:.{self.decimals_laps}f}"[:self.bar_width]
            else:
                lap_text = TEXT_NONE
            self.data_bar[f"lap_player_{index}"].setText(lap_text)
            self.data_bar[f"lap_player_{index}"].setStyleSheet(self.player_lap_color[curr[2]])

    def update_lap_int(self, curr, last, index):
        """Lap progress difference"""
        if curr != last:
            if 0 < curr:
                lap_text = f"{curr:.{self.decimals_laps}f}"[:self.bar_width]
            else:
                lap_text = TEXT_NONE
            self.data_bar[f"lap_player_{index}"].setText(lap_text)

    def update_pit_time_leader(self, curr, last):
        """Leader pit time"""
        if curr != last:
            self.data_bar[f"pit_leader_{self.total_slot - 1}"].setText(f"{curr:.0f}s")

    def update_pit_time_player(self, curr, last):
        """Player pit time"""
        if curr != last:
            self.data_bar[f"pit_player_{self.total_slot - 1}"].setText(f"{curr:.0f}s")

    def update_race_type(self, curr, last, index):
        """Race type"""
        if curr != last:
            if curr:
                type_text = "LAPS"
            else:
                type_text = "TIME"
            self.data_bar[f"pit_leader_{index}"].setText(type_text)

    def update_energy_type(self, curr, last, index):
        """Energy type"""
        if curr != last:
            if curr > 0:
                type_text = "NRG"
            else:
                type_text = "FUEL"
            self.data_bar[f"refill_{index}"].setText(type_text)

    def update_refill(self, curr, last, index, energy_type):
        """Player refill"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not energy_type:
                    curr = self.fuel_units(curr)
                refill_text = f"{curr:+.{self.decimals_refill}f}"[:self.bar_width].strip(".")
            else:
                refill_text = TEXT_NONE
            self.data_bar[f"refill_{index}"].setText(refill_text)

    def update_refill_extra(self, curr, last, index, energy_type):
        """Player refill extra lap"""
        if curr != last:
            if curr > -MAGIC_NUM:
                if not energy_type:
                    curr = self.fuel_units(curr)
                refill_text = f"{curr:+.{self.decimals_refill}f}"[:self.bar_width].strip(".")
            else:
                refill_text = TEXT_NONE
            self.data_bar[f"refill_extra_{index}"].setText(refill_text)

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    @staticmethod
    def find_leader_index():
        """Find leader index"""
        for index in range(api.read.vehicle.total_vehicles()):
            if api.read.vehicle.place(index) == 1:
                return index
        return 0

    def create_pit_time_set(self, total_slot, suffix):
        """Create pit time set"""
        pit_time_set = [0, 0]  # reserved first 2 slots
        predications = [
            max(self.wcfg[f"predication_{index + 1}_{suffix}_pit_time"], 0)
            for index in range(total_slot - 3)]
        pit_time_set.extend(predications)
        pit_time_set.append(0)  # reserved last slot
        return pit_time_set

    def time_type_final_progress(self, laptime_pace, lap_into, time_left, pit_time):
        """Calculate time-type final lap progress"""
        lap_into_offset = calc.lap_progress_offset(laptime_pace, lap_into, pit_time)
        lap_remaining = calc.end_timer_laps_remain(lap_into_offset, laptime_pace, time_left)
        lap_final = lap_remaining % 1
        laps_left = calc.time_type_laps_remain(roundup(lap_remaining), lap_into)
        highlight_range = self.set_highlight_range(laptime_pace, lap_final)
        return lap_final, laps_left, highlight_range

    def lap_type_final_progress(self, laptime_pace, laps_diff, pit_time):
        """Calculate lap-type final lap progress + lap difference from leader

        Final laps difference = leader's lap_final - player's lap_final.
        """
        lap_final_extend = laps_diff + calc.lap_progress_offset(laptime_pace, 0, pit_time)
        highlight_range = self.set_highlight_range(laptime_pace, lap_final_extend % 1)
        return lap_final_extend, 0, highlight_range

    def set_highlight_range(self, laptime_pace, lap_final):
        """Final lap highlight range"""
        if laptime_pace > 0:
            range_limit = laptime_pace / 3  # limit max range to 1/3 of laptime pace
            if lap_final < min(self.range_start, range_limit) / laptime_pace:
                return 1  # near start
            if lap_final > 1 - min(self.range_finish, range_limit) / laptime_pace:
                return -1  # near finish
        return 0


class LapTimePace:
    """Lap time pace"""

    def __init__(self, samples: int = 6, margin: float = 5, laptime: float = MAGIC_NUM) -> None:
        self.laptime_pace = laptime
        self.laptime_margin = margin
        self.pit_lap = 0
        self.ema_factor = self.set_ema_factor(samples)
        self.last_vehicle_class = None
        self.last_lap_stime = -1
        self.validating = 0

    @staticmethod
    def set_ema_factor(samples: int = 6) -> None:
        """Set EMA factor"""
        return calc.ema_factor(samples)

    @staticmethod
    def verify(laptime: float) -> bool:
        """Verify laptime"""
        return laptime > 0

    def reset_laptime(self, index: int) -> float:
        """Reset laptime"""
        return min(filter(self.verify,
            (api.read.timing.last_laptime(index),
            api.read.timing.best_laptime(index),
            MAGIC_NUM)))

    def update(self, index: int = 0) -> float:
        """Calculate laptime pace"""
        lap_stime = api.read.timing.start(index)
        self.pit_lap = bool(self.pit_lap + api.read.vehicle.in_pits(index))
        veh_class = api.read.vehicle.class_name(index)

        # Reset if vehicle class changes
        if veh_class != self.last_vehicle_class:
            self.last_vehicle_class = veh_class
            self.laptime_pace = self.reset_laptime(index)

        if lap_stime != self.last_lap_stime:
            self.validating = api.read.timing.elapsed()
            self.pit_lap = 0
        self.last_lap_stime = lap_stime

        if self.validating:
            timer = api.read.timing.elapsed() - self.validating
            laptime_last = api.read.timing.last_laptime(index)
            if 1 < timer <= 10 and self.verify(laptime_last):
                if not self.pit_lap:
                    if laptime_last < self.laptime_pace:
                        self.laptime_pace = laptime_last
                    else:
                        self.laptime_pace = calc.exp_mov_avg(
                            self.ema_factor,
                            self.laptime_pace,
                            min(laptime_last, self.laptime_pace + self.laptime_margin))
                elif self.laptime_pace >= MAGIC_NUM:
                    self.laptime_pace = self.reset_laptime(index)
                self.validating = 0
            elif timer > 10:  # switch off after 10s
                self.validating = 0

        return self.laptime_pace
