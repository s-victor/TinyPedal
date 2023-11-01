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


def setup_api(api):
    """Setup API custom parameters"""
    api.setMode(cfg.shared_memory_api["access_mode"])
    api.setPID(cfg.shared_memory_api["rF2_process_id"])
    api.setPlayerOverride(cfg.shared_memory_api["enable_player_index_override"])
    api.setPlayerIndex(cfg.shared_memory_api["player_index"])


# Load Shared Memory API
info = SimInfoSync("tinypedal")
setup_api(info)
info.start()

chknm = val.infnan2zero
cs2py = val.cbytes2str


def state():
    """Check whether is driving"""
    if cfg.shared_memory_api["enable_active_state_override"]:
        return cfg.shared_memory_api["active_state"]
    return not info.paused and info.rf2TeleVeh().mIgnitionStarter


def api_version():
    """Check API version"""
    version = cs2py(info.rf2Ext.mVersion)
    return version if version else "unknown"


def create_spectate_list():
    """Create player name spectate list based on player index order"""
    index_list = ["Anonymous"]
    veh_total = chknm(info.rf2Tele.mNumVehicles)
    if veh_total:
        for index in range(veh_total):
            index_list.append(cs2py(info.rf2ScorVeh(index).mDriverName))
    return index_list


def combo_check():
    """Track & vehicle combo data"""
    track_name = cs2py(info.rf2Scor.mScoringInfo.mTrackName)
    class_name = cs2py(info.rf2ScorVeh().mVehicleClass)
    return fmt.strip_invalid_char(f"{track_name} - {class_name}")


def vehicle_check():
    """Track & vehicle combo data"""
    class_name = cs2py(info.rf2ScorVeh().mVehicleClass)
    veh_name = cs2py(info.rf2ScorVeh().mVehicleName)
    return fmt.strip_invalid_char(f"{class_name} - {veh_name}")


def is_race():
    """Is race session"""
    return chknm(info.rf2Scor.mScoringInfo.mSession) > 9


def lap_timestamp():
    """lap timestamp data"""
    lap_stime = chknm(info.rf2TeleVeh().mLapStartET)
    lap_etime = chknm(info.rf2TeleVeh().mElapsedTime)
    return lap_stime, lap_etime


def lap_number():
    """Lap number data"""
    return chknm(info.rf2TeleVeh().mLapNumber)


def cruise():
    """Cruise data"""
    ori_yaw = (chknm(info.rf2TeleVeh().mOri[2].x),
               chknm(info.rf2TeleVeh().mOri[2].z))
    time_start = int(chknm(info.rf2Scor.mScoringInfo.mStartET))
    track_time = int(chknm(info.rf2Scor.mScoringInfo.mCurrentET))
    pos_y = round(chknm(info.rf2ScorVeh().mPos.y), 1)
    return ori_yaw, pos_y, time_start, track_time


def instrument():
    """Instrument data"""
    headlights = chknm(info.rf2TeleVeh().mHeadlights)
    ignition = (chknm(info.rf2TeleVeh().mIgnitionStarter),
                chknm(info.rf2TeleVeh().mEngineRPM))
    clutch = (chknm(info.rf2Ext.mPhysics.mAutoClutch),
              chknm(info.rf2TeleVeh().mFilteredClutch))
    brake = bool(chknm(info.rf2TeleVeh().mFilteredBrake) > 0)
    wheel_rot = [chknm(info.rf2TeleVeh().mWheels[data].mRotation)
                 for data in range(4)]
    speed = calc.vel2speed(chknm(info.rf2TeleVeh().mLocalVel.x),
                           chknm(info.rf2TeleVeh().mLocalVel.y),
                           chknm(info.rf2TeleVeh().mLocalVel.z))
    return headlights, ignition, clutch, brake, wheel_rot, speed


