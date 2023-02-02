#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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

import re
from pyRfactor2SharedMemory.sharedMemoryAPI import SimInfoAPI, Cbytestring2Python

from . import calculation as calc


# Load Shared Memory API
info = SimInfoAPI()
info.startUpdating()  # start Shared Memory updating thread

chknm = calc.in2zero
cs2py = Cbytestring2Python


def state():
    """Check whether is driving"""
    return info.syncedVehicleTelemetry().mIgnitionStarter != 0


def combo_check():
    """Track & vehicle combo data"""
    name_class = cs2py(info.syncedVehicleScoring().mVehicleClass)
    name_track = cs2py(info.LastScor.mScoringInfo.mTrackName)
    return re.sub('[\\\\/:*?"<>|]', "", f"{name_track} - {name_class}")


def cruise():
    """Cruise data"""
    ori_yaw = (chknm(info.syncedVehicleTelemetry().mOri[2].x),
               chknm(info.syncedVehicleTelemetry().mOri[2].z))
    pos_y = round(chknm(info.syncedVehicleScoring().mPos.y), 1)
    time_start = int(chknm(info.LastScor.mScoringInfo.mStartET))
    time_curr = int(chknm(info.LastScor.mScoringInfo.mCurrentET))
    return ori_yaw, pos_y, time_start, time_curr


def instrument():
    """Instrument data"""
    headlights = chknm(info.syncedVehicleTelemetry().mHeadlights)
    ignition = chknm(info.syncedVehicleTelemetry().mIgnitionStarter)
    rpm = chknm(info.syncedVehicleTelemetry().mEngineRPM)
    autoclutch = chknm(info.LastExt.mPhysics.mAutoClutch)
    clutch = chknm(info.syncedVehicleTelemetry().mFilteredClutch)
    brake = chknm(info.syncedVehicleTelemetry().mFilteredBrake)
    wheel_rot = (chknm(info.syncedVehicleTelemetry().mWheels[0].mRotation),
                 chknm(info.syncedVehicleTelemetry().mWheels[1].mRotation),
                 chknm(info.syncedVehicleTelemetry().mWheels[2].mRotation),
                 chknm(info.syncedVehicleTelemetry().mWheels[3].mRotation))
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    return headlights, ignition, rpm, autoclutch, clutch, brake, wheel_rot, speed


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
    steering_wheel_rot_range = chknm(info.syncedVehicleTelemetry().mPhysicalSteeringWheelRange)
    return raw_steering, steering_wheel_rot_range


def gear():
    """Gear data"""
    pit_limiter = chknm(info.syncedVehicleTelemetry().mSpeedLimiter)
    mgear = chknm(info.syncedVehicleTelemetry().mGear)
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    rpm = chknm(info.syncedVehicleTelemetry().mEngineRPM)
    rpm_max = chknm(info.syncedVehicleTelemetry().mEngineMaxRPM)
    race_phase = chknm(info.LastScor.mScoringInfo.mGamePhase)
    curr_session = chknm(info.LastScor.mScoringInfo.mSession)
    return pit_limiter, mgear, speed, rpm, rpm_max, race_phase, curr_session


def blue_flag():
    """Blue flag data"""
    blue = chknm(info.syncedVehicleScoring().mFlag)
    return blue


def yellow_flag():
    """Yellow flag data"""
    yellow_s1 = chknm(info.LastScor.mScoringInfo.mSectorFlag[0])
    yellow_s2 = chknm(info.LastScor.mScoringInfo.mSectorFlag[1])
    yellow_s3 = chknm(info.LastScor.mScoringInfo.mSectorFlag[2])
    return yellow_s1, yellow_s2, yellow_s3


def lap_timestamp():
    """lap timestamp data"""
    lap_start = chknm(info.syncedVehicleTelemetry().mLapStartET)
    lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    return lap_start - lap_etime


def startlights():
    """Startlights data"""
    lights_frame = chknm(info.LastScor.mScoringInfo.mStartLight)
    lights_number = chknm(info.LastScor.mScoringInfo.mNumRedLights) + 1
    return lights_number - lights_frame


