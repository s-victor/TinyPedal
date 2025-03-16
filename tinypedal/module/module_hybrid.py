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

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc


class Realtime(DataModule):
    """Hybrid data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        output = minfo.hybrid

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    battery_drain = 0
                    battery_regen = 0
                    battery_drain_last = 0
                    battery_regen_last = 0
                    last_battery_charge = 0
                    last_motor_state = 0
                    alt_motor_state = 1  # alternative state in case motor state not available
                    alt_motor_state_debounce = 0  # alternative state reset debounce counter
                    motor_active_timer = 0
                    motor_active_timer_start = False
                    motor_inactive_timer = 99999
                    motor_inactive_timer_start = False
                    lap_etime_last = 0
                    last_lap_stime = calc.FLOAT_INF  # last lap start time

                # Read telemetry
                lap_stime = api.read.timing.start()
                lap_etime = api.read.timing.elapsed()
                battery_charge = api.read.emotor.battery_charge() * 100
                motor_state = api.read.emotor.state()

                # Lap start & finish detection
                if lap_stime > last_lap_stime:
                    battery_drain_last = battery_drain
                    battery_regen_last = battery_regen
                    battery_drain = 0
                    battery_regen = 0
                    motor_active_timer = 0
                last_lap_stime = lap_stime  # reset

                if last_battery_charge:
                    if last_battery_charge > battery_charge > 0:  # drain
                        battery_drain += last_battery_charge - battery_charge
                        alt_motor_state_debounce = 0
                        alt_motor_state = 2
                    elif last_battery_charge < battery_charge < 100: # regen
                        battery_regen += battery_charge - last_battery_charge
                        alt_motor_state_debounce = 0
                        alt_motor_state = 3
                    elif alt_motor_state > 1:
                        alt_motor_state_debounce += 1
                        if alt_motor_state_debounce > 5:
                            alt_motor_state = 1
                last_battery_charge = battery_charge

                # Motor state correction
                if motor_state == 0 < battery_charge:
                    motor_state = alt_motor_state

                # Active timer
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
                output.batteryCharge = battery_charge
                output.batteryDrain = battery_drain
                output.batteryRegen = battery_regen
                output.batteryDrainLast = battery_drain_last
                output.batteryRegenLast = battery_regen_last
                output.motorActiveTimer = motor_active_timer
                output.motorInactiveTimer = motor_inactive_timer
                output.motorState = motor_state

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
