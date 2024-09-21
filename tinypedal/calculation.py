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
Calculation function
"""

import math
import statistics


distance = math.dist  # coordinates distance
mean = statistics.fmean
vel2speed = math.hypot  # velocity to speed
std_dev = statistics.stdev  # sample standard deviation
rad2deg = math.degrees  # radians to degrees
oriyaw2rad = math.atan2  # orientation yaw to radians


# Unit conversion
def meter2millmeter(meter):
    """Convert meter to millimeter"""
    return meter * 1000


def meter2feet(meter):
    """Convert meter to feet"""
    return meter * 3.2808399


def meter2kilometer(meter):
    """Convert meter to kilometer"""
    return meter * 0.001


def meter2mile(meter):
    """Convert meter to mile"""
    return meter / 1609.344


def mps2kph(meter):
    """meter per sec to kilometers per hour"""
    return meter * 3.6


def mps2mph(meter):
    """Meter per sec to miles per hour"""
    return meter * 2.23693629


def celsius2fahrenheit(temperature):
    """Celsius to Fahrenheit"""
    return temperature * 1.8 + 32


def liter2gallon(liter):
    """Liter to Gallon"""
    return liter * 0.26417205


def kelvin2celsius(kelvin):
    """Kelvin to Celsius"""
    return max(kelvin - 273.15, -99)


def kpa2psi(kilopascal):
    """Kilopascal to psi"""
    return kilopascal * 0.14503774


def kpa2bar(kilopascal):
    """Kilopascal to bar"""
    return kilopascal * 0.01


def kw2hp(kilowatt):
    """Kilowatt to imperial horsepower (hp)"""
    return kilowatt * 1.341


def kw2ps(kilowatt):
    """Kilowatt to metric horsepower (ps)"""
    return kilowatt * 1.3596


# Common
def sym_range(value, rng):
    """Symmetric range"""
    return min(max(value, -rng), rng)


def zero_one_range(value):
    """Limit value in range 0 to 1 """
    return min(max(value, 0), 1)


def mean_iter(avg, value, num_samples):
    """Average value"""
    return (avg * num_samples + value) / (num_samples + 1)


def min_vs_avg(data):
    """Min vs average"""
    return abs(min(data) - mean(data))


def max_vs_avg(data):
    """Max vs average"""
    return abs(max(data) - mean(data))


def max_vs_min(data):
    """Max vs min"""
    return max(data) - min(data)


def engine_power(torque, rpm):
    """Engine power (kW)"""
    if torque > 0:
        return torque * rpm / 9549.3
    return 0


def rake(height_fl, height_fr, height_rl, height_rr):
    """Raw rake (millmeters)"""
    return (height_rr + height_rl - height_fr - height_fl) * 0.5


def rake2angle(v_rake, wheelbase):
    """Rake angle based on wheelbase value (millmeters) set in JSON"""
    if wheelbase:
        return math.atan(rad2deg(v_rake / wheelbase))
    return 0


def rot2radius(speed, angular_speed):
    """Angular speed to radius"""
    if angular_speed:
        return abs(speed / angular_speed)
    return 0


def slip_ratio(w_rot, w_radius, v_speed):
    """Slip ratio (percentage), speed unit in m/s"""
    if int(v_speed):  # set minimum to avoid flickering while stationary
        return (abs(w_rot) * w_radius - v_speed) / v_speed
    return 0


def slip_angle(v_lat, v_lgt):
    """Slip angle (radians)"""
    if v_lgt:
        return math.atan(v_lat / v_lgt)
    return 0


def gforce(value, g_accel):
    """G force"""
    if g_accel:
        return value / g_accel
    return 0


def force_ratio(value1, value2):
    """Force ratio from Newtons"""
    if int(value2):
        return abs(100 * value1 / value2)
    return 0


def rotate_coordinate(ori_rad, value1, value2):
    """Rotate x y coordinates"""
    sin_rad = math.sin(ori_rad)
    cos_rad = math.cos(ori_rad)
    return (cos_rad * value1 - sin_rad * value2,
            cos_rad * value2 + sin_rad * value1)


def wheel_axle_rotation(rot_left, rot_right):
    """Wheel axle rotation"""
    # Make sure both wheels rotate towards same direction
    if rot_left >= 0 <= rot_right or rot_left <= 0 >= rot_right:
        return (rot_left + rot_right) / 2
    return 0


def wheel_rotation_bias(rot_axle, rot_left, rot_right):
    """Wheel rotation bias (difference) against axle rotation"""
    if rot_axle:
        return abs((rot_left - rot_right) / rot_axle)
    return 0


def wheel_rotation_ratio(rot_axle, rot_left, rot_right):
    """Calculate wheel rotation ratio between left and right wheel on same axle

    Range from 0 to 2. 1 means both wheels rotate at same speed.
    """
    if rot_axle:
        return rot_left / rot_axle, rot_right / rot_axle
    return 1, 1


def lap_progress_distance(dist, length):
    """Current lap progress (distance into lap) fraction"""
    if length:
        return min(max(dist / length, 0), 1)
    return 0


def lap_progress_correction(percent, laptime):
    """Lap progress desync correction"""
    if percent > 0.5 > laptime:
        return 0
    return percent


def lap_progress_offset(laptime, lap_into, seconds_delay):
    """Lap progress offset (fraction) by seconds delay, such as pit stop"""
    if laptime:
        return lap_into - seconds_delay / laptime
    return 0


def lap_progress_difference(ahead_laptime, behind_laptime):
    """Lap progress difference (fraction) between player ahead & behind"""
    if behind_laptime > ahead_laptime > 0:
        return (behind_laptime - ahead_laptime) / behind_laptime
    if ahead_laptime > behind_laptime > 0:
        return (ahead_laptime - behind_laptime) / ahead_laptime
    return 0


def circular_relative_distance(circle_length, plr_dist, opt_dist):
    """Relative distance between opponent & player in a circle"""
    rel_dist = opt_dist - plr_dist
    # Relative dist is greater than half of track length
    if abs(rel_dist) > circle_length * 0.5:
        if opt_dist > plr_dist:
            rel_dist -= circle_length  # opponent is behind player
        elif opt_dist < plr_dist:
            rel_dist += circle_length  # opponent is ahead player
    return rel_dist


def lap_difference(opt_laps, plr_laps, lap_ahead=1, lap_behind=1):
    """Calculate lap difference between target opponent and player

    Positive: lap(s) ahead.
    Negative: lap(s) behind.
    Zero: on same lap.
    """
    lap_diff = opt_laps - plr_laps
    if lap_diff > lap_ahead or lap_diff < -lap_behind:
        return lap_diff
    return 0


def relative_time_gap(rel_dist, plr_speed, opt_speed):
    """Relative time gap between opponent & player"""
    speed = max(plr_speed, opt_speed)
    if speed > 1:
        return abs(rel_dist / speed)
    return 0


def linear_interp(x, x1, y1, x2, y2):
    """Linear interpolation"""
    x_diff = x2 - x1
    if x_diff:
        return y1 + (x - x1) * (y2 - y1) / x_diff
    return y1


# Timing
def clock_time(seconds: float, start: int = 0, scale: int = 1) -> float:
    """Clock time (seconds) looped in full 24 hours, 0 to 86400"""
    time_curr = start + seconds * scale
    return time_curr - time_curr // 86400 * 86400


def sec2sessiontime(seconds: float) -> str:
    """Session time (hour:min:sec)"""
    return f"{seconds // 3600:02.0f}:{seconds // 60 % 60:02.0f}:{min(seconds % 60, 59):02.0f}"


def sec2laptime(seconds: float) -> str:
    """Lap time (min:sec.ms)"""
    if seconds > 60:
        return f"{seconds // 60:.0f}:{seconds % 60:06.3f}"
    return f"{seconds % 60:.3f}"


def sec2laptime_full(seconds: float) -> str:
    """Lap time full (min:sec.ms)"""
    return f"{seconds // 60:.0f}:{seconds % 60:06.3f}"


def sec2stinttime(seconds: float) -> str:
    """Stint time (min:sec)"""
    return f"{seconds // 60:02.0f}:{min(seconds % 60, 59):02.0f}"


def delta_telemetry(position: float, target: float, delta_list: list,
    condition: bool = True) -> float:
    """Calculate delta telemetry data"""
    if not condition:
        return 0
    index_higher = binary_search_higher_column(
        delta_list, position, 0, len(delta_list) - 1)
    if index_higher > 0:
        index_lower = index_higher - 1
        return (
            target - linear_interp(
                position,
                delta_list[index_lower][0],
                delta_list[index_lower][1],
                delta_list[index_higher][0],
                delta_list[index_higher][1],
            )
        )
    return 0


def mov_avg(sample_set: any, source: float) -> float:
    """Calculate moving average"""
    if not sample_set:
        return source
    sample_set.append(source)  # use deque
    return mean(sample_set)


def exp_mov_avg(factor: float, ema_last: float, source: float) -> float:
    """Calculate exponential moving average"""
    return ema_last + factor * (source - ema_last)


def ema_factor(samples: int) -> float:
    """Calculate smoothing factor for exponential moving average"""
    return 2 / (samples + 1)


def accumulated_sum(data: list, end_index: int) -> float:
    """Calculate accumulated sum"""
    return sum(data[:end_index + 1])


# Search
def search_column_key(key, column=None):
    """Search column key"""
    if column is None:
        return key
    return key[column]


def linear_search_higher(data, target, column=None):
    """linear search nearest value higher index from unordered list"""
    #key = lambda x:x[column] if column >= 0 else x
    end = len(data) - 1
    nearest = float("inf")
    for index, data_row in enumerate(data):
        if target <= search_column_key(data_row, column) < nearest:
            nearest = search_column_key(data_row, column)
            end = index
    return end


def binary_search_lower(data, target, start, end):
    """Binary search nearest value lower index from ordered list"""
    while start <= end:
        center = (start + end) // 2
        if target == data[center]:
            return center
        if target > data[center]:
            start = center + 1
        else:
            end = center - 1
    return end


def binary_search_higher(data, target, start, end):
    """Binary search nearest value higher index from ordered list"""
    while start < end:
        center = (start + end) // 2
        if target == data[center]:
            return center
        if target > data[center]:
            start = center + 1
        else:
            end = center
    return end


def binary_search_lower_column(data, target, start, end, column=0):
    """Binary search nearest value lower index from ordered list with column index"""
    while start <= end:
        center = (start + end) // 2
        if target == data[center][column]:
            return center
        if target > data[center][column]:
            start = center + 1
        else:
            end = center - 1
    return end


def binary_search_higher_column(data, target, start, end, column=0):
    """Binary search nearest value higher index from ordered list with column index"""
    while start < end:
        center = (start + end) // 2
        if target == data[center][column]:
            return center
        if target > data[center][column]:
            start = center + 1
        else:
            end = center
    return end


# Plot
def zoom_map(coords, map_scale, margin=0):
    """Zoom map data to specific scale, then add margin"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*coords))
    # Offset X, Y
    map_offset = min(x_range) * map_scale - margin, min(y_range) * map_scale - margin
    # Scale map coordinates
    x_range_scaled = [x_pos * map_scale - map_offset[0] for x_pos in x_range]
    y_range_scaled = [y_pos * map_scale - map_offset[1] for y_pos in y_range]
    # Map width, height
    map_size = max(x_range_scaled) + margin, max(y_range_scaled) + margin
    return tuple(zip(x_range_scaled, y_range_scaled)), map_size, map_offset


