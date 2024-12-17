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
from collections import deque
from typing import NamedTuple

MAX_VEHICLES = 128


class DeltaInfo:
    """Delta module output data"""

    __slots__ = (
        "deltaBest",
        "deltaLast",
        "deltaSession",
        "deltaStint",
        "isValidLap",
        "lapTimeCurrent",
        "lapTimeLast",
        "lapTimeBest",
        "lapTimeEstimated",
        "lapTimeSession",
        "lapTimeStint",
        "lapTimePace",
        "lapDistance",
        "metersDriven",
    )

    def __init__(self):
        self.deltaBest: float = 0.0
        self.deltaLast: float = 0.0
        self.deltaSession: float = 0.0
        self.deltaStint: float = 0.0
        self.isValidLap: bool = False
        self.lapTimeCurrent: float = 0.0
        self.lapTimeLast: float = 0.0
        self.lapTimeBest: float = 0.0
        self.lapTimeEstimated: float = 0.0
        self.lapTimeSession: float = 0.0
        self.lapTimeStint: float = 0.0
        self.lapTimePace: float = 0.0
        self.lapDistance: float = 0.0
        self.metersDriven: float = 0.0


class ForceInfo:
    """Force module output data"""

    __slots__ = (
        "lgtGForceRaw",
        "latGForceRaw",
        "maxAvgLatGForce",
        "maxLgtGForce",
        "maxLatGForce",
        "downForceFront",
        "downForceRear",
        "downForceRatio",
        "brakingRate",
        "transientMaxBrakingRate",
        "maxBrakingRate",
        "deltaBrakingRate",
    )

    def __init__(self):
        self.lgtGForceRaw: float = 0.0
        self.latGForceRaw: float = 0.0
        self.maxAvgLatGForce: float = 0.0
        self.maxLgtGForce: float = 0.0
        self.maxLatGForce: float = 0.0
        self.downForceFront: float = 0.0
        self.downForceRear: float = 0.0
        self.downForceRatio: float = 0.0
        self.brakingRate: float = 0.0
        self.transientMaxBrakingRate: float = 0.0
        self.maxBrakingRate: float = 0.0
        self.deltaBrakingRate: float = 0.0


class FuelInfo:
    """Fuel module output data"""

    __slots__ = (
        "capacity",
        "amountStart",
        "amountCurrent",
        "amountUsedCurrent",
        "amountNeeded",
        "amountEndStint",
        "lastLapConsumption",
        "lastLapValidConsumption",
        "estimatedConsumption",
        "estimatedValidConsumption",
        "estimatedLaps",
        "estimatedMinutes",
        "estimatedEmptyCapacity",
        "estimatedNumPitStopsEnd",
        "estimatedNumPitStopsEarly",
        "deltaConsumption",
        "oneLessPitConsumption",
    )

    def __init__(self):
        self.capacity: float = 0.0
        self.amountStart: float = 0.0
        self.amountCurrent: float = 0.0
        self.amountUsedCurrent: float = 0.0
        self.amountNeeded: float = 0.0
        self.amountEndStint: float = 0.0
        self.lastLapConsumption: float = 0.0
        self.lastLapValidConsumption: float = 0.0
        self.estimatedConsumption: float = 0.0
        self.estimatedValidConsumption: float = 0.0
        self.estimatedLaps: float = 0.0
        self.estimatedMinutes: float = 0.0
        self.estimatedEmptyCapacity: float = 0.0
        self.estimatedNumPitStopsEnd: float = 0.0
        self.estimatedNumPitStopsEarly: float = 0.0
        self.deltaConsumption: float = 0.0
        self.oneLessPitConsumption: float = 0.0


class ConsumptionDataSet(NamedTuple):
    """Consumption history data set"""
    completedLaps: int = 0
    isValidLap: bool = False
    lapTimeLast: float = 0.0
    lastLapUsedFuel: float = 0.0
    lastLapUsedEnergy: float = 0.0
    batteryDrainLast: float = 0.0
    batteryRegenLast: float = 0.0


class HistoryInfo:
    """History output data"""

    __slots__ = "consumption"

    def __init__(self):
        self.consumption: deque[ConsumptionDataSet] = deque([ConsumptionDataSet()], 100)


