#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
import time
import threading
from collections import namedtuple

from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_vehicles"

logger = logging.getLogger(__name__)


class Realtime:
    """Vehicles info"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False
        self.pit_time_list = array.array("f", [0,-1,0] * 128)

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("vehicles module started")

    def __calculation(self):
        """Create vehicles data list"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                vehicles_data = list(self.__vehicle_data(minfo.relative.classes))

                # Output
                minfo.vehicles.dataSet = vehicles_data
                minfo.vehicles.nearestStraight = min(
                    vehicles_data, key=nearest_line_dist).relativeStraightDistance
                minfo.vehicles.nearestTraffic = abs(
                    min(vehicles_data, key=nearest_traffic).relativeTimeGap)
                minfo.vehicles.nearestYellow = abs(
                    min(vehicles_data, key=nearest_yellow_dist).relativeDistance)
                #minfo.vehicles.nearestTrack = abs(
                # min(vehicles_data, key=nearest_track_dist).relativeDistance)

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("vehicles module closed")

    def __vehicle_data(self, class_pos_list):
        """Get vehicle data"""
        # Additional data
        veh_total = max(api.read.vehicle.total_vehicles(), 1)
        track_length = max(api.read.lap.track_length(), 1)
        in_race = api.read.session.in_race()
        valid_class_list = class_pos_list and len(class_pos_list) == veh_total

        # Local player data
        plr_total_laps = api.read.lap.total_laps()
        plr_lap_distance = api.read.lap.distance()
        plr_percentage_distance = calc.percentage_distance(plr_lap_distance, track_length, 0.99999)
        plr_speed = api.read.vehicle.speed()
        plr_pos_xz = (api.read.vehicle.pos_longitudinal(),
                      api.read.vehicle.pos_lateral())
        plr_ori_rad = api.read.vehicle.orientation_yaw_radians()

        # Generate data list from all vehicles in current session
        for index in range(veh_total):
            is_player = api.read.vehicle.is_player(index)
            slot_id = api.read.vehicle.slot_id(index)
            position = api.read.vehicle.place(index)
            driver_name = api.read.vehicle.driver_name(index)
            vehicle_name = api.read.vehicle.vehicle_name(index)
            vehicle_class = api.read.vehicle.class_name(index)

            if valid_class_list:
                position_in_class = class_pos_list[index][1]
                laptime_session_best = class_pos_list[index][3]
                laptime_class_best = class_pos_list[index][4]
            else:
                position_in_class = 0
                laptime_session_best = 99999
                laptime_class_best = 99999

            laptime_best = api.read.timing.best_laptime(index)
            laptime_last = api.read.timing.last_laptime(index)
            lap_etime = api.read.timing.elapsed(index)
            speed = api.read.vehicle.speed(index)

            # Distance & time
            total_laps = api.read.lap.total_laps(index)
            lap_distance = api.read.lap.distance(index)

            percentage_distance = calc.percentage_distance(lap_distance, track_length, 0.99999)
            relative_distance = calc.circular_relative_distance(
                track_length, plr_lap_distance, lap_distance
                ) if not is_player else 0
            relative_time_gap = calc.relative_time_gap(
                relative_distance, speed, plr_speed
                ) if not is_player else 0

            time_behind_leader = api.read.timing.behind_leader(index)
            time_behind_next = api.read.timing.behind_next(index)
            laps_behind_leader = api.read.lap.behind_leader(index)
            laps_behind_next = api.read.lap.behind_next(index)

            is_lapped = calc.lap_difference(
                total_laps, plr_total_laps,
                percentage_distance, plr_percentage_distance,
                in_race
                ) if not is_player else 0
            is_yellow = bool(speed <= 8)

            # Pit
            in_garage = api.read.vehicle.in_garage(index)
            in_pit = api.read.vehicle.in_pits(index)
            num_pit_stops = api.read.vehicle.number_pitstops(index)
            pit_state = api.read.vehicle.pit_state(index)
            pit_time = self.__calc_pit_time(
                index, in_pit, in_garage, laptime_last, lap_etime,
                in_pit * 1000 + slot_id)
            tire_compound_index = api.read.tyre.compound(index)

            # Position data
            pos_xz = (api.read.vehicle.pos_longitudinal(index),
                      api.read.vehicle.pos_lateral(index))
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
                slotID = slot_id,
                position = position,
                driverName = driver_name,
                vehicleName = vehicle_name,
                vehicleClass = vehicle_class,
                positionInClass = position_in_class,
                sessionBestLapTime = laptime_session_best,
                classBestLapTime = laptime_class_best,
                bestLapTime = laptime_best,
                lastLapTime = laptime_last,
                speed = speed,
                isPlayer = is_player,
                totalLaps = total_laps,
                lapDistance = lap_distance,
                percentageDistance = percentage_distance,
                relativeDistance = relative_distance,
                relativeTimeGap = relative_time_gap,
                timeBehindLeader = time_behind_leader,
                lapsBehindLeader = laps_behind_leader,
                timeBehindNext = time_behind_next,
                lapsBehindNext = laps_behind_next,
                isLapped = is_lapped,
                isYellow = is_yellow,
                inGarage = in_garage,
                inPit = in_pit,
                numPitStops = num_pit_stops,
                pitState = pit_state,
                pitTime = pit_time,
                tireCompoundIndex = tire_compound_index,
                posXZ = pos_xz,
                orientationXZRadians = orientation_xz_radians,
                relativeOrientationXZRadians = relative_orientation_xz_radians,
                relativeRotatedPosXZ = relative_rotated_pos_xz,
                relativeStraightDistance = relative_straight_distance,
            )

    def __calc_pit_time(self, index, in_pit, in_garage, laptime_last, lap_etime, pit_status):
        """Calculate lap & pit time"""
        index *= 3
        idx_inpit, idx_start, idx_timer = index, index + 1, index + 2
        # Pit status check
        if pit_status != self.pit_time_list[idx_inpit]:
            self.pit_time_list[idx_inpit] = pit_status  # last pit status
            self.pit_time_list[idx_start] = lap_etime  # last etime stamp
        # Ignore pit timer in garage
        if in_garage:
            self.pit_time_list[idx_start] = -1
            self.pit_time_list[idx_timer] = 0
        # Start counting pit time
        if self.pit_time_list[idx_start] >= 0:
            pit_time = min(max(lap_etime - self.pit_time_list[idx_start], 0), 999.9)
            if in_pit:
                self.pit_time_list[idx_timer] = pit_time
        # Reset pit time if made a valid lap time after pit
        if not in_pit and self.pit_time_list[idx_timer] > 0 and laptime_last > 0:
            self.pit_time_list[idx_timer] = 0
        return self.pit_time_list[idx_timer]


