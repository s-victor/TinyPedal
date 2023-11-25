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
DRS Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush, QColor

from ..api_control import api
from ..base import Widget

WIDGET_NAME = "drs"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        font_m = self.get_font_metrics(self.font)
        self.font_offset = self.calc_font_offset(font_m)

        # Config variable
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.drs_width = font_m.width * 3 + padx * 2
        self.drs_height = int(font_m.capital + pady * 2)

        # Config canvas
        self.resize(self.drs_width, self.drs_height)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        # Last data
        self.drs_state = (0, 0)
        self.last_drs_state = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # DRS update
            self.drs_state = (api.read.switch.drs(),
                              api.read.switch.drs_status())
            self.update_drs(self.drs_state, self.last_drs_state)
            self.last_drs_state = self.drs_state

    # GUI update methods
    def update_drs(self, curr, last):
        """DRS update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw DRS
        self.draw_drs(painter)

    def draw_drs(self, painter):
        """DRS"""
        fg_color, bg_color = self.color_drs(self.drs_state)
        self.brush.setColor(QColor(bg_color))
        self.pen.setColor(QColor(fg_color))

        # Set gauge size
        rect_drs = QRectF(0, 0, self.drs_width, self.drs_height)

        # Update DRS background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        painter.drawRect(rect_drs)

        # Update DRS text
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            rect_drs.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            "DRS"
        )

    # Additional methods
    def color_drs(self, drs_state):
        """DRS state color"""
        if drs_state[1] == 1:  # blue
            color = (self.wcfg["font_color_available"],
                     self.wcfg["bkg_color_available"])
        elif drs_state[1] == 2:
            if drs_state[0]:  # green
                color = (self.wcfg["font_color_activated"],
                         self.wcfg["bkg_color_activated"])
            else:  # orange
                color = (self.wcfg["font_color_allowed"],
                         self.wcfg["bkg_color_allowed"])
        else:  # grey
            color = (self.wcfg["font_color_not_available"],
                     self.wcfg["bkg_color_not_available"])
        return color
