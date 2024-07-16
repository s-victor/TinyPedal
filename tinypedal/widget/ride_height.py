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
Ride height Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPen

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "ride_height"


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
        font_offset = self.calc_font_offset(font_m)

        # Config variable
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = max(self.wcfg["bar_width"], 20)
        self.bar_height = int(font_m.capital + pady * 2)
        self.max_range = max(int(self.wcfg["ride_height_max_range"]), 10)
        self.width_scale = self.bar_width / self.max_range
        self.ride_height_offset = (
            self.wcfg["ride_height_offset_front_left"],
            self.wcfg["ride_height_offset_front_right"],
            self.wcfg["ride_height_offset_rear_left"],
            self.wcfg["ride_height_offset_rear_right"]
        )

        self.rect_bg_fl = QRectF(
            0,
            0,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_fr = QRectF(
            self.bar_width + bar_gap,
            0,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_rl = QRectF(
            0,
            self.bar_height + bar_gap,
            self.bar_width,
            self.bar_height
        )
        self.rect_bg_rr = QRectF(
            self.bar_width + bar_gap,
            self.bar_height + bar_gap,
            self.bar_width,
            self.bar_height
        )

        self.rect_rideh_fl = self.rect_bg_fl.adjusted(0,0,0,0)
        self.rect_rideh_fr = self.rect_bg_fr.adjusted(0,0,0,0)
        self.rect_rideh_rl = self.rect_bg_rl.adjusted(0,0,0,0)
        self.rect_rideh_rr = self.rect_bg_rr.adjusted(0,0,0,0)

        self.rect_text_bg_fl = self.rect_bg_fl.adjusted(padx, font_offset, 0, 0)
        self.rect_text_bg_fr = self.rect_bg_fr.adjusted(0, font_offset, -padx, 0)
        self.rect_text_bg_rl = self.rect_bg_rl.adjusted(padx, font_offset, 0, 0)
        self.rect_text_bg_rr = self.rect_bg_rr.adjusted(0, font_offset, -padx, 0)

        # Config canvas
        self.resize(
            self.bar_width * 2 + bar_gap,
            self.bar_height * 2 + bar_gap
        )

        self.pen = QPen()
        self.pen.setColor(self.wcfg["font_color"])

        # Last data
        self.ride_height = [0] * 4
        self.last_ride_height = [0] * 4

        # Set widget state & start update
        self.set_widget_state()

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:

            # Read ride height & rake data
            self.ride_height = api.read.wheel.ride_height()
            self.update_rideh(self.ride_height, self.last_ride_height)
            self.last_ride_height = self.ride_height

    # GUI update methods
    def update_rideh(self, curr, last):
        """Ride height update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        self.draw_background(painter)
        self.draw_ride_height(painter)
        self.draw_readings(painter)

    def draw_background(self, painter):
        """Draw background"""
        painter.setPen(Qt.NoPen)
        painter.fillRect(
            self.rect_bg_fl,
            self.color_rideh(self.ride_height[0], self.ride_height_offset[0])
        )
        painter.fillRect(
            self.rect_bg_fr,
            self.color_rideh(self.ride_height[1], self.ride_height_offset[1])
        )
        painter.fillRect(
            self.rect_bg_rl,
            self.color_rideh(self.ride_height[2], self.ride_height_offset[2])
        )
        painter.fillRect(
            self.rect_bg_rr,
            self.color_rideh(self.ride_height[3], self.ride_height_offset[3])
        )

    def draw_ride_height(self, painter):
        """Draw ride height"""
        self.rect_rideh_fl.setX(self.bar_width - max(self.ride_height[0], 0) * self.width_scale)
        self.rect_rideh_fr.setWidth(max(self.ride_height[1], 0) * self.width_scale)
        self.rect_rideh_rl.setX(self.bar_width - max(self.ride_height[2], 0) * self.width_scale)
        self.rect_rideh_rr.setWidth(max(self.ride_height[3], 0) * self.width_scale)

        hi_color = self.wcfg["highlight_color"]
        painter.fillRect(self.rect_rideh_fl, hi_color)
        painter.fillRect(self.rect_rideh_fr, hi_color)
        painter.fillRect(self.rect_rideh_rl, hi_color)
        painter.fillRect(self.rect_rideh_rr, hi_color)

    def draw_readings(self, painter):
        """Draw readings"""
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            self.rect_text_bg_fl,
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.ride_height[0]:.0f}"
        )
        painter.drawText(
            self.rect_text_bg_fr,
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.ride_height[1]:.0f}"
        )
        painter.drawText(
            self.rect_text_bg_rl,
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.ride_height[2]:.0f}"
        )
        painter.drawText(
            self.rect_text_bg_rr,
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.ride_height[3]:.0f}"
        )

    # Additional methods
    def color_rideh(self, value, offset):
        """Ride height indicator color"""
        if value > offset:
            return self.wcfg["bkg_color"]
        return self.wcfg["warning_color_bottoming"]
