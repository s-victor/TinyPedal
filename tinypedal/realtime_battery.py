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
Battery module
"""

import time
import threading

from .readapi import info, chknm, state


class Battery:
    """Battery usage data"""

    def __init__(self, config):
        self.cfg = config
        self.output_data = (0,[0,0,0,0],0)
        self.running = False
        self.stopped = True

    def start(self):
        """Start calculation thread"""
        self.running = True
        self.stopped = False
        self.thread = threading.Thread(target=self.__calculation)
        self.thread.daemon=True
        self.thread.start()
        print("battery module started")

    def __calculation(self):
        """Battery calculation"""
        verified = False  # additional check for conserving resources
        last_lap_stime = 0  # last lap start time
        battery_delta = [0,0,0,0]  # battery used & regen, last lap used & regen
        last_battery_charge = 0
        last_motor_state = 0
        motor_active_timer = 0
        motor_active_timer_start = False
        lap_etime_last = 0

        update_delay = 0.4  # changeable update delay for conserving resources

        while self.running:
            if state():

                (lap_stime, lap_etime, battery_charge, motor_state) = self.__telemetry()

                # Save switch
                if not verified:
                    verified = True
                    update_delay = 0.01  # shorter delay
                    last_lap_stime = lap_stime  # reset time stamp counter

                if lap_stime != last_lap_stime:  # time stamp difference
                    last_lap_stime = lap_stime  # reset
                    battery_delta = [0,0,*battery_delta.copy()]
                    motor_active_timer = 0

                if last_battery_charge:
                    if last_battery_charge > battery_charge > 0:
                        battery_delta[0] += last_battery_charge - battery_charge

                    if last_battery_charge < battery_charge < 100:
                        battery_delta[1] += battery_charge - last_battery_charge
                last_battery_charge = battery_charge

                if last_motor_state != motor_state and motor_state == 2:
                    motor_active_timer_start = True
                    lap_etime_last = lap_etime
                    last_motor_state = motor_state

                if motor_active_timer_start:
                    motor_active_timer += lap_etime - lap_etime_last
                    lap_etime_last = lap_etime
                    if motor_state != 2:
                        motor_active_timer_start = False
                        last_motor_state = motor_state

                # Output battery data
                self.output_data = (battery_charge, battery_delta, motor_active_timer)

            else:
                if verified:
                    verified = False
                    update_delay = 0.4  # longer delay while inactive
                    battery_delta = [0,0,0,0]
                    last_battery_charge = 0
                    last_motor_state = 0
                    motor_active_timer = 0
                    motor_active_timer_start = False
                    lap_etime_last = 0

            time.sleep(update_delay)

        self.stopped = True
        print("battery module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
        lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        battery_charge = chknm(info.syncedVehicleTelemetry().mBatteryChargeFraction) * 100
        motor_state = chknm(info.syncedVehicleTelemetry().mElectricBoostMotorState)
        return (lap_stime, lap_etime, battery_charge, motor_state)
