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
Delta module
"""

import logging
import time
import threading
import csv

from ..module_info import minfo
from ..const import PATH_DELTABEST
from ..readapi import info, chknm, state, combo_check
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_delta"
DELTA_ZERO = 0.0,0.0

logger = logging.getLogger(__name__)


class Realtime:
    """Delta time data"""
    module_name = MODULE_NAME
    filepath = PATH_DELTABEST

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
            logger.info("delta module started")

    def __calculation(self):
        """Delta calculation"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    recording = False
                    validating = False

                    combo_name = combo_check()
                    delta_list_best = self.load_deltabest(combo_name)
                    delta_list_curr = [DELTA_ZERO]  # distance, laptime
                    delta_list_last = [DELTA_ZERO]  # last lap
                    delta_best = 0  # delta time compare to best laptime

                    last_lap_stime = -1  # lap-start-time
                    laptime_curr = 0  # current laptime
                    laptime_last = 0  # last laptime
                    laptime_best = delta_list_best[-1][1]  # best laptime
                    pos_last = 0  # last checked vehicle position
                    pos_estimate = 0  # calculated position
                    gps_last = [0,0,0]  # last global position
                    meters_driven = self.cfg.setting_user["cruise"]["meters_driven"]

                # Read telemetry
                (lap_stime, laptime_curr, lastlap_valid, pos_curr, gps_curr
                 ) = self.__telemetry()

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    laptime_last = lap_stime - last_lap_stime
                    if len(delta_list_curr) > 1:
                        delta_list_curr.append(  # set end value
                            (round(pos_last + 10, 6), round(laptime_last, 6))
                        )
                        delta_list_last = delta_list_curr
                        validating = True
                    delta_list_curr = [DELTA_ZERO]  # reset
                    pos_last = pos_curr
                    recording = laptime_curr < 1
                last_lap_stime = lap_stime  # reset

                # 1 sec position distance check after new lap begins
                # Reset to 0 if higher than normal distance
                if 0 < laptime_curr < 1 and pos_curr > 300:
                    pos_last = pos_curr = 0

                # Update if position value is different & positive
                if 0 <= pos_curr != pos_last:
                    if recording and pos_curr > pos_last:  # position further
                        delta_list_curr.append(  # keep 6 decimals
                            (round(pos_curr, 6), round(laptime_curr, 6))
                        )
                    pos_estimate = pos_last = pos_curr  # reset last position

                # Validating 1s after passing finish line
                if validating:
                    if 1 < laptime_curr <= 8:  # compare current time
                        if laptime_last < laptime_best and abs(lastlap_valid - laptime_last) < 1:
                            laptime_best = laptime_last
                            delta_list_best = delta_list_last
                            delta_list_last = [DELTA_ZERO]
                            self.save_deltabest(combo_name, delta_list_best)
                            validating = False
                    elif 8 < laptime_curr < 10:  # switch off after 8s
                        validating = False

                # Calc delta
                if gps_last != gps_curr:
                    moved_distance = calc.distance(gps_last, gps_curr)
                    gps_last = gps_curr
                    # Update delta
                    pos_estimate += moved_distance
                    delta_best = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_best,
                        laptime_curr > 0.3,  # 300ms delay
                        0.02,  # add 20ms offset
                    )
                    # Update driven distance
                    if moved_distance < 1500 * active_interval:
                        meters_driven += moved_distance

                # Output delta time data
                minfo.delta.LaptimeCurrent = laptime_curr
                minfo.delta.LaptimeLast = laptime_last
                minfo.delta.LaptimeBest = laptime_best
                minfo.delta.LaptimeEstimated = laptime_best + delta_best
                minfo.delta.DeltaBest = delta_best
                minfo.delta.IsValidLap = lastlap_valid > 0
                minfo.delta.MetersDriven = meters_driven

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval
                    self.cfg.setting_user["cruise"]["meters_driven"] = int(meters_driven)
                    self.cfg.save()

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("delta module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.rf2TeleVeh().mLapStartET)
        laptime_curr = max(chknm(info.rf2TeleVeh().mElapsedTime) - lap_stime, 0)
        lastlap_valid = chknm(info.rf2ScorVeh().mLastLapTime)
        pos_curr = chknm(info.rf2ScorVeh().mLapDist)
        gps_curr = (chknm(info.rf2TeleVeh().mPos.x),
                    chknm(info.rf2TeleVeh().mPos.y),
                    chknm(info.rf2TeleVeh().mPos.z))
        return lap_stime, laptime_curr, lastlap_valid, pos_curr, gps_curr

    def load_deltabest(self, combo):
        """Load delta best & best laptime"""
        try:
            with open(f"{self.filepath}{combo}.csv",
                      newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                bestlist = list(deltaread)
                # Validate data
                if not val.delta_list(bestlist):
                    self.save_deltabest(combo, bestlist)
        except (FileNotFoundError, IndexError, ValueError, TypeError):
            logger.info("no valid deltabest data file found")
            bestlist = [(99999,99999)]
        return bestlist

    def save_deltabest(self, combo, listname):
        """Save delta best"""
        with open(f"{self.filepath}{combo}.csv",
                  "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(listname)
