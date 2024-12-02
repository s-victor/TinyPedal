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
Pedal Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPen
from PySide2.QtWidgets import QWidget

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "pedal"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight"]
        )
        self.setFont(font)
        font_m = self.get_font_metrics(font)
        font_offset = self.calc_font_offset(font_m)

        # Throttle
        if self.wcfg["show_throttle"]:
            self.bar_throttle = PedalBar(
                config=self.wcfg,
                font_offset=font_offset,
                fg_color=self.wcfg["font_color_throttle"],
                bg_color=self.wcfg["bkg_color"],
                input_color=self.wcfg["throttle_color"],
            )
            self.set_primary_orient(
                target=self.bar_throttle,
                column=self.wcfg["column_index_throttle"],
                option="enable_horizontal_style",
                default=1,
            )

        # Brake
        if self.wcfg["show_brake"]:
            self.bar_brake = PedalBar(
                config=self.wcfg,
                font_offset=font_offset,
                fg_color=self.wcfg["font_color_brake"],
                bg_color=self.wcfg["bkg_color"],
                input_color=self.wcfg["brake_color"],
            )
            self.set_primary_orient(
                target=self.bar_brake,
                column=self.wcfg["column_index_brake"],
                option="enable_horizontal_style",
                default=1,
            )

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = PedalBar(
                config=self.wcfg,
                font_offset=font_offset,
                fg_color=self.wcfg["font_color_clutch"],
                bg_color=self.wcfg["bkg_color"],
                input_color=self.wcfg["clutch_color"],
            )
            self.set_primary_orient(
                target=self.bar_clutch,
                column=self.wcfg["column_index_clutch"],
                option="enable_horizontal_style",
                default=1,
            )

        # Force feedback
        if self.wcfg["show_ffb_meter"]:
            self.bar_ffb = PedalBar(
                config=self.wcfg,
                font_offset=font_offset,
                fg_color=self.wcfg["font_color_ffb"],
                bg_color=self.wcfg["bkg_color"],
                input_color=self.wcfg["ffb_color"],
                ffb_color=self.wcfg["ffb_clipping_color"],
            )
            self.set_primary_orient(
                target=self.bar_ffb,
                column=self.wcfg["column_index_ffb"],
                option="enable_horizontal_style",
                default=1,
            )

        # Last data
        self.checked = False
        self.max_brake_pres = 0.01

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Throttle
            if self.wcfg["show_throttle"]:
                raw_throttle = api.read.input.throttle_raw()
                if self.wcfg["show_throttle_filtered"]:
                    throttle = raw_throttle + api.read.input.throttle()
                else:
                    throttle = raw_throttle + raw_throttle
                self.update_pedal(self.bar_throttle, throttle, raw_throttle)

            # Brake
            if self.wcfg["show_brake"]:
                raw_brake = api.read.input.brake_raw()
                if self.wcfg["show_brake_filtered"]:
                    if self.wcfg["show_brake_pressure"]:
                        f_brake = self.filtered_brake_pressure(api.read.brake.pressure())
                    else:
                        f_brake = api.read.input.brake()
                    brake = raw_brake + f_brake
                else:
                    brake = raw_brake + raw_brake
                self.update_pedal(self.bar_brake, brake, raw_brake)

            # Clutch
            if self.wcfg["show_clutch"]:
                raw_clutch = api.read.input.clutch_raw()
                if self.wcfg["show_clutch_filtered"]:
                    clutch = raw_clutch + api.read.input.clutch()
                else:
                    clutch = raw_clutch + raw_clutch
                self.update_pedal(self.bar_clutch, clutch, raw_clutch)

            # Force feedback
            if self.wcfg["show_ffb_meter"]:
                ffb = abs(api.read.input.force_feedback())
                self.update_ffb(self.bar_ffb, ffb)

        else:
            if self.checked:
                self.checked = False
                self.max_brake_pres = 0.01

    # GUI update methods
    def update_pedal(self, target, data, raw):
        """Pedal update"""
        if target.last != data:
            target.last = data
            target.update_input(raw, data - raw)

    def update_ffb(self, target, data):
        """FFB update"""
        if target.last != data:
            target.last = data
            target.update_input(data, data)

    # Additional methods
    def filtered_brake_pressure(self, value):
        """Percentage filtered brake pressure"""
        brake_pres = sum(value)
        if brake_pres > self.max_brake_pres:
            self.max_brake_pres = brake_pres
        return brake_pres / self.max_brake_pres


