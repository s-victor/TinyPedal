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
import threading

from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_force"

logger = logging.getLogger(__name__)


class Realtime:
    """Force data"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.event = threading.Event()

    def start(self):
        """Start update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__update_data, daemon=True).start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: module force")

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __update_data(self):
        """Update module data"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                    #gen_max_avg_lgt = self.calc_max_avg_gforce()
                    #max_avg_lgt_gforce = next(gen_max_avg_lgt)
                    gen_max_avg_lat = self.calc_max_avg_gforce()
                    max_avg_lat_gforce = next(gen_max_avg_lat)

                    gen_max_lgt = self.calc_max_gforce()
                    max_lgt_gforce = next(gen_max_lgt)
                    gen_max_lat = self.calc_max_gforce()
                    max_lat_gforce = next(gen_max_lat)

                # Read telemetry
                lap_etime = api.read.timing.elapsed()
                lat_accel = api.read.vehicle.accel_lateral()
                lgt_accel = api.read.vehicle.accel_longitudinal()
                dforce_f = api.read.vehicle.downforce_front()
                dforce_r = api.read.vehicle.downforce_rear()

                # G raw
                lgt_gforce_raw = calc.gforce(
                    lgt_accel, self.mcfg["gravitational_acceleration"])
                lat_gforce_raw = calc.gforce(
                    lat_accel, self.mcfg["gravitational_acceleration"])

                # Max average G
                #max_avg_lgt_gforce = gen_max_avg_lgt.send(lgt_gforce_raw)
                max_avg_lat_gforce = gen_max_avg_lat.send(lat_gforce_raw)

                # Max G
                max_lgt_gforce = gen_max_lgt.send((lgt_gforce_raw, lap_etime))
                max_lat_gforce = gen_max_lat.send((lat_gforce_raw, lap_etime))

                # G Vector
                #gforce_vector = calc.distance((lgt_gforce_raw, lat_gforce_raw),(0,0))

                # Downforce
                dforce_ratio = calc.force_ratio(dforce_f, dforce_f + dforce_r)

                # Output force data
                minfo.force.lgtGForceRaw = lgt_gforce_raw
                minfo.force.latGForceRaw = lat_gforce_raw
                #minfo.force.maxAvgLgtGForce = max_avg_lgt_gforce
                minfo.force.maxAvgLatGForce = max_avg_lat_gforce
                minfo.force.maxLgtGForce = max_lgt_gforce
                minfo.force.maxLatGForce = max_lat_gforce
                #minfo.force.gForceVector = gforce_vector
                minfo.force.downForceFront = dforce_f
                minfo.force.downForceRear = dforce_r
                minfo.force.downForceRatio = dforce_ratio

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: module force")

    def calc_max_avg_gforce(self):
        """Calc max average G force"""
        max_samples = max(int(self.mcfg["max_average_g_force_samples"]), 3)
        g_samples = array.array("f", [0] * max_samples)
        g_abs = 0
        g_abs_last = 0
        g_max_avg = 0
        sample_counter = 0
        sample_idx = 0
        while True:
            if sample_counter >= max_samples:
                g_avg = calc.mean(g_samples)
                g_std = calc.std_dev(g_samples, g_avg)
                if (g_avg > g_max_avg and
                    0 < g_std <= self.mcfg["max_average_g_force_difference"]):
                    g_max_avg = g_avg
                    sample_counter = 0
            # Reset sample index
            if sample_idx >= max_samples:
                sample_idx = 0
            # Update data if pos diff
            if g_abs != g_abs_last:
                g_samples[sample_idx] = g_abs_last = g_abs
                sample_idx += 1
                if sample_counter < max_samples:
                    sample_counter += 1
            g_raw = yield g_max_avg
            g_abs = abs(g_raw)

    def calc_max_gforce(self):
        """Calc max G force"""
        g_abs = 0
        g_max_abs = 0
        g_timer = 0
        etime = 0
        while True:
            if g_abs > g_max_abs:
                g_max_abs = g_abs
                g_timer = etime
            if g_timer:
                time_diff = etime - g_timer
                if time_diff > self.mcfg["max_g_force_freeze_duration"]:
                    g_max_abs = g_abs
                    g_timer = 0
            g_raw, etime = yield g_max_abs
            g_abs = abs(g_raw)
