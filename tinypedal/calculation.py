#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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


def vel2speed(vel_x, vel_y, vel_z):
    """Convert velocity to Speed"""
    return (vel_x ** 2 + vel_y ** 2 + vel_z ** 2) ** 0.5


def meter2millmeter(meter):
    """Convert meter to millimeter"""
    return meter * 1000


def mps2kph(meter):
    """meter per sec to kilometers per hour"""
    return meter * 3.6


def mps2mph(meter):
    """meter per sec to miles per hour"""
    return meter * 2.23693629


def celsius2fahrenheit(temp):
    """Celsius to Fahrenheit"""
    return temp * 1.8 + 32


def kelvin2celsius(kelvin):
    """Convert Kelvin to Celsius"""
    return max(kelvin - 273.15, 0)


def liter2gallon(fuel):
    """Liter to Gallon"""
    return fuel * 0.2641729


def average_value(average, value, num_samples):
    """Average value"""
    return (average * num_samples + value) / (num_samples + 1)


def rad2deg(radian):
    """Convert radians to degrees"""
    return radian * 57.2957795


def max_vs_avg_rotation(w_rot1, w_rot2):
    """Left and right wheel rotation difference of same axle"""
    max_rot = min(w_rot1, w_rot2)  # negative value is forward
    avg_rot = (w_rot1 + w_rot2) / 2
    return abs(max_rot - avg_rot)  # difference


def rake(height_fl, height_fr, height_rl, height_rr):
    """Raw rake"""
    return (height_rr + height_rl - height_fr - height_fl) * 0.5


def rake2angle(v_rake, wheelbase):
    """Rake angle based on wheelbase value set in JSON"""
    if wheelbase:
        return math.atan(v_rake / wheelbase * 57.2957795)
    return 0


def slip_ratio(w_rot, w_radius, v_speed):
    """Slip ratio (percentage), speed unit in m/s"""
    if v_speed > 0.1:  # set minimum speed to avoid flickering while stationary
        return abs((v_speed - abs(w_rot * w_radius)) / v_speed)
    return 0


def slip_angle(v_lat, v_lgt):
    """Slip angle (radians)"""
    if v_lgt:
        return math.atan(v_lat / v_lgt)
    return 0


def kpa2psi(pressure):
    """Convert kilopascal to psi"""
    return pressure * 0.14503774


def kpa2bar(pressure):
    """Convert kilopascal to bar"""
    return pressure * 0.01


def gforce(value, g_accel):
    """G force"""
    return value / g_accel


def force_ratio(value1, value2):
    """Force ratio from Newtons"""
    return abs(value1 / (value2 + 0.01) * 100)


def oriyaw2rad(value1, value2):
    """Convert orientation yaw to radians"""
    return math.atan2(value1, value2)


def rotate_pos(ori_rad, value1, value2):
    """Rotate x y coordinates"""
    new_pos_x = (math.cos(ori_rad) * value1) - (math.sin(ori_rad) * value2)
    new_pos_z = (math.cos(ori_rad) * value2) + (math.sin(ori_rad) * value1)
    return new_pos_x, new_pos_z


def distance_xy(value1, value2=None):
    """Distance in 2d space"""
    if value2:
        return ((value1[0] - value2[0]) ** 2
                + (value1[1] - value2[1]) ** 2) ** 0.5
    return (value1[0] ** 2 + value1[1] ** 2) ** 0.5


def distance_xyz(value1, value2):
    """Distance in 3d space"""
    return ((value1[0] - value2[0]) ** 2
             + (value1[1] - value2[1]) ** 2
             + (value1[2] - value2[2]) ** 2) ** 0.5


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


def relative_time_gap(distance, plr_speed, opt_speed):
    """Relative time gap between opponent & player"""
    speed = max(plr_speed, opt_speed)
    if speed > 1:
        return abs(distance / speed)
    return 0


def sec2sessiontime(seconds):
    """Session time (hour/min/sec/ms)"""
    hours = seconds // 3600
    mins = divmod(seconds // 60, 60)[1]
    secs = divmod(seconds, 60)[1]
    return f"{hours:01.0f}:{mins:02.0f}:{secs:02.0f}"


def sec2laptime(seconds):
    """Lap time (min/sec/ms)"""
    if seconds > 60:
        return f"{seconds // 60:.0f}:{divmod(seconds, 60)[1]:06.03f}"
    return f"{divmod(seconds, 60)[1]:.03f}"


def sec2laptime_full(seconds):
    """Lap time (min/sec/ms) full"""
    return f"{seconds // 60:.0f}:{divmod(seconds, 60)[1]:06.03f}"


def sec2stinttime(seconds):
    """Lap time (min/sec/ms)"""
    return f"{seconds // 60:02.0f}:{divmod(seconds, 60)[1]:02.0f}"


def linear_interp(meter, meter1, secs1, meter2, secs2):
    """Linear interpolation"""
    return secs1 + (meter - meter1) * (secs2 - secs1) / (meter2 - meter1 + 0.0000001)


def nearest_dist_index(position, listname):
    """Find nearest distance value index from list"""
    index_higher = 0
    nearest_dist = 99999999
    for index, column in enumerate(listname):
        if position < column[0] and nearest_dist > column[0]:
            nearest_dist = column[0]
            index_higher = index
    index_lower = max(index_higher - 1, 0)
    #for index in range(index_higher - 1, -1, -1):
    #    if position > listname[index][0]:
    #        index_lower = index
    #        break
    return index_lower, index_higher


def color_heatmap(heatmap, temperature):
    """Set color from heatmap"""
    last_color = heatmap[0][1]
    for temp in heatmap:
        if temperature < float(temp[0]):
            return last_color
        last_color = temp[1]
    return heatmap[-1][1]


def del_decimal_point(value):
    """Delete decimal point"""
    if value and value[-1] == ".":
        return value[:-1]
    return value


def lap_difference(opt_laps, plr_laps, opt_per_dist, plr_per_dist, session=10):
    """Calculate lap difference between 2 players"""
    lap_diff = opt_laps + opt_per_dist - plr_laps - plr_per_dist
    # Only check during race session
    if session > 9 and abs(lap_diff) > 1:
        return lap_diff
    return 0
