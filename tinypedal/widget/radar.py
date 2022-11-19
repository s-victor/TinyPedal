#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Radar Widget
"""

import tkinter as tk

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent
from tinypedal.load_func import module


class Draw(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "radar"

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self)
        self.cfg = config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        self.base_size = 100 * max(self.wcfg["area_scale"], 0.5)
        self.veh_width = max(int(self.wcfg["vehicle_width"] * 5 * self.wcfg["vehicle_scale"]), 1)
        self.veh_length = max(int(self.wcfg["vehicle_length"] * 5 * self.wcfg["vehicle_scale"]), 2)

        # Coordinates for drawing player vehicle
        plr_rect_coord = (self.base_size - self.veh_width,
                          self.base_size - self.veh_length,
                          self.base_size + self.veh_width,
                          self.base_size + self.veh_length)

        # Draw widget
        self.bar_radar = tk.Canvas(self, bd=0, highlightthickness=0,
                                   height=int(self.base_size * 2),
                                   width=int(self.base_size * 2),
                                   bg=self.wcfg["bkg_color"])
        self.bar_radar.grid(row=0, column=0, padx=0, pady=0)

        if self.wcfg["show_center_mark"]:
            self.bar_radar.create_line(self.base_size, 0, self.base_size, self.base_size * 2,
                                       fill=self.wcfg["center_mark_color"], dash=(2, 2))
            self.bar_radar.create_line(0, self.base_size, self.base_size * 2, self.base_size,
                                       fill=self.wcfg["center_mark_color"], dash=(2, 2))

        self.poly_plr = self.bar_radar.create_rectangle(
                        plr_rect_coord,
                        fill=self.wcfg["player_color"],
                        outline=self.wcfg["player_outline_color"],
                        width=max(self.wcfg["player_outline_width"], 0))

        poly_style = {"fill":self.wcfg["opponent_color"], "outline":""}

        self.poly_f_01 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_r_01 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_f_02 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_r_02 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_f_03 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_r_03 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)

        # Max visible vehicles
        self.radar_add_front = min(max(self.wcfg["additional_vehicles_front"], 0), 9)
        self.radar_add_behind = min(max(self.wcfg["additional_vehicles_behind"], 0), 9)

        if self.radar_add_front > 0:
            self.poly_f_04 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 0:
            self.poly_r_04 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 1:
            self.poly_f_05 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 1:
            self.poly_r_05 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 2:
            self.poly_f_06 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 2:
            self.poly_r_06 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 3:
            self.poly_f_07 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 3:
            self.poly_r_07 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 4:
            self.poly_f_08 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 4:
            self.poly_r_08 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 5:
            self.poly_f_09 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 5:
            self.poly_r_09 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 6:
            self.poly_f_10 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 6:
            self.poly_r_10 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 7:
            self.poly_f_11 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 7:
            self.poly_r_11 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_front > 8:
            self.poly_f_12 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        if self.radar_add_behind > 8:
            self.poly_r_12 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and module.relative_info.relative_list and self.wcfg["enable"]:

            # Read relative list player index
            rel_idx = module.relative_info.radar_list

            # Read orientation & position data
            veh_gps = module.relative_info.vehicle_gps(rel_idx)
            veh_center = int(3 + self.radar_add_front)

            # Check isPlayer before update
            if read_data.is_local_player():

                # Read vehicle position coordinates, lap number, orientation
                veh_plr = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center], rel_idx[veh_center])

                veh_f_01 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 1], rel_idx[veh_center - 1])
                veh_r_01 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 1], rel_idx[veh_center + 1])
                veh_f_02 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 2], rel_idx[veh_center - 2])
                veh_r_02 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 2], rel_idx[veh_center + 2])
                veh_f_03 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 3], rel_idx[veh_center - 3])
                veh_r_03 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 3], rel_idx[veh_center + 3])

                if self.radar_add_front > 0:
                    veh_f_04 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 4], rel_idx[veh_center - 4])
                if self.radar_add_behind > 0:
                    veh_r_04 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 4], rel_idx[veh_center + 4])
                if self.radar_add_front > 1:
                    veh_f_05 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 5], rel_idx[veh_center - 5])
                if self.radar_add_behind > 1:
                    veh_r_05 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 5], rel_idx[veh_center + 5])
                if self.radar_add_front > 2:
                    veh_f_06 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 6], rel_idx[veh_center - 6])
                if self.radar_add_behind > 2:
                    veh_r_06 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 6], rel_idx[veh_center + 6])
                if self.radar_add_front > 3:
                    veh_f_07 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 7], rel_idx[veh_center - 7])
                if self.radar_add_behind > 3:
                    veh_r_07 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 7], rel_idx[veh_center + 7])
                if self.radar_add_front > 4:
                    veh_f_08 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 8], rel_idx[veh_center - 8])
                if self.radar_add_behind > 4:
                    veh_r_08 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 8], rel_idx[veh_center + 8])
                if self.radar_add_front > 5:
                    veh_f_09 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 9], rel_idx[veh_center - 9])
                if self.radar_add_behind > 5:
                    veh_r_09 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 9], rel_idx[veh_center + 9])
                if self.radar_add_front > 6:
                    veh_f_10 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 10], rel_idx[veh_center - 10])
                if self.radar_add_behind > 6:
                    veh_r_10 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 10], rel_idx[veh_center + 10])
                if self.radar_add_front > 7:
                    veh_f_11 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 11], rel_idx[veh_center - 11])
                if self.radar_add_behind > 7:
                    veh_r_11 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 11], rel_idx[veh_center + 11])
                if self.radar_add_front > 8:
                    veh_f_12 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center - 12], rel_idx[veh_center - 12])
                if self.radar_add_behind > 8:
                    veh_r_12 = module.relative_info.radar_pos(veh_gps[veh_center], veh_gps[veh_center + 12], rel_idx[veh_center + 12])

                # Set vehicle color
                self.bar_radar.itemconfig(self.poly_f_01, fill=self.color_lapdiff(veh_f_01[1], veh_plr[1]))
                self.bar_radar.itemconfig(self.poly_r_01, fill=self.color_lapdiff(veh_r_01[1], veh_plr[1]))
                self.bar_radar.itemconfig(self.poly_f_02, fill=self.color_lapdiff(veh_f_02[1], veh_plr[1]))
                self.bar_radar.itemconfig(self.poly_r_02, fill=self.color_lapdiff(veh_r_02[1], veh_plr[1]))
                self.bar_radar.itemconfig(self.poly_f_03, fill=self.color_lapdiff(veh_f_03[1], veh_plr[1]))
                self.bar_radar.itemconfig(self.poly_r_03, fill=self.color_lapdiff(veh_r_03[1], veh_plr[1]))

                if self.radar_add_front > 0:
                    self.bar_radar.itemconfig(self.poly_f_04, fill=self.color_lapdiff(veh_f_04[1], veh_plr[1]))
                if self.radar_add_behind > 0:
                    self.bar_radar.itemconfig(self.poly_r_04, fill=self.color_lapdiff(veh_r_04[1], veh_plr[1]))
                if self.radar_add_front > 1:
                    self.bar_radar.itemconfig(self.poly_f_05, fill=self.color_lapdiff(veh_f_05[1], veh_plr[1]))
                if self.radar_add_behind > 1:
                    self.bar_radar.itemconfig(self.poly_r_05, fill=self.color_lapdiff(veh_r_05[1], veh_plr[1]))
                if self.radar_add_front > 2:
                    self.bar_radar.itemconfig(self.poly_f_06, fill=self.color_lapdiff(veh_f_06[1], veh_plr[1]))
                if self.radar_add_behind > 2:
                    self.bar_radar.itemconfig(self.poly_r_06, fill=self.color_lapdiff(veh_r_06[1], veh_plr[1]))
                if self.radar_add_front > 3:
                    self.bar_radar.itemconfig(self.poly_f_07, fill=self.color_lapdiff(veh_f_07[1], veh_plr[1]))
                if self.radar_add_behind > 3:
                    self.bar_radar.itemconfig(self.poly_r_07, fill=self.color_lapdiff(veh_r_07[1], veh_plr[1]))
                if self.radar_add_front > 4:
                    self.bar_radar.itemconfig(self.poly_f_08, fill=self.color_lapdiff(veh_f_08[1], veh_plr[1]))
                if self.radar_add_behind > 4:
                    self.bar_radar.itemconfig(self.poly_r_08, fill=self.color_lapdiff(veh_r_08[1], veh_plr[1]))
                if self.radar_add_front > 5:
                    self.bar_radar.itemconfig(self.poly_f_09, fill=self.color_lapdiff(veh_f_09[1], veh_plr[1]))
                if self.radar_add_behind > 5:
                    self.bar_radar.itemconfig(self.poly_r_09, fill=self.color_lapdiff(veh_r_09[1], veh_plr[1]))
                if self.radar_add_front > 6:
                    self.bar_radar.itemconfig(self.poly_f_10, fill=self.color_lapdiff(veh_f_10[1], veh_plr[1]))
                if self.radar_add_behind > 6:
                    self.bar_radar.itemconfig(self.poly_r_10, fill=self.color_lapdiff(veh_r_10[1], veh_plr[1]))
                if self.radar_add_front > 7:
                    self.bar_radar.itemconfig(self.poly_f_11, fill=self.color_lapdiff(veh_f_11[1], veh_plr[1]))
                if self.radar_add_behind > 7:
                    self.bar_radar.itemconfig(self.poly_r_11, fill=self.color_lapdiff(veh_r_11[1], veh_plr[1]))
                if self.radar_add_front > 8:
                    self.bar_radar.itemconfig(self.poly_f_12, fill=self.color_lapdiff(veh_f_12[1], veh_plr[1]))
                if self.radar_add_behind > 8:
                    self.bar_radar.itemconfig(self.poly_r_12, fill=self.color_lapdiff(veh_r_12[1], veh_plr[1]))

                # Update vehicle position
                self.bar_radar.coords(self.poly_f_01, self.update_veh_pos(veh_plr[0], veh_f_01[0], veh_f_01[2]))
                self.bar_radar.coords(self.poly_r_01, self.update_veh_pos(veh_plr[0], veh_r_01[0], veh_r_01[2]))
                self.bar_radar.coords(self.poly_f_02, self.update_veh_pos(veh_plr[0], veh_f_02[0], veh_f_02[2]))
                self.bar_radar.coords(self.poly_r_02, self.update_veh_pos(veh_plr[0], veh_r_02[0], veh_r_02[2]))
                self.bar_radar.coords(self.poly_f_03, self.update_veh_pos(veh_plr[0], veh_f_03[0], veh_f_03[2]))
                self.bar_radar.coords(self.poly_r_03, self.update_veh_pos(veh_plr[0], veh_r_03[0], veh_r_03[2]))

                if self.radar_add_front > 0:
                    self.bar_radar.coords(self.poly_f_04, self.update_veh_pos(veh_plr[0], veh_f_04[0], veh_f_04[2]))
                if self.radar_add_behind > 0:
                    self.bar_radar.coords(self.poly_r_04, self.update_veh_pos(veh_plr[0], veh_r_04[0], veh_r_04[2]))
                if self.radar_add_front > 1:
                    self.bar_radar.coords(self.poly_f_05, self.update_veh_pos(veh_plr[0], veh_f_05[0], veh_f_05[2]))
                if self.radar_add_behind > 1:
                    self.bar_radar.coords(self.poly_r_05, self.update_veh_pos(veh_plr[0], veh_r_05[0], veh_r_05[2]))
                if self.radar_add_front > 2:
                    self.bar_radar.coords(self.poly_f_06, self.update_veh_pos(veh_plr[0], veh_f_06[0], veh_f_06[2]))
                if self.radar_add_behind > 2:
                    self.bar_radar.coords(self.poly_r_06, self.update_veh_pos(veh_plr[0], veh_r_06[0], veh_r_06[2]))
                if self.radar_add_front > 3:
                    self.bar_radar.coords(self.poly_f_07, self.update_veh_pos(veh_plr[0], veh_f_07[0], veh_f_07[2]))
                if self.radar_add_behind > 3:
                    self.bar_radar.coords(self.poly_r_07, self.update_veh_pos(veh_plr[0], veh_r_07[0], veh_r_07[2]))
                if self.radar_add_front > 4:
                    self.bar_radar.coords(self.poly_f_08, self.update_veh_pos(veh_plr[0], veh_f_08[0], veh_f_08[2]))
                if self.radar_add_behind > 4:
                    self.bar_radar.coords(self.poly_r_08, self.update_veh_pos(veh_plr[0], veh_r_08[0], veh_r_08[2]))
                if self.radar_add_front > 5:
                    self.bar_radar.coords(self.poly_f_09, self.update_veh_pos(veh_plr[0], veh_f_09[0], veh_f_09[2]))
                if self.radar_add_behind > 5:
                    self.bar_radar.coords(self.poly_r_09, self.update_veh_pos(veh_plr[0], veh_r_09[0], veh_r_09[2]))
                if self.radar_add_front > 6:
                    self.bar_radar.coords(self.poly_f_10, self.update_veh_pos(veh_plr[0], veh_f_10[0], veh_f_10[2]))
                if self.radar_add_behind > 6:
                    self.bar_radar.coords(self.poly_r_10, self.update_veh_pos(veh_plr[0], veh_r_10[0], veh_r_10[2]))
                if self.radar_add_front > 7:
                    self.bar_radar.coords(self.poly_f_11, self.update_veh_pos(veh_plr[0], veh_f_11[0], veh_f_11[2]))
                if self.radar_add_behind > 7:
                    self.bar_radar.coords(self.poly_r_11, self.update_veh_pos(veh_plr[0], veh_r_11[0], veh_r_11[2]))
                if self.radar_add_front > 8:
                    self.bar_radar.coords(self.poly_f_12, self.update_veh_pos(veh_plr[0], veh_f_12[0], veh_f_12[2]))
                if self.radar_add_behind > 8:
                    self.bar_radar.coords(self.poly_r_12, self.update_veh_pos(veh_plr[0], veh_r_12[0], veh_r_12[2]))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # Additional methods
    def update_veh_pos(self, pos1, pos2, ori1):
        """Update vehicle coordinates"""
        # Relative distance towards player vehicle
        pos_x_diff = (pos1[0] - pos2[0]) * self.wcfg["vehicle_scale"] + self.base_size
        pos_y_diff = (pos1[1] - pos2[1]) * self.wcfg["vehicle_scale"] + self.base_size

        # Rotate opponent vehicle coordinates
        coord1 = calc.rotate_pos(ori1, -self.veh_width, -self.veh_length)
        coord2 = calc.rotate_pos(ori1, self.veh_width, -self.veh_length)
        coord3 = calc.rotate_pos(ori1, self.veh_width, self.veh_length)
        coord4 = calc.rotate_pos(ori1, -self.veh_width, self.veh_length)

        # Set new position coordinates
        new_veh_pos = (
                        (pos_y_diff - coord1[0]),  # coord 1
                        (pos_x_diff - coord1[1]),
                        (pos_y_diff - coord2[0]),  # coord 2
                        (pos_x_diff - coord2[1]),
                        (pos_y_diff - coord3[0]),  # coord 3
                        (pos_x_diff - coord3[1]),
                        (pos_y_diff - coord4[0]),  # coord 4
                        (pos_x_diff - coord4[1])
                      )
        return new_veh_pos

    def color_lapdiff(self, nlap, player_nlap):
        """Compare lap differences & set color"""
        if nlap > player_nlap:
            color = self.wcfg["opponent_color_laps_ahead"]
        elif nlap < player_nlap:
            color = self.wcfg["opponent_color_laps_behind"]
        else:
            color = self.wcfg["opponent_color"]
        return color
