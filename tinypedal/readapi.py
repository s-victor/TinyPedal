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

#from pyRfactor2SharedMemory.sharedMemoryAPI import Cbytestring2Python

from tinypedal.__init__ import info
import tinypedal.calculation as calc

chknum = info.in2zero

def state():
    """Check game state"""
    return chknum(info.playersVehicleTelemetry().mIgnitionStarter) != 0


def is_local_player():
    """Check if is local player"""
    if 0 <= chknum(info.playersVehicleScoring().mControl) <= 1:
        return True
    return False


def cruise():
    """Cruise data"""
    ori_yaw = 180 - (calc.oriyaw2rad(chknum(info.playersVehicleTelemetry().mOri[2].x),
                                     chknum(info.playersVehicleTelemetry().mOri[2].z)) * 57.2957795)
    pos_y = chknum(info.playersVehicleScoring().mPos.y)
    time_start = chknum(info.Rf2Scor.mScoringInfo.mStartET)
    time_curr = chknum(info.Rf2Scor.mScoringInfo.mCurrentET)
    return ori_yaw, pos_y, time_start, time_curr


def instrument():
    """Instrument data"""
    headlights = chknum(info.playersVehicleTelemetry().mHeadlights)
    ignition = chknum(info.playersVehicleTelemetry().mIgnitionStarter)
    rpm = chknum(info.playersVehicleTelemetry().mEngineRPM)
    autoclutch = chknum(info.Rf2Ext.mPhysics.mAutoClutch)
    clutch = chknum(info.playersVehicleTelemetry().mFilteredClutch)
    brake = chknum(info.playersVehicleTelemetry().mFilteredBrake)
    wheel_rot = (chknum(info.playersVehicleTelemetry().mWheels[0].mRotation),
                 chknum(info.playersVehicleTelemetry().mWheels[1].mRotation),
                 chknum(info.playersVehicleTelemetry().mWheels[2].mRotation),
                 chknum(info.playersVehicleTelemetry().mWheels[3].mRotation))
    speed = calc.vel2speed(chknum(info.playersVehicleTelemetry().mLocalVel.x),
                           chknum(info.playersVehicleTelemetry().mLocalVel.y),
                           chknum(info.playersVehicleTelemetry().mLocalVel.z))
    return headlights, ignition, rpm, autoclutch, clutch, brake, wheel_rot, speed


def pedal():
    """Pedal data"""
    throttle = chknum(info.playersVehicleTelemetry().mFilteredThrottle)
    brake = chknum(info.playersVehicleTelemetry().mFilteredBrake)
    clutch = chknum(info.playersVehicleTelemetry().mFilteredClutch)
    raw_throttle = chknum(info.playersVehicleTelemetry().mUnfilteredThrottle)
    raw_brake = chknum(info.playersVehicleTelemetry().mUnfilteredBrake)
    raw_clutch = chknum(info.playersVehicleTelemetry().mUnfilteredClutch)
    ffb = chknum(info.Rf2Ffb.mForceValue)
    return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb


def steering():
    """Steering data"""
    raw_steering = chknum(info.playersVehicleTelemetry().mUnfilteredSteering)
    steering_wheel_rot_range = chknum(info.playersVehicleTelemetry().mPhysicalSteeringWheelRange)
    return raw_steering, steering_wheel_rot_range


def gear():
    """Gear data"""
    pit_limiter = chknum(info.playersVehicleTelemetry().mSpeedLimiter)
    mgear = chknum(info.playersVehicleTelemetry().mGear)
    speed = calc.vel2speed(chknum(info.playersVehicleTelemetry().mLocalVel.x),
                           chknum(info.playersVehicleTelemetry().mLocalVel.y),
                           chknum(info.playersVehicleTelemetry().mLocalVel.z))
    rpm = chknum(info.playersVehicleTelemetry().mEngineRPM)
    rpm_max = chknum(info.playersVehicleTelemetry().mEngineMaxRPM)
    race_phase = chknum(info.Rf2Scor.mScoringInfo.mGamePhase)
    return pit_limiter, mgear, speed, rpm, rpm_max, race_phase


