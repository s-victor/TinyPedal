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
Battery Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "battery"


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
        bar_width = font_m.width * 8 + bar_padx
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)

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

        # Battery charge
        if self.wcfg["show_battery_charge"]:
            self.bar_style_charge = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_battery_charge"],
                    bg_color=self.wcfg["bkg_color_battery_charge"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_battery_charge"],
                    bg_color=self.wcfg["warning_color_low_battery"])
            )
            self.bar_charge = self.set_qlabel(
                text="BATTERY",
                style=self.bar_style_charge[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_charge,
                column=self.wcfg["column_index_battery_charge"],
            )

        # Battery drain
        if self.wcfg["show_battery_drain"]:
            bar_style_drain = self.set_qss(
                fg_color=self.wcfg["font_color_battery_drain"],
                bg_color=self.wcfg["bkg_color_battery_drain"]
            )
            self.bar_drain = self.set_qlabel(
                text="B DRAIN",
                style=bar_style_drain,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_drain,
                column=self.wcfg["column_index_battery_drain"],
            )

        # Battery regen
        if self.wcfg["show_battery_regen"]:
            bar_style_regen = self.set_qss(
                fg_color=self.wcfg["font_color_battery_regen"],
                bg_color=self.wcfg["bkg_color_battery_regen"]
            )
            self.bar_regen = self.set_qlabel(
                text="B REGEN",
                style=bar_style_regen,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_regen,
                column=self.wcfg["column_index_battery_regen"],
            )

        # Activation timer
        if self.wcfg["show_activation_timer"]:
            bar_style_timer = self.set_qss(
                fg_color=self.wcfg["font_color_activation_timer"],
                bg_color=self.wcfg["bkg_color_activation_timer"]
            )
            self.bar_timer = self.set_qlabel(
                text="B TIMER",
                style=bar_style_timer,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_timer,
                column=self.wcfg["column_index_activation_timer"],
            )

        # Last data
        self.last_battery_charge = None
        self.last_battery_drain = None
        self.last_battery_regen = None
        self.last_motor_active_timer = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Battery charge & usage
            if self.wcfg["show_battery_charge"]:
                self.update_charge(
                    minfo.hybrid.batteryCharge, self.last_battery_charge)
                self.last_battery_charge = minfo.hybrid.batteryCharge

            if 0 <= minfo.delta.lapTimeCurrent < self.freeze_duration:
                battery_drain = minfo.hybrid.batteryDrainLast
                battery_regen = minfo.hybrid.batteryRegenLast
            else:
                battery_drain = minfo.hybrid.batteryDrain
                battery_regen = minfo.hybrid.batteryRegen

            if self.wcfg["show_battery_drain"]:
                self.update_drain(battery_drain, self.last_battery_drain)
                self.last_battery_drain = battery_drain

            if self.wcfg["show_battery_regen"]:
                self.update_regen(battery_regen, self.last_battery_regen)
                self.last_battery_regen = battery_regen

            # Motor activation timer
            if self.wcfg["show_activation_timer"]:
                self.update_timer(
                    minfo.hybrid.motorActiveTimer, self.last_motor_active_timer)
                self.last_motor_active_timer = minfo.hybrid.motorActiveTimer

    # GUI update methods
    def update_charge(self, curr, last):
        """Battery charge"""
        if curr != last:
            self.bar_charge.setText(f"B{curr: >7.2f}"[:8])
            self.bar_charge.setStyleSheet(
                self.bar_style_charge[curr <= self.wcfg["low_battery_threshold"]])

    def update_drain(self, curr, last):
        """Battery drain"""
        if curr != last:
            self.bar_drain.setText(f"-{curr: >7.2f}"[:8])

    def update_regen(self, curr, last):
        """Battery regen"""
        if curr != last:
            self.bar_regen.setText(f"+{curr: >7.2f}"[:8])

    def update_timer(self, curr, last):
        """Motor activation timer"""
        if curr != last:
            format_text = f"{curr: >7.2f}"[:7]
            self.bar_timer.setText(f"{format_text}s")
