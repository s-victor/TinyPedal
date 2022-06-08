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

from tinypedal.__init__ import cfg
import tinypedal.readapi as read_data
from tinypedal.base import relative_info, Widget, MouseEvent
import tinypedal.calculation as calc


class DrawWidget(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "radar"
    cfg = cfg.setting_user[widget_name]

    def __init__(self):
        # Assign base setting
        Widget.__init__(self)

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.cfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.cfg['position_x']}+{self.cfg['position_y']}")

        self.base_size = 100 * max(self.cfg["area_scale"], 0.5)
        self.veh_width = max(int(self.cfg["vehicle_width"] * 5 * self.cfg["vehicle_scale"]), 1)
        self.veh_length = max(int(self.cfg["vehicle_length"] * 5 * self.cfg["vehicle_scale"]), 2)

        # Coordinates for drawing player vehicle
        plr_rect_coord = (self.base_size - self.veh_width,
                          self.base_size - self.veh_length,
                          self.base_size + self.veh_width,
                          self.base_size + self.veh_length)

        # Draw widget
        self.bar_radar = tk.Canvas(self, bd=0, highlightthickness=0,
                                   height=int(self.base_size * 2),
                                   width=int(self.base_size * 2),
                                   bg=self.cfg["bkg_color"])
        self.bar_radar.grid(row=0, column=0, padx=0, pady=0)

        if self.cfg["show_center_mark"]:
            self.bar_radar.create_line(self.base_size, 0, self.base_size, self.base_size * 2,
                                       fill=self.cfg["center_mark_color"], dash=(2, 2))
            self.bar_radar.create_line(0, self.base_size, self.base_size * 2, self.base_size,
                                       fill=self.cfg["center_mark_color"], dash=(2, 2))

        self.poly_veh_plr = self.bar_radar.create_rectangle(
                                plr_rect_coord,
                                fill=self.cfg["player_color"],
                                outline=self.cfg["player_outline_color"],
                                width=max(self.cfg["player_outline_width"], 0))

        poly_style = {"fill":self.cfg["opponent_color"], "outline":""}

        self.poly_veh1 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_veh2 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_veh3 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_veh5 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_veh6 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
        self.poly_veh7 = self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and relative_info.relative_list and self.cfg["enable"]:

            # Read orientation data
            ply_ori_rad = relative_info.orientation()

            # Read relative list player index
            rel_list = relative_info.relative_list[0]

            # Check isPlayer before update
            if read_data.is_local_player():

                # Read vehicle coordinates, lap number, orientation
                veh1_pos, veh1_lap, veh1_ori = relative_info.radar_pos(ply_ori_rad, rel_list[0])
                veh2_pos, veh2_lap, veh2_ori = relative_info.radar_pos(ply_ori_rad, rel_list[1])
                veh3_pos, veh3_lap, veh3_ori = relative_info.radar_pos(ply_ori_rad, rel_list[2])
                veh5_pos, veh5_lap, veh5_ori = relative_info.radar_pos(ply_ori_rad, rel_list[4])
                veh6_pos, veh6_lap, veh6_ori = relative_info.radar_pos(ply_ori_rad, rel_list[5])
                veh7_pos, veh7_lap, veh7_ori = relative_info.radar_pos(ply_ori_rad, rel_list[6])
                plr_pos, plr_lap, _ = relative_info.radar_pos(ply_ori_rad, rel_list[3])

                # Set vehicle color
                self.bar_radar.itemconfig(self.poly_veh1,
                                          fill=self.color_lapdiff(veh1_lap, plr_lap))
                self.bar_radar.itemconfig(self.poly_veh2,
                                          fill=self.color_lapdiff(veh2_lap, plr_lap))
                self.bar_radar.itemconfig(self.poly_veh3,
                                          fill=self.color_lapdiff(veh3_lap, plr_lap))
                self.bar_radar.itemconfig(self.poly_veh5,
                                          fill=self.color_lapdiff(veh5_lap, plr_lap))
                self.bar_radar.itemconfig(self.poly_veh6,
                                          fill=self.color_lapdiff(veh6_lap, plr_lap))
                self.bar_radar.itemconfig(self.poly_veh7,
                                          fill=self.color_lapdiff(veh7_lap, plr_lap))

                # Update vehicle position
                self.bar_radar.coords(self.poly_veh1,
                                      self.update_veh_pos(plr_pos, veh1_pos, veh1_ori))
                self.bar_radar.coords(self.poly_veh2,
                                      self.update_veh_pos(plr_pos, veh2_pos, veh2_ori))
                self.bar_radar.coords(self.poly_veh3,
                                      self.update_veh_pos(plr_pos, veh3_pos, veh3_ori))
                self.bar_radar.coords(self.poly_veh5,
                                      self.update_veh_pos(plr_pos, veh5_pos, veh5_ori))
                self.bar_radar.coords(self.poly_veh6,
                                      self.update_veh_pos(plr_pos, veh6_pos, veh6_ori))
                self.bar_radar.coords(self.poly_veh7,
                                      self.update_veh_pos(plr_pos, veh7_pos, veh7_ori))

        # Update rate
        self.after(self.cfg["update_delay"], self.update_data)

    # Additional methods
    def update_veh_pos(self, pos1, pos2, ori1):
        """Update vehicle coordinates"""
        # Relative distance towards player vehicle
        pos_x_diff = (pos1[0] - pos2[0]) * self.cfg["vehicle_scale"] + self.base_size
        pos_y_diff = (pos1[1] - pos2[1]) * self.cfg["vehicle_scale"] + self.base_size

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
            color = self.cfg["opponent_color_laps_ahead"]
        elif nlap < player_nlap:
            color = self.cfg["opponent_color_laps_behind"]
        else:
            color = self.cfg["opponent_color"]
        return color
