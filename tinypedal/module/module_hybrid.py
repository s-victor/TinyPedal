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
Hybrid module
"""

import logging
import time
import threading

from ..module_info import minfo
from ..readapi import info, chknm, state

MODULE_NAME = "module_hybrid"

logger = logging.getLogger(__name__)


class Realtime:
    """Hybrid data"""
    module_name = MODULE_NAME

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
            logger.info("hybrid module started")

    def __calculation(self):
        """Hybrid calculation"""
        reset = False  # additional check for conserving resources
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    battery_drain = 0
                    battery_regen = 0
                    battery_drain_last = 0
                    battery_regen_last = 0
                    last_battery_charge = 0
                    last_motor_state = 0
                    motor_active_timer = 0
                    motor_active_timer_start = False
                    motor_inactive_timer = 99999
                    motor_inactive_timer_start = False
                    lap_etime_last = 0
                    last_lap_stime = -1  # last lap start time

                # Read telemetry
                (lap_stime, lap_etime, battery_charge, motor_state
                 ) = self.__telemetry()

                # Lap start & finish detection
                if lap_stime > last_lap_stime != -1:
                    battery_drain_last = battery_drain
                    battery_regen_last = battery_regen
                    battery_drain = 0
                    battery_regen = 0
                    motor_active_timer = 0
                last_lap_stime = lap_stime  # reset

                if last_battery_charge:
                    if last_battery_charge > battery_charge > 0:  # drain
                        battery_drain += last_battery_charge - battery_charge

                    if last_battery_charge < battery_charge < 100: # regen
                        battery_regen += battery_charge - last_battery_charge
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
                        motor_inactive_timer_start = lap_etime
                        last_motor_state = motor_state

                if motor_inactive_timer_start:
                    motor_inactive_timer = lap_etime - motor_inactive_timer_start
                    if motor_state == 2:
                        motor_inactive_timer_start = False
                        motor_inactive_timer = 99999

                # Output hybrid data
                minfo.hybrid.BatteryCharge = battery_charge
                minfo.hybrid.BatteryDrain = battery_drain
                minfo.hybrid.BatteryRegen = battery_regen
                minfo.hybrid.BatteryDrainLast = battery_drain_last
                minfo.hybrid.BatteryRegenLast = battery_regen_last
                minfo.hybrid.MotorActiveTimer = motor_active_timer
                minfo.hybrid.MotorInActiveTimer = motor_inactive_timer
                minfo.hybrid.MotorState = motor_state

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("hybrid module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        lap_stime = chknm(info.rf2TeleVeh().mLapStartET)
        lap_etime = chknm(info.rf2TeleVeh().mElapsedTime)
        battery_charge = chknm(info.rf2TeleVeh().mBatteryChargeFraction) * 100
        motor_state = chknm(info.rf2TeleVeh().mElectricBoostMotorState)
        return (lap_stime, lap_etime, battery_charge, motor_state)
