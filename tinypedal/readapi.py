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


def state():
    """Check game state"""
    return info.playersVehicleTelemetry().mIgnitionStarter != 0


def is_local_player():
    """Check if is local player"""
    if 0 <= info.playersVehicleScoring().mControl <= 1:
        return True
    return False


def cruise():
    """Cruise data"""
    ori_yaw = 180 - (calc.oriyaw2rad(info.playersVehicleTelemetry().mOri[2].x,
                                     info.playersVehicleTelemetry().mOri[2].z) * 57.2957795)
    pos_y = info.playersVehicleScoring().mPos.y
    track_clock = info.Rf2Scor.mScoringInfo.mStartET + info.Rf2Scor.mScoringInfo.mCurrentET
    return ori_yaw, pos_y, track_clock


def instrument():
    """Instrument data"""
    start_curr = info.playersVehicleTelemetry().mLapStartET
    headlights = info.playersVehicleTelemetry().mHeadlights
    ignition = info.playersVehicleTelemetry().mIgnitionStarter
    rpm = info.playersVehicleTelemetry().mEngineRPM
    autoclutch = info.Rf2Ext.mPhysics.mAutoClutch
    clutch = info.playersVehicleTelemetry().mFilteredClutch
    brake = info.playersVehicleTelemetry().mFilteredBrake
    wheel_rot = [info.playersVehicleTelemetry().mWheels[0].mRotation,
                 info.playersVehicleTelemetry().mWheels[1].mRotation,
                 info.playersVehicleTelemetry().mWheels[2].mRotation,
                 info.playersVehicleTelemetry().mWheels[3].mRotation]
    speed = calc.vel2speed(info.playersVehicleTelemetry().mLocalVel.x,
                           info.playersVehicleTelemetry().mLocalVel.y,
                           info.playersVehicleTelemetry().mLocalVel.z)
    return start_curr, headlights, ignition, rpm, autoclutch, clutch, brake, wheel_rot, speed


def pedal():
    """Pedal data"""
    throttle = info.playersVehicleTelemetry().mFilteredThrottle
    brake = info.playersVehicleTelemetry().mFilteredBrake
    clutch = info.playersVehicleTelemetry().mFilteredClutch
    raw_throttle = info.playersVehicleTelemetry().mUnfilteredThrottle
    raw_brake = info.playersVehicleTelemetry().mUnfilteredBrake
    raw_clutch = info.playersVehicleTelemetry().mUnfilteredClutch
    ffb = info.Rf2Ffb.mForceValue
    return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb


def steering():
    """Steering data"""
    raw_steering = info.playersVehicleTelemetry().mUnfilteredSteering
    steering_wheel_rot_range = info.playersVehicleTelemetry().mPhysicalSteeringWheelRange
    return raw_steering, steering_wheel_rot_range


def gear():
    """Gear data"""
    pit_limiter = info.playersVehicleTelemetry().mSpeedLimiter
    mgear = info.playersVehicleTelemetry().mGear
    speed = calc.vel2speed(info.playersVehicleTelemetry().mLocalVel.x,
                           info.playersVehicleTelemetry().mLocalVel.y,
                           info.playersVehicleTelemetry().mLocalVel.z)
    rpm = info.playersVehicleTelemetry().mEngineRPM
    rpm_max = info.playersVehicleTelemetry().mEngineMaxRPM
    return pit_limiter, mgear, speed, rpm, rpm_max


def timing():
    """Timing data"""
    start_curr = info.playersVehicleTelemetry().mLapStartET
    laps_total = info.Rf2Scor.mScoringInfo.mMaxLaps
    laps_left = laps_total - info.playersVehicleScoring().mTotalLaps
    time_left = info.Rf2Scor.mScoringInfo.mEndET - info.Rf2Scor.mScoringInfo.mCurrentET
    return start_curr, laps_total, laps_left, time_left


def session():
    """Session data"""
    time_left = info.Rf2Scor.mScoringInfo.mEndET - info.Rf2Scor.mScoringInfo.mCurrentET
    lap_total = info.Rf2Scor.mScoringInfo.mMaxLaps
    lap_num = info.playersVehicleTelemetry().mLapNumber
    plr_place = info.playersVehicleScoring().mPlace
    veh_total = info.Rf2Scor.mScoringInfo.mNumVehicles
    lap_into = min(max(info.playersVehicleScoring().mLapDist * 100
                       / max(info.Rf2Scor.mScoringInfo.mLapDist, 1), 0), 99)
    return time_left, lap_total, lap_num, plr_place, veh_total, lap_into


def stint():
    """Stint data"""
    lap_num = info.playersVehicleTelemetry().mLapNumber
    wear_avg = 100 - (sum([info.playersVehicleTelemetry().mWheels[data].mWear
                           for data in range(4)]) * 25)
    fuel_curr = info.playersVehicleTelemetry().mFuel
    time_curr = info.Rf2Scor.mScoringInfo.mCurrentET
    inpits = info.playersVehicleScoring().mInPits
    ftire_idx = info.playersVehicleTelemetry().mFrontTireCompoundIndex
    rtire_idx = info.playersVehicleTelemetry().mRearTireCompoundIndex
    game_phase = info.Rf2Scor.mScoringInfo.mGamePhase
    return lap_num, wear_avg, fuel_curr, time_curr, inpits, ftire_idx, rtire_idx, game_phase


def fuel():
    """Fuel data"""
    amount_curr = info.playersVehicleTelemetry().mFuel
    capacity = info.playersVehicleTelemetry().mFuelCapacity
    return amount_curr, capacity


