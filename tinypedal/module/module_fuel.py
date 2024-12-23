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
Fuel module
"""

from __future__ import annotations
from functools import partial
from math import ceil, floor
from collections.abc import Callable

from ._base import DataModule
from ..module_info import minfo, FuelInfo, ConsumptionDataSet
from ..api_control import api
from .. import calculation as calc
from ..userfile.fuel_delta import load_fuel_delta_file, save_fuel_delta_file

DELTA_ZERO = 0.0,0.0
DELTA_DEFAULT = [DELTA_ZERO]

round6 = partial(round, ndigits=6)


class Realtime(DataModule):
    """Fuel usage data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        userpath_fuel_delta = self.cfg.path.fuel_delta

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    combo_id = api.read.check.combo_id()
                    gen_calc_fuel = calc_data(
                        output=minfo.fuel,
                        telemetry_func=telemetry_fuel,
                        filepath=userpath_fuel_delta,
                        filename=combo_id,
                        extension=".fuel",
                    )
                    # Initial run to reset module output
                    next(gen_calc_fuel)
                    gen_calc_fuel.send(True)

                # Run calculation
                gen_calc_fuel.send(True)

                # Update consumption history
                if (minfo.history.consumption[0][2] != minfo.delta.lapTimeLast
                    > minfo.delta.lapTimeCurrent > 2):  # record 2s after pass finish line
                    minfo.history.consumption.appendleft(
                        ConsumptionDataSet(
                            api.read.lap.completed_laps() - 1,
                            minfo.delta.isValidLap,
                            minfo.delta.lapTimeLast,
                            minfo.fuel.lastLapConsumption,
                            minfo.energy.lastLapConsumption,
                            minfo.hybrid.batteryDrainLast,
                            minfo.hybrid.batteryRegenLast,
                        )
                    )

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    # Trigger save check
                    gen_calc_fuel.send(False)


def telemetry_fuel() -> tuple[float, float]:
    """Telemetry fuel"""
    capacity = max(api.read.vehicle.tank_capacity(), 1)
    amount_curr = api.read.vehicle.fuel()
    return capacity, amount_curr


