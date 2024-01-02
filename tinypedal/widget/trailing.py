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
Trailing Widget
"""

from collections import deque
from PySide2.QtCore import Qt, Slot, QPointF
from PySide2.QtGui import QPainter, QPixmap, QPen

from ..api_control import api
from ._base import Overlay

WIDGET_NAME = "trailing"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config variable
        self.margin = max(int(self.wcfg["display_margin"]), 0)
        self.display_width = max(int(self.wcfg["display_width"]), 2)
        self.display_height = max(int(self.wcfg["display_height"]), 2)
        self.display_scale = max(self.wcfg["update_interval"] / 20 * self.wcfg["display_scale"], 1)

        if self.wcfg["show_vertical_style"]:
            self.max_samples = int(self.display_height / self.display_scale) + 2
            self.global_scale = self.display_width / 100
            self.pedal_max_range = self.display_width
            self.area_width = self.display_width + self.margin * 2
            self.area_height = self.display_height
        else:
            self.max_samples = int(self.display_width / self.display_scale) + 2
            self.global_scale = self.display_height / 100
            self.pedal_max_range = self.display_height
            self.area_width = self.display_width
            self.area_height = self.display_height + self.margin * 2

        # Config canvas
        self.resize(self.area_width, self.area_height)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.draw_background()

        # Last data
        self.delayed_update = False
        self.last_lap_etime = -1

        self.throttle = 0
        self.brake = 0
        self.clutch = 0
        self.ffb = 0
        self.data_throttle = self.create_data_samples(self.max_samples)
        self.data_brake = self.create_data_samples(self.max_samples)
        self.data_clutch = self.create_data_samples(self.max_samples)
        self.data_ffb = self.create_data_samples(self.max_samples)

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Use elapsed time to determine whether paused
            # add FFB value which has higher refresh rate
            lap_etime = api.read.timing.elapsed() + api.read.input.force_feedback()

            if lap_etime != self.last_lap_etime:
                if self.wcfg["show_throttle"]:
                    if self.wcfg["show_raw_throttle"]:
                        self.throttle = api.read.input.throttle_raw()
                    else:
                        self.throttle = api.read.input.throttle()
                    self.append_sample("throttle")

                if self.wcfg["show_brake"]:
                    if self.wcfg["show_raw_brake"]:
                        self.brake = api.read.input.brake_raw()
                    else:
                        self.brake = api.read.input.brake()
                    self.append_sample("brake")

                if self.wcfg["show_clutch"]:
                    if self.wcfg["show_raw_clutch"]:
                        self.clutch = api.read.input.clutch_raw()
                    else:
                        self.clutch = api.read.input.clutch()
                    self.append_sample("clutch")

                if self.wcfg["show_ffb"]:
                    self.ffb = abs(api.read.input.force_feedback())
                    self.append_sample("ffb")

                # Translate samples in single loop
                for index in range(self.max_samples):
                    if self.wcfg["show_throttle"]:
                        self.translate_samples(index, "throttle")
                    if self.wcfg["show_brake"]:
                        self.translate_samples(index, "brake")
                    if self.wcfg["show_clutch"]:
                        self.translate_samples(index, "clutch")
                    if self.wcfg["show_ffb"]:
                        self.translate_samples(index, "ffb")

                # Update after all pedal data set
                if self.delayed_update:
                    self.delayed_update = False
                    self.update()  # trigger paint event
                self.last_lap_etime = lap_etime

    # GUI update methods
    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw background
        painter.drawPixmap(
            0, 0, self.area_width, self.area_height, self.plot_background)

        if self.wcfg["show_ffb"]:
            self.draw_plot(painter, "ffb")
        if self.wcfg["show_clutch"]:
            self.draw_plot(painter, "clutch")
        if self.wcfg["show_brake"]:
            self.draw_plot(painter, "brake")
        if self.wcfg["show_throttle"]:
            self.draw_plot(painter, "throttle")

    def draw_background(self):
        """Draw background"""
        self.plot_background = QPixmap(self.area_width, self.area_height)
        self.plot_background.fill(self.wcfg["bkg_color"])
        painter = QPainter(self.plot_background)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw reference line
        if self.wcfg["show_reference_line"]:
            for idx in range(1, 6):
                self.draw_reference_line(
                    painter,
                    self.wcfg[f"reference_line_{idx}_style"],
                    self.wcfg[f"reference_line_{idx}_offset"],
                    self.wcfg[f"reference_line_{idx}_width"],
                    self.wcfg[f"reference_line_{idx}_color"]
                )

    def draw_reference_line(self, painter, style, offset, width, color):
        """Draw reference line"""
        if width:  # draw if line width > 0
            if style:
                self.pen.setStyle(Qt.DashLine)
            else:
                self.pen.setStyle(Qt.SolidLine)
            self.pen.setWidth(width)
            self.pen.setColor(color)
            painter.setPen(self.pen)
            painter.setBrush(Qt.NoBrush)
            if self.wcfg["show_vertical_style"]:
                painter.drawLine(
                    self.pedal_max_range * offset + self.margin,
                    0,
                    self.pedal_max_range * offset + self.margin,
                    self.display_height,
                )
            else:
                painter.drawLine(
                    0,
                    self.pedal_max_range * offset + self.margin,
                    self.display_width,
                    self.pedal_max_range * offset + self.margin,
                )

    def draw_plot(self, painter, suffix):
        """Draw plot"""
        if getattr(self, f"data_{suffix}"):
            self.pen.setWidth(self.wcfg[f"{suffix}_line_width"])
            self.pen.setColor(self.wcfg[f"{suffix}_color"])
            self.pen.setStyle(Qt.SolidLine)
            painter.setPen(self.pen)
            painter.setBrush(Qt.NoBrush)
            if self.wcfg[f"{suffix}_line_style"]:
                painter.drawPoints(getattr(self, f"data_{suffix}"))
            else:
                painter.drawPolyline(getattr(self, f"data_{suffix}"))

    # Additional methods
    def create_data_samples(self, samples):
        """Create data sample list"""
        return deque([QPointF(0, 0) for _ in range(samples)], self.max_samples)

    def scale_position(self, position):
        """Scale pedal value"""
        if self.wcfg["show_inverted_pedal"]:
            return position * 100 * self.global_scale + self.margin
        return (100 - position * 100) * self.global_scale + self.margin

    def append_sample(self, suffix):
        """Append new input sample to data list"""
        input_pos = self.scale_position(getattr(self, suffix))
        if self.wcfg["show_vertical_style"]:
            getattr(self, f"data_{suffix}").appendleft(QPointF(input_pos, 0))
        else:
            getattr(self, f"data_{suffix}").appendleft(QPointF(0, input_pos))
        self.delayed_update = True

    def translate_samples(self, index, suffix):
        """Translate sample position"""
        if self.wcfg["show_vertical_style"]:
            if self.wcfg["show_inverted_trailing"]:  # bottom alignment for display scale
                getattr(self, f"data_{suffix}")[index].setY(
                    self.display_height - index * self.display_scale)
            else:  # top alignment
                getattr(self, f"data_{suffix}")[index].setY(
                    index * self.display_scale + 1)
        else:  # right alignment for display scale
            if self.wcfg["show_inverted_trailing"]:
                getattr(self, f"data_{suffix}")[index].setX(
                    self.display_width - index * self.display_scale)
            else:  # left alignment
                getattr(self, f"data_{suffix}")[index].setX(
                    index * self.display_scale + 1)