def session():
    """Session data"""
    time_left = chknm(info.LastScor.mScoringInfo.mEndET) - chknm(info.LastScor.mScoringInfo.mCurrentET)
    lap_total = chknm(info.LastScor.mScoringInfo.mMaxLaps)
    lap_num = chknm(info.syncedVehicleTelemetry().mLapNumber)
    plr_place = chknm(info.syncedVehicleScoring().mPlace)
    veh_total = chknm(info.LastTele.mNumVehicles)
    lap_into = min(max(chknm(info.syncedVehicleScoring().mLapDist) * 100
                       / max(chknm(info.LastScor.mScoringInfo.mLapDist), 1), 0), 99)
    return time_left, lap_total, lap_num, plr_place, veh_total, lap_into


def stint():
    """Stint data"""
    lap_num = chknm(info.syncedVehicleTelemetry().mLapNumber)
    wear_avg = 100 - (sum([chknm(info.syncedVehicleTelemetry().mWheels[data].mWear)
                           for data in range(4)]) * 25)
    fuel_curr = chknm(info.syncedVehicleTelemetry().mFuel)
    time_curr = chknm(info.LastScor.mScoringInfo.mCurrentET)
    inpits = chknm(info.syncedVehicleScoring().mInPits)
    tire_idx = (chknm(info.syncedVehicleTelemetry().mFrontTireCompoundIndex),
                chknm(info.syncedVehicleTelemetry().mRearTireCompoundIndex))
    game_phase = chknm(info.LastScor.mScoringInfo.mGamePhase)
    return lap_num, wear_avg, fuel_curr, time_curr, inpits, tire_idx, game_phase


def camber():
    """Camber data"""
    raw_camber = (chknm(info.syncedVehicleTelemetry().mWheels[0].mCamber),
                  chknm(info.syncedVehicleTelemetry().mWheels[1].mCamber),
                  chknm(info.syncedVehicleTelemetry().mWheels[2].mCamber),
                  chknm(info.syncedVehicleTelemetry().mWheels[3].mCamber))
    return raw_camber


def toe():
    """Toe data"""
    raw_toe = (chknm(info.syncedVehicleTelemetry().mWheels[0].mToe),
               -chknm(info.syncedVehicleTelemetry().mWheels[1].mToe),
               chknm(info.syncedVehicleTelemetry().mWheels[2].mToe),
               -chknm(info.syncedVehicleTelemetry().mWheels[3].mToe))
    return raw_toe


def ride_height():
    """Ride height data"""
    height = (chknm(info.syncedVehicleTelemetry().mWheels[0].mRideHeight),
              chknm(info.syncedVehicleTelemetry().mWheels[1].mRideHeight),
              chknm(info.syncedVehicleTelemetry().mWheels[2].mRideHeight),
              chknm(info.syncedVehicleTelemetry().mWheels[3].mRideHeight))
    return height