def scale_map(coords, area_size, margin=0):
    """Scale map data"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*coords))
    # Map size: x=width, y=height
    map_range = min(x_range), max(x_range), min(y_range), max(y_range)
    map_size = map_range[1] - map_range[0], map_range[3] - map_range[2]
    # Display area / map_size
    map_scale = (area_size - margin * 2) / max(map_size[0], map_size[1])
    # Alignment offset
    if map_size[0] > map_size[1]:
        map_offset = margin, (area_size - map_size[1] * map_scale) * 0.5
    else:
        map_offset = (area_size - map_size[0] * map_scale) * 0.5, margin
    x_range_scaled = [(x_pos - map_range[0]) * map_scale + map_offset[0]
                        for x_pos in x_range]
    y_range_scaled = [(y_pos - map_range[2]) * map_scale + map_offset[1]
                        for y_pos in y_range]
    return list(zip(x_range_scaled, y_range_scaled)), map_range, map_scale, map_offset


def scale_elevation(coords, area_width, area_height):
    """Scale elevation data"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*coords))
    # Map size: x=width, y=height
    map_range = min(x_range), max(x_range), min(y_range), max(y_range)
    map_size = map_range[1] - map_range[0], map_range[3] - map_range[2]
    # Display area / map_size
    map_scale = area_width / map_size[0], area_height / map_size[1]
    x_range_scaled = [(x_pos - map_range[0]) * map_scale[0]
                        for x_pos in x_range]
    y_range_scaled = [(y_pos - map_range[2]) * map_scale[1]
                        for y_pos in y_range]
    return list(zip(x_range_scaled, y_range_scaled)), map_range, map_scale


