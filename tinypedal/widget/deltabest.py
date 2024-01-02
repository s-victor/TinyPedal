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
Deltabest Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush, QColor

from .. import calculation as calc
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "deltabest"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        font_m = self.get_font_metrics(self.font)
        self.font_offset = self.calc_font_offset(font_m)

        # Config variable
        self.dbar_length = int(self.wcfg["bar_length"] / 2)
        self.dbar_height = int(self.wcfg["bar_height"])
        self.bar_gap = self.wcfg["bar_gap"]
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.delta_width = font_m.width * 7 + padx * 2
        self.delta_height = int(font_m.capital + pady * 2)

        # Config canvas
        if self.wcfg["show_delta_bar"]:
            self.resize(self.dbar_length * 2,
                        self.dbar_height + self.bar_gap + self.delta_height)
        else:
            self.resize(self.delta_width, self.delta_height)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        # Last data
        self.delta_best = 0
        self.last_delta_best = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Deltabest
            self.delta_best = calc.sym_range(
                minfo.delta.deltaBest,
                self.wcfg["delta_display_range"])
            self.update_deltabest(self.delta_best, self.last_delta_best)
            self.last_delta_best = self.delta_best

    # GUI update methods
    def update_deltabest(self, curr, last):
        """Deltabest"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing, True)

        delta_pos = self.deltabar_pos(
            self.wcfg["bar_display_range"],
            self.delta_best,
            self.dbar_length)

        if self.wcfg["show_delta_bar"]:
            self.draw_deltabar(painter, delta_pos)

        self.draw_readings(painter, delta_pos)

    def draw_deltabar(self, painter, delta_pos):
        """Draw deltabar"""
        painter.setPen(Qt.NoPen)

        if self.delta_best > 0:
            pos_x = delta_pos
            size = self.dbar_length - delta_pos
        else:
            pos_x = self.dbar_length
            size = delta_pos - self.dbar_length

        if self.wcfg["layout"] == 0:
            pos_y = 0
        else:
            pos_y = self.delta_height + self.bar_gap

        rect_deltabar = QRectF(0, pos_y, self.dbar_length * 2, self.dbar_height)
        self.brush.setColor(QColor(self.wcfg["bkg_color_deltabar"]))
        painter.setBrush(self.brush)
        painter.drawRect(rect_deltabar)

        rect_deltapos = QRectF(pos_x, pos_y, size, self.dbar_height)
        self.brush.setColor(QColor(self.color_delta(self.delta_best)))
        painter.setBrush(self.brush)
        painter.drawRect(rect_deltapos)

    def draw_readings(self, painter, delta_pos):
        """Draw readings"""
        if self.wcfg["swap_style"]:
            self.pen.setColor(QColor(self.wcfg["bkg_color_deltabest"]))
            self.brush.setColor(QColor(self.color_delta(self.delta_best)))
        else:
            self.pen.setColor(QColor(self.color_delta(self.delta_best)))
            self.brush.setColor(QColor(self.wcfg["bkg_color_deltabest"]))

        if self.wcfg["layout"] == 0 and self.wcfg["show_delta_bar"]:
            pos_y = self.dbar_height + self.bar_gap
        else:
            pos_y = 0

        if self.wcfg["show_delta_bar"] and self.wcfg["show_animated_deltabest"]:
            pos_x = min(max(delta_pos - self.delta_width / 2, 0),
                        self.dbar_length * 2 - self.delta_width)
        elif self.wcfg["show_delta_bar"]:
            pos_x = self.dbar_length - self.delta_width / 2
        else:
            pos_x = 0

        painter.setPen(Qt.NoPen)
        rect = QRectF(pos_x, pos_y, self.delta_width, self.delta_height)
        painter.setBrush(self.brush)
        painter.drawRect(rect)

        painter.setFont(self.font)
        painter.setPen(self.pen)
        painter.drawText(
            rect.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{self.delta_best:+.03f}"[:7]
        )

    # Additional methods
    @staticmethod
    def deltabar_pos(rng, delta, length):
        """Delta position"""
        return (rng - calc.sym_range(delta, rng)) * length / rng

    def color_delta(self, delta):
        """Delta time color"""
        if delta <= 0:
            return self.wcfg["bkg_color_time_gain"]
        return self.wcfg["bkg_color_time_loss"]
