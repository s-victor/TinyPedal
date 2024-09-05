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
from PySide2.QtWidgets import QGridLayout, QLabel

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
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        bar_width = font_m.width * 8 + bar_padx
        self.freeze_duration = min(max(self.wcfg["freeze_duration"], 0), 30)

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
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
                    self.wcfg["font_color_battery_charge"],
                    self.wcfg["bkg_color_battery_charge"]),
                self.set_qss(
                    self.wcfg["font_color_battery_charge"],
                    self.wcfg["warning_color_low_battery"])
            )
            self.bar_charge = QLabel("BATTERY")
            self.bar_charge.setAlignment(Qt.AlignCenter)
            self.bar_charge.setMinimumWidth(bar_width)
            self.bar_charge.setStyleSheet(self.bar_style_charge[0])
            self.set_layout_orient(
                0, layout, self.bar_charge, self.wcfg["column_index_battery_charge"])

        # Battery drain
        if self.wcfg["show_battery_drain"]:
            self.bar_drain = QLabel("B DRAIN")
            self.bar_drain.setAlignment(Qt.AlignCenter)
            self.bar_drain.setMinimumWidth(bar_width)
            self.bar_drain.setStyleSheet(
                self.set_qss(
                    self.wcfg["font_color_battery_drain"],
                    self.wcfg["bkg_color_battery_drain"])
            )
            self.set_layout_orient(
                0, layout, self.bar_drain, self.wcfg["column_index_battery_drain"])

        # Battery regen
        if self.wcfg["show_battery_regen"]:
            self.bar_regen = QLabel("B REGEN")
            self.bar_regen.setAlignment(Qt.AlignCenter)
            self.bar_regen.setMinimumWidth(bar_width)
            self.bar_regen.setStyleSheet(
                self.set_qss(
                    self.wcfg["font_color_battery_regen"],
                    self.wcfg["bkg_color_battery_regen"])
            )
            self.set_layout_orient(
                0, layout, self.bar_regen, self.wcfg["column_index_battery_regen"])

        # Activation timer
        if self.wcfg["show_activation_timer"]:
            self.bar_timer = QLabel("B TIMER")
            self.bar_timer.setAlignment(Qt.AlignCenter)
            self.bar_timer.setMinimumWidth(bar_width)
            self.bar_timer.setStyleSheet(
                self.set_qss(
                    self.wcfg["font_color_activation_timer"],
                    self.wcfg["bkg_color_activation_timer"])
            )
            self.set_layout_orient(
                0, layout, self.bar_timer, self.wcfg["column_index_activation_timer"])

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
