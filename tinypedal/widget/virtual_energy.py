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
Virtual energy Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPixmap
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "virtual_energy"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "-.--"
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = max(self.wcfg["bar_width"], 3)
        style_width = font_m.width * self.bar_width + bar_padx

        self.decimals = tuple(
            map(self.decimal_range, (
            self.wcfg["decimal_places_end"],  # 0
            self.wcfg["decimal_places_remain"],  # 1
            self.wcfg["decimal_places_refill"],  # 2
            self.wcfg["decimal_places_used"],  # 3
            self.wcfg["decimal_places_delta"],  # 4
            self.wcfg["decimal_places_ratio"],  # 5
            self.wcfg["decimal_places_early"],  # 6
            self.wcfg["decimal_places_laps"],  # 7
            self.wcfg["decimal_places_minutes"],  # 8
            self.wcfg["decimal_places_save"],  # 9
            self.wcfg["decimal_places_pits"],  # 10
            self.wcfg["decimal_places_bias"],  # 11
        )))

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        layout_upper = QGridLayout()
        layout_lower = QGridLayout()
        layout_upper.setSpacing(0)
        layout_lower.setSpacing(0)
        layout.addLayout(layout_upper, self.wcfg["column_index_upper"], 0)
        layout.addLayout(layout_lower, self.wcfg["column_index_lower"], 0)

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = self.set_qss(
                fg_color=self.wcfg["font_color_caption"],
                bg_color=self.wcfg["bkg_color_caption"],
                font_size=int(self.wcfg['font_size'] * 0.8)
            )
            caption_upper = (
                self.wcfg["caption_text_end"],
                self.wcfg["caption_text_remain"],
                self.wcfg["caption_text_refill"],
                self.wcfg["caption_text_used"],
                self.wcfg["caption_text_delta"],
                self.wcfg["caption_text_ratio"],
            )
            caption_lower = (
                self.wcfg["caption_text_early"],
                self.wcfg["caption_text_laps"],
                self.wcfg["caption_text_minutes"],
                self.wcfg["caption_text_save"],
                self.wcfg["caption_text_pits"],
                self.wcfg["caption_text_bias"],
            )

            row_idx_upper = 2 * self.wcfg["swap_upper_caption"]
            for index, text_caption in enumerate(caption_upper):
                cap_temp = self.set_qlabel(
                    text=text_caption,
                    style=bar_style_desc,
                )
                layout_upper.addWidget(cap_temp, row_idx_upper, index)

            row_idx_lower = 2 - 2 * self.wcfg["swap_lower_caption"]
            for index, text_caption in enumerate(caption_lower):
                cap_temp = self.set_qlabel(
                    text=text_caption,
                    style=bar_style_desc,
                )
                layout_lower.addWidget(cap_temp, row_idx_lower, index)

        # Estimated end energy
        bar_style_energy_end = self.set_qss(
            fg_color=self.wcfg["font_color_end"],
            bg_color=self.wcfg["bkg_color_end"]
        )
        self.bar_energy_end = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_end,
            fixed_width=style_width,
        )

        # Remaining energy
        self.bar_style_energy_curr =(
            self.set_qss(
                fg_color=self.wcfg["font_color_remain"],
                bg_color=self.wcfg["bkg_color_remain"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_remain"],
                bg_color=self.wcfg["warning_color_low_energy"])
        )
        self.bar_energy_curr = self.set_qlabel(
            text=text_def,
            style=self.bar_style_energy_curr[0],
            fixed_width=style_width,
        )

        # Total needed energy
        self.bar_style_energy_need = (
            self.set_qss(
                fg_color=self.wcfg["font_color_refill"],
                bg_color=self.wcfg["bkg_color_refill"]),
            self.set_qss(
                fg_color=self.wcfg["font_color_refill"],
                bg_color=self.wcfg["warning_color_low_energy"])
        )
        self.bar_energy_need = self.set_qlabel(
            text=text_def,
            style=self.bar_style_energy_need[0],
            fixed_width=style_width,
        )

        # Estimated energy consumption
        bar_style_energy_used = self.set_qss(
            fg_color=self.wcfg["font_color_used"],
            bg_color=self.wcfg["bkg_color_used"]
        )
        self.bar_energy_used = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_used,
            fixed_width=style_width,
        )

        # Delta energy consumption
        bar_style_energy_delta = self.set_qss(
            fg_color=self.wcfg["font_color_delta"],
            bg_color=self.wcfg["bkg_color_delta"]
        )
        self.bar_energy_delta = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_delta,
            fixed_width=style_width,
        )

        # Fuel ratio energy consumption
        bar_style_energy_ratio = self.set_qss(
            fg_color=self.wcfg["font_color_ratio"],
            bg_color=self.wcfg["bkg_color_ratio"]
        )
        self.bar_energy_ratio = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_ratio,
            fixed_width=style_width,
        )

        # Estimate pit stop counts when pitting at end of current lap
        bar_style_energy_early = self.set_qss(
            fg_color=self.wcfg["font_color_early"],
            bg_color=self.wcfg["bkg_color_early"]
        )
        self.bar_energy_early = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_early,
            fixed_width=style_width,
        )

        # Estimated laps current energy can last
        bar_style_energy_laps = self.set_qss(
            fg_color=self.wcfg["font_color_laps"],
            bg_color=self.wcfg["bkg_color_laps"]
        )
        self.bar_energy_laps = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_laps,
            fixed_width=style_width,
        )

        # Estimated minutes current energy can last
        bar_style_energy_mins = self.set_qss(
            fg_color=self.wcfg["font_color_minutes"],
            bg_color=self.wcfg["bkg_color_minutes"]
        )
        self.bar_energy_mins = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_mins,
            fixed_width=style_width,
        )

        # Estimated one less pit energy consumption
        bar_style_energy_save = self.set_qss(
            fg_color=self.wcfg["font_color_save"],
            bg_color=self.wcfg["bkg_color_save"]
        )
        self.bar_energy_save = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_save,
            fixed_width=style_width,
        )

        # Estimate pit stop counts when pitting at end of current stint
        bar_style_energy_pits = self.set_qss(
            fg_color=self.wcfg["font_color_pits"],
            bg_color=self.wcfg["bkg_color_pits"]
        )
        self.bar_energy_pits = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_pits,
            fixed_width=style_width,
        )

        # Fuel bias
        bar_style_energy_bias = self.set_qss(
            fg_color=self.wcfg["font_color_bias"],
            bg_color=self.wcfg["bkg_color_bias"]
        )
        self.bar_energy_bias = self.set_qlabel(
            text=text_def,
            style=bar_style_energy_bias,
            fixed_width=style_width,
        )

        # Energy level bar
        if self.wcfg["show_energy_level_bar"]:
            self.energy_level_width = (font_m.width * self.bar_width + bar_padx) * 6
            energy_level_height = max(self.wcfg["energy_level_bar_height"], 1)
            self.rect_energy_left = QRectF(0, 0, 0, energy_level_height)
            self.rect_energy_start = QRectF(
                0, 0,
                max(self.wcfg["starting_energy_level_mark_width"], 1),
                energy_level_height
            )
            self.rect_energy_refill = QRectF(
                0, 0,
                max(self.wcfg["refilling_level_mark_width"], 1),
                energy_level_height
            )
            self.energy_level = self.set_qlabel(
                fixed_width=self.energy_level_width,
                fixed_height=energy_level_height,
            )
            self.pixmap_energy_level = QPixmap(self.energy_level_width, energy_level_height)
            self.draw_energy_level(0, 0, 0)
            layout.addWidget(self.energy_level, self.wcfg["column_index_middle"], 0)

        # Set layout
        layout_upper.addWidget(self.bar_energy_end, 1, 0)
        layout_upper.addWidget(self.bar_energy_curr, 1, 1)
        layout_upper.addWidget(self.bar_energy_need, 1, 2)
        layout_upper.addWidget(self.bar_energy_used, 1, 3)
        layout_upper.addWidget(self.bar_energy_delta, 1, 4)
        layout_upper.addWidget(self.bar_energy_ratio, 1, 5)
        layout_lower.addWidget(self.bar_energy_early, 1, 0)
        layout_lower.addWidget(self.bar_energy_laps, 1, 1)
        layout_lower.addWidget(self.bar_energy_mins, 1, 2)
        layout_lower.addWidget(self.bar_energy_save, 1, 3)
        layout_lower.addWidget(self.bar_energy_pits, 1, 4)
        layout_lower.addWidget(self.bar_energy_bias, 1, 5)

        # Last data
        self.last_amount_end = None
        self.last_amount_curr = None
        self.last_amount_need = None
        self.last_used_last = None
        self.last_delta_energy = None
        self.last_fuel_ratio = None
        self.last_est_pits_early = None
        self.last_est_runlaps = None
        self.last_est_runmins = None
        self.last_energy_save = None
        self.last_est_pits_end = None
        self.last_fuel_bias = None
        self.last_level_state = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Estimated end energy
            amount_end = f"{minfo.energy.amountEndStint:.{self.decimals[0]}f}"
            self.update_energy(
                self.bar_energy_end, amount_end, self.last_amount_end)
            self.last_amount_end = amount_end

            # Remaining energy
            amount_curr = f"{minfo.energy.amountCurrent:.{self.decimals[1]}f}"
            self.update_energy(
                self.bar_energy_curr, amount_curr, self.last_amount_curr,
                self.bar_style_energy_curr[
                    minfo.energy.estimatedLaps <= self.wcfg["low_energy_lap_threshold"]])
            self.last_amount_curr = amount_curr

            # Total needed energy
            amount_need = f"{calc.sym_max(minfo.energy.amountNeeded, 9999):+.{self.decimals[2]}f}"
            self.update_energy(
                self.bar_energy_need, amount_need, self.last_amount_need,
                self.bar_style_energy_need[
                minfo.energy.estimatedLaps <= self.wcfg["low_energy_lap_threshold"]])
            self.last_amount_need = amount_need

            # Estimated energy consumption
            used_last = f"{minfo.energy.estimatedConsumption:.{self.decimals[3]}f}"
            self.update_energy(
                self.bar_energy_used, used_last, self.last_used_last)
            self.last_used_last = used_last

            # Delta energy
            delta_energy = f"{minfo.energy.deltaConsumption:+.{self.decimals[4]}f}"
            self.update_energy(
                self.bar_energy_delta, delta_energy, self.last_delta_energy)
            self.last_delta_energy = delta_energy

            # Fuel ratio
            fuel_ratio = f"{minfo.hybrid.fuelEnergyRatio:.{self.decimals[5]}f}"
            self.update_energy(
                self.bar_energy_ratio, fuel_ratio, self.last_fuel_ratio)
            self.last_fuel_ratio = fuel_ratio

            # Estimate pit stop counts when pitting at end of current lap
            est_pits_early = f"{calc.zero_max(minfo.energy.estimatedNumPitStopsEarly, 99.99):.{self.decimals[6]}f}"
            self.update_energy(
                self.bar_energy_early, est_pits_early, self.last_est_pits_early)
            self.last_est_pits_early = est_pits_early

            # Estimated laps current energy can last
            est_runlaps = f"{min(minfo.energy.estimatedLaps, 9999):.{self.decimals[7]}f}"
            self.update_energy(
                self.bar_energy_laps, est_runlaps, self.last_est_runlaps)
            self.last_est_runlaps = est_runlaps

            # Estimated minutes current energy can last
            est_runmins = f"{min(minfo.energy.estimatedMinutes, 9999):.{self.decimals[8]}f}"
            self.update_energy(
                self.bar_energy_mins, est_runmins, self.last_est_runmins)
            self.last_est_runmins = est_runmins

            # Estimated one less pit energy consumption
            energy_save = f"{calc.zero_max(minfo.energy.oneLessPitConsumption, 99.99):.{self.decimals[9]}f}"
            self.update_energy(
                self.bar_energy_save, energy_save, self.last_energy_save)
            self.last_energy_save = energy_save

            # Estimate pit stop counts when pitting at end of current stint
            est_pits_end = f"{calc.zero_max(minfo.energy.estimatedNumPitStopsEnd, 99.99):.{self.decimals[10]}f}"
            self.update_energy(
                self.bar_energy_pits, est_pits_end, self.last_est_pits_end)
            self.last_est_pits_end = est_pits_end

            # Fuel bias
            if minfo.restapi.maxVirtualEnergy:
                bias = minfo.fuel.estimatedLaps - minfo.energy.estimatedLaps
            else:
                bias = 0
            fuel_bias = f"{bias:+.{self.decimals[10]}f}"
            self.update_energy(
                self.bar_energy_bias, fuel_bias, self.last_fuel_bias)
            self.last_fuel_bias = fuel_bias

            # Energy level bar
            if self.wcfg["show_energy_level_bar"]:
                level_capacity = minfo.energy.capacity
                level_curr = minfo.energy.amountCurrent
                level_start = minfo.energy.amountStart
                level_refill = level_curr + minfo.energy.amountNeeded

                level_state = round(level_start * level_refill, 3)
                if level_capacity and level_state != self.last_level_state:
                    self.draw_energy_level(
                        level_curr / level_capacity,
                        level_start / level_capacity,
                        level_refill / level_capacity,
                    )
                    self.last_level_state = level_state

    # GUI update methods
    def update_energy(self, target_bar, curr, last, color=None):
        """Update energy data"""
        if curr != last:
            if color:  # low energy warning
                target_bar.setStyleSheet(color)
            target_bar.setText(curr[:self.bar_width].strip("."))

    def draw_energy_level(self, energy_curr, energy_start, energy_refill):
        """Energy level"""
        self.pixmap_energy_level.fill(self.wcfg["bkg_color_energy_level"])
        painter = QPainter(self.pixmap_energy_level)
        painter.setPen(Qt.NoPen)

        # Update energy level highlight
        self.rect_energy_left.setWidth(energy_curr * self.energy_level_width)
        painter.fillRect(self.rect_energy_left, self.wcfg["highlight_color_energy_level"])

        # Update starting energy level mark
        if self.wcfg["show_starting_energy_level_mark"]:
            self.rect_energy_start.moveLeft(energy_start * self.energy_level_width)
            painter.fillRect(self.rect_energy_start, self.wcfg["starting_energy_level_mark_color"])

        if self.wcfg["show_refilling_level_mark"]:
            self.rect_energy_refill.moveLeft(energy_refill * self.energy_level_width)
            painter.fillRect(self.rect_energy_refill, self.wcfg["refilling_level_mark_color"])

        self.energy_level.setPixmap(self.pixmap_energy_level)

    @staticmethod
    def decimal_range(value):
        """Decimal place range"""
        return calc.zero_max(int(value), 3)
