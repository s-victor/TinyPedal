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
Session Widget
"""

import time
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "session"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

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

        column_sesn = self.wcfg["column_index_session_name"]
        column_sysc = self.wcfg["column_index_system_clock"]
        column_sest = self.wcfg["column_index_session_time"]
        column_lapn = self.wcfg["column_index_lapnumber"]
        column_plac = self.wcfg["column_index_position"]

        # Session name
        if self.wcfg["show_session_name"]:
            self.bar_session_name = QLabel("NAME")
            self.bar_session_name.setAlignment(Qt.AlignCenter)
            self.bar_session_name.setStyleSheet(
                f"color: {self.wcfg['font_color_session_name']};"
                f"background: {self.wcfg['bkg_color_session_name']};"
            )

        # System clock
        if self.wcfg["show_system_clock"]:
            self.bar_system_clock = QLabel("S CLOCK")
            self.bar_system_clock.setAlignment(Qt.AlignCenter)
            self.bar_system_clock.setStyleSheet(
                f"color: {self.wcfg['font_color_system_clock']};"
                f"background: {self.wcfg['bkg_color_system_clock']};"
            )

        # Session time
        if self.wcfg["show_session_time"]:
            self.bar_session_time = QLabel("SESSION")
            self.bar_session_time.setAlignment(Qt.AlignCenter)
            self.bar_session_time.setStyleSheet(
                f"color: {self.wcfg['font_color_session_time']};"
                f"background: {self.wcfg['bkg_color_session_time']};"
            )

        # Lap number
        if self.wcfg["show_lapnumber"]:
            self.bar_lapnumber = QLabel("LAPS")
            self.bar_lapnumber.setAlignment(Qt.AlignCenter)
            self.bar_lapnumber.setStyleSheet(
                f"color: {self.wcfg['font_color_lapnumber']};"
                f"background: {self.wcfg['bkg_color_lapnumber']};"
            )

        # Driver place & total vehicles
        if self.wcfg["show_position"]:
            self.bar_position = QLabel("PLACE")
            self.bar_position.setAlignment(Qt.AlignCenter)
            self.bar_position.setStyleSheet(
                f"color: {self.wcfg['font_color_position']};"
                f"background: {self.wcfg['bkg_color_position']};"
            )

        # Set layout
        if self.wcfg["show_session_name"]:
            layout.addWidget(self.bar_session_name, 0, column_sesn)
        if self.wcfg["show_system_clock"]:
            layout.addWidget(self.bar_system_clock, 0, column_sysc)
        if self.wcfg["show_session_time"]:
            layout.addWidget(self.bar_session_time, 0, column_sest)
        if self.wcfg["show_lapnumber"]:
            layout.addWidget(self.bar_lapnumber, 0, column_lapn)
        if self.wcfg["show_position"]:
            layout.addWidget(self.bar_position, 0, column_plac)
        self.setLayout(layout)

        # Last data
        self.last_session_name = None
        self.last_system_time = None
        self.last_session_time = None
        self.last_lap_into = None
        self.last_place = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Session name
            if self.wcfg["show_session_name"]:
                session_name = self.set_session_name(api.read.session.session_type())
                self.update_session_name(session_name, self.last_session_name)
                self.last_session_name = session_name

            # System Clock
            if self.wcfg["show_system_clock"]:
                system_time = time.strftime(self.wcfg["system_clock_format"])
                self.update_system_clock(system_time, self.last_system_time)
                self.last_system_time = system_time

            # Session time
            if self.wcfg["show_session_time"]:
                session_time = api.read.session.remaining()
                self.update_session_time(session_time, self.last_session_time)
                self.last_session_time = session_time

            # Lap number
            if self.wcfg["show_lapnumber"]:
                lap_into = api.read.lap.percent() * 100
                lap_num = api.read.lap.number()
                lap_max = api.read.lap.maximum()
                self.update_lapnumber(lap_into, self.last_lap_into, lap_num, lap_max)
                self.last_lap_into = lap_into

            # Driver place & total vehicles
            if self.wcfg["show_position"]:
                place = (api.read.vehicle.place(), api.read.vehicle.total_vehicles())
                self.update_position(place, self.last_place)
                self.last_place = place

    # GUI update methods
    def update_session_name(self, curr, last):
        """Session name"""
        if curr != last:
            self.bar_session_name.setText(curr)

    def update_system_clock(self, curr, last):
        """System Clock"""
        if curr != last:
            self.bar_system_clock.setText(f"{curr}")

    def update_session_time(self, curr, last):
        """Session time"""
        if curr != last:
            self.bar_session_time.setText(calc.sec2sessiontime(max(curr, 0)))

    def update_lapnumber(self, curr, last, lap_num, lap_max):
        """Lap number"""
        if curr != last:
            lap_text = "-" if lap_max > 100000 else lap_max

            self.bar_lapnumber.setText(
                f"{self.wcfg['prefix_lap_number']}{lap_num}.{curr:02.0f}/{lap_text}"
            )
            self.bar_lapnumber.setStyleSheet(
                f"color: {self.wcfg['font_color_lapnumber']};"
                f"background: {self.maxlap_warning(lap_num - lap_max)};"
            )

    def update_position(self, curr, last):
        """Driver place & total vehicles"""
        if curr != last:
            self.bar_position.setText(
                f"{self.wcfg['prefix_position']}{curr[0]:02.0f}/{curr[1]:02.0f}")

    # Additional methods
    def maxlap_warning(self, lap_diff):
        """Max lap warning"""
        if lap_diff >= -1:
            return self.wcfg["bkg_color_maxlap_warn"]
        return self.wcfg["bkg_color_lapnumber"]

    def set_session_name(self, session_id):
        """Set session name"""
        if session_id == 1:
            return self.wcfg["session_text_practice"]
        if session_id == 2:
            return self.wcfg["session_text_qualify"]
        if session_id == 3:
            return self.wcfg["session_text_warmup"]
        if session_id == 4:
            return self.wcfg["session_text_race"]
        return self.wcfg["session_text_testday"]