class PedalBar(QWidget):
    """Pedal bar"""

    def __init__(
        self, config: dict, font_offset: int,
        fg_color: str, bg_color: str, input_color: str, ffb_color: str = ""):
        super().__init__()
        self.show_readings = config["show_readings"]
        self.is_maxed = False
        self.last = None

        # Config variable
        max_gap = max(config["inner_gap"], 0)
        self.pedal_length = max(int(config["bar_length"]), 10)
        self.pedal_extend = max(int(config["max_indicator_height"]), 0) + max_gap
        pedal_uwidth = max(int(config["bar_width_unfiltered"]), 1)
        pedal_fwidth = max(int(config["bar_width_filtered"]), 1)
        bar_length = self.pedal_length + self.pedal_extend
        bar_width = pedal_uwidth + pedal_fwidth
        readings_offset = bar_length * (config["readings_offset"] - 0.5)

        if config["enable_horizontal_style"]:
            self.update_input = self.__update_hori
            pedal_size = 0, 0, bar_length, bar_width
            raw_size = 0, 0, bar_length, pedal_uwidth
            filtered_size = 0, pedal_uwidth, bar_length, pedal_fwidth
            max_size = self.pedal_length + max_gap, 0, self.pedal_extend - max_gap, bar_width
            reading_size = readings_offset, font_offset, bar_length, bar_width
        else:
            self.update_input = self.__update_vert
            pedal_size = 0, 0, bar_width, bar_length
            raw_size = 0, 0, pedal_uwidth, bar_length
            filtered_size = pedal_uwidth, 0, pedal_fwidth, bar_length
            max_size = 0, 0, bar_width, self.pedal_extend - max_gap
            reading_size = 0, readings_offset + font_offset, bar_width, bar_length

        self.rect_pedal = QRectF(*pedal_size)
        self.rect_raw = QRectF(*raw_size)
        self.rect_filtered = QRectF(*filtered_size)
        self.rect_readings = QRectF(*reading_size)

        if ffb_color:
            self.rect_max = self.rect_pedal
            self.max_color = ffb_color
        else:
            self.rect_max = QRectF(*max_size)
            self.max_color = input_color

        self.input_reading = 0
        self.input_color = input_color
        self.bg_color = bg_color

        self.pen = QPen()
        self.pen.setColor(fg_color)
        self.setFixedSize(pedal_size[2], pedal_size[3])

    def __update_hori(self, input_raw: float, input_filtered: float):
        """Update input value - horizontal style"""
        self.input_reading = max(input_raw, input_filtered) * 100
        scaled_raw = self.__scale_hori(input_raw)
        scaled_filtered = self.__scale_hori(input_filtered)
        self.rect_raw.setRight(scaled_raw)
        self.rect_filtered.setRight(scaled_filtered)
        self.is_maxed = scaled_raw >= self.pedal_length
        self.update()

    def __update_vert(self, input_raw: float, input_filtered: float):
        """Update input value - vertical style"""
        self.input_reading = max(input_raw, input_filtered) * 100
        scaled_raw = self.__scale_vert(input_raw)
        scaled_filtered = self.__scale_vert(input_filtered)
        self.rect_raw.setTop(scaled_raw)
        self.rect_filtered.setTop(scaled_filtered)
        self.is_maxed = scaled_raw <= self.pedal_extend
        self.update()

    def __scale_hori(self, value: float) -> float:
        """Scale input - horizontal style"""
        return value * self.pedal_length

    def __scale_vert(self, value: float) -> float:
        """Scale input - vertical style"""
        return (1 - value) * self.pedal_length + self.pedal_extend

    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.fillRect(self.rect_pedal, self.bg_color)
        painter.fillRect(self.rect_raw, self.input_color)
        painter.fillRect(self.rect_filtered, self.input_color)
        if self.is_maxed:
            painter.fillRect(self.rect_max, self.max_color)

        if self.show_readings:
            painter.setPen(self.pen)
            painter.drawText(
                self.rect_readings,
                Qt.AlignCenter,
                f"{self.input_reading:.0f}"
            )
