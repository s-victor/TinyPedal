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
from collections import namedtuple

from ..const import PATH_DELTABEST
from ..readapi import info, chknm, state, combo_check
from .. import calculation as calc

MODULE_NAME = "module_delta"

logger = logging.getLogger(__name__)


class Realtime:
    """Delta time data"""
    module_name = MODULE_NAME
    filepath = PATH_DELTABEST
    DataSet = namedtuple(
        "DataSet",
        [
        "LaptimeCurrent",
        "LaptimeLast",
        "LaptimeBest",
        "LaptimeEstimated",
        "DeltaBest",
        "IsValidLap",
        "MetersDriven",
        ],
        defaults = ([0] * 7)
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
            logger.info("delta module started")

    def __calculation(self):
        """Delta calculation"""
        recording = False  # set delta recording state
        verified = False  # additional check for conserving resources
        validating = False  # validate last laptime after cross finish line

        meters_driven = 0
        delta_list_curr = []  # distance vs time list, current lap
        delta_list_last = []  # distance vs time list, last lap, used for verification only
        delta_list_best = []  # distance vs time list, best lap
        delta_best = 0  # delta time compare to best laptime
        last_lap_stime = 0  # lap-start-time
        pos_last = 0  # last checked player vehicle position
        pos_append = 0  # append last checked position with calc traveled dist
        gps_last = [0,0,0]  # last global position
        last_time = 0  # last checked elapsed time
        laptime_curr = 0  # current laptime
        laptime_last = 0  # last laptime
        laptime_best = 99999  # best laptime
        laptime_est = 0  # estimated current laptime
        combo_name = "unknown"  # current car & track combo

        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                (lap_stime, elapsed_time, lastlap_check, speed, pos_curr, gps_curr, game_phase
                 ) = self.__telemetry()

                # Read combo & best laptime
                if not verified:
                    verified = True
                    update_interval = active_interval  # shorter delay
                    combo_name = combo_check()
                    delta_list_best, laptime_best = self.load_deltabest(combo_name)
                    meters_driven = self.cfg.setting_user["cruise"]["meters_driven"]
                    last_lap_stime = lap_stime  # reset lap-start-time

                if game_phase < 5:  # reset stint stats if session has not started
                    last_lap_stime = lap_stime  # reset

                # Start updating
                laptime_curr = max(elapsed_time - last_lap_stime, 0)  # current laptime

                # Lap start & finish detection
                if lap_stime > last_lap_stime:  # difference of lap-start-time
                    laptime_last = lap_stime - last_lap_stime

                    if delta_list_curr:  # non-empty list check
                        delta_list_curr.append((pos_last + 10, laptime_last))  # set end value
                        delta_list_last = delta_list_curr
                        validating = True

                    delta_list_curr = []  # reset current delta list
                    delta_list_curr.append((0.0, 0.0))  # set start value
                    recording = True  # activate delta recording
                    last_lap_stime = lap_stime  # reset
                    pos_last = pos_curr  # set pos last

                # Laptime validating 1s after passing finish line
                # To compensate 5fps refresh rate of Scoring data
                # Must place validating after lap start & finish detection
                # Negative mLastLapTime value indicates invalid last laptime
                if validating:
                    if 1 < laptime_curr <= 8:
                        if laptime_last < laptime_best and abs(lastlap_check - laptime_last) < 1:
                            laptime_best = laptime_last
                            delta_list_best = delta_list_last
                            self.save_deltabest(combo_name, delta_list_best)
                            validating = False
                    elif 8 < laptime_curr < 10:  # switch off validating after 8s
                        validating = False

                # Recording only from the beginning of a lap
                if recording:
                    # Update position if current dist value is diff & positive
                    if pos_curr != pos_last and pos_curr >= 0:
                        if pos_curr > pos_last:  # record if position is further away
                            delta_list_curr.append((pos_curr, laptime_curr))

                        pos_last = pos_curr  # reset last position
                        pos_append = pos_last  # reset initial position for appending

                # Update time difference & calculate additional traveled distance
                if elapsed_time != last_time:
                    delta_dist = speed * (elapsed_time - last_time)
                    pos_append += delta_dist
                    last_time = elapsed_time
                    index_lower, index_higher = calc.nearest_dist_index(
                                                pos_append, delta_list_best)
                    try:  # add 20ms error offset due to 50hz refresh rate limit
                        if sum([delta_list_best[index_lower][0],
                               delta_list_best[index_lower][1],
                               delta_list_best[index_higher][0],
                               delta_list_best[index_higher][1]]) != 0:
                            delta_best = laptime_curr + 0.02 - calc.linear_interp(
                                                pos_append,
                                                delta_list_best[index_lower][0],
                                                delta_list_best[index_lower][1],
                                                delta_list_best[index_higher][0],
                                                delta_list_best[index_higher][1])
                    except IndexError:
                        delta_best = 0

                laptime_est = laptime_best + delta_best

                # Record driven distance in meters
                if gps_last != gps_curr:
                    moved_distance = calc.distance_xyz(gps_last, gps_curr)
                    if moved_distance < 15:  # add small amount limit
                        meters_driven += moved_distance
                    gps_last = gps_curr

                # Output delta time data
                self.output = self.DataSet(
                    LaptimeCurrent = laptime_curr,
                    LaptimeLast = laptime_last,
                    LaptimeBest = laptime_best,
                    LaptimeEstimated = laptime_est,
                    DeltaBest = delta_best,
                    IsValidLap = bool(lastlap_check > 0),
                    MetersDriven = meters_driven,
                )

            else:
                if verified:
                    recording = False  # disable delta recording after exit track
                    verified = False  # activate verification when enter track next time
                    validating = False  # disable laptime validate
                    update_interval = idle_interval  # longer delay while inactive
                    delta_list_curr = []  # reset current delta list

                    # Save meters driven & last laptime data
                    self.cfg.setting_user["cruise"]["meters_driven"] = int(meters_driven)
                    self.cfg.save()

            time.sleep(update_interval)

        self.set_output()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("delta module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
        elapsed_time = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        lastlap_check = chknm(info.syncedVehicleScoring().mLastLapTime)
        speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.z))
        pos_curr = chknm(info.syncedVehicleScoring().mLapDist)
        gps_curr = (chknm(info.syncedVehicleTelemetry().mPos.x),
                    chknm(info.syncedVehicleTelemetry().mPos.y),
                    chknm(info.syncedVehicleTelemetry().mPos.z))
        game_phase = chknm(info.LastScor.mScoringInfo.mGamePhase)
        return (lap_stime, elapsed_time, lastlap_check, speed, pos_curr,
                gps_curr, game_phase)

    def load_deltabest(self, combo):
        """Load delta best & best laptime"""
        try:
            with open(f"{self.filepath}{combo}.csv", newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                bestlist = list(deltaread)
                bestlap = bestlist[-1][1]  # read best laptime
        except (FileNotFoundError, IndexError):
            bestlist = []
            bestlap = 99999
        return bestlist, bestlap

    def save_deltabest(self, combo, listname):
        """Save delta best"""
        with open(f"{self.filepath}{combo}.csv", "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(listname)
