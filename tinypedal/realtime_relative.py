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

from .readapi import info, chknm, cs2py, state
from . import calculation as calc


class RelativeInfo:
    """Relative info"""

    def __init__(self, config):
        self.cfg = config
        self.relative_list = None
        self.radar_list = None
        self.running = False
        self.stopped = True

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        relative_thread = threading.Thread(target=self.__relative)
        relative_thread.setDaemon(True)
        relative_thread.start()
        print("relative module started")

    def __relative(self):
        """Create relative list with vehicle class info

        Run calculation separately.
        """
        checked = False
        update_delay = 0.4  # changeable update delay for conserving resources

        # Load additional relative players
        rel_add_front = min(max(self.cfg.setting_user["relative"]["additional_players_front"], 0), 3)
        rel_add_behind = min(max(self.cfg.setting_user["relative"]["additional_players_behind"], 0), 3)

        # Load additional radar vehicles
        radar_add_front = min(max(self.cfg.setting_user["radar"]["additional_vehicles_front"], 0), 9)
        radar_add_behind = min(max(self.cfg.setting_user["radar"]["additional_vehicles_behind"], 0), 9)

        while self.running:
            # Reset switch
            if not checked:
                checked = True

            if state():
                update_delay = 0.1  # shorter delay

                # Generate raw data list from all vehicles in current session
                veh_dict = {}
                unsorted_veh_class = []
                unique_veh_class = []

                for index in range(max(chknm(info.LastTele.mNumVehicles), 1)):
                    # Create vehicle dict, use "vehicle index" as key, "distance position" as value
                    veh_dict.update({index:chknm(info.LastScor.mVehicles[index].mLapDist)})

                    # Create vehicle class list (class name, veh place, veh index)
                    vehclass = cs2py(info.LastScor.mVehicles[index].mVehicleClass)
                    place = chknm(info.LastScor.mVehicles[index].mPlace)

                    unsorted_veh_class.append((vehclass,  # 0 vehicle class name
                                               place,     # 1 overall position
                                               index     # 2 player index
                                               ))
                    unique_veh_class.append(vehclass)

                plr_index = info.players_index
                selected_index = self.calc_relative_index(veh_dict, plr_index, rel_add_front, rel_add_behind)
                veh_class_info = self.calc_veh_class_list(unsorted_veh_class, unique_veh_class)

                self.relative_list = (selected_index, veh_class_info, plr_index)

                self.radar_list = self.calc_relative_index(veh_dict, plr_index, radar_add_front, radar_add_behind)

            else:
                if checked:
                    checked = False
                    self.relative_list = None
                    self.radar_list = None
                    update_delay = 0.4  # longer delay while inactive

            time.sleep(update_delay)

        self.relative_list = None
        self.radar_list = None
        self.stopped = True
        print("relative module closed")

    def relative_data(self, index, index_player, veh_class_info):
        """Relative data, this function is accessed by relative widget"""
        # Prevent index out of range
        if 0 <= index < len(veh_class_info) and len(veh_class_info[index]) == 4:
            # 0 Driver place position
            place = f"{veh_class_info[index][3]:02d}"

            # 1 Driver name
            driver = (cs2py(info.LastScor.mVehicles[index].mDriverName),
                      cs2py(info.LastScor.mVehicles[index].mVehicleName))

            # 2 Lap time
            raw_laptime = chknm(info.LastScor.mVehicles[index].mLastLapTime)
            laptime = calc.sec2laptime(raw_laptime)[:9].rjust(9) if raw_laptime > 0 else "--:--.---"

            # 3 Vehicle position in class
            pos_class = f"{veh_class_info[index][1]:02d}"

            # 4 Vehicle class
            veh_class = veh_class_info[index][2]

            # 5 Time gap
            time_gap = self.calc_relative_time_gap(index, index_player)

            # 6 Completed laps
            num_lap = chknm(info.LastTele.mVehicles[index].mLapNumber)

            # 7 Is driver in pit
            in_pit = chknm(info.LastScor.mVehicles[index].mInPits)

            # 8 Tyre compound index
            tire_idx = (chknm(info.LastTele.mVehicles[index].mFrontTireCompoundIndex),
                        chknm(info.LastTele.mVehicles[index].mRearTireCompoundIndex))

            # 9 Pitstop count
            pit_count = chknm(info.LastScor.mVehicles[index].mNumPitstops)

        else:
            # Assign empty value to -1 player index
            (place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit, tire_idx, pit_count
             ) = "", ("",""), "", "", "", "", 0, 0, 0, -1
        return place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit, tire_idx, pit_count

    @staticmethod
    def calc_relative_index(veh_dict, plr_index, add_front, add_behind):
        """Calculate relative player index"""
        # Reverse-sort dict by values
        re_veh_dict = dict(sorted(veh_dict.items(), key=lambda item: item[1], reverse=True))

        # Extract keys (vehicle index) to create new sorted vehicle list
        sorted_veh_list = list(re_veh_dict.keys())

        # Append with -1 if sorted vehicle list has less than max_veh items
        max_veh = 7 + add_front + add_behind

        if len(sorted_veh_list) < max_veh:
            for _ in range(max_veh - len(sorted_veh_list)):
                sorted_veh_list.append(-1)

        # Double extend list
        sorted_veh_list *= 2

        # Locate player vehicle index in list
        if plr_index in sorted_veh_list:
            plr_num = sorted_veh_list.index(plr_index)
        else:
            plr_num = 0  # prevent index not found in list error

        # Center selection range on player index from sorted vehicle list
        selected_index = [sorted_veh_list[index] for index in range(int(plr_num - 3 - add_front), int(plr_num + 4 + add_behind))]
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
        track_length = chknm(info.LastScor.mScoringInfo.mLapDist)  # track length
        track_half = track_length * 0.5  # half of track length
        opv_dist = chknm(info.LastScor.mVehicles[index].mLapDist)  # opponent player vehicle position
        plr_dist = chknm(info.LastScor.mVehicles[index_player].mLapDist)  # player vehicle position
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
                    chknm(info.LastScor.mVehicles[index_player].mLocalVel.x),
                    chknm(info.LastScor.mVehicles[index_player].mLocalVel.y),
                    chknm(info.LastScor.mVehicles[index_player].mLocalVel.z))
        speed_opt = calc.vel2speed(
                    chknm(info.LastScor.mVehicles[index].mLocalVel.x),
                    chknm(info.LastScor.mVehicles[index].mLocalVel.y),
                    chknm(info.LastScor.mVehicles[index].mLocalVel.z))
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
            veh_gps.append((calc.oriyaw2rad(chknm(info.LastTele.mVehicles[index].mOri[2].z),
                                            chknm(info.LastTele.mVehicles[index].mOri[2].x)),
                            chknm(info.LastTele.mVehicles[index].mPos.x * 10),
                            chknm(info.LastTele.mVehicles[index].mPos.z * 10),
                            chknm(info.LastTele.mVehicles[index].mLapNumber)
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
