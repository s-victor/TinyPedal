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
Trailing Widget
"""

from PySide2.QtCore import Qt, QPointF, QRect
from PySide2.QtGui import QPainter, QPixmap, QPen

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "trailing"


class Realtime(Overlay):
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
        max_samples = 3 + max_line_width  # 3 offset + max line width
        self.samples_offset = max_samples - 2
        self.pedal_max_range = self.display_height
        self.area_width = self.display_width
        self.area_height = self.display_height + self.margin * 2
        self.draw_queue = self.config_draw_order()

        # Config canvas
        self.resize(self.area_width, self.area_height)
        self.rect_viewport = self.set_viewport_orientation()

        self.pixmap_background = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_section = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_last = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot_last.fill(Qt.transparent)

        if self.wcfg["show_throttle"]:
            self.data_throttle = self.create_data_samples(max_samples)
        if self.wcfg["show_brake"]:
            self.data_brake = self.create_data_samples(max_samples)
        if self.wcfg["show_clutch"]:
            self.data_clutch = self.create_data_samples(max_samples)
        if self.wcfg["show_ffb"]:
            self.data_ffb = self.create_data_samples(max_samples)
        if self.wcfg["show_wheel_lock"]:
            self.data_wheel_lock = self.create_data_samples(max_samples)
        if self.wcfg["show_wheel_slip"]:
            self.data_wheel_slip = self.create_data_samples(max_samples)

        self.pen = QPen()
        self.pen.setCapStyle(Qt.RoundCap)
        self.draw_background()
        self.draw_plot_section()
        self.draw_plot()

        # Last data
        self.delayed_update = False
        self.last_lap_etime = -1
        self.update_plot = 1

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Use elapsed time to determine whether data paused
            # Add 1 extra update compensation
            lap_etime = api.read.timing.elapsed()
            if lap_etime != self.last_lap_etime:
                self.update_plot = 2
            elif self.update_plot:
                self.update_plot -= 1
            self.last_lap_etime = lap_etime

            if self.update_plot:
                if self.wcfg["show_throttle"]:
                    if self.wcfg["show_raw_throttle"]:
                        throttle = api.read.input.throttle_raw()
                    else:
                        throttle = api.read.input.throttle()
                    self.update_sample(self.data_throttle, throttle)

                if self.wcfg["show_brake"]:
                    if self.wcfg["show_raw_brake"]:
                        brake = api.read.input.brake_raw()
                    else:
                        brake = api.read.input.brake()
                    self.update_sample(self.data_brake, brake)

                if self.wcfg["show_clutch"]:
                    if self.wcfg["show_raw_clutch"]:
                        clutch = api.read.input.clutch_raw()
                    else:
                        clutch = api.read.input.clutch()
                    self.update_sample(self.data_clutch, clutch)

                if self.wcfg["show_ffb"]:
                    ffb = abs(api.read.input.force_feedback())
                    self.update_sample(self.data_ffb, ffb)

                if self.wcfg["show_wheel_lock"]:
                    wheel_lock = min(abs(min(minfo.wheels.slipRatio)), 1)
                    if wheel_lock < self.wcfg["wheel_lock_threshold"] or api.read.input.brake_raw() <= 0.02:
                        wheel_lock = -999
                    self.update_sample(self.data_wheel_lock, wheel_lock)

                if self.wcfg["show_wheel_slip"]:
                    wheel_slip = min(max(minfo.wheels.slipRatio), 1)
                    if wheel_slip < self.wcfg["wheel_slip_threshold"] or api.read.input.throttle_raw() <= 0.02:
                        wheel_slip = -999
                    self.update_sample(self.data_wheel_slip, wheel_slip)

                # Update after all pedal data set
                if self.delayed_update:
                    self.delayed_update = False
                    self.draw_plot_section()
                    self.draw_plot()
                    self.pixmap_plot_last = self.pixmap_plot.copy(
                        0, 0, self.area_width, self.area_height)
                    self.update()  # trigger paint event

    # GUI update methods
    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setViewport(self.rect_viewport)
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
        # Draw section plot
        painter.drawPixmap(0, 0, self.pixmap_plot_section)
        # Avoid overlapping previous frame
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        # Draw last plot, +3 sample offset, -2 sample crop
        painter.drawPixmap(
            self.display_scale * 3, 0, self.pixmap_plot_last,
            self.display_scale * 2, 0, 0 ,0)

    def draw_plot_section(self):
        """Draw section plot"""
        self.pixmap_plot_section.fill(Qt.transparent)
        painter = QPainter(self.pixmap_plot_section)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setBrush(Qt.NoBrush)
        self.pen.setStyle(Qt.SolidLine)

        for plot_name in self.draw_queue:
            if self.wcfg[f"show_{plot_name}"]:
                self.draw_line(painter, plot_name)

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
    def create_data_samples(self, max_samples):
        """Create data sample list"""
        return tuple(QPointF(index * self.display_scale, 0)
                    for index in range(max_samples))

    def update_sample(self, dataset, value):
        """Update input position samples"""
        # Scale & set new input position
        dataset[0].setY(value * self.display_height + self.margin)
        # Move old input data (Y) 1 display unit to right
        for index in range(self.samples_offset, -1, -1):
            dataset[index + 1].setY(dataset[index].y())
        self.delayed_update = True

    def set_viewport_orientation(self):
        """Set viewport orientation"""
        if self.wcfg["show_inverted_pedal"]:
            y_pos = 0
            height = self.area_height
        else:
            y_pos = self.area_height
            height = -self.area_height
        if self.wcfg["show_inverted_trailing"]:  # right alignment
            x_pos = self.area_width
            width = -self.area_width
        else:
            x_pos = 0
            width = self.area_width
        return QRect(x_pos, y_pos, width, height)

    def config_draw_order(self):
        """Config plot draw order"""
        plot_list = (
            (self.wcfg["draw_order_index_throttle"], "throttle"),
            (self.wcfg["draw_order_index_brake"], "brake"),
            (self.wcfg["draw_order_index_clutch"], "clutch"),
            (self.wcfg["draw_order_index_ffb"], "ffb"),
            (self.wcfg["draw_order_index_wheel_lock"], "wheel_lock"),
            (self.wcfg["draw_order_index_wheel_slip"], "wheel_slip"),
        )
        return tuple(zip(*sorted(plot_list, reverse=True)))[1]
