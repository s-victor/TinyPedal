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
from collections import namedtuple

from ..const import PATH_FUEL
from ..readapi import info, chknm, state, combo_check
from .. import calculation as calc

MODULE_NAME = "module_fuel"

logger = logging.getLogger(__name__)


class Realtime:
    """Fuel usage data"""
    module_name = MODULE_NAME
    filepath = PATH_FUEL
    DataSet = namedtuple(
        "DataSet",
        [
        "Capacity",
        "AmountFuelStart",
        "AmountFuelCurrent",
        "AmountFuelNeeded",
        "AmountFuelBeforePitstop",
        "LastLapFuelConsumption",
        "EstimatedFuelConsumption",
        "EstimatedLaps",
        "EstimatedMinutes",
        "RequiredPitStops",
        "DeltaFuelConsumption",
        "OneLessPitFuelConsumption",
        ],
        defaults = ([0] * 12)
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
            logger.info("fuel module started")

    def __calculation(self):
        """Fuel calculation"""
        recording = False  # set fuel recording state
        verified = False  # additional check for conserving resources
        pittinglap = False  # set pitting lap state
        last_lap_stime = 0  # last lap start time
        amount_start = 0  # start fuel reading
        amount_last = 0  # last fuel reading
        amount_need = 0  # total additional fuel required to finish race
        amount_left = 0  # amount fuel left before pitting
        used_curr = 0  # current lap fuel consumption
        used_last = 0  # last lap fuel consumption
        used_est = 0  # estimated fuel consumption
        est_runlaps = 0  # estimate laps current fuel can last
        est_runmins = 0  # estimate minutes current fuel can last
        pit_required = 0  # minimum pit stops to finish race
        delta_list_curr = []  # distance vs fuel consumption list, current lap
        delta_list_last = []  # distance vs fuel consumption list, last lap
        last_time = 0  # last checked elapsed time
        pos_last = 0  # last checked player vehicle position
        pos_append = 0  # append last checked position with calc traveled dist
        delta_fuel = 0  # delta fuel consumption compare to last lap
        one_pit_save = 0  # target fuel consumption for one less pit stop
        laptime_last = 0 # last laptime

        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                (lap_stime, laps_total, laps_left, time_left, amount_curr, capacity,
                 inpits, pos_curr, elapsed_time, speed) = self.__telemetry()

                # Save switch
                if not verified:
                    verified = True
                    update_interval = active_interval  # shorter delay
                    combo_name = combo_check()
                    delta_list_last, used_last, laptime_last = self.load_deltafuel(combo_name)
                    last_lap_stime = lap_stime  # reset time stamp counter
                    pos_last = pos_curr

                # Start updating
                laptime_curr = max(elapsed_time - last_lap_stime, 0)  # current laptime

                if inpits == 1:
                    pittinglap = min(pittinglap + inpits, 1)

                # Realtime fuel consumption
                if amount_last < amount_curr:
                    amount_last = amount_curr
                    amount_start = amount_curr
                elif amount_last > amount_curr:
                    used_curr += amount_last - amount_curr
                    amount_last = amount_curr

                # Calc last lap fuel consumption
                if lap_stime > last_lap_stime:  # time stamp difference
                    # Update laptime during non-pitting lap
                    if delta_list_curr and not pittinglap:
                        laptime_last = lap_stime - last_lap_stime
                        used_last = used_curr
                        # Set end value
                        delta_list_curr.append((pos_last + 10, used_last, laptime_last))
                        delta_list_last = delta_list_curr

                    delta_list_curr = []  # reset current delta list
                    delta_list_curr.append((0.0, 0.0))  # set start value

                    recording = True  # activate fuel recording
                    last_lap_stime = lap_stime  # reset
                    pos_last = pos_curr  # set pos last
                    pittinglap = 0
                    used_curr = 0

                # Recording fuel data only from the beginning of a lap
                if recording:
                    # Update position if current dist value is diff & positive
                    if pos_curr != pos_last and pos_curr >= 0:
                        if pos_curr > pos_last:  # record if position is further away
                            delta_list_curr.append((pos_curr, used_curr))

                        pos_last = pos_curr  # reset last position
                        pos_append = pos_last  # reset initial position for appending

                # Update time difference & calculate additional traveled distance
                if elapsed_time != last_time:
                    delta_dist = speed * (elapsed_time - last_time)
                    pos_append += delta_dist
                    last_time = elapsed_time
                    index_lower, index_higher = calc.nearest_dist_index(
                                                pos_append, delta_list_last)
                    try:
                        if sum([delta_list_last[index_lower][0],
                                delta_list_last[index_lower][1],
                                delta_list_last[index_higher][0],
                                delta_list_last[index_higher][1]]) != 0:
                            delta_fuel = used_curr - calc.linear_interp(
                                                pos_append,
                                                delta_list_last[index_lower][0],
                                                delta_list_last[index_lower][1],
                                                delta_list_last[index_higher][0],
                                                delta_list_last[index_higher][1])
                    except IndexError:
                        delta_fuel = 0

                # Estimate fuel consumption
                # Wait 2s after cross finish line
                if elapsed_time - lap_stime > 2:
                    used_est = used_last + delta_fuel
                else:
                    used_est = used_last

                # Estimate laps current fuel can last
                if used_est:
                    # Total current fuel / last lap fuel consumption
                    est_runlaps = amount_curr / used_est
                    # Calculate from beginning of the lap
                    amount_left = math.modf((amount_curr + used_curr) / used_est)[0] * used_est
                else:
                    est_runlaps = 0
                    amount_left = 0

                # Estimate minutes current fuel can last
                est_runmins = est_runlaps * laptime_last / 60

                # Total additional fuel required to finish race
                if laps_total < 100000:  # detected lap type race
                    # Total laps left * last lap fuel consumption
                    amount_need = laps_left * used_est - amount_curr
                elif laptime_last > 0:  # detected time type race
                    # Time left / last laptime * last lap fuel consumption - total current fuel
                    full_laps_left = math.ceil((time_left + laptime_curr) / laptime_last)
                    laps_left = full_laps_left - laptime_curr / laptime_last
                    amount_need = full_laps_left * used_est - used_curr - amount_curr

                if capacity:
                    # Minimum required pitstops to finish race
                    pit_required = amount_need / capacity

                    one_pit_save = (
                        ((math.ceil(pit_required) - 1) * capacity + amount_curr) / laps_left)

                    # Output fuel data
                    self.output = self.DataSet(
                        Capacity = capacity,
                        AmountFuelStart = amount_start,
                        AmountFuelCurrent = amount_curr,
                        AmountFuelNeeded = amount_need,
                        AmountFuelBeforePitstop = amount_left,
                        LastLapFuelConsumption = used_last,
                        EstimatedFuelConsumption = used_est,
                        EstimatedLaps = est_runlaps,
                        EstimatedMinutes = est_runmins,
                        RequiredPitStops = pit_required,
                        DeltaFuelConsumption = delta_fuel,
                        OneLessPitFuelConsumption = one_pit_save,
                    )

            else:
                if verified:
                    recording = False  # disable fuel recording after exit track
                    verified = False
                    update_interval = idle_interval  # longer delay while inactive
                    delta_list_curr = []  # reset current delta list
                    amount_start = 0
                    amount_last = 0
                    used_curr = 0
                    pos_append = 0
                    if delta_list_last:
                        self.save_deltafuel(combo_name, delta_list_last)

            time.sleep(update_interval)

        self.set_output()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("fuel module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
        laps_total = chknm(info.LastScor.mScoringInfo.mMaxLaps)
        time_left = (chknm(info.LastScor.mScoringInfo.mEndET)
                     - chknm(info.LastScor.mScoringInfo.mCurrentET))
        amount_curr = chknm(info.syncedVehicleTelemetry().mFuel)
        capacity = chknm(info.syncedVehicleTelemetry().mFuelCapacity)
        inpits = chknm(info.syncedVehicleScoring().mInPits)
        pos_curr = chknm(info.syncedVehicleScoring().mLapDist)
        laps_left = (laps_total - chknm(info.syncedVehicleScoring().mTotalLaps)
                     - (pos_curr / max(chknm(info.LastScor.mScoringInfo.mLapDist), 1)))
        elapsed_time = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.z))
        return (lap_stime, laps_total, laps_left, time_left, amount_curr, capacity,
                inpits, pos_curr, elapsed_time, speed)

    def load_deltafuel(self, combo):
        """Load last saved fuel consumption data"""
        try:
            with open(f"{self.filepath}{combo}.fuel", newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                lastlist = list(deltaread)
                lastfuel = lastlist[-1][1]  # read fuel consumption
                lastlaptime = lastlist[-1][2]  # read last laptime
        except (FileNotFoundError, IndexError):
            lastlist = []
            lastfuel = 0
            lastlaptime = 0
        return lastlist, lastfuel, lastlaptime

    def save_deltafuel(self, combo, listname):
        """Save fuel consumption data"""
        with open(f"{self.filepath}{combo}.fuel", "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(listname)