class HybridInfo:
    """Hybrid module output data"""

    __slots__ = (
        "batteryCharge",
        "batteryDrain",
        "batteryRegen",
        "batteryDrainLast",
        "batteryRegenLast",
        "motorActiveTimer",
        "motorInactiveTimer",
        "motorState",
        "fuelEnergyRatio",
        "fuelEnergyBias",
    )

    def __init__(self):
        self.batteryCharge: float = 0.0
        self.batteryDrain: float = 0.0
        self.batteryRegen: float = 0.0
        self.batteryDrainLast: float = 0.0
        self.batteryRegenLast: float = 0.0
        self.motorActiveTimer: float = 0.0
        self.motorInactiveTimer: float = 0.0
        self.motorState: int = 0
        self.fuelEnergyRatio: float = 0.0
        self.fuelEnergyBias: float = 0.0


class MappingInfo:
    """Mapping module output data"""

    __slots__ = (
        "coordinates",
        "elevations",
        "sectors",
        "lastModified",
    )

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset"""
        self.coordinates: tuple[tuple[float, float], ...] | None = None
        self.elevations: tuple[tuple[float, float], ...] | None = None
        self.sectors: tuple[int, int] | None = None
        self.lastModified: float = 0.0


class NotesInfo:
    """Notes module output data"""

    __slots__ = (
        "currentIndex",
        "currentNote",
        "nextIndex",
        "nextNote",
    )

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset"""
        self.currentIndex: int = 0
        self.currentNote: dict = {}
        self.nextIndex: int = 0
        self.nextNote: dict = {}


class RelativeInfo:
    """Relative module output data"""

    __slots__ = (
        "relative",
        "standings",
        "classes",
    )

    def __init__(self):
        self.relative: list[int] = [-1]
        self.standings: list[int] = [-1]
        self.classes: list[list] = [[0, 1, "", 0, 0, -1, -1, False]]


class SectorsInfo:
    """Sectors module output data"""

    __slots__ = (
        "noDeltaSector",
        "sectorIndex",
        "sectorPrev",
        "sectorBestTB",
        "sectorBestPB",
        "deltaSectorBestPB",
        "deltaSectorBestTB",
    )

    def __init__(self):
        temp_sector = [99999.0] * 3
        self.noDeltaSector: bool = True
        self.sectorIndex: int = -1
        self.sectorPrev: list[float] = temp_sector
        self.sectorBestTB: list[float] = temp_sector
        self.sectorBestPB: list[float] = temp_sector
        self.deltaSectorBestPB: list[float] = temp_sector
        self.deltaSectorBestTB: list[float] = temp_sector


class RestAPIInfo:
    """Rest API module output data"""

    __slots__ = (
        "timeScale",
        "privateQualifying",
        "steeringWheelRange",
        "currentVirtualEnergy",
        "maxVirtualEnergy",
        "aeroDamage",
        "forecastPractice",
        "forecastQualify",
        "forecastRace",
        "brakeWear",
        "suspensionDamage",
    )

    def __init__(self):
        self.timeScale: int = 1
        self.privateQualifying: int = 0
        self.steeringWheelRange: float = 0.0
        self.currentVirtualEnergy: float = 0.0
        self.maxVirtualEnergy: float = 0.0
        self.aeroDamage: float = -1.0
        self.forecastPractice: list[tuple] | None = None
        self.forecastQualify: list[tuple] | None = None
        self.forecastRace: list[tuple] | None = None
        self.brakeWear: list[float] = [-1.0] * 4
        self.suspensionDamage: list[float] = [-1.0] * 4


class VehiclesInfo:
    """Vehicles module output data"""

    __slots__ = (
        "total",
        "dataSet",
        "dataSetVersion",
        "drawOrder",
        "nearestLine",
        "nearestTraffic",
        "nearestYellow",
    )

    def __init__(self):
        self.total: int = 0
        self.dataSet: tuple[VehicleDataSet, ...] = tuple(VehicleDataSet() for _ in range(128))
        self.dataSetVersion: int = -1
        self.drawOrder: list = [0]
        self.nearestLine: float = 999999.0
        self.nearestTraffic: float = 999999.0
        self.nearestYellow: float = 999999.0


