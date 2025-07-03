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
Wheels module
"""

from collections import deque

from .. import calculation as calc
from ..api_control import api
from ..const_common import POS_XY_ZERO
from ..module_info import WheelsInfo, minfo
from ..userfile.heatmap import brake_failure_thickness
from ..validator import generator_init
from ._base import DataModule


class Realtime(DataModule):
    """Wheels data"""

    __slots__ = ()

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        _event_wait = self._event.wait
        reset = False
        update_interval = self.active_interval

        output = minfo.wheels

        vehicle_name = ""
        radius_front_ema = 0.0
        radius_rear_ema = 0.0

        max_rot_bias_f = max(self.mcfg["maximum_rotation_difference_front"], 0.00001)
        max_rot_bias_r = max(self.mcfg["maximum_rotation_difference_rear"], 0.00001)
        min_rot_axle = max(self.mcfg["minimum_axle_rotation"], 0)
        min_coords = min(max(self.mcfg["cornering_radius_sampling_interval"], 5), 100)
        list_coords = deque([POS_XY_ZERO] * min_coords * 2, min_coords * 2)

        while not _event_wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    if vehicle_name != api.read.vehicle.vehicle_name():
                        vehicle_name = api.read.vehicle.vehicle_name()
                        radius_front_ema = 0.0
                        radius_rear_ema = 0.0

                    last_accel_max = 0.0
                    locking_f = 1
                    locking_r = 1
                    cornering_radius = 0
                    gps_last = POS_XY_ZERO

                    gen_brake_wear = calc_brake_wear(output)
                    gen_tyre_wear = calc_tyre_wear(output)

                # Read telemetry
                speed = api.read.vehicle.speed()
                wheel_rot = api.read.wheel.rotation()
                gps_curr = (api.read.vehicle.position_longitudinal(),
                            api.read.vehicle.position_lateral())
                accel_max = max(
                    abs(api.read.vehicle.accel_lateral()),
                    abs(api.read.vehicle.accel_longitudinal()),
                )

                # Get wheel axle rotation and difference
                rot_axle_f = calc.wheel_axle_rotation(wheel_rot[0], wheel_rot[1])
                rot_axle_r = calc.wheel_axle_rotation(wheel_rot[2], wheel_rot[3])
                rot_bias_f = calc.wheel_rotation_bias(rot_axle_f, wheel_rot[0], wheel_rot[1])
                rot_bias_r = calc.wheel_rotation_bias(rot_axle_r, wheel_rot[2], wheel_rot[3])

                if rot_axle_f < -min_rot_axle:
                    locking_f = calc.differential_locking_percent(rot_axle_f, wheel_rot[0])
                if rot_axle_r < -min_rot_axle:
                    locking_r = calc.differential_locking_percent(rot_axle_r, wheel_rot[2])

                # Record wheel radius value within max rotation difference
                if last_accel_max != accel_max:  # check if game paused
                    last_accel_max = accel_max
                    d_factor = 2 / max(40 * accel_max, 20)  # scale ema factor with max accel
                    # Front average wheel radius
                    if rot_axle_f < -min_rot_axle and 0 < rot_bias_f < max_rot_bias_f:
                        radius_front_ema = calc.exp_mov_avg(d_factor, radius_front_ema, calc.rot2radius(speed, rot_axle_f))
                    # Rear average wheel radius
                    if rot_axle_r < -min_rot_axle and 0 < rot_bias_r < max_rot_bias_r:
                        radius_rear_ema = calc.exp_mov_avg(d_factor, radius_rear_ema, calc.rot2radius(speed, rot_axle_r))

                # Calculate cornering radius based on tri-coordinates position
                if gps_last != gps_curr:
                    gps_last = gps_curr
                    list_coords.append(gps_curr)
                    arc_center_pos = calc.tri_coords_circle_center(
                        *list_coords[0], *list_coords[min_coords], *list_coords[-1])
                    cornering_radius = calc.distance(list_coords[0], arc_center_pos)

                # Calculate wear
                gen_brake_wear.send(minfo.restapi.brakeWear)
                gen_tyre_wear.send(api.read.tyre.wear())

                # Output wheels data
                output.lockingPercentFront = locking_f
                output.lockingPercentRear = locking_r
                output.corneringRadius = cornering_radius
                output.slipRatio[0] = calc.slip_ratio(wheel_rot[0], radius_front_ema, speed)
                output.slipRatio[1] = calc.slip_ratio(wheel_rot[1], radius_front_ema, speed)
                output.slipRatio[2] = calc.slip_ratio(wheel_rot[2], radius_rear_ema, speed)
                output.slipRatio[3] = calc.slip_ratio(wheel_rot[3], radius_rear_ema, speed)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


@generator_init
def calc_tyre_wear(output: WheelsInfo):
    """Calculate tyre wear & delta wear"""
    last_lap_stime = 0.0  # last lap start time
    tread_last = [0.0] * 4  # last moment remaining tread
    tread_wear_curr = [0.0] * 4  # current lap tread wear
    tread_wear_last = [0.0] * 4  # last lap tread wear
    delta_zero = (0.0,) * 5

    is_pit_lap = 0  # whether pit in or pit out lap
    is_valid_delta = False
    delta_recording = False
    delta_array_raw = [delta_zero]  # distance, battery net change
    delta_array_last = (delta_zero,)
    pos_last = 0.0  # last checked vehicle position
    min_delta_distance = 5

    while True:
        tread_curr_set = yield None
        lap_stime = api.read.timing.start()
        laptime_curr = api.read.timing.elapsed() - lap_stime
        pos_curr = api.read.lap.distance()
        is_pit_lap |= api.read.vehicle.in_pits()
        delay_update = laptime_curr > 0.3

        if lap_stime != last_lap_stime:
            tread_wear_last[:] = tread_wear_curr
            tread_wear_curr[0] = tread_wear_curr[1] = tread_wear_curr[2] = tread_wear_curr[3] = 0.0
            last_lap_stime = lap_stime  # reset time stamp counter
            # Update delta array
            if len(delta_array_raw) > 1 and not is_pit_lap:
                delta_array_last = tuple(delta_array_raw)
            delta_array_raw.clear()  # reset
            delta_array_raw.append(delta_zero)
            pos_last = pos_curr
            delta_recording = laptime_curr < 1
            is_valid_delta = len(delta_array_last) > 1
            is_pit_lap = 0

        # Distance desync check at start of new lap, reset if higher than normal distance
        if 0 < laptime_curr < 1 and pos_curr > 300:
            pos_last = pos_curr = 0
        elif pos_last > pos_curr:
            pos_last = pos_curr

        # Update if position value is different & positive
        if delta_recording and pos_curr - pos_last >= min_delta_distance:
            delta_array_raw.append((pos_curr, *tread_wear_curr))
            pos_last = pos_curr

        # Calculate wear difference
        for idx, tread_curr in enumerate(tread_curr_set):
            tread_curr *= 100

            # Update wear differences & accumulated wear
            wear_diff = tread_last[idx] - tread_curr
            tread_last[idx] = tread_curr
            if wear_diff > 0:
                tread_wear_curr[idx] += wear_diff

            # Delta wear
            if is_valid_delta:
                output.deltaTreadWear[idx] = calc.delta_telemetry(
                    delta_array_last,
                    pos_curr,
                    tread_wear_curr[idx],
                    delay_update,
                    0,
                    idx + 1,
                )

            # Output
            output.currentTreadDepth[idx] = tread_curr
            output.currentTreadWear[idx] = tread_wear_curr[idx]
            output.lastLapTreadWear[idx] = tread_wear_last[idx]


@generator_init
def calc_brake_wear(output: WheelsInfo):
    """Calculate brake wear"""
    last_lap_stime = 0.0  # last lap start time
    brake_last = [0.0] * 4  # last moment remaining brake
    brake_wear_curr = [0.0] * 4  # current lap brake wear
    brake_wear_last = [0.0] * 4  # last lap brake wear
    brake_max_thickness = [0.0] * 4  # brake max thickness at start of stint
    failure_thickness = brake_failure_thickness(api.read.vehicle.class_name())
    while True:
        brake_curr_set = yield None
        lap_stime = api.read.timing.start()

        if lap_stime != last_lap_stime:
            brake_wear_last[:] = brake_wear_curr
            brake_wear_curr[0] = brake_wear_curr[1] = brake_wear_curr[2] = brake_wear_curr[3] = 0.0
            last_lap_stime = lap_stime  # reset time stamp counter

        for idx, brake_curr in enumerate(brake_curr_set):
            # Calculate effective thickness
            brake_curr *= 1000  # meter to millimeter
            brake_curr -= failure_thickness[idx]

            # Calibrate max thickness
            if brake_max_thickness[idx] < brake_curr:
                brake_max_thickness[idx] = brake_curr
                output.maxBrakeThickness[idx] = brake_curr

            if not brake_max_thickness[idx]:  # bypass invalid value
                brake_curr = 0.0
            else:  # convert to percent
                brake_curr *= 100 / brake_max_thickness[idx]

            # Update wear differences & accumulated wear
            wear_diff = brake_last[idx] - brake_curr
            brake_last[idx] = brake_curr
            if wear_diff > 0:
                brake_wear_curr[idx] += wear_diff

            # Output
            output.currentBrakeThickness[idx] = brake_curr
            output.currentBrakeWear[idx] = brake_wear_curr[idx]
            output.lastLapBrakeWear[idx] = brake_wear_last[idx]
