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
DELTA_ZERO = 0.0,0.0

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
        "EstimatedEmptyCapacity",
        "EstimatedNumPitStopsEnd",
        "EstimatedNumPitStopsEarly",
        "DeltaFuelConsumption",
        "OneLessPitFuelConsumption",
        ],
        defaults = ([0] * 14)
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
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                (lap_stime, laptime_curr, lastlap_valid, time_left,
                 amount_curr, capacity, inpits, ingarage, pos_curr,
                 gps_curr, lap_number, lap_into, laps_max) = self.__telemetry()

                # Reset data
                if not reset:
                    reset = True
                    update_interval = active_interval  # shorter delay

                    recording = False
                    pittinglap = False
                    validating = False

                    combo_name = combo_check()
                    delta_list_last = self.load_deltafuel(combo_name)
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
                    used_est_less = 0  # estimate fuel consumption for one less pit stop

                    laptime_last = delta_list_last[-1][2] # last laptime
                    last_lap_stime = lap_stime  # last lap start time
                    laps_left = 0  # amount laps left at current lap distance
                    pos_last = 0  # last checked vehicle position
                    pos_estimate = 0  # calculated position
                    gps_last = [0,0,0]  # last global position

                # Realtime fuel consumption
                if amount_last < amount_curr:
                    amount_last = amount_curr
                    amount_start = amount_curr
                elif amount_last > amount_curr:
                    used_curr += amount_last - amount_curr
                    amount_last = amount_curr

                pittinglap = bool(pittinglap + inpits)

                # Lap start & finish detection
                if lap_stime > last_lap_stime:
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
                        if lastlap_valid > 0:
                            used_last = used_last_raw
                            laptime_last = lastlap_valid
                            delta_list_last = delta_list_temp
                            delta_list_temp = [DELTA_ZERO]
                            validating = False
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
                        laptime_curr > 0.2 and not ingarage,  # 200ms delay
                    )

                # Estimate fuel consumption for calculation
                # Exclude first lap & pit in & out lap
                if 0 == pittinglap < lap_number:
                    used_est = used_last + delta_fuel
                else:
                    used_est = used_last

                # Estimate laps current fuel can last
                if used_est:
                    # Total current fuel / last lap fuel consumption
                    est_runlaps = amount_curr / used_est
                    # Total remaining fuel at start of lap = current fuel + current used fuel
                    # Fraction of lap numbers * estimate fuel consumption
                    amount_left = math.modf((amount_curr + used_curr) / used_est)[0] * used_est
                else:
                    est_runlaps = 0
                    amount_left = 0

                # Estimate minutes current fuel can last
                est_runmins = est_runlaps * laptime_last / 60

                # Total refuel = laps left * last consumption - remaining fuel
                if laps_max < 99999:  # lap-type race
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

                # Estimate empty capacity at end of current lap
                est_empty = capacity - amount_curr - used_curr + used_last + delta_fuel

                # Estimate pit stop counts when pitting at end of current stint
                est_pits_end = amount_need / (capacity - amount_left)

                # Estimate pit stop counts when pitting at end of current lap
                if amount_need > est_empty:  # exceed capacity
                    est_pits_early = 1 + (amount_need - est_empty) / (capacity - amount_left)
                else:
                    est_pits_early = est_pits_end

                if laps_left:
                    used_est_less = (
                        ((math.ceil(est_pits_end) - 1) * capacity + amount_curr) / laps_left)
                else:
                    used_est_less = 0

                # Output fuel data
                self.output = self.DataSet(
                    Capacity = capacity,
                    AmountFuelStart = amount_start,
                    AmountFuelCurrent = amount_curr,
                    AmountFuelNeeded = amount_need,
                    AmountFuelBeforePitstop = amount_left,
                    LastLapFuelConsumption = used_last_raw,
                    EstimatedFuelConsumption = used_last + delta_fuel,
                    EstimatedLaps = est_runlaps,
                    EstimatedMinutes = est_runmins,
                    EstimatedEmptyCapacity = est_empty,
                    EstimatedNumPitStopsEnd = est_pits_end,
                    EstimatedNumPitStopsEarly = est_pits_early,
                    DeltaFuelConsumption = delta_fuel,
                    OneLessPitFuelConsumption = used_est_less,
                )

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval  # longer delay while inactive
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
        laptime_curr = max(chknm(info.syncedVehicleTelemetry().mElapsedTime) - lap_stime, 0)
        lastlap_valid = chknm(info.syncedVehicleScoring().mLastLapTime)
        time_left = (chknm(info.LastScor.mScoringInfo.mEndET)
                     - chknm(info.LastScor.mScoringInfo.mCurrentET))
        amount_curr = chknm(info.syncedVehicleTelemetry().mFuel)
        capacity = max(chknm(info.syncedVehicleTelemetry().mFuelCapacity), 1)
        inpits = chknm(info.syncedVehicleScoring().mInPits)
        ingarage = chknm(info.syncedVehicleScoring().mInGarageStall)
        pos_curr = chknm(info.syncedVehicleScoring().mLapDist)
        gps_curr = (chknm(info.syncedVehicleTelemetry().mPos.x),
                    chknm(info.syncedVehicleTelemetry().mPos.y),
                    chknm(info.syncedVehicleTelemetry().mPos.z))
        lap_number = chknm(info.syncedVehicleScoring().mTotalLaps)
        lap_into = max(pos_curr / max(chknm(info.LastScor.mScoringInfo.mLapDist), 1), 0)
        laps_max = chknm(info.LastScor.mScoringInfo.mMaxLaps)
        return (lap_stime, laptime_curr, lastlap_valid, time_left,
                amount_curr, capacity, inpits, ingarage, pos_curr,
                gps_curr, lap_number, lap_into, laps_max)

    def load_deltafuel(self, combo):
        """Load last saved fuel consumption data"""
        try:
            with open(f"{self.filepath}{combo}.fuel",
                      newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                lastlist = list(deltaread)
                lastlist[-1][1]  # test read fuel consumption
                lastlist[-1][2]  # test read last laptime
        except (FileNotFoundError, IndexError, ValueError):
            logger.info("no valid fuel data file found")
            lastlist = [(0,0,0)]
        return lastlist

    def save_deltafuel(self, combo, listname):
        """Save fuel consumption data"""
        if len(listname) > 1:
            with open(f"{self.filepath}{combo}.fuel",
                      "w", newline="", encoding="utf-8") as csvfile:
                deltawrite = csv.writer(csvfile)
                deltawrite.writerows(listname)
