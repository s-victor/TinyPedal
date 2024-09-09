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
        self.last_pitting_state = 0, -1
        self.last_fuel_usage = None
        self.last_limiter_state = None
        self.blue_flag_timer_start = 0
        self.last_blue_state = -1, -1
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
            if curr[0] != -1:
                if curr[1]:  # finished pits
                    color = self.bar_style_pit_timer[1]
                    state = "F " + f"{min(curr[0], 999.99):.2f}"[:5].rjust(5)
                elif api.read.session.pit_open():
                    color = self.bar_style_pit_timer[0]
                    state = "P " + f"{min(curr[0], 999.99):.2f}"[:5].rjust(5)
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
            if curr[1]:
                self.bar_lowfuel.setText(curr[2] + f"{curr[0]:.2f}"[:4].rjust(5))
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
                self.bar_blueflag.setText(f"BLUE{min(curr[0], 999):3.0f}")
                self.bar_blueflag.show()
            else:
                self.bar_blueflag.hide()

    def update_yellowflag(self, curr, last):
        """Yellow flag"""
        if curr != last:
            if curr[1]:
                if self.cfg.units["distance_unit"] == "Feet":
                    yelw_text = f"{curr[0] * 3.2808399:.0f}ft".rjust(6)
                else:  # meter
                    yelw_text = f"{curr[0]:.0f}m".rjust(6)

                self.bar_yellowflag.setText(f"Y{yelw_text}")
                self.bar_yellowflag.show()
            else:
                self.bar_yellowflag.hide()

    def update_startlights(self, curr, last):
        """Start lights"""
        if curr != last:
            if curr[0] == 0:
                self.bar_startlights.setText(
                    f"{self.wcfg['red_lights_text'][:6].ljust(6)}{curr[1]}")
                self.bar_startlights.setStyleSheet(self.bar_style_startlights[0])
                self.bar_startlights.show()
            elif curr[0] == 1:
                self.bar_startlights.setText(self.wcfg["green_flag_text"])
                self.bar_startlights.setStyleSheet(self.bar_style_startlights[1])
                self.bar_startlights.show()
            else:
                self.bar_startlights.hide()

    def update_traffic(self, curr, last):
        """Incoming traffic"""
        if curr != last:
            if curr[1]:
                self.bar_traffic.setText(f"≥{curr[0]:6.1f}")
                self.bar_traffic.show()
            else:
                self.bar_traffic.hide()

    def update_pit_request(self, curr, last):
        """Pit request"""
        if curr != last:
            if curr[0] == 1:
                countdown = f"{curr[1]:.2f}"[:3].strip(".").ljust(3)
                est_laps = f"{curr[2]:.2f}"[:3].strip(".").rjust(3)
                self.bar_pit_request.setText(f"{countdown}≤{est_laps}")
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

        low_fuel = (
            amount_curr < self.wcfg["low_fuel_volume_threshold"] and
            est_laps < self.wcfg["low_fuel_lap_threshold"] and
            (not self.wcfg["show_low_fuel_for_race_only"] or
            self.wcfg["show_low_fuel_for_race_only"] and in_race))
        if not low_fuel:
            return 99999, low_fuel, prefix
        if prefix == "LF":
            return round(self.fuel_units(amount_curr), 2), low_fuel, prefix
        return round(amount_curr, 2), low_fuel, prefix

    def incoming_traffic(self, in_pits, lap_etime):
        """Check incoming traffic and time gap"""
        if self.last_in_pits > in_pits:
            self.pitout_timer_start = lap_etime

        if (self.pitout_timer_start and
            self.wcfg["traffic_pitout_duration"] < lap_etime - self.pitout_timer_start):
            self.pitout_timer_start = 0

        if self.wcfg["traffic_low_speed_threshold"]:
            is_low_speed = api.read.vehicle.speed() < self.wcfg["traffic_low_speed_threshold"]
        else:
            is_low_speed = False

        any_traffic = bool(
            0 < minfo.vehicles.nearestTraffic < self.wcfg["traffic_maximum_time_gap"]
            and (is_low_speed or in_pits or self.pitout_timer_start))

        if any_traffic:
            return round(minfo.vehicles.nearestTraffic, 1), any_traffic
        return 99999, any_traffic

    def pit_in_countdown(self):
        """Pit in countdown(laps)"""
        pit_state = api.read.vehicle.pit_state()
        if pit_state:
            if minfo.restapi.maxVirtualEnergy:
                est_laps = min(minfo.fuel.estimatedLaps, minfo.energy.estimatedLaps)
            else:
                est_laps = minfo.fuel.estimatedLaps
            cd_laps = calc.pit_in_countdown_laps(est_laps, api.read.lap.progress())
            return pit_state, round(cd_laps, 2), round(est_laps, 2)
        return pit_state, 99999, 99999

    def pit_timer_state(self, in_pits, lap_etime):
        """Pit timer state"""
        pit_timer = -1
        pit_timer_highlight = False

        if in_pits > self.last_in_pits:
            self.pit_timer_start = lap_etime

        if self.pit_timer_start:
            if in_pits:
                pit_timer = round(lap_etime - self.pit_timer_start, 2)
            elif (lap_etime - self.last_pitting_state[0] - self.pit_timer_start
                <= self.wcfg["pit_time_highlight_duration"]):
                pit_timer = self.last_pitting_state[0] + 0.000001
                pit_timer_highlight = True
            else:
                self.pit_timer_start = 0  # stop timer
        return pit_timer, pit_timer_highlight

    def green_flag_state(self, lap_etime):
        """Green flag state"""
        if api.read.session.in_countdown():
            self.last_lap_stime = api.read.timing.start()
            start_lights = api.read.session.start_lights()
        else:
            start_lights = 0

        start_timer = max(self.last_lap_stime - lap_etime, -self.wcfg["green_flag_duration"])
        if start_timer > 0:
            green = 0  # enable red lights
        elif -start_timer == self.wcfg["green_flag_duration"]:
            green = 2  # disable green flag
        else:
            green = 1  # enable green flag
        return green, start_lights

    def yellow_flag_state(self, in_race):
        """Yellow flag state"""
        hide_yellow = self.wcfg["show_yellow_flag_for_race_only"] and not in_race
        if not hide_yellow:
            any_yellow = (
                api.read.session.yellow_flag() and
                minfo.vehicles.nearestYellow < self.wcfg["yellow_flag_maximum_range"])
            if any_yellow:
                return round(minfo.vehicles.nearestYellow), any_yellow
        return 99999, False

    def blue_flag_state(self, in_race, lap_etime):
        """Blue flag state"""
        hide_blue = self.wcfg["show_blue_flag_for_race_only"] and not in_race
        if not hide_blue:
            any_blue = api.read.session.blue_flag()
            if any_blue:
                if self.last_blue_state[1] != any_blue:
                    self.blue_flag_timer_start = lap_etime
                return round(lap_etime - self.blue_flag_timer_start), any_blue
        return -1, False
