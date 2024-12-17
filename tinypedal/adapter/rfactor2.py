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
Data set for rFactor 2

Notes:
    Convert all temperature (kelvin) to Celsius before output.
"""

from __future__ import annotations

from . import DataAdapter
from .. import validator as val
from ..formatter import strip_invalid_char
from ..calculation import (
    mean,
    lap_progress_distance,
    meter2millmeter,
    oriyaw2rad,
    slip_angle,
    vel2speed,
)

chknm = val.infnan2zero
cs2py = val.cbytes2str

# 0 = TESTDAY, 1 = PRACTICE, 2 = QUALIFY, 3 = WARMUP, 4 = RACE
RF2_SESSION_TYPE = (0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 4, 4, 4, 4, 0, 0, 0, 0)
# Sector index 0 = S3, index 1 = S1, index 2 = S2
RF2_SECTORS = (2, 0, 1, 0, 0, 0, 0)


class Check(DataAdapter):
    """Check"""

    __slots__ = ()

    def api_state(self) -> bool:
        """API state"""
        return (
            not self.info.isPaused and
            (self.info.rf2ScorInfo.mInRealtime
            or self.info.rf2TeleVeh().mIgnitionStarter)
        )

    def api_version(self) -> str:
        """Identify API version"""
        return cs2py(self.info.rf2Ext.mVersion)

    def sim_name(self) -> str:
        """Identify sim name"""
        name = cs2py(self.info.rf2ScorInfo.mPlrFileName)
        if name == "Settings":
            return "LMU"
        if name:
            return "RF2"
        return ""

    def combo_id(self) -> str:
        """Identify track & vehicle combo"""
        track_name = cs2py(self.info.rf2ScorInfo.mTrackName)
        class_name = cs2py(self.info.rf2ScorVeh().mVehicleClass)
        return strip_invalid_char(f"{track_name} - {class_name}")

    def vehicle_id(self) -> str:
        """Identify vehicle & class"""
        class_name = cs2py(self.info.rf2ScorVeh().mVehicleClass)
        veh_name = cs2py(self.info.rf2ScorVeh().mVehicleName)
        return strip_invalid_char(f"{class_name} - {veh_name}")

    def track_id(self) -> str:
        """Identify track name"""
        return strip_invalid_char(cs2py(self.info.rf2ScorInfo.mTrackName))

    def session_id(self) -> tuple[int]:
        """Identify session"""
        session_length = chknm(self.info.rf2ScorInfo.mEndET)
        session_type = chknm(self.info.rf2ScorInfo.mSession)
        session_stamp = int(session_length * 100 + session_type)
        session_etime = int(chknm(self.info.rf2ScorInfo.mCurrentET))
        session_tlaps = chknm(self.info.rf2ScorVeh().mTotalLaps)
        return session_stamp, session_etime, session_tlaps


class Brake(DataAdapter):
    """Brake"""

    __slots__ = ()

    def bias_front(self, index: int | None = None) -> float:
        """Brake bias front"""
        return 1 - chknm(self.info.rf2TeleVeh(index).mRearBrakeBias)

    def pressure(self, index: int | None = None, scale: float = 1) -> list[float]:
        """Brake pressure"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mBrakePressure) * scale for data in wheel_data]

    def temperature(self, index: int | None = None) -> list[float]:
        """Brake temperature"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mBrakeTemp) - 273.15 for data in wheel_data]


class ElectricMotor(DataAdapter):
    """Electric motor"""

    __slots__ = ()

    def state(self, index: int | None = None) -> int:
        """Motor state, 0 = n/a, 1 = off, 2 = drain, 3 = regen"""
        return chknm(self.info.rf2TeleVeh(index).mElectricBoostMotorState)

    def battery_charge(self, index: int | None = None) -> float:
        """Battery charge"""
        return chknm(self.info.rf2TeleVeh(index).mBatteryChargeFraction)

    def rpm(self, index: int | None = None) -> float:
        """Motor RPM"""
        return chknm(self.info.rf2TeleVeh(index).mElectricBoostMotorRPM)

    def torque(self, index: int | None = None) -> float:
        """Motor torque"""
        return chknm(self.info.rf2TeleVeh(index).mElectricBoostMotorTorque)

    def motor_temperature(self, index: int | None = None) -> float:
        """Motor temperature"""
        return chknm(self.info.rf2TeleVeh(index).mElectricBoostMotorTemperature)

    def water_temperature(self, index: int | None = None) -> float:
        """Motor water temperature"""
        return chknm(self.info.rf2TeleVeh(index).mElectricBoostWaterTemperature)


class Engine(DataAdapter):
    """Engine"""

    __slots__ = ()

    def gear(self, index: int | None = None) -> int:
        """Gear"""
        return chknm(self.info.rf2TeleVeh(index).mGear)

    def gear_max(self, index: int | None = None) -> int:
        """Max gear"""
        return chknm(self.info.rf2TeleVeh(index).mMaxGears)

    def rpm(self, index: int | None = None) -> float:
        """RPM"""
        return chknm(self.info.rf2TeleVeh(index).mEngineRPM)

    def rpm_max(self, index: int | None = None) -> float:
        """Max RPM"""
        return chknm(self.info.rf2TeleVeh(index).mEngineMaxRPM)

    def torque(self, index: int | None = None) -> float:
        """Torque"""
        return chknm(self.info.rf2TeleVeh(index).mEngineTorque)

    def turbo(self, index: int | None = None) -> float:
        """Turbo"""
        return chknm(self.info.rf2TeleVeh(index).mTurboBoostPressure)

    def oil_temperature(self, index: int | None = None) -> float:
        """Oil temperature"""
        return chknm(self.info.rf2TeleVeh(index).mEngineOilTemp)

    def water_temperature(self, index: int | None = None) -> float:
        """Water temperature"""
        return chknm(self.info.rf2TeleVeh(index).mEngineWaterTemp)


class Input(DataAdapter):
    """Input"""

    __slots__ = ()

    def throttle(self, index: int | None = None) -> float:
        """Throttle filtered"""
        return chknm(self.info.rf2TeleVeh(index).mFilteredThrottle)

    def throttle_raw(self, index: int | None = None) -> float:
        """Throttle raw"""
        return chknm(self.info.rf2TeleVeh(index).mUnfilteredThrottle)

    def brake(self, index: int | None = None) -> float:
        """Brake filtered"""
        return chknm(self.info.rf2TeleVeh(index).mFilteredBrake)

    def brake_raw(self, index: int | None = None) -> float:
        """Brake raw"""
        return chknm(self.info.rf2TeleVeh(index).mUnfilteredBrake)

    def clutch(self, index: int | None = None) -> float:
        """Clutch filtered"""
        return chknm(self.info.rf2TeleVeh(index).mFilteredClutch)

    def clutch_raw(self, index: int | None = None) -> float:
        """Clutch raw"""
        return chknm(self.info.rf2TeleVeh(index).mUnfilteredClutch)

    def steering(self, index: int | None = None) -> float:
        """Steering filtered"""
        return chknm(self.info.rf2TeleVeh(index).mFilteredSteering)

    def steering_raw(self, index: int | None = None) -> float:
        """Steering raw"""
        return chknm(self.info.rf2TeleVeh(index).mUnfilteredSteering)

    def steering_shaft_torque(self, index: int | None = None) -> float:
        """Steering shaft torque"""
        return chknm(self.info.rf2TeleVeh(index).mSteeringShaftTorque)

    def steering_range_physical(self, index: int | None = None) -> float:
        """Steering physical rotation range"""
        return chknm(self.info.rf2TeleVeh(index).mPhysicalSteeringWheelRange)

    def steering_range_visual(self, index: int | None = None) -> float:
        """Steering visual rotation range"""
        return chknm(self.info.rf2TeleVeh(index).mVisualSteeringWheelRange)

    def force_feedback(self) -> float:
        """Steering force feedback"""
        return chknm(self.info.rf2Ffb.mForceValue)


class Lap(DataAdapter):
    """Lap"""

    __slots__ = ()

    def number(self, index: int | None = None) -> int:
        """Current lap number"""
        return chknm(self.info.rf2TeleVeh(index).mLapNumber)

    def completed_laps(self, index: int | None = None) -> int:
        """Total completed laps"""
        return chknm(self.info.rf2ScorVeh(index).mTotalLaps)

    def track_length(self) -> float:
        """Full lap or track length"""
        return chknm(self.info.rf2ScorInfo.mLapDist)

    def distance(self, index: int | None = None) -> float:
        """Distance into lap"""
        return chknm(self.info.rf2ScorVeh(index).mLapDist)

    def progress(self, index: int | None = None) -> float:
        """Lap progress fraction (distance into lap)"""
        return lap_progress_distance(
            chknm(self.info.rf2ScorVeh(index).mLapDist),
            chknm(self.info.rf2ScorInfo.mLapDist))

    def maximum(self) -> int:
        """Maximum lap"""
        return chknm(self.info.rf2ScorInfo.mMaxLaps)

    def sector_index(self, index: int | None = None) -> int:
        """Sector index - convert to 0,1,2 order"""
        return RF2_SECTORS[int(chknm(self.info.rf2ScorVeh(index).mSector))]

    def behind_leader(self, index: int | None = None) -> int:
        """Laps behind leader"""
        return chknm(self.info.rf2ScorVeh(index).mLapsBehindLeader)

    def behind_next(self, index: int | None = None) -> int:
        """Laps behind next place"""
        return chknm(self.info.rf2ScorVeh(index).mLapsBehindNext)


class Session(DataAdapter):
    """Session"""

    __slots__ = ()

    def elapsed(self) -> float:
        """Session elapsed time"""
        return chknm(self.info.rf2ScorInfo.mCurrentET)

    def start(self) -> float:
        """Session start time"""
        return chknm(self.info.rf2ScorInfo.mStartET)

    def end(self) -> float:
        """Session end time"""
        return chknm(self.info.rf2ScorInfo.mEndET)

    def remaining(self) -> float:
        """Session time remaining"""
        return self.end() - self.elapsed()

    def session_type(self) -> int:
        """Session type"""
        return RF2_SESSION_TYPE[int(chknm(self.info.rf2ScorInfo.mSession))]

    def lap_type(self) -> bool:
        """Is lap type session, false for time type"""
        return chknm(self.info.rf2ScorInfo.mMaxLaps) < 99999

    def in_race(self) -> bool:
        """Is in race session"""
        return chknm(self.info.rf2ScorInfo.mSession) > 9

    def in_countdown(self) -> bool:
        """Is in countdown phase before race"""
        return self.info.rf2ScorInfo.mGamePhase == 4

    def in_formation(self) -> bool:
        """Is in formation phase before race"""
        return self.info.rf2ScorInfo.mGamePhase == 3

    def pit_open(self) -> bool:
        """Is pit lane open"""
        return chknm(self.info.rf2ScorInfo.mGamePhase) > 0

    def green_flag(self) -> bool:
        """Green flag"""
        # Inaccurate due to 5FPS refresh rate from API
        return self.info.rf2ScorInfo.mGamePhase == 5

    def blue_flag(self, index: int | None = None) -> bool:
        """Is under blue flag"""
        return self.info.rf2ScorVeh(index).mFlag == 6

    def yellow_flag(self) -> bool:
        """Is there yellow flag in any sectors"""
        sec_flag = self.info.rf2ScorInfo.mSectorFlag
        return any(data == 1 for data in sec_flag)

    def start_lights(self) -> int:
        """Start lights countdown sequence"""
        scor = self.info.rf2ScorInfo
        return chknm(scor.mNumRedLights) - chknm(scor.mStartLight) + 1

    def track_name(self) -> str:
        """Track name"""
        return cs2py(self.info.rf2ScorInfo.mTrackName)

    def track_temperature(self) -> float:
        """Track temperature"""
        return chknm(self.info.rf2ScorInfo.mTrackTemp)

    def ambient_temperature(self) -> float:
        """Ambient temperature"""
        return chknm(self.info.rf2ScorInfo.mAmbientTemp)

    def raininess(self) -> float:
        """Rain percentage"""
        return chknm(self.info.rf2ScorInfo.mRaining)

    def wetness_minimum(self) -> float:
        """Road minimum wetness"""
        return chknm(self.info.rf2ScorInfo.mMinPathWetness)

    def wetness_maximum(self) -> float:
        """Road maximum wetness"""
        return chknm(self.info.rf2ScorInfo.mMaxPathWetness)

    def wetness_average(self) -> float:
        """Road average wetness"""
        return chknm(self.info.rf2ScorInfo.mAvgPathWetness)

    def wetness(self) -> tuple[float]:
        """Road wetness set"""
        scor = self.info.rf2ScorInfo
        return (chknm(scor.mMinPathWetness),
                chknm(scor.mMaxPathWetness),
                chknm(scor.mAvgPathWetness))


class Switch(DataAdapter):
    """Switch"""

    __slots__ = ()

    def headlights(self, index: int | None = None) -> int:
        """Headlights"""
        return chknm(self.info.rf2TeleVeh(index).mHeadlights)

    def ignition_starter(self, index: int | None = None) -> int:
        """Ignition"""
        return chknm(self.info.rf2TeleVeh(index).mIgnitionStarter)

    def speed_limiter(self, index: int | None = None) -> int:
        """Speed limiter"""
        return chknm(self.info.rf2TeleVeh(index).mSpeedLimiter)

    def drs_status(self, index: int | None = None) -> int:
        """DRS status - 0 not_available, 1 available, 2 allowed(not activated), 3 activated"""
        tele_veh = self.info.rf2TeleVeh(index)
        status = tele_veh.mRearFlapLegalStatus
        if status == 1:
            return 1  # available
        if status == 2:
            if tele_veh.mRearFlapActivated:
                return 3  # activated
            return 2  # allowed
        return 0  # not_available

    def auto_clutch(self) -> int:
        """Auto clutch"""
        return chknm(self.info.rf2Ext.mPhysics.mAutoClutch)


class Timing(DataAdapter):
    """Timing"""

    __slots__ = ()

    def start(self, index: int | None = None) -> float:
        """Current lap start time"""
        return chknm(self.info.rf2TeleVeh(index).mLapStartET)

    def elapsed(self, index: int | None = None) -> float:
        """Current lap elapsed time"""
        return chknm(self.info.rf2TeleVeh(index).mElapsedTime)

    def current_laptime(self, index: int | None = None) -> float:
        """Current lap time"""
        tele_veh = self.info.rf2TeleVeh(index)
        return chknm(tele_veh.mElapsedTime) - chknm(tele_veh.mLapStartET)

    def last_laptime(self, index: int | None = None) -> float:
        """Last lap time"""
        return chknm(self.info.rf2ScorVeh(index).mLastLapTime)

    def best_laptime(self, index: int | None = None) -> float:
        """Best lap time"""
        return chknm(self.info.rf2ScorVeh(index).mBestLapTime)

    def estimated_laptime(self, index: int | None = None) -> float:
        """Estimated lap time"""
        return chknm(self.info.rf2ScorVeh(index).mEstimatedLapTime)

    def estimated_time_into(self, index: int | None = None) -> float:
        """Estimated time into lap"""
        return chknm(self.info.rf2ScorVeh(index).mTimeIntoLap)

    def current_sector1(self, index: int | None = None) -> float:
        """Current lap sector 1 time"""
        return chknm(self.info.rf2ScorVeh(index).mCurSector1)

    def current_sector2(self, index: int | None = None) -> float:
        """Current lap sector 1+2 time"""
        return chknm(self.info.rf2ScorVeh(index).mCurSector2)

    def last_sector1(self, index: int | None = None) -> float:
        """Last lap sector 1 time"""
        return chknm(self.info.rf2ScorVeh(index).mLastSector1)

    def last_sector2(self, index: int | None = None) -> float:
        """Last lap sector 1+2 time"""
        return chknm(self.info.rf2ScorVeh(index).mLastSector2)

    def best_sector1(self, index: int | None = None) -> float:
        """Best lap sector 1 time"""
        return chknm(self.info.rf2ScorVeh(index).mBestSector1)

    def best_sector2(self, index: int | None = None) -> float:
        """Best lap sector 1+2 time"""
        return chknm(self.info.rf2ScorVeh(index).mBestSector2)

    def behind_leader(self, index: int | None = None) -> float:
        """Time behind leader"""
        return chknm(self.info.rf2ScorVeh(index).mTimeBehindLeader)

    def behind_next(self, index: int | None = None) -> float:
        """Time behind next place"""
        return chknm(self.info.rf2ScorVeh(index).mTimeBehindNext)


class Tyre(DataAdapter):
    """Tyre"""

    __slots__ = ()

    def compound_front(self, index: int | None = None) -> int:
        """Tyre compound - front"""
        return chknm(self.info.rf2TeleVeh(index).mFrontTireCompoundIndex)

    def compound_rear(self, index: int | None = None) -> int:
        """Tyre compound - rear"""
        return chknm(self.info.rf2TeleVeh(index).mRearTireCompoundIndex)

    def compound(self, index: int | None = None) -> tuple[int]:
        """Tyre compound set"""
        tele_veh = self.info.rf2TeleVeh(index)
        return chknm(tele_veh.mFrontTireCompoundIndex), chknm(tele_veh.mRearTireCompoundIndex)

    def surface_temperature_avg(self, index: int | None = None) -> list[float]:
        """Tyre surface temperature set - average"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [
            chknm(mean(wheel_data[0].mTemperature)) - 273.15,
            chknm(mean(wheel_data[1].mTemperature)) - 273.15,
            chknm(mean(wheel_data[2].mTemperature)) - 273.15,
            chknm(mean(wheel_data[3].mTemperature)) - 273.15,
        ]

    def surface_temperature_ico(self, index: int | None = None) -> list[float]:
        """Tyre surface temperature set - inner,center,outer"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [
            chknm(wheel_data[0].mTemperature[0]) - 273.15,
            chknm(wheel_data[0].mTemperature[1]) - 273.15,
            chknm(wheel_data[0].mTemperature[2]) - 273.15,
            chknm(wheel_data[1].mTemperature[0]) - 273.15,
            chknm(wheel_data[1].mTemperature[1]) - 273.15,
            chknm(wheel_data[1].mTemperature[2]) - 273.15,
            chknm(wheel_data[2].mTemperature[0]) - 273.15,
            chknm(wheel_data[2].mTemperature[1]) - 273.15,
            chknm(wheel_data[2].mTemperature[2]) - 273.15,
            chknm(wheel_data[3].mTemperature[0]) - 273.15,
            chknm(wheel_data[3].mTemperature[1]) - 273.15,
            chknm(wheel_data[3].mTemperature[2]) - 273.15,
        ]

    def inner_temperature_avg(self, index: int | None = None) -> list[float]:
        """Tyre inner temperature set - average"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [
            chknm(mean(wheel_data[0].mTireInnerLayerTemperature)) - 273.15,
            chknm(mean(wheel_data[1].mTireInnerLayerTemperature)) - 273.15,
            chknm(mean(wheel_data[2].mTireInnerLayerTemperature)) - 273.15,
            chknm(mean(wheel_data[3].mTireInnerLayerTemperature)) - 273.15,
        ]

    def inner_temperature_ico(self, index: int | None = None) -> list[float]:
        """Tyre inner temperature set - inner,center,outer"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [
            chknm(wheel_data[0].mTireInnerLayerTemperature[0]) - 273.15,
            chknm(wheel_data[0].mTireInnerLayerTemperature[1]) - 273.15,
            chknm(wheel_data[0].mTireInnerLayerTemperature[2]) - 273.15,
            chknm(wheel_data[1].mTireInnerLayerTemperature[0]) - 273.15,
            chknm(wheel_data[1].mTireInnerLayerTemperature[1]) - 273.15,
            chknm(wheel_data[1].mTireInnerLayerTemperature[2]) - 273.15,
            chknm(wheel_data[2].mTireInnerLayerTemperature[0]) - 273.15,
            chknm(wheel_data[2].mTireInnerLayerTemperature[1]) - 273.15,
            chknm(wheel_data[2].mTireInnerLayerTemperature[2]) - 273.15,
            chknm(wheel_data[3].mTireInnerLayerTemperature[0]) - 273.15,
            chknm(wheel_data[3].mTireInnerLayerTemperature[1]) - 273.15,
            chknm(wheel_data[3].mTireInnerLayerTemperature[2]) - 273.15,
        ]

    def pressure(self, index: int | None = None) -> list[float]:
        """Tyre pressure"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mPressure) for data in wheel_data]

    def load(self, index: int | None = None) -> list[float]:
        """Tyre load"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mTireLoad) for data in wheel_data]

    def wear(self, index: int | None = None, scale: float = 1) -> list[float]:
        """Tyre wear"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mWear) * scale for data in wheel_data]

    def carcass_temperature(self, index: int | None = None) -> list[float]:
        """Tyre carcass temperature"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mTireCarcassTemperature) - 273.15 for data in wheel_data]


class Vehicle(DataAdapter):
    """Vehicle"""

    __slots__ = ()

    def is_player(self, index: int=0) -> bool:
        """Is local player"""
        return self.info.isPlayer(index)

    def is_driving(self) -> bool:
        """Is local player driving or in monitor"""
        return self.info.rf2TeleVeh().mIgnitionStarter

    def player_index(self) -> int:
        """Get Local player index"""
        return self.info.playerIndex

    def slot_id(self, index: int | None = None) -> int:
        """Vehicle slot id"""
        return chknm(self.info.rf2ScorVeh(index).mID)

    def driver_name(self, index: int | None = None) -> str:
        """Driver name"""
        return cs2py(self.info.rf2ScorVeh(index).mDriverName)

    def vehicle_name(self, index: int | None = None) -> str:
        """Vehicle name"""
        return cs2py(self.info.rf2ScorVeh(index).mVehicleName)

    def class_name(self, index: int | None = None) -> str:
        """Vehicle class name"""
        return cs2py(self.info.rf2ScorVeh(index).mVehicleClass)

    def same_class(self, index: int | None = None) -> bool:
        """Is same vehicle class"""
        return self.class_name(index) == self.class_name()

    def total_vehicles(self) -> int:
        """Total vehicles"""
        return chknm(self.info.rf2ScorInfo.mNumVehicles)

    def place(self, index: int | None = None) -> int:
        """Vehicle overall place"""
        return chknm(self.info.rf2ScorVeh(index).mPlace)

    def in_pits(self, index: int | None = None) -> bool:
        """Is in pits"""
        return chknm(self.info.rf2ScorVeh(index).mInPits)

    def in_garage(self, index: int | None = None) -> bool:
        """Is in garage"""
        return chknm(self.info.rf2ScorVeh(index).mInGarageStall)

    def number_pitstops(self, index: int | None = None) -> int:
        """Number of pit stops"""
        return chknm(self.info.rf2ScorVeh(index).mNumPitstops)

    def number_penalties(self, index: int | None = None) -> int:
        """Number of penalties"""
        return chknm(self.info.rf2ScorVeh(index).mNumPenalties)

    def pit_state(self, index: int | None = None) -> int:
        """Pit state, 0 = none, 1 = request, 2 = entering, 3 = stopped, 4 = exiting"""
        return chknm(self.info.rf2ScorVeh(index).mPitState)

    def finish_state(self, index: int | None = None) -> int:
        """Finish state, 0 = none, 1 = finished, 2 = DNF, 3 = DQ"""
        return chknm(self.info.rf2ScorVeh(index).mFinishStatus)

    def fuel(self, index: int | None = None) -> float:
        """Remaining fuel"""
        return chknm(self.info.rf2TeleVeh(index).mFuel)

    def tank_capacity(self, index: int | None = None) -> float:
        """Fuel tank capacity"""
        return chknm(self.info.rf2TeleVeh(index).mFuelCapacity)

    def orientation_yaw_radians(self, index: int | None = None) -> float:
        """Orientation yaw (radians)"""
        ori = self.info.rf2TeleVeh(index).mOri[2]
        return oriyaw2rad(chknm(ori.x), chknm(ori.z))

    def position_xyz(self, index: int | None = None) -> tuple[float]:
        """Raw XYZ position"""
        pos = self.info.rf2TeleVeh(index).mPos
        return chknm(pos.x), chknm(pos.y), chknm(pos.z)

    def position_longitudinal(self, index: int | None = None) -> float:
        """Longitudinal axis position related to world plane"""
        return chknm(self.info.rf2TeleVeh(index).mPos.x)  # in RF2 coord system

    def position_lateral(self, index: int | None = None) -> float:
        """Lateral axis position related to world plane"""
        return -chknm(self.info.rf2TeleVeh(index).mPos.z)  # in RF2 coord system

    def position_vertical(self, index: int | None = None) -> float:
        """Vertical axis position related to world plane"""
        return chknm(self.info.rf2TeleVeh(index).mPos.y)  # in RF2 coord system

    def accel_lateral(self, index: int | None = None) -> float:
        """Lateral acceleration"""
        return chknm(self.info.rf2TeleVeh(index).mLocalAccel.x)  # X in RF2 coord system

    def accel_longitudinal(self, index: int | None = None) -> float:
        """Longitudinal acceleration"""
        return chknm(self.info.rf2TeleVeh(index).mLocalAccel.z)  # Z in RF2 coord system

    def accel_vertical(self, index: int | None = None) -> float:
        """Vertical acceleration"""
        return chknm(self.info.rf2TeleVeh(index).mLocalAccel.y)  # Y in RF2 coord system

    def velocity_lateral(self, index: int | None = None) -> float:
        """Lateral velocity (x)"""
        return chknm(self.info.rf2TeleVeh(index).mLocalVel.x)  # X in RF2 coord system

    def velocity_longitudinal(self, index: int | None = None) -> float:
        """Longitudinal velocity (y)"""
        return chknm(self.info.rf2TeleVeh(index).mLocalVel.z)  # Z in RF2 coord system

    def velocity_vertical(self, index: int | None = None) -> float:
        """Vertical velocity (z)"""
        return chknm(self.info.rf2TeleVeh(index).mLocalVel.y)  # Y in RF2 coord system

    def speed(self, index: int | None = None) -> float:
        """Speed"""
        vel = self.info.rf2TeleVeh(index).mLocalVel
        return vel2speed(chknm(vel.x), chknm(vel.y), chknm(vel.z))

    def downforce_front(self, index: int | None = None) -> float:
        """Downforce front"""
        return chknm(self.info.rf2TeleVeh(index).mFrontDownforce)

    def downforce_rear(self, index: int | None = None) -> float:
        """Downforce rear"""
        return chknm(self.info.rf2TeleVeh(index).mRearDownforce)

    def damage_severity(self, index: int | None = None) -> tuple[int]:
        """Damage severity, sort row by row from left to right, top to bottom"""
        dmg = self.info.rf2TeleVeh(index).mDentSeverity
        return dmg[1], dmg[0], dmg[7], dmg[2], dmg[6], dmg[3], dmg[4], dmg[5]  # RF2 order

    def is_detached(self, index: int | None = None) -> bool:
        """Whether any vehicle parts are detached"""
        return chknm(self.info.rf2TeleVeh(index).mDetached)

    def impact_time(self, index: int | None = None) -> float:
        """Last impact time stamp"""
        return chknm(self.info.rf2TeleVeh(index).mLastImpactET)

    def impact_magnitude(self, index: int | None = None) -> float:
        """Last impact magnitude"""
        return chknm(self.info.rf2TeleVeh(index).mLastImpactMagnitude)

    def impact_position(self, index: int | None = None) -> list[float]:
        """Last impact position - x,y coordinates"""
        pos = self.info.rf2TeleVeh(index).mLastImpactPos
        return -chknm(pos.x), chknm(pos.z)


class Wheel(DataAdapter):
    """Wheel & suspension"""

    __slots__ = ()

    def camber(self, index: int | None = None) -> list[float]:
        """Wheel camber (radians)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mCamber) for data in wheel_data]

    def toe(self, index: int | None = None) -> list[float]:
        """Wheel toe (radians)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mToe) for data in wheel_data]

    def toe_symmetric(self, index: int | None = None) -> list[float]:
        """Wheel toe symmetric (radians)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(wheel_data[0].mToe),
                -chknm(wheel_data[1].mToe),
                chknm(wheel_data[2].mToe),
                -chknm(wheel_data[3].mToe)]

    def rotation(self, index: int | None = None) -> list[float]:
        """Wheel rotation (radians per second)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mRotation) for data in wheel_data]

    def velocity_longitudinal(self, index: int | None = None) -> list[float]:
        """Longitudinal velocity"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mLongitudinalGroundVel) for data in wheel_data]

    def velocity_lateral(self, index: int | None = None) -> list[float]:
        """Lateral velocity"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mLateralGroundVel) for data in wheel_data]

    def slip_angle_fl(self, index: int | None = None) -> float:
        """Slip angle (radians) front left"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels[0]
        return slip_angle(
            chknm(wheel_data.mLateralGroundVel),
            chknm(wheel_data.mLongitudinalGroundVel))

    def slip_angle_fr(self, index: int | None = None) -> float:
        """Slip angle (radians) front right"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels[1]
        return slip_angle(
            chknm(wheel_data.mLateralGroundVel),
            chknm(wheel_data.mLongitudinalGroundVel))

    def slip_angle_rl(self, index: int | None = None) -> float:
        """Slip angle (radians) rear left"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels[2]
        return slip_angle(
            chknm(wheel_data.mLateralGroundVel),
            chknm(wheel_data.mLongitudinalGroundVel))

    def slip_angle_rr(self, index: int | None = None) -> float:
        """Slip angle (radians) rear right"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels[3]
        return slip_angle(
            chknm(wheel_data.mLateralGroundVel),
            chknm(wheel_data.mLongitudinalGroundVel))

    def ride_height(self, index: int | None = None) -> list[float]:
        """Ride height (millmeters)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [meter2millmeter(chknm(data.mRideHeight)) for data in wheel_data]

    def suspension_deflection(self, index: int | None = None) -> list[float]:
        """Suspension deflection (millmeters)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [meter2millmeter(chknm(data.mSuspensionDeflection)) for data in wheel_data]

    def suspension_force(self, index: int | None = None) -> list[float]:
        """Suspension force (Newtons)"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mSuspForce) for data in wheel_data]

    def is_detached(self, index: int | None = None) -> list[bool]:
        """Whether wheel is detached"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return [chknm(data.mDetached) for data in wheel_data]

    def is_offroad(self, index: int | None = None) -> bool:
        """Whether all wheels are complete offroad"""
        wheel_data = self.info.rf2TeleVeh(index).mWheels
        return all(2 <= chknm(data.mSurfaceType) <= 4 for data in wheel_data)
