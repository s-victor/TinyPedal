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

import array
import logging
from collections import namedtuple

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_vehicles"

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Vehicles info"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)
        self.pit_timer = tuple(array.array("f", [0,-1,0]) for _ in range(128))

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    minfo.vehicles.dataSetVersion = -1

                vehicles_data = tuple(self.__update_vehicle_data(minfo.relative.classes))
                nearest_timegap, nearest_yellow = nearest_distance_data(vehicles_data)

                # Output
                minfo.vehicles.dataSet = vehicles_data
                minfo.vehicles.dataSetVersion += 1
                minfo.vehicles.nearestTraffic = nearest_timegap
                minfo.vehicles.nearestYellow = nearest_yellow

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

    def __update_vehicle_data(self, class_pos_list):
        """Update vehicle data"""
        # Additional data
        veh_total = max(api.read.vehicle.total_vehicles(), 1)
        track_length = api.read.lap.track_length()
        in_race = api.read.session.in_race()
        class_list_size = len(class_pos_list)

        # Local player data
        plr_total_laps = api.read.lap.total_laps()
        plr_lap_distance = api.read.lap.distance()
        plr_lap_progress = calc.lap_distance_progress(plr_lap_distance, track_length)
        plr_speed = api.read.vehicle.speed()
        plr_pos_xz = (api.read.vehicle.position_longitudinal(),
                      api.read.vehicle.position_lateral())
        plr_ori_rad = api.read.vehicle.orientation_yaw_radians()

        # Generate data list from all vehicles in current session
        for index in range(veh_total):
            is_player = api.read.vehicle.is_player(index)
            slot_id = api.read.vehicle.slot_id(index)
            position = api.read.vehicle.place(index)
            driver_name = api.read.vehicle.driver_name(index)
            vehicle_name = api.read.vehicle.vehicle_name(index)
            vehicle_class = api.read.vehicle.class_name(index)

            if index < class_list_size:
                position_in_class = class_pos_list[index][1]
                laptime_session_best = class_pos_list[index][3]
                laptime_class_best = class_pos_list[index][4]
                opt_index_ahead = class_pos_list[index][5]
            else:
                position_in_class = 0
                laptime_session_best = 99999
                laptime_class_best = 99999
                opt_index_ahead = -1

            laptime_best = api.read.timing.best_laptime(index)
            laptime_last = api.read.timing.last_laptime(index)
            lap_etime = api.read.timing.elapsed(index)
            speed = api.read.vehicle.speed(index)

            # Distance & time
            total_laps = api.read.lap.total_laps(index)
            lap_distance = api.read.lap.distance(index)

            lap_progress = calc.lap_distance_progress(lap_distance, track_length)
            relative_distance = calc.circular_relative_distance(
                track_length, plr_lap_distance, lap_distance
                ) if not is_player else 0
            relative_time_gap = calc.relative_time_gap(
                relative_distance, speed, plr_speed
                ) if not is_player else 0

            gap_behind_next_in_class = self.__calc_gap_behind_next_in_class(
                opt_index_ahead, track_length, speed, total_laps, lap_progress)
            gap_behind_next = self.__calc_gap_behind_next(index)
            gap_behind_leader = self.__calc_gap_behind_leader(index)

            is_lapped = 0 if is_player or not in_race else calc.lap_difference(
                total_laps + lap_progress,
                plr_total_laps + plr_lap_progress,
                self.mcfg["lap_difference_ahead_threshold"],
                self.mcfg["lap_difference_behind_threshold"]
                )
            is_yellow = speed < 8

            # Pit
            in_garage = api.read.vehicle.in_garage(index)
            in_pit = api.read.vehicle.in_pits(index)
            num_pit_stops = api.read.vehicle.number_pitstops(index)
            pit_state = api.read.vehicle.pit_state(index)
            pit_time = self.__calc_pit_time(
                self.pit_timer[index], in_pit, in_garage, laptime_last, lap_etime,
                in_pit * 1000 + slot_id)
            tire_compound = api.read.tyre.compound(index)

            # Position data
            pos_xz = (api.read.vehicle.position_longitudinal(index),
                      api.read.vehicle.position_lateral(index))
            orientation_xz_radians = api.read.vehicle.orientation_yaw_radians(index)
            relative_rotated_pos_xz = calc.rotate_pos(
                plr_ori_rad - 3.14159265,   # plr_ori_rad, rotate view
                pos_xz[0] - plr_pos_xz[0],  # x position related to player
                pos_xz[1] - plr_pos_xz[1]   # y position related to player
                ) if not is_player else (0,0)
            relative_orientation_xz_radians = (
                orientation_xz_radians - plr_ori_rad
                ) if not is_player else 0
            relative_straight_distance = calc.distance(
                plr_pos_xz, pos_xz
                ) if not is_player else 0

            yield DataSet(
                position = position,
                driverName = driver_name,
                vehicleName = vehicle_name,
                vehicleClass = vehicle_class,
                positionInClass = position_in_class,
                sessionBestLapTime = laptime_session_best,
                classBestLapTime = laptime_class_best,
                bestLapTime = laptime_best,
                lastLapTime = laptime_last,
                isPlayer = is_player,
                isNotPlayer = not is_player,
                lapProgress = lap_progress,
                relativeDistance = relative_distance,
                relativeTimeGap = relative_time_gap,
                gapBehindNextInClass = gap_behind_next_in_class,
                gapBehindNext = gap_behind_next,
                gapBehindLeader = gap_behind_leader,
                isLapped = is_lapped,
                isYellow = is_yellow,
                inGarage = in_garage,
                inPit = in_pit,
                numPitStops = num_pit_stops,
                pitState = pit_state,
                pitTime = pit_time,
                tireCompound = tire_compound,
                posXZ = pos_xz,
                relativeOrientationXZRadians = relative_orientation_xz_radians,
                relativeRotatedPosXZ = relative_rotated_pos_xz,
                relativeStraightDistance = relative_straight_distance,
                #slotID = slot_id,
                #speed = speed,
                #totalLaps = total_laps,
                #lapDistance = lap_distance,
                #orientationXZRadians = orientation_xz_radians,
            )

    @staticmethod
    def __calc_pit_time(pit_timer, in_pit, in_garage, laptime_last, lap_etime, pit_status):
        """Calculate lap & pit time

        Index:
            0 = in pit state
            1 = pit start time
            2 = pit timer
        """
        # Pit status check
        if pit_status != pit_timer[0]:
            pit_timer[0] = pit_status  # last pit status
            pit_timer[1] = lap_etime  # last etime stamp
        # Ignore pit timer in garage
        if in_garage:
            pit_timer[1] = -1
            pit_timer[2] = 0
            return 0
        # Calculating pit time while in pit
        if in_pit:
            if pit_timer[1] >= 0:
                pit_timer[2] = min(max(lap_etime - pit_timer[1], 0), 999.9)
        # Reset pit time if made a valid lap time after pitting
        else:
            if pit_timer[2] and laptime_last > 0:
                pit_timer[2] = 0
        return pit_timer[2]

    @staticmethod
    def __calc_gap_behind_next_in_class(
        opt_index, track_length, speed, total_laps, lap_progress):
        """Calculate interval behind next in class"""
        if opt_index < 0:
            return 0.0
        opt_total_laps = api.read.lap.total_laps(opt_index)
        opt_lap_distance = api.read.lap.distance(opt_index)
        opt_lap_progress = calc.lap_distance_progress(opt_lap_distance, track_length)
        lap_diff = abs(opt_total_laps + opt_lap_progress - total_laps - lap_progress)
        if lap_diff > 1:
            return int(lap_diff)
        return calc.relative_time_gap(
            lap_diff * track_length, api.read.vehicle.speed(opt_index), speed
        )

    @staticmethod
    def __calc_gap_behind_next(index):
        """Calculate interval behind next"""
        laps_behind_next = api.read.lap.behind_next(index)
        if laps_behind_next > 0:
            return laps_behind_next
        return api.read.timing.behind_next(index)

    @staticmethod
    def __calc_gap_behind_leader(index):
        """Calculate interval behind leader"""
        laps_behind_leader = api.read.lap.behind_leader(index)
        if laps_behind_leader > 0:
            return laps_behind_leader
        return api.read.timing.behind_leader(index)


