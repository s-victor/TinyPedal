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
Gear Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPixmap, QPen, QBrush, QColor, QFont, QFontMetrics
from PySide2.QtWidgets import (
    QLabel,
    QGridLayout,
)

from .. import calculation as calc
from ..api_control import api
from ..base import Widget
from ..module_info import minfo

WIDGET_NAME = "gear"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])

        font_w = QFontMetrics(self.font).averageCharWidth()
        font_h = QFontMetrics(self.font).height()
        font_l = QFontMetrics(self.font).leading()
        font_c = QFontMetrics(self.font).capHeight()
        font_d = QFontMetrics(self.font).descent()

        self.font_gear = self.font
        self.font_gear.setWeight(getattr(QFont, self.wcfg['font_weight_gear'].capitalize()))

        font_scale_speed = self.wcfg["font_scale_speed"] if self.wcfg["show_speed_below_gear"] else 1
        self.font_speed = QFont()
        self.font_speed.setFamily(self.wcfg['font_name'])
        self.font_speed.setWeight(getattr(QFont, self.wcfg['font_weight_speed'].capitalize()))
        self.font_speed.setPixelSize(round(self.wcfg['font_size'] * font_scale_speed))

        # Config variable
        bar_gap = self.wcfg["bar_gap"]
        self.inner_gap = self.wcfg["inner_gap"]
        padx = round(font_w * self.wcfg["bar_padding_horizontal"])
        pady = round(font_c * self.wcfg["bar_padding_vertical"])

        if self.wcfg["enable_auto_font_offset"]:
            self.font_offset = font_c + font_d * 2 + font_l * 2 - font_h
        else:
            self.font_offset = self.wcfg["font_offset_vertical"]

        self.gear_width = font_w + padx * 2
        self.gear_height = font_c + pady * 2
        self.speed_width = round(font_w * 3 * font_scale_speed) + padx * 2
        self.speed_height = round(font_c * font_scale_speed) + pady * 2
        self.limiter_width = (
            font_w * len(self.wcfg["speed_limiter_text"])
            + round(font_w * self.wcfg["speed_limiter_padding_horizontal"]) * 2)

        if self.wcfg["show_speed_below_gear"]:
            self.gauge_width = self.gear_width
            if self.wcfg["show_speed"]:
                self.gauge_height = self.gear_height + self.inner_gap + self.speed_height
            else:
                self.gauge_height = self.gear_height
        else:
            if self.wcfg["show_speed"]:
                self.gauge_width = self.gear_width + self.inner_gap + self.speed_width
            else:
                self.gauge_width = self.gear_width
            self.gauge_height = self.gear_height

        self.rpmbar_height = self.wcfg["rpm_bar_height"]
        self.battbar_height = self.wcfg["battery_bar_height"]

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_gauge = self.wcfg["column_index_gauge"]
        column_rpm = self.wcfg["column_index_rpm"]
        column_batt = self.wcfg["column_index_battery"]

        # Config canvas
        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        blank_gauge = QPixmap(self.gauge_width, self.gauge_height)
        self.bar_gauge = QLabel()
        self.bar_gauge.setFixedSize(self.gauge_width, self.gauge_height)
        self.bar_gauge.setPixmap(blank_gauge)
        self.draw_gauge(
            self.bar_gauge,
            (0,0,(self.wcfg["font_color"],self.wcfg["bkg_color"]))
        )

        if self.wcfg["show_speed_limiter"]:
            blank_limiter = QPixmap(self.limiter_width, self.gauge_height)
            self.bar_limiter = QLabel()
            self.bar_limiter.setFixedSize(self.limiter_width, self.gauge_height)
            self.bar_limiter.setPixmap(blank_limiter)
            self.draw_limiter(self.bar_limiter)

        if self.wcfg["show_rpm_bar"]:
            blank_rpmbar = QPixmap(self.gauge_width, self.rpmbar_height)
            self.bar_rpmbar = QLabel()
            self.bar_rpmbar.setFixedSize(self.gauge_width, self.rpmbar_height)
            self.bar_rpmbar.setPixmap(blank_rpmbar)
            self.draw_rpmbar(self.bar_rpmbar, 0)

        if self.wcfg["show_battery_bar"]:
            blank_battbar = QPixmap(self.gauge_width, self.battbar_height)
            self.bar_battbar = QLabel()
            self.bar_battbar.setFixedSize(self.gauge_width, self.battbar_height)
            self.bar_battbar.setPixmap(blank_battbar)
            self.draw_battbar(self.bar_battbar, 0)

        # Set layout
        layout.addWidget(self.bar_gauge, column_gauge, 0)
        if self.wcfg["show_speed_limiter"]:
            layout.addWidget(self.bar_limiter, column_gauge, 1)
        if self.wcfg["show_rpm_bar"]:
            layout.addWidget(self.bar_rpmbar, column_rpm, 0)
        if self.wcfg["show_battery_bar"]:
            layout.addWidget(self.bar_battbar, column_batt, 0)
        self.setLayout(layout)

        # Last data
        self.checked = False

        self.shifting_timer_start = 0
        self.shifting_timer = 0
        self.last_gear = None
        self.last_gauge_data = None
        self.last_rpm_scale = None
        self.last_battery = None
        self.last_motor_state = -1
        self.last_limiter = -1
        self.flicker = 0

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Switch
            if not self.checked:
                self.checked = True

            # Read gauge data
            limiter = api.read.instrument.speed_limiter()
            rpm = api.read.engine.rpm()
            rpm_max = api.read.engine.rpm_max()
            speed = api.read.vehicle.speed()
            gear = api.read.engine.gear()
            gear_max = api.read.engine.gear_max()
            lap_etime = api.read.timing.elapsed()

            rpm_safe = int(rpm_max * self.wcfg["rpm_multiplier_safe"])
            rpm_red = int(rpm_max * self.wcfg["rpm_multiplier_redline"])
            rpm_crit = int(rpm_max * self.wcfg["rpm_multiplier_critical"])

            # Gauge
            if gear != self.last_gear:
                self.shifting_timer_start = lap_etime
                self.last_gear = gear
            self.shifting_timer = lap_etime - self.shifting_timer_start

            gauge_data = (
                self.format_gear(gear),
                round(self.speed_units(speed)),
                self.color_rpm(
                    rpm, rpm_safe, rpm_red, rpm_crit, rpm_max, gear, gear_max, speed)
            )

            self.update_gauge(gauge_data, self.last_gauge_data)
            self.last_gauge_data = gauge_data

            # RPM bar
            if self.wcfg["show_rpm_bar"]:
                rpm_scale = self.scale_rpm(rpm, rpm_safe, rpm_max)
                self.update_rpmbar(rpm_scale, self.last_rpm_scale)
                self.last_rpm_scale = rpm_scale

            # Battery bar
            if self.wcfg["show_battery_bar"]:
                # Hide battery bar if electric motor unavailable
                motor_state = minfo.hybrid.motorState
                self.update_state("battbar", motor_state, self.last_motor_state)
                self.last_motor_state = motor_state

                if motor_state:
                    battery = minfo.hybrid.batteryCharge
                    self.update_battbar(battery, self.last_battery)
                    self.last_battery = battery

            # Speed limier
            if self.wcfg["show_speed_limiter"]:
                self.update_state("limiter", limiter, self.last_limiter)
                self.last_limiter = limiter

        else:
            if self.checked:
                self.checked = False

                # Reset state
                self.shifting_timer_start = 0
                self.shifting_timer = 0
                self.last_gear = None
                self.last_motor_state = -1
                self.last_limiter = -1

    # GUI update methods
    def update_gauge(self, curr, last):
        """Gauge update"""
        if curr != last:
            self.draw_gauge(self.bar_gauge, curr)

    def update_rpmbar(self, curr, last):
        """RPM bar update"""
        if curr != last:
            self.draw_rpmbar(self.bar_rpmbar, curr)

    def update_battbar(self, curr, last):
        """Battery bar update"""
        if curr != last:
            self.draw_battbar(self.bar_battbar, curr)

    def update_state(self, suffix, curr, last):
        """State update"""
        if curr != last:
            if curr:
                getattr(self, f"bar_{suffix}").show()
            else:
                getattr(self, f"bar_{suffix}").hide()

    def draw_gauge(self, canvas, gauge_data):
        """Gauge"""
        gauge = canvas.pixmap()
        painter = QPainter(gauge)
        #painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        self.brush.setColor(QColor(gauge_data[2][1]))

        # Set gauge size
        rect_gauge = QRectF(0, 0, self.gauge_width, self.gauge_height)

        # Update gauge background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawRect(rect_gauge)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Update gauge text
        self.pen.setColor(QColor(gauge_data[2][0]))
        painter.setPen(self.pen)

        rect_gear = QRectF(0, 0, self.gear_width, self.gear_height)
        painter.setFont(self.font_gear)
        painter.drawText(
            rect_gear.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            f"{gauge_data[0]}"
        )

        if self.wcfg["show_speed"]:
            if self.wcfg["show_speed_below_gear"]:
                rect_speed = QRectF(
                    0,
                    self.gear_height + self.inner_gap,
                    self.gear_width,
                    self.speed_height
                )
            else:
                rect_speed = QRectF(
                    self.gear_width + self.inner_gap,
                    0,
                    self.speed_width,
                    self.gear_height
                )
            painter.setFont(self.font_speed)
            painter.drawText(
                rect_speed.adjusted(0, self.font_offset, 0, 0),
                Qt.AlignCenter,
                f"{gauge_data[1]:03.0f}"
            )

        canvas.setPixmap(gauge)

    def draw_rpmbar(self, canvas, rpm_scale):
        """RPM bar"""
        rpmbar = canvas.pixmap()
        painter = QPainter(rpmbar)
        #painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(
            0, 0, self.gauge_width, self.rpmbar_height, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        self.brush.setColor(QColor(self.wcfg["rpm_bar_color"]))

        # Draw rpm
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, rpm_scale, self.rpmbar_height)

        canvas.setPixmap(rpmbar)

    def draw_battbar(self, canvas, battery):
        """Battery bar"""
        battbar = canvas.pixmap()
        painter = QPainter(battbar)
        #painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(
            0, 0, self.gauge_width, self.battbar_height, Qt.transparent)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        self.brush.setColor(QColor(self.wcfg["battery_bar_color"]))

        # Draw battery
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, battery * 0.01 * self.gauge_width, self.battbar_height)

        canvas.setPixmap(battbar)

    def draw_limiter(self, canvas):
        """Limiter"""
        limiter = canvas.pixmap()
        painter = QPainter(limiter)
        #painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)
        self.brush.setColor(QColor(self.wcfg["bkg_color_speed_limiter"]))

        # Set limiter size
        rect_limiter = QRectF(0, 0, self.limiter_width, self.gauge_height)
        rect_text = QRectF(
            0, 0, self.limiter_width, self.gauge_height)

        # Update limiter background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.brush)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawRect(rect_limiter)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Update limiter text
        self.pen.setColor(QColor(self.wcfg["font_color_speed_limiter"]))
        painter.setPen(self.pen)
        painter.setFont(self.font_gear)
        painter.drawText(
            rect_text.adjusted(0, self.font_offset, 0, 0),
            Qt.AlignCenter,
            self.wcfg["speed_limiter_text"]
        )

        canvas.setPixmap(limiter)

    # Additional methods
    @staticmethod
    def format_gear(gear_index):
        """Convert gear index to text string"""
        if gear_index > 0:
            return str(gear_index)
        if gear_index == 0:
            return "N"
        return "R"

    def speed_units(self, value):
        """Speed units"""
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        if self.cfg.units["speed_unit"] == "m/s":
            return value
        return calc.mps2kph(value)

    def scale_rpm(self, rpm, rpm_safe, rpm_max):
        """Scale rpm"""
        rpm_range = rpm_max - rpm_safe
        if rpm_range:
            return max(rpm - rpm_safe, 0) / rpm_range * self.gauge_width
        return 0

    def color_rpm(
            self, rpm, rpm_safe, rpm_red, rpm_crit, rpm_max, gear, gear_max, speed):
        """RPM indicator color"""
        self.flicker = bool(not self.flicker)
        fgcolor = self.wcfg["font_color"]
        if (self.wcfg["show_rpm_flickering_above_critical"] and
            self.flicker and
            gear < gear_max and
            rpm >= rpm_crit):
            fgcolor = self.wcfg["bkg_color"]
            bgcolor = self.wcfg["bkg_color"]
        elif (not gear and
              speed > self.wcfg["neutral_warning_speed_threshold"] and
              self.shifting_timer >= self.wcfg["neutral_warning_time_threshold"]):
            bgcolor = self.wcfg["rpm_color_over_rev"]
        elif rpm > rpm_max:
            bgcolor = self.wcfg["rpm_color_over_rev"]
        elif rpm >= rpm_red:
            bgcolor = self.wcfg["rpm_color_redline"]
        elif rpm >= rpm_safe:
            bgcolor = self.wcfg["rpm_color_safe"]
        else:
            bgcolor = self.wcfg["bkg_color"]
        return fgcolor, bgcolor
