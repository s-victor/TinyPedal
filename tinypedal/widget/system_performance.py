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
System performance Widget
"""

import os
from functools import partial

import psutil
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from .. import calculation as calc
from ._base import Overlay

WIDGET_NAME = "system_performance"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        if self.wcfg["layout"] == 0:
            prefix_just = max(
                len(self.wcfg["prefix_system"]),
                len(self.wcfg["prefix_tinypedal"]),
            )
        else:
            prefix_just = 0

        self.prefix_sys = self.wcfg["prefix_system"].ljust(prefix_just)
        self.prefix_app = self.wcfg["prefix_tinypedal"].ljust(prefix_just)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # System
        if self.wcfg["show_system_performance"]:
            text_system = f"{self.prefix_sys}0.00% 0.00GB"
            bar_style_system = self.set_qss(
                fg_color=self.wcfg["font_color_system"],
                bg_color=self.wcfg["bkg_color_system"]
            )
            self.bar_system = self.set_qlabel(
                text=text_system,
                style=bar_style_system,
                width=font_m.width * len(text_system) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_system,
                column=self.wcfg["column_index_system"],
            )

        # APP performance
        if self.wcfg["show_tinypedal_performance"]:
            text_app = f"{self.prefix_app}0.00% 0.00MB"
            bar_style_app = self.set_qss(
                fg_color=self.wcfg["font_color_tinypedal"],
                bg_color=self.wcfg["bkg_color_tinypedal"]
            )
            self.bar_app = self.set_qlabel(
                text=text_app,
                style=bar_style_app,
                width=font_m.width * len(text_app) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_app,
                column=self.wcfg["column_index_tinypedal"],
            )

        # Last data
        self.app_info = psutil.Process(os.getpid())
        self.cpu_count = os.cpu_count()
        self.last_sys_cpu = 0
        self.last_app_cpu = 0

        self.calc_ema_cpu = partial(
            calc.exp_mov_avg,
            calc.ema_factor(min(max(self.wcfg["average_samples"], 1), 500))
        )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            if self.wcfg["show_system_performance"]:
                sys_cpu = self.calc_ema_cpu(
                    self.last_sys_cpu, psutil.cpu_percent())
                self.update_system(
                    self.bar_system, sys_cpu, self.last_sys_cpu,
                    self.prefix_sys
                )
                self.last_sys_cpu = sys_cpu

            if self.wcfg["show_tinypedal_performance"]:
                app_cpu = self.calc_ema_cpu(
                    self.last_app_cpu, self.app_info.cpu_percent() / self.cpu_count)
                self.update_app(
                    self.bar_app, app_cpu, self.last_app_cpu,
                    self.prefix_app
                )
                self.last_app_cpu = app_cpu

    # GUI update methods
    def update_system(self, target_bar, curr, last, prefix):
        """System performance"""
        if curr != last:
            memory_used = round(
                psutil.virtual_memory().used / 1024 / 1024 / 1024, 1)
            cpu = f"{curr: >4.2f}"[:4].strip(".")
            mem = f"{memory_used: >4.2f}"[:4].strip(".")
            target_bar.setText(f"{prefix}{cpu: >4}%{mem: >5}GB")

    def update_app(self, target_bar, curr, last, prefix):
        """APP performance"""
        if curr != last:
            memory_used = round(
                self.app_info.memory_full_info().uss / 1024 / 1024, 1)
            cpu = f"{curr: >4.2f}"[:4].strip(".")
            mem = f"{memory_used: >4.2f}"[:4].strip(".")
            target_bar.setText(f"{prefix}{cpu: >4}%{mem: >5}MB")
