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
Read & sort data into groups.

Access rF2 shared memory data using:
 - The Iron Wolf’s rF2 Shared Memory Map Plugin
   https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin

 - Tony Whitley’s pyRfactor2SharedMemory Library
   https://github.com/TonyWhitley/pyRfactor2SharedMemory

   Note: TinyPedal currently requires a forked version of pyRfactor2SharedMemory
   that enables access to FFB & additional functions:
   https://github.com/s-victor/pyRfactor2SharedMemory
"""

from pyRfactor2SharedMemory.sharedMemoryAPI import Cbytestring2Python
from pyRfactor2SharedMemory.sim_info_sync import SimInfoSync

from . import validator as val
from . import calculation as calc


# Load Shared Memory API
info = SimInfoSync()
info.startUpdating()  # start Shared Memory updating thread

chknm = val.in2zero
cs2py = Cbytestring2Python


def state():
    """Check whether is driving"""
    return info.syncedVehicleTelemetry().mIgnitionStarter


def api_version():
    """Check API version"""
    version = cs2py(info.LastExt.mVersion)
    if version:
        return cs2py(info.LastExt.mVersion)
    return "unknown"


def combo_check():
    """Track & vehicle combo data"""
    track_name = cs2py(info.LastScor.mScoringInfo.mTrackName)
    class_name = cs2py(info.syncedVehicleScoring().mVehicleClass)
    return val.format_invalid_char(f"{track_name} - {class_name}")


def vehicle_check():
    """Track & vehicle combo data"""
    class_name = cs2py(info.syncedVehicleScoring().mVehicleClass)
    veh_name = cs2py(info.syncedVehicleScoring().mVehicleName)
    return val.format_invalid_char(f"{class_name} - {veh_name}")


def is_race():
    """Is race session"""
    return chknm(info.LastScor.mScoringInfo.mSession) > 9


def lap_timestamp():
    """lap timestamp data"""
    lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
    lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    return lap_stime, lap_etime


def lap_number():
    """Lap number data"""
    return chknm(info.syncedVehicleTelemetry().mLapNumber)


def cruise():
    """Cruise data"""
    ori_yaw = (chknm(info.syncedVehicleTelemetry().mOri[2].x),
               chknm(info.syncedVehicleTelemetry().mOri[2].z))
    time_start = int(chknm(info.LastScor.mScoringInfo.mStartET))
    track_time = int(chknm(info.LastScor.mScoringInfo.mCurrentET))
    pos_y = round(chknm(info.syncedVehicleScoring().mPos.y), 1)
    return ori_yaw, pos_y, time_start, track_time


def instrument():
    """Instrument data"""
    headlights = chknm(info.syncedVehicleTelemetry().mHeadlights)
    ignition = (chknm(info.syncedVehicleTelemetry().mIgnitionStarter),
                chknm(info.syncedVehicleTelemetry().mEngineRPM))
    clutch = (chknm(info.LastExt.mPhysics.mAutoClutch),
              chknm(info.syncedVehicleTelemetry().mFilteredClutch))
    brake = bool(chknm(info.syncedVehicleTelemetry().mFilteredBrake) > 0)
    wheel_rot = [chknm(info.syncedVehicleTelemetry().mWheels[data].mRotation)
                 for data in range(4)]
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    return headlights, ignition, clutch, brake, wheel_rot, speed


def pedal():
    """Pedal data"""
    throttle = chknm(info.syncedVehicleTelemetry().mFilteredThrottle)
    brake = chknm(info.syncedVehicleTelemetry().mFilteredBrake)
    clutch = chknm(info.syncedVehicleTelemetry().mFilteredClutch)
    raw_throttle = chknm(info.syncedVehicleTelemetry().mUnfilteredThrottle)
    raw_brake = chknm(info.syncedVehicleTelemetry().mUnfilteredBrake)
    raw_clutch = chknm(info.syncedVehicleTelemetry().mUnfilteredClutch)
    ffb = chknm(info.LastFfb.mForceValue)
    return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb


def steering():
    """Steering data"""
    raw_steering = chknm(info.syncedVehicleTelemetry().mUnfilteredSteering)
    sw_rot_range = chknm(info.syncedVehicleTelemetry().mPhysicalSteeringWheelRange)
    return raw_steering, sw_rot_range


def gauge():
    """Gauge data"""
    limiter = chknm(info.syncedVehicleTelemetry().mSpeedLimiter)
    mgear = chknm(info.syncedVehicleTelemetry().mGear)
    max_gear = chknm(info.syncedVehicleTelemetry().mMaxGears)
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    rpm = chknm(info.syncedVehicleTelemetry().mEngineRPM)
    rpm_max = chknm(info.syncedVehicleTelemetry().mEngineMaxRPM)
    lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    return limiter, mgear, max_gear, speed, rpm, rpm_max, lap_etime


def p2p():
    """P2P data"""
    mgear = chknm(info.syncedVehicleTelemetry().mGear)
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    throttle = chknm(info.syncedVehicleTelemetry().mUnfilteredThrottle)
    return mgear, speed, throttle


def pitting():
    """Pitting data"""
    inpits = chknm(info.syncedVehicleScoring().mInPits)
    pit_limiter = chknm(info.syncedVehicleTelemetry().mSpeedLimiter)
    race_phase = chknm(info.LastScor.mScoringInfo.mGamePhase)
    return inpits, pit_limiter, race_phase


def blue_flag():
    """Blue flag data"""
    return chknm(info.syncedVehicleScoring().mFlag)


def yellow_flag():
    """Yellow flag data"""
    return (chknm(info.LastScor.mScoringInfo.mSectorFlag[0]),
            chknm(info.LastScor.mScoringInfo.mSectorFlag[1]),
            chknm(info.LastScor.mScoringInfo.mSectorFlag[2]))


def radar():
    """Radar data"""
    lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    ingarage = chknm(info.syncedVehicleScoring().mInGarageStall)
    return lap_etime, ingarage


def startlights():
    """Startlights data"""
    lights_frame = chknm(info.LastScor.mScoringInfo.mStartLight)
    lights_number = chknm(info.LastScor.mScoringInfo.mNumRedLights) + 1
    return lights_number - lights_frame


def session():
    """Session data"""
    time_left = (chknm(info.LastScor.mScoringInfo.mEndET)
                 - chknm(info.LastScor.mScoringInfo.mCurrentET))
    lap_into = int(min(max(chknm(info.syncedVehicleScoring().mLapDist) * 100
                       / max(chknm(info.LastScor.mScoringInfo.mLapDist), 1), 0), 99))
    lap_total = chknm(info.LastScor.mScoringInfo.mMaxLaps)
    plr_position = (chknm(info.syncedVehicleScoring().mPlace),
                 chknm(info.LastTele.mNumVehicles))
    return time_left, lap_into, lap_total, plr_position


def stint():
    """Stint data"""
    time_curr = chknm(info.LastScor.mScoringInfo.mCurrentET)
    inpits = chknm(info.syncedVehicleScoring().mInPits)
    ingarage = chknm(info.syncedVehicleScoring().mInGarageStall)
    return time_curr, inpits, ingarage


def tyre_compound():
    """Tyre compound data"""
    return (chknm(info.syncedVehicleTelemetry().mFrontTireCompoundIndex),
            chknm(info.syncedVehicleTelemetry().mRearTireCompoundIndex))


def camber():
    """Camber data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mCamber)
            for data in range(4)]


