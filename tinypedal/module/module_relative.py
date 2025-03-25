#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from __future__ import annotations
from itertools import chain

from ..api_control import api
from ..calculation import zero_max, asym_max, circular_relative_distance
from ..const_common import MAX_VEHICLES, MAX_SECONDS, MAX_METERS, QUALIFY_DEFAULT
from ..module_info import minfo
from ._base import DataModule

REF_PLACES = tuple(range(1, MAX_VEHICLES + 1))
TEMP_DISTANCE = [[MAX_METERS, -1] for _ in range(MAX_VEHICLES)]
TEMP_CLASSES = [["", -1, -1, -1.0, -1.0] for _ in range(MAX_VEHICLES)]
TEMP_PLACES = [[-1, -1] for _ in range(MAX_VEHICLES)]
TEMP_CLASSES_POS = [[0, 1, "", 0.0, 0.0, -1, -1, False] for _ in range(MAX_VEHICLES)]


class Realtime(DataModule):
    """Relative & standings data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        output = minfo.relative
        setting_relative = self.cfg.user.setting["relative"]
        setting_standings = self.cfg.user.setting["standings"]
        last_version_update = None

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    last_veh_total = 0

                # Check setting
                if last_version_update != self.cfg.version_update:
                    last_version_update = self.cfg.version_update
                    show_in_garage = setting_relative["show_vehicle_in_garage"]
                    max_rel_veh, add_front, add_behind = max_relative_vehicles(
                        setting_relative["additional_players_front"],
                        setting_relative["additional_players_behind"])
                    is_split_mode = setting_standings["enable_multi_class_split_mode"]
                    min_top_veh = min_top_vehicles_in_class(
                        setting_standings["min_top_vehicles"])
                    veh_limit = max_vehicle_limit_set(  # 0 all, 1 other, 2 player
                        min_top_veh,
                        setting_standings["max_vehicles_combined_mode"],
                        setting_standings["max_vehicles_per_split_others"],
                        setting_standings["max_vehicles_per_split_player"])

                # Base info
                veh_total = max(api.read.vehicle.total_vehicles(), 1)
                plr_index = api.read.vehicle.player_index()
                plr_place = api.read.vehicle.place()

                # Get vehicles info
                (distance_index_list, classes_list, place_index_list,
                 laptime_session_best, is_multi_class
                 ) = get_vehicles_info(veh_total, plr_index, show_in_garage)

                # Create relative index list
                relative_index_list = create_relative_index(
                    distance_index_list, plr_index, max_rel_veh, add_front, add_behind)

                # Create vehicle class position list (initially ordered by class name)
                class_pos_list = create_position_in_class(classes_list, laptime_session_best)

                # Create standings index list
                standings_index_list = create_standings_index(
                    min_top_veh, veh_limit, plr_index, plr_place,
                    class_pos_list, place_index_list, is_split_mode and is_multi_class)

                # Sort vehicle class position list (by player index) for output
                class_pos_list.sort()

                # Race/start grid, update only if vehicle number changed
                if last_veh_total != veh_total:
                    last_veh_total = veh_total
                    qualifications = create_qualify_position(veh_total)
                    output.qualifications = qualifications

                # Output data
                output.relative = relative_index_list
                output.standings = standings_index_list
                output.classes = class_pos_list

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


def create_qualify_position(veh_total: int) -> list[tuple[int, int]]:
    """Create qualify position list

    Returns:
        list[(qualify overall, qualify in class)], ordered by "player index".
    """
    temp_class = sorted((
        api.read.vehicle.class_name(index),  # 0 class name
        api.read.vehicle.qualification(index),  # 1 qualification position
        index,  # 2 player index
    ) for index in range(veh_total))
    # Create grid position
    grid_classes = [QUALIFY_DEFAULT] * veh_total
    qualify_in_class = 0
    initial_class = None
    for veh_data in temp_class:
        if veh_data[0] == initial_class:
            qualify_in_class += 1
        else:
            initial_class = veh_data[0]
            qualify_in_class = 1
        grid_classes[veh_data[2]] = (veh_data[1], qualify_in_class)
    return grid_classes


def get_vehicles_info(veh_total: int, plr_index: int, show_in_garage: bool):
    """Get vehicles info: relative distance, classes, places, laptime"""
    track_length = api.read.lap.track_length()  # track length
    plr_dist = api.read.lap.distance()
    laptime_session_best = MAX_SECONDS
    last_class_name = None
    classes_count = 0

    for index in range(veh_total):
        # Update relative distance list
        if show_in_garage or index == plr_index or not api.read.vehicle.in_garage(index):
            rel_dist = circular_relative_distance(
                track_length, plr_dist, api.read.lap.distance(index))
        else:
            rel_dist = MAX_METERS
        TEMP_DISTANCE[index][:] = (  # slice assign
            rel_dist,  # 0 relative distance
            index,  # 1 player index
        )

        # Update classes list
        class_name = api.read.vehicle.class_name(index)
        position = api.read.vehicle.place(index)
        laptime_best = api.read.timing.best_laptime(index)
        laptime_last = api.read.timing.last_laptime(index)

        if laptime_last > 0 and not api.read.vehicle.in_pits(index):
            laptime_personal_last = laptime_last
        else:
            laptime_personal_last = MAX_SECONDS

        if laptime_best > 0:
            laptime_personal_best = laptime_best
            if laptime_best < laptime_session_best:
                laptime_session_best = laptime_best
        else:
            laptime_personal_best = MAX_SECONDS

        TEMP_CLASSES[index][:] = (  # slice assign
            class_name,  # 0 vehicle class name
            position,  # 1 overall position/place
            index,  # 2 player index
            laptime_personal_best,  # 3 best lap time
            laptime_personal_last,  # 4 last lap time (for fastest last lap check)
        )

        # Update place-index list
        TEMP_PLACES[index][:] = (  # slice assign
            position,  # 1 overall position/place
            index,     # 2 player index
        )

        # Check is multi classes
        if classes_count < 2 and last_class_name != class_name:
            last_class_name = class_name
            classes_count += 1

    # Sort output in-place
    new_distance = TEMP_DISTANCE[:veh_total]
    new_distance.sort(reverse=True)  # by reversed distance
    new_distance_index = [_dist[1] for _dist in new_distance if _dist[0] != MAX_METERS]

    new_classes = TEMP_CLASSES[:veh_total]
    new_classes.sort()  # by vehicle class

    new_place_index = TEMP_PLACES[:veh_total]
    new_place_index.sort()  # by overall position/place

    return (
        new_distance_index,  # -> distance_index_list
        new_classes,  # -> classes_list
        new_place_index,  # -> place_index_list
        laptime_session_best,
        classes_count > 1,  # -> is_multi_class
    )


def create_relative_index(
    distance_index_list: list, plr_index: int, max_rel_veh: int, add_front: int, add_behind: int):
    """Create player-centered relative index list"""
    if not distance_index_list:
        return distance_index_list
    # Locate player index position in list
    if plr_index in distance_index_list:
        plr_pos = distance_index_list.index(plr_index)
    else:
        plr_pos = 0  # prevent index not found in list error
    # Append with -1 if less than max number of vehicles
    num_diff = max_rel_veh - len(distance_index_list)
    if num_diff > 0:
        distance_index_list += [-1] * num_diff
    # Slice: max number of front players -> player index position
    front_cut = distance_index_list[max(plr_pos - 3 - add_front, 0):plr_pos]
    # Find number of missing front players (which is located at the end of list)
    front_miss = 3 + add_front - len(front_cut)
    front_list = distance_index_list[len(distance_index_list) - front_miss:] + front_cut
    # Slice: player index position -> max number of behind players
    behind_cut = distance_index_list[plr_pos:plr_pos + 4 + add_behind]
    # Find number of missing behind players (which is located at the beginning of list)
    behind_miss = 4 + add_behind - len(behind_cut)
    behind_list = behind_cut + distance_index_list[:behind_miss]
    # Combine index list
    front_list.extend(behind_list)
    return front_list


def create_position_in_class(sorted_veh_class: list, laptime_session_best: float):
    """Create vehicle position in class list"""
    initial_class = None
    position_in_class = 0
    player_index_ahead = -1
    player_index_behind = -1
    laptime_class_best = MAX_SECONDS
    last_fastest_laptime = MAX_SECONDS
    last_fastest_player_index = -1
    veh_total = len(sorted_veh_class)

    for index, veh_sort in enumerate(sorted_veh_class):
        if veh_sort[0] == initial_class:
            position_in_class += 1
        else:
            if last_fastest_player_index != -1:  # mark fastest last lap
                TEMP_CLASSES_POS[last_fastest_player_index][7] = True
            initial_class = veh_sort[0]  # reset init name
            position_in_class = 1  # reset position counter
            last_fastest_laptime = MAX_SECONDS  # reset last fastest
            last_fastest_player_index = -1  # reset player index

        if position_in_class == 1:
            laptime_class_best = veh_sort[3]
            player_index_ahead = -1  # no player ahead

        if last_fastest_laptime > veh_sort[4]:
            last_fastest_laptime = veh_sort[4]
            last_fastest_player_index = index

        # Check next index within range & is in same class
        next_index = index + 1
        if next_index < veh_total and sorted_veh_class[next_index][0] == veh_sort[0]:
            player_index_behind = sorted_veh_class[next_index][2]
        else:
            player_index_behind = -1

        TEMP_CLASSES_POS[index][:] = (
            veh_sort[2],       # 0 - 2 player index
            position_in_class,  # 1 - position in class
            veh_sort[0],       # 2 - 0 class name
            laptime_session_best,  # 3 session best
            laptime_class_best,  # 4 classes best
            player_index_ahead,  # 5 player index ahead
            player_index_behind,  # 6 player index behind
            False,  # 7 is class fastest last laptime
        )
        player_index_ahead = veh_sort[2]

    if last_fastest_player_index != -1:  # mark for last class
        TEMP_CLASSES_POS[last_fastest_player_index][7] = True

    return TEMP_CLASSES_POS[:veh_total]


def create_standings_index(
    min_top_veh: int, veh_limit: tuple, plr_index: int, plr_place: int,
    class_pos_list: list, place_index_list: list, is_multi_class: bool):
    """Create standings index list"""
    if is_multi_class:
        class_collection = sorted(
            split_class_list(class_pos_list),
            key=sort_class_collection  # sort by class best laptime
        )
        standing_index = list(chain(*list(  # combine class index lists group
            create_class_standings_index(
                min_top_veh, plr_index, class_collection, veh_limit[1], veh_limit[2]
            )
        )))
    else:
        standing_index = calc_standings_index(
            min_top_veh, veh_limit[0], plr_place, place_index_list)
    return standing_index


def create_class_standings_index(
    min_top_veh: int, plr_index: int, class_collection: list,
    veh_limit_other: int, veh_limit_player: int):
    """Generate class standings index list from class list collection"""
    for class_list in class_collection:
        # 0 index, 1 class pos, 2 class name, 3 session best, 4 classes best
        class_split = list(zip(*class_list))
        place_index_list = list(zip(class_split[1], class_split[0]))

        if plr_index in class_split[0]:
            veh_limit = veh_limit_player
            local_index = class_split[0].index(plr_index)
            plr_place = class_split[1][local_index]
        else:
            veh_limit = veh_limit_other
            plr_place = 0

        yield calc_standings_index(
            min_top_veh, veh_limit, plr_place, place_index_list)


def calc_standings_index(
    min_top_veh: int, veh_limit: int, plr_place: int, place_index_list: list):
    """Calculate vehicle standings index list"""
    veh_total = len(place_index_list)
    ref_place_list = create_reference_place(min_top_veh, veh_total, plr_place, veh_limit)
    # Create final standing index list
    return list(player_index_from_place_reference(ref_place_list, place_index_list, veh_total))


def create_reference_place(
    min_top_veh: int, veh_total: int, plr_place: int, veh_limit: int):
    """Create reference place list"""
    if veh_total <= veh_limit:
        return REF_PLACES[:veh_total]
    if plr_place <= min_top_veh:
        return REF_PLACES[:veh_limit]
    # Find nearby slice range relative to player
    max_cut_range = veh_limit - min_top_veh
    # Number of rear slots, should be equal or less than front slots (exclude player slot)
    rear_cut_count = (max_cut_range - 1) // 2  # exclude player slot, then floor divide
    front_cut_count = max_cut_range - rear_cut_count  # include player slot
    # Find front slice limit
    front_cut_raw = plr_place - front_cut_count
    if front_cut_raw < min_top_veh:
        front_cut_raw = min_top_veh
    # Find rear slice limit
    rear_cut_max = front_cut_raw + max_cut_range
    if rear_cut_max > veh_total:
        rear_cut_max = veh_total
    front_cut_max = rear_cut_max - max_cut_range
    return REF_PLACES[:min_top_veh] + REF_PLACES[front_cut_max:rear_cut_max]


def player_index_from_place_reference(
    ref_place_list: tuple, place_index_list: list, veh_total: int):
    """Match place from reference list to generate player index list"""
    for ref_idx in ref_place_list:
        if 0 < ref_idx <= veh_total:  # prevent out of range
            yield place_index_list[ref_idx - 1][1]  # 1 vehicle index
        else:
            break
    yield -1  # append an empty index as gap between classes


def split_class_list(class_list: list):
    """Split class list into class collection"""
    class_name = class_list[0][2]
    index_start = 0
    index_end = 0
    for vehicle in class_list:
        if vehicle[2] == class_name:
            index_end +=1
        elif vehicle[2] != class_name:
            class_name = vehicle[2]
            yield class_list[index_start:index_end]
            index_start = index_end
            index_end +=1
    # Final split
    yield class_list[index_start:index_end]


def max_relative_vehicles(add_front: int, add_behind: int, min_veh: int = 7):
    """Maximum number of vehicles in relative list"""
    add_front = int(zero_max(add_front, 60))
    add_behind = int(zero_max(add_behind, 60))
    max_vehicles = min_veh + add_front + add_behind
    return max_vehicles, add_front, add_behind


def min_top_vehicles_in_class(min_top_veh: int) -> int:
    """Minimum number of top vehicles in class list

    min_top_veh: value range limited in 1 to 5
    """
    return int(asym_max(min_top_veh, 1, 5))


def max_vehicles_in_class(max_cls_veh: int, min_top_veh: int, min_add_veh: int = 0) -> int:
    """Maximum number of vehicles in class list

    max_cls_veh: maximum vehicles per class limit
    min_top_veh: minimum top vehicles limit
    min_add_veh: minimum addition vehicles limit (for class has local player)
    """
    return max(int(max_cls_veh), min_top_veh + min_add_veh)


def max_vehicle_limit_set(
    min_top_veh: int, max_all: int, max_others: int, max_player: int):
    """Create max vehicle limit set"""
    limit_all = max_vehicles_in_class(max_all, min_top_veh, 2)
    limit_other = max_vehicles_in_class(max_others, min_top_veh)
    limit_player = max_vehicles_in_class(max_player, min_top_veh, 2)
    return limit_all, limit_other, limit_player


def sort_class_collection(collection: list):
    """Sort class collection list"""
    return collection[0][4]  # 4 class best laptime
