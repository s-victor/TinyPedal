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

chknum = info.in2zero


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
            if chknum(info.playersVehicleTelemetry().mIgnitionStarter) != 0:
                update_delay = 0.2  # shorter delay

                # Generate raw data list from all vehicles in current session
                veh_dict = {}
                unsorted_veh_class = []
                unique_veh_class = []

                for index in range(max(chknum(info.Rf2Scor.mScoringInfo.mNumVehicles), 1)):
                    # Create vehicle dict, use "vehicle index" as key, "distance position" as value
                    # Filter out negative distance value to zero
                    veh_dict.update({index:chknum(info.Rf2Scor.mVehicles[index].mLapDist)})

                    # Create vehicle class list (class name, veh place, veh index)
                    vehclass = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mVehicleClass)
                    place = chknum(info.Rf2Scor.mVehicles[index].mPlace)

                    unsorted_veh_class.append((vehclass,  # 0 vehicle class name
                                               place,     # 1 overall position
                                               index     # 2 player index
                                               ))
                    unique_veh_class.append(vehclass)

                plr_index = info.players_index
                selected_index = self.calc_relative_index(veh_dict, plr_index)
                veh_class_info = self.calc_veh_class_list(unsorted_veh_class, unique_veh_class)

                self.relative_list = (selected_index, veh_class_info, plr_index)

            else:
                update_delay = 0.5  # longer delay while inactive

            time.sleep(update_delay)

    def relative_data(self, index, index_player, veh_class_info):
        """Relative data, this function is accessed by relative widget"""
        # Prevent index out of range
        if 0 <= index < len(veh_class_info) and len(veh_class_info[index]) == 4:
            # Driver place position
            place = f"{veh_class_info[index][3]:02d}"

            # Vehicle position & class
            pos_class = f"{veh_class_info[index][1]:02d}"
            veh_class = veh_class_info[index][2]

            # Driver name
            driver = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mDriverName)

            # Lap time
            laptime = calc.sec2laptime(max(chknum(info.Rf2Scor.mVehicles[index].mLastLapTime), 0))

            # Relative time gap
            time_gap = self.calc_relative_time_gap(index, index_player)

            # Number of completed
            num_lap = chknum(info.Rf2Tele.mVehicles[index].mLapNumber)

            # Driver in pit
            in_pit = chknum(info.Rf2Scor.mVehicles[index].mInPits)

            # Tyre compound index
            tire_idx = (chknum(info.Rf2Tele.mVehicles[index].mFrontTireCompoundIndex),
                        chknum(info.Rf2Tele.mVehicles[index].mRearTireCompoundIndex))
        else:
            # Assign empty value to -1 player index
            (place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit, tire_idx
             ) = "", "", "", "", "", "", 0, 0, 0
        return place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit, tire_idx

    @staticmethod
    def calc_relative_index(veh_dict, plr_index):
        """Calculate relative player index"""
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
        if plr_index in sorted_veh_list:
            plr_num = sorted_veh_list.index(plr_index)
        else:
            plr_num = 0  # prevent index not found in list error

        # Center selection range on player index from sorted vehicle list
        selected_index = [sorted_veh_list[index] for index in range(plr_num - 3, plr_num + 4)]
        return selected_index

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

                    veh_class_info.append((sorted_veh_class[index][2],       # 0 - 2 player index
                                           pos_counter,                      # 1 - position in class
                                           unique_veh_class[unique_idx],     # 2 - 0 vehicle class name
                                           sorted_veh_class[index][1]        # 3 - 1 overall position
                                           ))
        return sorted(veh_class_info)

    @staticmethod
    def calc_relative_time_gap(index, index_player):
        """Calculate relative time gap"""
        # Relative distance position
        track_length = chknum(info.Rf2Scor.mScoringInfo.mLapDist)  # track length
        track_half = track_length * 0.5  # half of track length
        opv_dist = chknum(info.Rf2Scor.mVehicles[index].mLapDist)  # opponent player vehicle position
        plr_dist = chknum(info.Rf2Scor.mVehicles[index_player].mLapDist)  # player vehicle position
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
        speed_plr = calc.vel2speed(
                    chknum(info.Rf2Scor.mVehicles[index_player].mLocalVel.x),
                    chknum(info.Rf2Scor.mVehicles[index_player].mLocalVel.y),
                    chknum(info.Rf2Scor.mVehicles[index_player].mLocalVel.z))
        speed_opt = calc.vel2speed(
                    chknum(info.Rf2Scor.mVehicles[index].mLocalVel.x),
                    chknum(info.Rf2Scor.mVehicles[index].mLocalVel.y),
                    chknum(info.Rf2Scor.mVehicles[index].mLocalVel.z))
        speed = max(speed_plr, speed_opt)
        if round(speed, 1) > 0:
            time_gap = f"{abs(rel_dist / speed):.01f}"
        else:
            time_gap = "0.0"
        return time_gap

    @staticmethod
    def vehicle_gps(index_list):
        """Player orientation yaw & global position"""
        veh_gps = []
        for index in index_list:
            # Orientation, pos x z, lap number
            veh_gps.append((calc.oriyaw2rad(chknum(info.Rf2Tele.mVehicles[index].mOri[2].z),
                                            chknum(info.Rf2Tele.mVehicles[index].mOri[2].x)),
                            chknum(info.Rf2Tele.mVehicles[index].mPos.x * 10),
                            chknum(info.Rf2Tele.mVehicles[index].mPos.z * 10),
                            chknum(info.Rf2Tele.mVehicles[index].mLapNumber)
                            ))
        return veh_gps

    @staticmethod
    def radar_pos(plr_gps, opt_gps, index):
        """Calculate vehicle coordinates, lap number, orientation"""
        if index >= 0:
            new_pos = calc.rotate_pos(plr_gps[0], opt_gps[1], opt_gps[2])
            num_lap = opt_gps[3]
            ori_diff = opt_gps[0] - plr_gps[0]  # opponent orientation - player orientation
        else:
            new_pos = (-99999, -99999)
            num_lap = 0
            ori_diff = 0
        return new_pos, num_lap, ori_diff
