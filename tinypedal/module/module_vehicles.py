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
Vehicles module
"""

import logging

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_vehicles"
ALL_INDEXES = list(range(128))

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Vehicles info"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self.event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    minfo.vehicles.dataSetVersion = -1
                    max_lap_diff_ahead = self.mcfg["lap_difference_ahead_threshold"]
                    max_lap_diff_behind = self.mcfg["lap_difference_behind_threshold"]

                self.__update_vehicle_data(
                    minfo.vehicles.dataSet,
                    minfo.relative.classes,
                    max_lap_diff_ahead,
                    max_lap_diff_behind
                )

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

    def __update_vehicle_data(
        self, veh_info, class_pos_list, max_lap_diff_ahead, max_lap_diff_behind):
        """Update vehicle data"""
        veh_total = api.read.vehicle.total_vehicles()
        if veh_total < 1:
            return

        # General data
        track_length = api.read.lap.track_length()
        in_race = api.read.session.in_race()
        class_list_size = len(class_pos_list)
        draw_order = ALL_INDEXES[:veh_total]

        # Local player data
        nearest_line = 999999
        nearest_timegap = 999999
        nearest_yellow = 999999

        # Sorting reference index
        leader_idx = 0
        player_idx = -1  # local player may not exist, init with -1
        inpit_idx = 0

        # Update dataset from all vehicles in current session
        for index, data in enumerate(veh_info):
            if index >= veh_total:
                break

            # Vehicle class var
            if index < class_list_size:
                data.positionInClass = class_pos_list[index][1]
                data.sessionBestLapTime = class_pos_list[index][3]
                data.classBestLapTime = class_pos_list[index][4]
                opt_index_ahead = class_pos_list[index][5]
            else:
                opt_index_ahead = -1

            # Output var only
            data.driverName = api.read.vehicle.driver_name(index)
            data.vehicleName = api.read.vehicle.vehicle_name(index)
            data.vehicleClass = api.read.vehicle.class_name(index)
            data.gapBehindNext = calc_gap_behind_next(index)
            data.gapBehindLeader = calc_gap_behind_leader(index)
            data.bestLapTime = api.read.timing.best_laptime(index)
            data.lastLapTime = api.read.timing.last_laptime(index)
            data.numPitStops = api.read.vehicle.number_pitstops(index)
            data.pitState = api.read.vehicle.pit_state(index)
            data.tireCompound[0] = api.read.tyre.compound_front(index)
            data.tireCompound[1] = api.read.tyre.compound_rear(index)

            # Temp var only
            lap_etime = api.read.timing.elapsed(index)
            speed = api.read.vehicle.speed(index)
            laps_done = api.read.lap.completed_laps(index)
            lap_distance = api.read.lap.distance(index)

            # Temp & output var
            is_player = data.isPlayer = api.read.vehicle.is_player(index)
            position_overall = data.positionOverall = api.read.vehicle.place(index)
            in_pit = data.inPit = min(  #  value 0 = not in pit, 1 = in pit, 2 = in garage
                api.read.vehicle.in_pits(index) + api.read.vehicle.in_garage(index) * 2, 2)
            is_yellow = data.isYellow = speed < 8
            lap_progress = data.lapProgress = calc.lap_progress_distance(lap_distance, track_length)

            data.gapBehindNextInClass = calc_gap_behind_next_in_class(
                opt_index_ahead, track_length, speed, laps_done, lap_progress)
            calc_pit_time(data.pitTimer, in_pit, lap_etime)

            # Position & relative data
            if is_player:
                relative_distance = 0
                data.posXY[0] = api.read.vehicle.position_longitudinal(index)
                data.posXY[1] = api.read.vehicle.position_lateral(index)

            else:
                # Relative position & orientation
                plr_ori_yaw = api.read.vehicle.orientation_yaw_radians()
                opt_ori_yaw = api.read.vehicle.orientation_yaw_radians(index)
                plr_pos_x = api.read.vehicle.position_longitudinal()
                plr_pos_y = api.read.vehicle.position_lateral()
                opt_pos_x = data.posXY[0] = api.read.vehicle.position_longitudinal(index)
                opt_pos_y = data.posXY[1] = api.read.vehicle.position_lateral(index)

                data.relativeOrientationXYRadians = opt_ori_yaw - plr_ori_yaw
                data.relativeRotatedPosXY[0], data.relativeRotatedPosXY[1] = calc.rotate_coordinate(
                    plr_ori_yaw - 3.14159265,  # plr_ori_rad, rotate view
                    opt_pos_x - plr_pos_x,     # x position related to player
                    opt_pos_y - plr_pos_y)     # y position related to player

                # Relative distance & time gap
                relative_straight_distance = data.relativeStraightDistance = calc.distance(
                    (plr_pos_x, plr_pos_y), (opt_pos_x, opt_pos_y))
                plr_lap_distance = api.read.lap.distance()
                plr_lap_progress = calc.lap_progress_distance(plr_lap_distance, track_length)
                plr_laps_done = api.read.lap.completed_laps()
                relative_distance = calc.circular_relative_distance(
                    track_length, plr_lap_distance, lap_distance)
                data.isLapped = calc.lap_difference(
                    laps_done + lap_progress, plr_laps_done + plr_lap_progress,
                    max_lap_diff_ahead, max_lap_diff_behind
                ) if in_race else 0
                relative_time_gap = data.relativeTimeGap = calc.relative_time_gap(
                    relative_distance, speed, api.read.vehicle.speed())

                # Nearest straight line distance (non local players)
                if relative_straight_distance < nearest_line:
                    nearest_line = relative_straight_distance
                # Nearest traffic time gap (non local players)
                if 0 == in_pit > relative_distance and relative_time_gap < nearest_timegap:
                    nearest_timegap = relative_time_gap

            # Nearest yellow flag distance (all players)
            if is_yellow:
                rel_dist = abs(relative_distance)
                if rel_dist < nearest_yellow:
                    nearest_yellow = rel_dist

            # Sort draw order list in loop ->
            if position_overall == 1:  # save leader index
                leader_idx = draw_order[index]
            elif is_player:  # save local player index
                player_idx = draw_order[index]
            elif in_pit:  # swap opponent in pit/garage to start
                draw_order[index], draw_order[inpit_idx] = draw_order[inpit_idx], draw_order[index]
                inpit_idx += 1

        # Finalize draw order list ->
        # Move leader to end of draw order
        if leader_idx != draw_order[-1]:
            leader_pos = draw_order.index(leader_idx)
            draw_order[leader_pos], draw_order[-1] = draw_order[-1], draw_order[leader_pos]
        # Move local player to 2nd end of draw order, local player could be leader, compare first
        if player_idx != -1 and player_idx != leader_idx:
            player_pos = draw_order.index(player_idx)
            draw_order[player_pos], draw_order[-2] = draw_order[-2], draw_order[player_pos]
        # <- End draw order list

        # Output extra info
        minfo.vehicles.nearestLine = nearest_line
        minfo.vehicles.nearestTraffic = nearest_timegap
        minfo.vehicles.nearestYellow = nearest_yellow
        minfo.vehicles.drawOrder = draw_order
        minfo.vehicles.dataSetVersion += 1


def calc_pit_time(pit_timer: list, in_pit: int, lap_etime: float):
    """Calculate lap & pit time

    Pit timer list indexes:
        0 = in pit state (value 0 = not in pit, 1 = in pit, 2 = in garage)
        1 = pit start time
        2 = pit timer
    """
    # Pit status check
    if in_pit != pit_timer[0]:
        pit_timer[0] = in_pit  # last pit status
        pit_timer[1] = lap_etime  # last etime stamp
        #if in_pit:  # reset pit time if just entered pit
        #    pit_timer[2] = 0
    # Ignore pit timer in garage
    if in_pit == 2:
        pit_timer[1] = -1
        pit_timer[2] = 0
        return
    # Calculating pit time while in pit
    if in_pit:
        if pit_timer[1] >= 0:
            pit_timer[2] = lap_etime - pit_timer[1]


def calc_gap_behind_next_in_class(
    opt_index, track_length, speed, laps_done, lap_progress):
    """Calculate interval behind next in class"""
    if opt_index < 0:
        return 0.0
    opt_laps_done = api.read.lap.completed_laps(opt_index)
    opt_lap_distance = api.read.lap.distance(opt_index)
    opt_lap_progress = calc.lap_progress_distance(opt_lap_distance, track_length)
    lap_diff = abs(opt_laps_done + opt_lap_progress - laps_done - lap_progress)
    if lap_diff > 1:
        return int(lap_diff)
    return calc.relative_time_gap(
        lap_diff * track_length, api.read.vehicle.speed(opt_index), speed
    )


def calc_gap_behind_next(index):
    """Calculate interval behind next"""
    laps_behind_next = api.read.lap.behind_next(index)
    if laps_behind_next > 0:
        return laps_behind_next
    return api.read.timing.behind_next(index)


def calc_gap_behind_leader(index):
    """Calculate interval behind leader"""
    laps_behind_leader = api.read.lap.behind_leader(index)
    if laps_behind_leader > 0:
        return laps_behind_leader
    return api.read.timing.behind_leader(index)