def pedal():
    """Pedal data"""
    throttle = chknm(info.rf2TeleVeh().mFilteredThrottle)
    brake = chknm(info.rf2TeleVeh().mFilteredBrake)
    clutch = chknm(info.rf2TeleVeh().mFilteredClutch)
    raw_throttle = chknm(info.rf2TeleVeh().mUnfilteredThrottle)
    raw_brake = chknm(info.rf2TeleVeh().mUnfilteredBrake)
    raw_clutch = chknm(info.rf2TeleVeh().mUnfilteredClutch)
    ffb = chknm(info.rf2Ffb.mForceValue)
    return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb


def steering():
    """Steering data"""
    raw_steering = chknm(info.rf2TeleVeh().mUnfilteredSteering)
    sw_rot_range = chknm(info.rf2TeleVeh().mPhysicalSteeringWheelRange)
    return raw_steering, sw_rot_range


def gauge():
    """Gauge data"""
    limiter = chknm(info.rf2TeleVeh().mSpeedLimiter)
    mgear = chknm(info.rf2TeleVeh().mGear)
    max_gear = chknm(info.rf2TeleVeh().mMaxGears)
    speed = calc.vel2speed(chknm(info.rf2TeleVeh().mLocalVel.x),
                           chknm(info.rf2TeleVeh().mLocalVel.y),
                           chknm(info.rf2TeleVeh().mLocalVel.z))
    rpm = chknm(info.rf2TeleVeh().mEngineRPM)
    rpm_max = chknm(info.rf2TeleVeh().mEngineMaxRPM)
    lap_etime = chknm(info.rf2TeleVeh().mElapsedTime)
    return limiter, mgear, max_gear, speed, rpm, rpm_max, lap_etime


def p2p():
    """P2P data"""
    mgear = chknm(info.rf2TeleVeh().mGear)
    speed = calc.vel2speed(chknm(info.rf2TeleVeh().mLocalVel.x),
                           chknm(info.rf2TeleVeh().mLocalVel.y),
                           chknm(info.rf2TeleVeh().mLocalVel.z))
    throttle = chknm(info.rf2TeleVeh().mUnfilteredThrottle)
    return mgear, speed, throttle


def pitting():
    """Pitting data"""
    inpits = chknm(info.rf2ScorVeh().mInPits)
    pit_limiter = chknm(info.rf2TeleVeh().mSpeedLimiter)
    race_phase = chknm(info.rf2Scor.mScoringInfo.mGamePhase)
    return inpits, pit_limiter, race_phase


def blue_flag():
    """Blue flag data"""
    return chknm(info.rf2ScorVeh().mFlag)


def yellow_flag():
    """Yellow flag data"""
    return (chknm(info.rf2Scor.mScoringInfo.mSectorFlag[0]),
            chknm(info.rf2Scor.mScoringInfo.mSectorFlag[1]),
            chknm(info.rf2Scor.mScoringInfo.mSectorFlag[2]))


def radar():
    """Radar data"""
    lap_etime = chknm(info.rf2TeleVeh().mElapsedTime)
    ingarage = chknm(info.rf2ScorVeh().mInGarageStall)
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
        chknm(info.rf2ScorVeh().mLapDist) * 100,
        chknm(info.rf2Scor.mScoringInfo.mLapDist), 99)
    lap_total = chknm(info.rf2Scor.mScoringInfo.mMaxLaps)
    plr_position = (chknm(info.rf2ScorVeh().mPlace),
                 chknm(info.rf2Tele.mNumVehicles))
    return time_left, lap_into, lap_total, plr_position


def stint():
    """Stint data"""
    time_curr = chknm(info.rf2Scor.mScoringInfo.mCurrentET)
    inpits = chknm(info.rf2ScorVeh().mInPits)
    ingarage = chknm(info.rf2ScorVeh().mInGarageStall)
    return time_curr, inpits, ingarage


def tyre_compound():
    """Tyre compound data"""
    return (chknm(info.rf2TeleVeh().mFrontTireCompoundIndex),
            chknm(info.rf2TeleVeh().mRearTireCompoundIndex))


def camber():
    """Camber data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mCamber)
            for data in range(4)]


def toe():
    """Toe data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mToe)
            for data in range(4)]


def ride_height():
    """Ride height data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mRideHeight)
            for data in range(4)]


def brake_bias():
    """Brake bias data"""
    return chknm(info.rf2TeleVeh().mRearBrakeBias)

def brake_pressure():
    """Brake pressure data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mBrakePressure)
            for data in range(4)]


