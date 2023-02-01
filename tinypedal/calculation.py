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
            value = 0
    else:
        value = 0
    return value


def pedal_pos(pedal, offset, scale):
    """Convert input range to 100, and multiply scale"""
    position = offset - abs(pedal * 100) * scale
    return position


def steering_pos(steering, length):
    """Multiply scale, add offset"""
    position = steering * length + length
    return position


def scale_mark_gap(degree, rot_range, scale):
    """mark gap(degree) divide half of full steering range (degree) and multiply scale"""
    if rot_range != 0:
        gap = degree / (rot_range / 2) * scale
    else:
        gap = 0
    return gap


def vel2speed(vel_x, vel_y, vel_z):
    """Convert velocity to Speed"""
    speed = (vel_x ** 2 + vel_y ** 2 + vel_z ** 2) ** 0.5
    return speed


def conv_speed(speed, speed_unit):
    """3 different speed unit conversion"""
    if speed_unit == "0":
        multiplier = 3.6  # kph
    elif speed_unit == "1":
        multiplier = 2.23693629  # mph
    else:
        multiplier = 1  # meter per sec
    speed = speed * multiplier
    return speed


def conv_temperature(temp, temp_unit):
    """2 different temperature unit conversion, default is Celsius"""
    if temp_unit == "1":
        temp = temp * 1.8 + 32  # Celsius to Fahrenheit
    return temp


def conv_fuel(fuel, fuel_unit):
    """2 different fuel unit conversion, default is Liter"""
    if fuel_unit == "1":
        fuel = fuel * 0.2641729  # Liter to Gallon
    return fuel


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
    degree = radian * 57.2957795
    return degree


def meter2millmeter(meter):
    """Convert meter to millimeter"""
    millimeter = meter * 1000
    return millimeter


def rake(height_fl, height_fr, height_rl, height_rr):
    """Calculate rake"""
    diff = (height_rr + height_rl - height_fr - height_fl) * 0.5
    return diff


def rake2angle(v_rake, wheelbase):
    """Calculate rake angle based on wheelbase value set in JSON"""
    degree = math.atan(float(v_rake) / (wheelbase + 0.001) * 57.2957795)
    return degree


def slip_ratio(w_rot, w_radius, v_speed):
    """Calculate slip ratio, speed unit in m/s"""
    if v_speed > 0.1:
        percentage = abs((v_speed - abs(w_rot * w_radius)) / v_speed)
    else:
        percentage = 0
    return percentage


def max_vs_avg_rotation(w_rot1, w_rot2):
    """Calculate left and right wheel rotation difference of same axle"""
    max_rot = min(w_rot1, w_rot2)  # negative value is forward
    avg_rot = (w_rot1 + w_rot2) / 2
    difference = abs(max_rot - avg_rot)
    return difference


def kpa2psi(tyre_pres, pres_unit):
    """Convert kilopascal to psi"""
    if pres_unit == "0":
        pressure = f"{tyre_pres:03.0f}"  # kPa
    elif pres_unit == "1":
        pressure = f"{tyre_pres * 0.14503774:03.1f}"  # psi
    else:
        pressure = f"{tyre_pres * 0.01:03.2f}"  # bar
    return pressure


def gforce_lgt(g_force):
    """Add direction sign for longitudinal g-force"""
    if g_force > 0.1:
        force = "▼"
    elif g_force < -0.1:
        force = "▲"
    else:
        force = "●"
    return force


def gforce_lat(g_force):
    """Add direction sign for lateral g-force"""
    if g_force > 0.1:
        force = "◀"
    elif g_force < -0.1:
        force = "▶"
    else:
        force = "●"
    return force


def force_ratio(value1, value2):
    """Calculate force ratio from Newtons"""
    ratio = abs(value1 / (value1 + value2 + 0.01) * 100)
    return ratio


def oriyaw2rad(value1, value2):
    """Convert orientation yaw to radians"""
    radian = math.atan2(value1, value2)
    return radian


def rotate_pos(ori_rad, value1, value2):
    """Rotate x y coordinates"""
    new_pos_x = (math.cos(ori_rad) * value1) - (math.sin(ori_rad) * value2)
    new_pos_z = (math.cos(ori_rad) * value2) + (math.sin(ori_rad) * value1)
    return new_pos_x, new_pos_z


def pos2distance(value1, value2):
    """Calculate distance from global position difference"""
    meter = ((value1[0] - value2[0]) ** 2
              + (value1[1] - value2[1]) ** 2
              + (value1[2] - value2[2]) **2 ) ** 0.5
    return meter


def sec2sessiontime(seconds):
    """Calculate session time (hour/min/sec/ms)"""
    hours = seconds // 3600
    mins = divmod(seconds // 60, 60)[1]
    secs = divmod(seconds, 60)[1]
    sessiontime = f"{hours:02.0f}:{mins:02.0f}:{secs:04.01f}"
    return sessiontime


def sec2laptime(seconds):
    """Calculate lap time (min/sec/ms)"""
    if seconds > 60:
        laptime = f"{seconds // 60:.0f}:{divmod(seconds, 60)[1]:06.03f}"
    else:
        laptime = f"{divmod(seconds, 60)[1]:.03f}"
    return laptime


def sec2stinttime(seconds):
    """Calculate lap time (min/sec/ms)"""
    stinttime = f"{seconds // 60:02.0f}:{divmod(seconds, 60)[1]:02.0f}"
    return stinttime


def linear_interp(meter, meter1, secs1, meter2, secs2):
    """Linear interpolation"""
    secs = secs1 + (meter - meter1) * (secs2 - secs1) / (meter2 - meter1 + 0.0000001)
    return secs


def nearest_dist_index(position, listname):
    """Use current position to get nearest distance index from deltabest lap data"""
    index_lower, index_higher = 0, 0
    for index in range(0, len(listname)):
        if position < listname[index][0]:
            index_higher = index
            break
    for index in range(index_higher - 1, -1, -1):
        if position > listname[index][0]:
            index_lower = index
            break
    return index_lower, index_higher


# Unused
def _kelvin2celsius(kelvin):
    """Convert Kelvin to Celsius"""
    celsius = max(kelvin - 273.15, 0)
    return celsius