class WheelsInfo:
    """Wheels module output data"""

    __slots__ = (
        "radiusFront",
        "radiusRear",
        "lockingPercentFront",
        "lockingPercentRear",
        "corneringRadius",
        "slipRatio",
    )

    def __init__(self):
        self.radiusFront: float = 0.0
        self.radiusRear: float = 0.0
        self.lockingPercentFront: float = 0.0
        self.lockingPercentRear: float = 0.0
        self.corneringRadius: float = 0.0
        self.slipRatio: list[float] = [0.0] * 4


class VehiclePitTimer:
    """Vehicle pit timer"""

    __slots__ = (
        "last_state",
        "start",
        "elapsed",
    )

    def __init__(self):
        self.last_state: int = 0
        self.start: float = 0.0
        self.elapsed: float = 0.0


class VehicleDataSet:
    """Vehicle data set"""

    __slots__ = (
        "isPlayer",
        "positionOverall",
        "positionInClass",
        "driverName",
        "vehicleName",
        "vehicleClass",
        "sessionBestLapTime",
        "classBestLapTime",
        "bestLapTime",
        "lastLapTime",
        "lapProgress",
        "relativeTimeGap",
        "gapBehindNextInClass",
        "gapBehindNext",
        "gapBehindLeader",
        "isLapped",
        "isYellow",
        "inPit",
        "isClassFastestLastLap",
        "numPitStops",
        "pitState",
        "tireCompoundFront",
        "tireCompoundRear",
        "relativeOrientationRadians",
        "relativeStraightDistance",
        "worldPositionX",
        "worldPositionY",
        "relativeRotatedPositionX",
        "relativeRotatedPositionY",
        "pitTimer",
    )

    def __init__(self):
        self.isPlayer: bool = False
        self.positionOverall: int = 0
        self.positionInClass: int = 0
        self.driverName: str = ""
        self.vehicleName: str = ""
        self.vehicleClass: str = ""
        self.sessionBestLapTime: float = 99999.0
        self.classBestLapTime: float = 99999.0
        self.bestLapTime: float = 99999.0
        self.lastLapTime: float = 99999.0
        self.lapProgress: float = 0.0
        self.relativeTimeGap: float = 0.0
        self.gapBehindNextInClass: float = 0.0
        self.gapBehindNext: float = 0.0
        self.gapBehindLeader: float = 0.0
        self.isLapped: float = 0.0
        self.isYellow: bool = False
        self.inPit: int = 0
        self.isClassFastestLastLap: bool = False
        self.numPitStops: int = 0
        self.pitState: int = 0
        self.tireCompoundFront: int = 0
        self.tireCompoundRear: int = 0
        self.relativeOrientationRadians: float = 0.0
        self.relativeStraightDistance: float = 0.0
        self.worldPositionX: float = 0.0
        self.worldPositionY: float = 0.0
        self.relativeRotatedPositionX: float = 0.0
        self.relativeRotatedPositionY: float = 0.0
        self.pitTimer: VehiclePitTimer = VehiclePitTimer()


class ModuleInfo:
    """Modules output data"""

    __slots__ = (
        "delta",
        "energy",
        "force",
        "fuel",
        "history",
        "hybrid",
        "mapping",
        "pacenotes",
        "relative",
        "restapi",
        "sectors",
        "tracknotes",
        "vehicles",
        "wheels",
    )

    def __init__(self):
        self.delta = DeltaInfo()
        self.energy = FuelInfo()
        self.force = ForceInfo()
        self.fuel = FuelInfo()
        self.history = HistoryInfo()
        self.hybrid = HybridInfo()
        self.mapping = MappingInfo()
        self.pacenotes = NotesInfo()
        self.relative = RelativeInfo()
        self.restapi = RestAPIInfo()
        self.sectors = SectorsInfo()
        self.tracknotes = NotesInfo()
        self.vehicles = VehiclesInfo()
        self.wheels = WheelsInfo()


minfo = ModuleInfo()