def toe():
    """Toe data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mToe)
            for data in range(4)]


def ride_height():
    """Ride height data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mRideHeight)
            for data in range(4)]


def brake_bias():
    """Brake bias data"""
    return chknm(info.syncedVehicleTelemetry().mRearBrakeBias)

def brake_pressure():
    """Brake pressure data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mBrakePressure)
            for data in range(4)]


def brake_temp():
    """Brake temperature data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mBrakeTemp) - 273.15
            for data in range(4)]


def tyre_temp_surface():
    """Tyre surface temperature data"""
    return [[chknm(info.syncedVehicleTelemetry().mWheels[tyre].mTemperature[data]) - 273.15
             for data in range(3)] for tyre in range(4)]


def tyre_temp_innerlayer():
    """Tyre inner layer temperature data"""
    return [[chknm(info.syncedVehicleTelemetry().mWheels[tyre].mTireInnerLayerTemperature[data])
            - 273.15 for data in range(3)] for tyre in range(4)]


def wear():
    """Tyre wear data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mWear)
            for data in range(4)]


def tyre_load():
    """Tyre load data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mTireLoad)
            for data in range(4)]


def tyre_pressure():
    """Tyre pressure data"""
    return [chknm(info.syncedVehicleTelemetry().mWheels[data].mPressure)
            for data in range(4)]


