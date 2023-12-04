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
Relative module
"""

import logging
import time
import threading
from itertools import chain

from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_relative"

logger = logging.getLogger(__name__)


class Realtime:
    """Relative info"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: module relative")

    def __calculation(self):
        """Create relative list with vehicle class info"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                veh_total = max(api.read.vehicle.total_vehicles(), 1)
                plr_index = api.read.vehicle.player_index()
                plr_place = api.read.vehicle.place()

                # Create relative list
                rel_dist_list = list(self.__relative_dist_list(veh_total))
                rel_idx_list = self.__relative_index_list(
                    rel_dist_list, plr_index) if rel_dist_list else None

                # Create standings list
                (class_pos_list, unique_class_list, place_index_list
                 ) = self.__class_position_list(veh_total)
                stand_idx_list = self.__standings_index_list(
                    veh_total, plr_index, plr_place,
                    class_pos_list, unique_class_list, place_index_list)

                # Output data
                minfo.relative.classes = class_pos_list
                minfo.relative.relative = rel_idx_list
                minfo.relative.standings = stand_idx_list

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: module relative")

    def __relative_index_list(self, rel_dist_list, plr_index):
        """Create player-centered relative index list"""
        add_front = min(max(int(
            self.cfg.setting_user["relative"]["additional_players_front"]), 0), 60)
        add_behind = min(max(int(
            self.cfg.setting_user["relative"]["additional_players_behind"]), 0), 60)
        # Reverse-sort by relative distance
        reverse_dist_list = sorted(rel_dist_list, reverse=True)
        # Extract vehicle index to create new sorted vehicle list
        sorted_veh_list = list(list(zip(*reverse_dist_list))[1])
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
        selected_index = [sorted_veh_list[index] for index in range(
            int(plr_num - 3 - add_front), int(plr_num + 4 + add_behind))]
        return selected_index

    def __relative_dist_list(self, veh_total):
        """Calculate relative distance"""
        track_length = api.read.lap.track_length()  # track length
        plr_dist = api.read.lap.distance()
        race_check = bool(
            api.read.session.in_race() and not
            self.cfg.setting_user["relative"]["show_vehicle_in_garage_for_race"]
        )
        for index in range(veh_total):
            in_garage = api.read.vehicle.in_garage(index)
            opt_dist = api.read.lap.distance(index)
            if show_vehicles(race_check, in_garage):
                rel_dist = calc.circular_relative_distance(
                    track_length, plr_dist, opt_dist)
                yield (rel_dist, index)  # relative distance, player index

    def __class_position_list(self, veh_total):
        """Create vehicle class position list"""
        raw_veh_class = list(self.__class_data(veh_total))
        split_veh_list = tuple(zip(*raw_veh_class))
        # Create unique vehicle class list
        unique_class_list = list(set(split_veh_list[0]))
        # Create overall vehicle place, player index list
        place_index_list = sorted(list(zip(split_veh_list[1], split_veh_list[2])))
        # Sort & group different vehicle class list
        sorted_veh_class = sorted(raw_veh_class)
        class_position_list = list(
            self.__sort_class_data(sorted_veh_class, unique_class_list))
        return sorted(class_position_list), unique_class_list, place_index_list

    @staticmethod
    def __class_data(veh_total):
        """Get vehicle class data"""
        for index in range(veh_total):
            vehclass = api.read.vehicle.class_name(index)
            position = api.read.vehicle.place(index)
            laptime_best = api.read.timing.best_laptime(index)
            yield (
                vehclass,  # 0 vehicle class name
                position,  # 1 overall position/place
                index,     # 2 player index
                laptime_best if laptime_best > 0 else 99999, # 3 best lap time
            )

    @staticmethod
    def __sort_class_data(sorted_veh_class, unique_class_list):
        """Get vehicle class position data"""
        laptime_session_best = sorted(sorted_veh_class, key=lambda laptime:laptime[3])[0][3]
        laptime_class_best = 99999
        initial_class = unique_class_list[0]
        position_counter = 0  # position in class

        for veh_sort in sorted_veh_class:  # loop through sorted vehicle class list
            for veh_uniq in unique_class_list:  # unique vehicle class range
                if veh_sort[0] == veh_uniq:
                    if initial_class == veh_uniq:
                        position_counter += 1
                    else:
                        initial_class = veh_uniq  # reset init name
                        position_counter = 1  # reset position counter

                    if position_counter == 1:
                        laptime_class_best = veh_sort[3]

                    yield (
                        veh_sort[2],       # 0 - 2 player index
                        position_counter,  # 1 - position in class
                        veh_sort[0],       # 2 - 0 class name
                        laptime_session_best,  # 3 session best
                        laptime_class_best,  # 4 classes best
                    )

    def __standings_index_list(
        self, veh_total, plr_index, plr_place, class_pos_list, unique_class_list, place_index_list):
        """Create standings index list"""
        veh_top = min(max(int(self.cfg.setting_user["standings"]["min_top_vehicles"]), 1), 5)
        veh_limit = max(int(
            self.cfg.setting_user["standings"]["max_vehicles_combined_mode"]), veh_top + 2)

        if (self.cfg.setting_user["standings"]["enable_multi_class_split_mode"] and
           len(unique_class_list) > 1):
            sorted_class_pos_list = sorted(class_pos_list, key=sort_class)
            class_collection = sorted(list(
                split_class_list(sorted_class_pos_list)),
                key=lambda laptime:laptime[0][4])  # sort by class best laptime
            standing_index = list(chain(*list(  # combine class index lists group
                self.__class_standings_index(veh_top, plr_index, class_collection))))
        else:
            standing_index = self.__calc_standings_index(
                veh_top, veh_total, veh_limit, plr_place, place_index_list)

        return standing_index

    def __class_standings_index(self, veh_top, plr_index, class_collection):
        """Generate class standings index list from class list collection"""
        for class_list in class_collection:
            # 0 index, 1 class pos, 2 class name, 3 session best, 4 classes best
            class_split = list(zip(*class_list))
            veh_total = class_split[1][-1]  # last pos in class
            veh_limit = max(int(
                self.cfg.setting_user["standings"]["max_vehicles_per_split_others"]), veh_top)
            plr_place = 0
            place_index_list = list(zip(class_split[1], class_split[0]))
            if plr_index in class_split[0]:
                veh_limit = max(
                    int(self.cfg.setting_user["standings"]["max_vehicles_per_split_player"]),
                    veh_top + 2)
                local_index = class_split[0].index(plr_index)
                plr_place = class_split[1][local_index]

            yield self.__calc_standings_index(
                veh_top, veh_total, veh_limit, plr_place, place_index_list)

    def __calc_standings_index(
            self, veh_top, veh_total, veh_limit, plr_place, place_index_list):
        """Create vehicle standings index list"""
        # All vehicles place list
        all_veh_place_list = list(range(1, veh_total+1))

        # Create reference place list
        if plr_place <= veh_top or veh_total <= veh_limit:
            ref_place_list = all_veh_place_list[:veh_limit]
        else:
            # Create player centered place list
            plr_center_list = list(self.__relative_nearby_place_index(
                veh_top, veh_total, plr_place, veh_limit))
            ref_place_list = sorted(all_veh_place_list[:veh_top] + plr_center_list)

        # Create final standing index list
        standing_index_list = list(
            self.__place_index_from_reference(ref_place_list, place_index_list))
        #print(standings_index_list)
        return standing_index_list

    @staticmethod
    def __relative_nearby_place_index(veh_top, veh_total, plr_place, veh_limit):
        """Create nearby place index list relative to player"""
        max_range = veh_limit - veh_top
        counter = 0
        if plr_place:  # if player exist
            yield plr_place  # add player slot first
            counter += 1

        for veh in range(max_range):
            front = plr_place - 1 - veh
            rear = plr_place + 1 + veh
            if veh_top < front:
                yield front  # add front first
                counter += 1
                #max_range -= 1
                if counter >= max_range:
                    break
            if rear < veh_total:
                yield rear
                counter += 1
                #max_range -= 1
                if counter >= max_range:
                    break

    @staticmethod
    def __place_index_from_reference(ref_place_list, place_index_list):
        """Generate matched place index from reference list"""
        count = 0
        for veh in place_index_list:
            for place_index in ref_place_list:
                if place_index == veh[0]:  # 0 vehicle place
                    count += 1
                    yield veh[1]  # 1 vehicle index
                    break
        yield -1  # append an empty index as gap between classes


def show_vehicles(race_check, in_garage):
    """Vehicle filter"""
    if race_check:
        if not in_garage:
            return True  # not in garage, show
        return False  # in garage, hide
    return True  # not in race or off, show


def sort_class(class_list):
    """Sort class list"""
    return (
        class_list[2], # class name
        class_list[4], # class best laptime
        class_list[1], # class position
    )


def split_class_list(input_list):
    """Split class list collection"""
    class_name = input_list[0][2]
    index_start = 0
    index_end = 0
    for vehicle in input_list:
        if vehicle[2] == class_name:
            index_end +=1
        elif vehicle[2] != class_name:
            class_name = vehicle[2]
            yield input_list[index_start:index_end]
            index_start = index_end
            index_end +=1
    # Final split
    yield input_list[index_start:index_end]
