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

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "flag"
MAGIC_NUM = 99999


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
        bar_width = font_m.width * 7 + bar_padx

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

        # Pit status
        if self.wcfg["show_pit_timer"]:
            self.bar_style_pit_timer = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_pit_timer"],
                    bg_color=self.wcfg["bkg_color_pit_timer"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_pit_timer_stopped"],
                    bg_color=self.wcfg["bkg_color_pit_timer_stopped"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_pit_closed"],
                    bg_color=self.wcfg["bkg_color_pit_closed"])
            )
            self.bar_pit_timer = self.set_qlabel(
                text="PITST0P",
                style=self.bar_style_pit_timer[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_pit_timer,
                column=self.wcfg["column_index_pit_timer"],
            )

        # Low fuel warning
        if self.wcfg["show_low_fuel"]:
            bar_style_lowfuel = self.set_qss(
                fg_color=self.wcfg["font_color_low_fuel"],
                bg_color=self.wcfg["bkg_color_low_fuel"]
            )
            self.bar_lowfuel = self.set_qlabel(
                text="LOWFUEL",
                style=bar_style_lowfuel,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_lowfuel,
                column=self.wcfg["column_index_low_fuel"],
            )

        # Speed limiter
        if self.wcfg["show_speed_limiter"]:
            bar_style_limiter = self.set_qss(
                fg_color=self.wcfg["font_color_speed_limiter"],
                bg_color=self.wcfg["bkg_color_speed_limiter"]
            )
            self.bar_limiter = self.set_qlabel(
                text=self.wcfg["speed_limiter_text"],
                style=bar_style_limiter,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_limiter,
                column=self.wcfg["column_index_speed_limiter"],
            )

        # Yellow flag
        if self.wcfg["show_yellow_flag"]:
            bar_style_yellowflag = self.set_qss(
                fg_color=self.wcfg["font_color_yellow_flag"],
                bg_color=self.wcfg["bkg_color_yellow_flag"]
            )
            self.bar_yellowflag = self.set_qlabel(
                text="YELLOW",
                style=bar_style_yellowflag,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_yellowflag,
                column=self.wcfg["column_index_yellow_flag"],
            )

        # Blue flag
        if self.wcfg["show_blue_flag"]:
            bar_style_blueflag = self.set_qss(
                fg_color=self.wcfg["font_color_blue_flag"],
                bg_color=self.wcfg["bkg_color_blue_flag"]
            )
            self.bar_blueflag = self.set_qlabel(
                text="BLUE",
                style=bar_style_blueflag,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_blueflag,
                column=self.wcfg["column_index_blue_flag"],
            )

        # Start lights
        if self.wcfg["show_startlights"]:
            self.bar_style_startlights = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_startlights"],
                    bg_color=self.wcfg["bkg_color_red_lights"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_startlights"],
                    bg_color=self.wcfg["bkg_color_green_flag"])
            )
            self.bar_startlights = self.set_qlabel(
                text="SLIGHTS",
                style=self.bar_style_startlights[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_startlights,
                column=self.wcfg["column_index_startlights"],
            )

        # Incoming traffic
        if self.wcfg["show_traffic"]:
            bar_style_traffic = self.set_qss(
                fg_color=self.wcfg["font_color_traffic"],
                bg_color=self.wcfg["bkg_color_traffic"]
            )
            self.bar_traffic = self.set_qlabel(
                text="TRAFFIC",
                style=bar_style_traffic,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_traffic,
                column=self.wcfg["column_index_traffic"],
            )

        # Pit request
        if self.wcfg["show_pit_request"]:
            bar_style_pit_request = self.set_qss(
                fg_color=self.wcfg["font_color_pit_request"],
                bg_color=self.wcfg["bkg_color_pit_request"]
            )
            self.bar_pit_request = self.set_qlabel(
                text="PIT REQ",
                style=bar_style_pit_request,
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_pit_request,
                column=self.wcfg["column_index_pit_request"],
            )

        # Finish state
        if self.wcfg["show_finish_state"]:
            self.bar_style_finish_state = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_finish"],
                    bg_color=self.wcfg["bkg_color_finish"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_disqualify"],
                    bg_color=self.wcfg["bkg_color_disqualify"])
            )
            self.bar_finish_state = self.set_qlabel(
                text="FINISH",
                style=self.bar_style_finish_state[0],
                width=bar_width,
            )
            self.set_primary_orient(
                target=self.bar_finish_state,
                column=self.wcfg["column_index_finish_state"],
            )

        # Last data
        self.set_defaults()

    def set_defaults(self):
        """Initialize variables"""
        self.checked = False
        self.last_in_pits = 0
        self.pit_timer_start = 0
        self.last_pit_time = 0
        self.last_pitting_state = None
        self.last_fuel_usage = None
        self.last_limiter_state = None
        self.blue_flag_timer_start = 0
        self.last_blue_state = None
        self.last_yellow_state = None
        self.last_green_state = None
        self.last_lap_stime = 0
        self.last_traffic = None
        self.pitout_timer_start = 0
        self.last_pit_request = None
        self.last_finish_state = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read state data
            lap_etime = api.read.timing.elapsed()
            in_pits = api.read.vehicle.in_pits()
            in_race = api.read.session.in_race()

            # Pit timer
            if self.wcfg["show_pit_timer"]:
                pitting_state = self.pit_timer_state(in_pits, lap_etime)
                self.update_pit_timer(pitting_state, self.last_pitting_state)
                self.last_pitting_state = pitting_state

            # Low fuel update
            if self.wcfg["show_low_fuel"]:
                fuel_usage = self.is_lowfuel(in_race)
                self.update_lowfuel(fuel_usage, self.last_fuel_usage)
                self.last_fuel_usage = fuel_usage

            # Pit limiter
            if self.wcfg["show_speed_limiter"]:
                limiter_state = api.read.switch.speed_limiter()
                self.update_limiter(limiter_state, self.last_limiter_state)
                self.last_limiter_state = limiter_state

            # Blue flag
            if self.wcfg["show_blue_flag"]:
                blue_state = self.blue_flag_state(in_race, lap_etime)
                self.update_blueflag(blue_state, self.last_blue_state)
                self.last_blue_state = blue_state

            # Yellow flag
            if self.wcfg["show_yellow_flag"]:
                yellow_state = self.yellow_flag_state(in_race)
                self.update_yellowflag(yellow_state, self.last_yellow_state)
                self.last_yellow_state = yellow_state

            # Start lights
            if self.wcfg["show_startlights"]:
                green_state = self.green_flag_state(lap_etime)
                self.update_startlights(green_state, self.last_green_state)
                self.last_green_state = green_state

            # Incoming traffic
            if self.wcfg["show_traffic"]:
                traffic = self.incoming_traffic(in_pits, lap_etime)
                self.update_traffic(traffic, self.last_traffic)
                self.last_traffic = traffic

            # Pit request
            if self.wcfg["show_pit_request"]:
                pit_request = self.pit_in_countdown()
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
    def update_pit_timer(self, curr, last):
        """Pit timer"""
        if curr != last:  # timer
            if curr != MAGIC_NUM:
                if curr < 0:  # finished pits
                    color = self.bar_style_pit_timer[1]
                    state = f"F{-curr: >6.2f}"[:7]
                elif api.read.session.pit_open():
                    color = self.bar_style_pit_timer[0]
                    state = f"P{curr: >6.2f}"[:7]
                else:  # pit closed
                    color = self.bar_style_pit_timer[2]
                    state = self.wcfg["pit_closed_text"]

                self.bar_pit_timer.setText(state)
                self.bar_pit_timer.setStyleSheet(color)
                self.bar_pit_timer.show()
            else:
                self.bar_pit_timer.hide()

    def update_lowfuel(self, curr, last):
        """Low fuel warning"""
        if curr != last:
            if curr != "":
                self.bar_lowfuel.setText(curr)
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
            if curr != MAGIC_NUM:
                self.bar_blueflag.setText(f"BLUE{curr:3.0f}"[:7])
                self.bar_blueflag.show()
            else:
                self.bar_blueflag.hide()

    def update_yellowflag(self, curr, last):
        """Yellow flag"""
        if curr != last:
            if curr != MAGIC_NUM:
                if self.cfg.units["distance_unit"] == "Feet":
                    yelw_text = f"Y{curr * 3.281: >4.0f}ft"[:7]
                else:  # meter
                    yelw_text = f"Y{curr: >5.0f}m"[:7]

                self.bar_yellowflag.setText(yelw_text)
                self.bar_yellowflag.show()
            else:
                self.bar_yellowflag.hide()

    def update_startlights(self, curr, last):
        """Start lights"""
        if curr != last:
            if curr > 0:
                self.bar_startlights.setText(
                    f"{self.wcfg['red_lights_text'][:6]: <6}{curr}")
                self.bar_startlights.setStyleSheet(self.bar_style_startlights[0])
                self.bar_startlights.show()
            elif curr == 0:
                self.bar_startlights.setText(self.wcfg["green_flag_text"])
                self.bar_startlights.setStyleSheet(self.bar_style_startlights[1])
                self.bar_startlights.show()
            else:
                self.bar_startlights.hide()

    def update_traffic(self, curr, last):
        """Incoming traffic"""
        if curr != last:
            if curr != MAGIC_NUM:
                self.bar_traffic.setText(f"≥{curr: >6.1f}"[:7])
                self.bar_traffic.show()
            else:
                self.bar_traffic.hide()

    def update_pit_request(self, curr, last):
        """Pit request"""
        if curr != last:
            if curr != "":
                self.bar_pit_request.setText(curr)
                self.bar_pit_request.show()
            else:
                self.bar_pit_request.hide()

    def update_finish_state(self, curr, last):
        """Finish state"""
        if curr != last:
            if curr == 1:
                self.bar_finish_state.setText(self.wcfg["finish_text"])
                self.bar_finish_state.setStyleSheet(self.bar_style_finish_state[0])
                self.bar_finish_state.show()
            elif curr == 3:
                self.bar_finish_state.setText(self.wcfg["disqualify_text"])
                self.bar_finish_state.setStyleSheet(self.bar_style_finish_state[1])
                self.bar_finish_state.show()
            else:
                self.bar_finish_state.hide()

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def is_lowfuel(self, in_race):
        """Is low fuel"""
        if minfo.restapi.maxVirtualEnergy and minfo.energy.estimatedLaps < minfo.fuel.estimatedLaps:
            prefix = "LE"
            amount_curr = minfo.energy.amountCurrent
            est_laps = minfo.energy.estimatedLaps
        else:
            prefix = "LF"
            amount_curr = minfo.fuel.amountCurrent
            est_laps = minfo.fuel.estimatedLaps

        if not (  # low fuel
            amount_curr < self.wcfg["low_fuel_volume_threshold"] and
            est_laps < self.wcfg["low_fuel_lap_threshold"] and
            (not self.wcfg["show_low_fuel_for_race_only"] or
            self.wcfg["show_low_fuel_for_race_only"] and in_race)):
            return ""

        if prefix == "LF":
            return f"{prefix}{self.fuel_units(amount_curr): >5.2f}"[:7]
        return f"{prefix}{amount_curr: >5.2f}"[:7]

    def incoming_traffic(self, in_pits, lap_etime):
        """Check incoming traffic and time gap"""
        if self.last_in_pits > in_pits:
            self.pitout_timer_start = lap_etime

        if (self.pitout_timer_start and
            self.wcfg["traffic_pitout_duration"] < lap_etime - self.pitout_timer_start):
            self.pitout_timer_start = 0

        is_low_speed = (
            self.wcfg["traffic_low_speed_threshold"] > 0 and
            api.read.vehicle.speed() < self.wcfg["traffic_low_speed_threshold"]
        )
        if (0 < minfo.vehicles.nearestTraffic < self.wcfg["traffic_maximum_time_gap"] and
            (is_low_speed or in_pits or self.pitout_timer_start)):
            return round(minfo.vehicles.nearestTraffic, 1)
        return MAGIC_NUM

    def pit_in_countdown(self):
        """Pit in countdown (laps)"""
        if api.read.vehicle.pit_state() != 1:
            return ""

        if minfo.restapi.maxVirtualEnergy:
            est_laps = min(minfo.fuel.estimatedLaps, minfo.energy.estimatedLaps)
        else:
            est_laps = minfo.fuel.estimatedLaps
        cd_laps = calc.pit_in_countdown_laps(est_laps, api.read.lap.progress())

        cd_laps = f"{cd_laps:.2f}"[:3].strip(".")
        est_laps = f"{est_laps:.2f}"[:3].strip(".")
        return f"{cd_laps: <3}≤{est_laps: >3}"

    def pit_timer_state(self, in_pits, lap_etime):
        """Pit timer state"""
        pit_timer = MAGIC_NUM

        if in_pits > self.last_in_pits:
            self.pit_timer_start = lap_etime

        if self.pit_timer_start:
            if in_pits:
                pit_timer = round(lap_etime - self.pit_timer_start, 2)
                self.last_pit_time = pit_timer
            elif (lap_etime - self.last_pit_time - self.pit_timer_start
                <= self.wcfg["pit_time_highlight_duration"]):
                pit_timer = -self.last_pit_time  # set negative for highlighting
            else:
                self.pit_timer_start = 0  # stop timer
        return pit_timer

    def green_flag_state(self, lap_etime):
        """Green flag state"""
        if api.read.session.in_countdown():
            self.last_lap_stime = api.read.timing.start()
            start_lights = api.read.session.start_lights()
        else:
            start_lights = 0

        start_timer = lap_etime - self.last_lap_stime
        if start_timer < 0:
            green = start_lights  # enable red lights
        elif 0 <= start_timer <= self.wcfg["green_flag_duration"]:
            green = 0  # enable green flag
        else:
            green = -1  # disable green flag
        return green

    def yellow_flag_state(self, in_race):
        """Yellow flag state"""
        if in_race or not self.wcfg["show_yellow_flag_for_race_only"]:
            if (api.read.session.yellow_flag() and
                abs(minfo.vehicles.nearestYellow) < self.wcfg["yellow_flag_maximum_range"]):
                return round(abs(minfo.vehicles.nearestYellow))
        return MAGIC_NUM

    def blue_flag_state(self, in_race, lap_etime):
        """Blue flag state"""
        if in_race or not self.wcfg["show_blue_flag_for_race_only"]:
            if api.read.session.blue_flag():
                if self.last_blue_state == MAGIC_NUM:
                    self.blue_flag_timer_start = lap_etime
                return round(lap_etime - self.blue_flag_timer_start)
        return MAGIC_NUM
