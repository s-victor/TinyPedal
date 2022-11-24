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
Delta module
"""

import time
import threading
import csv

from tinypedal.readapi import info, chknm, cs2py, state, combo_check
import tinypedal.calculation as calc


class DeltaTime:
    """Delta time data"""

    def __init__(self, config):
        self.cfg = config
        self.output_data = (0,0,0,0,0)
        self.meters_driven = 0
        self.running = False
        self.stopped = True

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        delta_thread = threading.Thread(target=self.__calculation)
        delta_thread.setDaemon(True)
        delta_thread.start()
        print("delta module started")

    def __calculation(self):
        """Delta best & laptime

        Run calculation separately.
        Saving & loading delta data only on exit & enter.
        """
        recording = False  # set delta recording state
        verified = False  # additional check for conserving resources
        validating = False  # validate last laptime after cross finish line

        self.meters_driven = self.cfg.setting_user["cruise"]["meters_driven"]
        delta_list_curr = []  # distance vs time list, current lap
        delta_list_last = []  # distance vs time list, last lap, used for verification only
        delta_list_best = []  # distance vs time list, best lap
        delta_best = 0  # delta time compare to best laptime
        start_last = 0  # lap-start-time
        pos_last = 0  # last checked player vehicle position
        pos_append = 0  # append last checked position with calc traveled dist
        gps_last = [0,0,0]  # last global position
        last_time = 0  # last checked elapsed time
        laptime_curr = 0  # current laptime
        laptime_last = 0  # last laptime
        laptime_best = 5999.999  # best laptime
        laptime_est = 0  # estimated current laptime
        combo_name = "unknown"  # current car & track combo
        update_delay = 0.4  # changeable update delay for conserving resources

        while self.running:
            if state():

                (start_curr, elapsed_time, lastlap_check, speed, pos_curr, gps_curr, game_phase
                 ) = self.delta_telemetry()

                # Read combo & best laptime
                if not verified:
                    verified = True
                    update_delay = 0.01  # shorter delay
                    combo_name = combo_check()
                    delta_list_best, laptime_best = self.load_deltabest(combo_name)
                    start_last = start_curr  # reset lap-start-time

                if game_phase < 5:  # reset stint stats if session has not started
                    start_last = start_curr  # reset

                # Start updating
                laptime_curr = max(elapsed_time - start_last, 0)  # current laptime

                # Lap start & finish detection
                if start_curr > start_last:  # difference of lap-start-time
                    laptime_last = start_curr - start_last

                    if delta_list_curr:  # non-empty list check
                        delta_list_curr.append((pos_last + 10, laptime_last))  # set end value
                        delta_list_last = delta_list_curr.copy()
                        validating = True

                    delta_list_curr.clear()  # reset current delta list
                    delta_list_curr.append((0.0, 0.0))  # set start value
                    recording = True  # activate delta recording
                    start_last = start_curr  # reset
                    pos_last = pos_curr  # set pos last

                # Laptime validating 1s after passing finish line
                # To compensate 5fps refresh rate of Scoring data
                # Must place validating after lap start & finish detection
                # Negative mLastLapTime value indicates invalid last laptime
                if validating:
                    if 1 < laptime_curr <= 8:
                        if laptime_last < laptime_best and abs(lastlap_check - laptime_last) < 1:
                            laptime_best = laptime_last
                            delta_list_best = delta_list_last
                            self.save_deltabest(combo_name, delta_list_best)
                            validating = False
                    elif 8 < laptime_curr < 10:  # switch off validating after 8s
                        validating = False

                # Recording only from the beginning of a lap
                if recording:
                    # Update position if current dist value is diff & positive
                    if pos_curr != pos_last and pos_curr >= 0:
                        if pos_curr > pos_last:  # record if position is further away
                            delta_list_curr.append((pos_curr, laptime_curr))

                        pos_last = pos_curr  # reset last position
                        pos_append = pos_last  # reset initial position for appending

                # Update time difference & calculate additional traveled distance
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

                # Output delta time data
                self.output_data = (laptime_curr, laptime_last, laptime_best,
                                    laptime_est, delta_best)

                # Record driven distance in meters
                if gps_last != gps_curr:
                    moved_distance = calc.pos2distance(gps_last, gps_curr)
                    if moved_distance < 15:  # add small amount limit
                        self.meters_driven += moved_distance
                        gps_last = gps_curr
                    else:
                        gps_last = gps_curr

            else:
                if verified:
                    recording = False  # disable delta recording after exit track
                    verified = False  # activate verification when enter track next time
                    validating = False  # disable laptime validate
                    update_delay = 0.4  # longer delay while inactive
                    delta_list_curr.clear()  # reset current delta list

                    # Save delta best data
                    #if delta_list_best:
                        #self.save_deltabest(combo_name, delta_list_best)

                    # Save meters driven & last laptime data
                    self.cfg.setting_user["cruise"]["meters_driven"] = int(self.meters_driven)
                    self.cfg.save()

            time.sleep(update_delay)

        else:
            self.stopped = True
            print("delta module closed")

    @staticmethod
    def delta_telemetry():
        """Delta telemetry data"""
        start_curr = chknm(info.syncedVehicleTelemetry().mLapStartET)
        elapsed_time = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        lastlap_check = chknm(info.syncedVehicleScoring().mLastLapTime)
        speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                               chknm(info.syncedVehicleTelemetry().mLocalVel.z))
        pos_curr = chknm(info.syncedVehicleScoring().mLapDist)
        gps_curr = (chknm(info.syncedVehicleTelemetry().mPos.x),
                    chknm(info.syncedVehicleTelemetry().mPos.y),
                    chknm(info.syncedVehicleTelemetry().mPos.z))
        game_phase = chknm(info.LastScor.mScoringInfo.mGamePhase)
        return (start_curr, elapsed_time, lastlap_check, speed, pos_curr,
                gps_curr, game_phase)

    @staticmethod
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

    @staticmethod
    def save_deltabest(combo, listname):
        """Save delta best"""
        with open(f"deltabest/{combo}.csv", "w", newline="", encoding="utf-8") as csvfile:
            deltawrite = csv.writer(csvfile)
            deltawrite.writerows(listname)
