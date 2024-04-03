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
Relative module
"""

import logging
import threading
from functools import lru_cache
from itertools import chain
from operator import itemgetter

from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_relative"
ALL_PLACES = list(range(1, 128))

logger = logging.getLogger(__name__)


class Realtime:
    """Relative info"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.user.setting[self.module_name]
        self.stopped = True
        self.event = threading.Event()

    def start(self):
        """Start update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__update_data, daemon=True).start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: module relative")

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __update_data(self):
        """Update module data"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                veh_total = max(api.read.vehicle.total_vehicles(), 1)
                plr_index = api.read.vehicle.player_index()
                plr_place = api.read.vehicle.place()

                # Create relative list, reverse-sort by relative distance
                rel_dist_list = sorted(self.__relative_dist_list(veh_total), reverse=True)
                rel_idx_list = self.__relative_index_list(rel_dist_list, plr_index)

                # Create standings list
                (class_pos_list, place_index_list, is_multi_class
                 ) = self.__class_position_list(veh_total)
                stand_idx_list = self.__standings_index_list(
                    veh_total, plr_index, plr_place,
                    class_pos_list, place_index_list, is_multi_class)

                # Output data
                minfo.relative.classes = class_pos_list
                minfo.relative.relative = rel_idx_list
                minfo.relative.standings = stand_idx_list

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: module relative")

    def __relative_index_list(self, rel_dist_list, plr_index):
        """Create player-centered relative index list"""
        if not rel_dist_list:
            return rel_dist_list
        # Get vehicle number from relative widget
        max_rel_veh, add_front, add_behind = max_relative_vehicles(
            self.cfg.user.setting["relative"]["additional_players_front"],
            self.cfg.user.setting["relative"]["additional_players_behind"])
        # Extract vehicle index to create new sorted vehicle list
        sorted_veh_list = [_dist[1] for _dist in rel_dist_list]
        # Locate player index position in list
        if plr_index in sorted_veh_list:
            plr_pos = sorted_veh_list.index(plr_index)
        else:
            plr_pos = 0  # prevent index not found in list error
        # Append with -1 if less than max number of vehicles
        num_diff = max_rel_veh - len(sorted_veh_list)
        if num_diff > 0:
            sorted_veh_list += [-1] * num_diff
        # Slice: max number of front players -> player index position
        front_cut = sorted_veh_list[max(plr_pos - 3 - add_front, 0):plr_pos]
        # Find number of missing front players (which is located at the end of list)
        front_miss = 3 + add_front - len(front_cut)
        front_list = sorted_veh_list[len(sorted_veh_list) - front_miss:] + front_cut
        # Slice: player index position -> max number of behind players
        behind_cut = sorted_veh_list[plr_pos:plr_pos + 4 + add_behind]
        # Find number of missing behind players (which is located at the beginning of list)
        behind_miss = 4 + add_behind - len(behind_cut)
        behind_list = behind_cut + sorted_veh_list[:behind_miss]
        # Combine index list
        front_list.extend(behind_list)
        return front_list

    def __relative_dist_list(self, veh_total):
        """Calculate relative distance"""
        track_length = api.read.lap.track_length()  # track length
        plr_dist = api.read.lap.distance()
        race_check = bool(
            api.read.session.in_race() and not
            self.cfg.user.setting["relative"]["show_vehicle_in_garage_for_race"]
        )
        for index in range(veh_total):
            in_garage = api.read.vehicle.in_garage(index)
            opt_dist = api.read.lap.distance(index)
            # Whether to hide vehicle in garage during race (ex. retired)
            if not race_check or not in_garage:
                rel_dist = calc.circular_relative_distance(
                    track_length, plr_dist, opt_dist)
                yield (rel_dist, index)  # relative distance, player index

    def __class_position_list(self, veh_total):
        """Create vehicle class position list"""
        raw_veh_class = list(self.__raw_class_data(veh_total))
        split_veh_list = tuple(zip(*raw_veh_class))
        # Multi-class check
        is_multi_class = len(set(split_veh_list[0])) > 1
        # Create overall vehicle place, player index list
        place_index_list = sorted(zip(split_veh_list[1], split_veh_list[2]))
        # Create class position list
        raw_veh_class.sort()  # sort by vehicle class
        class_position_list = sorted(self.__sort_class_data(raw_veh_class))
        return class_position_list, place_index_list, is_multi_class

    @staticmethod
    def __raw_class_data(veh_total):
        """Raw vehicle class data"""
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
    def __sort_class_data(sorted_veh_class):
        """Sort vehicle class position data"""
        laptime_session_best = calc.session_best_laptime(sorted_veh_class, 3)
        laptime_class_best = 99999
        initial_class = sorted_veh_class[0][0]
        position_in_class = 0
        player_index_ahead = -1
        player_index_behind = -1
        total_veh = len(sorted_veh_class)

        for idx, veh_sort in enumerate(sorted_veh_class):
            if veh_sort[0] == initial_class:
                position_in_class += 1
            else:
                initial_class = veh_sort[0]  # reset init name
                position_in_class = 1  # reset position counter

            if position_in_class == 1:
                laptime_class_best = veh_sort[3]
                player_index_ahead = -1  # no player ahead

            if (idx + 1 < total_veh  # check next index within range
                and sorted_veh_class[idx + 1][0] == veh_sort[0]):  # next player is in same class
                player_index_behind = sorted_veh_class[idx + 1][2]
            else:
                player_index_behind = -1

            yield (
                veh_sort[2],       # 0 - 2 player index
                position_in_class,  # 1 - position in class
                veh_sort[0],       # 2 - 0 class name
                laptime_session_best,  # 3 session best
                laptime_class_best,  # 4 classes best
                player_index_ahead,  # 5 player index ahead
                player_index_behind,  # 6 player index behind
            )
            player_index_ahead = veh_sort[2]

    def __standings_index_list(
        self, veh_total, plr_index, plr_place, class_pos_list, place_index_list, is_multi_class):
        """Create standings index list"""
        veh_top = min_top_vehicles_in_class(
            self.cfg.user.setting["standings"]["min_top_vehicles"])

        if self.cfg.user.setting["standings"]["enable_multi_class_split_mode"] and is_multi_class:
            veh_limit_other = max_vehicles_in_class(
                self.cfg.user.setting["standings"]["max_vehicles_per_split_others"], veh_top)
            veh_limit_player = max_vehicles_in_class(
                self.cfg.user.setting["standings"]["max_vehicles_per_split_player"], veh_top, 2)

            sorted_class_pos_list = sorted(
                class_pos_list,        # sort by:
                key=itemgetter(2,4,1)  # 2 class name, 4 class best laptime, 1 class position
            )
            class_collection = sorted(
                split_class_list(sorted_class_pos_list),
                key=sort_class_collection  # sort by class best laptime
            )
            standing_index = list(chain(*list(  # combine class index lists group
                self.__class_standings_index(
                    veh_top, plr_index, class_collection, veh_limit_other, veh_limit_player
                )
            )))
        else:
            veh_limit = max_vehicles_in_class(
                self.cfg.user.setting["standings"]["max_vehicles_combined_mode"], veh_top, 2)
            standing_index = self.__calc_standings_index(
                veh_top, veh_total, veh_limit, plr_place, place_index_list)

        return standing_index

    def __class_standings_index(
            self, veh_top, plr_index, class_collection, veh_limit_other, veh_limit_player):
        """Generate class standings index list from class list collection"""
        for class_list in class_collection:
            # 0 index, 1 class pos, 2 class name, 3 session best, 4 classes best
            class_split = list(zip(*class_list))
            veh_total = class_split[1][-1]  # last pos in class
            veh_limit = veh_limit_other
            plr_place = 0
            place_index_list = list(zip(class_split[1], class_split[0]))
            if plr_index in class_split[0]:
                veh_limit = veh_limit_player
                local_index = class_split[0].index(plr_index)
                plr_place = class_split[1][local_index]

            yield self.__calc_standings_index(
                veh_top, veh_total, veh_limit, plr_place, place_index_list)

    def __calc_standings_index(
            self, veh_top, veh_total, veh_limit, plr_place, place_index_list):
        """Create vehicle standings index list"""
        # Create reference place list
        if plr_place <= veh_top or veh_total <= veh_limit:
            ref_place_list = ALL_PLACES[:veh_limit]
        else:
            # Create player centered place list
            plr_center_list = list(self.__relative_nearby_place_index(
                veh_top, veh_total, plr_place, veh_limit))
            ref_place_list = sorted(ALL_PLACES[:veh_top] + plr_center_list)

        # Create final standing index list
        standing_index_list = list(
            self.__player_index_from_place_reference(ref_place_list, place_index_list))
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
    def __player_index_from_place_reference(ref_place_list, place_index_list):
        """Match place from reference list to generate player index list"""
        max_places = len(place_index_list)
        for ref_idx in ref_place_list:
            if 0 < ref_idx <= max_places:  # prevent out of range
                yield place_index_list[ref_idx-1][1]  # 1 vehicle index
        yield -1  # append an empty index as gap between classes


def split_class_list(input_list):
    """Split class list into class collection"""
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


@lru_cache(maxsize=1)
def max_relative_vehicles(add_front: int, add_behind: int, min_veh: int = 7) -> tuple:
    """Maximum number of vehicles in relative list"""
    add_front = min(max(int(add_front), 0), 60)
    add_behind = min(max(int(add_behind), 0), 60)
    return min_veh + add_front + add_behind, add_front, add_behind


@lru_cache(maxsize=1)
def min_top_vehicles_in_class(min_top_veh: int) -> int:
    """Minimum number of top vehicles in class list

    min_top_veh: value range limited in 1 to 5
    """
    return  min(max(int(min_top_veh), 1), 5)


@lru_cache(maxsize=2)
def max_vehicles_in_class(max_cls_veh: int, min_top_veh: int, min_add_veh: int = 0) -> int:
    """Maximum number of vehicles in class list

    max_cls_veh: maximum vehicles per class limit
    min_top_veh: minimum top vehicles limit
    min_add_veh: minimum addition vehicles limit (for class has local player)
    """
    return max(int(max_cls_veh), min_top_veh + min_add_veh)


def sort_class_collection(collection):
    """Sort class collection list"""
    return collection[0][4]  # 4 class best laptime
