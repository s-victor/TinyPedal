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
Instrument Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPixmap, QPainter, QPen, QColor
from PySide2.QtWidgets import (
    QLabel,
    QGridLayout,
)

from .. import calculation as calc
from ..api_control import api
from ..base import Widget

WIDGET_NAME = "instrument"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config variable
        bar_gap = self.wcfg["bar_gap"]
        self.icon_size = int(max(self.wcfg["icon_size"], 16) / 2) * 2

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_hl = self.wcfg["column_index_headlights"]
        column_ig = self.wcfg["column_index_ignition"]
        column_cl = self.wcfg["column_index_clutch"]
        column_wl = self.wcfg["column_index_wheel_lock"]
        column_ws = self.wcfg["column_index_wheel_slip"]

        # Config canvas
        blank_image = QPixmap(self.icon_size, self.icon_size)
        icon_source = QPixmap("images/icon_instrument.png")
        self.icon_inst = icon_source.scaledToWidth(
            self.icon_size * 2,
            mode=Qt.SmoothTransformation
        )

        self.pen = QPen()

        # Headlights
        if self.wcfg["show_headlights"]:
            self.bar_headlights = QLabel()
            self.bar_headlights.setFixedSize(self.icon_size, self.icon_size)
            self.bar_headlights.setPixmap(blank_image)
            self.draw_instrument(self.bar_headlights, 1, 0)

        # Ignition
        if self.wcfg["show_ignition"]:
            self.bar_ignition = QLabel()
            self.bar_ignition.setFixedSize(self.icon_size, self.icon_size)
            self.bar_ignition.setPixmap(blank_image)
            self.draw_instrument(self.bar_ignition, 1, 1)

        # Clutch
        if self.wcfg["show_clutch"]:
            self.bar_clutch = QLabel()
            self.bar_clutch.setFixedSize(self.icon_size, self.icon_size)
            self.bar_clutch.setPixmap(blank_image)
            self.draw_instrument(self.bar_clutch, 1, 2)

        # Lock
        if self.wcfg["show_wheel_lock"]:
            self.bar_wlock = QLabel()
            self.bar_wlock.setFixedSize(self.icon_size, self.icon_size)
            self.bar_wlock.setPixmap(blank_image)
            self.draw_instrument(self.bar_wlock, 1, 3)

        # Slip
        if self.wcfg["show_wheel_slip"]:
            self.bar_wslip = QLabel()
            self.bar_wslip.setFixedSize(self.icon_size, self.icon_size)
            self.bar_wslip.setPixmap(blank_image)
            self.draw_instrument(self.bar_wslip, 1, 4)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Horizontal layout
            if self.wcfg["show_headlights"]:
                layout.addWidget(self.bar_headlights, 0, column_hl)
            if self.wcfg["show_ignition"]:
                layout.addWidget(self.bar_ignition, 0, column_ig)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, 0, column_cl)
            if self.wcfg["show_wheel_lock"]:
                layout.addWidget(self.bar_wlock, 0, column_wl)
            if self.wcfg["show_wheel_slip"]:
                layout.addWidget(self.bar_wslip, 0, column_ws)
        else:
            # Vertical layout
            if self.wcfg["show_headlights"]:
                layout.addWidget(self.bar_headlights, column_hl, 0)
            if self.wcfg["show_ignition"]:
                layout.addWidget(self.bar_ignition, column_ig, 0)
            if self.wcfg["show_clutch"]:
                layout.addWidget(self.bar_clutch, column_cl, 0)
            if self.wcfg["show_wheel_lock"]:
                layout.addWidget(self.bar_wlock, column_wl, 0)
            if self.wcfg["show_wheel_slip"]:
                layout.addWidget(self.bar_wslip, column_ws, 0)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.vehicle_id = None
        self.min_samples_f = 20
        self.min_samples_r = 20
        self.list_radius_f = []
        self.list_radius_r = []
        self.avg_wheel_radius_f = self.wcfg["last_wheel_radius_front"]
        self.avg_wheel_radius_r = self.wcfg["last_wheel_radius_rear"]

        self.last_headlights = None
        self.last_ignition = None
        self.last_clutch = None
        self.last_wlock = None
        self.last_slipratio = None
        self.flicker = 0

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and api.state:

            # Save switch
            if not self.checked:
                self.checked = True
                self.vehicle_id = api.read.check.vehicle_id()
                if self.wcfg["last_vehicle_info"] == self.vehicle_id:
                    self.min_samples_f = 320
                    self.min_samples_r = 320

            # Read instrument data
            headlights = api.read.switch.headlights()
            ignition = (api.read.switch.ignition_starter(),
                        api.read.engine.rpm())
            clutch = (api.read.switch.auto_clutch(),
                      api.read.input.clutch())
            is_braking = api.read.input.brake() > 0
            wheel_rot = api.read.wheel.rotation()
            speed = api.read.vehicle.speed()

            slipratio = round(self.calc_slipratio(wheel_rot, speed), 2)
            self.flicker = bool(not self.flicker)

            # Headlights
            if self.wcfg["show_headlights"]:
                self.update_headlights(headlights, self.last_headlights)
                self.last_headlights = headlights

            # Ignition
            if self.wcfg["show_ignition"]:
                self.update_ignition(ignition, self.last_ignition)
                self.last_ignition = ignition

            # Clutch
            if self.wcfg["show_clutch"]:
                self.update_clutch(clutch, self.last_clutch)
                self.last_clutch = clutch

            # Wheel lock
            if self.wcfg["show_wheel_lock"]:
                wlock = (is_braking, slipratio)
                self.update_wlock(wlock, self.last_wlock)
                self.last_wlock = wlock

            # Wheel slip
            if self.wcfg["show_wheel_slip"]:
                self.update_wslip(slipratio, self.last_slipratio)
                self.last_slipratio = slipratio

        else:
            if self.checked:
                self.checked = False

                if self.min_samples_f == self.min_samples_r == 320:
                    self.wcfg["last_vehicle_info"] = self.vehicle_id
                    self.wcfg["last_wheel_radius_front"] = self.avg_wheel_radius_f
                    self.wcfg["last_wheel_radius_rear"] = self.avg_wheel_radius_r
                self.cfg.save()

    # GUI update methods
    def update_headlights(self, curr, last):
        """Headlights update"""
        if curr != last:
            state = 0 if curr == 1 else 1
            self.draw_instrument(self.bar_headlights, state, 0)

    def update_ignition(self, curr, last):
        """Ignition update"""
        if curr != last:
            state = 0 if curr[0] > 0 else 1
            color = self.wcfg["warning_color_ignition"] if curr[1] < 10 else None
            self.draw_instrument(self.bar_ignition, state, 1, color)

    def update_clutch(self, curr, last):
        """Clutch update"""
        if curr != last:
            state = 0 if curr[0] > 0 else 1
            color = self.wcfg["warning_color_clutch"] if curr[1] > 0.01 else None
            self.draw_instrument(self.bar_clutch, state, 2, color)

    def update_wlock(self, curr, last):
        """Wheel lock update"""
        if curr != last:
            if self.flicker and curr[0] > 0 and curr[1] >= self.wcfg["wheel_lock_threshold"]:
                state = 0
                color = self.wcfg["warning_color_wheel_lock"]
            else:
                state = 1
                color = None
            self.draw_instrument(self.bar_wlock, state, 3, color)

    def update_wslip(self, curr, last):
        """Wheel slip update"""
        if curr != last:
            if self.flicker and curr >= self.wcfg["wheel_slip_threshold"]:
                state = 0
                color = self.wcfg["warning_color_wheel_slip"]
            else:
                state = 1
                color = None
            self.draw_instrument(self.bar_wslip, state, 4, color)

    def draw_instrument(self, canvas, h_offset, v_offset, hicolor=None):
        """Instrument"""
        icon = canvas.pixmap()
        painter = QPainter(icon)

        # Set size
        rect_size = QRectF(0, 0, self.icon_size, self.icon_size)
        rect_offset = QRectF(
            self.icon_size * h_offset,  # x pos
            self.icon_size * v_offset,  # y pos
            self.icon_size,
            self.icon_size
        )

        # Background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        rect_bg = QColor(self.wcfg["bkg_color"] if not hicolor else hicolor)
        painter.setPen(Qt.NoPen)
        painter.fillRect(rect_size, rect_bg)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Icon
        painter.drawPixmap(rect_size, self.icon_inst, rect_offset)
        canvas.setPixmap(icon)

    # Additional methods
    def calc_slipratio(self, wheel_rot, speed):
        """Calculate slip ratio"""
        if speed > self.wcfg["minimum_speed"]:
            # Get wheel rotation difference
            # Record radius value for targeted rotation difference
            # Max rotation vs average, negative = forward,  so use min instead of max
            diff_rot_f = calc.min_vs_avg(wheel_rot[0:2])
            diff_rot_r = calc.min_vs_avg(wheel_rot[2:4])
            # Record radius value for targeted rotation difference
            if 0 < diff_rot_f < 0.1:
                self.list_radius_f.append(
                    calc.rot2radius(speed, calc.mean(wheel_rot[0:2])))
            if 0 < diff_rot_r < 0.1:
                self.list_radius_r.append(
                    calc.rot2radius(speed, calc.mean(wheel_rot[2:4])))

            # Calc average wheel radius reading
            if len(self.list_radius_f) >= self.min_samples_f:
                radius_samples_f = sorted(
                    self.list_radius_f)[int(self.min_samples_f*0.25):int(self.min_samples_f*0.75)]
                self.avg_wheel_radius_f = round(calc.mean(radius_samples_f), 3)
                self.list_radius_f = []  # reset list
                if self.min_samples_f < 320:
                    self.min_samples_f *= 2  # double sample counts

            if len(self.list_radius_r) >= self.min_samples_r:
                radius_samples_r = sorted(
                    self.list_radius_r)[int(self.min_samples_r*0.25):int(self.min_samples_r*0.75)]
                self.avg_wheel_radius_r = round(calc.mean(radius_samples_r), 3)
                self.list_radius_r = []
                if self.min_samples_r < 320:
                    self.min_samples_r *= 2

        return max(tuple(map(
            calc.slip_ratio,
            wheel_rot,
            [self.avg_wheel_radius_f] * 2 + [self.avg_wheel_radius_r] * 2,
            [speed] * 4
        )))