def calc_data(
    output: FuelInfo, telemetry_func: Callable, filepath: str, filename: str, extension: str):
    """Calculate data"""
    recording = False
    delayed_save = False
    validating = 0
    pit_lap = 0  # whether pit in or pit out lap

    delta_list_last, used_last, laptime_last = load_fuel_delta_file(
        filepath=filepath,
        filename=filename,
        extension=extension,
        defaults=(DELTA_DEFAULT, 0, 0)
    )
    delta_list_curr = [DELTA_ZERO]  # distance, fuel used, laptime
    delta_list_temp = DELTA_DEFAULT  # last lap temp
    delta_fuel = 0.0  # delta fuel consumption compare to last lap

    amount_start = 0.0  # start fuel reading
    amount_last = 0.0  # last fuel reading
    amount_need_abs = 0.0  # total fuel (absolute) need to finish race
    amount_need_rel = 0.0  # total additional fuel (relative) need to finish race
    amount_end = 0.0  # amount fuel left at the end of stint before pitting
    used_curr = 0.0  # current lap fuel consumption
    used_last_raw = used_last  # raw usage
    used_est = 0.0  # estimated fuel consumption, for calculation only
    est_runlaps = 0.0  # estimate laps current fuel can last
    est_runmins = 0.0  # estimate minutes current fuel can last
    est_empty = 0.0  # estimate empty capacity at end of current lap
    est_pits_late = 0.0  # estimate end-stint pit stop counts
    est_pits_early = 0.0  # estimate end-lap pit stop counts
    used_est_less = 0.0  # estimate fuel consumption for one less pit stop

    last_lap_stime = -1.0  # last lap start time
    laps_left = 0.0  # amount laps left at current lap distance
    end_timer_laps_left = 0.0  # amount laps left from start of current lap to end of race timer
    pos_last = 0.0  # last checked vehicle position
    pos_estimate = 0.0  # calculated position
    pos_synced = False  # whether estimated position synced
    gps_last = (0.0,0.0,0.0)  # last global position

    while True:
        updating = yield None

        # Save check
        if not updating:
            if delayed_save:
                save_fuel_delta_file(
                    filepath=filepath,
                    filename=filename,
                    extension=extension,
                    dataset=delta_list_last,
                )
            continue

        # Read telemetry
        capacity, amount_curr = telemetry_func()
        lap_stime = api.read.timing.start()
        laptime_curr = max(api.read.timing.current_laptime(), 0)
        time_left = api.read.session.remaining()
        in_garage = api.read.vehicle.in_garage()
        pos_curr = api.read.lap.distance()
        gps_curr = api.read.vehicle.position_xyz()
        laps_done = api.read.lap.completed_laps()
        lap_into = api.read.lap.progress()
        pit_lap = bool(pit_lap + api.read.vehicle.in_pits())
        laptime_last = minfo.delta.lapTimePace

        # Realtime fuel consumption
        if amount_last < amount_curr:
            amount_last = amount_curr
            amount_start = amount_curr
        elif amount_last > amount_curr:
            used_curr += amount_last - amount_curr
            amount_last = amount_curr

        # Lap start & finish detection
        if lap_stime > last_lap_stime != -1:
            if len(delta_list_curr) > 1 and not pit_lap:
                delta_list_curr.append((  # set end value
                    round6(pos_last + 10),
                    round6(used_curr),
                    round6(lap_stime - last_lap_stime)
                ))
                delta_list_temp = delta_list_curr
                validating = api.read.timing.elapsed()
            delta_list_curr = [DELTA_ZERO]  # reset
            pos_last = pos_curr
            used_last_raw = used_curr
            used_curr = 0
            recording = laptime_curr < 1
            pit_lap = 0
        last_lap_stime = lap_stime  # reset

        # Distance desync check at start of new lap, reset if higher than normal distance
        if 0 < laptime_curr < 1 and pos_curr > 300:
            pos_last = pos_curr = 0

        # Update if position value is different & positive
        if 0 <= pos_curr != pos_last:
            if recording and pos_curr > pos_last:  # position further
                delta_list_curr.append((round6(pos_curr), round6(used_curr)))
            pos_last = pos_curr  # reset last position
            pos_synced = True

        # Validating 1s after passing finish line
        if validating:
            timer = api.read.timing.elapsed() - validating
            if (0.3 < timer <= 3 and  # compare current time
                api.read.timing.last_laptime() > 0):  # is valid laptime
                used_last = used_last_raw
                delta_list_last = delta_list_temp
                delta_list_temp = DELTA_DEFAULT
                delayed_save = True
                validating = 0
            elif timer > 3:  # switch off after 3s
                validating = 0

        # Calc delta
        if gps_last != gps_curr:
            if pos_synced:
                pos_estimate = pos_curr
                pos_synced = False
            else:
                pos_estimate += calc.distance(gps_last, gps_curr)
            gps_last = gps_curr
            # Update delta
            delta_fuel = calc.delta_telemetry(
                delta_list_last,
                pos_estimate,
                used_curr,
                laptime_curr > 0.3 and not in_garage,  # 300ms delay
            )

        # Exclude first lap & pit in/out lap
        used_est = calc.end_lap_consumption(
            used_last, delta_fuel, 0 == pit_lap < laps_done)

        # Total refuel = laps left * last consumption - remaining fuel
        if api.read.session.lap_type():  # lap-type
            full_laps_left = calc.lap_type_full_laps_remain(
                api.read.lap.maximum(), laps_done)
            laps_left = calc.lap_type_laps_remain(
                full_laps_left, lap_into)
        elif laptime_last > 0:  # time-type race
            end_timer_laps_left = calc.end_timer_laps_remain(
                lap_into, laptime_last, time_left)
            full_laps_left = ceil(end_timer_laps_left)
            laps_left = calc.time_type_laps_remain(
                full_laps_left, lap_into)

        amount_need_abs = laps_left * used_est

        amount_need_rel = amount_need_abs - amount_curr

        amount_end = calc.end_stint_fuel(
            amount_curr, used_curr, used_est)

        est_runlaps = calc.end_stint_laps(
            amount_curr, used_est)

        est_runmins = calc.end_stint_minutes(
            est_runlaps, laptime_last)

        est_empty = calc.end_lap_empty_capacity(
            capacity, amount_curr + used_curr, used_last + delta_fuel)

        est_pits_late = calc.end_stint_pit_counts(
            amount_need_rel, capacity - amount_end)

        est_pits_early = calc.end_lap_pit_counts(
            amount_need_rel, est_empty, capacity - amount_end)

        used_est_less = calc.one_less_pit_stop_consumption(
            est_pits_late, capacity, amount_curr, laps_left)

        output.capacity = capacity
        output.amountStart = amount_start
        output.amountCurrent = amount_curr
        output.amountUsedCurrent = used_curr
        output.amountEndStint = amount_end
        output.neededRelative = amount_need_rel
        output.neededAbsolute = amount_need_abs
        output.lastLapConsumption = used_last_raw
        output.lastLapValidConsumption = used_last
        output.estimatedConsumption = used_last + delta_fuel
        output.estimatedValidConsumption = used_est
        output.estimatedLaps = est_runlaps
        output.estimatedMinutes = est_runmins
        output.estimatedEmptyCapacity = est_empty
        output.estimatedNumPitStopsEnd = est_pits_late
        output.estimatedNumPitStopsEarly = est_pits_early
        output.deltaConsumption = delta_fuel
        output.oneLessPitConsumption = used_est_less