def camber():
    """Camber data"""
    camber_fl = info.playersVehicleTelemetry().mWheels[0].mCamber
    camber_fr = info.playersVehicleTelemetry().mWheels[1].mCamber
    camber_rl = info.playersVehicleTelemetry().mWheels[2].mCamber
    camber_rr = info.playersVehicleTelemetry().mWheels[3].mCamber
    return camber_fl, camber_fr, camber_rl, camber_rr


def toe():
    """Toe data"""
    toe_fl = info.playersVehicleTelemetry().mWheels[0].mToe
    toe_fr = -info.playersVehicleTelemetry().mWheels[1].mToe
    toe_rl = info.playersVehicleTelemetry().mWheels[2].mToe
    toe_rr = -info.playersVehicleTelemetry().mWheels[3].mToe
    return toe_fl, toe_fr, toe_rl, toe_rr


def ride_height():
    """Ride height data"""
    rideh_fl = info.playersVehicleTelemetry().mWheels[0].mRideHeight
    rideh_fr = info.playersVehicleTelemetry().mWheels[1].mRideHeight
    rideh_rl = info.playersVehicleTelemetry().mWheels[2].mRideHeight
    rideh_rr = info.playersVehicleTelemetry().mWheels[3].mRideHeight
    rake = (rideh_rr + rideh_rl - rideh_fr - rideh_fl) * 0.5
    return rideh_fl, rideh_fr, rideh_rl, rideh_rr, rake


def temperature():
    """Temperature data"""
    ttemp_fl = sum([info.playersVehicleTelemetry().mWheels[0].mTemperature[data]
                    for data in range(3)]) / 3
    ttemp_fr = sum([info.playersVehicleTelemetry().mWheels[1].mTemperature[data]
                    for data in range(3)]) / 3
    ttemp_rl = sum([info.playersVehicleTelemetry().mWheels[2].mTemperature[data]
                    for data in range(3)]) / 3
    ttemp_rr = sum([info.playersVehicleTelemetry().mWheels[3].mTemperature[data]
                    for data in range(3)]) / 3
    btemp_fl = info.playersVehicleTelemetry().mWheels[0].mBrakeTemp
    btemp_fr = info.playersVehicleTelemetry().mWheels[1].mBrakeTemp
    btemp_rl = info.playersVehicleTelemetry().mWheels[2].mBrakeTemp
    btemp_rr = info.playersVehicleTelemetry().mWheels[3].mBrakeTemp
    return ttemp_fl, ttemp_fr, ttemp_rl, ttemp_rr, btemp_fl, btemp_fr, btemp_rl, btemp_rr


def wear():
    """Tyre wear data"""
    wear_fl = info.playersVehicleTelemetry().mWheels[0].mWear * 100
    wear_fr = info.playersVehicleTelemetry().mWheels[1].mWear * 100
    wear_rl = info.playersVehicleTelemetry().mWheels[2].mWear * 100
    wear_rr = info.playersVehicleTelemetry().mWheels[3].mWear * 100
    return wear_fl, wear_fr, wear_rl, wear_rr


def tyre_load():
    """Tyre load data"""
    load_fl = info.playersVehicleTelemetry().mWheels[0].mTireLoad
    load_fr = info.playersVehicleTelemetry().mWheels[1].mTireLoad
    load_rl = info.playersVehicleTelemetry().mWheels[2].mTireLoad
    load_rr = info.playersVehicleTelemetry().mWheels[3].mTireLoad
    return load_fl, load_fr, load_rl, load_rr


def tyre_pres():
    """Tyre pressure data"""
    pres_fl = info.playersVehicleTelemetry().mWheels[0].mPressure
    pres_fr = info.playersVehicleTelemetry().mWheels[1].mPressure
    pres_rl = info.playersVehicleTelemetry().mWheels[2].mPressure
    pres_rr = info.playersVehicleTelemetry().mWheels[3].mPressure
    return pres_fl, pres_fr, pres_rl, pres_rr


def force():
    """Force data"""
    gf_lgt = info.playersVehicleTelemetry().mLocalAccel.z / 9.8  # long g-force
    gf_lat = info.playersVehicleTelemetry().mLocalAccel.x / 9.8  # lat g-force
    df_ratio = calc.force_ratio(info.playersVehicleTelemetry().mFrontDownforce,
                                info.playersVehicleTelemetry().mRearDownforce)
    return gf_lgt, gf_lat, df_ratio


def drs():
    """DRS data"""
    drs_on = info.playersVehicleTelemetry().mRearFlapActivated
    drs_status = info.playersVehicleTelemetry().mRearFlapLegalStatus
    return drs_on, drs_status


def engine():
    """Engine data"""
    temp_oil = info.playersVehicleTelemetry().mEngineOilTemp
    temp_water = info.playersVehicleTelemetry().mEngineWaterTemp
    e_turbo = info.playersVehicleTelemetry().mTurboBoostPressure
    e_rpm = info.playersVehicleTelemetry().mEngineRPM
    return temp_oil, temp_water, e_turbo, e_rpm


def weather():
    """Weather data"""
    amb_temp = info.Rf2Scor.mScoringInfo.mAmbientTemp
    trk_temp = info.Rf2Scor.mScoringInfo.mTrackTemp
    rain = info.Rf2Scor.mScoringInfo.mRaining * 100
    min_wet = info.Rf2Scor.mScoringInfo.mMinPathWetness * 100
    max_wet = info.Rf2Scor.mScoringInfo.mMaxPathWetness * 100
    avg_wet = info.Rf2Scor.mScoringInfo.mAvgPathWetness * 100
    return amb_temp, trk_temp, rain, min_wet, max_wet, avg_wet
