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

from pyRfactor2SharedMemory.sim_info_sync import SimInfoSync

from .setting import cfg
from . import validator as val
from . import formatter as fmt
from . import calculation as calc


# Load Shared Memory API
info = SimInfoSync("tinypedal")
info.setMode(cfg.shared_memory_api["access_mode"])
info.setPID(cfg.shared_memory_api["rF2_process_id"])
info.start()

chknm = val.numeric_validator
cs2py = info.cbytes2str


def state():
    """Check whether is driving"""
    return not info.paused and info.playerTele.mIgnitionStarter


def api_version():
    """Check API version"""
    version = cs2py(info.rf2Ext.mVersion)
    return version if version else "unknown"


def combo_check():
    """Track & vehicle combo data"""
    track_name = cs2py(info.rf2Scor.mScoringInfo.mTrackName)
    class_name = cs2py(info.playerScor.mVehicleClass)
    return fmt.strip_invalid_char(f"{track_name} - {class_name}")


def vehicle_check():
    """Track & vehicle combo data"""
    class_name = cs2py(info.playerScor.mVehicleClass)
    veh_name = cs2py(info.playerScor.mVehicleName)
    return fmt.strip_invalid_char(f"{class_name} - {veh_name}")


def is_race():
    """Is race session"""
    return chknm(info.rf2Scor.mScoringInfo.mSession) > 9


def lap_timestamp():
    """lap timestamp data"""
    lap_stime = chknm(info.playerTele.mLapStartET)
    lap_etime = chknm(info.playerTele.mElapsedTime)
    return lap_stime, lap_etime


def lap_number():
    """Lap number data"""
    return chknm(info.playerTele.mLapNumber)


def cruise():
    """Cruise data"""
    ori_yaw = (chknm(info.playerTele.mOri[2].x),
               chknm(info.playerTele.mOri[2].z))
    time_start = int(chknm(info.rf2Scor.mScoringInfo.mStartET))
    track_time = int(chknm(info.rf2Scor.mScoringInfo.mCurrentET))
    pos_y = round(chknm(info.playerScor.mPos.y), 1)
    return ori_yaw, pos_y, time_start, track_time


def instrument():
    """Instrument data"""
    headlights = chknm(info.playerTele.mHeadlights)
    ignition = (chknm(info.playerTele.mIgnitionStarter),
                chknm(info.playerTele.mEngineRPM))
    clutch = (chknm(info.rf2Ext.mPhysics.mAutoClutch),
              chknm(info.playerTele.mFilteredClutch))
    brake = bool(chknm(info.playerTele.mFilteredBrake) > 0)
    wheel_rot = [chknm(info.playerTele.mWheels[data].mRotation)
                 for data in range(4)]
    speed = calc.vel2speed(chknm(info.playerTele.mLocalVel.x),
                           chknm(info.playerTele.mLocalVel.y),
                           chknm(info.playerTele.mLocalVel.z))
    return headlights, ignition, clutch, brake, wheel_rot, speed


def pedal():
    """Pedal data"""
    throttle = chknm(info.playerTele.mFilteredThrottle)
    brake = chknm(info.playerTele.mFilteredBrake)
    clutch = chknm(info.playerTele.mFilteredClutch)
    raw_throttle = chknm(info.playerTele.mUnfilteredThrottle)
    raw_brake = chknm(info.playerTele.mUnfilteredBrake)
    raw_clutch = chknm(info.playerTele.mUnfilteredClutch)
    ffb = chknm(info.rf2Ffb.mForceValue)
    return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb


def steering():
    """Steering data"""
    raw_steering = chknm(info.playerTele.mUnfilteredSteering)
    sw_rot_range = chknm(info.playerTele.mPhysicalSteeringWheelRange)
    return raw_steering, sw_rot_range


def gauge():
    """Gauge data"""
    limiter = chknm(info.playerTele.mSpeedLimiter)
    mgear = chknm(info.playerTele.mGear)
    max_gear = chknm(info.playerTele.mMaxGears)
    speed = calc.vel2speed(chknm(info.playerTele.mLocalVel.x),
                           chknm(info.playerTele.mLocalVel.y),
                           chknm(info.playerTele.mLocalVel.z))
    rpm = chknm(info.playerTele.mEngineRPM)
    rpm_max = chknm(info.playerTele.mEngineMaxRPM)
    lap_etime = chknm(info.playerTele.mElapsedTime)
    return limiter, mgear, max_gear, speed, rpm, rpm_max, lap_etime


