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

from .. import calculation as calc
from .. import formatter as fmt
from .. import heatmap as hmp
from ..api_control import api
from ..const_common import TEXT_PLACEHOLDER
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
        self.int_width = max(int(self.wcfg["time_interval_width"]), 1)
        self.int_decimals = max(int(self.wcfg["time_interval_decimal_places"]), 0)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )

        # Max display players
        self.veh_range = 2

        # Empty dataset
        self.empty_vehicles_data = (
            0,  # in_pit
            "",  # position
            "",  # driver name
            "",  # vehicle name
            "",  # pos_class
            "",  # veh_class
            ("",""),  # tire_idx
            "",  # laptime
            "",  # best laptime
            (-999,0),  # pit_count
            ("",0),  # time_int
        )
        self.pixmap_brandlogo = {}
        self.row_visible = [False] * self.veh_range
        self.row_visible[0] = True

        # Driver position
        if self.wcfg["show_position"]:
            bar_style_pos = self.set_qss(
                fg_color=self.wcfg["font_color_position"],
                bg_color=self.wcfg["bkg_color_position"]
            )
            self.bars_pos = self.set_qlabel(
                style=bar_style_pos,
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pos,
                column_index=self.wcfg["column_index_position"],
                hide_start=1,
            )
        # Driver name
        if self.wcfg["show_driver_name"]:
            bar_style_drv = self.set_qss(
                fg_color=self.wcfg["font_color_driver_name"],
                bg_color=self.wcfg["bkg_color_driver_name"]
            )
            self.bars_drv = self.set_qlabel(
                style=bar_style_drv,
                width=self.drv_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_drv,
                column_index=self.wcfg["column_index_driver"],
                hide_start=1,
            )
        # Vehicle name
        if self.wcfg["show_vehicle_name"]:
            bar_style_veh = self.set_qss(
                fg_color=self.wcfg["font_color_vehicle_name"],
                bg_color=self.wcfg["bkg_color_vehicle_name"]
            )
            self.bars_veh = self.set_qlabel(
                style=bar_style_veh,
                width=self.veh_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_veh,
                column_index=self.wcfg["column_index_vehicle"],
                hide_start=1,
            )
        # Brand logo
        if self.wcfg["show_brand_logo"]:
            bar_style_brd = self.set_qss(
                bg_color=self.wcfg["bkg_color_brand_logo"]
            )
            self.bars_brd = self.set_qlabel(
                style=bar_style_brd,
                width=self.brd_width,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_brd,
                column_index=self.wcfg["column_index_brand_logo"],
                hide_start=1,
            )
        # Time interval
        if self.wcfg["show_time_interval"]:
            self.bar_style_int = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_time_interval_behind"],
                    bg_color=self.wcfg["bkg_color_time_interval_behind"]),
                self.set_qss(
                    fg_color=self.wcfg["font_color_time_interval_ahead"],
                    bg_color=self.wcfg["bkg_color_time_interval_ahead"])
            )
            self.bars_int = self.set_qlabel(
                style=self.bar_style_int[0],
                width=self.int_width * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_int,
                column_index=self.wcfg["column_index_timeinterval"],
                hide_start=1,
            )
        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            bar_style_lpt = self.set_qss(
                fg_color=self.wcfg["font_color_laptime"],
                bg_color=self.wcfg["bkg_color_laptime"]
            )
            self.bars_lpt = self.set_qlabel(
                style=bar_style_lpt,
                width=8 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_lpt,
                column_index=self.wcfg["column_index_laptime"],
                hide_start=1,
            )
        # Vehicle best laptime
        if self.wcfg["show_best_laptime"]:
            bar_style_blp = self.set_qss(
                fg_color=self.wcfg["font_color_best_laptime"],
                bg_color=self.wcfg["bkg_color_best_laptime"]
            )
            self.bars_blp = self.set_qlabel(
                style=bar_style_blp,
                width=8 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_blp,
                column_index=self.wcfg["column_index_best_laptime"],
                hide_start=1,
            )
        # Position in class
        if self.wcfg["show_position_in_class"]:
            bar_style_pic = self.set_qss(
                fg_color=self.wcfg["font_color_position_in_class"],
                bg_color=self.wcfg["bkg_color_position_in_class"]
            )
            self.bars_pic = self.set_qlabel(
                style=bar_style_pic,
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_pic,
                column_index=self.wcfg["column_index_position_in_class"],
                hide_start=1,
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
                hide_start=1,
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
                hide_start=1,
            )
        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            bar_style_tcp = self.set_qss(
                fg_color=self.wcfg["font_color_tyre_compound"],
                bg_color=self.wcfg["bkg_color_tyre_compound"]
            )
            self.bars_tcp = self.set_qlabel(
                style=bar_style_tcp,
                width=2 * font_m.width + bar_padx,
                count=self.veh_range,
            )
            self.set_grid_layout_table_column(
                layout=layout,
                targets=self.bars_tcp,
                column_index=self.wcfg["column_index_tyre_compound"],
                hide_start=1,
            )
        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            self.bar_style_psc = (
                self.set_qss(
                    fg_color=self.wcfg["font_color_pitstop_count"],
                    bg_color=self.wcfg["bkg_color_pitstop_count"]),
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
                hide_start=1,
            )

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            classes_list = minfo.relative.classes
            total_cls_idx = len(classes_list)
            player_idx = minfo.vehicles.playerIndex
            in_race = api.read.session.in_race()

            if player_idx < total_cls_idx:
                rivals_list = classes_list[player_idx][5:7]
            else:
                rivals_list = -1,-1

            # Standings update
            for idx, rvl_idx in enumerate(rivals_list):

                # Get vehicle dataset
                if rvl_idx >= 0:
                    self.row_visible[idx] = True
                    temp_data = self.get_data(
                        minfo.vehicles.dataSet[rvl_idx],
                        minfo.vehicles.dataSet[player_idx],
                        in_race)
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
                # Time interval
                if self.wcfg["show_time_interval"]:
                    self.update_int(self.bars_int[idx], temp_data[10])
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(self.bars_lpt[idx], temp_data[7])
                # Vehicle best laptime
                if self.wcfg["show_best_laptime"]:
                    self.update_blp(self.bars_blp[idx], temp_data[8])
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
                    self.update_tcp(self.bars_tcp[idx], temp_data[6])
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(self.bars_psc[idx], temp_data[9])

    # GUI update methods
    def update_pos(self, target, data):
        """Driver position"""
        if target.last != data:
            target.last = data
            if data != "":
                text = f"{data:02d}"
            else:
                text = ""
            target.setText(text)
            self.toggle_visibility(target, data)

    def update_drv(self, target, data):
        """Driver name"""
        if target.last != data:
            target.last = data
            if self.wcfg["driver_name_shorten"]:
                text = fmt.shorten_driver_name(data)
            else:
                text = data
            if self.wcfg["driver_name_uppercase"]:
                text = text.upper()
            if self.wcfg["driver_name_align_center"]:
                text = text[:self.drv_width]
            else:
                text = text[:self.drv_width].ljust(self.drv_width)
            target.setText(text)
            self.toggle_visibility(target, data)

    def update_veh(self, target, data):
        """Vehicle name"""
        if target.last != data:
            target.last = data
            if self.wcfg["show_vehicle_brand_as_name"]:
                text = self.cfg.user.brands.get(data, data)
            else:
                text = data
            if self.wcfg["vehicle_name_uppercase"]:
                text = text.upper()
            if self.wcfg["vehicle_name_align_center"]:
                text = text[:self.veh_width]
            else:
                text = text[:self.veh_width].ljust(self.veh_width)
            target.setText(text)
            self.toggle_visibility(target, data)

    def update_brd(self, target, data):
        """Brand logo"""
        if target.last != data:
            target.last = data
            if data:
                brand_name = self.cfg.user.brands.get(data, data)
            else:
                brand_name = "blank"
            target.setPixmap(self.set_brand_logo(brand_name))
            self.toggle_visibility(target, data)

    def update_int(self, target, data):
        """Time interval"""
        if target.last != data:
            target.last = data
            if data[0] != "":
                text = self.int_to_next(data[0], data[1])[
                    :self.int_width].strip(".").rjust(self.int_width)
            else:
                text = ""
            target.setText(text)
            target.setStyleSheet(self.bar_style_int[data[1]])
            self.toggle_visibility(target, text)

    def update_lpt(self, target, data):
        """Vehicle laptime"""
        if target.last != data:
            target.last = data
            if data != "":
                text = self.set_laptime(*data)
            else:
                text = ""
            target.setText(text)
            self.toggle_visibility(target, text)

    def update_blp(self, target, data):
        """Vehicle best laptime"""
        if target.last != data:
            target.last = data
            if data != "":
                text = self.set_best_laptime(data)
            else:
                text = ""
            target.setText(text)
            self.toggle_visibility(target, data)

    def update_pic(self, target, data):
        """Position in class"""
        if target.last != data:
            target.last = data
            if data != "":
                text = f"{data:02d}"
            else:
                text = ""
            target.setText(text)
            self.toggle_visibility(target, data)

    def update_cls(self, target, data):
        """Vehicle class"""
        if target.last != data:
            target.last = data
            text, bg_color = self.set_class_style(data)
            target.setText(text[:self.cls_width])
            target.setStyleSheet(
                f"color:{self.wcfg['font_color_class']};background:{bg_color};")
            self.toggle_visibility(target, data)

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
            self.toggle_visibility(target, text)

    def update_tcp(self, target, data):
        """Tyre compound index"""
        if target.last != data:
            target.last = data
            if data[0] != "":
                text = f"{hmp.select_compound_symbol(data[0])}{hmp.select_compound_symbol(data[1])}"
            else:
                text = ""
            target.setText(text)
            self.toggle_visibility(target, text)

    def update_psc(self, target, data):
        """Pitstop count"""
        if target.last != data:
            target.last = data
            if -999 < data[0] < 0:
                color_index = 2
            elif self.wcfg["show_pit_request"] and data[1] == 1:
                color_index = 1
            else:
                color_index = 0
            text = self.set_pitcount(data[0])
            target.setText(text)
            target.setStyleSheet(self.bar_style_psc[color_index])
            self.toggle_visibility(target, text)

    # Additional methods
    @staticmethod
    def toggle_visibility(target, state):
        """Hide bar if unavailable"""
        if state:
            target.show()
        else:
            target.hide()

    def set_brand_logo(self, brand_name: str):
        """Set brand logo"""
        if brand_name not in self.pixmap_brandlogo:  # load & cache logo
            self.pixmap_brandlogo[brand_name] = load_brand_logo_file(
                filepath=self.cfg.path.brand_logo,
                filename=brand_name,
                max_width=self.brd_width,
                max_height=self.brd_height,
            )
        return self.pixmap_brandlogo[brand_name]

    @staticmethod
    def set_pitcount(pits):
        """Set pitstop count test"""
        if pits == 0:
            return TEXT_PLACEHOLDER
        if pits != -999:
            return f"{pits}"
        return ""

    def set_class_style(self, class_name: str):
        """Compare vehicle class name with user defined dictionary"""
        style = self.cfg.user.classes.get(class_name, None)
        if style is not None:
            return style["alias"], style["color"]
        if class_name and self.wcfg["show_random_color_for_unknown_class"]:
            return class_name, fmt.random_color_class(class_name)
        return class_name, self.wcfg["bkg_color_class"]

    @staticmethod
    def set_laptime(inpit, laptime_last, pit_time):
        """Set lap time"""
        if inpit:
            return f"PIT{pit_time: >5.1f}"[:8] if pit_time > 0 else "-:--.---"
        if laptime_last <= 0:
            return f"OUT{pit_time: >5.1f}"[:8] if pit_time > 0 else "-:--.---"
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

    def get_data(self, veh_info, plr_veh_info, in_race):
        """Standings dataset"""
        # 0 Vehicle in pit (in_pit: bool)
        in_pit = veh_info.inPit

        # 1 Driver position (position: int)
        position = veh_info.positionOverall

        # 2 Driver name (drv_name: str)
        drv_name = veh_info.driverName

        # 3 Vehicle name (veh_name: str)
        veh_name = veh_info.vehicleName

        # 4 Position in class (pos_class: int)
        pos_class = veh_info.positionInClass

        # 5 Vehicle class (veh_class: str)
        veh_class = veh_info.vehicleClass

        # 6 Tyre compound index (tire_idx: str)
        tire_idx = (veh_info.tireCompoundFront, veh_info.tireCompoundRear)

        # 7 Lap time (laptime: tuple)
        if self.wcfg["show_best_laptime"] or in_race:
            laptime = (veh_info.inPit, veh_info.lastLapTime, veh_info.pitTimer.elapsed)
        else:
            laptime = (0, veh_info.bestLapTime, 0)

        # 8 Best lap time (best_laptime: float)
        best_laptime = veh_info.bestLapTime

        # 9 Pitstop count (pit_count: int, pit_state: int)
        pit_count = (veh_info.numPitStops, veh_info.pitState)

        # 10 Time interval (time_int: float, is_ahead)
        is_ahead = veh_info.positionOverall < plr_veh_info.positionOverall
        if is_ahead:
            time_int = (plr_veh_info.gapBehindNextInClass, is_ahead)
        else:
            time_int = (veh_info.gapBehindNextInClass, is_ahead)

        return (in_pit, position, drv_name, veh_name, pos_class, veh_class,
                tire_idx, laptime, best_laptime, pit_count, time_int)