def svg_view_box(coords, margin=0):
    """Map bounding box"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*coords))
    # Map size: x=width, y=height
    map_range = min(x_range), max(x_range), min(y_range), max(y_range)
    map_size = map_range[1] - map_range[0], map_range[3] - map_range[2]
    x1 = round(map_range[0] - margin, 4)
    y1 = round(map_range[2] - margin, 4)
    x2 = round(map_size[0] + margin * 2, 4)
    y2 = round(map_size[1] + margin * 2, 4)
    return f"{x1} {y1} {x2} {y2}"


def line_intersect_coords(coord_a, coord_b, radians, length):
    """Create intersect line coordinates from 2 coordinates

    coord_a: coordinate A
    coord_b: coordinate B
    radians: amount rotation to apply
    length: length between coordinates
    """
    yaw_rad = oriyaw2rad(
        coord_b[1] - coord_a[1],
        coord_b[0] - coord_a[0]
    )
    pos_x1, pos_y1 = rotate_coordinate(
        yaw_rad + radians,
        length,  # x pos
        0  # y pos
    )
    pos_x2, pos_y2 = rotate_coordinate(
        yaw_rad - radians,
        length,  # x pos
        0  # y pos
    )
    return (pos_x1 + coord_a[0],
            pos_y1 + coord_a[1],
            pos_x2 + coord_a[0],
            pos_y2 + coord_a[1])


def session_best_laptime(data_list: list, column: int, laptime: int = 99999):
    """Find session best lap time from data list"""
    for data in data_list:
        if 0 < data[column] < laptime:
            laptime = data[column]
    return laptime


# Fuel
def lap_type_full_laps_remain(laps_total, laps_finished):
    """Lap type race remaining laps count from finish line"""
    return laps_total - laps_finished


def lap_type_laps_remain(laps_full_remain, lap_into):
    """Lap type race remaining laps count from current on track position"""
    return laps_full_remain - lap_into


def end_timer_laps_remain(lap_into, laptime_last, seconds_remain):
    """Estimated remaining laps(fraction) count from finish line after race timer ended"""
    if laptime_last:
        if seconds_remain <= 0:
            return lap_into
        return seconds_remain / laptime_last + lap_into
    return 0


def time_type_full_laps_remain(lap_into, laptime_last, seconds_remain):
    """Estimated full remaining laps count from finish line after race timer ended"""
    # alternative-lap-into = laptime_current / laptime_last % 1
    return math.ceil(end_timer_laps_remain(lap_into, laptime_last, seconds_remain))


def time_type_laps_remain(laps_full_remain, lap_into):
    """Time type race remaining laps count from current on track position"""
    return max(laps_full_remain - lap_into, 0)


def total_fuel_needed(laps_remain, consumption, fuel_in_tank):
    """Total additional fuel needed"""
    return laps_remain * consumption - fuel_in_tank


def end_lap_consumption(consumption, consumption_delta, condition):
    """Estimate fuel consumption"""
    if condition:
        return consumption + consumption_delta
    return consumption


def end_stint_fuel(fuel_in_tank, consumption_into_lap, consumption):
    """Estimate end-stint remaining fuel before pitting"""
    if consumption:
        # Total fuel at start of current lap
        fuel_at_lap_start = fuel_in_tank + consumption_into_lap
        # Fraction of lap counts * estimate fuel consumption
        return fuel_at_lap_start / consumption % 1 * consumption
    return 0


def end_stint_laps(fuel_in_tank, consumption):
    """Estimate laps current fuel can last to end of stint"""
    if consumption:
        # Laps = remaining fuel / estimate fuel consumption
        return fuel_in_tank / consumption
    return 0


def end_stint_minutes(laps_total, laptime_last):
    """Estimate minutes current fuel can last to end of stint"""
    return laps_total * laptime_last / 60


def pit_in_countdown_laps(laps_remain, lap_into):
    """Estimate countdown laps till last chance to pit-in"""
    return laps_remain - (laps_remain + lap_into) % 1


def end_lap_empty_capacity(capacity_total, fuel_in_tank, consumption):
    """Estimate empty capacity at end of current lap"""
    return capacity_total - fuel_in_tank + consumption


def end_stint_pit_counts(fuel_needed, capacity_total):
    """Estimate end-stint pit stop counts"""
    if capacity_total:
        # Pit counts = required fuel / empty capacity
        return fuel_needed / capacity_total
    return 0


def end_lap_pit_counts(fuel_needed, capacity_empty, capacity_total):
    """Estimate end-lap pit stop counts"""
    # Amount fuel can be added without exceeding capacity
    fuel_addable = min(fuel_needed, capacity_empty)
    # Pit count of current stint, 1 if exceed empty capacity or no empty space
    pit_counts_before = fuel_addable / capacity_empty if capacity_empty else 1
    # Pit counts after current stint
    pit_counts_after = (fuel_needed - fuel_addable) / capacity_total
    # Total pit counts add together
    return pit_counts_before + pit_counts_after


def one_less_pit_stop_consumption(pit_counts_late, capacity_total, fuel_in_tank, laps_remain):
    """Estimate fuel consumption for one less pit stop"""
    if laps_remain:
        pit_counts = math.ceil(pit_counts_late) - 1
        # Consumption = total fuel / laps
        return (pit_counts * capacity_total + fuel_in_tank) / laps_remain
    return 0


def fuel_to_energy_ratio(fuel, energy):
    """Fuel to energy ratio"""
    if energy:
        return fuel / energy
    return 0


# Tyre
def tyre_wear_difference(wear_curr: float, wear_prev: float, wear_total: float):
    """Tyre wear difference and accumulated total wear"""
    if wear_prev < wear_curr:
        wear_prev = wear_curr
    elif wear_prev > wear_curr:
        wear_total += wear_prev - wear_curr
        wear_prev = wear_curr
    return wear_prev, wear_total


def tyre_lifespan_in_laps(
    wear_curr: float, wear_last_lap: float, wear_curr_lap: float):
    """Tyre lifespan in laps = remaining / last lap wear"""
    if wear_curr_lap > wear_last_lap > 0:
        est_laps = wear_curr / wear_curr_lap
    elif wear_last_lap > 0:
        est_laps = wear_curr / wear_last_lap
    else:
        est_laps = 999
    return min(est_laps, 999)


def tyre_lifespan_in_mins(
    wear_curr: float, wear_last_lap: float, wear_curr_lap: float, laptime: float):
    """Tyre lifespan in minutes = remaining / last lap wear * laptime / 60"""
    if laptime <= 0:
        return 999
    if wear_curr_lap > wear_last_lap > 0:
        est_mins = wear_curr / wear_curr_lap * laptime / 60
    elif wear_last_lap > 0:
        est_mins = wear_curr / wear_last_lap * laptime / 60
    else:
        est_mins = 999
    return min(est_mins, 999)


# Misc
def image_size_adaption(org_width, org_height, target_width, target_height):
    """Whether adapt image size to width or height

    Returns:
        True: adapt to height
        False: adapt to width
    """
    return org_width * target_height / max(org_height, 1) > target_width
