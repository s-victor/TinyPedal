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
Flag Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "flag"


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

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
            f"min-width: {font_m.width * 7}px;"
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
        column_icom = self.wcfg["column_index_traffic"]
        column_preq = self.wcfg["column_index_pit_request"]
        column_fins = self.wcfg["column_index_finish_state"]

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

        # Incoming traffic
        if self.wcfg["show_traffic"]:
            self.bar_traffic = QLabel("TRAFFIC")
            self.bar_traffic.setAlignment(Qt.AlignCenter)
            self.bar_traffic.setStyleSheet(
                f"color: {self.wcfg['font_color_traffic']};"
                f"background: {self.wcfg['bkg_color_traffic']};"
            )

        # Pit request
        if self.wcfg["show_pit_request"]:
            self.bar_pit_request = QLabel("PIT REQ")
            self.bar_pit_request.setAlignment(Qt.AlignCenter)
            self.bar_pit_request.setStyleSheet(
                f"color: {self.wcfg['font_color_pit_request']};"
                f"background: {self.wcfg['bkg_color_pit_request']};"
            )

        # Finish state
        if self.wcfg["show_finish_state"]:
            self.bar_finish_state = QLabel("FINISH")
            self.bar_finish_state.setAlignment(Qt.AlignCenter)
            self.bar_finish_state.setStyleSheet(
                f"color: {self.wcfg['font_color_finish']};"
                f"background: {self.wcfg['bkg_color_finish']};"
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
            if self.wcfg["show_traffic"]:
                layout.addWidget(self.bar_traffic, column_icom, 0)
            if self.wcfg["show_pit_request"]:
                layout.addWidget(self.bar_pit_request, column_preq, 0)
            if self.wcfg["show_finish_state"]:
                layout.addWidget(self.bar_finish_state, column_fins, 0)
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
            if self.wcfg["show_traffic"]:
                layout.addWidget(self.bar_traffic, 0, column_icom)
            if self.wcfg["show_pit_request"]:
                layout.addWidget(self.bar_pit_request, 0, column_preq)
            if self.wcfg["show_finish_state"]:
                layout.addWidget(self.bar_finish_state, 0, column_fins)
        self.setLayout(layout)

        # Last data
        self.set_defaults()

        # Set widget state & start update
        self.set_widget_state()

    def set_defaults(self):
        """Initialize variables"""
        self.checked = False
        self.last_in_pits = None
        self.pit_timer_start = None
        self.last_pit_timer = None
        self.last_fuel_usage = None
        self.last_limiter = None
        self.last_blue_flag = None
        self.blue_flag_timer_start = None
        self.last_blue_flag_data = None
        self.last_yellow_flag = None
        self.last_start_timer = None
        self.last_lap_stime = 0
        self.last_traffic = None
        self.traffic_timer_start = None
        self.last_pit_request = None
        self.last_finish_state = None

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read flag data
            lap_stime = api.read.timing.start()
            lap_etime = api.read.timing.elapsed()
            in_pits = api.read.vehicle.in_pits()
            pit_open = api.read.session.pit_open()
            in_countdown = api.read.session.in_countdown()
            in_race = api.read.session.in_race()

            # Pit timer
            if self.wcfg["show_pit_timer"]:
                pit_timer = -1
                pit_timer_highlight = False
                if in_pits != self.last_in_pits:
                    if in_pits:
                        self.pit_timer_start = lap_etime
                    #self.last_in_pits = in_pits

                if self.pit_timer_start:
                    if in_pits:
                        pit_timer = min(lap_etime - self.pit_timer_start, 999.99)
                    elif (lap_etime - self.last_pit_timer - self.pit_timer_start
                          <= self.wcfg["pit_time_highlight_duration"]):
                        pit_timer = self.last_pit_timer + 0.000001
                        pit_timer_highlight = True
                    else:
                        self.pit_timer_start = 0  # stop timer

                self.update_pit_timer(
                    pit_timer, self.last_pit_timer, pit_open, pit_timer_highlight)
                self.last_pit_timer = pit_timer

            # Low fuel update
            if self.wcfg["show_low_fuel"]:
                fuel_usage = (
                    min(round(minfo.fuel.amountFuelCurrent, 2),
                        self.wcfg["low_fuel_volume_threshold"]),
                    min(round(minfo.fuel.estimatedLaps, 1),
                        self.wcfg["low_fuel_lap_threshold"]),
                    bool(not self.wcfg["show_low_fuel_for_race_only"] or
                         self.wcfg["show_low_fuel_for_race_only"] and in_race)
                )
                self.update_lowfuel(fuel_usage, self.last_fuel_usage)
                self.last_fuel_usage = fuel_usage

            # Pit limiter
            if self.wcfg["show_speed_limiter"]:
                limiter = api.read.switch.speed_limiter()
                self.update_limiter(limiter, self.last_limiter)
                self.last_limiter = limiter

            # Blue flag
            if self.wcfg["show_blue_flag"]:
                #blue_flag = 6  # testing
                blue_flag = api.read.session.blue_flag()
                blue_flag_timer = -1

                if self.last_blue_flag != blue_flag:
                    self.blue_flag_timer_start = lap_etime if blue_flag else 0
                self.last_blue_flag = blue_flag

                if self.blue_flag_timer_start:
                    blue_flag_timer = min(round(lap_etime - self.blue_flag_timer_start, 1), 999)

                blue_flag_data = (
                    blue_flag_timer,
                    bool(not self.wcfg["show_blue_flag_for_race_only"] or
                         self.wcfg["show_blue_flag_for_race_only"] and in_race)
                )
                self.update_blueflag(blue_flag_data, self.last_blue_flag_data)
                self.last_blue_flag_data = blue_flag_data

            # Yellow flag
            if self.wcfg["show_yellow_flag"]:
                #yellow_flag = [1,0,0,0]# testing
                is_yellow_near = minfo.vehicles.nearestYellow < self.wcfg["yellow_flag_maximum_range"]
                is_yellow_show = bool(not self.wcfg["show_yellow_flag_for_race_only"] or
                                      self.wcfg["show_yellow_flag_for_race_only"] and in_race)
                yellow_flag = (
                    api.read.session.yellow_flag() and is_yellow_near and is_yellow_show,
                    minfo.vehicles.nearestYellow
                )
                self.update_yellowflag(yellow_flag, self.last_yellow_flag)
                self.last_yellow_flag = yellow_flag

            # Start lights
            if self.wcfg["show_startlights"]:
                if in_countdown:
                    self.last_lap_stime = lap_stime

                green = 1  # enable green flag
                start_timer = max(self.last_lap_stime - lap_etime,
                                  -self.wcfg["green_flag_duration"])
                if start_timer > 0:
                    green = 0  # enable red lights
                elif -start_timer == self.wcfg["green_flag_duration"]:
                    green = 2  # disable green flag
                self.update_startlights(start_timer, self.last_start_timer, green)
                self.last_start_timer = start_timer

            # Incoming traffic
            if self.wcfg["show_traffic"]:
                if in_pits != self.last_in_pits:
                    if not in_pits and self.last_in_pits:
                        self.traffic_timer_start = lap_etime

                if (self.traffic_timer_start and
                    self.wcfg["traffic_pitout_duration"]
                    < lap_etime - self.traffic_timer_start):
                    self.traffic_timer_start = 0

                traffic = (
                    minfo.vehicles.nearestTraffic,
                    bool(0 < minfo.vehicles.nearestTraffic
                         < self.wcfg["traffic_maximum_time_gap"]
                         and (in_pits or self.traffic_timer_start)))
                self.update_traffic(traffic, self.last_traffic)
                self.last_traffic = traffic

            # Pit request
            if self.wcfg["show_pit_request"]:
                pit_request = api.read.vehicle.pit_state()
                self.update_pit_request(pit_request, self.last_pit_request)
                self.last_pit_request = pit_request

            # Finish state
            if self.wcfg["show_finish_state"]:
                finish_state = api.read.vehicle.finish_state()
                self.update_finish_state(finish_state, self.last_finish_state)
                self.last_finish_state = finish_state

            # Reset
            if in_pits != self.last_in_pits:
                self.last_in_pits = in_pits

        else:
            if self.checked:
                self.set_defaults()

    # GUI update methods
    def update_pit_timer(self, curr, last, pitopen, highlight):
        """Pit timer"""
        if curr != last:  # timer
            if curr != -1:
                if highlight:
                    color = (f"color: {self.wcfg['font_color_pit_timer_stopped']};"
                             f"background: {self.wcfg['bkg_color_pit_timer_stopped']};")
                    state = "F " + f"{curr:.02f}"[:5].rjust(5)
                elif pitopen:
                    color = (f"color: {self.wcfg['font_color_pit_timer']};"
                                f"background: {self.wcfg['bkg_color_pit_timer']};")
                    state = "P " + f"{curr:.02f}"[:5].rjust(5)
                else:
                    color = (f"color: {self.wcfg['font_color_pit_closed']};"
                                f"background: {self.wcfg['bkg_color_pit_closed']};")
                    state = self.wcfg["pit_closed_text"]

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
            if curr[0]:
                if self.cfg.units["distance_unit"] == "Feet":
                    yelw_text = f"{curr[1] * 3.2808399:.0f}ft".rjust(6)
                else:  # meter
                    yelw_text = f"{curr[1]:.0f}m".rjust(6)

                self.bar_yellowflag.setText(f"Y{yelw_text}")
                self.bar_yellowflag.show()
            else:
                self.bar_yellowflag.hide()

    def update_startlights(self, curr, last, green=0):
        """Start lights"""
        if curr != last:
            if green == 0:
                self.bar_startlights.setText(
                    f"{self.wcfg['red_lights_text'][:6].ljust(6)}{api.read.session.start_lights()}")
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

    def update_traffic(self, curr, last):
        """Incoming traffic"""
        if curr != last:
            if curr[1]:
                self.bar_traffic.setText(f"≥{curr[0]:6.01f}")
                self.bar_traffic.show()
            else:
                self.bar_traffic.hide()

    def update_pit_request(self, curr, last):
        """Pit request"""
        if curr != last:
            if curr == 1:
                self.bar_pit_request.show()
            else:
                self.bar_pit_request.hide()

    def update_finish_state(self, curr, last):
        """Finish state"""
        if curr != last:
            if curr == 1:
                self.bar_finish_state.setText(self.wcfg["finish_text"])
                self.bar_finish_state.setStyleSheet(
                    f"color: {self.wcfg['font_color_finish']};"
                    f"background: {self.wcfg['bkg_color_finish']};")
                self.bar_finish_state.show()
            elif curr == 3:
                self.bar_finish_state.setText(self.wcfg["disqualify_text"])
                self.bar_finish_state.setStyleSheet(
                    f"color: {self.wcfg['font_color_disqualify']};"
                    f"background: {self.wcfg['bkg_color_disqualify']};")
                self.bar_finish_state.show()
            else:
                self.bar_finish_state.hide()