def nearest_line_dist(value):
    """Find nearest straight line distance"""
    if not value.isPlayer:
        return value.relativeStraightDistance
    return 999999


def nearest_track_dist(value):
    """Find nearest track distance"""
    if not value.isPlayer:
        return abs(value.relativeDistance)
    return 999999


def nearest_traffic(value):
    """Find nearest traffic gap"""
    if 0 == value.inPit > value.relativeDistance:
        return value.relativeTimeGap
    return 999999


def nearest_yellow_dist(value):
    """Find nearest yellow flag distance"""
    if value.isYellow:
        return abs(value.relativeDistance)
    return 999999


DataSet = namedtuple(
    "DataSet",
    [
    "slotID",
    "position",
    "driverName",
    "vehicleName",
    "vehicleClass",
    "positionInClass",
    "sessionBestLapTime",
    "classBestLapTime",
    "bestLapTime",
    "lastLapTime",
    "speed",
    "isPlayer",
    "totalLaps",
    "lapDistance",
    "percentageDistance",
    "relativeDistance",
    "relativeTimeGap",
    "timeBehindLeader",
    "lapsBehindLeader",
    "timeBehindNext",
    "lapsBehindNext",
    "isLapped",
    "isYellow",
    "inGarage",
    "inPit",
    "numPitStops",
    "pitState",
    "pitTime",
    "tireCompoundIndex",
    "posXZ",
    "orientationXZRadians",
    "relativeOrientationXZRadians",
    "relativeRotatedPosXZ",
    "relativeStraightDistance",
    ]
)
