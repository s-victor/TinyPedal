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

            # Read relative list player index
            rel_idx = relative_info.relative_list[0]

            # Read orientation & position data
            veh_gps = relative_info.vehicle_gps(rel_idx)

            # Check isPlayer before update
            if read_data.is_local_player():

                # Read vehicle position coordinates, lap number, orientation
                veh_a = relative_info.radar_pos(veh_gps[3], veh_gps[0], rel_idx[0])
                veh_b = relative_info.radar_pos(veh_gps[3], veh_gps[1], rel_idx[1])
                veh_c = relative_info.radar_pos(veh_gps[3], veh_gps[2], rel_idx[2])
                veh_d = relative_info.radar_pos(veh_gps[3], veh_gps[3], rel_idx[3])
                veh_e = relative_info.radar_pos(veh_gps[3], veh_gps[4], rel_idx[4])
                veh_f = relative_info.radar_pos(veh_gps[3], veh_gps[5], rel_idx[5])
                veh_g = relative_info.radar_pos(veh_gps[3], veh_gps[6], rel_idx[6])

                # Set vehicle color
                self.bar_radar.itemconfig(self.poly_veh1,
                                          fill=self.color_lapdiff(veh_a[1], veh_d[1]))
                self.bar_radar.itemconfig(self.poly_veh2,
                                          fill=self.color_lapdiff(veh_b[1], veh_d[1]))
                self.bar_radar.itemconfig(self.poly_veh3,
                                          fill=self.color_lapdiff(veh_c[1], veh_d[1]))
                self.bar_radar.itemconfig(self.poly_veh5,
                                          fill=self.color_lapdiff(veh_e[1], veh_d[1]))
                self.bar_radar.itemconfig(self.poly_veh6,
                                          fill=self.color_lapdiff(veh_f[1], veh_d[1]))
                self.bar_radar.itemconfig(self.poly_veh7,
                                          fill=self.color_lapdiff(veh_g[1], veh_d[1]))

                # Update vehicle position
                self.bar_radar.coords(self.poly_veh1,
                                      self.update_veh_pos(veh_d[0], veh_a[0], veh_a[2]))
                self.bar_radar.coords(self.poly_veh2,
                                      self.update_veh_pos(veh_d[0], veh_b[0], veh_b[2]))
                self.bar_radar.coords(self.poly_veh3,
                                      self.update_veh_pos(veh_d[0], veh_c[0], veh_c[2]))
                self.bar_radar.coords(self.poly_veh5,
                                      self.update_veh_pos(veh_d[0], veh_e[0], veh_e[2]))
                self.bar_radar.coords(self.poly_veh6,
                                      self.update_veh_pos(veh_d[0], veh_f[0], veh_f[2]))
                self.bar_radar.coords(self.poly_veh7,
                                      self.update_veh_pos(veh_d[0], veh_g[0], veh_g[2]))

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
