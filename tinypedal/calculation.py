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


# Unit conversion
def meter2millmeter(meter):
    """Convert meter to millimeter"""
    return meter * 1000


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
    return liter * 0.2641729


def kelvin2celsius(kelvin):
    """Kelvin to Celsius"""
    return max(kelvin - 273.15, -99)


def kpa2psi(kilopascal):
    """Kilopascal to psi"""
    return kilopascal * 0.14503774


def kpa2bar(kilopascal):
    """Kilopascal to bar"""
    return kilopascal * 0.01


# Common
def vel2speed(vel_x, vel_y, vel_z=0):
    """Convert velocity to Speed"""
    # (vel_x ** 2 + vel_y ** 2 + vel_z ** 2) ** 0.5
    return math.hypot(vel_x, vel_y, vel_z)


def distance(value1, value2):
    """Coordinates distance"""
    return math.dist(value1, value2)


def sym_range(value, rng):
    """Symmetric range"""
    return min(max(value, -rng), rng)


def zero_one_range(value):
    """Limit value in range 0 to 1 """
    return min(max(value, 0), 1)


def mean(data):
    """Average value"""
    # sum(data) / len(data)
    return statistics.fmean(data)


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


def std_dev(data, avg):
    """Sample standard deviation"""
    # math.sqrt(sum(map(lambda x:(x-avg)**2, data)) / (len(data) - k))
    return statistics.stdev(data, avg)


def rad2deg(radian):
    """Radians to degrees"""
    return math.degrees(radian)


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


def oriyaw2rad(value1, value2):
    """Orientation yaw to radians"""
    return math.atan2(value1, value2)


def rotate_pos(ori_rad, value1, value2):
    """Rotate x y coordinates"""
    sin_rad = math.sin(ori_rad)
    cos_rad = math.cos(ori_rad)
    return (cos_rad * value1 - sin_rad * value2,
            cos_rad * value2 + sin_rad * value1)


def percentage_distance(dist, length, max_range=1, min_range=0):
    """Current distance in percentage relative to length"""
    if length:
        return min(max(dist / length, min_range), max_range)
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
def sec2sessiontime(seconds):
    """Session time (hour/min/sec/ms)"""
    return f"{seconds // 3600:01.0f}:{seconds // 60 % 60:02.0f}:{min(seconds % 60, 59):02.0f}"


def sec2laptime(seconds):
    """Lap time (min/sec/ms)"""
    if seconds > 60:
        return f"{seconds // 60:.0f}:{seconds % 60:06.03f}"
    return f"{seconds % 60:.03f}"


def sec2laptime_full(seconds):
    """Lap time (min/sec/ms) full"""
    return f"{seconds // 60:.0f}:{seconds % 60:06.03f}"


def sec2stinttime(seconds):
    """Lap time (min/sec/ms)"""
    return f"{seconds // 60:02.0f}:{min(seconds % 60, 59):02.0f}"


def delta_telemetry(position, live_data, delta_list, condition=True, offset=0):
    """Calculate delta telemetry data"""
    index_higher = binary_search_hi(
        delta_list, position, 0, len(delta_list) - 1, 0)
    # At least 2 data pieces & additional condition
    if index_higher > 0 and condition:
        index_lower = index_higher - 1
        return (
            live_data + offset - linear_interp(
                position,
                delta_list[index_lower][0],
                delta_list[index_lower][1],
                delta_list[index_higher][0],
                delta_list[index_higher][1],
            )
        )
    return 0


# Search
def search_column_key(key, column=None):
    """Search column key"""
    if column is None:
        return key
    return key[column]


def linear_search_hi(data, target, column=None):
    """linear search nearest value higher index from unordered list"""
    #key = lambda x:x[column] if column >= 0 else x
    end = len(data) - 1
    nearest = float("inf")
    for index, data_row in enumerate(data):
        if target <= search_column_key(data_row, column) < nearest:
            nearest = search_column_key(data_row, column)
            end = index
    return end


