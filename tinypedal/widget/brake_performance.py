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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import formatter as fmt
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "brake_performance"


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
        self.bar_width = font_m.width * 5

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

        column_tbr = self.wcfg["column_index_transient_max_braking_rate"]
        column_mbr = self.wcfg["column_index_max_braking_rate"]
        column_dbr = self.wcfg["column_index_delta_braking_rate"]
        column_fwl = self.wcfg["column_index_front_wheel_lock_duration"]
        column_rwl = self.wcfg["column_index_rear_wheel_lock_duration"]

        # Transient max braking rate
        if self.wcfg["show_transient_max_braking_rate"]:
            self.bar_transient_rate = QLabel("0.00g")
            self.bar_transient_rate.setAlignment(Qt.AlignCenter)
            self.bar_transient_rate.setStyleSheet(
                f"color: {self.wcfg['font_color_transient_max_braking_rate']};"
                f"background: {self.wcfg['bkg_color_transient_max_braking_rate']};"
                f"min-width: {self.bar_width}px;"
            )

        # Max braking rate
        if self.wcfg["show_max_braking_rate"]:
            self.bar_max_rate = QLabel("0.00g")
            self.bar_max_rate.setAlignment(Qt.AlignCenter)
            self.bar_max_rate.setStyleSheet(
                f"color: {self.wcfg['font_color_max_braking_rate']};"
                f"background: {self.wcfg['bkg_color_max_braking_rate']};"
                f"min-width: {self.bar_width}px;"
            )

        # Delta braking rate
        if self.wcfg["show_delta_braking_rate"]:
            self.bar_delta_rate = QLabel("+0.00")
            self.bar_delta_rate.setAlignment(Qt.AlignCenter)
            self.bar_delta_rate.setStyleSheet(
                f"color: {self.wcfg['font_color_delta_braking_rate']};"
                f"background: {self.wcfg['bkg_color_delta_braking_rate']};"
                f"min-width: {self.bar_width}px;"
            )

        # Front wheel lock duration
        if self.wcfg["show_front_wheel_lock_duration"]:
            self.bar_lock_time_f = QLabel("F 0.0")
            self.bar_lock_time_f.setAlignment(Qt.AlignCenter)
            self.bar_lock_time_f.setStyleSheet(
                f"color: {self.wcfg['font_color_front_wheel_lock_duration']};"
                f"background: {self.wcfg['bkg_color_front_wheel_lock_duration']};"
                f"min-width: {self.bar_width}px;"
            )

        # Front wheel lock duration
        if self.wcfg["show_rear_wheel_lock_duration"]:
            self.bar_lock_time_r = QLabel("R 0.0")
            self.bar_lock_time_r.setAlignment(Qt.AlignCenter)
            self.bar_lock_time_r.setStyleSheet(
                f"color: {self.wcfg['font_color_rear_wheel_lock_duration']};"
                f"background: {self.wcfg['bkg_color_rear_wheel_lock_duration']};"
                f"min-width: {self.bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_transient_max_braking_rate"]:
                layout.addWidget(self.bar_transient_rate, column_tbr, 0)
            if self.wcfg["show_max_braking_rate"]:
                layout.addWidget(self.bar_max_rate, column_mbr, 0)
            if self.wcfg["show_delta_braking_rate"]:
                layout.addWidget(self.bar_delta_rate, column_dbr, 0)
            if self.wcfg["show_front_wheel_lock_duration"]:
                layout.addWidget(self.bar_lock_time_f, column_fwl, 0)
            if self.wcfg["show_rear_wheel_lock_duration"]:
                layout.addWidget(self.bar_lock_time_r, column_rwl, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_transient_max_braking_rate"]:
                layout.addWidget(self.bar_transient_rate, 0, column_tbr)
            if self.wcfg["show_max_braking_rate"]:
                layout.addWidget(self.bar_max_rate, 0, column_mbr)
            if self.wcfg["show_delta_braking_rate"]:
                layout.addWidget(self.bar_delta_rate, 0, column_dbr)
            if self.wcfg["show_front_wheel_lock_duration"]:
                layout.addWidget(self.bar_lock_time_f, 0, column_fwl)
            if self.wcfg["show_rear_wheel_lock_duration"]:
                layout.addWidget(self.bar_lock_time_r, 0, column_rwl)
        self.setLayout(layout)

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

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

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

                if lap_stime != self.last_lap_stime:
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
            format_text = f"{curr:.02f}"[:4]
            self.bar_transient_rate.setText(f"{format_text}g")

    def update_max_rate(self, curr, last):
        """Max braking rate"""
        if curr != last:
            format_text = f"{curr:.02f}"[:4]
            self.bar_max_rate.setText(f"{format_text}g")

    def update_delta_rate(self, curr, last):
        """Delta braking rate"""
        if curr != last:
            if curr > 0:
                color = (f"color: {self.wcfg['font_color_delta_braking_rate']};"
                         f"background: {self.wcfg['bkg_color_braking_rate_gain']};")
            elif curr < 0:
                color = (f"color: {self.wcfg['font_color_delta_braking_rate']};"
                         f"background: {self.wcfg['bkg_color_braking_rate_loss']};")
            else:
                color = (f"color: {self.wcfg['font_color_delta_braking_rate']};"
                         f"background: {self.wcfg['bkg_color_delta_braking_rate']};")

            if self.wcfg["show_delta_braking_rate_in_percentage"] and minfo.force.maxBrakingRate:
                format_text = f"{curr / minfo.force.maxBrakingRate:+.0%}"
            else:
                format_text = f"{curr:+.02f}"
            self.bar_delta_rate.setText(format_text[:5])
            self.bar_delta_rate.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_lock_time_f(self, curr, last):
        """Front wheel lock duration"""
        if curr != last:
            format_text = fmt.strip_decimal_pt(f"{curr:.01f}"[:3]).rjust(3)
            self.bar_lock_time_f.setText(f"F {format_text}")

    def update_lock_time_r(self, curr, last):
        """Rear wheel lock duration"""
        if curr != last:
            format_text = fmt.strip_decimal_pt(f"{curr:.01f}"[:3]).rjust(3)
            self.bar_lock_time_r.setText(f"R {format_text}")