def brake_temp():
    """Brake temperature data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mBrakeTemp) - 273.15
            for data in range(4)]


def tyre_temp_surface():
    """Tyre surface temperature data"""
    return [[chknm(info.rf2TeleVeh().mWheels[tyre].mTemperature[data]) - 273.15
             for data in range(3)] for tyre in range(4)]


def tyre_temp_innerlayer():
    """Tyre inner layer temperature data"""
    return [[chknm(info.rf2TeleVeh().mWheels[tyre].mTireInnerLayerTemperature[data])
            - 273.15 for data in range(3)] for tyre in range(4)]


def wear():
    """Tyre wear data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mWear)
            for data in range(4)]


def tyre_load():
    """Tyre load data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mTireLoad)
            for data in range(4)]


def tyre_pressure():
    """Tyre pressure data"""
    return [chknm(info.rf2TeleVeh().mWheels[data].mPressure)
            for data in range(4)]


def ground_velocity():
    """Ground velocity data"""
    lat_gv = [chknm(info.rf2TeleVeh().mWheels[data].mLateralGroundVel)
              for data in range(4)]
    lgt_gv = [chknm(info.rf2TeleVeh().mWheels[data].mLongitudinalGroundVel)
              for data in range(4)]
    return lat_gv, lgt_gv


def drs():
    """DRS data"""
    drs_on = chknm(info.rf2TeleVeh().mRearFlapActivated)
    drs_status = chknm(info.rf2TeleVeh().mRearFlapLegalStatus)
    return drs_on, drs_status


def timing(index):
    """Timing data"""
    veh_total = chknm(info.rf2Tele.mNumVehicles)
    laptime_opt = chknm(info.rf2ScorVeh(index).mBestLapTime)
    class_opt = cs2py(info.rf2ScorVeh(index).mVehicleClass)
    class_plr = cs2py(info.rf2ScorVeh().mVehicleClass)
    return veh_total, laptime_opt, class_opt == class_plr


def electric_motor():
    """Electric motor data"""
    motor_temp = chknm(info.rf2TeleVeh().mElectricBoostMotorTemperature)
    water_temp = chknm(info.rf2TeleVeh().mElectricBoostWaterTemperature)
    motor_rpm = chknm(info.rf2TeleVeh().mElectricBoostMotorRPM)
    motor_torque = chknm(info.rf2TeleVeh().mElectricBoostMotorTorque)
    return motor_temp, water_temp, motor_rpm, motor_torque


def engine():
    """Engine data"""
    temp_oil = chknm(info.rf2TeleVeh().mEngineOilTemp)
    temp_water = chknm(info.rf2TeleVeh().mEngineWaterTemp)
    e_turbo = int(chknm(info.rf2TeleVeh().mTurboBoostPressure))
    e_rpm = int(chknm(info.rf2TeleVeh().mEngineRPM))
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


def speedometer():
    """Speedometer data"""
    speed = calc.vel2speed(chknm(info.rf2TeleVeh().mLocalVel.x),
                           chknm(info.rf2TeleVeh().mLocalVel.y),
                           chknm(info.rf2TeleVeh().mLocalVel.z))
    raw_throttle = chknm(info.rf2TeleVeh().mUnfilteredThrottle)
    mgear = chknm(info.rf2TeleVeh().mGear)
    lap_etime = chknm(info.rf2TeleVeh().mElapsedTime)
    return speed, raw_throttle, mgear, lap_etime


def session_check():
    """Check session time stamp, type, elapsed time, completed laps"""
    session_length = chknm(info.rf2Scor.mScoringInfo.mEndET)
    session_type = chknm(info.rf2Scor.mScoringInfo.mSession)
    session_stamp = f"{session_length:.0f}{session_type:.0f}"
    session_etime = int(chknm(info.rf2Scor.mScoringInfo.mCurrentET))
    session_tlaps = chknm(info.rf2ScorVeh().mTotalLaps)
    return session_stamp, session_etime, session_tlaps
