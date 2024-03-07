#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from .. import calculation as calc
from .. import formatter as fmt
from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "relative"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.drv_width = max(int(self.wcfg["driver_name_width"]), 1)
        self.veh_width = max(int(self.wcfg["vehicle_name_width"]), 1)
        self.cls_width = max(int(self.wcfg["class_width"]), 1)
        self.gap_width = max(int(self.wcfg["time_gap_width"]), 1)
        self.gap_decimals = max(int(self.wcfg["time_gap_decimal_places"]), 0)
        self.tyre_compound_string = self.cfg.units["tyre_compound_symbol"].ljust(20, "?")

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Max display players
        self.veh_add_front = min(max(int(self.wcfg["additional_players_front"]), 0), 60)
        self.veh_add_behind = min(max(int(self.wcfg["additional_players_behind"]), 0), 60)
        self.veh_range = max(7 + self.veh_add_front + self.veh_add_behind, 7)

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

        # Create layout
        self.layout = QGridLayout()
        self.layout.setContentsMargins(0,0,0,0)  # remove border
        self.layout.setHorizontalSpacing(0)
        self.layout.setVerticalSpacing(bar_gap)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_pos = self.wcfg["column_index_position"]
        column_drv = self.wcfg["column_index_driver"]
        column_veh = self.wcfg["column_index_vehicle"]
        column_lpt = self.wcfg["column_index_laptime"]
        column_pic = self.wcfg["column_index_position_in_class"]
        column_cls = self.wcfg["column_index_class"]
        column_tcp = self.wcfg["column_index_tyre_compound"]
        column_psc = self.wcfg["column_index_pitstop_count"]
        column_gap = self.wcfg["column_index_timegap"]
        column_pit = self.wcfg["column_index_pitstatus"]

        # Driver position
        if self.wcfg["show_position"]:
            self.bar_width_pos = f"min-width: {font_m.width * 2}px;"
            bar_style_pos = (
                f"color: {self.wcfg['font_color_position']};"
                f"background: {self.wcfg['bkg_color_position']};"
                f"{self.bar_width_pos}"
            )
            self.generate_bar("pos", bar_style_pos, column_pos)

        # Driver name
        if self.wcfg["show_driver_name"]:
            self.bar_width_drv = f"min-width: {font_m.width * self.drv_width}px;"
            bar_style_drv = (
                f"color: {self.wcfg['font_color_driver_name']};"
                f"background: {self.wcfg['bkg_color_driver_name']};"
                f"{self.bar_width_drv}"
            )
            self.generate_bar("drv", bar_style_drv, column_drv)

        # Vehicle name
        if self.wcfg["show_vehicle_name"]:
            self.bar_width_veh = f"min-width: {font_m.width * self.veh_width}px;"
            bar_style_veh = (
                f"color: {self.wcfg['font_color_vehicle_name']};"
                f"background: {self.wcfg['bkg_color_vehicle_name']};"
                f"{self.bar_width_veh}"
            )
            self.generate_bar("veh", bar_style_veh, column_veh)

        # Time gap
        if self.wcfg["show_time_gap"]:
            self.bar_width_gap = f"min-width: {font_m.width * self.gap_width}px;"
            bar_style_gap = (
                f"color: {self.wcfg['font_color_time_gap']};"
                f"background: {self.wcfg['bkg_color_time_gap']};"
                f"{self.bar_width_gap}"
            )
            self.generate_bar("gap", bar_style_gap, column_gap)

        # Vehicle laptime
        if self.wcfg["show_laptime"]:
            self.bar_width_lpt = f"min-width: {font_m.width * 8}px;"
            bar_style_lpt = (
                f"color: {self.wcfg['font_color_laptime']};"
                f"background: {self.wcfg['bkg_color_laptime']};"
                f"{self.bar_width_lpt}"
            )
            self.generate_bar("lpt", bar_style_lpt, column_lpt)

        # Vehicle position in class
        if self.wcfg["show_position_in_class"]:
            self.bar_width_pic = f"min-width: {font_m.width * 2}px;"
            bar_style_pic = (
                f"color: {self.wcfg['font_color_position_in_class']};"
                f"background: {self.wcfg['bkg_color_position_in_class']};"
                f"{self.bar_width_pic}"
            )
            self.generate_bar("pic", bar_style_pic, column_pic)

        # Vehicle class
        if self.wcfg["show_class"]:
            self.bar_width_cls = f"min-width: {font_m.width * self.cls_width}px;"
            bar_style_cls = (
                f"color: {self.wcfg['font_color_class']};"
                f"background: {self.wcfg['bkg_color_class']};"
                f"{self.bar_width_cls}"
            )
            self.generate_bar("cls", bar_style_cls, column_cls)

        # Vehicle in pit
        if self.wcfg["show_pit_status"]:
            self.bar_width_pit = f"min-width: {font_m.width * len(self.wcfg['pit_status_text'])}px;"
            bar_style_pit = (
                f"color: {self.wcfg['font_color_pit']};"
                f"background: {self.wcfg['bkg_color_pit']};"
                f"{self.bar_width_pit}"
            )
            self.generate_bar("pit", bar_style_pit, column_pit)

        # Tyre compound index
        if self.wcfg["show_tyre_compound"]:
            self.bar_width_tcp = f"min-width: {font_m.width * 2}px;"
            bar_style_tcp = (
                f"color: {self.wcfg['font_color_tyre_compound']};"
                f"background: {self.wcfg['bkg_color_tyre_compound']};"
                f"{self.bar_width_tcp}"
            )
            self.generate_bar("tcp", bar_style_tcp, column_tcp)

        # Pitstop count
        if self.wcfg["show_pitstop_count"]:
            self.bar_width_psc = f"min-width: {font_m.width * 2}px;"
            bar_style_psc = (
                f"color: {self.wcfg['font_color_pitstop_count']};"
                f"background: {self.wcfg['bkg_color_pitstop_count']};"
                f"{self.bar_width_psc}"
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
                getattr(self, f"row_{idx}_{suffix}"), idx, column_idx
            )
            # Last data
            setattr(self, f"last_veh_{idx}", [None] * data_slots)

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state and minfo.relative.relative:

            relative_idx = minfo.relative.relative
            vehicles_data = minfo.vehicles.dataSet
            total_idx = len(relative_idx)

            # Relative update
            for idx in range(self.veh_range):

                # Get vehicle data
                if idx < total_idx:
                    setattr(self, f"veh_{idx}",
                            self.get_data(relative_idx[idx], vehicles_data)
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
                # Time gap
                if self.wcfg["show_time_gap"]:
                    self.update_gap(f"{idx}_gap",
                                    getattr(self, f"veh_{idx}")[7],
                                    getattr(self, f"last_veh_{idx}")[7],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Vehicle laptime
                if self.wcfg["show_laptime"]:
                    self.update_lpt(f"{idx}_lpt",
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
                                    getattr(self, f"veh_{idx}")[8],
                                    getattr(self, f"last_veh_{idx}")[8],
                                    getattr(self, f"veh_{idx}")[0]  # is_player
                                    )
                # Pitstop count
                if self.wcfg["show_pitstop_count"]:
                    self.update_psc(f"{idx}_psc",
                                    getattr(self, f"veh_{idx}")[10],
                                    getattr(self, f"last_veh_{idx}")[10],
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
                if self.wcfg["show_lap_difference"]:
                    fgcolor = self.color_lap_diff(curr[1])
                else:
                    fgcolor = self.wcfg["font_color_position"]
                color = (f"color: {fgcolor};"
                         f"background: {self.wcfg['bkg_color_position']};")

            getattr(self, f"row_{suffix}").setText(curr[0])
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_pos}"
            )

    def update_drv(self, suffix, curr, last, isplayer):
        """Driver name"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_driver_name']};"
                         f"background: {self.wcfg['bkg_color_player_driver_name']};")
            else:
                if self.wcfg["show_lap_difference"]:
                    fgcolor = self.color_lap_diff(curr[1])
                else:
                    fgcolor = self.wcfg["font_color_driver_name"]
                color = (f"color: {fgcolor};"
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
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_drv}"
            )

    def update_veh(self, suffix, curr, last, isplayer):
        """Vehicle name"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_vehicle_name']};"
                         f"background: {self.wcfg['bkg_color_player_vehicle_name']};")
            else:
                if self.wcfg["show_lap_difference"]:
                    fgcolor = self.color_lap_diff(curr[1])
                else:
                    fgcolor = self.wcfg["font_color_vehicle_name"]
                color = (f"color: {fgcolor};"
                         f"background: {self.wcfg['bkg_color_vehicle_name']};")

            if self.wcfg["show_vehicle_brand_as_name"]:
                vname = self.cfg.brands_user.get(curr[0], curr[0])
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
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_veh}"
            )

    def update_gap(self, suffix, curr, last, isplayer):
        """Time gap"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_time_gap']};"
                         f"background: {self.wcfg['bkg_color_player_time_gap']};")
            else:
                if self.wcfg["show_lap_difference"]:
                    fgcolor = self.color_lap_diff(curr[1])
                else:
                    fgcolor = self.wcfg["font_color_time_gap"]
                color = (f"color: {fgcolor};"
                         f"background: {self.wcfg['bkg_color_time_gap']};")

            getattr(self, f"row_{suffix}").setText(
                fmt.strip_decimal_pt(curr[0][:self.gap_width]).rjust(self.gap_width))
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_gap}"
            )

    def update_lpt(self, suffix, curr, last, isplayer):
        """Vehicle laptime"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_laptime']};"
                         f"background: {self.wcfg['bkg_color_player_laptime']};")
            else:
                color = (f"color: {self.wcfg['font_color_laptime']};"
                         f"background: {self.wcfg['bkg_color_laptime']};")

            getattr(self, f"row_{suffix}").setText(curr)
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_lpt}"
            )

    def update_pic(self, suffix, curr, last, isplayer):
        """Position in class"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_position_in_class']};"
                         f"background: {self.wcfg['bkg_color_player_position_in_class']};")
            else:
                color = (f"color: {self.wcfg['font_color_position_in_class']};"
                         f"background: {self.wcfg['bkg_color_position_in_class']};")

            getattr(self, f"row_{suffix}").setText(curr)
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_pic}"
            )

    def update_cls(self, suffix, curr, last):
        """Vehicle class"""
        if curr != last:
            text, bg_color = self.set_class_style(curr)
            color = (f"color: {self.wcfg['font_color_class']};"
                     f"background: {bg_color};")

            getattr(self, f"row_{suffix}").setText(text[:self.cls_width])
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_cls}"
            )

    def update_pit(self, suffix, curr, last):
        """Vehicle in pit"""
        if curr != last:
            text, bg_color = self.set_pitstatus(curr)
            color = (f"color: {self.wcfg['font_color_pit']};"
                     f"background: {bg_color};")

            getattr(self, f"row_{suffix}").setText(text)
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_pit}"
            )

    def update_tcp(self, suffix, curr, last, isplayer):
        """Tyre compound index"""
        if curr != last:
            if self.wcfg["show_player_highlighted"] and isplayer:
                color = (f"color: {self.wcfg['font_color_player_tyre_compound']};"
                         f"background: {self.wcfg['bkg_color_player_tyre_compound']};")
            else:
                color = (f"color: {self.wcfg['font_color_tyre_compound']};"
                         f"background: {self.wcfg['bkg_color_tyre_compound']};")

            getattr(self, f"row_{suffix}").setText(self.set_tyre_cmp(curr))
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_tcp}"
            )

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

            getattr(self, f"row_{suffix}").setText(self.set_pitcount(curr[0]))
            getattr(self, f"row_{suffix}").setStyleSheet(
                f"{color}{self.bar_width_psc}"
            )

    # Additional methods
    def color_lap_diff(self, is_lapped):
        """Compare lap differences & set color"""
        if is_lapped > 0:
            return self.wcfg["font_color_laps_ahead"]
        if is_lapped < 0:
            return self.wcfg["font_color_laps_behind"]
        return self.wcfg["font_color_same_lap"]

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
        if vehclass_name in self.cfg.classes_user:
            return tuple(*self.cfg.classes_user[vehclass_name].items())  # sub_name, sub_color
        if vehclass_name and self.wcfg["show_random_color_for_unknown_class"]:
            return vehclass_name, fmt.random_color_class(vehclass_name)
        return vehclass_name, self.wcfg["bkg_color_class"]

    @staticmethod
    def set_laptime(inpit, laptime_last, pit_time):
        """Set lap time"""
        if inpit:
            return "PIT" + f"{pit_time:.01f}"[:5].rjust(5) if pit_time > 0 else "-:--.---"
        if laptime_last <= 0:
            return "OUT" + f"{pit_time:.01f}"[:5].rjust(5) if pit_time > 0 else "-:--.---"
        return calc.sec2laptime_full(laptime_last)[:8].rjust(8)

    def get_data(self, index, vehicles_data):
        """Relative data"""
        # Prevent index out of range
        if vehicles_data and 0 <= index < len(vehicles_data):

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
            time_gap = (f"{vehicles_data[index].relativeTimeGap:.0{self.gap_decimals}f}", is_lapped)

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
        # Assign empty value to -1 index
        return self.empty_vehicles_data
