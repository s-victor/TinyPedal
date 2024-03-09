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


def vel2speed(vel_x, vel_y, vel_z):
    """Convert velocity to Speed"""
    # (vel_x ** 2 + vel_y ** 2 + vel_z ** 2) ** 0.5
    return math.hypot(vel_x, vel_y, vel_z)


def distance(value1, value2):
    """Coordinates distance"""
    return math.dist(value1, value2)


def meter2millmeter(meter):
    """Convert meter to millimeter"""
    return meter * 1000


def mps2kph(meter):
    """meter per sec to kilometers per hour"""
    return meter * 3.6


def mps2mph(meter):
    """Meter per sec to miles per hour"""
    return meter * 2.23693629


def celsius2fahrenheit(temp):
    """Celsius to Fahrenheit"""
    return temp * 1.8 + 32


def kelvin2celsius(kelvin):
    """Kelvin to Celsius"""
    return kelvin - 273.15 if kelvin else 0


def liter2gallon(fuel):
    """Liter to Gallon"""
    return fuel * 0.2641729


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
    """Raw rake"""
    return (height_rr + height_rl - height_fr - height_fl) * 0.5


def rake2angle(v_rake, wheelbase):
    """Rake angle based on wheelbase value set in JSON"""
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
        return abs((v_speed - abs(w_rot * w_radius)) / v_speed)
    return 0


def slip_angle(v_lat, v_lgt):
    """Slip angle (radians)"""
    if v_lgt:
        return math.atan(v_lat / v_lgt)
    return 0


def kpa2psi(pressure):
    """Kilopascal to psi"""
    return pressure * 0.14503774


def kpa2bar(pressure):
    """Kilopascal to bar"""
    return pressure * 0.01


def gforce(value, g_accel):
    """G force"""
    return value / g_accel


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


def linear_interp(x, x1, y1, x2, y2):
    """Linear interpolation"""
    x_diff = x2 - x1
    if x_diff:
        return y1 + (x - x1) * (y2 - y1) / x_diff
    return y1


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


def zoom_map(map_data, map_scale, margin=0):
    """Zoom map data to specific scale, then add margin"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*map_data))
    # Offset X, Y
    map_offset = min(x_range) * map_scale - margin, min(y_range) * map_scale - margin
    # Scale map coordinates
    x_range_scaled = [x_pos * map_scale - map_offset[0] for x_pos in x_range]
    y_range_scaled = [y_pos * map_scale - map_offset[1] for y_pos in y_range]
    # Map width, height
    map_size = max(x_range_scaled) + margin, max(y_range_scaled) + margin
    return tuple(zip(x_range_scaled, y_range_scaled)), map_size, map_offset


def scale_map(map_data, area_size, margin=0):
    """Scale map data"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*map_data))
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


def map_view_box(map_data, margin=0):
    """Map bounding box"""
    # Separate X & Y coordinates
    x_range, y_range = tuple(zip(*map_data))
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
