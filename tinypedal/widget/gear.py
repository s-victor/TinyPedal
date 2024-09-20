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
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "gear"


class Realtime(Overlay):
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
        inner_gap = self.wcfg["inner_gap"]
        padx = round(font_m.width * self.wcfg["bar_padding_horizontal"])
        pady = round(font_m.capital * self.wcfg["bar_padding_vertical"])

        gear_width = font_m.width + padx * 2
        gear_height = font_m.capital + pady * 2
        speed_width = round(font_m.width * 3 * font_scale_speed) + padx * 2
        speed_height = round(font_m.capital * font_scale_speed) + pady * 2
        limiter_width = (
            font_m.width * len(self.wcfg["speed_limiter_text"])
            + round(font_m.width * self.wcfg["speed_limiter_padding_horizontal"]) * 2)

        if self.wcfg["show_speed_below_gear"]:
            self.gauge_width = gear_width
            if self.wcfg["show_speed"]:
                gauge_height = gear_height + inner_gap + speed_height
            else:
                gauge_height = gear_height
        else:
            if self.wcfg["show_speed"]:
                self.gauge_width = gear_width + inner_gap + speed_width
            else:
                self.gauge_width = gear_width
            gauge_height = gear_height

        self.rpmbar_height = max(self.wcfg["rpm_bar_height"], 1)
        self.battbar_height = max(self.wcfg["battery_bar_height"], 1)

        self.rect_text_gear = QRectF(0, font_offset, gear_width, gear_height)
        self.rect_text_limiter = QRectF(0, font_offset, limiter_width, gauge_height)
        if self.wcfg["show_speed_below_gear"]:
            self.rect_text_speed = QRectF(
                0,
                gear_height + inner_gap + font_offset,
                gear_width,
                speed_height
            )
        else:
            self.rect_text_speed = QRectF(
                gear_width + inner_gap,
                font_offset,
                speed_width,
                gear_height
            )

        # Last data
        self.flicker = 0
        self.shifting_timer_start = 0
        self.shifting_timer = 0
        self.rpm_safe = 0
        self.rpm_red = 0
        self.rpm_crit = 0
        self.rpm_range = 0
        self.last_rpm_max = 0
        self.last_rpm_scale = 0
        self.last_gear = 0
        self.last_gauge_state = None
        self.last_battery = 0
        self.last_motor_state = -1
        self.last_limiter = -1

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Config canvas
        self.pen = QPen()
        self.brush = QBrush(Qt.SolidPattern)

        self.bar_gauge = self.set_qlabel(
            fixed_width=self.gauge_width,
            fixed_height=gauge_height,
        )
        self.pixmap_gauge = QPixmap(self.gauge_width, gauge_height)
        self.draw_gauge(
            self.bar_gauge, self.pixmap_gauge, 0, 0,
            self.wcfg["font_color"], self.wcfg["bkg_color"],
        )
        layout.addWidget(self.bar_gauge, self.wcfg["column_index_gauge"], 0)

        if self.wcfg["show_speed_limiter"]:
            self.bar_limiter = self.set_qlabel(
                fixed_width=limiter_width,
                fixed_height=gauge_height,
            )
            self.pixmap_limiter = QPixmap(limiter_width, gauge_height)
            self.draw_limiter(self.bar_limiter, self.pixmap_limiter)
            layout.addWidget(self.bar_limiter, self.wcfg["column_index_gauge"], 1)

        if self.wcfg["show_rpm_bar"]:
            bar_style_rpmbar = self.set_qss(
                bg_color=self.wcfg["rpm_bar_bkg_color"]
            )
            self.bar_rpmbar = self.set_qlabel(
                style=bar_style_rpmbar,
                fixed_width=self.gauge_width,
                fixed_height=self.rpmbar_height,
            )
            self.pixmap_rpmbar = QPixmap(self.gauge_width, self.rpmbar_height)
            self.draw_rpmbar(self.bar_rpmbar, self.pixmap_rpmbar, 0)
            layout.addWidget(self.bar_rpmbar, self.wcfg["column_index_rpm"], 0)

        if self.wcfg["show_battery_bar"]:
            bar_style_battbar = self.set_qss(
                bg_color=self.wcfg["battery_bar_bkg_color"]
            )
            self.bar_battbar = self.set_qlabel(
                style=bar_style_battbar,
                fixed_width=self.gauge_width,
                fixed_height=self.battbar_height,
            )
            self.pixmap_battbar = QPixmap(self.gauge_width, self.battbar_height)
            self.draw_battbar(self.bar_battbar, self.pixmap_battbar, 0)
            layout.addWidget(self.bar_battbar, self.wcfg["column_index_battery"], 0)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Read gauge data
            limiter = api.read.switch.speed_limiter()
            rpm = api.read.engine.rpm()
            rpm_max = api.read.engine.rpm_max()
            speed = api.read.vehicle.speed()
            gear = api.read.engine.gear()
            gear_max = api.read.engine.gear_max()
            lap_etime = api.read.timing.elapsed()

            # RPM reference
            if self.last_rpm_max != rpm_max:
                self.last_rpm_max = rpm_max
                self.rpm_safe = int(rpm_max * self.wcfg["rpm_multiplier_safe"])
                self.rpm_red = int(rpm_max * self.wcfg["rpm_multiplier_redline"])
                self.rpm_crit = int(rpm_max * self.wcfg["rpm_multiplier_critical"])
                self.rpm_range = rpm_max - self.rpm_safe

            # Shifting timer
            if self.last_gear != gear:
                self.shifting_timer_start = lap_etime
                self.last_gear = gear
            self.shifting_timer = lap_etime - self.shifting_timer_start

            # Gauge
            gauge_state = rpm + gear + speed
            if gauge_state != self.last_gauge_state:
                gauge_fg, gauge_bg = self.color_rpm(rpm, gear, gear_max, speed)
                self.draw_gauge(
                    self.bar_gauge, self.pixmap_gauge,
                    gear, speed, gauge_fg, gauge_bg,
                )
                self.last_gauge_state = gauge_state

            # RPM bar
            if self.wcfg["show_rpm_bar"]:
                rpm_scale = self.scale_rpm(rpm)
                self.update_rpmbar(rpm_scale, self.last_rpm_scale)
                self.last_rpm_scale = rpm_scale

            # Battery bar
            if self.wcfg["show_battery_bar"]:
                # Hide battery bar if electric motor unavailable
                motor_state = minfo.hybrid.motorState
                self.update_state(self.bar_battbar, motor_state, self.last_motor_state)
                self.last_motor_state = motor_state

                if motor_state:
                    battery = minfo.hybrid.batteryCharge
                    self.update_battbar(battery, self.last_battery)
                    self.last_battery = battery

            # Speed limier
            if self.wcfg["show_speed_limiter"]:
                self.update_state(self.bar_limiter, limiter, self.last_limiter)
                self.last_limiter = limiter

    # GUI update methods
    def update_rpmbar(self, curr, last):
        """RPM bar update"""
        if curr != last:
            self.draw_rpmbar(self.bar_rpmbar, self.pixmap_rpmbar, curr)

    def update_battbar(self, curr, last):
        """Battery bar update"""
        if curr != last:
            self.draw_battbar(self.bar_battbar, self.pixmap_battbar, curr)

    def update_state(self, target_bar, curr, last):
        """State update"""
        if curr != last:
            if curr:
                target_bar.show()
            else:
                target_bar.hide()

    def draw_gauge(self, canvas, pixmap, gear, speed, fg_color, bg_color):
        """Gauge"""
        pixmap.fill(bg_color)
        painter = QPainter(pixmap)

        # Update gauge text
        self.pen.setColor(fg_color)
        painter.setPen(self.pen)

        painter.setFont(self.font_gear)
        painter.drawText(
            self.rect_text_gear,
            Qt.AlignCenter,
            fmt.select_gear(gear)
        )

        if self.wcfg["show_speed"]:
            painter.setFont(self.font_speed)
            painter.drawText(
                self.rect_text_speed,
                Qt.AlignCenter,
                f"{self.speed_units(speed):03.0f}"
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

    def draw_battbar(self, canvas, pixmap, battery):
        """Battery bar"""
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)

        # Draw battery
        painter.setPen(Qt.NoPen)
        if self.last_motor_state == 3:
            self.brush.setColor(self.wcfg["battery_bar_color_regen"])
        else:
            self.brush.setColor(self.wcfg["battery_bar_color"])
        painter.setBrush(self.brush)
        painter.drawRect(0, 0, battery * 0.01 * self.gauge_width, self.battbar_height)

        canvas.setPixmap(pixmap)

    def draw_limiter(self, canvas, pixmap):
        """Limiter bar (draw only once)"""
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
        if self.cfg.units["speed_unit"] == "KPH":
            return calc.mps2kph(value)
        if self.cfg.units["speed_unit"] == "MPH":
            return calc.mps2mph(value)
        return value

    def scale_rpm(self, rpm):
        """Scale rpm"""
        rpm_offset = rpm - self.rpm_safe
        if self.rpm_range > 0 <= rpm_offset:
            return rpm_offset / self.rpm_range * self.gauge_width
        return 0

    def color_rpm(self, rpm, gear, gear_max, speed):
        """RPM indicator color"""
        self.flicker = not self.flicker

        if (self.wcfg["show_rpm_flickering_above_critical"] and
            self.flicker and
            gear < gear_max and
            rpm >= self.rpm_crit):
            return self.wcfg["bkg_color"], self.wcfg["bkg_color"]

        if (not gear and
            speed > self.wcfg["neutral_warning_speed_threshold"] and
            self.shifting_timer >= self.wcfg["neutral_warning_time_threshold"]):
            bgcolor = self.wcfg["rpm_color_over_rev"]
        elif rpm > self.last_rpm_max:
            bgcolor = self.wcfg["rpm_color_over_rev"]
        elif rpm >= self.rpm_red:
            bgcolor = self.wcfg["rpm_color_redline"]
        elif rpm >= self.rpm_safe:
            bgcolor = self.wcfg["rpm_color_safe"]
        else:
            bgcolor = self.wcfg["bkg_color"]
        return self.wcfg["font_color"], bgcolor
