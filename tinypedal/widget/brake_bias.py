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
Brake bias Widget
"""

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "brake_bias"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.decimals_bias = max(self.wcfg["decimal_places_brake_bias"], 0)
        self.decimals_migt = max(self.wcfg["decimal_places_brake_migration"], 1)
        self.prefix_bias = self.wcfg["prefix_brake_bias"]
        self.prefix_migt = self.wcfg["prefix_brake_migration"]
        self.suffix_migt = self.wcfg["suffix_brake_migration"]
        self.sign_text = "%" if self.wcfg["show_percentage_sign"] else ""

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Brake bias
        text_bbias = self.format_brake_bias(50)
        bar_style_bbias = self.set_qss(
            fg_color=self.wcfg["font_color_brake_bias"],
            bg_color=self.wcfg["bkg_color_brake_bias"]
        )
        self.bar_bbias = self.set_qlabel(
            text=text_bbias,
            style=bar_style_bbias,
            width=font_m.width * len(text_bbias) + bar_padx,
        )
        self.set_primary_orient(
            target=self.bar_bbias,
            column=self.wcfg["column_index_brake_bias"],
        )

        # Brake migration
        if self.wcfg["show_brake_migration"]:
            text_bmigt = self.format_brake_migt(0)
            bar_style_bmigt = self.set_qss(
                fg_color=self.wcfg["font_color_brake_migration"],
                bg_color=self.wcfg["bkg_color_brake_migration"]
            )
            self.bar_bmigt = self.set_qlabel(
                text=text_bmigt,
                style=bar_style_bmigt,
                width=font_m.width * len(text_bmigt) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_bmigt,
                column=self.wcfg["column_index_brake_migration"],
            )

        # Last data
        self.checked = False
        self.brake_bmigt = BrakeMigration(self.wcfg["electric_braking_allocation"])

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Brake bias
            bbias = api.read.brake.bias_front()
            self.update_bbias(self.bar_bbias, bbias)

            # Brake migration
            if self.wcfg["show_brake_migration"]:
                bmigt = self.brake_bmigt.calc(
                    brake_raw=api.read.input.brake_raw(),
                    brake_bias=bbias,
                    brake_pres=api.read.brake.pressure()
                )
                self.update_bmigt(self.bar_bmigt, bmigt)

        else:
            if self.checked:
                self.checked = False
                self.brake_bmigt.reset()

    # GUI update methods
    def update_bbias(self, target, data):
        """Brake bias"""
        if target.last != data:
            target.last = data
            target.setText(self.format_brake_bias(data * 100))

    def update_bmigt(self, target, data):
        """Brake migration"""
        if target.last != data:
            target.last = data
            target.setText(self.format_brake_migt(data * 100))

    # Additional methods
    def format_brake_bias(self, value):
        """Format brake bias"""
        front = f"{self.prefix_bias}{value:02.{self.decimals_bias}f}"
        if self.wcfg["show_front_and_rear"]:
            return f"{front}:{100 - value:02.{self.decimals_bias}f}"
        return f"{front}{self.sign_text}"

    def format_brake_migt(self, value):
        """Format brake migration"""
        reading = f"{value:.{self.decimals_migt}f}"[:2 + self.decimals_migt]
        return f"{self.prefix_migt}{reading}{self.suffix_migt}"


class BrakeMigration:
    """Brake migration detection & calculation"""

    def __init__(self, ebrake_alloc: int) -> None:
        """
        Args:
            ebrake_alloc: electric braking allocation, -1 = auto detect, 0 = front, 1 = rear.
        """
        self._bpres_max = 0
        self._bpres_scale = 1
        self._ebrake_alloc = ebrake_alloc
        self._auto_detect = bool(ebrake_alloc == -1)

    def calc(self, brake_raw: float, brake_bias: float, brake_pres: list) -> float:
        """Calculate brake migration

        Args:
            brake_raw: raw brake input.
            brake_bias: front brake bias (fraction).
            brake_pres: brake pressure (4 tyres).

        Returns:
            Brake migration (fraction).
        """
        bpres_sum = sum(brake_pres)

        if self._bpres_max < bpres_sum:
            self._bpres_max = bpres_sum
            self._bpres_scale = 2 / bpres_sum

        if brake_raw > max(brake_pres) > 0:
            max_front = max(brake_pres[:2])
            max_rear = max(brake_pres[2:])

            if self._auto_detect and minfo.hybrid.motorState == 3 and max_rear > 0:
                max_brake_ratio = max_front / max_rear
                if max_brake_ratio < 0.25:
                    self._ebrake_alloc = 0  # front ebrake
                elif max_brake_ratio > 4:
                    self._ebrake_alloc = 1  # rear ebrake

            if self._ebrake_alloc == 0:
                bias_rear = max_rear * self._bpres_scale
                bias_front_live = 1 - bias_rear / brake_raw
            else:
                bias_front = max_front * self._bpres_scale
                bias_front_live = bias_front / brake_raw

            return max(bias_front_live - brake_bias, +0)
        return 0

    def reset(self):
        """Reset"""
        self._bpres_max = 0
        self._bpres_scale = 1
