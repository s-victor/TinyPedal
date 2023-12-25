#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "speedometer"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        self.decimals = max(int(self.wcfg["decimal_places"]), 0)
        if self.decimals > 0:
            bar_width = font_m.width * (4 + self.decimals)
            zero_offset = 1
        else:
            bar_width = font_m.width * 3
            zero_offset = 0
        self.leading_zero = min(max(self.wcfg["leading_zero"], 1), 3) + zero_offset + self.decimals

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_sc = self.wcfg["column_index_speed"]
        column_sm = self.wcfg["column_index_speed_minimum"]
        column_sx = self.wcfg["column_index_speed_maximum"]
        column_sf = self.wcfg["column_index_speed_fastest"]

        # Speed
        if self.wcfg["show_speed"]:
            self.bar_speed_curr = QLabel("SPD")
            self.bar_speed_curr.setAlignment(Qt.AlignCenter)
            self.bar_speed_curr.setStyleSheet(
                f"color: {self.wcfg['font_color_speed']};"
                f"background: {self.wcfg['bkg_color_speed']};"
                f"min-width: {bar_width}px;"
            )

        if self.wcfg["show_speed_minimum"]:
            self.bar_speed_min = QLabel("MIN")
            self.bar_speed_min.setAlignment(Qt.AlignCenter)
            self.bar_speed_min.setStyleSheet(
                f"color: {self.wcfg['font_color_speed_minimum']};"
                f"background: {self.wcfg['bkg_color_speed_minimum']};"
                f"min-width: {bar_width}px;"
            )

        if self.wcfg["show_speed_maximum"]:
            self.bar_speed_max = QLabel("MAX")
            self.bar_speed_max.setAlignment(Qt.AlignCenter)
            self.bar_speed_max.setStyleSheet(
                f"color: {self.wcfg['font_color_speed_maximum']};"
                f"background: {self.wcfg['bkg_color_speed_maximum']};"
                f"min-width: {bar_width}px;"
            )

        if self.wcfg["show_speed_fastest"]:
            self.bar_speed_fast = QLabel("TOP")
            self.bar_speed_fast.setAlignment(Qt.AlignCenter)
            self.bar_speed_fast.setStyleSheet(
                f"color: {self.wcfg['font_color_speed_fastest']};"
                f"background: {self.wcfg['bkg_color_speed_fastest']};"
                f"min-width: {bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Horizontal layout
            if self.wcfg["show_speed"]:
                layout.addWidget(self.bar_speed_curr, 0, column_sc)
            if self.wcfg["show_speed_minimum"]:
                layout.addWidget(self.bar_speed_min, 0, column_sm)
            if self.wcfg["show_speed_maximum"]:
                layout.addWidget(self.bar_speed_max, 0, column_sx)
            if self.wcfg["show_speed_fastest"]:
                layout.addWidget(self.bar_speed_fast, 0, column_sf)
        else:
            # Vertical layout
            if self.wcfg["show_speed"]:
                layout.addWidget(self.bar_speed_curr, column_sc, 0)
            if self.wcfg["show_speed_minimum"]:
                layout.addWidget(self.bar_speed_min, column_sm, 0)
            if self.wcfg["show_speed_maximum"]:
                layout.addWidget(self.bar_speed_max, column_sx, 0)
            if self.wcfg["show_speed_fastest"]:
                layout.addWidget(self.bar_speed_fast, column_sf, 0)
        self.setLayout(layout)

        # Last data
        self.last_speed_curr = -1
        self.last_speed_min = -1
        self.last_speed_max = -1
        self.last_speed_fast = -1
        self.off_throttle_timer_start = 0
        self.on_throttle_timer_start = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Read speed data
            speed = api.read.vehicle.speed()
            lap_etime = api.read.timing.elapsed()
            raw_throttle = api.read.input.throttle_raw()

            # Update current speed
            if self.wcfg["show_speed"]:
                self.update_speed("curr", speed, self.last_speed_curr)
                self.last_speed_curr = speed

            # Update minimum speed off throttle
            if self.wcfg["show_speed_minimum"] and raw_throttle < self.wcfg["off_throttle_threshold"]:
                if speed < self.last_speed_min:
                    self.update_speed("min", speed, self.last_speed_min)
                    self.last_speed_min = speed
                    self.off_throttle_timer_start = lap_etime
                if lap_etime - self.off_throttle_timer_start > self.wcfg["speed_minimum_reset_cooldown"]:
                    self.last_speed_min = speed

            # Update maximum speed on throttle
            if self.wcfg["show_speed_maximum"] and raw_throttle > self.wcfg["on_throttle_threshold"]:
                if speed > self.last_speed_max:
                    self.update_speed("max", speed, self.last_speed_max)
                    self.last_speed_max = speed
                    self.on_throttle_timer_start = lap_etime
                if lap_etime - self.on_throttle_timer_start > self.wcfg["speed_maximum_reset_cooldown"]:
                    self.last_speed_max = speed

            # Update fastest speed
            if self.wcfg["show_speed_fastest"]:
                if api.read.engine.gear() < 0:  # reset on reverse gear
                    self.last_speed_fast = 0
                if speed > self.last_speed_fast:
                    self.update_speed("fast", speed, self.last_speed_fast)
                    self.last_speed_fast = speed

    # GUI update methods
    def update_speed(self, suffix, curr, last):
        """Vehicle speed"""
        if curr != last:
            getattr(self, f"bar_speed_{suffix}").setText(
                f"{self.speed_units(curr):0{self.leading_zero}.0{self.decimals}f}")

    # Additional methods
    def speed_units(self, value):
        """Speed units"""
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        if self.cfg.units["speed_unit"] == "m/s":
            return value
        return calc.mps2kph(value)
