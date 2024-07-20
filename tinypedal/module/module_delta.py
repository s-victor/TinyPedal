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
from functools import partial

from ._base import DataModule
from ..module_info import minfo
from ..const import PATH_DELTABEST
from ..api_control import api
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_delta"
DELTA_ZERO = 0.0,0.0

logger = logging.getLogger(__name__)
round6 = partial(round, ndigits=6)


class Realtime(DataModule):
    """Delta time data"""
    filepath = PATH_DELTABEST

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        last_session_id = ("",-1,-1,-1)
        delta_list_session = [DELTA_ZERO]
        delta_list_stint = [DELTA_ZERO]
        laptime_session_best = 99999
        laptime_stint_best = 99999

        exp_mov_avg = partial(calc.exp_mov_avg, self.set_smoothing_factor())

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
                    if not val.same_session(combo_id, session_id, last_session_id):
                        delta_list_session = [DELTA_ZERO]
                        laptime_session_best = 99999
                        last_session_id = (combo_id, *session_id)

                    delta_list_best, laptime_best = load_deltabest(self.filepath, combo_id)
                    delta_list_curr = [DELTA_ZERO]  # distance, laptime
                    delta_list_last = [DELTA_ZERO]  # last lap

                    delta_best = 0  # delta time compare to best laptime
                    delta_last = 0
                    delta_session = 0
                    delta_stint = 0

                    delta_best_ema = 0
                    delta_last_ema = 0
                    delta_session_ema = 0
                    delta_stint_ema = 0

                    laptime_curr = 0  # current laptime
                    laptime_last = 0  # last laptime

                    last_lap_stime = -1  # lap-start-time
                    pos_last = 0  # last checked vehicle position
                    pos_estimate = 0  # calculated position
                    pos_synced = False  # whether estimated position synced
                    gps_last = [0,0,0]  # last global position
                    meters_driven = self.cfg.user.setting["cruise"]["meters_driven"]

                # Read telemetry
                lap_stime = api.read.timing.start()
                laptime_curr = max(api.read.timing.current_laptime(), 0)
                laptime_valid = api.read.timing.last_laptime()
                pos_curr = api.read.lap.distance()
                gps_curr = api.read.vehicle.position_xyz()
                in_pits = api.read.vehicle.in_pits()
                speed = api.read.vehicle.speed()

                # Reset delta stint best if in pit
                if in_pits and delta_list_stint[-1][0] and speed < 0.1:
                    delta_list_stint = [DELTA_ZERO]
                    laptime_stint_best = 99999

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    laptime_last = lap_stime - last_lap_stime
                    if len(delta_list_curr) > 1:  # set end value
                        delta_list_curr.append((round6(pos_last + 10), round6(laptime_last)))
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
                        delta_list_curr.append((round6(pos_curr), round6(laptime_curr)))
                    pos_last = pos_curr  # reset last position
                    pos_synced = True

                # Validating 1s after passing finish line
                if validating:
                    timer = api.read.timing.elapsed() - validating
                    if 1 < timer <= 10:  # compare current time
                        if laptime_valid > 0 and abs(laptime_valid - laptime_last) < 2:
                            # Update delta best list
                            if laptime_last < laptime_best:
                                laptime_best = laptime_last
                                delta_list_best = delta_list_last.copy()
                                save_deltabest(delta_list_best, self.filepath, combo_id)
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
                    # Estimate distance
                    if pos_synced:
                        pos_estimate = pos_curr
                        pos_synced = False
                    else:
                        pos_estimate += moved_distance
                    # Update delta
                    delay_update = laptime_curr > 0.3
                    delta_best = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_best,
                        delay_update,
                    )
                    delta_last = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_last,
                        delay_update,
                    )
                    delta_session = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_session,
                        delay_update,
                    )
                    delta_stint = calc.delta_telemetry(
                        pos_estimate,
                        laptime_curr,
                        delta_list_stint,
                        delay_update,
                    )
                    # Smooth delta
                    delta_best_ema = exp_mov_avg(delta_best_ema, delta_best)
                    delta_last_ema = exp_mov_avg(delta_last_ema, delta_last)
                    delta_session_ema = exp_mov_avg(delta_session_ema, delta_session)
                    delta_stint_ema = exp_mov_avg(delta_stint_ema, delta_stint)
                    # Update driven distance
                    if moved_distance < 1500 * self.active_interval:
                        meters_driven += moved_distance

                # Output delta time data
                minfo.delta.deltaBest = delta_best_ema
                minfo.delta.deltaLast = delta_last_ema
                minfo.delta.deltaSession = delta_session_ema
                minfo.delta.deltaStint = delta_stint_ema
                minfo.delta.isValidLap = laptime_valid > 0
                minfo.delta.lapTimeCurrent = laptime_curr
                minfo.delta.lapTimeLast = laptime_last
                minfo.delta.lapTimeBest = laptime_best
                minfo.delta.lapTimeEstimated = laptime_best + delta_best_ema
                minfo.delta.lapTimeSession = laptime_session_best
                minfo.delta.lapTimeStint = laptime_stint_best
                minfo.delta.metersDriven = meters_driven

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    last_session_id = (combo_id, *session_id)
                    self.cfg.user.setting["cruise"]["meters_driven"] = int(meters_driven)
                    self.cfg.save()

    def set_smoothing_factor(self):
        """Set smoothing factor"""
        samples = min(max(self.mcfg["number_of_smoothing_samples"], 1), 100)
        factor = calc.ema_factor(samples)
        return factor


def load_deltabest(filepath:str, combo: str):
    """Load delta best & best laptime"""
    try:
        with open(f"{filepath}{combo}.csv", newline="", encoding="utf-8") as csvfile:
            temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
            temp_list_size = len(temp_list)
            # Validate data
            bestlist = val.delta_list(temp_list)
            laptime_best = bestlist[-1][1]
            # Save data if modified
            if temp_list_size != len(bestlist):
                save_deltabest(bestlist, filepath, combo)
    except (FileNotFoundError, IndexError, ValueError, TypeError):
        logger.info("MISSING: deltabest data")
        bestlist = [(99999,99999)]
        laptime_best = 99999
    return bestlist, laptime_best


def save_deltabest(dataset: list, filepath: str, combo: str):
    """Save delta best"""
    if len(dataset) >= 10:
        with open(f"{filepath}{combo}.csv", "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(dataset)
