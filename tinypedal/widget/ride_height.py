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
Ride height Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QColor

from ..api_control import api
from ..base import Widget

WIDGET_NAME = "ride_height"


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
        self.padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.bar_gap = self.wcfg["bar_gap"]
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

        # Config canvas
        self.resize(
            self.bar_width * 2 + self.bar_gap,
            self.bar_height * 2 + self.bar_gap
        )

        self.pen = QPen()
        self.pen.setColor(QColor(self.wcfg["font_color"]))

        # Last data
        self.ride_height = [0] * 4
        self.last_ride_height = [0] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

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
        #painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw ride height
        self.draw_ride_height(painter)

    def draw_ride_height(self, painter):
        """Ride height"""
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
        # Ride height size
        rideh_fl_min = max(self.ride_height[0], 0) * self.width_scale
        rect_rideh_fl = QRectF(
            self.bar_width - rideh_fl_min,
            0,
            rideh_fl_min,
            self.bar_height
        )
        rect_rideh_fr = QRectF(
            self.bar_width + self.bar_gap,
            0,
            max(self.ride_height[1], 0) * self.width_scale,
            self.bar_height
        )
        rideh_rl_min = max(self.ride_height[2], 0) * self.width_scale
        rect_rideh_rl = QRectF(
            self.bar_width - rideh_rl_min,
            self.bar_height + self.bar_gap,
            rideh_rl_min,
            self.bar_height
        )
        rect_rideh_rr = QRectF(
            self.bar_width + self.bar_gap,
            self.bar_height + self.bar_gap,
            max(self.ride_height[3], 0) * self.width_scale,
            self.bar_height
        )

        # Update background
        painter.setPen(Qt.NoPen)
        painter.fillRect(
            rect_bg_fl,
            QColor(self.color_rideh(self.ride_height[0], self.ride_height_offset[0]))
        )
        painter.fillRect(
            rect_bg_fr,
            QColor(self.color_rideh(self.ride_height[1], self.ride_height_offset[1]))
        )
        painter.fillRect(
            rect_bg_rl,
            QColor(self.color_rideh(self.ride_height[2], self.ride_height_offset[2]))
        )
        painter.fillRect(
            rect_bg_rr,
            QColor(self.color_rideh(self.ride_height[3], self.ride_height_offset[3]))
        )

        hi_color = QColor(self.wcfg["highlight_color"])
        painter.fillRect(rect_rideh_fl, hi_color)
        painter.fillRect(rect_rideh_fr, hi_color)
        painter.fillRect(rect_rideh_rl, hi_color)
        painter.fillRect(rect_rideh_rr, hi_color)

        # Update text
        painter.setPen(self.pen)
        painter.setFont(self.font)
        painter.drawText(
            rect_bg_fl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.ride_height[0]:.0f}"
        )
        painter.drawText(
            rect_bg_fr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.ride_height[1]:.0f}"
        )
        painter.drawText(
            rect_bg_rl.adjusted(self.padx, self.font_offset, 0, 0),
            Qt.AlignLeft | Qt.AlignVCenter,
            f"{self.ride_height[2]:.0f}"
        )
        painter.drawText(
            rect_bg_rr.adjusted(0, self.font_offset, -self.padx, 0),
            Qt.AlignRight | Qt.AlignVCenter,
            f"{self.ride_height[3]:.0f}"
        )

    # Additional methods
    def color_rideh(self, value, offset):
        """Ride height indicator color"""
        if value > offset:
            return self.wcfg["bkg_color"]
        return self.wcfg["warning_color_bottoming"]
