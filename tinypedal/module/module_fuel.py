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
Fuel module
"""

import logging
import time
import threading
import csv
import math

from ..module_info import minfo
from ..const import PATH_FUEL
from ..api_control import api
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_fuel"
DELTA_ZERO = 0.0,0.0

logger = logging.getLogger(__name__)


class Realtime:
    """Fuel usage data"""
    module_name = MODULE_NAME
    filepath = PATH_FUEL

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
            logger.info("fuel module started")

    def __calculation(self):
        """Fuel calculation"""
        reset = False
        delayed_save = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                    recording = False
                    pittinglap = False
                    validating = False
                    delayed_save = False

                    combo_id = api.read.identify.combo()
                    delta_list_last = self.load_deltafuel(combo_id)
                    delta_list_curr = [DELTA_ZERO]  # distance, fuel used, laptime
                    delta_list_temp = [DELTA_ZERO]  # last lap temp
                    delta_fuel = 0  # delta fuel consumption compare to last lap

                    amount_start = 0  # start fuel reading
                    amount_last = 0  # last fuel reading
                    amount_need = 0  # total additional fuel need to finish race
                    amount_left = 0  # amount fuel left before pitting
                    used_curr = 0  # current lap fuel consumption
                    used_last = delta_list_last[-1][1]  # exclude first & pit lap
                    used_last_raw = delta_list_last[-1][1]  # raw usage
                    used_est = 0  # estimated fuel consumption, for calculation only
                    est_runlaps = 0  # estimate laps current fuel can last
                    est_runmins = 0  # estimate minutes current fuel can last
                    est_empty = 0  # estimate empty capacity at end of current lap
                    est_pits_late = 0  # estimate end-stint pit stop counts
                    est_pits_early = 0  # estimate end-lap pit stop counts
                    used_est_less = 0  # estimate fuel consumption for one less pit stop

                    laptime_last = delta_list_last[-1][2] # last laptime
                    last_lap_stime = -1  # last lap start time
                    laps_left = 0  # amount laps left at current lap distance
                    pos_last = 0  # last checked vehicle position
                    pos_estimate = 0  # calculated position
                    gps_last = [0,0,0]  # last global position

                # Read telemetry
                lap_stime = api.read.timing.start()
                laptime_curr = max(api.read.timing.current_laptime(), 0)
                laptime_valid = api.read.timing.last_laptime()
                time_left = api.read.session.remaining()
                amount_curr = api.read.vehicle.fuel()
                capacity = max(api.read.vehicle.tank_capacity(), 1)
                inpits = api.read.state.in_pits()
                ingarage = api.read.state.in_garage()
                pos_curr = api.read.lap.distance()
                gps_curr = api.read.vehicle.pos_xyz()
                lap_number = api.read.lap.number()
                lap_into = api.read.lap.percent()
                laps_max = api.read.lap.maximum()

                # Realtime fuel consumption
                if amount_last < amount_curr:
                    amount_last = amount_curr
                    amount_start = amount_curr
                elif amount_last > amount_curr:
                    used_curr += amount_last - amount_curr
                    amount_last = amount_curr

                pittinglap = bool(pittinglap + inpits)

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    if len(delta_list_curr) > 1 and not pittinglap:
                        delta_list_curr.append(  # set end value
                            (round(pos_last + 10, 6),
                             round(used_curr, 6),
                             round(lap_stime - last_lap_stime, 6))
                        )
                        delta_list_temp = delta_list_curr
                        validating = True
                    delta_list_curr = [DELTA_ZERO]  # reset
                    pos_last = pos_curr
                    used_last_raw = used_curr
                    used_curr = 0
                    recording = laptime_curr < 1
                    pittinglap = False
                last_lap_stime = lap_stime  # reset

                # 1 sec position distance check after new lap begins
                # Reset to 0 if higher than normal distance
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
                        laptime_curr > 0.3 and not ingarage,  # 300ms delay
                    )

                # Exclude first lap & pit in & out lap
                used_est = end_lap_consumption(
                    used_last, delta_fuel, 0 == pittinglap < lap_number)

                # Total refuel = laps left * last consumption - remaining fuel
                if api.read.state.is_lap_race():  # lap-type race
                    full_laps_left = laps_max - lap_number
                    laps_left = full_laps_left - lap_into
                    amount_need = laps_left * used_est - amount_curr
                elif laptime_last > 0:  # time-type race
                    # Make sure time into lap is not greater than last laptime
                    rel_lap_into = math.modf(laptime_curr / laptime_last)[0] * laptime_last
                    # Full laps left value counts from start line of current lap
                    full_laps_left = math.ceil((time_left + rel_lap_into) / laptime_last)
                    if laptime_curr > 0.2:  # 200ms delay check to avoid lap number desync
                        laps_left = max(full_laps_left - lap_into, 0)
                    amount_need = full_laps_left * used_est - used_curr - amount_curr

                amount_left = end_stint_fuel(
                    amount_curr, used_curr, used_est)

                est_runlaps = end_stint_laps(
                    amount_curr, used_est)

                est_runmins = est_runlaps * laptime_last / 60

                est_empty = end_lap_empty_capacity(
                    capacity, amount_curr + used_curr, used_last + delta_fuel)

                est_pits_late = end_stint_pit_counts(
                    amount_need, capacity - amount_left)

                est_pits_early = end_lap_pit_counts(
                    amount_need, est_empty, capacity - amount_left)

                used_est_less = less_pit_stop_consumption(
                    est_pits_late, capacity, amount_curr, laps_left)

                # Output fuel data
                minfo.fuel.tankCapacity = capacity
                minfo.fuel.amountFuelStart = amount_start
                minfo.fuel.amountFuelCurrent = amount_curr
                minfo.fuel.amountFuelNeeded = amount_need
                minfo.fuel.amountFuelBeforePitstop = amount_left
                minfo.fuel.lastLapFuelConsumption = used_last_raw
                minfo.fuel.estimatedFuelConsumption = used_last + delta_fuel
                minfo.fuel.estimatedLaps = est_runlaps
                minfo.fuel.estimatedMinutes = est_runmins
                minfo.fuel.estimatedEmptyCapacity = est_empty
                minfo.fuel.estimatedNumPitStopsEnd = est_pits_late
                minfo.fuel.estimatedNumPitStopsEarly = est_pits_early
                minfo.fuel.deltaFuelConsumption = delta_fuel
                minfo.fuel.oneLessPitFuelConsumption = used_est_less

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval
                    if delayed_save:
                        self.save_deltafuel(combo_id, delta_list_last)

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("fuel module closed")

    def load_deltafuel(self, combo):
        """Load last saved fuel consumption data"""
        try:
            with open(f"{self.filepath}{combo}.fuel",
                      newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                lastlist = list(deltaread)
                int(lastlist[-1][2])  # test read last laptime
                # Validate data
                if not val.delta_list(lastlist):
                    self.save_deltafuel(combo, lastlist)
        except (FileNotFoundError, IndexError, ValueError, TypeError):
            logger.info("no valid fuel data file found")
            lastlist = [(99999,0,0)]
        return lastlist

    def save_deltafuel(self, combo, listname):
        """Save fuel consumption data"""
        if len(listname) > 1:
            with open(f"{self.filepath}{combo}.fuel",
                      "w", newline="", encoding="utf-8") as csvfile:
                deltawrite = csv.writer(csvfile)
                deltawrite.writerows(listname)


def end_lap_consumption(used_last, delta_fuel, condition):
    """Estimate fuel consumption"""
    if condition:
        return used_last + delta_fuel
    return used_last


def end_stint_fuel(amount_curr, used_curr, used_est):
    """Estimate end-stint remaining fuel before pitting"""
    if used_est:
        # Total fuel at start of current lap
        total_fuel = amount_curr + used_curr
        # Fraction of lap counts * estimate fuel consumption
        return math.modf(total_fuel / used_est)[0] * used_est
    return 0


def end_stint_laps(amount_curr, used_est):
    """Estimate laps current fuel can last"""
    if used_est:
        # Laps = remaining fuel / estimate fuel consumption
        return amount_curr / used_est
    return 0


def end_lap_empty_capacity(capacity, fuel_remain, fuel_consumption):
    """Estimate empty capacity at end of current lap"""
    return capacity - fuel_remain + fuel_consumption


def end_stint_pit_counts(amount_need, capacity):
    """Estimate end-stint pit stop counts"""
    # Pit counts = required fuel / empty capacity
    return amount_need / capacity


def end_lap_pit_counts(amount_need, est_empty, capacity):
    """Estimate end-lap pit stop counts"""
    # Amount fuel can be added without exceeding capacity
    max_add_curr = min(amount_need, est_empty)
    # Pit count of current stint, 1 if exceed empty capacity or no empty space
    est_pits_curr = max_add_curr / est_empty if est_empty else 1
    # Pit counts after current stint
    est_pits_end = (amount_need - max_add_curr) / capacity
    # Total pit counts add together
    return est_pits_curr + est_pits_end


def less_pit_stop_consumption(est_pits_late, capacity, amount_curr, laps_left):
    """Estimate fuel consumption for one less pit stop"""
    if laps_left:
        pit_counts = math.ceil(est_pits_late) - 1
        # Consumption = total fuel / laps
        return (pit_counts * capacity + amount_curr) / laps_left
    return 0
