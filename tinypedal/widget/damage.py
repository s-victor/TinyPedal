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
Damage Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPen, QBrush

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "damage"


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
        display_margin = max(int(self.wcfg["display_margin"]), 0)
        inner_gap = max(int(self.wcfg["inner_gap"]), 0)

        parts_max_width = max(int(self.wcfg["parts_max_width"]), 4)
        parts_max_height = max(int(self.wcfg["parts_max_height"]), parts_max_width)

        parts_full_width = parts_max_width * 3 + inner_gap * 2
        parts_full_height = parts_max_height * 3 + inner_gap * 2
        parts_width = max(min(
            int(self.wcfg["parts_width"]),
            parts_max_width * 0.5,
            parts_max_height * 0.5), 1)

        self.display_width = parts_full_width + display_margin * 2
        self.display_height = parts_full_height + display_margin * 2

        # Parts mask rect
        self.parts_mask = QRectF(
            display_margin + parts_width, display_margin + parts_width,
            parts_full_width - parts_width * 2, parts_full_height - parts_width * 2)

        # Wheel parts rect
        self.wheel_fl = QRectF(  # front left
            display_margin + parts_width + inner_gap,
            display_margin + parts_width + inner_gap,
            parts_width, parts_max_width)
        self.wheel_fr = QRectF(  # front right
            display_margin + parts_full_width - parts_width * 2 - inner_gap,
            display_margin + parts_width + inner_gap,
            parts_width, parts_max_width)
        self.wheel_rl = QRectF(  # rear left
            display_margin + parts_width + inner_gap,
            display_margin + parts_full_height - parts_width - parts_max_width - inner_gap,
            parts_width, parts_max_width)
        self.wheel_rr = QRectF(  # rear right
            display_margin + parts_full_width - parts_width * 2 - inner_gap,
            display_margin + parts_full_height - parts_width - parts_max_width - inner_gap,
            parts_width, parts_max_width)

        # Body parts rect
        self.part_fl = QRectF(  # front left
            display_margin, display_margin,
            parts_max_width, parts_max_height)
        self.part_fc = QRectF(  # front center
            display_margin + inner_gap + parts_max_width,
            display_margin,
            parts_max_width, parts_max_height)
        self.part_fr = QRectF(  # front right
            display_margin + (inner_gap + parts_max_width) * 2,
            display_margin,
            parts_max_width, parts_max_height)

        self.part_cl = QRectF(  # center left
            display_margin,
            display_margin + inner_gap + parts_max_height,
            parts_max_width, parts_max_height)
        self.part_cr = QRectF(  # center right
            display_margin + (inner_gap + parts_max_width) * 2,
            display_margin + inner_gap + parts_max_height,
            parts_max_width, parts_max_height)

        self.part_rl = QRectF(  # rear left
            display_margin,
            display_margin + (inner_gap + parts_max_height) * 2,
            parts_max_width, parts_max_height)
        self.part_rc = QRectF(  # rear center
            display_margin + inner_gap + parts_max_width,
            display_margin + (inner_gap + parts_max_height) * 2,
            parts_max_width, parts_max_height)
        self.part_rr = QRectF(  # rear right
            display_margin + (inner_gap + parts_max_width) * 2,
            display_margin + (inner_gap + parts_max_height) * 2,
            parts_max_width, parts_max_height)

        # Text rect
        self.rect_integrity = QRectF(0, font_offset, self.display_width, self.display_height)

        # Config canvas
        self.resize(self.display_width, self.display_height)

        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        # Last data
        self.damage_body = [0] * 8
        self.last_damage_body = None
        self.damage_wheel = [0] * 4
        self.last_damage_wheel = None

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Damage body
            self.damage_body = api.read.vehicle.damage_severity()
            self.update_damage(self.damage_body, self.last_damage_body)
            self.last_damage_body = self.damage_body

            # Damage wheel
            self.damage_wheel = api.read.wheel.is_detached()
            self.update_damage(self.damage_wheel, self.last_damage_wheel)
            self.last_damage_wheel = self.damage_wheel

    # GUI update methods
    def update_damage(self, curr, last):
        """Damage update"""
        if curr != last:
            self.update()

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)

        # Draw damage body
        self.draw_damage_body(painter)
        # Draw damage mask
        painter.setCompositionMode(QPainter.CompositionMode_DestinationOut)
        painter.fillRect(self.parts_mask, "#FFFFFF")
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        # Draw damage wheel
        self.draw_damage_wheel(painter)
        # Draw damage readings
        if self.wcfg["show_integrity_reading"]:
            if self.wcfg["show_inverted_integrity"]:
                damage_value = sum(self.damage_body) * 6.25
            else:
                damage_value = 100 - sum(self.damage_body) * 6.25
            self.draw_readings(painter, damage_value)
        # Draw background below mask
        if self.wcfg["show_background"]:
            painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
            self.draw_background(painter)

    def draw_background(self, painter):
        """Draw background"""
        painter.setPen(Qt.NoPen)
        painter.fillRect(
            0, 0, self.display_width, self.display_height, self.wcfg["bkg_color"]
        )

    def draw_damage_body(self, painter):
        """Draw damage body"""
        painter.setPen(Qt.NoPen)

        self.brush.setColor(self.color_damage_body(self.damage_body[1]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_fl)

        self.brush.setColor(self.color_damage_body(self.damage_body[0]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_fc)

        self.brush.setColor(self.color_damage_body(self.damage_body[7]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_fr)

        self.brush.setColor(self.color_damage_body(self.damage_body[2]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_cl)

        self.brush.setColor(self.color_damage_body(self.damage_body[6]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_cr)

        self.brush.setColor(self.color_damage_body(self.damage_body[3]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_rl)

        self.brush.setColor(self.color_damage_body(self.damage_body[4]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_rc)

        self.brush.setColor(self.color_damage_body(self.damage_body[5]))
        painter.setBrush(self.brush)
        painter.drawRect(self.part_rr)

    def draw_damage_wheel(self, painter):
        """Draw damage wheel"""
        painter.setPen(Qt.NoPen)

        self.brush.setColor(self.color_damage_wheel(self.damage_wheel[0]))
        painter.setBrush(self.brush)
        painter.drawRect(self.wheel_fl)

        self.brush.setColor(self.color_damage_wheel(self.damage_wheel[1]))
        painter.setBrush(self.brush)
        painter.drawRect(self.wheel_fr)

        self.brush.setColor(self.color_damage_wheel(self.damage_wheel[2]))
        painter.setBrush(self.brush)
        painter.drawRect(self.wheel_rl)

        self.brush.setColor(self.color_damage_wheel(self.damage_wheel[3]))
        painter.setBrush(self.brush)
        painter.drawRect(self.wheel_rr)

    def draw_readings(self, painter, value):
        """Draw body integrity readings"""
        self.pen.setColor(self.wcfg["font_color_integrity"])
        painter.setFont(self.font)
        painter.setPen(self.pen)
        painter.drawText(
            self.rect_integrity,
            Qt.AlignCenter,
            f"{value:.0f}%"[:4]
        )

    # Additional methods
    def color_damage_body(self, value):
        """Damage body color"""
        if value == 1:
            return self.wcfg["color_damage_light"]
        if value == 2:
            return self.wcfg["color_damage_heavy"]
        return self.wcfg["color_body"]

    def color_damage_wheel(self, value):
        """Damage wheel color"""
        if value:
            return self.wcfg["color_damage_detached"]
        return self.wcfg["color_wheel"]
