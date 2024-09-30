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
from collections import deque


@dataclass
class DeltaInfo:
    """Delta module output data"""
    deltaBest: float = 0
    deltaLast: float = 0
    deltaSession: float = 0
    deltaStint: float = 0
    isValidLap: bool = False
    lapTimeCurrent: float = 0
    lapTimeLast: float = 0
    lapTimeBest: float = 0
    lapTimeEstimated: float = 0
    lapTimeSession: float = 0
    lapTimeStint: float = 0
    lapTimePace: float = 0
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
    transientMaxBrakingRate: float = 0
    maxBrakingRate: float = 0
    deltaBrakingRate: float = 0


@dataclass
class FuelInfo:
    """Fuel module output data"""
    capacity: float = 0
    amountStart: float = 0
    amountCurrent: float = 0
    amountUsedCurrent: float = 0
    amountNeeded: float = 0
    amountEndStint: float = 0
    lastLapConsumption: float = 0
    lastLapValidConsumption: float = 0
    estimatedConsumption: float = 0
    estimatedValidConsumption: float = 0
    estimatedLaps: float = 0
    estimatedMinutes: float = 0
    estimatedEmptyCapacity: float = 0
    estimatedNumPitStopsEnd: float = 0
    estimatedNumPitStopsEarly: float = 0
    deltaConsumption: float = 0
    oneLessPitConsumption: float = 0


@dataclass
class HistoryInfo:
    """History output data

    consumption list:
        0 lapnumber, 1 is valid laptime, 2 laptime,
        3 fuel, 4 energy, 5 batter drain, 6 battery regen
    """
    consumption: deque = field(default_factory=deque)

    def __post_init__(self):
        self.consumption = deque([(0,0,0,0,0,0,0)], 100)


@dataclass
class HybridInfo:
    """Hybrid module output data"""
    batteryCharge: float = 0
    batteryDrain: float = 0
    batteryRegen: float = 0
    batteryDrainLast: float = 0
    batteryRegenLast: float = 0
    motorActiveTimer: float = 0
    motorInactiveTimer: float = 0
    motorState: int = 0
    fuelEnergyRatio: float = 0


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

    def __post_init__(self):
        """Initialize list to avoid out of range"""
        self.relative = [-1]
        self.standings = [-1]
        self.classes = [[0,1,"",0,0,-1,-1]]


@dataclass
class SectorsInfo:
    """Sectors module output data"""
    noDeltaSector: bool = True
    sectorIndex: int = -1
    sectorPrev: list | None = None
    sectorBestTB: list | None = None
    sectorBestPB: list | None = None
    deltaSectorBestPB: list | None = None
    deltaSectorBestTB: list | None = None

    def __post_init__(self):
        """Initialize list to avoid out of range

        Those are placehold, will be overwritten by Sectors module, no copy needed.
        """
        self.sectorPrev = [99999,99999,99999]
        self.sectorBestTB = self.sectorPrev
        self.sectorBestPB = self.sectorPrev
        self.deltaSectorBestPB = self.sectorPrev
        self.deltaSectorBestTB = self.sectorPrev


@dataclass
class RestAPIInfo:
    """Rest API module output data"""
    timeScale: int = 1
    privateQualifying: int = 0
    steeringWheelRange: float = 0
    currentVirtualEnergy: float = 0
    maxVirtualEnergy: float = 0
    forecastPractice: list | None = None
    forecastQualify: list | None = None
    forecastRace: list | None = None


@dataclass
class VehiclesInfo:
    """Vehicles module output data"""
    total: int = 0
    dataSet: tuple = field(default_factory=tuple)
    dataSetVersion: int = -1
    drawOrder: list = field(default_factory=list)
    nearestLine: float = 999999
    nearestTraffic: float = 999999
    nearestYellow: float = 999999

    def __post_init__(self):
        self.dataSet = tuple(VehicleDataSet() for _ in range(128))
        self.drawOrder = [0]


@dataclass
class WheelsInfo:
    """Wheels module output data"""
    radiusFront: float = 0
    radiusRear: float = 0
    lockingPercentFront: float = 0
    lockingPercentRear: float = 0
    slipRatio: list = field(default_factory=list)

    def __post_init__(self):
        self.slipRatio = [0,0,0,0]


@dataclass
class VehicleDataSet:
    """Vehicle data set"""
    isPlayer: bool = False
    positionOverall: int = 0
    positionInClass: int = 0
    driverName: str = ""
    vehicleName: str = ""
    vehicleClass: str = ""
    sessionBestLapTime: float = 99999
    classBestLapTime: float = 99999
    bestLapTime: float = 99999
    lastLapTime: float = 99999
    lapProgress: float = 0
    relativeTimeGap: float = 0
    gapBehindNextInClass: float = 0
    gapBehindNext: float = 0
    gapBehindLeader: float = 0
    isLapped: bool = False
    isYellow: bool = False
    inPit: bool = False
    numPitStops: int = 0
    pitState: int = 0
    relativeOrientationXYRadians: float = 0
    relativeStraightDistance: float = 0
    # Sub-list
    pitTimer: list = field(default_factory=list)
    posXY: list = field(default_factory=list)
    tireCompound: list = field(default_factory=list)
    relativeRotatedPosXY: list = field(default_factory=list)

    def __post_init__(self):
        """Initialize sub-list"""
        self.pitTimer = [0, -1, 0]  # 0 in pit state, 1 pit start time, 2 pit timer
        self.posXY = [0, 0]
        self.tireCompound = [0, 0]  # front, rear
        self.relativeRotatedPosXY = [0, 0]


class ModuleInfo:
    """Modules output data"""
    MAX_VEHICLES = 128

    def __init__(self):
        self.delta = DeltaInfo()
        self.energy = FuelInfo()
        self.force = ForceInfo()
        self.fuel = FuelInfo()
        self.history = HistoryInfo()
        self.hybrid = HybridInfo()
        self.mapping = MappingInfo()
        self.relative = RelativeInfo()
        self.restapi = RestAPIInfo()
        self.sectors = SectorsInfo()
        self.vehicles = VehiclesInfo()
        self.wheels = WheelsInfo()


minfo = ModuleInfo()
