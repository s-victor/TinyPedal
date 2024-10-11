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
Energy module
"""

import logging

from ._base import DataModule
from .module_fuel import calc_data
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc

MODULE_NAME = "module_energy"

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Energy usage data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)
        self.filepath = self.cfg.path.energy_delta

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    combo_id = api.read.check.combo_id()
                    gen_calc_energy = calc_data(
                        minfo.energy, telemetry_energy, self.filepath, combo_id, "energy")
                    # Initial run to reset module output
                    next(gen_calc_energy)
                    gen_calc_energy.send(True)

                # Run calculation if virtual energy available
                if minfo.restapi.maxVirtualEnergy:
                    gen_calc_energy.send(True)

                    # Update fuel to energy ratio
                    minfo.hybrid.fuelEnergyRatio = calc.fuel_to_energy_ratio(
                        minfo.fuel.estimatedConsumption,
                        minfo.energy.estimatedConsumption)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    # Trigger save check
                    gen_calc_energy.send(False)


def telemetry_energy():
    """Telemetry energy, output in percentage"""
    max_energy = minfo.restapi.maxVirtualEnergy
    if max_energy:
        return 100, minfo.restapi.currentVirtualEnergy / max_energy * 100
    return 100, 0
