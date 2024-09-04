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
Rivals Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..const import PATH_BRANDLOGO
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "rivals"


class Realtime(Overlay):
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
        self.int_width = max(int(self.wcfg["time_interval_width"]), 1)
        self.int_decimals = max(int(self.wcfg["time_interval_decimal_places"]), 0)
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Max display players
        self.veh_range = 2

        # Empty data set
        self.empty_vehicles_data = (
            0,  # in_pit
            "",  # position
            "",  # driver name
            "",  # vehicle name
            "",  # pos_class
            "",  # veh_class
            "",  # tire_idx
            "",  # laptime
            "",  # best laptime
            (-1,0),  # pit_count
            ("",0),  # time_int
        )
        self.pixmap_brandlogo = {"blank": QPixmap()}
        self.data_bar = {}
        self.curr_data = [None] * self.veh_range
        self.last_data = [tuple(None for _ in self.empty_vehicles_data)] * self.veh_range

        # Create layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)  # remove border
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(bar_gap)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(self.layout)

        # Driver position
        if self.wcfg["show_position"]:
            bar_style_pos = self.qss_color(
                self.wcfg["font_color_position"],
                self.wcfg["bkg_color_position"]
            )
            self.generate_bar(
                "pos", bar_style_pos, self.wcfg["column_index_position"],
                2 * font_m.width + bar_padx
            )
        # Driver name
        if self.wcfg["show_driver_name"]:
            bar_style_drv = self.qss_color(
                self.wcfg["font_color_driver_name"],
                self.wcfg["bkg_color_driver_name"]
            )
            self.generate_bar(
                "drv", bar_style_drv, self.wcfg["column_index_driver"],
                self.drv_width * font_m.width + bar_padx
            )
        # Vehicle name
        if self.wcfg["show_vehicle_name"]:
            bar_style_veh = self.qss_color(
                self.wcfg["font_color_vehicle_name"],
                self.wcfg["bkg_color_vehicle_name"]
            )
            self.generate_bar(
                "veh", bar_style_veh, self.wcfg["column_index_vehicle"],
                self.veh_width * font_m.width + bar_padx
            )
        # Brand logo
        if self.wcfg["show_brand_logo"]:
            bar_style_brd = self.qss_color(
                self.wcfg["bkg_color_brand_logo"],
                self.wcfg["bkg_color_brand_logo"]
            )
            self.generate_bar(
                "brd", bar_style_brd, self.wcfg["column_index_brand_logo"],
                self.brd_width
            )
        # Time interval
        if self.wcfg["show_time_interval"]:
            self.bar_style_int = (
                self.qss_color(
                    self.wcfg["font_color_time_interval_behind"],
                    self.wcfg["bkg_color_time_interval_behind"]),
                self.qss_color(
                    self.wcfg["font_color_time_interval_ahead"],
                    self.wcfg["bkg_color_time_interval_ahead"])
            )
            self.generate_bar(
                "int", self.bar_style_int[0], self.wcfg["column_index_timeinterval"],
                self.int_width * font_m.width + bar_padx
            )
        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            bar_style_lpt = self.qss_color(
                self.wcfg["font_color_laptime"],
                self.wcfg["bkg_color_laptime"]
            )
            self.generate_bar(
                "lpt", bar_style_lpt, self.wcfg["column_index_laptime"],
                8 * font_m.width + bar_padx
            )
        # Vehicle best laptime
        if self.wcfg["show_best_laptime"]:
            bar_style_blp = self.qss_color(
                self.wcfg["font_color_best_laptime"],
                self.wcfg["bkg_color_best_laptime"]
            )
            self.generate_bar(
                "blp", bar_style_blp, self.wcfg["column_index_best_laptime"],
                8 * font_m.width + bar_padx
            )
        # Position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_pic = self.qss_color(
                self.wcfg["font_color_position_in_class"],
                self.wcfg["bkg_color_position_in_class"]
            )
            self.generate_bar(
                "pic", bar_style_pic, self.wcfg["column_index_position_in_class"],
                2 * font_m.width + bar_padx
            )
        # Vehicle class
        if self.wcfg["show_class"]:
            bar_style_cls = self.qss_color(
                self.wcfg["font_color_class"],
                self.wcfg["bkg_color_class"]
            )
            self.generate_bar(
                "cls", bar_style_cls, self.wcfg["column_index_class"],
                self.cls_width * font_m.width + bar_padx
            )
        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            self.bar_style_pit = (
                self.qss_color("#00000000", "#00000000"),
                self.qss_color(
                    self.wcfg["font_color_pit"],
                    self.wcfg["bkg_color_pit"])
            )
            self.generate_bar(
                "pit", self.bar_style_pit[1], self.wcfg["column_index_pitstatus"],
                len(self.wcfg["pit_status_text"]) * font_m.width + bar_padx
            )
        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcp = self.qss_color(
                self.wcfg["font_color_tyre_compound"],
                self.wcfg["bkg_color_tyre_compound"]
            )
            self.generate_bar(
                "tcp", bar_style_tcp, self.wcfg["column_index_tyre_compound"],
                2 * font_m.width + bar_padx
            )
        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            self.bar_style_psc = (
                self.qss_color(
                    self.wcfg["font_color_pitstop_count"],
                    self.wcfg["bkg_color_pitstop_count"]),
                self.qss_color(
                    self.wcfg["font_color_pit_request"],
                    self.wcfg["bkg_color_pit_request"])
            )
            self.generate_bar(
                "psc", self.bar_style_psc[0], self.wcfg["column_index_pitstop_count"],
                2 * font_m.width + bar_padx
            )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            player_idx = api.read.vehicle.player_index()
            vehicles_data = minfo.vehicles.dataSet
            total_idx = len(minfo.relative.classes)
            total_veh_idx = len(vehicles_data)
            in_race = api.read.session.in_race()

            if player_idx < total_idx:
                rivals_list = minfo.relative.classes[player_idx][5:7]
            else:
                rivals_list = -1,-1

            # Standings update
            for idx in range(self.veh_range):

                # Get vehicle data
                if 0 <= rivals_list[idx] < total_veh_idx:
                    self.curr_data[idx] = self.get_data(
                        rivals_list[idx], player_idx, vehicles_data, in_race)
                elif self.last_data[idx] == self.empty_vehicles_data:
                    continue  # skip if already empty
                else:
                    self.curr_data[idx] = self.empty_vehicles_data
                # Driver position
                if self.wcfg["show_position"]:
                    self.update_pos(self.data_bar[f"row_{idx}_pos"],
                                    self.curr_data[idx][1],
                                    self.last_data[idx][1],
                                    )
                # Driver name
                if self.wcfg["show_driver_name"]:
                    self.update_drv(self.data_bar[f"row_{idx}_drv"],
                                    self.curr_data[idx][2],
                                    self.last_data[idx][2],
                                    )
                # Vehicle name
                if self.wcfg["show_vehicle_name"]:
                    self.update_veh(self.data_bar[f"row_{idx}_veh"],
                                    self.curr_data[idx][3],
                                    self.last_data[idx][3],
                                    )
                # Brand logo
                if self.wcfg["show_brand_logo"]:
                    self.update_brd(self.data_bar[f"row_{idx}_brd"],
                                    self.curr_data[idx][3],
                                    self.last_data[idx][3]
                                    )
                # Time interval
                if self.wcfg["show_time_interval"]:
                    self.update_int(self.data_bar[f"row_{idx}_int"],
                                    self.curr_data[idx][10],
                                    self.last_data[idx][10],
                                    )
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(self.data_bar[f"row_{idx}_lpt"],
                                    self.curr_data[idx][7],
                                    self.last_data[idx][7],
                                    )
                # Vehicle best laptime
                if self.wcfg["show_best_laptime"]:
                    self.update_blp(self.data_bar[f"row_{idx}_blp"],
                                    self.curr_data[idx][8],
                                    self.last_data[idx][8],
                                    )
                # Position in class
                if self.wcfg["show_position_in_class"]:
                    self.update_pic(self.data_bar[f"row_{idx}_pic"],
                                    self.curr_data[idx][4],
                                    self.last_data[idx][4],
                                    )
                # Vehicle class
                if self.wcfg["show_class"]:
                    self.update_cls(self.data_bar[f"row_{idx}_cls"],
                                    self.curr_data[idx][5],
                                    self.last_data[idx][5],
                                    )
                # Vehicle in pit
                if self.wcfg["show_pit_status"]:
                    self.update_pit(self.data_bar[f"row_{idx}_pit"],
                                    self.curr_data[idx][0],
                                    self.last_data[idx][0],
                                    )
                # Tyre compound index
                if self.wcfg["show_tyre_compound"]:
                    self.update_tcp(self.data_bar[f"row_{idx}_tcp"],
                                    self.curr_data[idx][6],
                                    self.last_data[idx][6],
                                    )
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(self.data_bar[f"row_{idx}_psc"],
                                    self.curr_data[idx][9],
                                    self.last_data[idx][9],
                                    )
                # Store last data reading
                self.last_data[idx] = self.curr_data[idx]

    # GUI update methods
    def update_pos(self, target_bar, curr, last):
        """Driver position"""
        if curr != last:
            if curr != "":
                text = f"{curr:02d}"
            else:
                text = ""

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_drv(self, target_bar, curr, last):
        """Driver name"""
        if curr != last:
            if self.wcfg["driver_name_shorten"]:
                text = fmt.shorten_driver_name(curr)
            else:
                text = curr

            if self.wcfg["driver_name_uppercase"]:
                text = text.upper()

            if self.wcfg["driver_name_align_center"]:
                text = text[:self.drv_width]
            else:
                text = text[:self.drv_width].ljust(self.drv_width)

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_veh(self, target_bar, curr, last):
        """Vehicle name"""
        if curr != last:
            if self.wcfg["show_vehicle_brand_as_name"]:
                vname = self.cfg.user.brands.get(curr, curr)
            else:
                vname = curr

            if self.wcfg["vehicle_name_uppercase"]:
                text = vname.upper()
            else:
                text = vname

            if self.wcfg["vehicle_name_align_center"]:
                text = text[:self.veh_width]
            else:
                text = text[:self.veh_width].ljust(self.veh_width)

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_brd(self, target_bar, curr, last):
        """Brand logo"""
        if curr != last:
            if curr:
                brand_name = self.cfg.user.brands.get(curr, curr)
            else:
                brand_name = "blank"
            # Draw brand logo
            target_bar.setPixmap(self.load_brand_logo(brand_name))
            self.toggle_visibility(curr, target_bar)

    def update_int(self, target_bar, curr, last):
        """Time interval"""
        if curr != last:
            if curr[0] != "":
                text = self.int_to_next(curr[0], curr[1])[
                    :self.int_width].strip(".").rjust(self.int_width)
            else:
                text = ""

            target_bar.setText(text)
            target_bar.setStyleSheet(self.bar_style_int[curr[1]])
            self.toggle_visibility(text, target_bar)

    def update_lpt(self, target_bar, curr, last):
        """Vehicle laptime"""
        if curr != last:
            if curr != "":
                text = self.set_laptime(*curr)
            else:
                text = ""

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_blp(self, target_bar, curr, last):
        """Vehicle best laptime"""
        if curr != last:
            if curr != "":
                text = self.set_best_laptime(curr)
            else:
                text = ""

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_pic(self, target_bar, curr, last):
        """Position in class"""
        if curr != last:
            if curr != "":
                text = f"{curr:02d}"
            else:
                text = ""

            target_bar.setText(text)
            self.toggle_visibility(curr, target_bar)

    def update_cls(self, target_bar, curr, last):
        """Vehicle class"""
        if curr != last:
            text, bg_color = self.set_class_style(curr)
            target_bar.setText(text[:self.cls_width])
            target_bar.setStyleSheet(
                f"color: {self.wcfg['font_color_class']};background: {bg_color};")
            self.toggle_visibility(curr, target_bar)

    def update_pit(self, target_bar, curr, last):
        """Vehicle in pit"""
        if curr != last:
            if curr:
                text = self.wcfg["pit_status_text"]
            else:
                text = ""

            target_bar.setText(text)
            target_bar.setStyleSheet(self.bar_style_pit[curr])
            self.toggle_visibility(text, target_bar)

    def update_tcp(self, target_bar, curr, last):
        """Tyre compound index"""
        if curr != last:
            text = self.set_tyre_cmp(curr)
            target_bar.setText(text)
            self.toggle_visibility(text, target_bar)

    def update_psc(self, target_bar, curr, last):
        """Pitstop count"""
        if curr != last:
            text = self.set_pitcount(curr[0])
            target_bar.setText(text)
            target_bar.setStyleSheet(
                self.bar_style_psc[self.wcfg["show_pit_request"] and curr[1] == 1])
            self.toggle_visibility(text, target_bar)

    # GUI generate methods
    def generate_bar(self, suffix, style, column_idx, bar_width):
        """Generate bar set"""
        for idx in range(self.veh_range):
            bar_name = f"row_{idx}_{suffix}"
            self.data_bar[bar_name] = QLabel("")
            self.data_bar[bar_name].setAlignment(Qt.AlignCenter)
            self.data_bar[bar_name].setStyleSheet(style)
            self.data_bar[bar_name].setMinimumWidth(bar_width)
            self.layout.addWidget(self.data_bar[bar_name], idx, column_idx)
            if idx > 0:  # show only first row initially
                self.data_bar[bar_name].hide()

    # Additional methods
    @staticmethod
    def toggle_visibility(state, row_bar):
        """Hide row bar if empty data"""
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

    def int_to_next(self, gap_behind_class, is_ahead):
        """Interval to next"""
        if isinstance(gap_behind_class, int):
            return f"{'+-'[is_ahead]}{gap_behind_class:.0f}L"
        return f"{'+-'[is_ahead]}{gap_behind_class:.{self.int_decimals}f}"

    def get_data(self, index, player_idx, vehicles_data, in_race):
        """Standings data"""
        # 0 Vehicle in pit (in_pit: bool)
        in_pit = vehicles_data[index].inPit

        # 1 Driver position (position: int)
        position = vehicles_data[index].position

        # 2 Driver name (drv_name: str)
        drv_name = vehicles_data[index].driverName

        # 3 Vehicle name (veh_name: str)
        veh_name = vehicles_data[index].vehicleName

        # 4 Position in class (pos_class: int)
        pos_class = vehicles_data[index].positionInClass

        # 5 Vehicle class (veh_class: str)
        veh_class = vehicles_data[index].vehicleClass

        # 6 Tyre compound index (tire_idx: tuple)
        tire_idx = vehicles_data[index].tireCompound

        # 7 Lap time (laptime: tuple)
        if self.wcfg["show_best_laptime"] or in_race:
            laptime = (
                    vehicles_data[index].inPit,
                    vehicles_data[index].lastLapTime,
                    vehicles_data[index].pitTime
                )
        else:
            laptime = (
                    0,
                    vehicles_data[index].bestLapTime,
                    0
                )

        # 8 Best lap time (best_laptime: float)
        best_laptime = vehicles_data[index].bestLapTime

        # 9 Pitstop count (pit_count: int, pit_state: int)
        pit_count = (
            vehicles_data[index].numPitStops,
            vehicles_data[index].pitState)

        # 10 Time interval (time_int: float, is_ahead)
        is_ahead = vehicles_data[index].position < vehicles_data[player_idx].position
        time_int = (vehicles_data[player_idx if is_ahead else index].gapBehindNextInClass, is_ahead)

        return (in_pit, position, drv_name, veh_name, pos_class, veh_class,
                tire_idx, laptime, best_laptime, pit_count, time_int)
