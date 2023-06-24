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
from ..readapi import info, chknm, cs2py, state
from .. import calculation as calc

MODULE_NAME = "module_vehicles"

logger = logging.getLogger(__name__)


class Realtime:
    """Vehicles info"""
    module_name = MODULE_NAME
    DataSet = namedtuple(
        "DataSet",
        [
        "VehicleID",
        "Position",
        "DriverName",
        "VehicleName",
        "VehicleClass",
        "PositionInClass",
        "SessionBestLaptime",
        "ClassBestLaptime",
        "BestLaptime",
        "LastLaptime",
        "Speed",
        "IsPlayer",
        "TotalLaps",
        "LapDistance",
        "PercentageDistance",
        "RelativeDistance",
        "RelativeTimeGap",
        "TimeBehindLeader",
        "LapsBehindLeader",
        "TimeBehindNext",
        "LapsBehindNext",
        "IsLapped",
        "IsYellow",
        "InGarage",
        "InPit",
        "NumPitStops",
        "PitState",
        "PitTime",
        "TireCompoundIndex",
        "PosXZ",
        "OrientationXZRadians",
        "RelativeOrientationXZRadians",
        "RelativeRotatedPosXZ",
        "RelativeStraightDistance",
        ]
    )

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
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                class_pos_list = minfo.relative.Classes
                veh_total = max(chknm(info.rf2Tele.mNumVehicles), 1)
                if class_pos_list and len(class_pos_list) == veh_total:
                    vehicles_data = list(self.__vehicle_data(veh_total, class_pos_list))
                    # Output
                    minfo.vehicles.Data = vehicles_data
                    minfo.vehicles.NearestStraight = min(
                        vehicles_data, key=nearest_line_dist).RelativeStraightDistance
                    minfo.vehicles.NearestTraffic = abs(
                        min(vehicles_data, key=nearest_traffic).RelativeTimeGap)
                    minfo.vehicles.NearestYellow = abs(
                        min(vehicles_data, key=nearest_yellow_dist).RelativeDistance)
                    #minfo.vehicles.nearestTrack = abs(
                    # min(vehicles_data, key=nearest_track_dist).RelativeDistance)

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("vehicles module closed")

    def __vehicle_data(self, veh_total, class_pos_list):
        """Get vehicle data"""
        # Additional data
        track_length = max(chknm(info.rf2Scor.mScoringInfo.mLapDist), 1)
        current_session = chknm(info.rf2Scor.mScoringInfo.mSession)

        # Local player data
        plr_total_laps = chknm(info.playerScor.mTotalLaps)
        plr_lap_distance = chknm(info.playerScor.mLapDist)
        plr_percentage_distance = plr_lap_distance / track_length
        plr_speed = calc.vel2speed(
            chknm(info.playerScor.mLocalVel.x),
            chknm(info.playerScor.mLocalVel.y),
            chknm(info.playerScor.mLocalVel.z))
        plr_pos_xz = (chknm(info.playerTele.mPos.x),
                     -chknm(info.playerTele.mPos.z))
        plr_ori_rad = calc.oriyaw2rad(
            chknm(info.playerTele.mOri[2].x),
            chknm(info.playerTele.mOri[2].z))

        # Generate data list from all vehicles in current session
        for index in range(veh_total):
            tele_index = info.find_player_index_tele(index)
            is_player = chknm(info.rf2Scor.mVehicles[index].mIsPlayer)

            vehicle_id = chknm(info.rf2Scor.mVehicles[index].mID)
            position = chknm(info.rf2Scor.mVehicles[index].mPlace)
            driver_name = cs2py(info.rf2Scor.mVehicles[index].mDriverName)
            vehicle_name = cs2py(info.rf2Scor.mVehicles[index].mVehicleName)
            vehicle_class = cs2py(info.rf2Scor.mVehicles[index].mVehicleClass)
            position_in_class = class_pos_list[index][1]

            session_best_laptime = class_pos_list[index][3]
            class_best_laptime = class_pos_list[index][4]
            best_laptime = chknm(info.rf2Scor.mVehicles[index].mBestLapTime)
            last_laptime = chknm(info.rf2Scor.mVehicles[index].mLastLapTime)
            elapsed_time = chknm(info.rf2Tele.mVehicles[tele_index].mElapsedTime)
            speed = calc.vel2speed(
                chknm(info.rf2Scor.mVehicles[index].mLocalVel.x),
                chknm(info.rf2Scor.mVehicles[index].mLocalVel.y),
                chknm(info.rf2Scor.mVehicles[index].mLocalVel.z)
            )

            # Distance & time
            total_laps = chknm(info.rf2Scor.mVehicles[index].mTotalLaps)
            lap_distance = chknm(info.rf2Scor.mVehicles[index].mLapDist)
            percentage_distance = lap_distance / track_length
            relative_distance = calc.circular_relative_distance(
                track_length, plr_lap_distance, lap_distance
                ) if not is_player else 0
            relative_time_gap = calc.relative_time_gap(
                relative_distance, speed, plr_speed
                ) if not is_player else 0
            time_behind_leader = chknm(info.rf2Scor.mVehicles[index].mTimeBehindLeader)
            laps_behind_leader = chknm(info.rf2Scor.mVehicles[index].mLapsBehindLeader)
            time_behind_next = chknm(info.rf2Scor.mVehicles[index].mTimeBehindNext)
            laps_behind_next = chknm(info.rf2Scor.mVehicles[index].mLapsBehindNext)
            is_lapped = calc.lap_difference(
                total_laps, plr_total_laps,
                percentage_distance, plr_percentage_distance,
                current_session
                ) if not is_player else 0
            is_yellow = bool(speed <= 8)

            # Pit
            in_garage = chknm(info.rf2Scor.mVehicles[index].mInGarageStall)
            in_pit = chknm(info.rf2Scor.mVehicles[index].mInPits)
            num_pit_stops = chknm(info.rf2Scor.mVehicles[index].mNumPitstops)
            pit_state = chknm(info.rf2Scor.mVehicles[index].mPitState)
            pit_time = self.__calc_pit_time(
                index, in_pit, in_garage, last_laptime, elapsed_time,
                in_pit * 1000 + vehicle_id)
            tire_compound_index = (
                chknm(info.rf2Tele.mVehicles[tele_index].mFrontTireCompoundIndex),
                chknm(info.rf2Tele.mVehicles[tele_index].mRearTireCompoundIndex)
            )

            # Position data
            pos_xz = (chknm(info.rf2Tele.mVehicles[tele_index].mPos.x),
                     -chknm(info.rf2Tele.mVehicles[tele_index].mPos.z))
            orientation_xz_radians = calc.oriyaw2rad(
                chknm(info.rf2Tele.mVehicles[tele_index].mOri[2].x),
                chknm(info.rf2Tele.mVehicles[tele_index].mOri[2].z))
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

            yield self.DataSet(
                VehicleID = vehicle_id,
                Position = position,
                DriverName = driver_name,
                VehicleName = vehicle_name,
                VehicleClass = vehicle_class,
                PositionInClass = position_in_class,
                SessionBestLaptime = session_best_laptime,
                ClassBestLaptime = class_best_laptime,
                BestLaptime = best_laptime,
                LastLaptime = last_laptime,
                Speed = speed,
                IsPlayer = is_player,
                TotalLaps = total_laps,
                LapDistance = lap_distance,
                PercentageDistance = percentage_distance,
                RelativeDistance = relative_distance,
                RelativeTimeGap = relative_time_gap,
                TimeBehindLeader = time_behind_leader,
                LapsBehindLeader = laps_behind_leader,
                TimeBehindNext = time_behind_next,
                LapsBehindNext = laps_behind_next,
                IsLapped = is_lapped,
                IsYellow = is_yellow,
                InGarage = in_garage,
                InPit = in_pit,
                NumPitStops = num_pit_stops,
                PitState = pit_state,
                PitTime = pit_time,
                TireCompoundIndex = tire_compound_index,
                PosXZ = pos_xz,
                OrientationXZRadians = orientation_xz_radians,
                RelativeOrientationXZRadians = relative_orientation_xz_radians,
                RelativeRotatedPosXZ = relative_rotated_pos_xz,
                RelativeStraightDistance = relative_straight_distance,
            )

    def __calc_pit_time(self, index, in_pit, in_garage, last_laptime, elapsed_time, pit_status):
        """Calculate lap & pit time"""
        index *= 3
        idx_inpit, idx_start, idx_timer = index, index + 1, index + 2
        # Pit status check
        if pit_status != self.pit_time_list[idx_inpit]:
            self.pit_time_list[idx_inpit] = pit_status  # last pit status
            self.pit_time_list[idx_start] = elapsed_time  # last etime stamp
        # Ignore pit timer in garage
        if in_garage:
            self.pit_time_list[idx_start] = -1
            self.pit_time_list[idx_timer] = 0
        # Start counting pit time
        if self.pit_time_list[idx_start] >= 0:
            pit_time = min(max(elapsed_time - self.pit_time_list[idx_start], 0), 999.9)
            if in_pit:
                self.pit_time_list[idx_timer] = pit_time
        # Reset pit time if made a valid lap time after pit
        if not in_pit and self.pit_time_list[idx_timer] > 0 and last_laptime > 0:
            self.pit_time_list[idx_timer] = 0
        return self.pit_time_list[idx_timer]


def nearest_line_dist(value):
    """Find nearest straight line distance"""
    if not value.IsPlayer:
        return value.RelativeStraightDistance
    return 999999


def nearest_track_dist(value):
    """Find nearest track distance"""
    if not value.IsPlayer:
        return abs(value.RelativeDistance)
    return 999999


def nearest_traffic(value):
    """Find nearest traffic gap"""
    if 0 == value.InPit > value.RelativeDistance:
        return value.RelativeTimeGap
    return 999999


def nearest_yellow_dist(value):
    """Find nearest yellow flag distance"""
    if value.IsYellow:
        return abs(value.RelativeDistance)
    return 999999
