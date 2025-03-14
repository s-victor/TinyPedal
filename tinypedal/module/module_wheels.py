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
Wheels module
"""

from collections import deque

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc


class Realtime(DataModule):
    """Wheels data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        output = minfo.wheels

        list_radius_f = deque([], 160)
        list_radius_r = deque([], 160)
        max_rot_bias_f = max(self.mcfg["maximum_rotation_difference_front"], 0.00001)
        max_rot_bias_r = max(self.mcfg["maximum_rotation_difference_rear"], 0.00001)
        min_rot_axle = max(self.mcfg["minimum_axle_rotation"], 0)
        min_coords = min(max(self.mcfg["cornering_radius_sampling_interval"], 5), 100)
        list_coords = deque([(0,0)] * min_coords * 2, min_coords * 2)

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    if output.vehicleName == api.read.vehicle.vehicle_name():
                        radius_front = output.radiusFront
                        radius_rear = output.radiusRear
                        min_samples_f = 160
                        min_samples_r = 160
                    else:
                        output.vehicleName = api.read.vehicle.vehicle_name()
                        list_radius_f.clear()
                        list_radius_r.clear()
                        radius_front = 0.0
                        radius_rear = 0.0
                        min_samples_f = 20
                        min_samples_r = 20

                    samples_slice_f = sample_slice_indices(min_samples_f)
                    samples_slice_r = sample_slice_indices(min_samples_r)
                    locking_f = 1
                    locking_r = 1
                    gps_last = 0
                    cornering_radius = 0

                # Read telemetry
                speed = api.read.vehicle.speed()
                wheel_rot = api.read.wheel.rotation()
                gps_curr = (api.read.vehicle.position_longitudinal(),
                            api.read.vehicle.position_lateral())

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
                if rot_axle_f < -min_rot_axle and 0 < rot_bias_f < max_rot_bias_f:
                    list_radius_f.append(calc.rot2radius(speed, rot_axle_f))
                    # Front average wheel radius
                    if len(list_radius_f) >= min_samples_f:
                        radius_front = calc.mean(sorted(list_radius_f)[samples_slice_f])
                        if min_samples_f < 160:
                            min_samples_f *= 2  # double sample counts
                            samples_slice_f = sample_slice_indices(min_samples_f)

                if rot_axle_r < -min_rot_axle and 0 < rot_bias_r < max_rot_bias_r:
                    list_radius_r.append(calc.rot2radius(speed, rot_axle_r))
                    # Rear average wheel radius
                    if len(list_radius_r) >= min_samples_r:
                        radius_rear = calc.mean(sorted(list_radius_r)[samples_slice_r])
                        if min_samples_r < 160:
                            min_samples_r *= 2
                            samples_slice_r = sample_slice_indices(min_samples_r)

                # Calculate cornering radius based on tri-coordinates position
                if gps_last != gps_curr:
                    gps_last = gps_curr
                    list_coords.append(gps_curr)
                    arc_center_pos = calc.tri_coords_circle_center(
                        *list_coords[0], *list_coords[min_coords], *list_coords[-1])
                    cornering_radius = calc.distance(list_coords[0], arc_center_pos)

                # Output wheels data
                output.radiusFront = radius_front
                output.radiusRear = radius_rear
                output.lockingPercentFront = locking_f
                output.lockingPercentRear = locking_r
                output.corneringRadius = cornering_radius
                output.slipRatio[0] = calc.slip_ratio(wheel_rot[0], radius_front, speed)
                output.slipRatio[1] = calc.slip_ratio(wheel_rot[1], radius_front, speed)
                output.slipRatio[2] = calc.slip_ratio(wheel_rot[2], radius_rear, speed)
                output.slipRatio[3] = calc.slip_ratio(wheel_rot[3], radius_rear, speed)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


def sample_slice_indices(samples: int) -> slice:
    """Calculate sample slice indices from minimum samples"""
    return slice(int(samples * 0.25), int(samples * 0.75))
