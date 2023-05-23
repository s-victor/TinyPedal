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

import logging
import time
import threading
from collections import namedtuple

from ..readapi import info, chknm, state
from .. import calculation as calc

MODULE_NAME = "module_force"

logger = logging.getLogger(__name__)


class Realtime:
    """Force data"""
    module_name = MODULE_NAME
    DataSet = namedtuple(
        "DataSet",
        [
        "LgtGForceRaw",
        "LatGForceRaw",
        "MaxAvgLgtGForce",
        "MaxAvgLatGForce",
        "MaxLgtGForce",
        "MaxLatGForce",
        "GForceVector",
        "DownForceFront",
        "DownForceRear",
        "DownForceRatio",
        ],
        defaults = ([0] * 10)
    )

    def __init__(self, mctrl, config):
        self.mctrl = mctrl
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False
        self.set_output()

    def set_output(self):
        """Set output"""
        self.output = self.DataSet()

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
        checked = False

        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                (elapsed_time, lgt_accel, lat_accel, dforce_f, dforce_r
                 ) = self.__telemetry()

                if not checked:
                    checked = True
                    update_interval = active_interval  # shorter delay

                    gen_max_avg_lgt = self.calc_max_avg_gforce()
                    max_avg_lgt_gforce = next(gen_max_avg_lgt)
                    gen_max_avg_lat = self.calc_max_avg_gforce()
                    max_avg_lat_gforce = next(gen_max_avg_lat)

                    gen_max_lgt = self.calc_max_gforce()
                    max_lgt_gforce = next(gen_max_lgt)
                    gen_max_lat = self.calc_max_gforce()
                    max_lat_gforce = next(gen_max_lat)

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
                gforce_vector = calc.distance_xy((lgt_gforce_raw, lat_gforce_raw))

                # Downforce
                dforce_ratio = calc.force_ratio(dforce_f, dforce_f + dforce_r)

                # Output force data
                self.output = self.DataSet(
                    LgtGForceRaw = lgt_gforce_raw,
                    LatGForceRaw = lat_gforce_raw,
                    MaxAvgLgtGForce = max_avg_lgt_gforce,
                    MaxAvgLatGForce = max_avg_lat_gforce,
                    MaxLgtGForce = max_lgt_gforce,
                    MaxLatGForce = max_lat_gforce,
                    GForceVector = gforce_vector,
                    DownForceFront = dforce_f,
                    DownForceRear = dforce_r,
                    DownForceRatio = dforce_ratio,
                )

            else:
                if checked:
                    checked = False
                    update_interval = idle_interval  # longer delay while inactive

            time.sleep(update_interval)

        self.set_output()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("force module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        elapsed_time = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        lgt_accel = chknm(info.syncedVehicleTelemetry().mLocalAccel.z)
        lat_accel = chknm(info.syncedVehicleTelemetry().mLocalAccel.x)
        dforce_f = chknm(info.syncedVehicleTelemetry().mFrontDownforce)
        dforce_r = chknm(info.syncedVehicleTelemetry().mRearDownforce)
        return elapsed_time, lgt_accel, lat_accel, dforce_f, dforce_r

    def calc_max_avg_gforce(self):
        """Calc max average G force"""
        g_abs = 0
        g_max_avg = 0
        g_samples = []
        while True:
            if len(g_samples) >= self.mcfg["max_average_g_force_samples"]:
                g_diff = max(g_samples) - min(g_samples)
                g_avg = sum(g_samples) / len(g_samples)
                if (g_avg > g_max_avg and
                    0 < g_diff <= self.mcfg["max_average_g_force_differece"]):
                    g_max_avg = g_avg
                    g_samples.clear()
                else:
                    g_samples.pop(0)
            if g_samples and g_abs != g_samples[-1]:  # update if pos diff
                g_samples.append(g_abs)
            elif not g_samples:
                g_samples.append(g_abs)
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