def p2p():
    """P2P data"""
    mgear = chknm(info.playerTele.mGear)
    speed = calc.vel2speed(chknm(info.playerTele.mLocalVel.x),
                           chknm(info.playerTele.mLocalVel.y),
                           chknm(info.playerTele.mLocalVel.z))
    throttle = chknm(info.playerTele.mUnfilteredThrottle)
    return mgear, speed, throttle


def pitting():
    """Pitting data"""
    inpits = chknm(info.playerScor.mInPits)
    pit_limiter = chknm(info.playerTele.mSpeedLimiter)
    race_phase = chknm(info.rf2Scor.mScoringInfo.mGamePhase)
    return inpits, pit_limiter, race_phase


def blue_flag():
    """Blue flag data"""
    return chknm(info.playerScor.mFlag)


def yellow_flag():
    """Yellow flag data"""
    return (chknm(info.rf2Scor.mScoringInfo.mSectorFlag[0]),
            chknm(info.rf2Scor.mScoringInfo.mSectorFlag[1]),
            chknm(info.rf2Scor.mScoringInfo.mSectorFlag[2]))


def radar():
    """Radar data"""
    lap_etime = chknm(info.playerTele.mElapsedTime)
    ingarage = chknm(info.playerScor.mInGarageStall)
    return lap_etime, ingarage


def startlights():
    """Startlights data"""
    lights_frame = chknm(info.rf2Scor.mScoringInfo.mStartLight)
    lights_number = chknm(info.rf2Scor.mScoringInfo.mNumRedLights) + 1
    return lights_number - lights_frame


def session():
    """Session data"""
    time_left = (chknm(info.rf2Scor.mScoringInfo.mEndET)
                 - chknm(info.rf2Scor.mScoringInfo.mCurrentET))
    lap_into = calc.percentage_distance(
        chknm(info.playerScor.mLapDist) * 100,
        chknm(info.rf2Scor.mScoringInfo.mLapDist), 99)
    lap_total = chknm(info.rf2Scor.mScoringInfo.mMaxLaps)
    plr_position = (chknm(info.playerScor.mPlace),
                 chknm(info.rf2Tele.mNumVehicles))
    return time_left, lap_into, lap_total, plr_position


def stint():
    """Stint data"""
    time_curr = chknm(info.rf2Scor.mScoringInfo.mCurrentET)
    inpits = chknm(info.playerScor.mInPits)
    ingarage = chknm(info.playerScor.mInGarageStall)
    return time_curr, inpits, ingarage


def tyre_compound():
    """Tyre compound data"""
    return (chknm(info.playerTele.mFrontTireCompoundIndex),
            chknm(info.playerTele.mRearTireCompoundIndex))


def camber():
    """Camber data"""
    return [chknm(info.playerTele.mWheels[data].mCamber)
            for data in range(4)]


def toe():
    """Toe data"""
    return [chknm(info.playerTele.mWheels[data].mToe)
            for data in range(4)]


def ride_height():
    """Ride height data"""
    return [chknm(info.playerTele.mWheels[data].mRideHeight)
            for data in range(4)]


def brake_bias():
    """Brake bias data"""
    return chknm(info.playerTele.mRearBrakeBias)

def brake_pressure():
    """Brake pressure data"""
    return [chknm(info.playerTele.mWheels[data].mBrakePressure)
            for data in range(4)]


def brake_temp():
    """Brake temperature data"""
    return [chknm(info.playerTele.mWheels[data].mBrakeTemp) - 273.15
            for data in range(4)]


def tyre_temp_surface():
    """Tyre surface temperature data"""
    return [[chknm(info.playerTele.mWheels[tyre].mTemperature[data]) - 273.15
             for data in range(3)] for tyre in range(4)]


def tyre_temp_innerlayer():
    """Tyre inner layer temperature data"""
    return [[chknm(info.playerTele.mWheels[tyre].mTireInnerLayerTemperature[data])
            - 273.15 for data in range(3)] for tyre in range(4)]


