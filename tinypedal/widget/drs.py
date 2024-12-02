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
DRS Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "drs"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        self.setFont(font)
        font_m = self.get_font_metrics(font)
        font_offset = self.calc_font_offset(font_m)

        # Config variable
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.drs_width = font_m.width * len(self.wcfg["drs_text"]) + padx * 2
        self.drs_height = int(font_m.capital + pady * 2)
        self.drs_color = (
            (self.wcfg["font_color_not_available"], self.wcfg["bkg_color_not_available"]),
            (self.wcfg["font_color_available"], self.wcfg["bkg_color_available"]),
            (self.wcfg["font_color_allowed"], self.wcfg["bkg_color_allowed"]),
            (self.wcfg["font_color_activated"], self.wcfg["bkg_color_activated"]),
        )

        # Config canvas
        self.resize(self.drs_width, self.drs_height)

        self.pen = QPen()
        self.pen.setColor(self.drs_color[0][0])
        self.brush = QBrush(Qt.SolidPattern)
        self.brush.setColor(self.drs_color[0][1])

        # Config rect size
        self.rect_drs = QRectF(0, 0, self.drs_width, self.drs_height)
        self.rect_text_drs = self.rect_drs.adjusted(0, font_offset, 0, 0)

        # Last data
        self.last_drs_state = None

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # DRS update
            drs_state = api.read.switch.drs_status()
            self.update_drs(drs_state, self.last_drs_state)
            self.last_drs_state = drs_state

    # GUI update methods
    def update_drs(self, curr, last):
        """DRS update"""
        if curr != last:
            self.pen.setColor(self.drs_color[curr][0])
            self.brush.setColor(self.drs_color[curr][1])
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)

        # Draw background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        painter.drawRect(self.rect_drs)

        # Draw DRS text
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_text_drs,
            Qt.AlignCenter,
            self.wcfg["drs_text"]
        )
