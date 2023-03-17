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

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget, MouseEvent
from ..module_control import module

WIDGET_NAME = "radar"


class Draw(Widget, MouseEvent):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        self.base_size = max(self.wcfg["radar_radius"], 5) * 10 * self.wcfg["radar_scale"]
        self.veh_width = max(int(self.wcfg["vehicle_width"] * 5 * self.wcfg["radar_scale"]), 1)
        self.veh_length = max(int(self.wcfg["vehicle_length"] * 5 * self.wcfg["radar_scale"]), 2)

        # Coordinates for drawing player vehicle
        plr_rect_coord = (self.base_size - self.veh_width,
                          self.base_size - self.veh_length,
                          self.base_size + self.veh_width,
                          self.base_size + self.veh_length)

        # Max visible vehicles
        self.veh_add_front = min(max(self.wcfg["additional_vehicles_front"], 0), 60)
        self.veh_add_behind = min(max(self.wcfg["additional_vehicles_behind"], 0), 60)
        self.veh_range = max(4, self.veh_add_front + 4, self.veh_add_behind + 4)

        # Draw widget
        self.bar_radar = tk.Canvas(self, bd=0, highlightthickness=0,
                                   height=int(self.base_size * 2),
                                   width=int(self.base_size * 2),
                                   bg=self.wcfg["bkg_color"])
        self.bar_radar.grid(row=0, column=0, padx=0, pady=0)

        if self.wcfg["show_center_mark"]:
            mark_scale = self.wcfg["center_mark_radius"] * 10 * self.wcfg["radar_scale"]
            self.bar_radar.create_line(self.base_size,
                                       self.base_size - mark_scale,
                                       self.base_size,
                                       self.base_size + mark_scale - 1,
                                       fill=self.wcfg["center_mark_color"], dash=(2, 2))
            self.bar_radar.create_line(self.base_size - mark_scale,
                                       self.base_size,
                                       self.base_size + mark_scale - 1,
                                       self.base_size,
                                       fill=self.wcfg["center_mark_color"], dash=(2, 2))

        if self.wcfg["show_distance_circle"]:
            circle_scale1 = self.wcfg["distance_circle_1_radius"] * 10 * self.wcfg["radar_scale"]
            if self.wcfg["distance_circle_1_radius"] < self.wcfg["radar_radius"]:
                self.bar_radar.create_oval(self.base_size - circle_scale1,
                                           self.base_size - circle_scale1,
                                           self.base_size + circle_scale1 - 1,
                                           self.base_size + circle_scale1 - 1,
                                           fill="", dash=(2, 2),
                                           outline=self.wcfg["distance_circle_color"])
            circle_scale2 = self.wcfg["distance_circle_2_radius"] * 10 * self.wcfg["radar_scale"]
            if self.wcfg["distance_circle_2_radius"] < self.wcfg["radar_radius"]:
                self.bar_radar.create_oval(self.base_size - circle_scale2,
                                           self.base_size - circle_scale2,
                                           self.base_size + circle_scale2 - 1,
                                           self.base_size + circle_scale2 - 1,
                                           fill="", dash=(2, 2),
                                           outline=self.wcfg["distance_circle_color"])

        self.poly_plr = self.bar_radar.create_rectangle(
                        plr_rect_coord,
                        fill=self.wcfg["player_color"],
                        outline=self.wcfg["player_outline_color"],
                        width=max(self.wcfg["player_outline_width"], 0))

        poly_style = {"fill":self.wcfg["opponent_color"], "outline":""}

        for idx in range(1, self.veh_range):
            if idx < self.veh_add_front + 4:
                # Draw vehicles: poly_f_**
                setattr(self, f"poly_f_{idx}",
                        self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
                        )
                # Last data
                setattr(self, f"last_veh_lap_f_{idx}", None)
                setattr(self, f"last_veh_pos_f_{idx}", None)

            if idx < self.veh_add_behind + 4:
                # Draw vehicles
                setattr(self, f"poly_r_{idx}",
                        self.bar_radar.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, poly_style)
                        )
                # Last data
                setattr(self, f"last_veh_lap_r_{idx}", None)
                setattr(self, f"last_veh_pos_r_{idx}", None)

        # Last data
        self.autohide_timer_start = 1

        # Start updating
        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and module.relative_info.relative_list and self.wcfg["enable"]:

            # Read relative list player index
            rel_idx = module.relative_info.radar_list

            # Read orientation & position data
            veh_center = int(3 + self.veh_add_front)
            veh_gps = module.relative_info.vehicle_gps(rel_idx, rel_idx[veh_center])

            # Auto hide radar if no nearby vehicles
            if self.wcfg["auto_hide"]:
                self.autohide_radar()

            # Data index reference:
            # 1 position coordinates, 2 orientation, 3 is lapped
            # Set player vehicle data
            veh_plr_pos = module.relative_info.radar_pos(
                                veh_gps[veh_center], veh_gps[veh_center], rel_idx[veh_center])[0]

            # Set opponent vehicle data: veh_f_**
            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    setattr(self, f"veh_f_{idx}",
                            module.relative_info.radar_pos(
                                veh_gps[veh_center],        # player position
                                veh_gps[veh_center - idx],  # opponent position
                                rel_idx[veh_center - idx]   # relative index
                                )
                            )
                if idx < self.veh_add_behind + 4:
                    setattr(self, f"veh_r_{idx}",
                            module.relative_info.radar_pos(
                                veh_gps[veh_center],
                                veh_gps[veh_center + idx],
                                rel_idx[veh_center + idx]
                                )
                            )

            # Vehicle color
            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    self.update_color(f"f_{idx}",
                                      getattr(self, f"veh_f_{idx}")[2],  # is_lapped
                                      getattr(self, f"last_veh_lap_f_{idx}")
                                      )
                    setattr(self, f"last_veh_lap_f_{idx}",
                            getattr(self, f"veh_f_{idx}")[2])

                if idx < self.veh_add_behind + 4:
                    self.update_color(f"r_{idx}",
                                      getattr(self, f"veh_r_{idx}")[2],
                                      getattr(self, f"last_veh_lap_r_{idx}")
                                      )
                    setattr(self, f"last_veh_lap_r_{idx}",
                            getattr(self, f"veh_r_{idx}")[2])

            # Vehicle position
            for idx in range(1, self.veh_range):
                if idx < self.veh_add_front + 4:
                    setattr(self, f"veh_pos_f_{idx}",  # update coordinates data
                            self.update_veh_pos(
                                veh_plr_pos,
                                getattr(self, f"veh_f_{idx}")[0],
                                getattr(self, f"veh_f_{idx}")[1]
                                )
                            )
                    self.update_position(f"f_{idx}",  # update vehicle position
                                         getattr(self, f"veh_pos_f_{idx}"),
                                         getattr(self, f"last_veh_pos_f_{idx}")
                                         )
                    setattr(self, f"last_veh_pos_f_{idx}",
                            getattr(self, f"veh_pos_f_{idx}"))

                if idx < self.veh_add_behind + 4:
                    setattr(self, f"veh_pos_r_{idx}",
                            self.update_veh_pos(
                                veh_plr_pos,
                                getattr(self, f"veh_r_{idx}")[0],
                                getattr(self, f"veh_r_{idx}")[1]
                                )
                            )
                    self.update_position(f"r_{idx}",
                                         getattr(self, f"veh_pos_r_{idx}"),
                                         getattr(self, f"last_veh_pos_r_{idx}")
                                         )
                    setattr(self, f"last_veh_pos_r_{idx}",
                            getattr(self, f"veh_pos_r_{idx}"))

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)

    # GUI update methods
    def update_color(self, suffix, curr, last):
        """Vehicle color based on lap difference"""
        if curr != last:
            self.bar_radar.itemconfig(
                getattr(self, f"poly_{suffix}"), fill=self.color_lapdiff(curr))

    def update_position(self, suffix, curr, last):
        """Vehicle position"""
        if curr != last:
            self.bar_radar.coords(
                getattr(self, f"poly_{suffix}"), curr)

    # Additional methods
    def update_veh_pos(self, plr_pos, opt_pos, opt_ori):
        """Update vehicle coordinates"""
        # Relative distance towards player vehicle
        pos_x_diff = (plr_pos[0] - opt_pos[0]) * self.wcfg["radar_scale"] + self.base_size
        pos_y_diff = (plr_pos[1] - opt_pos[1]) * self.wcfg["radar_scale"] + self.base_size

        # Rotate opponent vehicle coordinates
        coord1 = calc.rotate_pos(opt_ori, -self.veh_width, -self.veh_length)
        coord2 = calc.rotate_pos(opt_ori, self.veh_width, -self.veh_length)
        coord3 = calc.rotate_pos(opt_ori, self.veh_width, self.veh_length)
        coord4 = calc.rotate_pos(opt_ori, -self.veh_width, self.veh_length)

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

    def color_lapdiff(self, is_lapped):
        """Compare lap differences & set color"""
        if is_lapped > 0:
            return self.wcfg["opponent_color_laps_ahead"]
        if is_lapped < 0:
            return self.wcfg["opponent_color_laps_behind"]
        return self.wcfg["opponent_color"]

    def autohide_radar(self):
        """Auto hide radar if no nearby vehicles"""
        lap_etime, ingarage = read_data.radar()

        if self.nearby() or ingarage:
            if not self.autohide_timer_start:
                self.bar_radar.grid()
            self.autohide_timer_start = lap_etime

        if self.autohide_timer_start:
            autohide_timer = lap_etime - self.autohide_timer_start
            if autohide_timer > self.wcfg["auto_hide_time_threshold"]:
                self.bar_radar.grid_remove()
                self.autohide_timer_start = 0

    def nearby(self):
        """Check nearby vehicles"""
        if self.wcfg["minimum_auto_hide_distance"] == -1:
            return module.relative_info.nearest_opt_dist < self.wcfg["radar_radius"]
        return module.relative_info.nearest_opt_dist < self.wcfg["minimum_auto_hide_distance"]
