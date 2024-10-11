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
Force module
"""

import array
import logging

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_force"

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Force data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    gen_max_avg_lat = self.calc_max_avg_gforce()
                    max_avg_lat_gforce = next(gen_max_avg_lat)

                    gen_max_lgt = self.calc_max_gforce()
                    max_lgt_gforce = next(gen_max_lgt)
                    gen_max_lat = self.calc_max_gforce()
                    max_lat_gforce = next(gen_max_lat)
                    gen_braking_rate = self.calc_braking_rate()
                    (braking_rate, max_braking_rate_transient, max_braking_rate, delta_braking_rate
                     ) = next(gen_braking_rate)

                # Read telemetry
                lap_etime = api.read.timing.elapsed()
                lat_accel = api.read.vehicle.accel_lateral()
                lgt_accel = api.read.vehicle.accel_longitudinal()
                dforce_f = api.read.vehicle.downforce_front()
                dforce_r = api.read.vehicle.downforce_rear()
                speed = api.read.vehicle.speed()

                # G raw
                lgt_gforce_raw = calc.gforce(
                    lgt_accel, self.mcfg["gravitational_acceleration"])
                lat_gforce_raw = calc.gforce(
                    lat_accel, self.mcfg["gravitational_acceleration"])

                # Max average lateral G
                max_avg_lat_gforce = gen_max_avg_lat.send((lat_gforce_raw, lap_etime))

                # Max G
                max_lgt_gforce = gen_max_lgt.send((lgt_gforce_raw, lap_etime))
                max_lat_gforce = gen_max_lat.send((lat_gforce_raw, lap_etime))

                # G Vector
                #gforce_vector = calc.distance((lgt_gforce_raw, lat_gforce_raw),(0,0))

                # Downforce
                dforce_ratio = calc.force_ratio(dforce_f, dforce_f + dforce_r)

                # Braking rate
                (braking_rate, max_braking_rate_transient, max_braking_rate, delta_braking_rate
                 ) = gen_braking_rate.send((speed, lap_etime))

                # Output force data
                minfo.force.lgtGForceRaw = lgt_gforce_raw
                minfo.force.latGForceRaw = lat_gforce_raw
                minfo.force.maxAvgLatGForce = max_avg_lat_gforce
                minfo.force.maxLgtGForce = max_lgt_gforce
                minfo.force.maxLatGForce = max_lat_gforce
                minfo.force.downForceFront = dforce_f
                minfo.force.downForceRear = dforce_r
                minfo.force.downForceRatio = dforce_ratio
                minfo.force.brakingRate = braking_rate
                minfo.force.transientMaxBrakingRate = max_braking_rate_transient
                minfo.force.maxBrakingRate = max_braking_rate
                minfo.force.deltaBrakingRate = delta_braking_rate

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

    def calc_max_avg_gforce(self):
        """Calc max average G force"""
        max_samples = max(int(self.mcfg["max_average_g_force_samples"]), 3)
        g_samples = array.array("f", [0] * max_samples)
        g_abs = 0
        g_abs_last = 0
        g_max_avg = 0       # max average g
        g_max_avg_alt = 0   # secondary max average g
        sample_counter = 0
        sample_idx = 0
        etime = 0
        reset_timer = 0
        reset_max = False
        while True:
            if sample_counter >= max_samples:
                g_avg = calc.mean(g_samples)
                g_std = calc.std_dev(g_samples, g_avg)
                valid_range = 0 < g_std <= self.mcfg["max_average_g_force_difference"]
                if g_avg > g_max_avg and valid_range:
                    g_max_avg = g_avg
                    sample_counter = 0
                    reset_timer = 0
                    reset_max = False
                elif g_avg > g_max_avg_alt and valid_range:
                    g_max_avg_alt = g_avg
                    reset_timer = etime
            # Reset max avg g
            if reset_max:
                g_max_avg = g_max_avg_alt
                g_max_avg_alt = 0
                reset_max = False
            # Start reset timer
            if reset_timer and etime - reset_timer > self.mcfg["max_average_g_force_reset_delay"]:
                reset_timer = 0
                reset_max = True
            # Reset sample index
            if sample_idx >= max_samples:
                sample_idx = 0
            # Update data if pos diff
            if g_abs != g_abs_last:
                g_samples[sample_idx] = g_abs_last = g_abs
                sample_idx += 1
                if sample_counter < max_samples:
                    sample_counter += 1
            # Output
            g_raw, etime = yield g_max_avg
            g_abs = abs(g_raw)

    def calc_max_gforce(self):
        """Calc max G force"""
        g_abs = 0
        g_max_abs = 0
        etime = 0
        reset_timer = 0
        while True:
            if g_abs > g_max_abs:
                g_max_abs = g_abs
                reset_timer = etime
            # Start reset timer
            if reset_timer and etime - reset_timer > self.mcfg["max_g_force_reset_delay"]:
                g_max_abs = g_abs
                reset_timer = 0
            # Output
            g_raw, etime = yield g_max_abs
            g_abs = abs(g_raw)

    def calc_braking_rate(self):
        """Calc braking rate"""
        speed = 0
        etime = 0
        last_speed = 0
        last_etime = 0
        braking_rate = 0
        max_braking_rate = 0       # max rate
        max_braking_rate_alt = 0   # secondary max rate
        max_braking_rate_transient = 0  # transient max rate
        delta_braking_rate = 0     # delta rate between best max & transient max rate
        freeze_timer = 0
        reset_timer = 0
        reset_max = False
        while True:
            if last_etime != etime:
                if api.read.input.brake_raw() > 0.02 and speed > 1:
                    braking_decel = max(last_speed - speed, 0) / (etime - last_etime)
                    braking_rate = braking_decel / self.mcfg["gravitational_acceleration"]
                    freeze_timer = etime
                    # Update transient max braking rate
                    if braking_rate > max_braking_rate_transient:
                        max_braking_rate_transient = braking_rate
                    # Update secondary max braking rate
                    if braking_rate > max_braking_rate:  # reset timer trigger
                        max_braking_rate_alt = 0
                        reset_timer = 0
                        reset_max = False
                    elif braking_rate > max_braking_rate_alt:
                        max_braking_rate_alt = braking_rate
                        reset_timer = etime
                last_speed = speed
                last_etime = etime
            # Reset max braking rate
            if reset_max:
                max_braking_rate = max_braking_rate_alt
                max_braking_rate_alt = 0
                reset_max = False
            # Start timer
            if freeze_timer:
                delta_braking_rate = max_braking_rate_transient - max_braking_rate
                # Reset if impacted within past 2 seconds
                if etime - api.read.vehicle.impact_time() < 2:
                    freeze_timer = 0
                    max_braking_rate_transient = 0
                    delta_braking_rate = 0
                # Update transient max rate to max rate, 3 seconds after brake released
                if etime - freeze_timer > 3:
                    if max_braking_rate_transient > max_braking_rate:
                        max_braking_rate = max_braking_rate_transient
                    freeze_timer = 0
                    max_braking_rate_transient = 0
            if reset_timer and etime - reset_timer > self.mcfg["max_braking_rate_reset_delay"]:
                reset_timer = 0
                reset_max = True
            # Output
            speed, etime = yield (
                braking_rate, max_braking_rate_transient, max_braking_rate, delta_braking_rate)
