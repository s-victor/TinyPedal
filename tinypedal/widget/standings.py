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
Standings Widget
"""

from functools import partial

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..const import PATH_BRANDLOGO
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "standings"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"]) * 2
        bar_gap = self.wcfg["bar_gap"]
        self.drv_width = max(int(self.wcfg["driver_name_width"]), 1)
        self.veh_width = max(int(self.wcfg["vehicle_name_width"]), 1)
        self.brd_width = max(int(self.wcfg["brand_logo_width"]), 1)
        self.brd_height = max(self.wcfg["font_size"], 1)
        self.cls_width = max(int(self.wcfg["class_width"]), 1)
        self.gap_width = max(int(self.wcfg["time_gap_width"]), 1)
        self.int_width = max(int(self.wcfg["time_interval_width"]), 1)
        self.gap_decimals = max(int(self.wcfg["time_gap_decimal_places"]), 0)
        self.int_decimals = max(int(self.wcfg["time_interval_decimal_places"]), 0)
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )
        self.bar_min_width = partial(calc.qss_min_width, font_width=font_m.width, padding=bar_padx)

        # Max display players
        if self.wcfg["enable_multi_class_split_mode"]:
            self.veh_range = min(max(int(self.wcfg["max_vehicles_split_mode"]), 5), 126)
        else:
            self.veh_range = min(max(int(self.wcfg["max_vehicles_combined_mode"]), 5), 126)

        # Empty data set
        self.empty_vehicles_data = (
            0,  # is_player
            (0,0),  # in_pit
            ("",0),  # position
            ("",0),  # driver name
            ("",0),  # vehicle name
            ("",0),  # pos_class
            ("",0),  # veh_class
            (0,0),  # tire_idx
            ("",0),  # laptime
            ("",0),  # best laptime
            ("",0),  # time_gap
            (-1,0),  # pit_count
            ("",0),  # time_int
        )
        self.pixmap_brandlogo = {"blank": QPixmap()}

        # Create layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)  # remove border
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(bar_gap)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_pos = self.wcfg["column_index_position"]
        column_drv = self.wcfg["column_index_driver"]
        column_veh = self.wcfg["column_index_vehicle"]
        column_brd = self.wcfg["column_index_brand_logo"]
        column_lpt = self.wcfg["column_index_laptime"]
        column_blp = self.wcfg["column_index_best_laptime"]
        column_pic = self.wcfg["column_index_position_in_class"]
        column_cls = self.wcfg["column_index_class"]
        column_tcp = self.wcfg["column_index_tyre_compound"]
        column_psc = self.wcfg["column_index_pitstop_count"]
        column_gap = self.wcfg["column_index_timegap"]
        column_int = self.wcfg["column_index_timeinterval"]
        column_pit = self.wcfg["column_index_pitstatus"]

        # Driver position
        if self.wcfg["show_position"]:
            bar_style_pos = self.bar_min_width(
                2,
                f"color: {self.wcfg['font_color_position']};"
                f"background: {self.wcfg['bkg_color_position']};"
            )
            self.generate_bar("pos", bar_style_pos, column_pos)

        # Driver name
        if self.wcfg["show_driver_name"]:
            bar_style_drv = self.bar_min_width(
                self.drv_width,
                f"color: {self.wcfg['font_color_driver_name']};"
                f"background: {self.wcfg['bkg_color_driver_name']};"
            )
            self.generate_bar("drv", bar_style_drv, column_drv)

        # Vehicle name
        if self.wcfg["show_vehicle_name"]:
            bar_style_veh = self.bar_min_width(
                self.veh_width,
                f"color: {self.wcfg['font_color_vehicle_name']};"
                f"background: {self.wcfg['bkg_color_vehicle_name']};"
            )
            self.generate_bar("veh", bar_style_veh, column_veh)

        # Brand logo
        if self.wcfg["show_brand_logo"]:
            bar_style_brd = (
                f"background: {self.wcfg['bkg_color_brand_logo']};"
                f"min-width: {self.brd_width}px;"
            )
            self.generate_bar("brd", bar_style_brd, column_brd)

        # Time gap
        if self.wcfg["show_time_gap"]:
            bar_style_gap = self.bar_min_width(
                self.gap_width,
                f"color: {self.wcfg['font_color_time_gap']};"
                f"background: {self.wcfg['bkg_color_time_gap']};"
            )
            self.generate_bar("gap", bar_style_gap, column_gap)

        # Time interval
        if self.wcfg["show_time_interval"]:
            bar_style_int = self.bar_min_width(
                self.int_width,
                f"color: {self.wcfg['font_color_time_interval']};"
                f"background: {self.wcfg['bkg_color_time_interval']};"
            )
            self.generate_bar("int", bar_style_int, column_int)

        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            bar_style_lpt = self.bar_min_width(
                8,
                f"color: {self.wcfg['font_color_laptime']};"
                f"background: {self.wcfg['bkg_color_laptime']};"
            )
            self.generate_bar("lpt", bar_style_lpt, column_lpt)

        # Vehicle best laptime
        if self.wcfg["show_best_laptime"]:
            bar_style_blp = self.bar_min_width(
                8,
                f"color: {self.wcfg['font_color_best_laptime']};"
                f"background: {self.wcfg['bkg_color_best_laptime']};"
            )
            self.generate_bar("blp", bar_style_blp, column_blp)

        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_pic = self.bar_min_width(
                2,
                f"color: {self.wcfg['font_color_position_in_class']};"
                f"background: {self.wcfg['bkg_color_position_in_class']};"
            )
            self.generate_bar("pic", bar_style_pic, column_pic)

        # Vehicle class
        if self.wcfg["show_class"]:
            bar_style_cls = self.bar_min_width(
                self.cls_width,
                f"color: {self.wcfg['font_color_class']};"
                f"background: {self.wcfg['bkg_color_class']};"
            )
            self.generate_bar("cls", bar_style_cls, column_cls)

        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            bar_style_pit = self.bar_min_width(
                len(self.wcfg['pit_status_text']),
                f"color: {self.wcfg['font_color_pit']};"
                f"background: {self.wcfg['bkg_color_pit']};"
            )
            self.generate_bar("pit", bar_style_pit, column_pit)

        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcp = self.bar_min_width(
                2,
                f"color: {self.wcfg['font_color_tyre_compound']};"
                f"background: {self.wcfg['bkg_color_tyre_compound']};"
            )
            self.generate_bar("tcp", bar_style_tcp, column_tcp)

        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            bar_style_psc = self.bar_min_width(
                2,
                f"color: {self.wcfg['font_color_pitstop_count']};"
                f"background: {self.wcfg['bkg_color_pitstop_count']};"
            )
            self.generate_bar("psc", bar_style_psc, column_psc)

        # Set layout
        self.setLayout(self.layout)

        # Set widget state & start update
        self.set_widget_state()

    def generate_bar(self, suffix, style, column_idx):
        """Generate data bar"""
        data_slots = len(self.empty_vehicles_data)
        for idx in range(self.veh_range):
            setattr(self, f"row_{idx}_{suffix}", QLabel(""))
            getattr(self, f"row_{idx}_{suffix}").setAlignment(Qt.AlignCenter)
            getattr(self, f"row_{idx}_{suffix}").setStyleSheet(style)
            self.layout.addWidget(
                getattr(self, f"row_{idx}_{suffix}"), idx, column_idx)
            if idx > 0:  # show only first row initially
                getattr(self, f"row_{idx}_{suffix}").setStyleSheet(
                    f"max-height:{self.wcfg['split_gap']}px;"
                )
            # Last data
            setattr(self, f"last_veh_{idx}", [None] * data_slots)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if api.state and minfo.relative.standings:

            standings_idx = minfo.relative.standings
            vehicles_data = minfo.vehicles.dataSet
            total_idx = len(standings_idx)
            total_veh_idx = len(vehicles_data)

            # Standings update
            for idx in range(self.veh_range):

                # Get vehicle data
                if idx < total_idx and 0 <= standings_idx[idx] < total_veh_idx:
                    setattr(self, f"veh_{idx}",
                            self.get_data(standings_idx[idx], vehicles_data)
                            )
                else:  # bypass index out range
                    setattr(self, f"veh_{idx}",
                            self.empty_vehicles_data
                            )
                # Driver position
                if self.wcfg["show_position"]:
                    self.update_pos(f"{idx}_pos",
                                    getattr(self, f"veh_{idx}")[2],
                                    getattr(self, f"last_veh_{idx}")[2],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Driver name
                if self.wcfg["show_driver_name"]:
                    self.update_drv(f"{idx}_drv",
                                    getattr(self, f"veh_{idx}")[3],
                                    getattr(self, f"last_veh_{idx}")[3],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle name
                if self.wcfg["show_vehicle_name"]:
                    self.update_veh(f"{idx}_veh",
                                    getattr(self, f"veh_{idx}")[4],
                                    getattr(self, f"last_veh_{idx}")[4],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Brand logo
                if self.wcfg["show_brand_logo"]:
                    self.update_brd(f"{idx}_brd",
                                    getattr(self, f"veh_{idx}")[4],
                                    getattr(self, f"last_veh_{idx}")[4],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Time gap
                if self.wcfg["show_time_gap"]:
                    self.update_gap(f"{idx}_gap",
                                    getattr(self, f"veh_{idx}")[10],
                                    getattr(self, f"last_veh_{idx}")[10],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Time interval
                if self.wcfg["show_time_interval"]:
                    self.update_int(f"{idx}_int",
                                    getattr(self, f"veh_{idx}")[12],
                                    getattr(self, f"last_veh_{idx}")[12],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(f"{idx}_lpt",
                                    getattr(self, f"veh_{idx}")[8],
                                    getattr(self, f"last_veh_{idx}")[8],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle best laptime
                if self.wcfg["show_best_laptime"]:
                    self.update_blp(f"{idx}_blp",
                                    getattr(self, f"veh_{idx}")[9],
                                    getattr(self, f"last_veh_{idx}")[9],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle position in class
                if self.wcfg["show_position_in_class"]:
                    self.update_pic(f"{idx}_pic",
                                    getattr(self, f"veh_{idx}")[5],
                                    getattr(self, f"last_veh_{idx}")[5],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle class
                if self.wcfg["show_class"]:
                    self.update_cls(f"{idx}_cls",
                                    getattr(self, f"veh_{idx}")[6],
                                    getattr(self, f"last_veh_{idx}")[6]
                                    )
                # Vehicle in pit
                if self.wcfg["show_pit_status"]:
                    self.update_pit(f"{idx}_pit",
                                    getattr(self, f"veh_{idx}")[1],
                                    getattr(self, f"last_veh_{idx}")[1]
                                    )
                # Tyre compound index
                if self.wcfg["show_tyre_compound"]:
                    self.update_tcp(f"{idx}_tcp",
                                    getattr(self, f"veh_{idx}")[7],
                                    getattr(self, f"last_veh_{idx}")[7],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(f"{idx}_psc",
                                    getattr(self, f"veh_{idx}")[11],
                                    getattr(self, f"last_veh_{idx}")[11],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Store last data reading
                setattr(self, f"last_veh_{idx}", getattr(self, f"veh_{idx}"))

    # GUI update methods
    def update_pos(self, suffix, curr, last, isplayer):
        """Driver position"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_position']};"
                         f"background: {self.wcfg['bkg_color_player_position']};")
            else:
                color = (f"color: {self.wcfg['font_color_position']};"
                         f"background: {self.wcfg['bkg_color_position']};")

            getattr(self, f"row_{suffix}").setText(curr[0])
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(2, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_drv(self, suffix, curr, last, isplayer):
        """Driver name"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_driver_name']};"
                         f"background: {self.wcfg['bkg_color_player_driver_name']};")
            else:
                color = (f"color: {self.wcfg['font_color_driver_name']};"
                         f"background: {self.wcfg['bkg_color_driver_name']};")

            if self.wcfg["driver_name_shorten"]:
                text = fmt.shorten_driver_name(curr[0])
            else:
                text = curr[0]

            if self.wcfg["driver_name_uppercase"]:
                text = text.upper()

            if self.wcfg["driver_name_align_center"]:
                text = text[:self.drv_width]
            else:
                text = text[:self.drv_width].ljust(self.drv_width)

            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(self.drv_width, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_veh(self, suffix, curr, last, isplayer):
        """Vehicle name"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_vehicle_name']};"
                         f"background: {self.wcfg['bkg_color_player_vehicle_name']};")
            else:
                color = (f"color: {self.wcfg['font_color_vehicle_name']};"
                         f"background: {self.wcfg['bkg_color_vehicle_name']};")

            if self.wcfg["show_vehicle_brand_as_name"]:
                vname = self.cfg.user.brands.get(curr[0], curr[0])
            else:
                vname = curr[0]

            if self.wcfg["vehicle_name_uppercase"]:
                text = vname.upper()
            else:
                text = vname

            if self.wcfg["vehicle_name_align_center"]:
                text = text[:self.veh_width]
            else:
                text = text[:self.veh_width].ljust(self.veh_width)

            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(self.veh_width, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_brd(self, suffix, curr, last, isplayer):
        """Brand logo"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = f"background: {self.wcfg['bkg_color_player_brand_logo']};"
            else:
                color = f"background: {self.wcfg['bkg_color_brand_logo']};"

            if curr[0]:
                brand_name = self.cfg.user.brands.get(curr[0], curr[0])
            else:
                brand_name = "blank"
            # Draw brand logo
            getattr(self, f"row_{suffix}").setPixmap(self.load_brand_logo(brand_name))
            # Draw background
            getattr(self, f"row_{suffix}").setStyleSheet(f"{color}min-width: {self.brd_width}px;")
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_gap(self, suffix, curr, last, isplayer):
        """Time gap"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_time_gap']};"
                         f"background: {self.wcfg['bkg_color_player_time_gap']};")
            else:
                color = (f"color: {self.wcfg['font_color_time_gap']};"
                         f"background: {self.wcfg['bkg_color_time_gap']};")

            getattr(self, f"row_{suffix}").setText(
                curr[0][:self.gap_width].strip("."))
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(self.gap_width, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_int(self, suffix, curr, last, isplayer):
        """Time interval"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_time_interval']};"
                         f"background: {self.wcfg['bkg_color_player_time_interval']};")
            else:
                color = (f"color: {self.wcfg['font_color_time_interval']};"
                         f"background: {self.wcfg['bkg_color_time_interval']};")

            getattr(self, f"row_{suffix}").setText(
                curr[0][:self.int_width].strip("."))
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(self.int_width, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_lpt(self, suffix, curr, last, isplayer):
        """Vehicle laptime"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_laptime']};"
                         f"background: {self.wcfg['bkg_color_player_laptime']};")
            else:
                color = (f"color: {self.wcfg['font_color_laptime']};"
                         f"background: {self.wcfg['bkg_color_laptime']};")

            getattr(self, f"row_{suffix}").setText(curr[0])
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(8, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_blp(self, suffix, curr, last, isplayer):
        """Vehicle best laptime"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_best_laptime']};"
                         f"background: {self.wcfg['bkg_color_player_best_laptime']};")
            else:
                color = (f"color: {self.wcfg['font_color_best_laptime']};"
                         f"background: {self.wcfg['bkg_color_best_laptime']};")

            getattr(self, f"row_{suffix}").setText(curr[0])
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(8, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_pic(self, suffix, curr, last, isplayer):
        """Position in class"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_position_in_class']};"
                         f"background: {self.wcfg['bkg_color_player_position_in_class']};")
            else:
                color = (f"color: {self.wcfg['font_color_position_in_class']};"
                         f"background: {self.wcfg['bkg_color_position_in_class']};")

            getattr(self, f"row_{suffix}").setText(curr[0])
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(2, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_cls(self, suffix, curr, last):
        """Vehicle class"""
        if curr != last:
            text, bg_color = self.set_class_style(curr[0])
            color = (f"color: {self.wcfg['font_color_class']};"
                     f"background: {bg_color};")

            getattr(self, f"row_{suffix}").setText(text[:self.cls_width])
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(self.cls_width, color))
            self.toggle_visibility(curr[0], getattr(self, f"row_{suffix}"))

    def update_pit(self, suffix, curr, last):
        """Vehicle in pit"""
        if curr != last:
            text, bg_color = self.set_pitstatus(curr[0])
            color = (f"color: {self.wcfg['font_color_pit']};"
                     f"background: {bg_color};")

            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(len(text), color))
            self.toggle_visibility(text, getattr(self, f"row_{suffix}"))

    def update_tcp(self, suffix, curr, last, isplayer):
        """Tyre compound index"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_tyre_compound']};"
                         f"background: {self.wcfg['bkg_color_player_tyre_compound']};")
            else:
                color = (f"color: {self.wcfg['font_color_tyre_compound']};"
                         f"background: {self.wcfg['bkg_color_tyre_compound']};")

            text = self.set_tyre_cmp(curr[0])
            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(2, color))
            self.toggle_visibility(text, getattr(self, f"row_{suffix}"))

    def update_psc(self, suffix, curr, last, isplayer):
        """Pitstop count"""
        if curr != last:
            if self.wcfg["show_pit_request"] and curr[1] == 1:
                color = (f"color: {self.wcfg['font_color_pit_request']};"
                         f"background: {self.wcfg['bkg_color_pit_request']};")
            elif self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_pitstop_count']};"
                         f"background: {self.wcfg['bkg_color_player_pitstop_count']};")
            else:
                color = (f"color: {self.wcfg['font_color_pitstop_count']};"
                         f"background: {self.wcfg['bkg_color_pitstop_count']};")

            text = self.set_pitcount(curr[0])
            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(self.bar_min_width(2, color))
            self.toggle_visibility(text, getattr(self, f"row_{suffix}"))

    # Additional methods
    def toggle_visibility(self, state, row_bar):
        """Hide row bar if empty data"""
        if self.wcfg["split_gap"] > 0:
            if not state:  # add gap between non-empty data
                row_bar.setStyleSheet(f"max-height:{self.wcfg['split_gap']}px;")
        else:  # workaround to 1px minimum bar height limit
            if state:
                if row_bar.isHidden():
                    row_bar.show()
            else:
                if not row_bar.isHidden():
                    row_bar.hide()

    def load_brand_logo(self, brand_name):
        """Load brand logo"""
        # Load cached logo
        if brand_name in self.pixmap_brandlogo:
            return self.pixmap_brandlogo[brand_name]
        # Add available logo to cached
        if brand_name in self.cfg.user.brands_logo:
            logo_temp = QPixmap(f"{PATH_BRANDLOGO}{brand_name}.png")
            if calc.image_size_adaption(
                logo_temp.width(), logo_temp.height(), self.brd_width, self.brd_height):
                logo_image = logo_temp.scaledToWidth(  # adapt to width
                    self.brd_width, mode=Qt.SmoothTransformation)
            else:
                logo_image = logo_temp.scaledToHeight(  # adapt to height
                    self.brd_height, mode=Qt.SmoothTransformation)
            self.pixmap_brandlogo[brand_name] = logo_image
            return self.pixmap_brandlogo[brand_name]
        # Load blank logo if unavailable
        return self.pixmap_brandlogo["blank"]

    def set_tyre_cmp(self, tc_indices):
        """Substitute tyre compound index with custom chars"""
        if tc_indices:
            return "".join((self.tyre_compound_string[idx] for idx in tc_indices))
        return ""

    def set_pitstatus(self, pits):
        """Set pit status color"""
        if pits > 0:
            return self.wcfg["pit_status_text"], self.wcfg["bkg_color_pit"]
        return "", "#00000000"

    @staticmethod
    def set_pitcount(pits):
        """Set pitstop count test"""
        if pits == 0:
            return "-"
        if pits > 0:
            return f"{pits}"
        return ""

    def set_class_style(self, vehclass_name):
        """Compare vehicle class name with user defined dictionary"""
        if vehclass_name in self.cfg.user.classes:
            return tuple(*self.cfg.user.classes[vehclass_name].items())  # sub_name, sub_color
        if vehclass_name and self.wcfg["show_random_color_for_unknown_class"]:
            return vehclass_name, fmt.random_color_class(vehclass_name)
        return vehclass_name, self.wcfg["bkg_color_class"]

    @staticmethod
    def set_laptime(inpit, laptime_last, pit_time):
        """Set lap time"""
        if inpit:
            return "PIT" + f"{pit_time:.1f}"[:5].rjust(5) if pit_time > 0 else "-:--.---"
        if laptime_last <= 0:
            return "OUT" + f"{pit_time:.1f}"[:5].rjust(5) if pit_time > 0 else "-:--.---"
        return calc.sec2laptime_full(laptime_last)[:8].rjust(8)

    @staticmethod
    def set_best_laptime(laptime_best):
        """Set best lap time"""
        if laptime_best <= 0:
            return "-:--.---"
        return calc.sec2laptime_full(laptime_best)[:8].rjust(8)

    def gap_to_session_bestlap(self, bestlap, sbestlap, cbestlap):
        """Gap to session best laptime"""
        if self.wcfg["show_time_gap_from_class_best"]:
            time = bestlap - cbestlap  # class best
        else:
            time = bestlap - sbestlap  # session best
        if time == 0 and bestlap > 0:
            return self.wcfg["time_gap_leader_text"]
        if time < 0 or bestlap < 1:  # no time set
            return "0.0"
        return f"{time:.{self.gap_decimals}f}"

    def gap_to_leader_race(self, gap_behind, position):
        """Gap to race leader"""
        if position == 1:
            return self.wcfg["time_gap_leader_text"]
        if isinstance(gap_behind, int):
            return f"{gap_behind:.0f}L"
        return f"{gap_behind:.{self.gap_decimals}f}"

    def int_to_next(self, gap_behind_class, gap_behind, position_class, position):
        """Interval to next"""
        if (self.wcfg["enable_multi_class_split_mode"]
            and self.wcfg["show_time_interval_from_same_class"]):
            pos = position_class
            gap = gap_behind_class
        else:
            pos = position
            gap = gap_behind
        if pos == 1:
            return self.wcfg["time_interval_leader_text"]
        if isinstance(gap, int):
            return f"{gap:.0f}L"
        return f"{gap:.{self.int_decimals}f}"

    def get_data(self, index, vehicles_data):
        """Standings data"""
        # 0 Is player
        is_player = vehicles_data[index].isPlayer

        # 1 Vehicle in pit
        in_pit = (vehicles_data[index].inPit, is_player)

        # 2 Driver position
        position = (f"{vehicles_data[index].position:02d}", is_player)

        # 3 Driver name
        drv_name = (vehicles_data[index].driverName, is_player)

        # 4 Vehicle name
        veh_name = (vehicles_data[index].vehicleName, is_player)

        # 5 Vehicle position in class
        pos_class = (f"{vehicles_data[index].positionInClass:02d}", is_player)

        # 6 Vehicle class
        veh_class = (vehicles_data[index].vehicleClass, is_player)

        # 7 Tyre compound index
        tire_idx = (vehicles_data[index].tireCompound, is_player)

        in_race = api.read.session.in_race()

        # 8 Lap time (last)
        if self.wcfg["show_best_laptime"] or in_race:
            laptime = (
                self.set_laptime(
                    vehicles_data[index].inPit,
                    vehicles_data[index].lastLapTime,
                    vehicles_data[index].pitTime
                ),
                is_player)
        else:
            laptime = (
                self.set_laptime(
                    0,
                    vehicles_data[index].bestLapTime,
                    0
                ),
                is_player)

        # 9 Best lap time
        best_laptime = (
            self.set_best_laptime(vehicles_data[index].bestLapTime),
            is_player)

        # 10 Time gap
        if in_race:
            time_gap = (
                self.gap_to_leader_race(
                    vehicles_data[index].gapBehindLeader,
                    vehicles_data[index].position
                ),
                is_player)
        else:
            time_gap = (
                self.gap_to_session_bestlap(
                    vehicles_data[index].bestLapTime,
                    vehicles_data[index].sessionBestLapTime,
                    vehicles_data[index].classBestLapTime,
                ),
                is_player)

        # 11 Pitstop count
        pit_count = (vehicles_data[index].numPitStops,
                    vehicles_data[index].pitState,
                    is_player)

        # 12 Time interval
        time_int = (
            self.int_to_next(
                vehicles_data[index].gapBehindNextInClass,
                vehicles_data[index].gapBehindNext,
                vehicles_data[index].positionInClass,
                vehicles_data[index].position,
            ),
            is_player)

        return (is_player, in_pit, position, drv_name, veh_name, pos_class, veh_class,
                tire_idx, laptime, best_laptime, time_gap, pit_count, time_int)
