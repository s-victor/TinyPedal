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
Standings module
"""

import logging
import time
import threading
from collections import namedtuple

from ..readapi import info, chknm, cs2py, state
from .. import calculation as calc

MODULE_NAME = "module_standings"

logger = logging.getLogger(__name__)


class Realtime:
    """Standings info"""
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
    DistSet = namedtuple(
        "DistSet",
        [
        "Straight",
        "Track",
        "Yellow",
        ],
        defaults = ([999999] * 3)
    )
    pit_time_list = [[0,-1,0] for _ in range(128)]

    def __init__(self, mctrl, config):
        self.mctrl = mctrl
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False
        self.set_defaults()

    def set_defaults(self):
        """Set default output"""
        self.vehicles = None
        self.nearest = self.DistSet()

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("standings module started")

    def __calculation(self):
        """Create standings list"""
        checked = False

        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():
                # Reset switch
                if not checked:
                    checked = True
                    update_interval = active_interval  # shorter delay

                class_pos_list = self.mctrl.vehicle_classes
                veh_total = max(chknm(info.LastTele.mNumVehicles), 1)
                if class_pos_list and len(class_pos_list) == veh_total:
                    # Output
                    self.vehicles = list(self.__vehicle_data(veh_total, class_pos_list))
                    self.nearest = self.DistSet(
                        Straight = min(self.vehicles, key=nearest_line_dist).RelativeStraightDistance,
                        Track = abs(min(self.vehicles, key=nearest_track_dist).RelativeDistance),
                        Yellow = abs(min(self.vehicles, key=nearest_yellow_dist).RelativeDistance),
                    )
                #timer_start = time.perf_counter()
                #timer_end = time.perf_counter() - timer_start
                #logger.info(timer_end)

            else:
                if checked:
                    checked = False
                    update_interval = idle_interval  # longer delay while inactive

            time.sleep(update_interval)

        self.set_defaults()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("standings module closed")

    def __vehicle_data(self, veh_total, class_pos_list):
        """Get vehicle data"""
        # Additional data
        track_length = chknm(info.LastScor.mScoringInfo.mLapDist)
        current_session = chknm(info.LastScor.mScoringInfo.mSession)

        # Local player data
        plr_total_laps = chknm(info.syncedVehicleScoring().mTotalLaps)
        plr_lap_distance = chknm(info.syncedVehicleScoring().mLapDist)
        plr_percentage_distance = plr_lap_distance / max(track_length, 1)
        plr_speed = calc.vel2speed(
            chknm(info.syncedVehicleScoring().mLocalVel.x),
            chknm(info.syncedVehicleScoring().mLocalVel.y),
            chknm(info.syncedVehicleScoring().mLocalVel.z))
        plr_pos_xz = (chknm(info.syncedVehicleTelemetry().mPos.x),
                    -chknm(info.syncedVehicleTelemetry().mPos.z))
        plr_ori_rad = calc.oriyaw2rad(
            chknm(info.syncedVehicleTelemetry().mOri[2].x),
            chknm(info.syncedVehicleTelemetry().mOri[2].z))

        # Generate data list from all vehicles in current session
        for index in range(veh_total):
            tele_index = info.find_player_index_tele(index)

            vehicle_id = chknm(info.LastScor.mVehicles[index].mID)
            position = chknm(info.LastScor.mVehicles[index].mPlace)
            driver_name = cs2py(info.LastScor.mVehicles[index].mDriverName)
            vehicle_name = cs2py(info.LastScor.mVehicles[index].mVehicleName)
            vehicle_class = cs2py(info.LastScor.mVehicles[index].mVehicleClass)
            position_in_class = class_pos_list[index][1]

            session_best_laptime = class_pos_list[index][3]
            class_best_laptime = class_pos_list[index][4]
            best_laptime = chknm(info.LastScor.mVehicles[index].mBestLapTime)
            last_laptime = chknm(info.LastScor.mVehicles[index].mLastLapTime)
            elapsed_time = chknm(info.LastTele.mVehicles[tele_index].mElapsedTime)
            speed = calc.vel2speed(
                chknm(info.LastScor.mVehicles[index].mLocalVel.x),
                chknm(info.LastScor.mVehicles[index].mLocalVel.y),
                chknm(info.LastScor.mVehicles[index].mLocalVel.z)
            )
            is_player = chknm(info.LastScor.mVehicles[index].mIsPlayer)

            # Distance & time
            total_laps = chknm(info.LastScor.mVehicles[index].mTotalLaps)
            lap_distance = chknm(info.LastScor.mVehicles[index].mLapDist)
            percentage_distance = lap_distance / max(track_length, 1)
            relative_distance = calc.circular_relative_distance(
                track_length, plr_lap_distance, lap_distance)
            relative_time_gap = calc.relative_time_gap(
                relative_distance, speed, plr_speed)
            time_behind_leader = chknm(info.LastScor.mVehicles[index].mTimeBehindLeader)
            laps_behind_leader = chknm(info.LastScor.mVehicles[index].mLapsBehindLeader)
            time_behind_next = chknm(info.LastScor.mVehicles[index].mTimeBehindNext)
            laps_behind_next = chknm(info.LastScor.mVehicles[index].mLapsBehindNext)
            is_lapped = calc.lap_difference(
                total_laps, plr_total_laps,
                percentage_distance, plr_percentage_distance,
                current_session
            )
            is_yellow = bool(speed <= 8)

            # Pit
            in_garage = chknm(info.LastScor.mVehicles[index].mInGarageStall)
            in_pit = chknm(info.LastScor.mVehicles[index].mInPits)
            num_pit_stops = chknm(info.LastScor.mVehicles[index].mNumPitstops)
            pit_state = chknm(info.LastScor.mVehicles[index].mPitState)
            pit_time = self.__calc_pit_time(
                index, in_pit, in_garage, last_laptime, elapsed_time)
            tire_compound_index = (
                chknm(info.LastTele.mVehicles[tele_index].mFrontTireCompoundIndex),
                chknm(info.LastTele.mVehicles[tele_index].mRearTireCompoundIndex)
            )

            # Position data
            pos_xz = (chknm(info.LastTele.mVehicles[tele_index].mPos.x),
                    -chknm(info.LastTele.mVehicles[tele_index].mPos.z))
            orientation_xz_radians = calc.oriyaw2rad(
                chknm(info.LastTele.mVehicles[tele_index].mOri[2].x),
                chknm(info.LastTele.mVehicles[tele_index].mOri[2].z))
            relative_rotated_pos_xz = calc.rotate_pos(
                plr_ori_rad - 3.14159265,   # plr_ori_rad, rotate view
                pos_xz[0] - plr_pos_xz[0],  # x position related to player
                pos_xz[1] - plr_pos_xz[1]   # y position related to player
            )
            relative_orientation_xz_radians = orientation_xz_radians - plr_ori_rad
            relative_straight_distance = calc.distance_xy(plr_pos_xz, pos_xz)

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

    def __calc_pit_time(self, index, in_pit, in_garage, last_laptime, elapsed_time):
        """Calculate lap & pit time"""
        pit_status = in_pit * 1000 + chknm(info.LastScor.mVehicles[index].mID)
        # Pit status check
        if pit_status != self.pit_time_list[index][0]:
            self.pit_time_list[index][0] = pit_status  # last pit status
            self.pit_time_list[index][1] = elapsed_time  # last etime stamp
        # Ignore pit timer in garage
        if in_garage:
            self.pit_time_list[index][1] = -1
            self.pit_time_list[index][2] = 0
        # Start counting pit time
        if self.pit_time_list[index][1] >= 0:
            pit_time = min(max(elapsed_time - self.pit_time_list[index][1], 0), 999.9)
            if in_pit:
                self.pit_time_list[index][2] = pit_time
        # Reset pit time if made a valid lap time after pit
        if not in_pit and self.pit_time_list[index][2] > 0 and last_laptime > 0:
            self.pit_time_list[index][2] = 0
        return self.pit_time_list[index][2]


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


def nearest_yellow_dist(value):
    """Find nearest yellow flag distance"""
    if value.IsYellow:
        return abs(value.RelativeDistance)
    return 999999
