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
Speedometer Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget

WIDGET_NAME = "speedometer"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2


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

        column_sc = self.wcfg["column_index_speed_current"]
        column_sb = self.wcfg["column_index_speed_best"]

        # Speed
        self.bar_width_speed = font_w * 5
        self.bar_speed_curr = QLabel("")
        self.bar_speed_curr.setAlignment(Qt.AlignCenter)
        self.bar_speed_curr.setStyleSheet(
            f"color: {self.wcfg['font_color_speed']};"
            f"background: {self.wcfg['bkg_color_speed']};"
            f"min-width: {self.bar_width_speed}px;"
        )
        self.bar_speed_best = QLabel("")
        self.bar_speed_best.setAlignment(Qt.AlignCenter)
        self.bar_speed_best.setStyleSheet(
            f"color: {self.wcfg['font_color_speed']};"
            f"background: {self.wcfg['bkg_color_speed']};"
            f"min-width: {self.bar_width_speed}px;"
        )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            layout.addWidget(self.bar_speed_curr, column_sc, 0)
            layout.addWidget(self.bar_speed_best, column_sb, 0)
        else:
            # Horizontal layout
            layout.addWidget(self.bar_speed_curr, 0, column_sc)
            layout.addWidget(self.bar_speed_best, 0, column_sb)
        self.setLayout(layout)

        # Last data
        self.last_cb_topspeed = None
        self.last_ub_topspeed = None

        self.last_lap_stime = 0                  # last lap start time
        self.valid_topspeed = True
        self.cb_topspeed = 0                     # current-lap best top speed
        self.sb_topspeed = 0                     # session best top speed
        self.ub_topspeed = 0                     # unverified session best top speed
        self.speed_timer_start = 0               # speed timer start

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read Sector data
            lap_stime, lap_etime = read_data.lap_timestamp()
            laptime_curr = max(lap_etime - lap_stime, 0)
            speed = read_data.speed()

            # Lap start & finish detection
            if lap_stime != self.last_lap_stime:  # time stamp difference
                self.cb_topspeed = speed  # reset current lap fastest speed
                self.last_lap_stime = lap_stime  # reset
                self.valid_topspeed = False

            # Validate fastest speed
            if not self.valid_topspeed and laptime_curr > 1:
                self.sb_topspeed = self.ub_topspeed
                # Update session top speed display
                self.update_speed_best(self.ub_topspeed, MAGIC_NUM)
                self.valid_topspeed = True

            # Update current top speed display
            if speed > self.cb_topspeed:
                self.cb_topspeed = speed
            self.update_speed_curr(self.cb_topspeed, self.last_cb_topspeed)
            self.last_cb_topspeed = self.cb_topspeed

            # Update session top speed display
            if speed > self.ub_topspeed:
                self.ub_topspeed = speed
                self.speed_timer_start = lap_etime  # start timer if speed higher

            if self.speed_timer_start:
                speed_timer = lap_etime - self.speed_timer_start
                if speed_timer >= max(self.wcfg["speed_highlight_duration"], 0):
                    self.speed_timer_start = 0  # stop timer
                    self.update_speed_best(self.ub_topspeed, MAGIC_NUM)
                else:
                    self.update_speed_best(self.ub_topspeed, self.last_ub_topspeed, True)

            self.last_ub_topspeed = self.ub_topspeed

    # GUI update methods
    def update_speed_curr(self, curr, last):
        """Current lap best top speed"""
        if curr != last:
            self.bar_speed_curr.setText(
                f"{self.speed_units(curr):.01f}")

    def update_speed_best(self, curr, last, highlighted=False):
        """Session best top speed"""
        if curr != last:
            speed_text = f"{self.speed_units(curr):.01f}"
            if highlighted:
                color = (f"color: {self.wcfg['font_color_speed_highlighted']};"
                         f"background: {self.wcfg['bkg_color_speed_highlighted']};")
            else:
                color = (f"color: {self.wcfg['font_color_speed']};"
                         f"background: {self.wcfg['bkg_color_speed']};")

            self.bar_speed_best.setText(speed_text)
            self.bar_speed_best.setStyleSheet(
                f"{color}min-width: {self.bar_width_speed}px;")

    # Additional methods
    def speed_units(self, value):
        """Speed units"""
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        if self.cfg.units["speed_unit"] == "m/s":
            return value
        return calc.mps2kph(value)
