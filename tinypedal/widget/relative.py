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
Relative Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import formatter as fmt
from ..const import PATH_BRANDLOGO
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "relative"


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
        self.gap_width = max(int(self.wcfg["time_gap_width"]), 1)
        self.gap_decimals = max(int(self.wcfg["time_gap_decimal_places"]), 0)
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")
        self.hiplayer = self.wcfg["show_player_highlighted"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
        )

        # Max display players
        veh_add_front = min(max(int(self.wcfg["additional_players_front"]), 0), 60)
        veh_add_behind = min(max(int(self.wcfg["additional_players_behind"]), 0), 60)
        self.veh_range = max(7 + veh_add_front + veh_add_behind, 7)

        # Empty data set
        self.empty_vehicles_data = (
            0,  # is_player
            0,  # in_pit
            ("",0),  # position
            ("",0),  # driver name
            ("",0),  # vehicle name
            "",  # pos_class
            "",  # veh_class
            ("",0),  # time_gap
            "",  # tire_idx
            "",  # laptime
            (-1,0)  # pit_count
        )
        self.pixmap_brandlogo = {"blank": QPixmap()}
        self.data_bar = {}
        self.curr_data = [None] * self.veh_range
        self.last_data = [self.empty_vehicles_data] * self.veh_range

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
            self.bar_style_brd = (
                f"background: {self.wcfg['bkg_color_brand_logo']};",
                f"background: {self.wcfg['bkg_color_player_brand_logo']};"
            )
            self.generate_bar(
                "brd", self.bar_style_brd[0], self.wcfg["column_index_brand_logo"],
                self.brd_width
            )
        # Time gap
        if self.wcfg["show_time_gap"]:
            bar_style_gap = self.qss_color(
                self.wcfg["font_color_time_gap"],
                self.wcfg["bkg_color_time_gap"]
            )
            self.generate_bar(
                "gap", bar_style_gap, self.wcfg["column_index_timegap"],
                self.gap_width * font_m.width + bar_padx
            )
        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            self.bar_style_lpt = (
                self.qss_color(
                    self.wcfg["font_color_laptime"],
                    self.wcfg["bkg_color_laptime"]),
                self.qss_color(
                    self.wcfg["font_color_player_laptime"],
                    self.wcfg["bkg_color_player_laptime"])
            )
            self.generate_bar(
                "lpt", self.bar_style_lpt[0], self.wcfg["column_index_laptime"],
                8 * font_m.width + bar_padx
            )
        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            self.bar_style_pic = (
                self.qss_color(
                    self.wcfg["font_color_position_in_class"],
                    self.wcfg["bkg_color_position_in_class"]),
                self.qss_color(
                    self.wcfg["font_color_player_position_in_class"],
                    self.wcfg["bkg_color_player_position_in_class"])
            )
            self.generate_bar(
                "pic", self.bar_style_pic[0], self.wcfg["column_index_position_in_class"],
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
            bar_style_pit = self.qss_color(
                self.wcfg["font_color_pit"],
                self.wcfg["bkg_color_pit"]
            )
            self.generate_bar(
                "pit", bar_style_pit, self.wcfg["column_index_pitstatus"],
                len(self.wcfg["pit_status_text"]) * font_m.width + bar_padx
            )
        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            self.bar_style_tcp = (
                self.qss_color(
                    self.wcfg["font_color_tyre_compound"],
                    self.wcfg["bkg_color_tyre_compound"]),
                self.qss_color(
                    self.wcfg["font_color_player_tyre_compound"],
                    self.wcfg["bkg_color_player_tyre_compound"])
            )
            self.generate_bar(
                "tcp", self.bar_style_tcp[0], self.wcfg["column_index_tyre_compound"],
                2 * font_m.width + bar_padx
            )
        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            self.bar_style_psc = (
                self.qss_color(
                    self.wcfg["font_color_pitstop_count"],
                    self.wcfg["bkg_color_pitstop_count"]),
                self.qss_color(
                    self.wcfg["font_color_player_pitstop_count"],
                    self.wcfg["bkg_color_player_pitstop_count"]),
                self.qss_color(
                    self.wcfg["font_color_pit_request"],
                    self.wcfg["bkg_color_pit_request"])
            )
            self.generate_bar(
                "psc", self.bar_style_psc[0], self.wcfg["column_index_pitstop_count"],
                2 * font_m.width + bar_padx
            )

    def generate_bar(self, suffix, style, column_idx, bar_width):
        """Generate data bar"""
        for idx in range(self.veh_range):
            bar_name = f"row_{idx}_{suffix}"
            self.data_bar[bar_name] = QLabel("")
            self.data_bar[bar_name].setAlignment(Qt.AlignCenter)
            self.data_bar[bar_name].setStyleSheet(style)
            self.data_bar[bar_name].setMinimumWidth(bar_width)
            self.layout.addWidget(
                self.data_bar[bar_name], idx, column_idx)

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active and minfo.relative.relative:

            relative_idx = minfo.relative.relative
            vehicles_data = minfo.vehicles.dataSet
            total_idx = len(relative_idx)
            total_veh_idx = len(vehicles_data)

            # Relative update
            for idx in range(self.veh_range):

                # Get vehicle data
                if idx < total_idx and 0 <= relative_idx[idx] < total_veh_idx:
                    self.curr_data[idx] = self.get_data(
                        relative_idx[idx], vehicles_data)
                else:  # bypass index out range
                    self.curr_data[idx] = self.empty_vehicles_data
                # Driver position
                if self.wcfg["show_position"]:
                    self.update_pos(self.data_bar[f"row_{idx}_pos"],
                                    self.curr_data[idx][2],
                                    self.last_data[idx][2],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Driver name
                if self.wcfg["show_driver_name"]:
                    self.update_drv(self.data_bar[f"row_{idx}_drv"],
                                    self.curr_data[idx][3],
                                    self.last_data[idx][3],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Vehicle name
                if self.wcfg["show_vehicle_name"]:
                    self.update_veh(self.data_bar[f"row_{idx}_veh"],
                                    self.curr_data[idx][4],
                                    self.last_data[idx][4],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Brand logo
                if self.wcfg["show_brand_logo"]:
                    self.update_brd(self.data_bar[f"row_{idx}_brd"],
                                    self.curr_data[idx][4],
                                    self.last_data[idx][4],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Time gap
                if self.wcfg["show_time_gap"]:
                    self.update_gap(self.data_bar[f"row_{idx}_gap"],
                                    self.curr_data[idx][7],
                                    self.last_data[idx][7],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(self.data_bar[f"row_{idx}_lpt"],
                                    self.curr_data[idx][9],
                                    self.last_data[idx][9],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Vehicle position in class
                if self.wcfg["show_position_in_class"]:
                    self.update_pic(self.data_bar[f"row_{idx}_pic"],
                                    self.curr_data[idx][5],
                                    self.last_data[idx][5],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Vehicle class
                if self.wcfg["show_class"]:
                    self.update_cls(self.data_bar[f"row_{idx}_cls"],
                                    self.curr_data[idx][6],
                                    self.last_data[idx][6]
                                    )
                # Vehicle in pit
                if self.wcfg["show_pit_status"]:
                    self.update_pit(self.data_bar[f"row_{idx}_pit"],
                                    self.curr_data[idx][1],
                                    self.last_data[idx][1]
                                    )
                # Tyre compound index
                if self.wcfg["show_tyre_compound"]:
                    self.update_tcp(self.data_bar[f"row_{idx}_tcp"],
                                    self.curr_data[idx][8],
                                    self.last_data[idx][8],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(self.data_bar[f"row_{idx}_psc"],
                                    self.curr_data[idx][10],
                                    self.last_data[idx][10],
                                    self.curr_data[idx][0]  # is_player
                                    )
                # Store last data reading
                self.last_data[idx] = self.curr_data[idx]

    # GUI update methods
    def update_pos(self, target_bar, curr, last, isplayer):
        """Driver position"""
        if curr != last:
            if self.hiplayer and isplayer:
                color = (f"color: {self.wcfg['font_color_player_position']};"
                         f"background: {self.wcfg['bkg_color_player_position']};")
            elif self.wcfg["show_lap_difference"]:
                color = (f"color: {self.color_lap_diff(curr[1])};"
                         f"background: {self.wcfg['bkg_color_position']};")
            else:
                color = (f"color: {self.wcfg['font_color_position']};"
                         f"background: {self.wcfg['bkg_color_position']};")

            target_bar.setText(curr[0])
            target_bar.setStyleSheet(color)

    def update_drv(self, target_bar, curr, last, isplayer):
        """Driver name"""
        if curr != last:
            if self.hiplayer and isplayer:
                color = (f"color: {self.wcfg['font_color_player_driver_name']};"
                         f"background: {self.wcfg['bkg_color_player_driver_name']};")
            elif self.wcfg["show_lap_difference"]:
                color = (f"color: {self.color_lap_diff(curr[1])};"
                         f"background: {self.wcfg['bkg_color_driver_name']};")
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

            target_bar.setText(text)
            target_bar.setStyleSheet(color)

    def update_veh(self, target_bar, curr, last, isplayer):
        """Vehicle name"""
        if curr != last:
            if self.hiplayer and isplayer:
                color = (f"color: {self.wcfg['font_color_player_vehicle_name']};"
                         f"background: {self.wcfg['bkg_color_player_vehicle_name']};")
            elif self.wcfg["show_lap_difference"]:
                color = (f"color: {self.color_lap_diff(curr[1])};"
                         f"background: {self.wcfg['bkg_color_vehicle_name']};")
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

            target_bar.setText(text)
            target_bar.setStyleSheet(color)

    def update_brd(self, target_bar, curr, last, isplayer):
        """Brand logo"""
        if curr != last:
            if curr[0]:
                brand_name = self.cfg.user.brands.get(curr[0], curr[0])
            else:
                brand_name = "blank"
            # Draw brand logo
            target_bar.setPixmap(self.load_brand_logo(brand_name))
            # Draw background
            target_bar.setStyleSheet(self.bar_style_brd[self.hiplayer and isplayer])

    def update_gap(self, target_bar, curr, last, isplayer):
        """Time gap"""
        if curr != last:
            if self.hiplayer and isplayer:
                color = (f"color: {self.wcfg['font_color_player_time_gap']};"
                         f"background: {self.wcfg['bkg_color_player_time_gap']};")
            elif self.wcfg["show_lap_difference"]:
                color = (f"color: {self.color_lap_diff(curr[1])};"
                         f"background: {self.wcfg['bkg_color_time_gap']};")
            else:
                color = (f"color: {self.wcfg['font_color_time_gap']};"
                         f"background: {self.wcfg['bkg_color_time_gap']};")

            target_bar.setText(
                curr[0][:self.gap_width].strip(".").rjust(self.gap_width))
            target_bar.setStyleSheet(color)

    def update_lpt(self, target_bar, curr, last, isplayer):
        """Vehicle laptime"""
        if curr != last:
            target_bar.setText(curr)
            target_bar.setStyleSheet(self.bar_style_lpt[self.hiplayer and isplayer])

    def update_pic(self, target_bar, curr, last, isplayer):
        """Position in class"""
        if curr != last:
            target_bar.setText(curr)
            target_bar.setStyleSheet(self.bar_style_pic[self.hiplayer and isplayer])

    def update_cls(self, target_bar, curr, last):
        """Vehicle class"""
        if curr != last:
            text, bg_color = self.set_class_style(curr)
            target_bar.setText(text[:self.cls_width])
            target_bar.setStyleSheet(
                f"color: {self.wcfg['font_color_class']};background: {bg_color};")

    def update_pit(self, target_bar, curr, last):
        """Vehicle in pit"""
        if curr != last:
            text, bg_color = self.set_pitstatus(curr)
            target_bar.setText(text)
            target_bar.setStyleSheet(
                f"color: {self.wcfg['font_color_pit']};background: {bg_color};")

    def update_tcp(self, target_bar, curr, last, isplayer):
        """Tyre compound index"""
        if curr != last:
            target_bar.setText(self.set_tyre_cmp(curr))
            target_bar.setStyleSheet(self.bar_style_tcp[self.hiplayer and isplayer])

    def update_psc(self, target_bar, curr, last, isplayer):
        """Pitstop count"""
        if curr != last:
            if self.wcfg["show_pit_request"] and curr[1] == 1:
                color = self.bar_style_psc[2]
            elif self.hiplayer and isplayer:
                color = self.bar_style_psc[1]
            else:
                color = self.bar_style_psc[0]

            target_bar.setText(self.set_pitcount(curr[0]))
            target_bar.setStyleSheet(color)

    # Additional methods
    def color_lap_diff(self, is_lapped):
        """Compare lap differences & set color"""
        if is_lapped > 0:
            return self.wcfg["font_color_laps_ahead"]
        if is_lapped < 0:
            return self.wcfg["font_color_laps_behind"]
        return self.wcfg["font_color_same_lap"]

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

    def get_data(self, index, vehicles_data):
        """Relative data"""
        # check whether is lapped
        is_lapped = vehicles_data[index].isLapped

        # 0 Is player
        is_player = vehicles_data[index].isPlayer

        # 1 Vehicle in pit
        in_pit = vehicles_data[index].inPit

        # 2 Driver position
        position = (f"{vehicles_data[index].position:02d}", is_lapped)

        # 3 Driver name
        drv_name = (vehicles_data[index].driverName, is_lapped)

        # 4 Vehicle name
        veh_name = (vehicles_data[index].vehicleName, is_lapped)

        # 5 Vehicle position in class
        pos_class = f"{vehicles_data[index].positionInClass:02d}"

        # 6 Vehicle class
        veh_class = vehicles_data[index].vehicleClass

        # 7 Time gap
        time_gap = (f"{vehicles_data[index].relativeTimeGap:.{self.gap_decimals}f}", is_lapped)

        # 8 Tyre compound index
        tire_idx = vehicles_data[index].tireCompound

        # 9 Lap time
        laptime = self.set_laptime(
            vehicles_data[index].inPit,
            vehicles_data[index].lastLapTime,
            vehicles_data[index].pitTime
        )

        # 10 Pitstop count
        pit_count = (vehicles_data[index].numPitStops,
                    vehicles_data[index].pitState)

        return (is_player, in_pit, position, drv_name, veh_name, pos_class, veh_class,
                time_gap, tire_idx, laptime, pit_count)
