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
        self.display_scale = max(int(
            self.wcfg["update_interval"] / 20 * self.wcfg["display_scale"]), 1)

        max_line_width = int(max(
            1,
            self.wcfg["throttle_line_width"],
            self.wcfg["brake_line_width"],
            self.wcfg["clutch_line_width"],
            self.wcfg["ffb_line_width"],
        ))
        self.max_samples = 3 + max_line_width  # 3 offset + max line width
        self.pedal_scale = self.display_height / 100
        self.pedal_max_range = self.display_height
        self.area_width = self.display_width
        self.area_height = self.display_height + self.margin * 2

        # Config canvas
        self.resize(self.area_width, self.area_height)
        self.pixmap_background = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_section = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_last = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_last.fill(Qt.transparent)

        self.data_throttle = self.create_data_samples(self.max_samples)
        self.data_brake = self.create_data_samples(self.max_samples)
        self.data_clutch = self.create_data_samples(self.max_samples)
        self.data_ffb = self.create_data_samples(self.max_samples)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.draw_background()
        self.draw_plot_section()
        self.draw_plot()

        # Last data
        self.delayed_update = False
        self.last_lap_etime = -1

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
                        throttle = api.read.input.throttle_raw()
                    else:
                        throttle = api.read.input.throttle()
                    self.append_sample("throttle", throttle)

                if self.wcfg["show_brake"]:
                    if self.wcfg["show_raw_brake"]:
                        brake = api.read.input.brake_raw()
                    else:
                        brake = api.read.input.brake()
                    self.append_sample("brake", brake)

                if self.wcfg["show_clutch"]:
                    if self.wcfg["show_raw_clutch"]:
                        clutch = api.read.input.clutch_raw()
                    else:
                        clutch = api.read.input.clutch()
                    self.append_sample("clutch", clutch)

                if self.wcfg["show_ffb"]:
                    ffb = abs(api.read.input.force_feedback())
                    self.append_sample("ffb", ffb)

                # Update after all pedal data set
                if self.delayed_update:
                    self.delayed_update = False
                    self.translate_samples()
                    self.draw_plot_section()
                    self.draw_plot()
                    self.pixmap_plot_last = self.pixmap_plot.copy(
                        0, 0, self.area_width, self.area_height)
                    self.update()  # trigger paint event
                self.last_lap_etime = lap_etime

    # GUI update methods
    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        if self.wcfg["show_inverted_trailing"]:  # right alignment
            painter.setViewport(self.area_width, 0, -self.area_width, self.area_height)
        painter.drawPixmap(0, 0, self.pixmap_background)
        painter.drawPixmap(0, 0, self.pixmap_plot)

    def draw_background(self):
        """Draw background"""
        self.pixmap_background.fill(self.wcfg["bkg_color"])
        painter = QPainter(self.pixmap_background)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(Qt.NoBrush)

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
        if width > 0:
            if style:
                self.pen.setStyle(Qt.DashLine)
            else:
                self.pen.setStyle(Qt.SolidLine)
            self.pen.setWidth(width)
            self.pen.setColor(color)
            painter.setPen(self.pen)
            painter.drawLine(
                0,
                self.pedal_max_range * offset + self.margin,
                self.display_width,
                self.pedal_max_range * offset + self.margin,
            )

    def draw_plot(self):
        """Draw final plot"""
        self.pixmap_plot.fill(Qt.transparent)
        painter = QPainter(self.pixmap_plot)
        # Draw section plot, -2 sample offset
        painter.drawPixmap(-self.display_scale * 2, 0, self.pixmap_plot_section)
        # Avoid overlapping previous frame
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        # Draw last plot, +1 sample offset
        painter.drawPixmap(self.display_scale, 0, self.pixmap_plot_last)

    def draw_plot_section(self):
        """Draw section plot"""
        self.pixmap_plot_section.fill(Qt.transparent)
        painter = QPainter(self.pixmap_plot_section)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(Qt.NoBrush)
        self.pen.setStyle(Qt.SolidLine)

        if self.wcfg["show_ffb"]:
            self.draw_line(painter, "ffb")
        if self.wcfg["show_clutch"]:
            self.draw_line(painter, "clutch")
        if self.wcfg["show_brake"]:
            self.draw_line(painter, "brake")
        if self.wcfg["show_throttle"]:
            self.draw_line(painter, "throttle")

    def draw_line(self, painter, suffix):
        """Draw plot line"""
        self.pen.setWidth(self.wcfg[f"{suffix}_line_width"])
        self.pen.setColor(self.wcfg[f"{suffix}_color"])
        painter.setPen(self.pen)
        if self.wcfg[f"{suffix}_line_style"]:
            painter.drawPoints(getattr(self, f"data_{suffix}"))
        else:
            painter.drawPolyline(getattr(self, f"data_{suffix}"))

    # Additional methods
    @staticmethod
    def create_data_samples(samples):
        """Create data sample list"""
        return deque([QPointF(0, 0) for _ in range(samples)], samples)

    def scale_position(self, position):
        """Scale pedal value"""
        if self.wcfg["show_inverted_pedal"]:
            return position * 100 * self.pedal_scale + self.margin
        return (100 - position * 100) * self.pedal_scale + self.margin

    def append_sample(self, suffix, value):
        """Append input position sample to data list"""
        input_pos = self.scale_position(value)
        getattr(self, f"data_{suffix}").appendleft(QPointF(0, input_pos))
        self.delayed_update = True

    def translate_samples(self):
        """Translate sample position"""
        for index in range(self.max_samples):
            index_offset = index * self.display_scale + 1
            if self.wcfg["show_throttle"]:
                self.data_throttle[index].setX(index_offset)
            if self.wcfg["show_brake"]:
                self.data_brake[index].setX(index_offset)
            if self.wcfg["show_clutch"]:
                self.data_clutch[index].setX(index_offset)
            if self.wcfg["show_ffb"]:
                self.data_ffb[index].setX(index_offset)