def lap_timestamp():
    """lap timestamp data"""
    lap_start = chknum(info.playersVehicleTelemetry().mLapStartET)
    lap_etime = chknum(info.playersVehicleTelemetry().mElapsedTime)
    return lap_start - lap_etime


def startlights():
    """Startlights data"""
    lights_frame = chknum(info.Rf2Scor.mScoringInfo.mStartLight)
    lights_number = chknum(info.Rf2Scor.mScoringInfo.mNumRedLights) + 1
    return lights_number - lights_frame


def session():
    """Session data"""
    time_left = chknum(info.Rf2Scor.mScoringInfo.mEndET) - chknum(info.Rf2Scor.mScoringInfo.mCurrentET)
    lap_total = chknum(info.Rf2Scor.mScoringInfo.mMaxLaps)
    lap_num = chknum(info.playersVehicleTelemetry().mLapNumber)
    plr_place = chknum(info.playersVehicleScoring().mPlace)
    veh_total = chknum(info.Rf2Scor.mScoringInfo.mNumVehicles)
    lap_into = min(max(chknum(info.playersVehicleScoring().mLapDist) * 100
                       / max(chknum(info.Rf2Scor.mScoringInfo.mLapDist), 1), 0), 99)
    return time_left, lap_total, lap_num, plr_place, veh_total, lap_into


def stint():
    """Stint data"""
    lap_num = chknum(info.playersVehicleTelemetry().mLapNumber)
    wear_avg = 100 - (sum([chknum(info.playersVehicleTelemetry().mWheels[data].mWear)
                           for data in range(4)]) * 25)
    fuel_curr = chknum(info.playersVehicleTelemetry().mFuel)
    time_curr = chknum(info.Rf2Scor.mScoringInfo.mCurrentET)
    inpits = chknum(info.playersVehicleScoring().mInPits)
    tire_idx = (chknum(info.playersVehicleTelemetry().mFrontTireCompoundIndex),
                chknum(info.playersVehicleTelemetry().mRearTireCompoundIndex))
    game_phase = chknum(info.Rf2Scor.mScoringInfo.mGamePhase)
    return lap_num, wear_avg, fuel_curr, time_curr, inpits, tire_idx, game_phase


def fuel():
    """Fuel data"""
    start_curr = chknum(info.playersVehicleTelemetry().mLapStartET)
    laps_total = chknum(info.Rf2Scor.mScoringInfo.mMaxLaps)
    laps_left = laps_total - chknum(info.playersVehicleScoring().mTotalLaps)
    time_left = chknum(info.Rf2Scor.mScoringInfo.mEndET) - chknum(info.Rf2Scor.mScoringInfo.mCurrentET)
    amount_curr = chknum(info.playersVehicleTelemetry().mFuel)
    capacity = chknum(info.playersVehicleTelemetry().mFuelCapacity)
    return start_curr, laps_total, laps_left, time_left, amount_curr, capacity


def camber():
    """Camber data"""
    raw_camber = (chknum(info.playersVehicleTelemetry().mWheels[0].mCamber),
                  chknum(info.playersVehicleTelemetry().mWheels[1].mCamber),
                  chknum(info.playersVehicleTelemetry().mWheels[2].mCamber),
                  chknum(info.playersVehicleTelemetry().mWheels[3].mCamber))
    return raw_camber


def toe():
    """Toe data"""
    raw_toe = (chknum(info.playersVehicleTelemetry().mWheels[0].mToe),
               -chknum(info.playersVehicleTelemetry().mWheels[1].mToe),
               chknum(info.playersVehicleTelemetry().mWheels[2].mToe),
               -chknum(info.playersVehicleTelemetry().mWheels[3].mToe))
    return raw_toe


def ride_height():
    """Ride height data"""
    height = (chknum(info.playersVehicleTelemetry().mWheels[0].mRideHeight),
              chknum(info.playersVehicleTelemetry().mWheels[1].mRideHeight),
              chknum(info.playersVehicleTelemetry().mWheels[2].mRideHeight),
              chknum(info.playersVehicleTelemetry().mWheels[3].mRideHeight))
    return height


