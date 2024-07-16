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
Gear Widget
"""

from PySide2.QtCore import Qt, QRectF
from PySide2.QtGui import QPainter, QPixmap, QPen, QBrush
from PySide2.QtWidgets import QLabel, QGridLayout

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "gear"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font_gear = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight_gear"]
        )
        font_m = self.get_font_metrics(self.font_gear)
        font_offset = self.calc_font_offset(font_m)

        self.font_speed = self.config_font(
            self.wcfg["font_name"],
            self.wcfg["font_size"],
            self.wcfg["font_weight_speed"]
        )
        if self.wcfg["show_speed_below_gear"]:
            font_scale_speed = self.wcfg["font_scale_speed"]
        else:
            font_scale_speed = 1
        self.font_speed.setPixelSize(round(self.wcfg["font_size"] * font_scale_speed))

        # Config variable
        bar_gap = self.wcfg["bar_gap"]
        self.inner_gap = self.wcfg["inner_gap"]
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        self.gear_width = font_m.width + padx * 2
        self.gear_height = font_m.capital + pady * 2
        self.speed_width = round(font_m.width * 3 * font_scale_speed) + padx * 2
        self.speed_height = round(font_m.capital * font_scale_speed) + pady * 2
        self.limiter_width = (
            font_m.width * len(self.wcfg["speed_limiter_text"])
            + round(font_m.width * self.wcfg["speed_limiter_padding_horizontal"]) * 2)

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

        self.rpmbar_height = max(self.wcfg["rpm_bar_height"], 1)
        self.battbar_height = max(self.wcfg["battery_bar_height"], 1)

        self.rect_text_gear = QRectF(0, font_offset, self.gear_width, self.gear_height)
        self.rect_text_limiter = QRectF(0, font_offset, self.limiter_width, self.gauge_height)
        if self.wcfg["show_speed_below_gear"]:
            self.rect_text_speed = QRectF(
                0,
                self.gear_height + self.inner_gap + font_offset,
                self.gear_width,
                self.speed_height
            )
        else:
            self.rect_text_speed = QRectF(
                self.gear_width + self.inner_gap,
                font_offset,
                self.speed_width,
                self.gear_height
            )

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

        self.bar_gauge = QLabel()
        self.bar_gauge.setFixedSize(self.gauge_width, self.gauge_height)
        self.pixmap_gauge = QPixmap(self.gauge_width, self.gauge_height)
        self.draw_gauge(
            self.bar_gauge, self.pixmap_gauge,
            (0,0,(self.wcfg["font_color"],self.wcfg["bkg_color"]))
        )

        if self.wcfg["show_speed_limiter"]:
            self.bar_limiter = QLabel()
            self.bar_limiter.setFixedSize(self.limiter_width, self.gauge_height)
            self.pixmap_limiter = QPixmap(self.limiter_width, self.gauge_height)
            self.draw_limiter(self.bar_limiter, self.pixmap_limiter)

        if self.wcfg["show_rpm_bar"]:
            self.bar_rpmbar = QLabel()
            self.bar_rpmbar.setFixedSize(self.gauge_width, self.rpmbar_height)
            self.bar_rpmbar.setStyleSheet(f"background: {self.wcfg['rpm_bar_bkg_color']};")
            self.pixmap_rpmbar = QPixmap(self.gauge_width, self.rpmbar_height)
            self.draw_rpmbar(self.bar_rpmbar, self.pixmap_rpmbar, 0)

        if self.wcfg["show_battery_bar"]:
            self.bar_battbar = QLabel()
            self.bar_battbar.setFixedSize(self.gauge_width, self.battbar_height)
            self.bar_battbar.setStyleSheet(f"background: {self.wcfg['battery_bar_bkg_color']};")
            self.pixmap_battbar = QPixmap(self.gauge_width, self.battbar_height)
            self.draw_battbar(self.bar_battbar, self.pixmap_battbar, 0, 0)

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

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state:

            # Switch
            if not self.checked:
                self.checked = True

            # Read gauge data
            limiter = api.read.switch.speed_limiter()
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
                fmt.select_gear(gear),
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
                    battery = minfo.hybrid.batteryCharge, motor_state
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
            self.draw_gauge(self.bar_gauge, self.pixmap_gauge, curr)

    def update_rpmbar(self, curr, last):
        """RPM bar update"""
        if curr != last:
            self.draw_rpmbar(self.bar_rpmbar, self.pixmap_rpmbar, curr)

    def update_battbar(self, curr, last):
        """Battery bar update"""
        if curr != last:
            self.draw_battbar(self.bar_battbar, self.pixmap_battbar, *curr)

    def update_state(self, suffix, curr, last):
        """State update"""
        if curr != last:
            if curr:
                getattr(self, f"bar_{suffix}").show()
            else:
                getattr(self, f"bar_{suffix}").hide()

    def draw_gauge(self, canvas, pixmap, gauge_data):
        """Gauge"""
        pixmap.fill(gauge_data[2][1])
        painter = QPainter(pixmap)

        # Update gauge text
        self.pen.setColor(gauge_data[2][0])
        painter.setPen(self.pen)

        painter.setFont(self.font_gear)
        painter.drawText(
            self.rect_text_gear,
            Qt.AlignCenter,
            f"{gauge_data[0]}"
        )

        if self.wcfg["show_speed"]:
            painter.setFont(self.font_speed)
            painter.drawText(
                self.rect_text_speed,
                Qt.AlignCenter,
                f"{gauge_data[1]:03.0f}"
            )

        canvas.setPixmap(pixmap)

    def draw_rpmbar(self, canvas, pixmap, rpm_scale):
        """RPM bar"""
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # Draw rpm
        painter.setPen(Qt.NoPen)
        self.brush.setColor(self.wcfg["rpm_bar_color"])
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, rpm_scale, self.rpmbar_height)

        canvas.setPixmap(pixmap)

    def draw_battbar(self, canvas, pixmap, battery, state):
        """Battery bar"""
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # Draw battery
        painter.setPen(Qt.NoPen)
        if state == 3:
            self.brush.setColor(self.wcfg["battery_bar_color_regen"])
        else:
            self.brush.setColor(self.wcfg["battery_bar_color"])
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, battery * 0.01 * self.gauge_width, self.battbar_height)

        canvas.setPixmap(pixmap)

    def draw_limiter(self, canvas, pixmap):
        """Limiter"""
        pixmap.fill(self.wcfg["bkg_color_speed_limiter"])
        painter = QPainter(pixmap)

        # Update limiter text
        self.pen.setColor(self.wcfg["font_color_speed_limiter"])
        painter.setPen(self.pen)
        painter.setFont(self.font_gear)
        painter.drawText(
            self.rect_text_limiter,
            Qt.AlignCenter,
            self.wcfg["speed_limiter_text"]
        )

        canvas.setPixmap(pixmap)

    # Additional methods
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
