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
import math

from tinypedal.readapi import info, chknm, state
import tinypedal.calculation as calc


class FuelUsage:
    """Fuel usage data"""

    def __init__(self, config):
        self.cfg = config
        self.output_data = (0,0,0,0,0,0)
        self.running = False
        self.stopped = True

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        fuel_thread = threading.Thread(target=self.__calculation)
        fuel_thread.setDaemon(True)
        fuel_thread.start()
        print("fuel module started")

    def __calculation(self):
        """Fuel usage

        Run calculation separately.
        Saving & loading fuel data only on exit & enter.
        """
        recording = False  # set fuel recording state
        pittinglap = False  # set pitting lap state
        start_last = 0.0  # last lap start time
        amount_last = 0.0  # total fuel at end of last lap
        amount_need = 0.0  # total additional fuel required to finish race
        used_last = 0.0  # last lap fuel consumption
        est_runlaps = 0.0  # estimate laps current fuel can last
        est_runmins = 0.0  # estimate minutes current fuel can last
        pit_required = 0.0  # minimum pit stops to finish race
        laptime_last = self.cfg.setting_user["timing"]["last_laptime"]  # load last laptime
        fuel_unit = self.cfg.setting_user["fuel"]["fuel_unit"]  # load fuel unit setting
        update_delay = 0.4  # changeable update delay for conserving resources

        while self.running:
            if state():

                # Save switch
                if not recording:
                    recording = True
                    update_delay = 0.01  # shorter delay
                    used_last = self.cfg.setting_user["fuel"]["fuel_consumption"]

                (start_curr, laps_total, laps_left, time_left, amount_curr, capacity, inpits
                 ) = self.fuel_telemetry()

                # Start updating
                if inpits == 1:
                    pittinglap = min(pittinglap + inpits, 1)

                # Calc last lap fuel consumption
                if start_curr != start_last:  # time stamp difference
                    if start_curr > start_last:
                        # Only update laptime during non-pitting lap
                        if not pittinglap:
                            laptime_last = start_curr - start_last
                            # Calc last laptime from lap difference to bypass empty invalid laptime
                            if max(amount_last - amount_curr, 0) != 0:
                                used_last = max(amount_last - amount_curr, 0)
                    amount_last = amount_curr  # reset fuel counter
                    start_last = start_curr  # reset time stamp counter
                    pittinglap = 0

                # Estimate laps current fuel can last
                if used_last != 0:
                    # Total current fuel / last lap fuel consumption
                    est_runlaps = amount_curr / used_last
                else:
                    est_runlaps = 0

                # Estimate minutes current fuel can last
                est_runmins = est_runlaps * laptime_last / 60

                # Total additional fuel required to finish race
                if laps_total < 100000:  # detected lap type race
                    # Total laps left * last lap fuel consumption
                    amount_need = laps_left * used_last - amount_curr
                else:  # detected time type race
                    # Time left / last laptime * last lap fuel consumption - total current fuel
                    amount_need = (math.ceil(time_left / (laptime_last + 0.001) + 0.001)
                                        * used_last - amount_curr)

                # Minimum required pitstops to finish race
                pit_required = min(max(amount_need / (capacity + 0.001), 0), 99.99)

                # Unit conversion
                amount_curr_d = calc.conv_fuel(amount_curr, fuel_unit)
                amount_need_d = calc.conv_fuel(min(max(amount_need, -999.9), 999.9), fuel_unit)
                used_last_d = calc.conv_fuel(used_last, fuel_unit)

                # Output fuel data
                self.output_data = (amount_curr_d, amount_need_d, used_last_d,
                                    est_runlaps, est_runmins, pit_required)

            else:
                if recording:
                    self.cfg.setting_user["fuel"]["fuel_consumption"] = round(used_last, 6)
                    update_delay = 0.4  # longer delay while inactive

            time.sleep(update_delay)

        else:
            self.stopped = True
            print("fuel module closed")

    @staticmethod
    def fuel_telemetry():
        """Fuel Telemetry data"""
        start_curr = chknm(info.playersVehicleTelemetry().mLapStartET)
        laps_total = chknm(info.LastScor.mScoringInfo.mMaxLaps)
        laps_left = laps_total - chknm(info.playersVehicleScoring().mTotalLaps)
        time_left = (chknm(info.LastScor.mScoringInfo.mEndET)
                     - chknm(info.LastScor.mScoringInfo.mCurrentET))
        amount_curr = chknm(info.playersVehicleTelemetry().mFuel)
        capacity = chknm(info.playersVehicleTelemetry().mFuelCapacity)
        inpits = chknm(info.playersVehicleScoring().mInPits)
        return (start_curr, laps_total, laps_left, time_left, amount_curr,
                capacity, inpits)