def nearest_distance_data(
    vehicle_data: tuple,
    nearest_timegap: int = 999999,
    nearest_yellow: int = 999999):
    """Calculate nearest distance data"""
    for data in vehicle_data:
        # Find nearest straight line distance
        #if not data.isPlayer and data.relativeStraightDistance < nearest_dist:
        #    nearest_dist = data.relativeStraightDistance
        # Find nearest traffic time gap
        if 0 == data.inPit > data.relativeDistance and data.relativeTimeGap < nearest_timegap:
            nearest_timegap = data.relativeTimeGap
        # Find nearest yellow flag (on track) distance
        if data.isYellow:
            rel_dist = abs(data.relativeDistance)
            if rel_dist < nearest_yellow:
                nearest_yellow = rel_dist
    return nearest_timegap, nearest_yellow


DataSet = namedtuple(
    "DataSet",
    [
    # Sorting priority section (for track map display, set reverse sort)
    "isNotPlayer",
    "inGarage",
    "inPit",
    "position",
    # End of sorting priority section
    "driverName",
    "vehicleName",
    "vehicleClass",
    "positionInClass",
    "sessionBestLapTime",
    "classBestLapTime",
    "bestLapTime",
    "lastLapTime",
    "isPlayer",
    "lapProgress",
    "relativeDistance",
    "relativeTimeGap",
    "gapBehindNextInClass",
    "gapBehindNext",
    "gapBehindLeader",
    "isLapped",
    "isYellow",
    "numPitStops",
    "pitState",
    "pitTime",
    "tireCompound",
    "posXZ",
    "relativeOrientationXZRadians",
    "relativeRotatedPosXZ",
    "relativeStraightDistance",
    #"slotID",
    #"speed",
    #"totalLaps",
    #"lapDistance",
    #"orientationXZRadians",
    ]
)