def temperature():
    """Temperature data"""
    ttemp_fl = sum([chknm(info.syncedVehicleTelemetry().mWheels[0].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_fr = sum([chknm(info.syncedVehicleTelemetry().mWheels[1].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_rl = sum([chknm(info.syncedVehicleTelemetry().mWheels[2].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_rr = sum([chknm(info.syncedVehicleTelemetry().mWheels[3].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    btemp = (chknm(info.syncedVehicleTelemetry().mWheels[0].mBrakeTemp) - 273.15,
             chknm(info.syncedVehicleTelemetry().mWheels[1].mBrakeTemp) - 273.15,
             chknm(info.syncedVehicleTelemetry().mWheels[2].mBrakeTemp) - 273.15,
             chknm(info.syncedVehicleTelemetry().mWheels[3].mBrakeTemp) - 273.15)
    return (ttemp_fl, ttemp_fr, ttemp_rl, ttemp_rr), btemp


def wear():
    """Tyre wear data"""
    start_curr = chknm(info.syncedVehicleTelemetry().mLapStartET)
    lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    wear_curr = (chknm(info.syncedVehicleTelemetry().mWheels[0].mWear) * 100,
                 chknm(info.syncedVehicleTelemetry().mWheels[1].mWear) * 100,
                 chknm(info.syncedVehicleTelemetry().mWheels[2].mWear) * 100,
                 chknm(info.syncedVehicleTelemetry().mWheels[3].mWear) * 100)
    return start_curr, lap_etime, wear_curr


def tyre_load():
    """Tyre load data"""
    raw_load = (chknm(info.syncedVehicleTelemetry().mWheels[0].mTireLoad),
                chknm(info.syncedVehicleTelemetry().mWheels[1].mTireLoad),
                chknm(info.syncedVehicleTelemetry().mWheels[2].mTireLoad),
                chknm(info.syncedVehicleTelemetry().mWheels[3].mTireLoad))
    return raw_load


def tyre_pressure():
    """Tyre pressure data"""
    pressure = (chknm(info.syncedVehicleTelemetry().mWheels[0].mPressure),
                chknm(info.syncedVehicleTelemetry().mWheels[1].mPressure),
                chknm(info.syncedVehicleTelemetry().mWheels[2].mPressure),
                chknm(info.syncedVehicleTelemetry().mWheels[3].mPressure))
    return pressure


def force():
    """Force data"""
    lgt_accel = chknm(info.syncedVehicleTelemetry().mLocalAccel.z)
    lat_accel = chknm(info.syncedVehicleTelemetry().mLocalAccel.x)
    downforce = (chknm(info.syncedVehicleTelemetry().mFrontDownforce),
                 chknm(info.syncedVehicleTelemetry().mRearDownforce))
    return lgt_accel, lat_accel, downforce


def drs():
    """DRS data"""
    drs_on = chknm(info.syncedVehicleTelemetry().mRearFlapActivated)
    drs_status = chknm(info.syncedVehicleTelemetry().mRearFlapLegalStatus)
    return drs_on, drs_status


def engine():
    """Engine data"""
    temp_oil = chknm(info.syncedVehicleTelemetry().mEngineOilTemp)
    temp_water = chknm(info.syncedVehicleTelemetry().mEngineWaterTemp)
    e_turbo = chknm(info.syncedVehicleTelemetry().mTurboBoostPressure)
    e_rpm = chknm(info.syncedVehicleTelemetry().mEngineRPM)
    return temp_oil, temp_water, e_turbo, e_rpm


def weather():
    """Weather data"""
    amb_temp = chknm(info.LastScor.mScoringInfo.mAmbientTemp)
    trk_temp = chknm(info.LastScor.mScoringInfo.mTrackTemp)
    rain = chknm(info.LastScor.mScoringInfo.mRaining) * 100
    min_wet = chknm(info.LastScor.mScoringInfo.mMinPathWetness) * 100
    max_wet = chknm(info.LastScor.mScoringInfo.mMaxPathWetness) * 100
    avg_wet = chknm(info.LastScor.mScoringInfo.mAvgPathWetness) * 100
    return amb_temp, trk_temp, rain, min_wet, max_wet, avg_wet


def sector():
    """Sector data"""
    mSector = chknm(info.syncedVehicleScoring().mSector)
    mCurSector1 = chknm(info.syncedVehicleScoring().mCurSector1)
    mCurSector2 = chknm(info.syncedVehicleScoring().mCurSector2)
    mLastSector2 = chknm(info.syncedVehicleScoring().mLastSector2)
    mLastLapTime = chknm(info.syncedVehicleScoring().mLastLapTime)
    mTotalLaps = chknm(info.syncedVehicleScoring().mTotalLaps) + 1
    mPlace = chknm(info.syncedVehicleScoring().mPlace)
    mElapsedTime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
    speed = calc.vel2speed(chknm(info.syncedVehicleTelemetry().mLocalVel.x),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.y),
                           chknm(info.syncedVehicleTelemetry().mLocalVel.z))
    start_curr = chknm(info.syncedVehicleTelemetry().mLapStartET)
    return (mSector, mCurSector1, mCurSector2, mLastSector2, mLastLapTime,
            mTotalLaps, mPlace, mElapsedTime, speed, start_curr)


def session_check():
    """Check session time stamp, type, elapsed time, completed laps"""
    session_length = chknm(info.LastScor.mScoringInfo.mEndET)
    session_type = chknm(info.LastScor.mScoringInfo.mSession)
    session_stamp = f"{session_length:.0f}{session_type:.0f}"
    session_etime = int(chknm(info.LastScor.mScoringInfo.mCurrentET))
    session_tlaps = chknm(info.syncedVehicleScoring().mTotalLaps)
    return session_stamp, session_etime, session_tlaps
