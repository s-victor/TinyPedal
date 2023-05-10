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
Tyre load Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush, QColor, QFont, QFontMetrics

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget

WIDGET_NAME = "tyre_load"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        self.font.setWeight(getattr(QFont, self.wcfg['font_weight'].capitalize()))

        font_w = QFontMetrics(self.font).averageCharWidth()
        font_h = QFontMetrics(self.font).height()
        font_l = QFontMetrics(self.font).leading()
        font_c = QFontMetrics(self.font).capHeight()
        font_d = QFontMetrics(self.font).descent()

        # Config variable
        self.padx = round(font_w * self.wcfg["bar_padding_horizontal"])
        pady = round(font_c * self.wcfg["bar_padding_vertical"])

        if not self.wcfg["font_offset_vertical"]:
            self.font_offset = font_c + font_d * 2 + font_l * 2 - font_h
        else:
            self.font_offset = self.wcfg["font_offset_vertical"]

        self.bar_gap = self.wcfg["bar_gap"]
        self.bar_width = max(self.wcfg["bar_width"], 20)
        self.bar_height = int(font_c + pady * 2)

        # Config canvas
        self.resize(
            self.bar_width * 2 + self.bar_gap,
            self.bar_height * 2 + self.bar_gap
        )

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        # Last data
        self.tload = [0] * 4
        self.tratio = [0] * 4
        self.last_tload = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read tyre load data
            raw_load = read_data.tyre_load()
            self.tload = tuple(map(round, raw_load))
            self.tratio = tuple(map(self.tyre_load_ratio, raw_load, [sum(raw_load)] * 4))

            self.update_tyre_load(self.tload, self.last_tload)
            self.last_tload = self.tload

    # GUI update methods
    def update_tyre_load(self, curr, last):
        """Tyre load update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw tyre load
        self.draw_tyre_load(painter)

    def draw_tyre_load(self, painter):
        """Tyre load"""
        # Background size
        rect_bg_fl = QRectF(
            0,
            0,
            self.bar_width,
            self.bar_height
        )
        rect_bg_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            self.bar_width,
            self.bar_height
        )
        rect_bg_rl = QRectF(
            0,
            self.bar_height + self.bar_gap,
            self.bar_width,
            self.bar_height
        )
        rect_bg_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            self.bar_width,
            self.bar_height
        )
        # Tyre load size
        rect_load_fl = QRectF(
            self.bar_width - self.tratio[0] * self.bar_width * 0.01,
            0,
            self.tratio[0] * self.bar_width * 0.01,
            self.bar_height
        )
        rect_load_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            self.tratio[1] * self.bar_width * 0.01,
            self.bar_height
        )
        rect_load_rl = QRectF(
            self.bar_width - self.tratio[2] * self.bar_width * 0.01,
            self.bar_height + self.bar_gap,
            self.tratio[2] * self.bar_width * 0.01,
            self.bar_height
        )
        rect_load_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            self.tratio[3] * self.bar_width * 0.01,
            self.bar_height
        )

        # Update background
        self.brush.setColor(QColor(self.wcfg["bkg_color"]))
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        painter.drawRect(rect_bg_fl)
        painter.drawRect(rect_bg_fr)
        painter.drawRect(rect_bg_rl)
        painter.drawRect(rect_bg_rr)

        self.brush.setColor(QColor(self.wcfg["highlight_color"]))
        painter.setBrush(self.brush)
        painter.drawRect(rect_load_fl)
        painter.drawRect(rect_load_fr)
        painter.drawRect(rect_load_rl)
        painter.drawRect(rect_load_rr)

        # Update text
        if self.wcfg["show_tyre_load_ratio"]:
            display_text = self.tratio
        else:
            display_text = self.tload

        self.pen.setColor(QColor(self.wcfg["font_color"]))
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            rect_bg_fl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{display_text[0]:.0f}"
        )
        painter.drawText(
            rect_bg_fr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{display_text[1]:.0f}"
        )
        painter.drawText(
            rect_bg_rl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{display_text[2]:.0f}"
        )
        painter.drawText(
            rect_bg_rr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{display_text[3]:.0f}"
        )

    # Additional methods
    @staticmethod
    def tyre_load_ratio(value, total):
        """Tyre load ratio"""
        return round(calc.force_ratio(value, total), 2)
