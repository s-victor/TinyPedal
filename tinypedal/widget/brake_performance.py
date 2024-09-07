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
Brake performance Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "brake_performance"


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
        bar_width = font_m.width * 5 + bar_padx

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

        # Transient max braking rate
        if self.wcfg["show_transient_max_braking_rate"]:
            bar_style_trans_rate = self.set_qss(
                self.wcfg["font_color_transient_max_braking_rate"],
                self.wcfg["bkg_color_transient_max_braking_rate"]
            )
            self.bar_trans_rate = self.set_qlabel(
                text="0.00g",
                style=bar_style_trans_rate,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_trans_rate,
                column=self.wcfg["column_index_transient_max_braking_rate"],
            )

        # Max braking rate
        if self.wcfg["show_max_braking_rate"]:
            bar_style_max_rate = self.set_qss(
                self.wcfg["font_color_max_braking_rate"],
                self.wcfg["bkg_color_max_braking_rate"]
            )
            self.bar_max_rate = self.set_qlabel(
                text="0.00g",
                style=bar_style_max_rate,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_max_rate,
                column=self.wcfg["column_index_max_braking_rate"],
            )

        # Delta braking rate
        if self.wcfg["show_delta_braking_rate"]:
            self.bar_style_delta_rate = (
                self.set_qss(
                    self.wcfg["font_color_delta_braking_rate"],
                    self.wcfg["bkg_color_delta_braking_rate"]),
                self.set_qss(
                    self.wcfg["font_color_delta_braking_rate"],
                    self.wcfg["bkg_color_braking_rate_gain"]),
                self.set_qss(
                    self.wcfg["font_color_delta_braking_rate"],
                    self.wcfg["bkg_color_braking_rate_loss"])
            )
            self.bar_delta_rate = self.set_qlabel(
                text="+0.00",
                style=self.bar_style_delta_rate[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_delta_rate,
                column=self.wcfg["column_index_delta_braking_rate"],
            )

        # Front wheel lock duration
        if self.wcfg["show_front_wheel_lock_duration"]:
            bar_style_lock_f = self.set_qss(
                self.wcfg["font_color_front_wheel_lock_duration"],
                self.wcfg["bkg_color_front_wheel_lock_duration"]
            )
            self.bar_lock_f = self.set_qlabel(
                text="F 0.0",
                style=bar_style_lock_f,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_lock_f,
                column=self.wcfg["column_index_front_wheel_lock_duration"],
            )

        # Front wheel lock duration
        if self.wcfg["show_rear_wheel_lock_duration"]:
            bar_style_lock_r = self.set_qss(
                self.wcfg["font_color_rear_wheel_lock_duration"],
                self.wcfg["bkg_color_rear_wheel_lock_duration"]
            )
            self.bar_lock_r = self.set_qlabel(
                text="R 0.0",
                style=bar_style_lock_r,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_lock_r,
                column=self.wcfg["column_index_rear_wheel_lock_duration"],
            )

        # Last data
        self.last_transient_rate = 0
        self.last_max_rate = 0
        self.last_delta_rate = 0
        self.lock_time_f = 0
        self.last_lock_time_f = 0
        self.lock_time_r = 0
        self.last_lock_time_r = 0
        self.last_lap_etime = 0
        self.last_lap_stime = 0
        self.reset_lock_duration = False

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Transient max braking rate
            if self.wcfg["show_transient_max_braking_rate"]:
                transient_rate = minfo.force.transientMaxBrakingRate
                self.update_transient_rate(transient_rate, self.last_transient_rate)
                self.last_transient_rate = transient_rate

            # Max braking rate
            if self.wcfg["show_max_braking_rate"]:
                max_rate = minfo.force.maxBrakingRate
                self.update_max_rate(max_rate, self.last_max_rate)
                self.last_max_rate = max_rate

            # Delta braking rate
            if self.wcfg["show_delta_braking_rate"]:
                delta_rate = minfo.force.deltaBrakingRate
                self.update_delta_rate(delta_rate, self.last_delta_rate)
                self.last_delta_rate = delta_rate

            # Wheel lock duration
            if self.wcfg["show_front_wheel_lock_duration"] or self.wcfg["show_rear_wheel_lock_duration"]:
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()

                if lap_stime != self.last_lap_stime:  # reset on new lap
                    self.last_lap_stime = lap_stime
                    self.reset_lock_duration = True  # trigger reset on next braking

                if api.read.input.brake_raw() > 0.03:
                    if self.reset_lock_duration:
                        self.lock_time_f = 0
                        self.lock_time_r = 0
                        self.reset_lock_duration = False
                    if min(minfo.wheels.slipRatio[0:2]) < -self.wcfg["wheel_lock_threshold"]:
                        if self.last_lap_etime < lap_etime:
                            self.lock_time_f += lap_etime - self.last_lap_etime
                    if min(minfo.wheels.slipRatio[2:4]) < -self.wcfg["wheel_lock_threshold"]:
                        if self.last_lap_etime < lap_etime:
                            self.lock_time_r += lap_etime - self.last_lap_etime
                self.last_lap_etime = lap_etime

            if self.wcfg["show_front_wheel_lock_duration"]:
                self.update_lock_time_f(self.lock_time_f, self.last_lock_time_f)
                self.last_lock_time_f = self.lock_time_f

            if self.wcfg["show_rear_wheel_lock_duration"]:
                self.update_lock_time_r(self.lock_time_r, self.last_lock_time_r)
                self.last_lock_time_r = self.lock_time_r

    # GUI update methods
    def update_transient_rate(self, curr, last):
        """Transient max braking rate"""
        if curr != last:
            self.bar_trans_rate.setText(f"{curr: >4.2f}g"[:5])

    def update_max_rate(self, curr, last):
        """Max braking rate"""
        if curr != last:
            self.bar_max_rate.setText(f"{curr: >4.2f}g"[:5])

    def update_delta_rate(self, curr, last):
        """Delta braking rate"""
        if curr != last:
            if curr > 0:
                color = 1
            elif curr < 0:
                color = 2
            else:
                color = 0

            if self.wcfg["show_delta_braking_rate_in_percentage"]:
                if minfo.force.maxBrakingRate:
                    format_text = f"{curr / minfo.force.maxBrakingRate:+.0%}"[:5]
                else:
                    format_text = "+0%"
            else:
                format_text = f"{curr:+.2f}"[:5]
            self.bar_delta_rate.setText(format_text)
            self.bar_delta_rate.setStyleSheet(self.bar_style_delta_rate[color])

    def update_lock_time_f(self, curr, last):
        """Front wheel lock duration"""
        if curr != last:
            format_text = f"{curr:.1f}"[:3].strip(".").rjust(3)
            self.bar_lock_f.setText(f"F {format_text}")

    def update_lock_time_r(self, curr, last):
        """Rear wheel lock duration"""
        if curr != last:
            format_text = f"{curr:.1f}"[:3].strip(".").rjust(3)
            self.bar_lock_r.setText(f"R {format_text}")
