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
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                (lap_stime, laps_total, laps_left, time_left, amount_curr, capacity,
                 inpits, pos_curr, elapsed_time, gps_curr) = self.__telemetry()

                # Reset data
                if not reset:
                    reset = True
                    update_interval = active_interval  # shorter delay

                    recording = False
                    lap_diff = False
                    pittinglap = False

                    combo_name = combo_check()
                    delta_list_curr = [DELTA_ZERO]  # distance, fuel used, laptime
                    delta_list_last = self.load_deltafuel(combo_name)
                    delta_fuel = 0  # delta fuel consumption compare to last lap

                    amount_start = 0  # start fuel reading
                    amount_last = 0  # last fuel reading
                    amount_need = 0  # total additional fuel to finish race
                    amount_left = 0  # amount fuel left before pitting
                    used_curr = 0  # current lap fuel consumption
                    used_last = delta_list_last[-1][1]  # last lap fuel consumption
                    used_est = 0  # estimated fuel consumption
                    est_runlaps = 0  # estimate laps current fuel can last
                    est_runmins = 0  # estimate minutes current fuel can last
                    pit_required = 0  # minimum pit stops to finish race
                    pit_one_less = 0  # target fuel consumption for one less pit stop

                    laptime_last = delta_list_last[-1][2] # last laptime
                    last_lap_stime = lap_stime  # last lap start time
                    pos_last = 0  # last checked vehicle position
                    pos_calc = 0  # calculated position
                    gps_last = [0,0,0]  # last global position

                # Realtime fuel consumption
                if amount_last < amount_curr:
                    amount_last = amount_curr
                    amount_start = amount_curr
                elif amount_last > amount_curr:
                    used_curr += amount_last - amount_curr
                    amount_last = amount_curr

                # Lap start & finish detection
                if lap_stime > last_lap_stime:
                    laptime_last = lap_stime - last_lap_stime
                    lap_diff = True
                else:
                    lap_diff = False
                last_lap_stime = lap_stime  # reset
                laptime_curr = max(elapsed_time - last_lap_stime, 0)
                pittinglap = bool(pittinglap + inpits)

                if lap_diff:
                    if len(delta_list_curr) > 1 and not pittinglap:
                        used_last = used_curr
                        delta_list_curr.append(  # set end value
                            (round(pos_last + 10, 6), round(used_last, 6), round(laptime_last, 6))
                        )
                        delta_list_last = delta_list_curr
                    delta_list_curr = [DELTA_ZERO]  # reset
                    pos_last = pos_curr
                    recording = True if laptime_curr < 1 else False
                    pittinglap = False
                    used_curr = 0

                # Update if position value is different & positive
                if 0 <= pos_curr != pos_last:
                    if recording and pos_curr > pos_last:  # position further
                        delta_list_curr.append(  # keep 6 decimals
                            (round(pos_curr, 6), round(used_curr, 6))
                        )
                    pos_last = pos_curr  # reset last position
                    pos_calc = pos_last  # reset calc position

                # Calc delta
                if gps_last != gps_curr:
                    pos_calc += calc.distance_xyz(gps_last, gps_curr)
                    gps_last = gps_curr
                    delta_fuel = calc.delta_telemetry(
                        pos_calc,
                        used_curr,
                        delta_list_last,
                        laptime_curr > 0.2 and not pittinglap,  # 200ms delay
                    )

                # Estimate fuel consumption
                used_est = used_last + delta_fuel

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
                if laps_total < 99999:  # detected lap type race
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
                    pit_one_less = (
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
                    OneLessPitFuelConsumption = pit_one_less,
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
        gps_curr = (chknm(info.syncedVehicleTelemetry().mPos.x),
                    chknm(info.syncedVehicleTelemetry().mPos.y),
                    chknm(info.syncedVehicleTelemetry().mPos.z))
        return (lap_stime, laps_total, laps_left, time_left, amount_curr, capacity,
                inpits, pos_curr, elapsed_time, gps_curr)

    def load_deltafuel(self, combo):
        """Load last saved fuel consumption data"""
        try:
            with open(f"{self.filepath}{combo}.fuel",
                      newline="", encoding="utf-8") as csvfile:
                deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
                lastlist = list(deltaread)
                lastlist[-1][1]  # test read fuel consumption
                lastlist[-1][2]  # test read last laptime
        except (FileNotFoundError, IndexError):
            lastlist = [(0,0,0)]
        return lastlist

    def save_deltafuel(self, combo, listname):
        """Save fuel consumption data"""
        if len(listname) > 1:
            with open(f"{self.filepath}{combo}.fuel",
                      "w", newline="", encoding="utf-8") as csvfile:
                deltawrite = csv.writer(csvfile)
                deltawrite.writerows(listname)
