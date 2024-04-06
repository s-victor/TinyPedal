#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
import threading

from ..module_info import minfo
from ..api_control import api

MODULE_NAME = "module_hybrid"

logger = logging.getLogger(__name__)


class Realtime:
    """Hybrid data"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.user.setting[self.module_name]
        self.stopped = True
        self.event = threading.Event()

    def start(self):
        """Start update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__update_data, daemon=True).start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: %s", MODULE_NAME)

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __update_data(self):
        """Update module data"""
        reset = False  # additional check for conserving resources
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = active_interval

        while not self.event.wait(update_interval):
            if api.state:

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
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()
                battery_charge = api.read.emotor.battery_charge() * 100
                motor_state = api.read.emotor.state()

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
                minfo.hybrid.batteryCharge = battery_charge
                minfo.hybrid.batteryDrain = battery_drain
                minfo.hybrid.batteryRegen = battery_regen
                minfo.hybrid.batteryDrainLast = battery_drain_last
                minfo.hybrid.batteryRegenLast = battery_regen_last
                minfo.hybrid.motorActiveTimer = motor_active_timer
                minfo.hybrid.motorInActiveTimer = motor_inactive_timer
                minfo.hybrid.motorState = motor_state

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: %s", MODULE_NAME)
