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
Force module
"""

import array
import logging
import time
import threading

from ..module_info import minfo
from ..readapi import info, chknm, state
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
        self.running = False

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("force module started")

    def __calculation(self):
        """Force calculation"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    gen_max_avg_lgt = self.calc_max_avg_gforce()
                    max_avg_lgt_gforce = next(gen_max_avg_lgt)
                    gen_max_avg_lat = self.calc_max_avg_gforce()
                    max_avg_lat_gforce = next(gen_max_avg_lat)

                    gen_max_lgt = self.calc_max_gforce()
                    max_lgt_gforce = next(gen_max_lgt)
                    gen_max_lat = self.calc_max_gforce()
                    max_lat_gforce = next(gen_max_lat)

                # Read telemetry
                (elapsed_time, lgt_accel, lat_accel, dforce_f, dforce_r
                 ) = self.__telemetry()

                # G raw
                lgt_gforce_raw = calc.gforce(
                    lgt_accel, self.mcfg["gravitational_acceleration"])
                lat_gforce_raw = calc.gforce(
                    lat_accel, self.mcfg["gravitational_acceleration"])

                # Max average G
                max_avg_lgt_gforce = gen_max_avg_lgt.send(lgt_gforce_raw)
                max_avg_lat_gforce = gen_max_avg_lat.send(lat_gforce_raw)

                # Max G
                max_lgt_gforce = gen_max_lgt.send((lgt_gforce_raw, elapsed_time))
                max_lat_gforce = gen_max_lat.send((lat_gforce_raw, elapsed_time))

                # G Vector
                gforce_vector = calc.distance((lgt_gforce_raw, lat_gforce_raw),(0,0))

                # Downforce
                dforce_ratio = calc.force_ratio(dforce_f, dforce_f + dforce_r)

                # Output force data
                minfo.force.LgtGForceRaw = lgt_gforce_raw
                minfo.force.LatGForceRaw = lat_gforce_raw
                minfo.force.MaxAvgLgtGForce = max_avg_lgt_gforce
                minfo.force.MaxAvgLatGForce = max_avg_lat_gforce
                minfo.force.MaxLgtGForce = max_lgt_gforce
                minfo.force.MaxLatGForce = max_lat_gforce
                minfo.force.GForceVector = gforce_vector
                minfo.force.DownForceFront = dforce_f
                minfo.force.DownForceRear = dforce_r
                minfo.force.DownForceRatio = dforce_ratio

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("force module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        elapsed_time = chknm(info.playerTele.mElapsedTime)
        lgt_accel = chknm(info.playerTele.mLocalAccel.z)
        lat_accel = chknm(info.playerTele.mLocalAccel.x)
        dforce_f = chknm(info.playerTele.mFrontDownforce)
        dforce_r = chknm(info.playerTele.mRearDownforce)
        return elapsed_time, lgt_accel, lat_accel, dforce_f, dforce_r

    def calc_max_avg_gforce(self):
        """Calc max average G force"""
        max_samples = int(max(self.mcfg["max_average_g_force_samples"], 3))
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
                    0 < g_std <= self.mcfg["max_average_g_force_differece"]):
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
