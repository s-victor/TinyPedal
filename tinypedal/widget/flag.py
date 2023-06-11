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
Flag Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics
from PySide2.QtWidgets import (
    QGridLayout,
    QLabel,
)

from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "flag"


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
            f"min-width: {font_w * 7}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_ptim = self.wcfg["column_index_pit_timer"]
        column_fuel = self.wcfg["column_index_low_fuel"]
        column_slmt = self.wcfg["column_index_speed_limiter"]
        column_yllw = self.wcfg["column_index_yellow_flag"]
        column_blue = self.wcfg["column_index_blue_flag"]
        column_slit = self.wcfg["column_index_startlights"]

        # Pit status
        if self.wcfg["show_pit_timer"]:
            self.bar_pit_timer = QLabel("PITST0P")
            self.bar_pit_timer.setAlignment(Qt.AlignCenter)
            self.bar_pit_timer.setStyleSheet(
                f"color: {self.wcfg['font_color_pit_timer']};"
                f"background: {self.wcfg['bkg_color_pit_timer']};"
            )

        # Low fuel warning
        if self.wcfg["show_low_fuel"]:
            self.bar_lowfuel = QLabel("LOWFUEL")
            self.bar_lowfuel.setAlignment(Qt.AlignCenter)
            self.bar_lowfuel.setStyleSheet(
                f"color: {self.wcfg['font_color_low_fuel']};"
                f"background: {self.wcfg['bkg_color_low_fuel']};"
            )

        # Speed limiter
        if self.wcfg["show_speed_limiter"]:
            self.bar_limiter = QLabel(self.wcfg["speed_limiter_text"])
            self.bar_limiter.setAlignment(Qt.AlignCenter)
            self.bar_limiter.setStyleSheet(
                f"color: {self.wcfg['font_color_speed_limiter']};"
                f"background: {self.wcfg['bkg_color_speed_limiter']};"
            )

        # Yellow flag
        if self.wcfg["show_yellow_flag"]:
            self.bar_yellowflag = QLabel("YELLOW")
            self.bar_yellowflag.setAlignment(Qt.AlignCenter)
            self.bar_yellowflag.setStyleSheet(
                f"color: {self.wcfg['font_color_yellow_flag']};"
                f"background: {self.wcfg['bkg_color_yellow_flag']};"
            )

        # Blue flag
        if self.wcfg["show_blue_flag"]:
            self.bar_blueflag = QLabel("BLUE")
            self.bar_blueflag.setAlignment(Qt.AlignCenter)
            self.bar_blueflag.setStyleSheet(
                f"color: {self.wcfg['font_color_blue_flag']};"
                f"background: {self.wcfg['bkg_color_blue_flag']};"
            )

        # Start lights
        if self.wcfg["show_startlights"]:
            self.bar_startlights = QLabel("SLIGHTS")
            self.bar_startlights.setAlignment(Qt.AlignCenter)
            self.bar_startlights.setStyleSheet(
                f"color: {self.wcfg['font_color_startlights']};"
                f"background: {self.wcfg['bkg_color_red_lights']};"
            )

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_pit_timer"]:
                layout.addWidget(self.bar_pit_timer, column_ptim, 0)
            if self.wcfg["show_low_fuel"]:
                layout.addWidget(self.bar_lowfuel, column_fuel, 0)
            if self.wcfg["show_speed_limiter"]:
                layout.addWidget(self.bar_limiter, column_slmt, 0)
            if self.wcfg["show_yellow_flag"]:
                layout.addWidget(self.bar_yellowflag, column_yllw, 0)
            if self.wcfg["show_blue_flag"]:
                layout.addWidget(self.bar_blueflag, column_blue, 0)
            if self.wcfg["show_startlights"]:
                layout.addWidget(self.bar_startlights, column_slit, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_pit_timer"]:
                layout.addWidget(self.bar_pit_timer, 0, column_ptim)
            if self.wcfg["show_low_fuel"]:
                layout.addWidget(self.bar_lowfuel, 0, column_fuel)
            if self.wcfg["show_speed_limiter"]:
                layout.addWidget(self.bar_limiter, 0, column_slmt)
            if self.wcfg["show_yellow_flag"]:
                layout.addWidget(self.bar_yellowflag, 0, column_yllw)
            if self.wcfg["show_blue_flag"]:
                layout.addWidget(self.bar_blueflag, 0, column_blue)
            if self.wcfg["show_startlights"]:
                layout.addWidget(self.bar_startlights, 0, column_slit)
        self.setLayout(layout)

        # Last data
        self.set_defaults()

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    def set_defaults(self):
        """Initialize variables"""
        self.checked = False
        self.last_inpits = None
        self.pit_timer_start = None
        self.last_pit_timer = None
        self.last_fuel_usage = None
        self.last_pit_limiter = None
        self.last_blue_flag = None
        self.blue_flag_timer_start = None
        self.last_blue_flag_data = None
        self.last_yellow_flag = None
        self.last_start_timer = None
        self.last_lap_stime = 0

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read flag data
            inpits, pit_limiter, race_phase = read_data.pitting()
            is_race = read_data.is_race()
            lap_stime, lap_etime = read_data.lap_timestamp()

            # Pit timer
            if self.wcfg["show_pit_timer"]:
                pit_timer = -1
                pit_timer_highlight = False
                if inpits != self.last_inpits:
                    if inpits:
                        self.pit_timer_start = lap_etime
                    self.last_inpits = inpits

                if self.pit_timer_start:
                    if inpits:
                        pit_timer = min(lap_etime - self.pit_timer_start, 999.99)
                    elif (lap_etime - self.last_pit_timer - self.pit_timer_start
                          <= self.wcfg["pit_time_highlight_duration"]):
                        pit_timer = self.last_pit_timer + 0.000001
                        pit_timer_highlight = True
                    else:
                        self.pit_timer_start = 0  # stop timer

                self.update_pit_timer(
                    pit_timer, self.last_pit_timer, race_phase, pit_timer_highlight)
                self.last_pit_timer = pit_timer

            # Low fuel update
            if self.wcfg["show_low_fuel"]:
                fuel_info = mctrl.module_fuel.output
                fuel_usage = (
                    min(round(fuel_info.AmountFuelCurrent, 2),
                        self.wcfg["low_fuel_volume_threshold"]),
                    min(round(fuel_info.EstimatedLaps, 1),
                        self.wcfg["low_fuel_lap_threshold"]),
                    bool(not self.wcfg["show_low_fuel_for_race_only"] or
                         self.wcfg["show_low_fuel_for_race_only"] and is_race)
                )

                self.update_lowfuel(fuel_usage, self.last_fuel_usage)
                self.last_fuel_usage = fuel_usage

            # Pit limiter
            if self.wcfg["show_speed_limiter"]:
                self.update_limiter(pit_limiter, self.last_pit_limiter)
                self.last_pit_limiter = pit_limiter

            # Blue flag
            if self.wcfg["show_blue_flag"]:
                #blue_flag = 6  # testing
                blue_flag = read_data.blue_flag()
                blue_flag_timer = -1

                if self.last_blue_flag != blue_flag and blue_flag == 6:
                    self.blue_flag_timer_start = lap_etime
                elif self.last_blue_flag != blue_flag and blue_flag != 6:
                    self.blue_flag_timer_start = 0
                self.last_blue_flag = blue_flag

                if self.blue_flag_timer_start:
                    blue_flag_timer = min(round(lap_etime - self.blue_flag_timer_start, 1), 999)

                blue_flag_data = (
                    blue_flag_timer,
                    bool(not self.wcfg["show_blue_flag_for_race_only"] or
                         self.wcfg["show_blue_flag_for_race_only"] and is_race)
                )
                self.update_blueflag(blue_flag_data, self.last_blue_flag_data)
                self.last_blue_flag_data = blue_flag_data

            # Yellow flag
            if self.wcfg["show_yellow_flag"]:
                #yellow_flag = [1,1,1,0,0]# testing
                yellow_flag = (
                    *read_data.yellow_flag(),  # 0,1,2
                    mctrl.module_standings.nearest.Yellow,  # 3
                    bool(mctrl.module_standings.nearest.Yellow  # 4
                         < self.wcfg["yellow_flag_maximum_range"]),
                    bool(not self.wcfg["show_yellow_flag_for_race_only"] or  # 5
                         self.wcfg["show_yellow_flag_for_race_only"] and is_race)
                )
                self.update_yellowflag(yellow_flag, self.last_yellow_flag)
                self.last_yellow_flag = yellow_flag

            # Start lights
            if self.wcfg["show_startlights"]:
                if race_phase == 4:
                    self.last_lap_stime = lap_stime

                green = 1  # enable green flag
                start_timer = max(self.last_lap_stime - lap_etime,
                                  -self.wcfg["green_flag_duration"])

                if start_timer > 0:
                    green = 0  # enable red lights
                elif -start_timer == self.wcfg["green_flag_duration"]:
                    green = 2  # disable green flag

                if self.wcfg["show_startlights"]:
                    self.update_startlights(start_timer, self.last_start_timer, green)

                self.last_start_timer = start_timer

        else:
            if self.checked:
                self.set_defaults()

    # GUI update methods
    def update_pit_timer(self, curr, last, phase, mode=0):
        """Pit timer"""
        if curr != last:  # timer
            if curr != -1:
                if mode == 0:
                    if phase == 0:
                        color = (f"color: {self.wcfg['font_color_pit_closed']};"
                                 f"background: {self.wcfg['bkg_color_pit_closed']};")
                        state = "P CLOSE"
                    else:
                        color = (f"color: {self.wcfg['font_color_pit_timer']};"
                                 f"background: {self.wcfg['bkg_color_pit_timer']};")
                        state = "P " + f"{curr:.02f}"[:5].rjust(5)
                else:  # highlight
                    color = (f"color: {self.wcfg['font_color_pit_timer_stopped']};"
                             f"background: {self.wcfg['bkg_color_pit_timer_stopped']};")
                    state = "F " + f"{curr:.02f}"[:5].rjust(5)

                self.bar_pit_timer.setText(state)
                self.bar_pit_timer.setStyleSheet(color)
                self.bar_pit_timer.show()
            else:
                self.bar_pit_timer.hide()

    def update_lowfuel(self, curr, last):
        """Low fuel warning"""
        if curr != last:
            if (curr[2] and
                curr[0] < self.wcfg["low_fuel_volume_threshold"] and
                curr[1] < self.wcfg["low_fuel_lap_threshold"]):
                self.bar_lowfuel.setText("LF" + f"{curr[0]:.02f}"[:4].rjust(5))
                self.bar_lowfuel.show()
            else:
                self.bar_lowfuel.hide()

    def update_limiter(self, curr, last):
        """Speed limiter"""
        if curr != last:
            if curr == 1:
                self.bar_limiter.show()
            else:
                self.bar_limiter.hide()

    def update_blueflag(self, curr, last):
        """Blue flag"""
        if curr != last:
            if curr[1] and curr[0] != -1:
                self.bar_blueflag.setText(f"BLUE{curr[0]:3.0f}")
                self.bar_blueflag.show()
            else:
                self.bar_blueflag.hide()

    def update_yellowflag(self, curr, last):
        """Yellow flag"""
        if curr != last:
            if curr[0] == 1 or curr[1] == 1 or curr[2] == 1:
                yellow = True
            else:
                yellow = False

            if curr[5] and yellow and curr[4]:
                self.bar_yellowflag.setText(f"Y{curr[3]:5.0f}M")
                self.bar_yellowflag.show()
            else:
                self.bar_yellowflag.hide()

    def update_startlights(self, curr, last, green=0):
        """Start lights"""
        if curr != last:
            if green == 0:
                self.bar_startlights.setText(
                    f"{self.wcfg['red_lights_text'][:6].ljust(6)}{read_data.startlights()}")
                self.bar_startlights.setStyleSheet(
                    f"color: {self.wcfg['font_color_startlights']};"
                    f"background: {self.wcfg['bkg_color_red_lights']};")
                self.bar_startlights.show()
            elif green == 1:
                self.bar_startlights.setText(
                    self.wcfg["green_flag_text"])
                self.bar_startlights.setStyleSheet(
                    f"color: {self.wcfg['font_color_startlights']};"
                    f"background: {self.wcfg['bkg_color_green_flag']};")
                self.bar_startlights.show()
            else:
                self.bar_startlights.hide()

    # Additional methods
    @staticmethod
    def yflag_text(value, sector):
        """Yellow flag text"""
        if value == 1:
            return f" S{sector}"
        return ""