def binary_search_hi(data, target, start, end, column=None):
    """Binary search nearest value higher index from ordered list"""
    #key = lambda x:x[column] if column >= 0 else x
    while start < end:
        center = (start + end) // 2
        if target == search_column_key(data[center], column):
            return center
        if target > search_column_key(data[center], column):
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
    return tuple(zip(x_range_scaled, y_range_scaled)), map_range, map_scale, map_offset


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
    pos_x1, pos_y1 = rotate_pos(
        yaw_rad + radians,
        length,  # x pos
        0  # y pos
    )
    pos_x2, pos_y2 = rotate_pos(
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
def lap_type_full_left(laps_max, lap_number):
    """Lap type race full remaining laps"""
    return laps_max - lap_number


def lap_type_laps_left(full_laps_left, lap_into):
    """Lap type race remaining laps"""
    return full_laps_left - lap_into


def time_type_full_left(laptime_curr, laptime_last, time_left):
    """Time type race full remaining laps"""
    # Relative time into lap based on last laptime
    rel_lap_into = math.modf(laptime_curr / laptime_last)[0] * laptime_last
    # Full laps left value counts from start line of current lap
    return math.ceil((time_left + rel_lap_into) / laptime_last)


def time_type_laps_left(full_laps_left, lap_into, laps_left, delay=False):
    """Time type race full remaining laps"""
    if delay:  # delay check to avoid lap number desync
        return laps_left
    return max(full_laps_left - lap_into, 0)


def total_fuel_to_add(laps_left, used_est, amount_curr):
    """Total additional fuel needed"""
    return laps_left * used_est - amount_curr


def end_lap_consumption(used_last, delta_fuel, condition):
    """Estimate fuel consumption"""
    if condition:
        return used_last + delta_fuel
    return used_last


def end_stint_fuel(amount_curr, used_curr, used_est):
    """Estimate end-stint remaining fuel before pitting"""
    if used_est:
        # Total fuel at start of current lap
        total_fuel = amount_curr + used_curr
        # Fraction of lap counts * estimate fuel consumption
        return math.modf(total_fuel / used_est)[0] * used_est
    return 0


def end_stint_laps(amount_curr, used_est):
    """Estimate laps current fuel can last"""
    if used_est:
        # Laps = remaining fuel / estimate fuel consumption
        return amount_curr / used_est
    return 0


def end_lap_empty_capacity(capacity, fuel_remain, fuel_consumption):
    """Estimate empty capacity at end of current lap"""
    return capacity - fuel_remain + fuel_consumption


def end_stint_pit_counts(amount_need, capacity):
    """Estimate end-stint pit stop counts"""
    # Pit counts = required fuel / empty capacity
    return amount_need / capacity


def end_lap_pit_counts(amount_need, est_empty, capacity):
    """Estimate end-lap pit stop counts"""
    # Amount fuel can be added without exceeding capacity
    max_add_curr = min(amount_need, est_empty)
    # Pit count of current stint, 1 if exceed empty capacity or no empty space
    est_pits_curr = max_add_curr / est_empty if est_empty else 1
    # Pit counts after current stint
    est_pits_end = (amount_need - max_add_curr) / capacity
    # Total pit counts add together
    return est_pits_curr + est_pits_end


def less_pit_stop_consumption(est_pits_late, capacity, amount_curr, laps_left):
    """Estimate fuel consumption for one less pit stop"""
    if laps_left:
        pit_counts = math.ceil(est_pits_late) - 1
        # Consumption = total fuel / laps
        return (pit_counts * capacity + amount_curr) / laps_left
    return 0


def estimate_starting_fuel(total_laps, used_est, laptime_avg, race_time):
    """Estimate race starting fuel"""
    if total_laps > 0:
        return total_fuel_to_add(total_laps, used_est, 0)
    total_laps = time_type_full_left(0, laptime_avg, race_time)
    return total_fuel_to_add(total_laps, used_est, 0)


# Misc
def image_size_adaption(org_width, org_height, target_width, target_height):
    """Whether adapt image size to width or height

    Returns:
        True: adapt to height
        False: adapt to width
    """
    return org_width * target_height / max(org_height, 1) > target_width
