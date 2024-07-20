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
from PySide2.QtWidgets import QLabel, QGridLayout

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "virtual_energy"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "-.--"
        self.bar_width = max(self.wcfg["bar_width"], 3)
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.decimals = tuple(
            map(self.decimal_range, (
            self.wcfg["decimal_places_end"],  # 0
            self.wcfg["decimal_places_remain"],  # 1
            self.wcfg["decimal_places_refill"],  # 2
            self.wcfg["decimal_places_used"],  # 3
            self.wcfg["decimal_places_ratio"],  # 4
            self.wcfg["decimal_places_early"],  # 5
            self.wcfg["decimal_places_laps"],  # 6
            self.wcfg["decimal_places_minutes"],  # 7
            self.wcfg["decimal_places_save"],  # 8
            self.wcfg["decimal_places_pits"],  # 9
        )))

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        self.style_width = (f"min-width: {font_m.width * self.bar_width + bar_padx}px;"
                            f"max-width: {font_m.width * self.bar_width + bar_padx}px;")

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_upper = QGridLayout()
        layout_lower = QGridLayout()
        layout_upper.setSpacing(0)
        layout_lower.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_upr = self.wcfg["column_index_upper"]
        column_mid = self.wcfg["column_index_middle"]
        column_lwr = self.wcfg["column_index_lower"]

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
                f"{self.style_width}"
            )
            caption_list = (
                self.wcfg["caption_text_end"],
                self.wcfg["caption_text_remain"],
                self.wcfg["caption_text_refill"],
                self.wcfg["caption_text_used"],
                self.wcfg["caption_text_ratio"],
                self.wcfg["caption_text_early"],
                self.wcfg["caption_text_laps"],
                self.wcfg["caption_text_minutes"],
                self.wcfg["caption_text_save"],
                self.wcfg["caption_text_pits"],
            )
            for index, caption in enumerate(caption_list):
                setattr(self, f"bar_desc_{caption}", QLabel(caption))
                getattr(self, f"bar_desc_{caption}").setAlignment(Qt.AlignCenter)
                getattr(self, f"bar_desc_{caption}").setStyleSheet(bar_style_desc)
                if index < 5:
                    row_idx = 2 if self.wcfg["swap_upper_caption"] else 0
                    layout_upper.addWidget(getattr(self, f"bar_desc_{caption}"), row_idx, index)
                else:
                    row_idx = 0 if self.wcfg["swap_lower_caption"] else 2
                    layout_lower.addWidget(getattr(self, f"bar_desc_{caption}"), row_idx, index - 5)

        # Estimated end energy
        self.bar_energy_end = QLabel(text_def)
        self.bar_energy_end.setAlignment(Qt.AlignCenter)
        self.bar_energy_end.setStyleSheet(
            f"color: {self.wcfg['font_color_end']};"
            f"background: {self.wcfg['bkg_color_end']};"
            f"{self.style_width}"
        )

        # Remaining energy
        self.bar_energy_curr = QLabel(text_def)
        self.bar_energy_curr.setAlignment(Qt.AlignCenter)
        self.bar_energy_curr.setStyleSheet(
            f"color: {self.wcfg['font_color_remain']};"
            f"background: {self.wcfg['bkg_color_remain']};"
            f"{self.style_width}"
        )

        # Total needed energy
        self.bar_energy_need = QLabel(text_def)
        self.bar_energy_need.setAlignment(Qt.AlignCenter)
        self.bar_energy_need.setStyleSheet(
            f"color: {self.wcfg['font_color_refill']};"
            f"background: {self.wcfg['bkg_color_refill']};"
            f"{self.style_width}"
        )

        # Estimated energy consumption
        self.bar_energy_used = QLabel(text_def)
        self.bar_energy_used.setAlignment(Qt.AlignCenter)
        self.bar_energy_used.setStyleSheet(
            f"color: {self.wcfg['font_color_used']};"
            f"background: {self.wcfg['bkg_color_used']};"
            f"{self.style_width}"
        )

        # Fuel ratio energy consumption
        self.bar_energy_ratio = QLabel(text_def)
        self.bar_energy_ratio.setAlignment(Qt.AlignCenter)
        self.bar_energy_ratio.setStyleSheet(
            f"color: {self.wcfg['font_color_ratio']};"
            f"background: {self.wcfg['bkg_color_ratio']};"
            f"{self.style_width}"
        )

        # Estimate pit stop counts when pitting at end of current lap
        self.bar_energy_early = QLabel(text_def)
        self.bar_energy_early.setAlignment(Qt.AlignCenter)
        self.bar_energy_early.setStyleSheet(
            f"color: {self.wcfg['font_color_early']};"
            f"background: {self.wcfg['bkg_color_early']};"
            f"{self.style_width}"
        )

        # Estimated laps current energy can last
        self.bar_energy_laps = QLabel(text_def)
        self.bar_energy_laps.setAlignment(Qt.AlignCenter)
        self.bar_energy_laps.setStyleSheet(
            f"color: {self.wcfg['font_color_laps']};"
            f"background: {self.wcfg['bkg_color_laps']};"
            f"{self.style_width}"
        )

        # Estimated minutes current energy can last
        self.bar_energy_mins = QLabel(text_def)
        self.bar_energy_mins.setAlignment(Qt.AlignCenter)
        self.bar_energy_mins.setStyleSheet(
            f"color: {self.wcfg['font_color_minutes']};"
            f"background: {self.wcfg['bkg_color_minutes']};"
            f"{self.style_width}"
        )

        # Estimated one less pit energy consumption
        self.bar_energy_save = QLabel(text_def)
        self.bar_energy_save.setAlignment(Qt.AlignCenter)
        self.bar_energy_save.setStyleSheet(
            f"color: {self.wcfg['font_color_save']};"
            f"background: {self.wcfg['bkg_color_save']};"
            f"{self.style_width}"
        )

        # Estimate pit stop counts when pitting at end of current stint
        self.bar_energy_pits = QLabel(text_def)
        self.bar_energy_pits.setAlignment(Qt.AlignCenter)
        self.bar_energy_pits.setStyleSheet(
            f"color: {self.wcfg['font_color_pits']};"
            f"background: {self.wcfg['bkg_color_pits']};"
            f"{self.style_width}"
        )

        # Energy level bar
        if self.wcfg["show_energy_level_bar"]:
            self.energy_level_width = (font_m.width * self.bar_width + bar_padx) * 5
            self.energy_level_height = max(self.wcfg["energy_level_bar_height"], 1)
            self.rect_energy_left = QRectF(0, 0, 0, self.energy_level_height)
            self.rect_energy_start = QRectF(
                0, 0,
                max(self.wcfg["starting_energy_level_mark_width"], 1),
                self.energy_level_height)
            self.rect_energy_refill = QRectF(
                0, 0,
                max(self.wcfg["refilling_level_mark_width"], 1),
                self.energy_level_height)

            self.energy_level = QLabel()
            self.energy_level.setFixedSize(self.energy_level_width, self.energy_level_height)
            self.pixmap_energy_level = QPixmap(self.energy_level_width, self.energy_level_height)
            self.draw_energy_level(self.energy_level, self.pixmap_energy_level, [0,0,0])

        # Set layout
        layout_upper.addWidget(self.bar_energy_end, 1, 0)
        layout_upper.addWidget(self.bar_energy_curr, 1, 1)
        layout_upper.addWidget(self.bar_energy_need, 1, 2)
        layout_upper.addWidget(self.bar_energy_used, 1, 3)
        layout_upper.addWidget(self.bar_energy_ratio, 1, 4)
        layout_lower.addWidget(self.bar_energy_early, 1, 0)
        layout_lower.addWidget(self.bar_energy_laps, 1, 1)
        layout_lower.addWidget(self.bar_energy_mins, 1, 2)
        layout_lower.addWidget(self.bar_energy_save, 1, 3)
        layout_lower.addWidget(self.bar_energy_pits, 1, 4)
        layout.addLayout(layout_upper, column_upr, 0)
        if self.wcfg["show_energy_level_bar"]:
            layout.addWidget(self.energy_level, column_mid, 0)
        layout.addLayout(layout_lower, column_lwr, 0)
        self.setLayout(layout)

        # Last data
        self.last_amount_end = None
        self.last_amount_curr = None
        self.last_amount_need = None
        self.last_used_last = None
        self.last_fuel_ratio = None
        self.last_est_pits_early = None
        self.last_est_runlaps = None
        self.last_est_runmins = None
        self.last_energy_save = None
        self.last_est_pits_end = None
        self.last_energy_level = None

        # Set widget state & start update
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:

            # Estimated end energy
            amount_end = f"{minfo.energy.amountEndStint:.{self.decimals[0]}f}"
            self.update_energy("end", amount_end, self.last_amount_end)
            self.last_amount_end = amount_end

            # Remaining energy
            amount_curr = f"{minfo.energy.amountCurrent:.{self.decimals[1]}f}"
            self.update_energy(
                "curr", amount_curr, self.last_amount_curr, minfo.energy.estimatedLaps)
            self.last_amount_curr = amount_curr

            # Total needed energy
            amount_need = f"{calc.sym_range(minfo.energy.amountNeeded, 9999):+.{self.decimals[2]}f}"
            self.update_energy(
                "need", amount_need, self.last_amount_need, minfo.energy.estimatedLaps)
            self.last_amount_need = amount_need

            # Estimated energy consumption
            used_last = f"{minfo.energy.estimatedConsumption:.{self.decimals[3]}f}"
            self.update_energy("used", used_last, self.last_used_last)
            self.last_used_last = used_last

            # Fuel ratio
            fuel_ratio = f"{minfo.hybrid.fuelEnergyRatio:.{self.decimals[4]}f}"
            self.update_energy("ratio", fuel_ratio, self.last_fuel_ratio)
            self.last_fuel_ratio = fuel_ratio

            # Estimate pit stop counts when pitting at end of current lap
            est_pits_early = f"{min(max(minfo.energy.estimatedNumPitStopsEarly, 0), 99.99):.{self.decimals[5]}f}"
            self.update_energy("early", est_pits_early, self.last_est_pits_early)
            self.last_est_pits_early = est_pits_early

            # Estimated laps current energy can last
            est_runlaps = f"{min(minfo.energy.estimatedLaps, 9999):.{self.decimals[6]}f}"
            self.update_energy("laps", est_runlaps, self.last_est_runlaps)
            self.last_est_runlaps = est_runlaps

            # Estimated minutes current energy can last
            est_runmins = f"{min(minfo.energy.estimatedMinutes, 9999):.{self.decimals[7]}f}"
            self.update_energy("mins", est_runmins, self.last_est_runmins)
            self.last_est_runmins = est_runmins

            # Estimated one less pit energy consumption
            energy_save = f"{min(max(minfo.energy.oneLessPitConsumption, 0), 99.99):.{self.decimals[8]}f}"
            self.update_energy("save", energy_save, self.last_energy_save)
            self.last_energy_save = energy_save

            # Estimate pit stop counts when pitting at end of current stint
            est_pits_end = f"{min(max(minfo.energy.estimatedNumPitStopsEnd, 0), 99.99):.{self.decimals[9]}f}"
            self.update_energy("pits", est_pits_end, self.last_est_pits_end)
            self.last_est_pits_end = est_pits_end

            # Energy level bar
            if self.wcfg["show_energy_level_bar"]:
                energy_capacity = max(minfo.energy.capacity, 1)
                energy_level = (
                    round(minfo.energy.amountCurrent / energy_capacity, 3),
                    round(minfo.energy.amountStart / energy_capacity, 3),
                    round((minfo.energy.amountCurrent + minfo.energy.amountNeeded) / energy_capacity, 3),
                )
                self.update_energy_level(energy_level, self.last_energy_level)
                self.last_energy_level = energy_level

    # GUI update methods
    def update_energy(self, suffix, curr, last, state=None):
        """Update energy data"""
        if curr != last:
            if state:  # low energy warning
                getattr(self, f"bar_energy_{suffix}").setStyleSheet(
                    f"{self.color_lowenergy(state, suffix)}{self.style_width}"
                )
            getattr(self, f"bar_energy_{suffix}").setText(
                fmt.strip_decimal_pt(curr[:self.bar_width]))

    def update_energy_level(self, curr, last):
        """Energy level update"""
        if curr != last:
            self.draw_energy_level(self.energy_level, self.pixmap_energy_level, curr)

    def draw_energy_level(self, canvas, pixmap, energy_data):
        """Energy level"""
        pixmap.fill(self.wcfg["bkg_color_energy_level"])
        painter = QPainter(pixmap)

        # Update energy level highlight
        painter.setPen(Qt.NoPen)
        self.rect_energy_left.setWidth(energy_data[0] * self.energy_level_width)
        painter.fillRect(self.rect_energy_left, self.wcfg["highlight_color_energy_level"])

        # Update starting energy level mark
        if self.wcfg["show_starting_energy_level_mark"]:
            self.rect_energy_start.moveLeft(energy_data[1] * self.energy_level_width)
            painter.fillRect(self.rect_energy_start, self.wcfg["starting_energy_level_mark_color"])

        if self.wcfg["show_refilling_level_mark"]:
            self.rect_energy_refill.moveLeft(energy_data[2] * self.energy_level_width)
            painter.fillRect(self.rect_energy_refill, self.wcfg["refilling_level_mark_color"])

        canvas.setPixmap(pixmap)

    # Additional methods
    def color_lowenergy(self, state, suffix):
        """Low energy warning color"""
        if suffix == "curr":
            fgcolor = self.wcfg["font_color_remain"]
            bgcolor = self.wcfg["bkg_color_remain"]
        else:
            fgcolor = self.wcfg["font_color_refill"]
            bgcolor = self.wcfg["bkg_color_refill"]

        if state > self.wcfg["low_energy_lap_threshold"]:
            return f"color: {fgcolor};background: {bgcolor};"
        return f"color: {fgcolor};background: {self.wcfg['warning_color_low_energy']};"

    @staticmethod
    def decimal_range(value):
        """Decimal place range"""
        return min(max(int(value), 0), 3)
