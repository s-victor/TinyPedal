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
Session Widget
"""

from time import strftime

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "session"


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
        self.session_name_list = (
            self.wcfg["session_text_testday"],
            self.wcfg["session_text_practice"],
            self.wcfg["session_text_qualify"],
            self.wcfg["session_text_warmup"],
            self.wcfg["session_text_race"],
        )

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

        # Session name
        if self.wcfg["show_session_name"]:
            text_session_name = self.session_name_list[0]
            bar_style_session_name = self.set_qss(
                fg_color=self.wcfg["font_color_session_name"],
                bg_color=self.wcfg["bkg_color_session_name"]
            )
            self.bar_session_name = self.set_qlabel(
                text=text_session_name,
                style=bar_style_session_name,
                width=font_m.width * max(len(name) for name in self.session_name_list) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_session_name,
                column=self.wcfg["column_index_session_name"],
            )

        # System clock
        if self.wcfg["show_system_clock"]:
            text_system_clock = strftime(self.wcfg["system_clock_format"])
            bar_style_system_clock = self.set_qss(
                fg_color=self.wcfg["font_color_system_clock"],
                bg_color=self.wcfg["bkg_color_system_clock"]
            )
            self.bar_system_clock = self.set_qlabel(
                text=text_system_clock,
                style=bar_style_system_clock,
                width=font_m.width * len(text_system_clock) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_system_clock,
                column=self.wcfg["column_index_system_clock"],
            )

        # Session time
        if self.wcfg["show_session_time"]:
            text_session_time = calc.sec2sessiontime(0)
            bar_style_session_time = self.set_qss(
                fg_color=self.wcfg["font_color_session_time"],
                bg_color=self.wcfg["bkg_color_session_time"]
            )
            self.bar_session_time = self.set_qlabel(
                text=text_session_time,
                style=bar_style_session_time,
                width=font_m.width * len(text_session_time) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_session_time,
                column=self.wcfg["column_index_session_time"],
            )

        # Last data
        self.last_session_name = None
        self.last_system_time = None
        self.last_session_time = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Session name
            if self.wcfg["show_session_name"]:
                session_name = self.session_name_list[api.read.session.session_type()]
                self.update_session_name(session_name, self.last_session_name)
                self.last_session_name = session_name

            # System Clock
            if self.wcfg["show_system_clock"]:
                system_time = strftime(self.wcfg["system_clock_format"])
                self.update_system_clock(system_time, self.last_system_time)
                self.last_system_time = system_time

            # Session time
            if self.wcfg["show_session_time"]:
                session_time = api.read.session.remaining()
                self.update_session_time(session_time, self.last_session_time)
                self.last_session_time = session_time

    # GUI update methods
    def update_session_name(self, curr, last):
        """Session name"""
        if curr != last:
            self.bar_session_name.setText(curr)

    def update_system_clock(self, curr, last):
        """System Clock"""
        if curr != last:
            self.bar_system_clock.setText(curr)

    def update_session_time(self, curr, last):
        """Session time"""
        if curr != last:
            if curr < 0:
                curr = 0
            self.bar_session_time.setText(calc.sec2sessiontime(curr))