def temperature():
    """Temperature data"""
    ttemp_fl = sum([chknum(info.playersVehicleTelemetry().mWheels[0].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_fr = sum([chknum(info.playersVehicleTelemetry().mWheels[1].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_rl = sum([chknum(info.playersVehicleTelemetry().mWheels[2].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    ttemp_rr = sum([chknum(info.playersVehicleTelemetry().mWheels[3].mTemperature[data])
                    for data in range(3)]) / 3 - 273.15
    btemp = (chknum(info.playersVehicleTelemetry().mWheels[0].mBrakeTemp) - 273.15,
             chknum(info.playersVehicleTelemetry().mWheels[1].mBrakeTemp) - 273.15,
             chknum(info.playersVehicleTelemetry().mWheels[2].mBrakeTemp) - 273.15,
             chknum(info.playersVehicleTelemetry().mWheels[3].mBrakeTemp) - 273.15)
    return (ttemp_fl, ttemp_fr, ttemp_rl, ttemp_rr), btemp


def wear():
    """Tyre wear data"""
    start_curr = chknum(info.playersVehicleTelemetry().mLapStartET)
    wear_curr = (chknum(info.playersVehicleTelemetry().mWheels[0].mWear) * 100,
                 chknum(info.playersVehicleTelemetry().mWheels[1].mWear) * 100,
                 chknum(info.playersVehicleTelemetry().mWheels[2].mWear) * 100,
                 chknum(info.playersVehicleTelemetry().mWheels[3].mWear) * 100)
    return start_curr, wear_curr


def tyre_load():
    """Tyre load data"""
    raw_load = (chknum(info.playersVehicleTelemetry().mWheels[0].mTireLoad),
                chknum(info.playersVehicleTelemetry().mWheels[1].mTireLoad),
                chknum(info.playersVehicleTelemetry().mWheels[2].mTireLoad),
                chknum(info.playersVehicleTelemetry().mWheels[3].mTireLoad))
    return raw_load


def tyre_pressure():
    """Tyre pressure data"""
    pressure = (chknum(info.playersVehicleTelemetry().mWheels[0].mPressure),
                chknum(info.playersVehicleTelemetry().mWheels[1].mPressure),
                chknum(info.playersVehicleTelemetry().mWheels[2].mPressure),
                chknum(info.playersVehicleTelemetry().mWheels[3].mPressure))
    return pressure


def force():
    """Force data"""
    gf_lgt = chknum(info.playersVehicleTelemetry().mLocalAccel.z) / 9.8  # long g-force
    gf_lat = chknum(info.playersVehicleTelemetry().mLocalAccel.x) / 9.8  # lat g-force
    df_ratio = calc.force_ratio(chknum(info.playersVehicleTelemetry().mFrontDownforce),
                                chknum(info.playersVehicleTelemetry().mRearDownforce))
    return gf_lgt, gf_lat, df_ratio


def drs():
    """DRS data"""
    drs_on = chknum(info.playersVehicleTelemetry().mRearFlapActivated)
    drs_status = chknum(info.playersVehicleTelemetry().mRearFlapLegalStatus)
    return drs_on, drs_status


def engine():
    """Engine data"""
    temp_oil = chknum(info.playersVehicleTelemetry().mEngineOilTemp)
    temp_water = chknum(info.playersVehicleTelemetry().mEngineWaterTemp)
    e_turbo = chknum(info.playersVehicleTelemetry().mTurboBoostPressure)
    e_rpm = chknum(info.playersVehicleTelemetry().mEngineRPM)
    return temp_oil, temp_water, e_turbo, e_rpm


def weather():
    """Weather data"""
    amb_temp = chknum(info.Rf2Scor.mScoringInfo.mAmbientTemp)
    trk_temp = chknum(info.Rf2Scor.mScoringInfo.mTrackTemp)
    rain = chknum(info.Rf2Scor.mScoringInfo.mRaining) * 100
    min_wet = chknum(info.Rf2Scor.mScoringInfo.mMinPathWetness) * 100
    max_wet = chknum(info.Rf2Scor.mScoringInfo.mMaxPathWetness) * 100
    avg_wet = chknum(info.Rf2Scor.mScoringInfo.mAvgPathWetness) * 100
    return amb_temp, trk_temp, rain, min_wet, max_wet, avg_wet
