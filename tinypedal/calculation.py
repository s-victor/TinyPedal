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
Calculation function
"""

import math


def in2zero(value):
    """Convert invalid value to zero"""
    if isinstance(value, (float, int)):
        if math.isnan(value) or math.isinf(value):  # bypass nan & inf
            return 0
        return value
    return 0


def vel2speed(vel_x, vel_y, vel_z):
    """Convert velocity to Speed"""
    return (vel_x ** 2 + vel_y ** 2 + vel_z ** 2) ** 0.5


def conv_speed(speed, speed_unit):
    """3 different speed unit conversion"""
    if speed_unit == "0":
        multiplier = 3.6  # kph
    elif speed_unit == "1":
        multiplier = 2.23693629  # mph
    else:
        multiplier = 1  # meter per sec
    return speed * multiplier


def celsius2fahrenheit(temp):
    """Celsius to Fahrenheit"""
    return temp * 1.8 + 32


def liter2gallon(fuel):
    """Liter to Gallon"""
    return fuel * 0.2641729


def average_value(average, value, num_samples):
    """Calculate average value"""
    return (average * num_samples + value) / (num_samples + 1)


def gear(gear_index):
    """Convert gear index to text string"""
    if gear_index > 0:
        text = str(gear_index)
    elif gear_index == 0:
        text = "N"
    else:
        text = "R"
    return text


def rad2deg(radian):
    """Convert radians to degrees"""
    return radian * 57.2957795


def max_vs_avg_rotation(w_rot1, w_rot2):
    """Calculate left and right wheel rotation difference of same axle"""
    max_rot = min(w_rot1, w_rot2)  # negative value is forward
    avg_rot = (w_rot1 + w_rot2) / 2
    return abs(max_rot - avg_rot)  # difference


def meter2millmeter(meter):
    """Convert meter to millimeter"""
    return meter * 1000


def rake(height_fl, height_fr, height_rl, height_rr):
    """Calculate rake"""
    return (height_rr + height_rl - height_fr - height_fl) * 0.5


def rake2angle(v_rake, wheelbase):
    """Calculate rake angle based on wheelbase value set in JSON"""
    return math.atan(float(v_rake) / (wheelbase + 0.001) * 57.2957795)


def slip_ratio(w_rot, w_radius, v_speed):
    """Calculate slip ratio (percentage), speed unit in m/s"""
    if v_speed > 0.1:  # set minimum speed to avoid flickering while stationary
        return abs((v_speed - abs(w_rot * w_radius)) / v_speed)
    return 0


def kpa2psi(pressure):
    """Convert kilopascal to psi"""
    return pressure * 0.14503774


def kpa2bar(pressure):
    """Convert kilopascal to bar"""
    return pressure * 0.01


def gforce(value):
    """Calculate G force"""
    force = value / 9.8
    return force


def force_ratio(value1, value2):
    """Calculate force ratio from Newtons"""
    return abs(value1 / (value2 + 0.01) * 100)


def oriyaw2rad(value1, value2):
    """Convert orientation yaw to radians"""
    return math.atan2(value1, value2)


def rotate_pos(ori_rad, value1, value2):
    """Rotate x y coordinates"""
    new_pos_x = (math.cos(ori_rad) * value1) - (math.sin(ori_rad) * value2)
    new_pos_z = (math.cos(ori_rad) * value2) + (math.sin(ori_rad) * value1)
    return new_pos_x, new_pos_z


def pos2distance(value1, value2):
    """Calculate distance from global position difference"""
    return ((value1[0] - value2[0]) ** 2
             + (value1[1] - value2[1]) ** 2
             + (value1[2] - value2[2]) **2 ) ** 0.5


def sec2sessiontime(seconds):
    """Calculate session time (hour/min/sec/ms)"""
    hours = seconds // 3600
    mins = divmod(seconds // 60, 60)[1]
    secs = divmod(seconds, 60)[1]
    return f"{hours:02.0f}:{mins:02.0f}:{secs:04.01f}"


def sec2laptime(seconds):
    """Calculate lap time (min/sec/ms)"""
    if seconds > 60:
        return f"{seconds // 60:.0f}:{divmod(seconds, 60)[1]:06.03f}"
    return f"{divmod(seconds, 60)[1]:.03f}"


def sec2stinttime(seconds):
    """Calculate lap time (min/sec/ms)"""
    return f"{seconds // 60:02.0f}:{divmod(seconds, 60)[1]:02.0f}"


def linear_interp(meter, meter1, secs1, meter2, secs2):
    """Linear interpolation"""
    return secs1 + (meter - meter1) * (secs2 - secs1) / (meter2 - meter1 + 0.0000001)


def nearest_dist_index(position, listname):
    """Use current position to get nearest distance index from deltabest lap data"""
    index_lower, index_higher = 0, 0
    for index, line in enumerate(listname):
        if position < line[0]:
            index_higher = index
            break
    for index in range(index_higher - 1, -1, -1):
        if position > listname[index][0]:
            index_lower = index
            break
    return index_lower, index_higher


# Unused
def kelvin2celsius(kelvin):
    """Convert Kelvin to Celsius"""
    return max(kelvin - 273.15, 0)
