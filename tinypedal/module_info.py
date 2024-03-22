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
Module info
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class DeltaInfo:
    """Delta module output data"""
    lapTimeCurrent: float = 0
    lapTimeLast: float = 0
    lapTimeBest: float = 0
    lapTimeEstimated: float = 0
    lapTimeStintBest: float = 0
    deltaBest: float = 0
    deltaLast: float = 0
    deltaSession: float = 0
    deltaStint: float = 0
    isValidLap: bool = False
    metersDriven: float = 0


@dataclass
class ForceInfo:
    """Force module output data"""
    lgtGForceRaw: float = 0
    latGForceRaw: float = 0
    maxAvgLatGForce: float = 0
    maxLgtGForce: float = 0
    maxLatGForce: float = 0
    downForceFront: float = 0
    downForceRear: float = 0
    downForceRatio: float = 0
    brakingRate: float = 0
    maxBrakingRate: float = 0
    deltaBrakingRate: float = 0


@dataclass
class FuelInfo:
    """Fuel module output data"""
    tankCapacity: float = 0
    amountFuelStart: float = 0
    amountFuelCurrent: float = 0
    amountFuelNeeded: float = 0
    amountFuelBeforePitstop: float = 0
    lastLapFuelConsumption: float = 0
    estimatedFuelConsumption: float = 0
    estimatedLaps: float = 0
    estimatedMinutes: float = 0
    estimatedEmptyCapacity: float = 0
    estimatedNumPitStopsEnd: float = 0
    estimatedNumPitStopsEarly: float = 0
    deltaFuelConsumption: float = 0
    oneLessPitFuelConsumption: float = 0


@dataclass
class HybridInfo:
    """Hybrid module output data"""
    batteryCharge: float = 0
    batteryDrain: float = 0
    batteryRegen: float = 0
    batteryDrainLast: float = 0
    batteryRegenLast: float = 0
    motorActiveTimer: float = 0
    motorInActiveTimer: float = 0
    motorState: int = 0


@dataclass
class MappingInfo:
    """Mapping module output data"""
    coordinates: tuple | None = None
    coordinatesHash: int | None = None
    elevations: tuple | None = None
    elevationsHash: int | None = None
    sectors: tuple | None = None


@dataclass
class RelativeInfo:
    """Relative module output data"""
    relative: list = field(default_factory=list)
    standings: list = field(default_factory=list)
    classes: list = field(default_factory=list)


@dataclass
class SectorsInfo:
    """Sectors module output data"""
    sectorIndex: int = -1
    deltaSectorBestPB: list | None = None
    deltaSectorBestTB: list | None = None
    sectorBestTB: list | None = None
    sectorBestPB: list | None = None
    sectorPrev: list | None = None
    noDeltaSector: bool = True


@dataclass
class VehiclesInfo:
    """Vehicles module output data"""
    dataSet: tuple = field(default_factory=tuple)
    dataSetVersion: int = -1
    nearestStraight: float = 999999
    nearestTraffic: float = 999999
    nearestYellow: float = 999999


class ModuleInfo:
    """Modules output data"""

    def __init__(self):
        self.delta = DeltaInfo()
        self.force = ForceInfo()
        self.fuel = FuelInfo()
        self.hybrid = HybridInfo()
        self.mapping = MappingInfo()
        self.relative = RelativeInfo()
        self.sectors = SectorsInfo()
        self.vehicles = VehiclesInfo()


minfo = ModuleInfo()