def wear():
    """Tyre wear data"""
    return [chknm(info.playerTele.mWheels[data].mWear)
            for data in range(4)]


def tyre_load():
    """Tyre load data"""
    return [chknm(info.playerTele.mWheels[data].mTireLoad)
            for data in range(4)]


def tyre_pressure():
    """Tyre pressure data"""
    return [chknm(info.playerTele.mWheels[data].mPressure)
            for data in range(4)]


def ground_velocity():
    """Ground velocity data"""
    lat_gv = [chknm(info.playerTele.mWheels[data].mLateralGroundVel)
              for data in range(4)]
    lgt_gv = [chknm(info.playerTele.mWheels[data].mLongitudinalGroundVel)
              for data in range(4)]
    return lat_gv, lgt_gv


def drs():
    """DRS data"""
    drs_on = chknm(info.playerTele.mRearFlapActivated)
    drs_status = chknm(info.playerTele.mRearFlapLegalStatus)
    return drs_on, drs_status


def timing(index):
    """Timing data"""
    veh_total = chknm(info.rf2Tele.mNumVehicles)
    laptime_opt = chknm(info.rf2Scor.mVehicles[index].mBestLapTime)
    class_opt = cs2py(info.rf2Scor.mVehicles[index].mVehicleClass)
    class_plr = cs2py(info.playerScor.mVehicleClass)
    return veh_total, laptime_opt, class_opt == class_plr


def electric_motor():
    """Electric motor data"""
    motor_temp = chknm(info.playerTele.mElectricBoostMotorTemperature)
    water_temp = chknm(info.playerTele.mElectricBoostWaterTemperature)
    motor_rpm = chknm(info.playerTele.mElectricBoostMotorRPM)
    motor_torque = chknm(info.playerTele.mElectricBoostMotorTorque)
    return motor_temp, water_temp, motor_rpm, motor_torque


def engine():
    """Engine data"""
    temp_oil = chknm(info.playerTele.mEngineOilTemp)
    temp_water = chknm(info.playerTele.mEngineWaterTemp)
    e_turbo = int(chknm(info.playerTele.mTurboBoostPressure))
    e_rpm = int(chknm(info.playerTele.mEngineRPM))
    return temp_oil, temp_water, e_turbo, e_rpm


def weather():
    """Weather data"""
    track_temp = chknm(info.rf2Scor.mScoringInfo.mTrackTemp)
    ambient_temp = chknm(info.rf2Scor.mScoringInfo.mAmbientTemp)
    rain_per = chknm(info.rf2Scor.mScoringInfo.mRaining) * 100
    wet_road = (chknm(info.rf2Scor.mScoringInfo.mMinPathWetness) * 100,
                chknm(info.rf2Scor.mScoringInfo.mMaxPathWetness) * 100,
                chknm(info.rf2Scor.mScoringInfo.mAvgPathWetness) * 100)
    return track_temp, ambient_temp, rain_per, wet_road


def sector():
    """Sector data

    Convert game sector index order to 0,1,2 for consistency.
    """
    sector_idx = (2,0,1)[min(max(chknm(info.playerScor.mSector), 0), 2)]
    curr_sector1 = chknm(info.playerScor.mCurSector1)
    curr_sector2 = chknm(info.playerScor.mCurSector2)
    last_sector2 = chknm(info.playerScor.mLastSector2)
    last_laptime = chknm(info.playerScor.mLastLapTime)
    speed = calc.vel2speed(chknm(info.playerTele.mLocalVel.x),
                           chknm(info.playerTele.mLocalVel.y),
                           chknm(info.playerTele.mLocalVel.z))
    return sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime, speed


def session_check():
    """Check session time stamp, type, elapsed time, completed laps"""
    session_length = chknm(info.rf2Scor.mScoringInfo.mEndET)
    session_type = chknm(info.rf2Scor.mScoringInfo.mSession)
    session_stamp = f"{session_length:.0f}{session_type:.0f}"
    session_etime = int(chknm(info.rf2Scor.mScoringInfo.mCurrentET))
    session_tlaps = chknm(info.playerScor.mTotalLaps)
    return session_stamp, session_etime, session_tlaps
