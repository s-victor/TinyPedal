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
Vehicles module
"""

import array
import logging
import threading
from dataclasses import dataclass

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
        self.event = threading.Event()
        self.pit_time_list = array.array("f", [0,-1,0] * 128)

    def start(self):
        """Start update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__update_data, daemon=True).start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: module vehicles")

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __update_data(self):
        """Update module data"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = active_interval
        vehicles_data = []

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval
                    minfo.vehicles.dataSetVersion = -1

                veh_total = min(max(api.read.vehicle.total_vehicles(), 1), 128)
                veh_data_size = len(vehicles_data)

                if veh_data_size != veh_total:
                    if veh_data_size < veh_total:
                        for _ in range(veh_total - veh_data_size):
                            vehicles_data.append(DataSet())
                    else:
                        for _ in range(veh_data_size - veh_total):
                            vehicles_data.pop()

                self.__update_vehicle_data(vehicles_data, minfo.relative.classes)
                dist_line, dist_time, dist_yellow = nearest_distance_data(vehicles_data)

                # Output
                minfo.vehicles.dataSet = vehicles_data[:veh_total]
                minfo.vehicles.dataSetVersion += 1
                minfo.vehicles.nearestStraight = dist_line
                minfo.vehicles.nearestTraffic = dist_time
                minfo.vehicles.nearestYellow = dist_yellow

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: module vehicles")

    def __update_vehicle_data(self, data_set, class_pos_list):
        """Update vehicle data"""
        # Additional data
        track_length = api.read.lap.track_length()
        in_race = api.read.session.in_race()
        class_list_size = len(class_pos_list)

        # Local player data
        plr_total_laps = api.read.lap.total_laps()
        plr_lap_distance = api.read.lap.distance()
        plr_percentage_distance = calc.percentage_distance(plr_lap_distance, track_length, 0.99999)
        plr_speed = api.read.vehicle.speed()
        plr_pos_xz = (api.read.vehicle.pos_longitudinal(),
                      api.read.vehicle.pos_lateral())
        plr_ori_rad = api.read.vehicle.orientation_yaw_radians()

        # Update data from all vehicles in current session
        for _idx, _data in enumerate(data_set):
            slot_id = api.read.vehicle.slot_id(_idx)
            lap_etime = api.read.timing.elapsed(_idx)
            speed = api.read.vehicle.speed(_idx)
            total_laps = api.read.lap.total_laps(_idx)
            lap_distance = api.read.lap.distance(_idx)
            orientation_xz_radians = api.read.vehicle.orientation_yaw_radians(_idx)

            _data.isPlayer = api.read.vehicle.is_player(_idx)
            _data.isNotPlayer = not _data.isPlayer
            _data.position = api.read.vehicle.place(_idx)
            _data.driverName = api.read.vehicle.driver_name(_idx)
            _data.vehicleName = api.read.vehicle.vehicle_name(_idx)
            _data.vehicleClass = api.read.vehicle.class_name(_idx)

            if _idx < class_list_size:
                _data.positionInClass = class_pos_list[_idx][1]
                _data.sessionBestLapTime = class_pos_list[_idx][3]
                _data.classBestLapTime = class_pos_list[_idx][4]

            _data.bestLapTime = api.read.timing.best_laptime(_idx)
            _data.lastLapTime = api.read.timing.last_laptime(_idx)

            # Distance & time
            _data.percentageDistance = calc.percentage_distance(
                lap_distance, track_length, 0.99999)
            _data.relativeDistance = calc.circular_relative_distance(
                track_length, plr_lap_distance, lap_distance
                ) if not _data.isPlayer else 0
            _data.relativeTimeGap = calc.relative_time_gap(
                _data.relativeDistance, speed, plr_speed
                ) if not _data.isPlayer else 0

            _data.timeBehindLeader = api.read.timing.behind_leader(_idx)
            _data.timeBehindNext = api.read.timing.behind_next(_idx)
            _data.lapsBehindLeader = api.read.lap.behind_leader(_idx)
            _data.lapsBehindNext = api.read.lap.behind_next(_idx)

            _data.isLapped = 0 if _data.isPlayer or not in_race else calc.lap_difference(
                total_laps + _data.percentageDistance,
                plr_total_laps + plr_percentage_distance,
                self.mcfg["lap_difference_ahead_threshold"],
                self.mcfg["lap_difference_behind_threshold"]
                )
            _data.isYellow = speed < 8

            # Pit
            _data.inGarage = api.read.vehicle.in_garage(_idx)
            _data.inPit = api.read.vehicle.in_pits(_idx)
            _data.numPitStops = api.read.vehicle.number_pitstops(_idx)
            _data.pitState = api.read.vehicle.pit_state(_idx)
            _data.pitTime = self.__calc_pit_time(
                _idx, _data.inPit, _data.inGarage, _data.lastLapTime, lap_etime,
                _data.inPit * 1000 + slot_id)
            _data.tireCompound = api.read.tyre.compound(_idx)

            # Position data
            _data.posXZ = (api.read.vehicle.pos_longitudinal(_idx),
                      api.read.vehicle.pos_lateral(_idx))
            _data.relativeRotatedPosXZ = calc.rotate_pos(
                plr_ori_rad - 3.14159265,   # plr_ori_rad, rotate view
                _data.posXZ[0] - plr_pos_xz[0],  # x position related to player
                _data.posXZ[1] - plr_pos_xz[1]   # y position related to player
                ) if not _data.isPlayer else (0,0)
            _data.relativeOrientationXZRadians = (
                orientation_xz_radians - plr_ori_rad
                ) if not _data.isPlayer else 0
            _data.relativeStraightDistance = calc.distance(
                plr_pos_xz, _data.posXZ
                ) if not _data.isPlayer else 0

            # Unused data set
            #_data.slotID = slot_id
            #_data.speed = speed
            #_data.totalLaps = total_laps
            #_data.lapDistance = lap_distance
            #_data.orientationXZRadians = orientation_xz_radians

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
            return 0
        # Calculating pit time while in pit
        if in_pit and self.pit_time_list[idx_start] >= 0:
            self.pit_time_list[idx_timer] = min(
                max(lap_etime - self.pit_time_list[idx_start], 0), 999.9)
        # Reset pit time if made a valid lap time after pitting
        if not in_pit and self.pit_time_list[idx_timer] and laptime_last > 0:
            self.pit_time_list[idx_timer] = 0
        return self.pit_time_list[idx_timer]


def nearest_distance_data(
    data_list: list,
    dist_line: int = 999999,
    dist_time: int = 999999,
    dist_yellow: int = 999999):
    """Calculate nearest distance data"""
    for data in data_list:
        # Find nearest straight line distance
        if not data.isPlayer and data.relativeStraightDistance < dist_line:
            dist_line = data.relativeStraightDistance
        # Find nearest traffic time gap
        if 0 == data.inPit > data.relativeDistance and data.relativeTimeGap < dist_time:
            dist_time = data.relativeTimeGap
        # Find nearest yellow flag (on track) distance
        if data.isYellow:
            rel_dist = abs(data.relativeDistance)
            if rel_dist < dist_yellow:
                dist_yellow = rel_dist
    return dist_line, dist_time, dist_yellow


@dataclass(order=True)
class DataSet:
    """Vehicle data set"""
    # Sorting priority section (for track map display, set reverse sort)
    isNotPlayer: bool = True
    inGarage: bool = False
    inPit: bool = False
    position: int = 0
    # End of sorting priority section
    driverName: str = ""
    vehicleName: str = ""
    vehicleClass: str = ""
    positionInClass: int = 0
    sessionBestLapTime: float = 99999
    classBestLapTime: float = 99999
    bestLapTime: float = 99999
    lastLapTime: float = 99999
    isPlayer: bool = False
    percentageDistance: float = 0
    relativeDistance: float = 0
    relativeTimeGap: float = 0
    timeBehindLeader: float = 0
    lapsBehindLeader: float = 0
    timeBehindNext: float = 0
    lapsBehindNext: float = 0
    isLapped: bool = False
    isYellow: bool = False
    numPitStops: int = 0
    pitState: int = 0
    pitTime: float = 0
    tireCompound: tuple = 0, 0
    posXZ: tuple = 0, 0
    relativeOrientationXZRadians: float = 0
    relativeRotatedPosXZ: tuple = 0, 0
    relativeStraightDistance: float = 0
    #slotID: int = 0
    #speed: float = 0
    #totalLaps: int = 0
    #lapDistance: float = 0
    #orientationXZRadians: float
