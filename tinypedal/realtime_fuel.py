#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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

import time
import threading
import csv
import math

from .const import PATH_FUEL
from .readapi import info, chknm, state, combo_check
from . import calculation as calc


class FuelUsage:
    """Fuel usage data"""
    filepath = PATH_FUEL

    def __init__(self, config):
        self.cfg = config
        self.output_data = (0,0,0,0,0,0)
        self.running = False
        self.stopped = True

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        self.thread = threading.Thread(target=self.__calculation)
        self.thread.daemon=True
        self.thread.start()
        print("fuel module started")

    def __calculation(self):
        """Fuel usage

        Run calculation separately.
        Saving & loading fuel data only on exit & enter.
        """
        recording = False  # set fuel recording state
        verified = False  # additional check for conserving resources
        pittinglap = False  # set pitting lap state
        last_lap_stime = 0  # last lap start time
        amount_last = 0.0  # last fuel reading
        amount_need = 0.0  # total additional fuel required to finish race
        used_curr = 0.0  # current lap fuel consumption
        used_last = 0.0  # last lap fuel consumption
        used_est = 0.0  # estimated fuel consumption
        est_runlaps = 0.0  # estimate laps current fuel can last
        est_runmins = 0.0  # estimate minutes current fuel can last
        pit_required = 0.0  # minimum pit stops to finish race
        delta_list_curr = []  # distance vs fuel consumption list, current lap
        delta_list_last = []  # distance vs fuel consumption list, last lap
        last_time = 0  # last checked elapsed time
        pos_last = 0  # last checked player vehicle position
        pos_append = 0  # append last checked position with calc traveled dist
        delta_fuel = 0  # delta fuel consumption compare to last lap

        laptime_last = 0 # last laptime
        update_delay = 0.4  # changeable update delay for conserving resources

        while self.running:
            if state():

                (lap_stime, laps_total, laps_left, time_left, amount_curr, capacity,
                 inpits, pos_curr, elapsed_time, speed) = self.__telemetry()

                # Save switch
                if not verified:
                    verified = True
                    update_delay = 0.01  # shorter delay
                    combo_name = combo_check()
                    delta_list_last, used_last, laptime_last = self.load_deltafuel(combo_name)
                    last_lap_stime = lap_stime  # reset time stamp counter
                    pos_last = pos_curr

                # Start updating
                if inpits == 1:
                    pittinglap = min(pittinglap + inpits, 1)

                # Realtime fuel consumption
                if amount_last < amount_curr:
                    amount_last = amount_curr
                elif amount_last > amount_curr:
                    used_curr += amount_last - amount_curr
                    amount_last = amount_curr

                # Calc last lap fuel consumption
                if lap_stime > last_lap_stime:  # time stamp difference
                    # Update laptime during non-pitting lap
                    if delta_list_curr and not pittinglap:
                        laptime_last = lap_stime - last_lap_stime
                        used_last = used_curr
                        delta_list_curr.append((pos_last + 10, used_last, laptime_last))  # set end value
                        delta_list_last = delta_list_curr.copy()

                    delta_list_curr.clear()  # reset current delta list
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
                if elapsed_time - lap_stime > 2:  # wait 2s after cross finish line
                    used_est = used_last + delta_fuel
                else:
                    used_est = used_last

                # Estimate laps current fuel can last
                if used_est:
                    # Total current fuel / last lap fuel consumption
                    est_runlaps = amount_curr / used_est
                else:
                    est_runlaps = 0

                # Estimate minutes current fuel can last
                est_runmins = est_runlaps * laptime_last / 60

                # Total additional fuel required to finish race
                if laps_total < 100000:  # detected lap type race
                    # Total laps left * last lap fuel consumption
                    amount_need = laps_left * used_est - amount_curr
                elif laptime_last > 0:  # detected time type race
                    # Time left / last laptime * last lap fuel consumption - total current fuel
                    amount_need = (math.ceil(time_left / laptime_last) * used_est - amount_curr)

                # Minimum required pitstops to finish race
                pit_required = amount_need / max(capacity, 1)

                # Unit conversion
                amount_curr_d = self.fuel_units(amount_curr)
                amount_need_d = self.fuel_units(amount_need)
                used_est_d = self.fuel_units(used_est)

                # Output fuel data
                self.output_data = (amount_curr_d, amount_need_d, used_est_d,
                                    est_runlaps, est_runmins, pit_required)

            else:
                if verified:
                    recording = False  # disable fuel recording after exit track
                    verified = False
                    update_delay = 0.4  # longer delay while inactive
                    delta_list_curr.clear()  # reset current delta list
                    used_curr = 0
                    pos_append = 0
                    if delta_list_last:
                        self.save_deltafuel(combo_name, delta_list_last)

            time.sleep(update_delay)

        self.stopped = True
        print("fuel module closed")

    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.setting_user["fuel"]["fuel_unit"] != "0":
            return calc.liter2gallon(fuel)
        return fuel

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
        laps_total = chknm(info.LastScor.mScoringInfo.mMaxLaps)
        laps_left = laps_total - chknm(info.syncedVehicleScoring().mTotalLaps)
        time_left = (chknm(info.LastScor.mScoringInfo.mEndET)
                     - chknm(info.LastScor.mScoringInfo.mCurrentET))
        amount_curr = chknm(info.syncedVehicleTelemetry().mFuel)
        capacity = chknm(info.syncedVehicleTelemetry().mFuelCapacity)
        inpits = chknm(info.syncedVehicleScoring().mInPits)
        pos_curr = chknm(info.syncedVehicleScoring().mLapDist)
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
