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

from PySide2.QtGui import QPixmap

from .. import calculation as calc
from .. import formatter as fmt
from ..module_info import minfo
from ..userfile.brand_logo import load_brand_logo_file
from ._base import Overlay


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config, widget_name):
        # Assign base setting
        super().__init__(config, widget_name)
        layout = self.set_grid_layout(gap_vert=self.wcfg["bar_gap"])
        self.set_primary_layout(layout=layout)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        self.drv_width = max(int(self.wcfg["driver_name_width"]), 1)
        self.veh_width = max(int(self.wcfg["vehicle_name_width"]), 1)
        self.brd_width = max(int(self.wcfg["brand_logo_width"]), 1)
        self.brd_height = max(self.wcfg["font_size"], 1)
        self.cls_width = max(int(self.wcfg["class_width"]), 1)
        self.gap_width = max(int(self.wcfg["time_gap_width"]), 1)
        self.gap_decimals = max(int(self.wcfg["time_gap_decimal_places"]), 0)
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Max display players
        veh_add_front = min(max(int(self.wcfg["additional_players_front"]), 0), 60)
        veh_add_behind = min(max(int(self.wcfg["additional_players_behind"]), 0), 60)
        self.veh_range = max(7 + veh_add_front + veh_add_behind, 7)

        # Empty dataset
        self.empty_vehicles_data = (
            0,  # in_pit
            ("",0,0),  # position
            ("",0,0),  # driver name
            ("",0,0),  # vehicle name
            ("",0),  # pos_class
            "",  # veh_class
            ("",0),  # time_gap
            (-1,-1,0),  # tire_idx
            ("",0,0),  # laptime
            (-999,0,0)  # pit_count
        )
        self.pixmap_brandlogo = {"blank": QPixmap()}
        self.row_visible = [False] * self.veh_range
        self.row_visible[0] = True

        # Driver position
        if self.wcfg["show_position"]:
            self.bar_style_pos = self.set_qss_lap_difference(
                fg_color=self.wcfg["font_color_position"],
                bg_color=self.wcfg["bkg_color_position"],
                plr_fg_color=self.wcfg["font_color_player_position"],
                plr_bg_color=self.wcfg["bkg_color_player_position"],
            )
            self.bars_pos = self.set_qlabel(
                style=self.bar_style_pos[0],
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pos,
                column_index=self.wcfg["column_index_position"],
            )
        # Driver name
        if self.wcfg["show_driver_name"]:
            self.bar_style_drv = self.set_qss_lap_difference(
                fg_color=self.wcfg["font_color_driver_name"],
                bg_color=self.wcfg["bkg_color_driver_name"],
                plr_fg_color=self.wcfg["font_color_player_driver_name"],
                plr_bg_color=self.wcfg["bkg_color_player_driver_name"],
            )
            self.bars_drv = self.set_qlabel(
                style=self.bar_style_drv[0],
                width=self.drv_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_drv,
                column_index=self.wcfg["column_index_driver"],
            )
        # Vehicle name
        if self.wcfg["show_vehicle_name"]:
            self.bar_style_veh = self.set_qss_lap_difference(
                fg_color=self.wcfg["font_color_vehicle_name"],
                bg_color=self.wcfg["bkg_color_vehicle_name"],
                plr_fg_color=self.wcfg["font_color_player_vehicle_name"],
                plr_bg_color=self.wcfg["bkg_color_player_vehicle_name"],
            )
            self.bars_veh = self.set_qlabel(
                style=self.bar_style_veh[0],
                width=self.veh_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_veh,
                column_index=self.wcfg["column_index_vehicle"],
            )
        # Brand logo
        if self.wcfg["show_brand_logo"]:
            self.bar_style_brd = (
                self.set_qss(
                    bg_color=self.wcfg["bkg_color_brand_logo"]),
                self.set_qss(
                    bg_color=self.wcfg["bkg_color_player_brand_logo"])
            )
            self.bars_brd = self.set_qlabel(
                style=self.bar_style_brd[0],
                width=self.brd_width,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_brd,
                column_index=self.wcfg["column_index_brand_logo"],
            )
        # Time gap
        if self.wcfg["show_time_gap"]:
            self.bar_style_gap = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_time_gap"],
                    bg_color=self.wcfg["bkg_color_time_gap"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_time_gap"],
                    bg_color=self.wcfg["bkg_color_player_time_gap"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_nearest_time_gap"],
                    bg_color=self.wcfg["bkg_color_nearest_time_gap"])
            )
            self.nearest_time_gap = (
                -max(self.wcfg["nearest_time_gap_threshold_behind"], 0),
                max(self.wcfg["nearest_time_gap_threshold_front"], 0),
            )
            self.bars_gap = self.set_qlabel(
                style=self.bar_style_gap[0],
                width=self.gap_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_gap,
                column_index=self.wcfg["column_index_timegap"],
            )
        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            self.bar_style_lpt = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_laptime"],
                    bg_color=self.wcfg["bkg_color_laptime"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_laptime"],
                    bg_color=self.wcfg["bkg_color_player_laptime"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_fastest_last_laptime"],
                    bg_color=self.wcfg["bkg_color_fastest_last_laptime"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_fastest_last_laptime"],
                    bg_color=self.wcfg["bkg_color_player_fastest_last_laptime"])
            )
            self.bars_lpt = self.set_qlabel(
                style=self.bar_style_lpt[0],
                width=8 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_lpt,
                column_index=self.wcfg["column_index_laptime"],
            )
        # Position in class
        if self.wcfg["show_position_in_class"]:
            self.bar_style_pic = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_position_in_class"],
                    bg_color=self.wcfg["bkg_color_position_in_class"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_position_in_class"],
                    bg_color=self.wcfg["bkg_color_player_position_in_class"])
            )
            self.bars_pic = self.set_qlabel(
                style=self.bar_style_pic[0],
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pic,
                column_index=self.wcfg["column_index_position_in_class"],
            )
        # Vehicle class
        if self.wcfg["show_class"]:
            bar_style_cls = self.set_qss(
                fg_color=self.wcfg["font_color_class"],
                bg_color=self.wcfg["bkg_color_class"]
            )
            self.bars_cls = self.set_qlabel(
                style=bar_style_cls,
                width=self.cls_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_cls,
                column_index=self.wcfg["column_index_class"],
            )
        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            self.pit_status_text = (
                self.wcfg["pit_status_text"],
                self.wcfg["garage_status_text"]
            )
            self.bar_style_pit = (
                "",
                self.set_qss(
                    fg_color=self.wcfg["font_color_pit"],
                    bg_color=self.wcfg["bkg_color_pit"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_garage"],
                    bg_color=self.wcfg["bkg_color_garage"])
            )
            self.bars_pit = self.set_qlabel(
                style=self.bar_style_pit[0],
                width=max(map(len, self.pit_status_text)) * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pit,
                column_index=self.wcfg["column_index_pitstatus"],
            )
        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            self.bar_style_tcp = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_tyre_compound"],
                    bg_color=self.wcfg["bkg_color_tyre_compound"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_tyre_compound"],
                    bg_color=self.wcfg["bkg_color_player_tyre_compound"])
            )
            self.bars_tcp = self.set_qlabel(
                style=self.bar_style_tcp[0],
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_tcp,
                column_index=self.wcfg["column_index_tyre_compound"],
            )
        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            self.bar_style_psc = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_pitstop_count"],
                    bg_color=self.wcfg["bkg_color_pitstop_count"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_player_pitstop_count"],
                    bg_color=self.wcfg["bkg_color_player_pitstop_count"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_pit_request"],
                    bg_color=self.wcfg["bkg_color_pit_request"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_penalty_count"],
                    bg_color=self.wcfg["bkg_color_penalty_count"])
            )
            self.bars_psc = self.set_qlabel(
                style=self.bar_style_psc[0],
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_psc,
                column_index=self.wcfg["column_index_pitstop_count"],
            )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            relative_list = minfo.relative.relative
            total_rel_idx = len(relative_list)

            # Relative update
            for idx in range(self.veh_range):

                if idx < total_rel_idx:
                    rel_idx = relative_list[idx]
                else:
                    rel_idx = -2

                # Get vehicle dataset
                if rel_idx >= 0:
                    self.row_visible[idx] = True
                    temp_data = self.get_data(minfo.vehicles.dataSet[rel_idx])
                elif not self.row_visible[idx]:
                    continue  # skip if already empty
                else:
                    self.row_visible[idx] = False
                    temp_data = self.empty_vehicles_data
                # Driver position
                if self.wcfg["show_position"]:
                    self.update_pos(self.bars_pos[idx], temp_data[1])
                # Driver name
                if self.wcfg["show_driver_name"]:
                    self.update_drv(self.bars_drv[idx], temp_data[2])
                # Vehicle name
                if self.wcfg["show_vehicle_name"]:
                    self.update_veh(self.bars_veh[idx], temp_data[3])
                # Brand logo
                if self.wcfg["show_brand_logo"]:
                    self.update_brd(self.bars_brd[idx], temp_data[3])
                # Time gap
                if self.wcfg["show_time_gap"]:
                    self.update_gap(self.bars_gap[idx], temp_data[6])
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(self.bars_lpt[idx], temp_data[8])
                # Position in class
                if self.wcfg["show_position_in_class"]:
                    self.update_pic(self.bars_pic[idx], temp_data[4])
                # Vehicle class
                if self.wcfg["show_class"]:
                    self.update_cls(self.bars_cls[idx], temp_data[5])
                # Vehicle in pit
                if self.wcfg["show_pit_status"]:
                    self.update_pit(self.bars_pit[idx], temp_data[0])
                # Tyre compound index
                if self.wcfg["show_tyre_compound"]:
                    self.update_tcp(self.bars_tcp[idx], temp_data[7])
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(self.bars_psc[idx], temp_data[9])

    # GUI update methods
    def update_pos(self, target, data):
        """Driver position"""
        if target.last != data:
            target.last = data
            if data[2]:  # highlight player
                color = self.bar_style_pos[1]
            elif self.wcfg["show_lap_difference"]:
                color = self.bar_style_pos[lap_difference_index(data[1])]
            else:
                color = self.bar_style_pos[0]
            if data[0] != "":
                text = f"{data[0]:02d}"
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(color)

    def update_drv(self, target, data):
        """Driver name"""
        if target.last != data:
            target.last = data
            if data[2]:  # highlight player
                color = self.bar_style_drv[1]
            elif self.wcfg["show_lap_difference"]:
                color = self.bar_style_drv[lap_difference_index(data[1])]
            else:
                color = self.bar_style_drv[0]
            if self.wcfg["driver_name_shorten"]:
                text = fmt.shorten_driver_name(data[0])
            else:
                text = data[0]
            if self.wcfg["driver_name_uppercase"]:
                text = text.upper()
            if self.wcfg["driver_name_align_center"]:
                text = text[:self.drv_width]
            else:
                text = text[:self.drv_width].ljust(self.drv_width)
            target.setText(text)
            target.setStyleSheet(color)

    def update_veh(self, target, data):
        """Vehicle name"""
        if target.last != data:
            target.last = data
            if data[2]:  # highlight player
                color = self.bar_style_veh[1]
            elif self.wcfg["show_lap_difference"]:
                color = self.bar_style_veh[lap_difference_index(data[1])]
            else:
                color = self.bar_style_veh[0]
            if self.wcfg["show_vehicle_brand_as_name"]:
                text = self.cfg.user.brands.get(data[0], data[0])
            else:
                text = data[0]
            if self.wcfg["vehicle_name_uppercase"]:
                text = text.upper()
            if self.wcfg["vehicle_name_align_center"]:
                text = text[:self.veh_width]
            else:
                text = text[:self.veh_width].ljust(self.veh_width)
            target.setText(text)
            target.setStyleSheet(color)

    def update_brd(self, target, data):
        """Brand logo"""
        if target.last != data:
            target.last = data
            if data[0]:
                brand_name = self.cfg.user.brands.get(data[0], data[0])
            else:
                brand_name = "blank"
            target.setPixmap(self.set_brand_logo(brand_name))
            target.setStyleSheet(self.bar_style_brd[data[2]])

    def update_gap(self, target, data):
        """Time gap"""
        if target.last != data:
            target.last = data
            if data[1]:  # highlight player
                color_index = 1
            elif (self.wcfg["show_highlighted_nearest_time_gap"] and
                  "" != data[0] and
                  self.nearest_time_gap[0] <= data[0] <= self.nearest_time_gap[1]):
                color_index = 2
            else:
                color_index = 0
            if data[0] != "":
                if self.wcfg["show_time_gap_sign"] and data[0] != 0:
                    value = f"{-data[0]:+.{self.gap_decimals}f}"
                else:
                    value = f"{abs(data[0]):.{self.gap_decimals}f}"
                text = value[:self.gap_width].strip(".").rjust(self.gap_width)
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(self.bar_style_gap[color_index])

    def update_lpt(self, target, data):
        """Vehicle laptime"""
        if target.last != data:
            target.last = data
            if data[0] != "":
                text = self.set_laptime(*data[0])
            else:
                text = ""
            if self.wcfg["show_highlighted_fastest_last_laptime"] and data[1]:
                color_index = 2 + data[2]
            else:
                color_index = data[2]
            target.setText(text)
            target.setStyleSheet(self.bar_style_lpt[color_index])

    def update_pic(self, target, data):
        """Position in class"""
        if target.last != data:
            target.last = data
            if data[0] != "":
                text = f"{data[0]:02d}"
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(self.bar_style_pic[data[1]])

    def update_cls(self, target, data):
        """Vehicle class"""
        if target.last != data:
            target.last = data
            text, bg_color = self.set_class_style(data)
            target.setText(text[:self.cls_width])
            target.setStyleSheet(
                f"color:{self.wcfg['font_color_class']};background:{bg_color};")

    def update_pit(self, target, data):
        """Vehicle in pit"""
        if target.last != data:
            target.last = data
            if data:
                text = self.pit_status_text[data - 1]
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(self.bar_style_pit[data])

    def update_tcp(self, target, data):
        """Tyre compound index"""
        if target.last != data:
            target.last = data
            if data[0] != -1:
                text = f"{self.tyre_compound_string[data[0]]}{self.tyre_compound_string[data[1]]}"
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(self.bar_style_tcp[data[2]])

    def update_psc(self, target, data):
        """Pitstop count"""
        if target.last != data:
            target.last = data
            if -999 < data[0] < 0:
                color_index = 3
            elif self.wcfg["show_pit_request"] and data[1] == 1:
                color_index = 2
            elif data[2]:  # highlight player
                color_index = 1
            else:
                color_index = 0
            target.setText(self.set_pitcount(data[0]))
            target.setStyleSheet(self.bar_style_psc[color_index])

    # Additional methods
    def set_qss_lap_difference(self, fg_color, bg_color, plr_fg_color, plr_bg_color):
        """Set style with player & lap difference:
        0 default, 1 player, 2 same lap, 3 behind lap, 4 ahead lap.
        """
        return (
            self.set_qss(  # 0 default
                fg_color=fg_color,
                bg_color=bg_color),
            self.set_qss(  # 1 player
                fg_color=plr_fg_color,
                bg_color=plr_bg_color),
            self.set_qss(  # 2 same lap
                fg_color=self.wcfg["font_color_same_lap"],
                bg_color=bg_color),
            self.set_qss(  # 3 behind lap
                fg_color=self.wcfg["font_color_laps_behind"],
                bg_color=bg_color),
            self.set_qss(  # 4 ahead lap
                fg_color=self.wcfg["font_color_laps_ahead"],
                bg_color=bg_color),
        )

    def set_brand_logo(self, brand_name):
        """Set brand logo"""
        if brand_name in self.pixmap_brandlogo:  # cached logo
            return self.pixmap_brandlogo[brand_name]
        if brand_name in self.cfg.user.brands_logo:  # add to cache
            self.pixmap_brandlogo[brand_name] = load_brand_logo_file(
                filepath=self.cfg.path.brand_logo,
                filename=brand_name,
                max_width=self.brd_width,
                max_height=self.brd_height,
            )
            return self.pixmap_brandlogo[brand_name]
        return self.pixmap_brandlogo["blank"]  # load blank if unavailable

    @staticmethod
    def set_pitcount(pits):
        """Set pitstop count test"""
        if pits == 0:
            return "-"
        if pits != -999:
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
            return f"PIT{pit_time: >5.1f}"[:8] if pit_time > 0 else "-:--.---"
        if laptime_last <= 0:
            return f"OUT{pit_time: >5.1f}"[:8] if pit_time > 0 else "-:--.---"
        return calc.sec2laptime_full(laptime_last)[:8].rjust(8)

    def get_data(self, veh_info):
        """Relative dataset"""
        # Check whether is lapped (is_lapped: int)
        is_lapped = veh_info.isLapped

        # Highlighted player (hi_player: bool)
        hi_player = self.wcfg["show_player_highlighted"] and veh_info.isPlayer

        # 0 Vehicle in pit (in_pit: bool)
        in_pit = veh_info.inPit

        # 1 Driver position (position: int, is_lapped, hi_player)
        position = (veh_info.positionOverall, is_lapped, hi_player)

        # 2 Driver name (drv_name: str, is_lapped, hi_player)
        drv_name = (veh_info.driverName, is_lapped, hi_player)

        # 3 Vehicle name (veh_name: str, is_lapped, hi_player)
        veh_name = (veh_info.vehicleName, is_lapped, hi_player)

        # 4 Position in class (pos_class: int, hi_player)
        pos_class = (veh_info.positionInClass, hi_player)

        # 5 Vehicle class (veh_class: str)
        veh_class = veh_info.vehicleClass

        # 6 Time gap (time_gap: float, hi_player)
        time_gap = (veh_info.relativeTimeGap, hi_player)

        # 7 Tyre compound index (tire_idx: int, hi_player)
        tire_idx = (veh_info.tireCompoundFront, veh_info.tireCompoundRear, hi_player)

        # 8 Lap time (laptime: tuple, is fastest last: bool, hi_player)
        laptime = ((
                veh_info.inPit,
                veh_info.lastLapTime,
                veh_info.pitTimer.elapsed
            ),
            veh_info.isClassFastestLastLap, hi_player)

        # 9 Pitstop count (pit_count: int, pit_state: int, hi_player)
        pit_count = (
            veh_info.numPitStops,
            veh_info.pitState,
            hi_player)

        return (in_pit, position, drv_name, veh_name, pos_class, veh_class,
                time_gap, tire_idx, laptime, pit_count)


def lap_difference_index(is_lapped, offset=2):
    """Set lap difference as index

    Returns:
        0 = same lap, 1 = behind, 2 = ahead
    """
    return (is_lapped < 0) + (is_lapped > 0) * 2 + offset
