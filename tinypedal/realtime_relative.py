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
Relative module
"""

import time
import threading

from pyRfactor2SharedMemory.sharedMemoryAPI import Cbytestring2Python

from tinypedal.__init__ import info
import tinypedal.calculation as calc


class RelativeInfo:
    """Relative info"""

    def __init__(self):
        self.relative_list = None

    def start(self):
        """Start calculation thread"""
        relative_thread = threading.Thread(target=self.__relative)
        relative_thread.setDaemon(True)
        relative_thread.start()

    def __relative(self):
        """Create relative list with vehicle class info

        Run calculation separately.
        """
        update_delay = 0.5  # changeable update delay for conserving resources

        while True:
            if info.playersVehicleTelemetry().mIgnitionStarter != 0:
                update_delay = 0.2  # shorter delay

                # Generate raw data list from all vehicles in current session
                veh_dict = {}
                unsorted_veh_class = []
                unique_veh_class = []

                for index in range(max(info.Rf2Scor.mScoringInfo.mNumVehicles, 1)):
                    # Create vehicle dict, use "vehicle index" as key, "distance position" as value
                    # Filter out negative distance value to zero
                    veh_dict.update({index:info.Rf2Scor.mVehicles[index].mLapDist})

                    # Create vehicle class list (class name, veh place, veh index)
                    vehclass = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mVehicleClass)
                    place = info.Rf2Scor.mVehicles[index].mPlace
                    unsorted_veh_class.append((vehclass, place, index))
                    unique_veh_class.append(vehclass)

                selected_list = self.calc_relative_list(veh_dict)
                veh_class_info = self.calc_veh_class_list(unsorted_veh_class, unique_veh_class)

                self.relative_list = (selected_list, veh_class_info)

            else:
                update_delay = 0.5  # longer delay while inactive

            time.sleep(update_delay)

    def relative_data(self, index, index_player, veh_class_info):
        """Relative data"""
        if index >= 0:
            # Driver place position
            place = f"{veh_class_info[index][3]:02d}"

            # Driver name
            driver = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mDriverName)

            # Lap time
            laptime = calc.sec2laptime(max(info.Rf2Scor.mVehicles[index].mLastLapTime, 0))

            # Vehicle position & class
            pos_class = f"{veh_class_info[index][1]:02d}"
            veh_class = veh_class_info[index][2]

            # Relative time gap
            time_gap = self.calc_relative_time_gap(index, index_player)

            # Number of completed
            num_lap = info.Rf2Tele.mVehicles[index].mLapNumber

            # Driver in pit
            in_pit = info.Rf2Scor.mVehicles[index].mInPits
        else:
            # Assign empty value to -1 player index
            (place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit
             ) = "", "", "", "", "", "", 0, 0
        return place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit

    @staticmethod
    def calc_relative_list(veh_dict):
        """Calculate relative list"""
        # Reverse-sort dict by values
        re_veh_dict = dict(sorted(veh_dict.items(), key=lambda item: item[1], reverse=True))

        # Extract keys (vehicle index) to create new sorted vehicle list
        sorted_veh_list = list(re_veh_dict.keys())

        # Append with -1 if sorted vehicle list has less than 7 items
        if len(sorted_veh_list) < 7:
            for _ in range(7 - len(sorted_veh_list)):
                sorted_veh_list.append(-1)

        # Double extend list
        sorted_veh_list *= 2

        # Locate player vehicle index in list
        plr_index = info.players_index
        if plr_index in sorted_veh_list:
            plr_num = sorted_veh_list.index(plr_index)
        else:
            plr_num = 0  # prevent index not found in list error

        # Center selection range on player index from sorted vehicle list
        selected_list = [sorted_veh_list[index] for index in range(plr_num - 3, plr_num + 4)]
        return selected_list

    @staticmethod
    def calc_veh_class_list(unsorted_veh_class, unique_veh_class):
        """Calculate vehicle class info list"""
        sorted_veh_class = sorted(unsorted_veh_class)  # sort & group different vehicle class list
        unique_veh_class = list(set(unique_veh_class))  # create unique vehicle class list
        unique_initial_class = unique_veh_class[0]  # set initial unique class name for comparison

        # Create vehicle class reference list (vehicle index, position in class, class name, place)
        veh_class_info = []
        pos_counter = 0  # position in class
        for index in range(len(sorted_veh_class)):  # loop through sorted vehicle class list
            for unique_idx in range(len(unique_veh_class)):  # unique vehicle class range
                if sorted_veh_class[index][0] == unique_veh_class[unique_idx]:
                    if unique_initial_class == unique_veh_class[unique_idx]:
                        pos_counter += 1
                    else:
                        pos_counter = 1  # reset position counter
                        unique_initial_class = unique_veh_class[unique_idx]  # reset init name
                    veh_class_info.append((sorted_veh_class[index][2],
                                           pos_counter,
                                           unique_veh_class[unique_idx],
                                           sorted_veh_class[index][1]
                                           ))
        return sorted(veh_class_info)

    @staticmethod
    def calc_relative_time_gap(index, index_player):
        """Calculate relative time gap"""
        # Relative distance position
        track_length = info.Rf2Scor.mScoringInfo.mLapDist  # track length
        track_half = track_length * 0.5  # half of track length
        opv_dist = info.Rf2Scor.mVehicles[index].mLapDist  # opponent player vehicle position
        plr_dist = info.Rf2Scor.mVehicles[index_player].mLapDist  # player vehicle position
        rel_dist = abs(opv_dist - plr_dist)  # get relative distance between opponent & player

        # Opponent is ahead of player
        if opv_dist > plr_dist:
            # Relative dist is greater than half of track length
            if rel_dist > track_half:
                rel_dist = track_length - opv_dist + plr_dist
        # Opponent is behind player
        elif opv_dist < plr_dist:
            if rel_dist > track_half:
                rel_dist = track_length + opv_dist - plr_dist
        else:
            rel_dist = 0

        # Time gap = Relative dist / player speed
        speed = int(calc.vel2speed(
                    info.Rf2Scor.mVehicles[index_player].mLocalVel.x,
                    info.Rf2Scor.mVehicles[index_player].mLocalVel.y,
                    info.Rf2Scor.mVehicles[index_player].mLocalVel.z))
        if speed != 0:
            time_gap = f"{rel_dist / speed:.01f}"
        else:
            time_gap = "0.0"
        return time_gap

    @staticmethod
    def orientation():
        """Player orientation yaw"""
        ori_rad = calc.oriyaw2rad(info.playersVehicleTelemetry().mOri[2].z,
                                  info.playersVehicleTelemetry().mOri[2].x)  # invert
        return ori_rad

    @staticmethod
    def radar_pos(plr_ori_rad, index):
        """Calculate vehicle coordinates, lap number, orientation"""
        if index >= 0:
            pos_x = info.Rf2Tele.mVehicles[index].mPos.x * 10
            pos_z = info.Rf2Tele.mVehicles[index].mPos.z * 10

            new_pos = calc.rotate_pos(plr_ori_rad, pos_x, pos_z)
            num_lap = info.Rf2Tele.mVehicles[index].mLapNumber

            opt_ori_rad = calc.oriyaw2rad(info.Rf2Tele.mVehicles[index].mOri[2].z,
                                          info.Rf2Tele.mVehicles[index].mOri[2].x)
            ori_diff = opt_ori_rad - plr_ori_rad  # opponent orientation - player orientation
        else:
            new_pos = (-99999, -99999)
            num_lap = 0
            ori_diff = 0
        return new_pos, num_lap, ori_diff
