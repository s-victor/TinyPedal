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
Delta time module
"""

import time
import threading
import csv

from pyRfactor2SharedMemory.sharedMemoryAPI import Cbytestring2Python

from tinypedal.__init__ import info
import tinypedal.calculation as calc


class DeltaTime:
    """Delta time data"""

    def __init__(self):
        self.output_data = [0,0,0,0,0]

    def start(self):
        """Start calculation thread"""
        delta_thread = threading.Thread(target=self.calculation)
        delta_thread.setDaemon(True)
        delta_thread.start()

    def calculation(self):
        """Delta best & laptime

        Run calculation separately.
        Saving & loading delta data only on exit & enter.
        """
        recording = False  # set delta recording state
        verified = False  # additional check for conserving resources
        delta_list_curr = []  # distance vs time list, current lap
        delta_list_best = []  # distance vs time list, best lap
        delta_best = 0  # delta time compare to best laptime
        start_last = 0  # lap-start-time
        pos_last = 0  # last checked player vehicle position
        pos_append = 0  # append last checked position with calc traveled dist
        last_time = 0  # last checked elapsed time
        laptime_curr = 0  # current laptime
        laptime_last = 0  # last laptime
        laptime_best = 5999.999  # best laptime
        laptime_est = 0  # estimated current laptime
        combo_name = "unknown"  # current car & track combo
        update_delay = 0.5  # changeable update delay for conserving resources

        while True:
            if info.Rf2Ext.mInRealtimeFC:
                # Read combo & best laptime
                if not verified:
                    verified = True
                    update_delay = 0.01  # shorter delay
                    combo_name = combo_check()
                    delta_list_best, laptime_best = load_deltabest(combo_name)
                    start_last = 0  # reset last lap-start-time

                start_curr, elapsed_time, speed, track_length, pos_curr = telemetry()
                laptime_curr = elapsed_time - start_last  # current laptime

                if start_curr > start_last:  # difference of lap-start-time
                    laptime_last = start_curr - start_last

                    if delta_list_curr:  # non-empty list check
                        delta_list_curr.append((track_length, laptime_last))  # set end value

                        if laptime_last < laptime_best:
                            laptime_best = laptime_last
                            delta_list_best = delta_list_curr.copy()

                    delta_list_curr.clear()  # reset current delta list
                    delta_list_curr.append((0.0, 0.0))  # set start value
                    recording = True  # activate delta recording
                    start_last = start_curr  # reset lap-start-time
                    pos_last = pos_curr  # set pos last

                if recording:  # start recording
                    if pos_curr != pos_last:  # update pos if pos diff
                        if  pos_curr > pos_last:  # record if pos is further away
                            delta_list_curr.append((pos_curr, laptime_curr))

                        pos_last = pos_curr  # reset last pos
                        pos_append = pos_last  # reset initial pos for appending

                if elapsed_time != last_time:
                    delta_dist = speed * (elapsed_time - last_time)
                    pos_append += delta_dist
                    last_time = elapsed_time
                    index_lower, index_higher = calc.nearest_dist_index(
                                                pos_append, delta_list_best)
                    try:  # add 20ms error offset due to 50hz refresh rate limit
                        delta_best = laptime_curr + 0.02 - calc.linear_interp(
                                            pos_append,
                                            delta_list_best[index_lower][0],
                                            delta_list_best[index_lower][1],
                                            delta_list_best[index_higher][0],
                                            delta_list_best[index_higher][1])
                    except IndexError:
                        delta_best = 0

                laptime_est = laptime_best + delta_best
                self.output_data = [laptime_curr, laptime_last, laptime_best,
                                    laptime_est, delta_best]

            else:
                if recording:
                    recording = False  # disable delta recording after exit track
                    verified = False  # activate verification when enter track next time
                    update_delay = 0.5  # longer delay

                    if delta_list_best:  # save populated delta best list
                        save_deltabest(combo_name, delta_list_best)

                if delta_list_curr:
                    delta_list_curr.clear()  # reset current delta list

            time.sleep(update_delay)

    def output(self):
        """Output timing data"""
        return self.output_data


def telemetry():
    """Telemetry data"""
    plr_tele = info.playersVehicleTelemetry()

    start_curr = plr_tele.mLapStartET
    elapsed_time = plr_tele.mElapsedTime
    speed = calc.vel2speed(plr_tele.mLocalVel.x, plr_tele.mLocalVel.y, plr_tele.mLocalVel.z)
    track_length = info.Rf2Scor.mScoringInfo.mLapDist
    pos_curr = min(info.playersVehicleScoring().mLapDist, track_length)
    return start_curr, elapsed_time, speed, track_length, pos_curr


def combo_check():
    """Track & vehicle combo data"""
    name_class = Cbytestring2Python(info.playersVehicleScoring().mVehicleClass)
    name_track = Cbytestring2Python(info.Rf2Scor.mScoringInfo.mTrackName)
    return f"{name_track} - {name_class}"


def load_deltabest(combo):
    """Load delta best & best laptime"""
    try:
        with open(f"deltabest/{combo}.csv", newline="", encoding="utf-8") as csvfile:
            deltaread = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
            bestlist = list(deltaread)
            bestlap = bestlist[-1][1]  # read best laptime
    except (FileNotFoundError, IndexError):
        bestlist = []
        bestlap = 5999.999
    return bestlist, bestlap


def save_deltabest(combo, listname):
    """Save delta best"""
    with open(f"deltabest/{combo}.csv", "w", newline="", encoding="utf-8") as csvfile:
        deltawrite = csv.writer(csvfile)
        deltawrite.writerows(listname)
