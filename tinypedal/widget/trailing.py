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
        self.display_height = max(int(self.wcfg["display_height"]), 2)
        self.area_width = max(int(self.wcfg["display_width"]), 2)
        self.area_height = self.display_height + self.margin * 2
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

        # Config canvas
        self.resize(self.area_width, self.area_height)
        self.rect_viewport = self.set_viewport_orientation()

        self.pixmap_background = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot = QPixmap(self.area_width, self.area_height)
        self.pixmap_plot.fill(Qt.transparent)
        self.pixmap_plot_section = QPixmap(self.display_scale * 3, self.area_height)
        self.pixmap_plot_section.fill(Qt.transparent)

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

        self.draw_queue = self.config_draw_order()
        self.draw_background()

        # Last data
        self.last_lap_etime = -1
        self.update_plot = 1

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Use elapsed time to determine whether data paused
            # Add 1 extra update compensation
            lap_etime = api.read.timing.elapsed()
            if self.last_lap_etime != lap_etime:
                self.last_lap_etime = lap_etime
                self.update_plot = 2
            elif self.update_plot > 0:
                self.update_plot -= 1

            if self.update_plot:
                throttle_raw = api.read.input.throttle_raw()
                brake_raw = api.read.input.brake_raw()

                if self.wcfg["show_throttle"]:
                    if self.wcfg["show_raw_throttle"]:
                        throttle = throttle_raw
                    else:
                        throttle = api.read.input.throttle()
                    self.update_sample(self.data_throttle, throttle)

                if self.wcfg["show_brake"]:
                    if self.wcfg["show_raw_brake"]:
                        brake = brake_raw
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
                    if wheel_lock < self.wcfg["wheel_lock_threshold"] or brake_raw <= 0.02:
                        wheel_lock = -999
                    self.update_sample(self.data_wheel_lock, wheel_lock)

                if self.wcfg["show_wheel_slip"]:
                    wheel_slip = min(max(minfo.wheels.slipRatio), 1)
                    if wheel_slip < self.wcfg["wheel_slip_threshold"] or throttle_raw <= 0.02:
                        wheel_slip = -999
                    self.update_sample(self.data_wheel_slip, wheel_slip)

                # Update after all pedal data set
                self.draw_plot_section()
                self.draw_plot()
                self.update()  # trigger paint event

    # GUI update methods
    def paintEvent(self, event):
        """Draw"""
        painter = QPainter(self)
        painter.setViewport(self.rect_viewport)
        painter.drawPixmap(0, 0, self.pixmap_plot)
        # Draw background below plot
        painter.setCompositionMode(QPainter.CompositionMode_DestinationOver)
        painter.drawPixmap(0, 0, self.pixmap_background)

    def draw_background(self):
        """Draw background"""
        self.pixmap_background.fill(self.wcfg["bkg_color"])
        painter = QPainter(self.pixmap_background)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Draw reference line
        if self.wcfg["show_reference_line"]:
            pen = QPen()
            for idx in range(1, 6):
                self.draw_reference_line(
                    painter, pen,
                    self.wcfg[f"reference_line_{idx}_style"],
                    self.wcfg[f"reference_line_{idx}_offset"],
                    self.wcfg[f"reference_line_{idx}_width"],
                    self.wcfg[f"reference_line_{idx}_color"]
                )

    def draw_reference_line(self, painter, pen, style, offset, width, color):
        """Draw reference line"""
        if width > 0:
            pen.setStyle(Qt.DashLine if style else Qt.SolidLine)
            pen.setWidth(width)
            pen.setColor(color)
            painter.setPen(pen)
            pos_offset = self.display_height * offset + self.margin
            painter.drawLine(0, pos_offset, self.area_width, pos_offset)

    def draw_plot(self):
        """Draw final plot"""
        painter = QPainter(self.pixmap_plot)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        # Draw last plot, +3 sample offset, -2 sample crop
        painter.drawPixmap(
            self.display_scale * 3, 0, self.pixmap_plot,
            self.display_scale * 2, 0, 0 ,0)
        # Draw section plot
        painter.drawPixmap(0, 0, self.pixmap_plot_section)

    def draw_plot_section(self):
        """Draw section plot"""
        self.pixmap_plot_section.fill(Qt.transparent)
        painter = QPainter(self.pixmap_plot_section)
        painter.setRenderHint(QPainter.Antialiasing, True)
        for _, data, pen, line_style in self.draw_queue:
            painter.setPen(pen)
            if line_style:
                painter.drawPoints(data)
            else:
                painter.drawPolyline(data)

    # Additional methods
    def create_data_samples(self, max_samples):
        """Create data sample list"""
        return tuple(QPointF(index * self.display_scale, 0) for index in range(max_samples))

    def update_sample(self, dataset, value):
        """Update input position samples"""
        # Scale & set new input position
        dataset[0].setY(value * self.display_height + self.margin)
        # Move old input data (Y) 1 display unit to right
        for index in range(self.samples_offset, -1, -1):
            dataset[index + 1].setY(dataset[index].y())

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
        plot_names = ("throttle", "brake", "clutch", "ffb", "wheel_lock", "wheel_slip")
        plot_list = []
        for plot_name in plot_names:
            if not self.wcfg[f"show_{plot_name}"]:
                continue
            pen = QPen()
            pen.setCapStyle(Qt.RoundCap)
            pen.setWidth(self.wcfg[f"{plot_name}_line_width"])
            pen.setColor(self.wcfg[f"{plot_name}_color"])
            plot_list.append(
                (
                    self.wcfg[f"draw_order_index_{plot_name}"],  # index
                    getattr(self, f"data_{plot_name}"),  # data
                    pen,  # pen style
                    self.wcfg[f"{plot_name}_line_style"],  # line style
                )
            )
        plot_list.sort(reverse=True)
        return plot_list
