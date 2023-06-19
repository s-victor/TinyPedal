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
Module info
"""

from dataclasses import dataclass


@dataclass
class DeltaInfo:
    """Delta module output data"""
    LaptimeCurrent: float = 0
    LaptimeLast: float = 0
    LaptimeBest: float = 0
    LaptimeEstimated: float = 0
    DeltaBest: float = 0
    IsValidLap: bool = 0
    MetersDriven: float = 0


@dataclass
class ForceInfo:
    """Force module output data"""
    LgtGForceRaw: float = 0
    LatGForceRaw: float = 0
    MaxAvgLgtGForce: float = 0
    MaxAvgLatGForce: float = 0
    MaxLgtGForce: float = 0
    MaxLatGForce: float = 0
    GForceVector: float = 0
    DownForceFront: float = 0
    DownForceRear: float = 0
    DownForceRatio: float = 0


@dataclass
class FuelInfo:
    """Fuel module output data"""
    Capacity: float = 0
    AmountFuelStart: float = 0
    AmountFuelCurrent: float = 0
    AmountFuelNeeded: float = 0
    AmountFuelBeforePitstop: float = 0
    LastLapFuelConsumption: float = 0
    EstimatedFuelConsumption: float = 0
    EstimatedLaps: float = 0
    EstimatedMinutes: float = 0
    EstimatedEmptyCapacity: float = 0
    EstimatedNumPitStopsEnd: float = 0
    EstimatedNumPitStopsEarly: float = 0
    DeltaFuelConsumption: float = 0
    OneLessPitFuelConsumption: float = 0


@dataclass
class HybridInfo:
    """Hybrid module output data"""
    BatteryCharge: float = 0
    BatteryDrain: float = 0
    BatteryRegen: float = 0
    BatteryDrainLast: float = 0
    BatteryRegenLast: float = 0
    MotorActiveTimer: float = 0
    MotorInActiveTimer: float = 0
    MotorState: int = 0


@dataclass
class MappingInfo:
    """Mapping module output data"""
    Coordinates: list = None
    Elevations: list = None
    Sectors: list = None


@dataclass
class RelativeInfo:
    """Relative module output data"""
    Relative: list = None
    Standings: list = None
    Classes: list = None


@dataclass
class StandingsInfo:
    """Standings module output data"""
    Vehicles: list = None
    NearestStraight: float = 999999
    NearestTraffic: float = 999999
    NearestYellow: float = 999999


class ModuleInfo:
    """Modules output data"""

    def __init__(self):
        self.delta = DeltaInfo()
        self.force = ForceInfo()
        self.fuel = FuelInfo()
        self.hybrid = HybridInfo()
        self.mapping = MappingInfo()
        self.relative = RelativeInfo()
        self.standings = StandingsInfo()


minfo = ModuleInfo()
