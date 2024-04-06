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
Delta module
"""

import logging
import csv

from ._base import DataModule
from ..module_info import minfo
from ..const import PATH_DELTABEST
from ..api_control import api
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_delta"
DELTA_ZERO = 0.0,0.0

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Delta time data"""
    filepath = PATH_DELTABEST

    def __init__(self, config):
        DataModule.__init__(self, config, MODULE_NAME, self.update_data)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        last_session_id = ("",-1,-1,-1)
        delta_list_session = [DELTA_ZERO]
        delta_list_stint = [DELTA_ZERO]
        laptime_session_best = 99999
        laptime_stint_best = 99999

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    recording = False
                    validating = 0

                    combo_id = api.read.check.combo_id()
                    session_id = api.read.check.session_id()

                    # Reset delta session best if not same session
                    if not self.is_same_session(combo_id, session_id, last_session_id):
                        delta_list_session = [DELTA_ZERO]
                        laptime_session_best = 99999
                        last_session_id = (combo_id, *session_id)

                    delta_list_best, laptime_best = self.load_deltabest(combo_id)
                    delta_list_curr = [DELTA_ZERO]  # distance, laptime
                    delta_list_last = [DELTA_ZERO]  # last lap

                    delta_best = 0  # delta time compare to best laptime
                    delta_last = 0
                    session_delta_best = 0
                    stint_delta_best = 0

                    laptime_curr = 0  # current laptime
                    laptime_last = 0  # last laptime

                    last_lap_stime = -1  # lap-start-time
                    pos_last = 0  # last checked vehicle position
                    pos_estimate = 0  # calculated position
                    gps_last = [0,0,0]  # last global position
                    meters_driven = self.cfg.user.setting["cruise"]["meters_driven"]

                # Read telemetry
                lap_stime = api.read.timing.start()
                laptime_curr = max(api.read.timing.current_laptime(), 0)
                laptime_valid = api.read.timing.last_laptime()
                pos_curr = api.read.lap.distance()
                gps_curr = (api.read.vehicle.position_x(),
                            api.read.vehicle.position_y(),
                            api.read.vehicle.position_z())
                in_pits = api.read.vehicle.in_pits()
                speed = api.read.vehicle.speed()

                # Reset delta stint best if in pit
                if in_pits and delta_list_stint[-1][0] and speed < 0.1:
                    delta_list_stint = [DELTA_ZERO]
                    laptime_stint_best = 99999

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    laptime_last = lap_stime - last_lap_stime
                    if len(delta_list_curr) > 1:
                        delta_list_curr.append(  # set end value
                            (round(pos_last + 10, 6), round(laptime_last, 6))
                        )
                        delta_list_last = delta_list_curr
                        validating = api.read.timing.elapsed()
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
                    timer = api.read.timing.elapsed() - validating
                    if 1 < timer <= 10:  # compare current time
                        if laptime_valid > 0 and abs(laptime_valid - laptime_last) < 2:
                            # Update delta best list
                            if laptime_last < laptime_best:
                                laptime_best = laptime_last
                                delta_list_best = delta_list_last.copy()
                                self.save_deltabest(combo_id, delta_list_best)
                            # Update delta session best list
                            if laptime_last < laptime_session_best:
                                laptime_session_best = laptime_last
                                delta_list_session = delta_list_last.copy()
                            # Update delta stint best list
                            if laptime_last < laptime_stint_best:
                                laptime_stint_best = laptime_last
                                delta_list_stint = delta_list_last.copy()
                            # Reset delta last list
                            # delta_list_last = [DELTA_ZERO]
                            validating = 0
                    elif timer > 10:  # switch off after 8s
                        validating = 0

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
                    delta_last = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_last,
                        laptime_curr > 0.3,  # 300ms delay
                        0.02,  # add 20ms offset
                    )
                    session_delta_best = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_session,
                        laptime_curr > 0.3,  # 300ms delay
                        0.02,  # add 20ms offset
                    )
                    stint_delta_best = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_stint,
                        laptime_curr > 0.3,  # 300ms delay
                        0.02,  # add 20ms offset
                    )
                    # Update driven distance
                    if moved_distance < 1500 * self.active_interval:
                        meters_driven += moved_distance

                # Output delta time data
                minfo.delta.lapTimeCurrent = laptime_curr
                minfo.delta.lapTimeLast = laptime_last
                minfo.delta.lapTimeBest = laptime_best
                minfo.delta.lapTimeEstimated = laptime_best + delta_best
                minfo.delta.lapTimeStintBest = laptime_stint_best
                minfo.delta.deltaBest = delta_best
                minfo.delta.deltaLast = delta_last
                minfo.delta.deltaSession = session_delta_best
                minfo.delta.deltaStint = stint_delta_best
                minfo.delta.isValidLap = laptime_valid > 0
                minfo.delta.metersDriven = meters_driven

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    last_session_id = (combo_id, *session_id)
                    self.cfg.user.setting["cruise"]["meters_driven"] = int(meters_driven)
                    self.cfg.save()

    def load_deltabest(self, combo):
        """Load delta best & best laptime"""
        try:
            with open(f"{self.filepath}{combo}.csv",
                      newline="", encoding="utf-8") as csvfile:
                temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
                temp_list_size = len(temp_list)
                # Validate data
                bestlist = val.delta_list(temp_list)
                laptime_best = bestlist[-1][1]
                # Save data if modified
                if temp_list_size != len(bestlist):
                    self.save_deltabest(combo, bestlist)
        except (FileNotFoundError, IndexError, ValueError, TypeError):
            logger.info("MISSING: deltabest data")
            bestlist = [(99999,99999)]
            laptime_best = 99999
        return bestlist, laptime_best

    def save_deltabest(self, combo, listname):
        """Save delta best"""
        if len(listname) >= 10:
            with open(f"{self.filepath}{combo}.csv",
                    "w", newline="", encoding="utf-8") as csvfile:
                deltawrite = csv.writer(csvfile)
                deltawrite.writerows(listname)

    @staticmethod
    def is_same_session(combo_id, session_id, last_session_id):
        """Check if same session, car, track combo"""
        return bool(
            combo_id == last_session_id[0] and
            last_session_id[1] == session_id[0] and
            last_session_id[2] <= session_id[1] and
            last_session_id[3] <= session_id[2]
        )