def ground_velocity():
    """Ground velocity data"""
    lat_gv = [chknm(info.syncedVehicleTelemetry().mWheels[data].mLateralGroundVel)
              for data in range(4)]
    lgt_gv = [chknm(info.syncedVehicleTelemetry().mWheels[data].mLongitudinalGroundVel)
              for data in range(4)]
    return lat_gv, lgt_gv


def drs():
    """DRS data"""
    drs_on = chknm(info.syncedVehicleTelemetry().mRearFlapActivated)
    drs_status = chknm(info.syncedVehicleTelemetry().mRearFlapLegalStatus)
    return drs_on, drs_status


def timing(index):
    """Timing data"""
    veh_total = chknm(info.LastTele.mNumVehicles)
    laptime_opt = chknm(info.LastScor.mVehicles[index].mBestLapTime)
    class_opt = cs2py(info.LastScor.mVehicles[index].mVehicleClass)
    class_plr = cs2py(info.syncedVehicleScoring().mVehicleClass)
    return veh_total, laptime_opt, class_opt == class_plr


def electric_motor():
    """Electric motor data"""
    motor_temp = chknm(info.syncedVehicleTelemetry().mElectricBoostMotorTemperature)
    water_temp = chknm(info.syncedVehicleTelemetry().mElectricBoostWaterTemperature)
    motor_rpm = chknm(info.syncedVehicleTelemetry().mElectricBoostMotorRPM)
    motor_torque = chknm(info.syncedVehicleTelemetry().mElectricBoostMotorTorque)
    return motor_temp, water_temp, motor_rpm, motor_torque


def engine():
    """Engine data"""
    temp_oil = chknm(info.syncedVehicleTelemetry().mEngineOilTemp)
    temp_water = chknm(info.syncedVehicleTelemetry().mEngineWaterTemp)
    e_turbo = int(chknm(info.syncedVehicleTelemetry().mTurboBoostPressure))
    e_rpm = int(chknm(info.syncedVehicleTelemetry().mEngineRPM))
    return temp_oil, temp_water, e_turbo, e_rpm


def weather():
    """Weather data"""
    track_temp = chknm(info.LastScor.mScoringInfo.mTrackTemp)
    ambient_temp = chknm(info.LastScor.mScoringInfo.mAmbientTemp)
    rain_per = chknm(info.LastScor.mScoringInfo.mRaining) * 100
    wet_road = (chknm(info.LastScor.mScoringInfo.mMinPathWetness) * 100,
                chknm(info.LastScor.mScoringInfo.mMaxPathWetness) * 100,
                chknm(info.LastScor.mScoringInfo.mAvgPathWetness) * 100)
    return track_temp, ambient_temp, rain_per, wet_road


def sector():
    """Sector data

    Convert game sector index order to 0,1,2 for consistency.
    """
    sector_idx = (2,0,1)[min(max(chknm(info.syncedVehicleScoring().mSector), 0), 2)]
    curr_sector1 = chknm(info.syncedVehicleScoring().mCurSector1)
    curr_sector2 = chknm(info.syncedVehicleScoring().mCurSector2)
    last_sector2 = chknm(info.syncedVehicleScoring().mLastSector2)
    last_laptime = chknm(info.syncedVehicleScoring().mLastLapTime)
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    return sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime, speed


def session_check():
    """Check session time stamp, type, elapsed time, completed laps"""
    session_length = chknm(info.LastScor.mScoringInfo.mEndET)
    session_type = chknm(info.LastScor.mScoringInfo.mSession)
    session_stamp = f"{session_length:.0f}{session_type:.0f}"
    session_etime = int(chknm(info.LastScor.mScoringInfo.mCurrentET))
    session_tlaps = chknm(info.syncedVehicleScoring().mTotalLaps)
    return session_stamp, session_etime, session_tlaps
