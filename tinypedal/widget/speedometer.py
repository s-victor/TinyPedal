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
Speedometer Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "speedometer"


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

        self.decimals = max(int(self.wcfg["decimal_places"]), 0)
        if self.decimals > 0:
            bar_width = font_m.width * (4 + self.decimals) + bar_padx
            zero_offset = 1
        else:
            bar_width = font_m.width * 3 + bar_padx
            zero_offset = 0
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3) + zero_offset + self.decimals

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

        # Speed
        if self.wcfg["show_speed"]:
            bar_style_speed_curr = self.set_qss(
                fg_color=self.wcfg["font_color_speed"],
                bg_color=self.wcfg["bkg_color_speed"]
            )
            self.bar_speed_curr = self.set_qlabel(
                text="SPD",
                style=bar_style_speed_curr,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_speed_curr,
                column=self.wcfg["column_index_speed"],
            )

        if self.wcfg["show_speed_minimum"]:
            bar_style_speed_min = self.set_qss(
                fg_color=self.wcfg["font_color_speed_minimum"],
                bg_color=self.wcfg["bkg_color_speed_minimum"]
            )
            self.bar_speed_min = self.set_qlabel(
                text="MIN",
                style=bar_style_speed_min,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_speed_min,
                column=self.wcfg["column_index_speed_minimum"],
            )

        if self.wcfg["show_speed_maximum"]:
            bar_style_speed_max = self.set_qss(
                fg_color=self.wcfg["font_color_speed_maximum"],
                bg_color=self.wcfg["bkg_color_speed_maximum"]
            )
            self.bar_speed_max = self.set_qlabel(
                text="MAX",
                style=bar_style_speed_max,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_speed_max,
                column=self.wcfg["column_index_speed_maximum"],
            )

        if self.wcfg["show_speed_fastest"]:
            bar_style_speed_fast = self.set_qss(
                fg_color=self.wcfg["font_color_speed_fastest"],
                bg_color=self.wcfg["bkg_color_speed_fastest"]
            )
            self.bar_speed_fast = self.set_qlabel(
                text="TOP",
                style=bar_style_speed_fast,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_speed_fast,
                column=self.wcfg["column_index_speed_fastest"],
            )

        # Last data
        self.last_speed_curr = -1
        self.last_speed_min = -1
        self.last_speed_max = -1
        self.last_speed_fast = -1
        self.off_throttle_timer_start = 0
        self.on_throttle_timer_start = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read speed data
            speed = api.read.vehicle.speed()
            lap_etime = api.read.timing.elapsed()
            raw_throttle = api.read.input.throttle_raw()

            # Update current speed
            if self.wcfg["show_speed"]:
                self.update_speed(self.bar_speed_curr, speed, self.last_speed_curr)
                self.last_speed_curr = speed

            # Update minimum speed off throttle
            if self.wcfg["show_speed_minimum"] and raw_throttle < self.wcfg["off_throttle_threshold"]:
                if speed < self.last_speed_min:
                    self.update_speed(self.bar_speed_min, speed, self.last_speed_min)
                    self.last_speed_min = speed
                    self.off_throttle_timer_start = lap_etime
                if lap_etime - self.off_throttle_timer_start > self.wcfg["speed_minimum_reset_cooldown"]:
                    self.last_speed_min = speed

            # Update maximum speed on throttle
            if self.wcfg["show_speed_maximum"] and raw_throttle > self.wcfg["on_throttle_threshold"]:
                if speed > self.last_speed_max:
                    self.update_speed(self.bar_speed_max, speed, self.last_speed_max)
                    self.last_speed_max = speed
                    self.on_throttle_timer_start = lap_etime
                if lap_etime - self.on_throttle_timer_start > self.wcfg["speed_maximum_reset_cooldown"]:
                    self.last_speed_max = speed

            # Update fastest speed
            if self.wcfg["show_speed_fastest"]:
                if api.read.engine.gear() < 0:  # reset on reverse gear
                    self.last_speed_fast = 0
                if speed > self.last_speed_fast:
                    self.update_speed(self.bar_speed_fast, speed, self.last_speed_fast)
                    self.last_speed_fast = speed

    # GUI update methods
    def update_speed(self, target_bar, curr, last):
        """Vehicle speed"""
        if curr != last:
            target_bar.setText(
                f"{self.speed_units(curr):0{self.leading_zero}.{self.decimals}f}")

    # Additional methods
    def speed_units(self, value):
        """Speed units"""
        if self.cfg.units["speed_unit"] == "KPH":
            return calc.mps2kph(value)
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        return value
