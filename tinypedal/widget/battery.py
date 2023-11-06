#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import readapi
from ..base import Widget
from ..module_info import minfo

WIDGET_NAME = "battery"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        font_w = QFontMetrics(self.font).averageCharWidth()

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_w * 8

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

        column_bc = self.wcfg["column_index_battery_charge"]
        column_bd = self.wcfg["column_index_battery_drain"]
        column_br = self.wcfg["column_index_battery_regen"]
        column_at = self.wcfg["column_index_activation_timer"]

        # Battery charge
        if self.wcfg["show_battery_charge"]:
            self.bar_battery_charge = QLabel("BATTERY")
            self.bar_battery_charge.setAlignment(Qt.AlignCenter)
            self.bar_battery_charge.setStyleSheet(
                f"color: {self.wcfg['font_color_battery_charge']};"
                f"background: {self.wcfg['bkg_color_battery_charge']};"
                f"min-width: {self.bar_width}px;"
            )

        # Battery drain
        if self.wcfg["show_battery_drain"]:
            self.bar_battery_drain = QLabel("B DRAIN")
            self.bar_battery_drain.setAlignment(Qt.AlignCenter)
            self.bar_battery_drain.setStyleSheet(
                f"color: {self.wcfg['font_color_battery_drain']};"
                f"background: {self.wcfg['bkg_color_battery_drain']};"
                f"min-width: {self.bar_width}px;"
            )

        # Battery regen
        if self.wcfg["show_battery_regen"]:
            self.bar_battery_regen = QLabel("B REGEN")
            self.bar_battery_regen.setAlignment(Qt.AlignCenter)
            self.bar_battery_regen.setStyleSheet(
                f"color: {self.wcfg['font_color_battery_regen']};"
                f"background: {self.wcfg['bkg_color_battery_regen']};"
                f"min-width: {self.bar_width}px;"
            )

        # Activation timer
        if self.wcfg["show_activation_timer"]:
            self.bar_activation_timer = QLabel("B TIMER")
            self.bar_activation_timer.setAlignment(Qt.AlignCenter)
            self.bar_activation_timer.setStyleSheet(
                f"color: {self.wcfg['font_color_activation_timer']};"
                f"background: {self.wcfg['bkg_color_activation_timer']};"
                f"min-width: {self.bar_width}px;"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_battery_charge"]:
                layout.addWidget(self.bar_battery_charge, column_bc, 0)
            if self.wcfg["show_battery_drain"]:
                layout.addWidget(self.bar_battery_drain, column_bd, 0)
            if self.wcfg["show_battery_regen"]:
                layout.addWidget(self.bar_battery_regen, column_br, 0)
            if self.wcfg["show_activation_timer"]:
                layout.addWidget(self.bar_activation_timer, column_at, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_battery_charge"]:
                layout.addWidget(self.bar_battery_charge, 0, column_bc)
            if self.wcfg["show_battery_drain"]:
                layout.addWidget(self.bar_battery_drain, 0, column_bd)
            if self.wcfg["show_battery_regen"]:
                layout.addWidget(self.bar_battery_regen, 0, column_br)
            if self.wcfg["show_activation_timer"]:
                layout.addWidget(self.bar_activation_timer, 0, column_at)
        self.setLayout(layout)

        # Last data
        self.last_lap_stime = 0  # last lap start time

        self.last_battery_charge = None
        self.last_battery_drain = None
        self.last_battery_regen = None
        self.last_motor_active_timer = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and readapi.state():

            lap_stime, lap_etime = readapi.lap_timestamp()

            # Battery charge & usage
            if self.wcfg["show_battery_charge"]:
                self.update_battery_charge(
                    minfo.hybrid.BatteryCharge, self.last_battery_charge)

            if lap_stime != self.last_lap_stime:
                elapsed_time = lap_etime - lap_stime
                if elapsed_time >= self.wcfg["freeze_duration"] or elapsed_time < 0:
                    self.last_lap_stime = lap_stime
                battery_drain = minfo.hybrid.BatteryDrainLast
                battery_regen = minfo.hybrid.BatteryRegenLast
            else:
                battery_drain = minfo.hybrid.BatteryDrain
                battery_regen = minfo.hybrid.BatteryRegen

            if self.wcfg["show_battery_drain"]:
                self.update_battery_drain(battery_drain, self.last_battery_drain)
                self.last_battery_drain = battery_drain

            if self.wcfg["show_battery_regen"]:
                self.update_battery_regen(battery_regen, self.last_battery_regen)
                self.last_battery_regen = battery_regen

            self.last_battery_charge = minfo.hybrid.BatteryCharge

            # Motor activation timer
            if self.wcfg["show_activation_timer"]:
                self.update_activation_timer(
                    minfo.hybrid.MotorActiveTimer, self.last_motor_active_timer)
                self.last_motor_active_timer = minfo.hybrid.MotorActiveTimer

    # GUI update methods
    def update_battery_charge(self, curr, last):
        """Battery charge"""
        if curr != last:
            if curr > self.wcfg["low_battery_threshold"]:
                color = (f"color: {self.wcfg['font_color_battery_charge']};"
                         f"background: {self.wcfg['bkg_color_battery_charge']};")
            else:
                color = (f"color: {self.wcfg['font_color_battery_charge']};"
                         f"background: {self.wcfg['warning_color_low_battery']};")

            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_charge.setText(f"B{format_text}")
            self.bar_battery_charge.setStyleSheet(
                f"{color}min-width: {self.bar_width}px;")

    def update_battery_drain(self, curr, last):
        """Battery drain"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_drain.setText(f"-{format_text}")

    def update_battery_regen(self, curr, last):
        """Battery regen"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_battery_regen.setText(f"+{format_text}")

    def update_activation_timer(self, curr, last):
        """Motor activation timer"""
        if curr != last:
            format_text = f"{curr:.02f}"[:7].rjust(7)
            self.bar_activation_timer.setText(f"{format_text}s")
