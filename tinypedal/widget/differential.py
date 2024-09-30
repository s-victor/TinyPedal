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
Differential Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "differential"


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
        self.leading_space = 3 + self.decimals + (self.decimals > 0)

        if self.wcfg["layout"] == 0:
            prefix_just = max(
                len(self.wcfg["prefix_power_front"]),
                len(self.wcfg["prefix_coast_front"]),
                len(self.wcfg["prefix_power_rear"]),
                len(self.wcfg["prefix_coast_rear"]),
            )
        else:
            prefix_just = 0

        self.prefix_power_f = self.wcfg["prefix_power_front"].ljust(prefix_just)
        self.prefix_coast_f = self.wcfg["prefix_coast_front"].ljust(prefix_just)
        self.prefix_power_r = self.wcfg["prefix_power_rear"].ljust(prefix_just)
        self.prefix_coast_r = self.wcfg["prefix_coast_rear"].ljust(prefix_just)

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

        # Power locking front
        if self.wcfg["show_power_locking_front"]:
            text_power_front = f"{self.prefix_power_f}{self.format_reading(1)}"
            bar_style_power_front = self.set_qss(
                fg_color=self.wcfg["font_color_power_locking_front"],
                bg_color=self.wcfg["bkg_color_power_locking_front"]
            )
            self.bar_power_front = self.set_qlabel(
                text=text_power_front,
                style=bar_style_power_front,
                width=font_m.width * len(text_power_front) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_power_front,
                column=self.wcfg["column_index_power_locking_front"],
            )

        # Coast locking front
        if self.wcfg["show_coast_locking_front"]:
            text_coast_front = f"{self.prefix_coast_f}{self.format_reading(1)}"
            bar_style_coast_front = self.set_qss(
                fg_color=self.wcfg["font_color_coast_locking_front"],
                bg_color=self.wcfg["bkg_color_coast_locking_front"]
            )
            self.bar_coast_front = self.set_qlabel(
                text=text_coast_front,
                style=bar_style_coast_front,
                width=font_m.width * len(text_coast_front) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_coast_front,
                column=self.wcfg["column_index_coast_locking_front"],
            )

        # Power locking rear
        if self.wcfg["show_power_locking_rear"]:
            text_power_rear = f"{self.prefix_power_r}{self.format_reading(1)}"
            bar_style_power_rear = self.set_qss(
                fg_color=self.wcfg["font_color_power_locking_rear"],
                bg_color=self.wcfg["bkg_color_power_locking_rear"]
            )
            self.bar_power_rear = self.set_qlabel(
                text=text_power_rear,
                style=bar_style_power_rear,
                width=font_m.width * len(text_power_rear) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_power_rear,
                column=self.wcfg["column_index_power_locking_rear"],
            )

        # Coast locking rear
        if self.wcfg["show_coast_locking_rear"]:
            text_coast_rear = f"{self.prefix_coast_r}{self.format_reading(1)}"
            bar_style_coast_rear = self.set_qss(
                fg_color=self.wcfg["font_color_coast_locking_rear"],
                bg_color=self.wcfg["bkg_color_coast_locking_rear"]
            )
            self.bar_coast_rear = self.set_qlabel(
                text=text_coast_rear,
                style=bar_style_coast_rear,
                width=font_m.width * len(text_coast_rear) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_coast_rear,
                column=self.wcfg["column_index_coast_locking_rear"],
            )

        # Last data
        self.power_timer_f = 0
        self.coast_timer_f = 0
        self.min_power_f = 1
        self.min_coast_f = 1
        self.last_power_f = 0
        self.last_coast_f = 0

        self.power_timer_r = 0
        self.coast_timer_r = 0
        self.min_power_r = 1
        self.min_coast_r = 1
        self.last_power_r = 0
        self.last_coast_r = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            raw_throttle = api.read.input.throttle_raw()
            lap_etime = api.read.timing.elapsed()
            locking_front = minfo.wheels.lockingPercentFront
            locking_rear = minfo.wheels.lockingPercentRear

            # Power locking front
            if self.wcfg["show_power_locking_front"] and raw_throttle > self.wcfg["on_throttle_threshold"]:
                if self.min_power_f > locking_front:
                    self.min_power_f = locking_front
                    self.power_timer_f = lap_etime
                    self.update_locking(
                        self.bar_power_front, self.min_power_f, self.last_power_f,
                        self.prefix_power_f
                    )
                    self.last_power_f = self.min_power_f
                elif lap_etime - self.power_timer_f > self.wcfg["power_locking_reset_cooldown"]:
                    self.min_power_f = 1
                elif self.power_timer_f > lap_etime:  # timer correction
                    self.power_timer_f = lap_etime

            # Coast locking front
            if self.wcfg["show_coast_locking_front"] and raw_throttle < self.wcfg["off_throttle_threshold"]:
                if self.min_coast_f > locking_front:
                    self.min_coast_f = locking_front
                    self.coast_timer_f = lap_etime
                    self.update_locking(
                        self.bar_coast_front, self.min_coast_f, self.last_coast_f,
                        self.prefix_coast_f
                    )
                    self.last_coast_f = self.min_coast_f
                elif lap_etime - self.coast_timer_f > self.wcfg["coast_locking_reset_cooldown"]:
                    self.min_coast_f = 1
                elif self.coast_timer_f > lap_etime:
                    self.coast_timer_f = lap_etime

            # Power locking rear
            if self.wcfg["show_power_locking_rear"] and raw_throttle > self.wcfg["on_throttle_threshold"]:
                if self.min_power_r > locking_rear:
                    self.min_power_r = locking_rear
                    self.power_timer_r = lap_etime
                    self.update_locking(
                        self.bar_power_rear, self.min_power_r, self.last_power_r,
                        self.prefix_power_r
                    )
                    self.last_power_r = self.min_power_r
                elif lap_etime - self.power_timer_r > self.wcfg["power_locking_reset_cooldown"]:
                    self.min_power_r = 1
                elif self.power_timer_r > lap_etime:
                    self.power_timer_r = lap_etime

            # Coast locking rear
            if self.wcfg["show_coast_locking_rear"] and raw_throttle < self.wcfg["off_throttle_threshold"]:
                if self.min_coast_r > locking_rear:
                    self.min_coast_r = locking_rear
                    self.coast_timer_r = lap_etime
                    self.update_locking(
                        self.bar_coast_rear, self.min_coast_r, self.last_coast_r,
                        self.prefix_coast_r
                        )
                    self.last_coast_r = self.min_coast_r
                elif lap_etime - self.coast_timer_r > self.wcfg["coast_locking_reset_cooldown"]:
                    self.min_coast_r = 1
                elif self.coast_timer_r > lap_etime:
                    self.coast_timer_r = lap_etime

    # GUI update methods
    def update_locking(self, target_bar, curr, last, prefix):
        """Differential locking percent"""
        if curr != last:
            target_bar.setText(f"{prefix}{self.format_reading(curr)}")

    # Additional methods
    def format_reading(self, value):
        """Format reading"""
        if self.wcfg["show_inverted_locking"]:
            value = 1 - value
        return f"{value: >{self.leading_space}.{self.decimals}%}"[:self.leading_space]
