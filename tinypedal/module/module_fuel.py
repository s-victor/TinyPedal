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

import logging
import csv

from ._base import DataModule
from ..module_info import minfo
from ..const import PATH_FUEL
from ..api_control import api
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_fuel"
DELTA_ZERO = 0.0,0.0

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Fuel usage data"""
    filepath = PATH_FUEL

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    combo_id = api.read.check.combo_id()
                    gen_calc_fuel = calc_data(
                        minfo.fuel, telemetry_fuel, self.filepath, combo_id, "fuel")
                    # Initial run to reset module output
                    next(gen_calc_fuel)
                    gen_calc_fuel.send(True)

                # Run calculation
                gen_calc_fuel.send(True)

                # Update consumption history
                if (minfo.history.consumption[0][2] != minfo.delta.lapTimeLast
                    > minfo.delta.lapTimeCurrent > 2):  # record 2s after pass finish line
                    minfo.history.consumption.appendleft((
                        api.read.lap.total_laps() - 1,
                        minfo.delta.isValidLap,
                        minfo.delta.lapTimeLast,
                        minfo.fuel.lastLapConsumption,
                        minfo.energy.lastLapConsumption,
                        minfo.hybrid.batteryDrainLast,
                        minfo.hybrid.batteryRegenLast))

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    # Trigger save check
                    gen_calc_fuel.send(False)


def telemetry_fuel():
    """Telemetry fuel"""
    capacity = max(api.read.vehicle.tank_capacity(), 1)
    amount_curr = api.read.vehicle.fuel()
    return capacity, amount_curr


def calc_data(output, telemetry_func, filepath, combo_id, extension):
    """Calculate data"""
    recording = False
    validating = False
    delayed_save = False
    pit_lap = False  # whether pit in or pit out lap

    delta_list_last, used_last, laptime_last = load_delta(filepath, combo_id, extension)
    delta_list_curr = [DELTA_ZERO]  # distance, fuel used, laptime
    delta_list_temp = [DELTA_ZERO]  # last lap temp
    delta_fuel = 0  # delta fuel consumption compare to last lap

    amount_start = 0  # start fuel reading
    amount_last = 0  # last fuel reading
    amount_need = 0  # total additional fuel need to finish race
    amount_left = 0  # amount fuel left before pitting
    used_curr = 0  # current lap fuel consumption
    used_last_raw = used_last  # raw usage
    used_est = 0  # estimated fuel consumption, for calculation only
    est_runlaps = 0  # estimate laps current fuel can last
    est_runmins = 0  # estimate minutes current fuel can last
    est_empty = 0  # estimate empty capacity at end of current lap
    est_pits_late = 0  # estimate end-stint pit stop counts
    est_pits_early = 0  # estimate end-lap pit stop counts
    used_est_less = 0  # estimate fuel consumption for one less pit stop

    last_lap_stime = -1  # last lap start time
    laps_left = 0  # amount laps left at current lap distance
    pos_last = 0  # last checked vehicle position
    pos_estimate = 0  # calculated position
    gps_last = [0,0,0]  # last global position

    while True:
        updating = yield None

        # Save check
        if not updating:
            if delayed_save:
                save_delta(delta_list_last, filepath, combo_id, extension)
            continue

        # Read telemetry
        capacity, amount_curr = telemetry_func()
        lap_stime = api.read.timing.start()
        laptime_curr = max(api.read.timing.current_laptime(), 0)
        laptime_valid = api.read.timing.last_laptime()
        time_left = api.read.session.remaining()
        in_garage = api.read.vehicle.in_garage()
        pos_curr = api.read.lap.distance()
        gps_curr = (api.read.vehicle.position_x(),
                    api.read.vehicle.position_y(),
                    api.read.vehicle.position_z())
        lap_number = api.read.lap.total_laps()
        lap_into = api.read.lap.progress()
        laps_max = api.read.lap.maximum()
        pit_lap = bool(pit_lap + api.read.vehicle.in_pits())

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
                    round(pos_last + 10, 6),
                    round(used_curr, 6),
                    round(lap_stime - last_lap_stime, 6)
                ))
                delta_list_temp = delta_list_curr
                validating = True
            delta_list_curr = [DELTA_ZERO]  # reset
            pos_last = pos_curr
            used_last_raw = used_curr
            used_curr = 0
            recording = laptime_curr < 1
            pit_lap = False
        last_lap_stime = lap_stime  # reset

        # Distance desync check at start of new lap, reset if higher than normal distance
        if 0 < laptime_curr < 1 and pos_curr > 300:
            pos_last = pos_curr = 0

        # Update if position value is different & positive
        if 0 <= pos_curr != pos_last:
            if recording and pos_curr > pos_last:  # position further
                delta_list_curr.append(  # keep 6 decimals
                    (round(pos_curr, 6), round(used_curr, 6))
                )
            pos_estimate = pos_last = pos_curr  # reset last position

        # Validating 1s after passing finish line
        if validating:
            if 0.2 < laptime_curr <= 3:  # compare current time
                if laptime_valid > 0:
                    used_last = used_last_raw
                    laptime_last = laptime_valid
                    delta_list_last = delta_list_temp
                    delta_list_temp = [DELTA_ZERO]
                    validating = False
                    delayed_save = True
            elif 3 < laptime_curr < 5:  # switch off after 3s
                validating = False

        # Calc delta
        if gps_last != gps_curr:
            pos_estimate += calc.distance(gps_last, gps_curr)
            gps_last = gps_curr
            delta_fuel = calc.delta_telemetry(
                pos_estimate,
                used_curr,
                delta_list_last,
                laptime_curr > 0.3 and not in_garage,  # 300ms delay
            )

        # Exclude first lap & pit in/out lap
        used_est = calc.end_lap_consumption(
            used_last, delta_fuel, 0 == pit_lap < lap_number)

        # Total refuel = laps left * last consumption - remaining fuel
        if api.read.session.lap_type():  # lap-type
            full_laps_left = calc.lap_type_full_laps_remain(
                laps_max, lap_number)
            laps_left = calc.lap_type_laps_remain(
                full_laps_left, lap_into)
            amount_need = calc.total_fuel_needed(
                laps_left, used_est, amount_curr)
        elif laptime_last > 0:  # time-type race
            full_laps_left = calc.time_type_full_laps_remain(
                lap_into, laptime_last, time_left)
            if laptime_curr > 0.2:
                laps_left = calc.time_type_laps_remain(
                    full_laps_left, lap_into)
            amount_need = calc.total_fuel_needed(
                laps_left, used_est, amount_curr)

        amount_left = calc.end_stint_fuel(
            amount_curr, used_curr, used_est)

        est_runlaps = calc.end_stint_laps(
            amount_curr, used_est)

        est_runmins = calc.end_stint_minutes(
            est_runlaps, laptime_last)

        est_empty = calc.end_lap_empty_capacity(
            capacity, amount_curr + used_curr, used_last + delta_fuel)

        est_pits_late = calc.end_stint_pit_counts(
            amount_need, capacity - amount_left)

        est_pits_early = calc.end_lap_pit_counts(
            amount_need, est_empty, capacity - amount_left)

        used_est_less = calc.one_less_pit_stop_consumption(
            est_pits_late, capacity, amount_curr, laps_left)

        output.capacity = capacity
        output.amountStart = amount_start
        output.amountCurrent = amount_curr
        output.amountNeeded = amount_need
        output.amountBeforePitstop = amount_left
        output.lastLapConsumption = used_last_raw
        output.estimatedConsumption = used_last + delta_fuel
        output.estimatedLaps = est_runlaps
        output.estimatedMinutes = est_runmins
        output.estimatedEmptyCapacity = est_empty
        output.estimatedNumPitStopsEnd = est_pits_late
        output.estimatedNumPitStopsEarly = est_pits_early
        output.deltaConsumption = delta_fuel
        output.oneLessPitConsumption = used_est_less


def save_delta(dataset: list, filepath: str, combo: str, extension: str):
    """Save consumption data"""
    if len(dataset) >= 10:
        with open(f"{filepath}{combo}.{extension}",
                    "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(dataset)


def load_delta(filepath: str, combo: str, extension: str):
    """Load consumption data"""
    try:
        with open(f"{filepath}{combo}.{extension}",
                    newline="", encoding="utf-8") as csvfile:
            temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
            temp_list_size = len(temp_list)
            # Validate data
            lastlist = val.delta_list(temp_list)
            used_last = lastlist[-1][1]
            laptime_last = lastlist[-1][2]
            # Save data if modified
            if temp_list_size != len(lastlist):
                save_delta(lastlist, filepath, combo, extension)
    except (FileNotFoundError, IndexError, ValueError, TypeError):
        logger.info("MISSING: %s data", extension)
        lastlist = [(99999,0,0)]
        used_last = 0
        laptime_last = 0
    return lastlist, used_last, laptime_last
