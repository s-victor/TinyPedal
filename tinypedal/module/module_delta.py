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

from functools import partial

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from ..validator import position_sync
from .. import calculation as calc
from .. import validator as val
from ..userfile.delta_best import load_delta_best_file, save_delta_best_file

DELTA_ZERO = 0.0,0.0
DELTA_DEFAULT = (DELTA_ZERO,)
MAGIC_NUM = 99999

round6 = partial(round, ndigits=6)


class Realtime(DataModule):
    """Delta time data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        userpath_delta_best = self.cfg.path.delta_best
        output = minfo.delta

        last_session_id = ("",-1,-1,-1)
        delta_list_session = DELTA_DEFAULT
        delta_list_stint = DELTA_DEFAULT
        laptime_session_best = MAGIC_NUM
        laptime_stint_best = MAGIC_NUM
        min_delta_distance = self.mcfg["minimum_delta_distance"]

        calc_ema_delta = partial(
            calc.exp_mov_avg,
            calc.ema_factor(min(max(self.mcfg["delta_smoothing_samples"], 1), 100))
        )
        calc_ema_laptime = partial(
            calc.exp_mov_avg,
            calc.ema_factor(min(max(self.mcfg["laptime_pace_samples"], 1), 20))
        )
        laptime_pace_margin = max(self.mcfg["laptime_pace_margin"], 0.1)
        gen_position_sync = position_sync()

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    recording = False
                    validating = 0
                    pit_lap = 0  # whether pit in or pit out lap

                    gen_position_sync.send(None)
                    combo_id = api.read.check.combo_id()
                    session_id = api.read.check.session_id()

                    # Reset delta session best if not same session
                    if not val.same_session(combo_id, session_id, last_session_id):
                        delta_list_session = DELTA_DEFAULT
                        laptime_session_best = MAGIC_NUM
                        last_session_id = (combo_id, *session_id)

                    delta_list_best, laptime_best = load_delta_best_file(
                        filepath=userpath_delta_best,
                        filename=combo_id,
                        defaults=(DELTA_DEFAULT, MAGIC_NUM)
                    )
                    output.deltaBestData = delta_list_best
                    delta_list_raw = [DELTA_ZERO]  # distance, laptime
                    delta_list_last = DELTA_DEFAULT  # last lap

                    delta_best_ema = 0.0
                    delta_last_ema = 0.0
                    delta_session_ema = 0.0
                    delta_stint_ema = 0.0

                    laptime_curr = 0.0  # current laptime
                    laptime_last = 0.0  # last laptime
                    laptime_pace = laptime_best  # avearge laptime pace

                    last_lap_stime = -1.0  # lap-start-time
                    pos_recorded = 0.0  # last recorded vehicle position
                    pos_last = 0.0  # last checked vehicle position
                    pos_estimate = 0.0  # estimated vehicle position
                    pos_synced = 0.0  # synced estimated vehicle position
                    pos_synced_last = 0.0  # last synced estimated vehicle position
                    is_pos_synced = False  # vehicle position synced with API
                    gps_last = (0.0,0.0,0.0)  # last global position
                    meters_driven = self.cfg.user.setting["cruise"]["meters_driven"]

                # Read telemetry
                lap_stime = api.read.timing.start()
                laptime_curr = max(api.read.timing.current_laptime(), 0)
                laptime_valid = api.read.timing.last_laptime()
                pos_curr = api.read.lap.distance()
                gps_curr = api.read.vehicle.position_xyz()
                in_pits = api.read.vehicle.in_pits()
                pit_lap = bool(pit_lap + in_pits)

                # Reset delta stint best if in pit and stopped
                if in_pits and delta_list_stint[-1][0] and api.read.vehicle.speed() < 0.1:
                    delta_list_stint = DELTA_DEFAULT
                    laptime_stint_best = MAGIC_NUM

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    laptime_last = lap_stime - last_lap_stime
                    if len(delta_list_raw) > 1:  # set end value
                        delta_list_raw.append((round6(pos_last + 10), round6(laptime_last)))
                        delta_list_last = tuple(delta_list_raw)
                        validating = api.read.timing.elapsed()
                    delta_list_raw = [DELTA_ZERO]  # reset
                    pos_last = pos_recorded = pos_curr
                    recording = laptime_curr < 1
                    pit_lap = 0
                last_lap_stime = lap_stime  # reset

                # 1 sec position distance check after new lap begins
                # Reset to 0 if higher than normal distance
                if 0 < laptime_curr < 1 and pos_curr > 300:
                    pos_last = pos_recorded = pos_curr = 0

                # Update if position value is different & positive
                if 0 <= pos_curr != pos_last:
                    if recording and pos_curr - pos_recorded >= min_delta_distance:
                        delta_list_raw.append((round6(pos_curr), round6(laptime_curr)))
                        pos_recorded = pos_curr
                    pos_last = pos_curr  # reset last position
                    is_pos_synced = True

                # Validating 1s after passing finish line
                if validating:
                    timer = api.read.timing.elapsed() - validating
                    if (1 < timer <= 10 and  # compare current time
                        laptime_valid > 0 and  # is valid laptime
                        int(laptime_valid - laptime_last) == 0):  # is matched laptime
                        # Update laptime pace
                        if not pit_lap:
                            # Set initial laptime if invalid, or align to faster laptime
                            if not 0 < laptime_pace < MAGIC_NUM or laptime_valid < laptime_pace:
                                laptime_pace = laptime_valid
                            else:
                                laptime_pace = min(
                                    calc_ema_laptime(laptime_pace, laptime_valid),
                                    laptime_pace + laptime_pace_margin,
                                )
                        # Update delta best list
                        if laptime_last < laptime_best:
                            laptime_best = laptime_last
                            output.deltaBestData = delta_list_best = delta_list_last
                            save_delta_best_file(
                                filepath=userpath_delta_best,
                                filename=combo_id,
                                dataset=delta_list_best,
                            )
                        # Update delta session best list
                        if laptime_last < laptime_session_best:
                            laptime_session_best = laptime_last
                            delta_list_session = delta_list_last
                        # Update delta stint best list
                        if laptime_last < laptime_stint_best:
                            laptime_stint_best = laptime_last
                            delta_list_stint = delta_list_last
                        validating = 0
                    elif timer > 10:  # switch off after 10s
                        validating = 0

                # Calc distance
                if gps_last != gps_curr:
                    moved_distance = calc.distance(gps_last, gps_curr)
                    gps_last = gps_curr
                    # Estimate distance into lap
                    if is_pos_synced:
                        pos_estimate = pos_curr
                        is_pos_synced = False
                    else:
                        pos_estimate += moved_distance
                    pos_synced = gen_position_sync.send(pos_estimate)
                    # Update driven distance
                    if moved_distance < 1500 * update_interval:
                        meters_driven += moved_distance

                # Calc delta
                if pos_synced_last != pos_synced:
                    pos_synced_last = pos_synced
                    delay_update = laptime_curr > 0.3
                    delta_best_raw = calc.delta_telemetry(
                        delta_list_best,
                        pos_synced,
                        laptime_curr,
                        delay_update,
                    )
                    delta_last_raw = calc.delta_telemetry(
                        delta_list_last,
                        pos_synced,
                        laptime_curr,
                        delay_update,
                    )
                    delta_session_raw = calc.delta_telemetry(
                        delta_list_session,
                        pos_synced,
                        laptime_curr,
                        delay_update,
                    )
                    delta_stint_raw = calc.delta_telemetry(
                        delta_list_stint,
                        pos_synced,
                        laptime_curr,
                        delay_update,
                    )
                    # Smooth delta
                    delta_best_ema = calc_ema_delta(delta_best_ema, delta_best_raw)
                    delta_last_ema = calc_ema_delta(delta_last_ema, delta_last_raw)
                    delta_session_ema = calc_ema_delta(delta_session_ema, delta_session_raw)
                    delta_stint_ema = calc_ema_delta(delta_stint_ema, delta_stint_raw)

                # Output delta time data
                output.deltaBest = delta_best_ema
                output.deltaLast = delta_last_ema
                output.deltaSession = delta_session_ema
                output.deltaStint = delta_stint_ema
                output.isValidLap = laptime_valid > 0
                output.lapTimeCurrent = laptime_curr
                output.lapTimeLast = laptime_last
                output.lapTimeBest = laptime_best
                output.lapTimeEstimated = laptime_best + delta_best_ema
                output.lapTimeSession = laptime_session_best
                output.lapTimeStint = laptime_stint_best
                output.lapTimePace = laptime_pace
                output.lapDistance = pos_synced
                output.metersDriven = meters_driven

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    last_session_id = (combo_id, *session_id)
                    self.cfg.user.setting["cruise"]["meters_driven"] = int(meters_driven)
                    self.cfg.save()
