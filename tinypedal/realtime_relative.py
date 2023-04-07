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
        self.running = False
        self.stopped = True

        self.relative_list = None
        self.radar_list = None
        self.nearest_opt_dist = 99999
        self.pit_time_list = [[0,-1,0] for _ in range(128)]

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        self.thread = threading.Thread(target=self.__relative)
        self.thread.daemon=True
        self.thread.start()
        print("relative module started")

    def __relative(self):
        """Create relative list with vehicle class info

        Run calculation separately.
        """
        checked = False
        update_delay = 0.4  # changeable update delay for conserving resources

        # Load additional relative players
        rel_add_front = min(max(self.cfg.setting_user["relative"]["additional_players_front"], 0), 60)
        rel_add_behind = min(max(self.cfg.setting_user["relative"]["additional_players_behind"], 0), 60)

        # Load additional radar vehicles
        radar_add_front = min(max(self.cfg.setting_user["radar"]["additional_vehicles_front"], 0), 60)
        radar_add_behind = min(max(self.cfg.setting_user["radar"]["additional_vehicles_behind"], 0), 60)

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

                plr_index = info.players_scor_index
                race_check = bool(
                    chknm(info.LastScor.mScoringInfo.mSession) > 9
                    and self.cfg.setting_user["relative"]["hide_vehicle_in_garage_for_race"])

                for index in range(max(chknm(info.LastTele.mNumVehicles), 1)):
                    if self.veh_filter(race_check, index):
                        rel_dist = self.calc_relative_dist(index, plr_index)  # relative distance
                        # Create vehicle dict, use "vehicle index" as key, "distance position" as value
                        veh_dict.update({index:rel_dist})

                    # Create vehicle class list (class name, veh place, veh index)
                    vehclass = cs2py(info.LastScor.mVehicles[index].mVehicleClass)
                    place = chknm(info.LastScor.mVehicles[index].mPlace)

                    unsorted_veh_class.append((vehclass,  # 0 vehicle class name
                                               place,     # 1 overall position
                                               index      # 2 player index
                                               ))
                    unique_veh_class.append(vehclass)

                selected_index = self.calc_relative_index(veh_dict, plr_index, rel_add_front, rel_add_behind)
                veh_class_info = self.calc_veh_class_list(unsorted_veh_class, unique_veh_class)

                self.relative_list = (selected_index, veh_class_info, plr_index)

                self.radar_list = self.calc_relative_index(veh_dict, plr_index, radar_add_front, radar_add_behind)

                self.nearest_opt_dist = self.nearest_opponent_dist(self.radar_list, plr_index)

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

    def veh_filter(self, race_check, index):
        """Vehicle filter for creating relative list"""
        if race_check:
            if not chknm(info.LastScor.mVehicles[index].mInGarageStall):
                return True  # not in garage, show
            return False  # in garage, hide
        return True  # not in race or off, show

    def relative_data(self, index, index_player, veh_class_info):
        """Relative data, this function is accessed by relative widget"""
        # Prevent index out of range
        if 0 <= index < len(veh_class_info) and len(veh_class_info[index]) == 4:
            tele_index = info.find_player_index_tele(index)

            # 6 Completed laps
            num_lap = chknm(info.LastScor.mVehicles[index].mTotalLaps)

            # check whether is lapped
            is_lapped = num_lap - chknm(info.LastScor.mVehicles[index_player].mTotalLaps)

            # 0 Driver place position
            place = (f"{veh_class_info[index][3]:02d}", is_lapped)

            # 1 Driver name
            driver = (cs2py(info.LastScor.mVehicles[index].mDriverName),
                      cs2py(info.LastScor.mVehicles[index].mVehicleName),
                      is_lapped)

            # 2 Lap time
            laptime = self.calc_lap_pit_time(index)

            # 3 Vehicle position in class
            pos_class = f"{veh_class_info[index][1]:02d}"

            # 4 Vehicle class
            veh_class = veh_class_info[index][2]

            # 5 Time gap
            time_gap = (self.calc_relative_time_gap(index, index_player), is_lapped)

            # 7 Is driver in pit
            in_pit = chknm(info.LastScor.mVehicles[index].mInPits)

            # 8 Tyre compound index
            tire_idx = (chknm(info.LastTele.mVehicles[tele_index].mFrontTireCompoundIndex),
                        chknm(info.LastTele.mVehicles[tele_index].mRearTireCompoundIndex))

            # 9 Pitstop count
            pit_count = (chknm(info.LastScor.mVehicles[index].mNumPitstops),
                         chknm(info.LastScor.mVehicles[index].mPitState))

            return place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit, tire_idx, pit_count
        # Assign empty value to -1 player index
        return ("",0), ("","",0), "", "", "", ("",0), 0, 0, 0, (-1,0)

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
        for veh_sort in sorted_veh_class:  # loop through sorted vehicle class list
            for veh_uniq in unique_veh_class:  # unique vehicle class range
                if veh_sort[0] == veh_uniq:
                    if unique_initial_class == veh_uniq:
                        pos_counter += 1
                    else:
                        pos_counter = 1  # reset position counter
                        unique_initial_class = veh_uniq  # reset init name

                    veh_class_info.append((veh_sort[2],  # 0 - 2 player index
                                           pos_counter,  # 1 - position in class
                                           veh_uniq,     # 2 - 0 vehicle class name
                                           veh_sort[1]   # 3 - 1 overall position
                                           ))
        return sorted(veh_class_info)

    @staticmethod
    def calc_relative_dist(index, index_player):
        """Calculate relative distance"""
        # Relative distance position
        track_length = chknm(info.LastScor.mScoringInfo.mLapDist)  # track length
        track_half = track_length * 0.5  # half of track length
        opv_dist = chknm(info.LastScor.mVehicles[index].mLapDist)  # opponent player vehicle position
        plr_dist = chknm(info.LastScor.mVehicles[index_player].mLapDist)  # player vehicle position
        rel_dist = opv_dist - plr_dist  # get relative distance between opponent & player

        # Relative dist is greater than half of track length
        if abs(rel_dist) > track_half:
            if opv_dist > plr_dist:
                rel_dist -= track_length  # opponent is behind player
            elif opv_dist < plr_dist:
                rel_dist += track_length  # opponent is ahead player
        return rel_dist

    def calc_relative_time_gap(self, index, index_player):
        """Calculate relative time gap"""
        rel_dist = self.calc_relative_dist(index, index_player)
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
        if int(speed):
            return f"{abs(rel_dist / speed):.01f}"
        return "0.0"

    def calc_lap_pit_time(self, index):
        """Calculate lap & pit time"""
        raw_laptime = chknm(info.LastScor.mVehicles[index].mLastLapTime)
        laptime_format = calc.sec2laptime_full(raw_laptime)[:8].rjust(8)

        if self.cfg.setting_user["relative"]["show_pit_timer"]:
            tele_index = info.find_player_index_tele(index)

            in_pit = chknm(info.LastScor.mVehicles[index].mInPits)
            lap_etime = chknm(info.LastTele.mVehicles[tele_index].mElapsedTime)
            pit_status = in_pit * 1000 + chknm(info.LastTele.mVehicles[tele_index].mID)

            if pit_status != self.pit_time_list[index][0]:
                self.pit_time_list[index][0] = pit_status  # last pit status
                self.pit_time_list[index][1] = lap_etime  # last etime stamp

            if chknm(info.LastScor.mVehicles[index].mInGarageStall):
                self.pit_time_list[index][1] = -1
                self.pit_time_list[index][2] = 0

            if self.pit_time_list[index][1] >= 0:
                pit_time = min(max(lap_etime - self.pit_time_list[index][1], 0), 999.9)

                if in_pit:
                    raw_laptime = pit_time
                    self.pit_time_list[index][2] = pit_time
                    laptime_format = "PIT" + f"{raw_laptime:.01f}"[:5].rjust(5)
                elif pit_time <= self.cfg.setting_user["relative"]["pit_time_highlight_duration"]:
                    raw_laptime = self.pit_time_list[index][2]
                    laptime_format = "OUT" + f"{raw_laptime:.01f}"[:5].rjust(5)

        return laptime_format if raw_laptime > 0 else "-:--.---"

    @staticmethod
    def vehicle_gps(index_list, index_player):
        """Player orientation yaw & global position"""
        veh_gps = []
        plr_lapnum = chknm(info.LastScor.mVehicles[index_player].mTotalLaps)
        for index in index_list:
            tele_index = info.find_player_index_tele(index)
            # Orientation, pos x z, is lapped
            veh_gps.append((calc.oriyaw2rad(chknm(info.LastTele.mVehicles[tele_index].mOri[2].z),
                                            chknm(info.LastTele.mVehicles[tele_index].mOri[2].x)),
                            chknm(info.LastTele.mVehicles[tele_index].mPos.x * 10),
                            chknm(info.LastTele.mVehicles[tele_index].mPos.z * 10),
                            chknm(info.LastScor.mVehicles[index].mTotalLaps) - plr_lapnum
                            ))
        return veh_gps

    @staticmethod
    def nearest_opponent_dist(index_list, index_player):
        """Nearest opponent straight line distance"""
        opt_dist = 99999
        plr_pos = (chknm(info.LastScor.mVehicles[index_player].mPos.x),
                   chknm(info.LastScor.mVehicles[index_player].mPos.z),
                   0)
        for index in index_list:
            rel_dist = calc.pos2distance(
                        plr_pos,
                        (chknm(info.LastScor.mVehicles[index].mPos.x),
                         chknm(info.LastScor.mVehicles[index].mPos.z),
                         0),
                        )
            if index >= 0 and index != index_player and rel_dist < opt_dist:
                opt_dist = rel_dist
        return opt_dist

    @staticmethod
    def radar_pos(plr_gps, opt_gps, index):
        """Calculate vehicle coordinates, is lapped, orientation"""
        if index >= 0:
            new_pos = calc.rotate_pos(plr_gps[0], opt_gps[1], opt_gps[2])
            ori_diff = opt_gps[0] - plr_gps[0]  # opponent orientation - player orientation
            is_lapped = opt_gps[3]
        else:
            new_pos = (-99999, -99999)
            ori_diff = 0
            is_lapped = 0
        return new_pos, ori_diff, is_lapped
