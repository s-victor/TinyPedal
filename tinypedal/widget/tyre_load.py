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
Tyre load Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QColor

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "tyre_load"


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
        self.padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.bar_gap = self.wcfg["bar_gap"]
        self.bar_width = max(self.wcfg["bar_width"], 20)
        self.bar_height = int(font_m.capital + pady * 2)
        self.width_scale = self.bar_width * 0.01

        # Config canvas
        self.resize(
            self.bar_width * 2 + self.bar_gap,
            self.bar_height * 2 + self.bar_gap
        )

        self.pen = QPen()
        self.pen.setColor(QColor(self.wcfg["font_color"]))

        # Config rect size
        self.rect_bg_fl = QRectF(
            0,
            0,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_rl = QRectF(
            0,
            self.bar_height + self.bar_gap,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            self.bar_width,
            self.bar_height
        )

        # Last data
        self.tload = [0] * 4
        self.tratio = [0] * 4
        self.last_tload = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Read tyre load data
            raw_load = api.read.tyre.load()
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

        self.draw_background(painter)

        self.draw_tyre_load(painter)

        self.draw_readings(painter)

    def draw_background(self, painter):
        """Draw background"""
        # Update background
        painter.setPen(Qt.NoPen)
        bkg_color = QColor(self.wcfg["bkg_color"])
        painter.fillRect(self.rect_bg_fl, bkg_color)
        painter.fillRect(self.rect_bg_fr, bkg_color)
        painter.fillRect(self.rect_bg_rl, bkg_color)
        painter.fillRect(self.rect_bg_rr, bkg_color)

    def draw_tyre_load(self, painter):
        """Draw tyre load"""
        # Tyre load size
        rect_load_fl = QRectF(
            self.bar_width - self.tratio[0] * self.width_scale,
            0,
            self.tratio[0] * self.width_scale,
            self.bar_height
        )
        rect_load_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            self.tratio[1] * self.width_scale,
            self.bar_height
        )
        rect_load_rl = QRectF(
            self.bar_width - self.tratio[2] * self.width_scale,
            self.bar_height + self.bar_gap,
            self.tratio[2] * self.width_scale,
            self.bar_height
        )
        rect_load_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            self.tratio[3] * self.width_scale,
            self.bar_height
        )

        hi_color = QColor(self.wcfg["highlight_color"])
        painter.fillRect(rect_load_fl, hi_color)
        painter.fillRect(rect_load_fr, hi_color)
        painter.fillRect(rect_load_rl, hi_color)
        painter.fillRect(rect_load_rr, hi_color)

    def draw_readings(self, painter):
        """Draw readings"""
        if self.wcfg["show_tyre_load_ratio"]:
            display_text = self.tratio
        else:
            display_text = self.tload

        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            self.rect_bg_fl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{display_text[0]:.0f}"
        )
        painter.drawText(
            self.rect_bg_fr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{display_text[1]:.0f}"
        )
        painter.drawText(
            self.rect_bg_rl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{display_text[2]:.0f}"
        )
        painter.drawText(
            self.rect_bg_rr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{display_text[3]:.0f}"
        )

    # Additional methods
    @staticmethod
    def tyre_load_ratio(value, total):
        """Tyre load ratio"""
        return round(calc.force_ratio(value, total), 2)
