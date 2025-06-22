#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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
Laps and position Widget
"""

from .. import calculation as calc
from ..api_control import api
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "00/00"
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])

        if self.wcfg["layout"] == 0:
            self.just_right = 9
            prefix_just = max(
                len(self.wcfg["prefix_lap_number"]),
                len(self.wcfg["prefix_position_overall"]),
                len(self.wcfg["prefix_position_in_class"]),
            )
        else:
            self.just_right = 6
            prefix_just = 0

        self.prefix_lap_number = self.wcfg["prefix_lap_number"].ljust(prefix_just)
        self.prefix_pos_overall = self.wcfg["prefix_position_overall"].ljust(prefix_just)
        self.prefix_pos_inclass = self.wcfg["prefix_position_in_class"].ljust(prefix_just)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Lap number
        if self.wcfg["show_lap_number"]:
            text_lap_number = f"{self.prefix_lap_number}  0.00/--"
            self.bar_style_lap_number = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_lap_number"],
                    bg_color=self.wcfg["bkg_color_lap_number"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_lap_number"],
                    bg_color=self.wcfg["bkg_color_maxlap_warn"])
            )
            self.bar_lap_number = self.set_qlabel(
                text=text_lap_number,
                style=self.bar_style_lap_number[0],
                width=font_m.width * len(text_lap_number) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_lap_number,
                column=self.wcfg["column_index_lap_number"],
            )

        # Position overall
        if self.wcfg["show_position_overall"]:
            text_pos_overall = f"{self.prefix_pos_overall}{text_def: >{self.just_right}}"
            bar_style_pos_overall = self.set_qss(
                fg_color=self.wcfg["font_color_position_overall"],
                bg_color=self.wcfg["bkg_color_position_overall"]
            )
            self.bar_pos_overall = self.set_qlabel(
                text=text_pos_overall,
                style=bar_style_pos_overall,
                width=font_m.width * len(text_pos_overall) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_pos_overall,
                column=self.wcfg["column_index_position_overall"],
            )

        # Position in class
        if self.wcfg["show_position_in_class"]:
            text_pos_inclass = f"{self.prefix_pos_inclass}{text_def: >{self.just_right}}"
            bar_style_pos_inclass = self.set_qss(
                fg_color=self.wcfg["font_color_position_in_class"],
                bg_color=self.wcfg["bkg_color_position_in_class"]
            )
            self.bar_pos_inclass = self.set_qlabel(
                text=text_pos_inclass,
                style=bar_style_pos_inclass,
                width=font_m.width * len(text_pos_inclass) + bar_padx,
            )
            self.set_primary_orient(
                target=self.bar_pos_inclass,
                column=self.wcfg["column_index_position_in_class"],
            )

        # Last data
        self.last_veh_total = 0
        self.last_plr_place = 0

    def timerEvent(self, event):
        """Update when vehicle on track"""
        # Lap number
        if self.wcfg["show_lap_number"]:
            lap_into = calc.lap_progress_correction(
                api.read.lap.progress(), api.read.timing.current_laptime())
            self.update_lap_number(self.bar_lap_number, lap_into)

        # Position update
        if self.wcfg["show_position_overall"] or self.wcfg["show_position_in_class"]:
            plr_place = api.read.vehicle.place()
            veh_total = api.read.vehicle.total_vehicles()

            # Only update if total vehicle or player position changes
            if self.last_plr_place != plr_place or self.last_veh_total != veh_total:
                self.last_plr_place = plr_place
                self.last_veh_total = veh_total

                # Position overall
                if self.wcfg["show_position_overall"]:
                    self.update_position(
                        self.bar_pos_overall, plr_place, veh_total,
                        self.prefix_pos_overall
                    )

                # Position in class
                if self.wcfg["show_position_in_class"]:
                    plr_class = api.read.vehicle.class_name()
                    total_class_vehicle = 0
                    place_higher = 0

                    for index in range(veh_total):
                        if api.read.vehicle.class_name(index) == plr_class:
                            total_class_vehicle += 1
                            if api.read.vehicle.place(index) > plr_place:
                                place_higher += 1

                    pos_in_class = total_class_vehicle - place_higher
                    self.update_position(
                        self.bar_pos_inclass, pos_in_class, total_class_vehicle,
                        self.prefix_pos_inclass
                    )

    # GUI update methods
    def update_lap_number(self, target, data):
        """Lap number"""
        if target.last != data:
            target.last = data
            lap_num = api.read.lap.number()
            lap_max = api.read.lap.maximum()
            lap_total = lap_max if api.read.session.lap_type() else "--"
            text_laps = f"{lap_num + data:02.2f}/{lap_total}"[:9]
            target.setText(f"{self.prefix_lap_number}{text_laps: >9}")
            target.setStyleSheet(self.bar_style_lap_number[lap_num - lap_max >= -1])

    def update_position(self, target, place, total, prefix):
        """Driver place & total vehicles"""
        text_pos = f"{place:02.0f}/{total:02.0f}"
        target.setText(f"{prefix}{text_pos: >{self.just_right}}")
