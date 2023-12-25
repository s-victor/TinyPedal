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
Suspension position Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QColor

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "suspension_position"


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
        self.max_range = max(int(self.wcfg["position_max_range"]), 10)
        self.width_scale = self.bar_width / self.max_range

        # Config canvas
        self.resize(
            self.bar_width * 2 + self.bar_gap,
            self.bar_height * 2 + self.bar_gap
        )

        self.pen = QPen()
        self.pen.setColor(QColor(self.wcfg["font_color"]))

        # Last data
        self.pos_raw = [0] * 4
        self.last_pos_raw = [0] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Suspension position
            self.pos_raw = api.read.wheel.suspension_deflection()
            self.update_susp_pos(self.pos_raw, self.last_pos_raw)
            self.last_pos_raw = self.pos_raw

    # GUI update methods
    def update_susp_pos(self, curr, last):
        """Suspension position update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        #painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw suspension position
        self.draw_susp_pos(painter)

    def draw_susp_pos(self, painter):
        """Suspension position"""
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
        # Suspension position size
        pos_fl_abs = abs(self.pos_raw[0]) * self.width_scale
        susp_pos_fl = QRectF(
            self.bar_width - pos_fl_abs,
            0,
            pos_fl_abs,
            self.bar_height
        )
        susp_pos_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            abs(self.pos_raw[1]) * self.width_scale,
            self.bar_height
        )
        pos_rl_abs = abs(self.pos_raw[2]) * self.width_scale
        susp_pos_rl = QRectF(
            self.bar_width - pos_rl_abs,
            self.bar_height + self.bar_gap,
            pos_rl_abs,
            self.bar_height
        )
        susp_pos_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            abs(self.pos_raw[3]) * self.width_scale,
            self.bar_height
        )

        # Update background
        painter.setPen(Qt.NoPen)
        bkg_color = QColor(self.wcfg["bkg_color"])
        painter.fillRect(rect_bg_fl, bkg_color)
        painter.fillRect(rect_bg_fr, bkg_color)
        painter.fillRect(rect_bg_rl, bkg_color)
        painter.fillRect(rect_bg_rr, bkg_color)

        painter.fillRect(susp_pos_fl, QColor(self.color_pos(self.pos_raw[0])))
        painter.fillRect(susp_pos_fr, QColor(self.color_pos(self.pos_raw[1])))
        painter.fillRect(susp_pos_rl, QColor(self.color_pos(self.pos_raw[2])))
        painter.fillRect(susp_pos_rr, QColor(self.color_pos(self.pos_raw[3])))

        # Update text
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            rect_bg_fl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.pos_raw[0]:.0f}"
        )
        painter.drawText(
            rect_bg_fr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.pos_raw[1]:.0f}"
        )
        painter.drawText(
            rect_bg_rl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.pos_raw[2]:.0f}"
        )
        painter.drawText(
            rect_bg_rr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.pos_raw[3]:.0f}"
        )

    # Additional methods
    def color_pos(self, value):
        """Set suspension position color"""
        if value < 0:
            return self.wcfg["negative_position_color"]
        return self.wcfg["positive_position_color"]
