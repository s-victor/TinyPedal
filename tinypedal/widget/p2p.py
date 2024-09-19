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
P2P Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "p2p"


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
                    fg_color=self.wcfg["font_color_battery_cooldown"],  # 0 cooldown
                    bg_color=self.wcfg["bkg_color_battery_cooldown"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_battery_charge"],  # 1 ready
                    bg_color=self.wcfg["bkg_color_battery_charge"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_battery_charge"],  # 2 drain
                    bg_color=self.wcfg["bkg_color_battery_drain"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_battery_charge"],  # 3 regen
                    bg_color=self.wcfg["bkg_color_battery_regen"])
            )
            self.bar_charge = self.set_qlabel(
                text="P2P",
                style=self.bar_style_charge[1],
                width=font_m.width * 3 + bar_padx,
            )
            layout.addWidget(self.bar_charge, 0, self.wcfg["column_index_battery_charge"])

        # Activation timer
        if self.wcfg["show_activation_timer"]:
            self.bar_style_timer = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_activation_timer"],
                    bg_color=self.wcfg["bkg_color_activation_timer"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_activation_cooldown"],
                    bg_color=self.wcfg["bkg_color_activation_cooldown"])
            )
            self.bar_timer = self.set_qlabel(
                text="0.00",
                style=self.bar_style_timer[0],
                width=font_m.width * 4 + bar_padx,
            )
            layout.addWidget(self.bar_timer, 0, self.wcfg["column_index_activation_timer"])

        # Last data
        self.last_battery_charge = None
        self.last_active_timer = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Battery charge
            if self.wcfg["show_battery_charge"]:
                state = minfo.hybrid.motorState
                if state == 1:  # cooldown check
                    state = (
                        api.read.engine.gear() >= self.wcfg["activation_threshold_gear"] and
                        api.read.vehicle.speed() * 3.6 > self.wcfg["activation_threshold_speed"] and
                        api.read.input.throttle_raw() >= self.wcfg["activation_threshold_throttle"] and
                        minfo.hybrid.motorInactiveTimer >= self.wcfg["minimum_activation_time_delay"] and
                        minfo.hybrid.motorActiveTimer < self.wcfg["maximum_activation_time_per_lap"] - 0.05
                    )
                battery_charge = minfo.hybrid.batteryCharge, state
                self.update_battery_charge(battery_charge, self.last_battery_charge)
                self.last_battery_charge = battery_charge

            # Activation timer
            if self.wcfg["show_activation_timer"]:
                active_timer = minfo.hybrid.motorActiveTimer, minfo.hybrid.motorState
                self.update_active_timer(active_timer, self.last_active_timer)
                self.last_active_timer = active_timer

    # GUI update methods
    def update_battery_charge(self, curr, last):
        """Battery charge"""
        if curr != last:
            if curr[0] < 99.5:
                format_text = f"±{curr[0]:02.0f}"
            else:
                format_text = "MAX"

            self.bar_charge.setText(format_text)
            self.bar_charge.setStyleSheet(self.bar_style_charge[curr[1]])

    def update_active_timer(self, curr, last):
        """P2P activation timer"""
        if curr != last:
            self.bar_timer.setText(f"{curr[0]:.2f}"[:4])
            self.bar_timer.setStyleSheet(self.bar_style_timer[curr[1] != 2])
