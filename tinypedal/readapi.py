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

from pyRfactor2SharedMemory.sharedMemoryAPI import Cbytestring2Python

from tinypedal.__init__ import info
import tinypedal.calculation as calc


def state():
    """Check game state"""
    return info.Rf2Ext.mInRealtimeFC


def is_local_player(input_pidx):
    """Check if is local player"""
    if input_pidx == info.players_index and (0 <= info.playersVehicleScoring().mControl <= 1):
        return True
    return False


def cruise():
    """Cruise data"""
    ori_yaw = calc.oriyaw2deg(info.playersVehicleTelemetry().mOri[2].x,
                              info.playersVehicleTelemetry().mOri[2].z)
    pos_y = info.playersVehicleScoring().mPos.y
    return ori_yaw, pos_y


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


### RELATIVE INFO SECTION ###

def relative_list():
    """Create relative list with vehicle class info"""
    # Generate raw data list from all vehicles in current session
    veh_dict = {}
    unsorted_veh_class = []
    unique_veh_class = []

    for index in range(max(info.Rf2Scor.mScoringInfo.mNumVehicles, 1)):
        # Create vehicle dict, use "vehicle index" as key, "distance position" as value
        # Filter out negative distance value to zero
        veh_dict.update({index:max(info.Rf2Scor.mVehicles[index].mLapDist, 0)})

        # Create vehicle class list (class name, veh place, veh index)
        vehclass = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mVehicleClass)
        place = info.Rf2Scor.mVehicles[index].mPlace
        unsorted_veh_class.append((vehclass, place, index))
        unique_veh_class.append(vehclass)

    selected_list = calc_relative_list(veh_dict)
    veh_class_info = calc_veh_class_list(unsorted_veh_class, unique_veh_class)

    return selected_list, veh_class_info


def relative_data(index, index_player, veh_class_info):
    """Relative data"""
    if index >= 0:
        # Driver place position
        place = f"{veh_class_info[index][3]:02d}"

        # Driver name
        driver = Cbytestring2Python(info.Rf2Scor.mVehicles[index].mDriverName)

        # Lap time
        laptime = calc.sec2laptime(max(info.Rf2Scor.mVehicles[index].mLastLapTime, 0))

        # Vehicle position & class
        pos_class = f"{veh_class_info[index][1]:02d}"
        veh_class = veh_class_info[index][2]

        # Relative time gap
        time_gap = calc_relative_time_gap(index, index_player)

        # Number of completed
        num_lap = info.Rf2Tele.mVehicles[index].mLapNumber

        # Driver in pit
        in_pit = info.Rf2Scor.mVehicles[index].mInPits
    else:
        # Assign empty value to -1 player index
        (place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit
         ) = "", "", "", "", "", "", 0, 0
    return place, driver, laptime, pos_class, veh_class, time_gap, num_lap, in_pit


def calc_relative_list(veh_dict):
    """Calculate relative list"""
    # Reverse-sort dict by values
    re_veh_dict = dict(sorted(veh_dict.items(), key=lambda item: item[1], reverse=True))

    # Extract keys (vehicle index) to create new sorted vehicle list
    sorted_veh_list = list(re_veh_dict.keys())

    # Append with -1 if sorted vehicle list has less than 7 items
    if len(sorted_veh_list) < 7:
        for _ in range(7 - len(sorted_veh_list)):
            sorted_veh_list.append(-1)

    # Double extend list
    sorted_veh_list *= 2

    # Locate player vehicle index in list
    plr_index = info.players_index
    if plr_index in sorted_veh_list:
        plr_num = sorted_veh_list.index(plr_index)
    else:
        plr_num = 0  # prevent index not found in list error

    # Center selection range on player index from sorted vehicle list
    selected_list = [sorted_veh_list[index] for index in range(plr_num - 3, plr_num + 4)]
    return selected_list


def calc_veh_class_list(unsorted_veh_class, unique_veh_class):
    """Calculate vehicle class info list"""
    sorted_veh_class = sorted(unsorted_veh_class)  # sort & group different vehicle class list
    unique_veh_class = list(set(unique_veh_class))  # create unique vehicle class list
    unique_initial_class = unique_veh_class[0]  # set initial unique class name for comparison

    # Create vehicle class reference list (vehicle index, position in class, class name, place)
    veh_class_info = []
    pos_counter = 0  # position in class
    for index in range(len(sorted_veh_class)):  # loop through sorted vehicle class list
        for unique_idx in range(len(unique_veh_class)):  # unique vehicle class range
            if sorted_veh_class[index][0] == unique_veh_class[unique_idx]:
                if unique_initial_class == unique_veh_class[unique_idx]:
                    pos_counter += 1
                else:
                    pos_counter = 1  # reset position counter
                    unique_initial_class = unique_veh_class[unique_idx]  # reset init name
                veh_class_info.append((sorted_veh_class[index][2],
                                       pos_counter,
                                       unique_veh_class[unique_idx],
                                       sorted_veh_class[index][1]
                                       ))
    return sorted(veh_class_info)


def calc_relative_time_gap(index, index_player):
    """Calculate relative time gap"""
    # Relative distance position
    track_length = info.Rf2Scor.mScoringInfo.mLapDist  # track length
    track_half = track_length * 0.5  # half of track length
    opv_dist = info.Rf2Scor.mVehicles[index].mLapDist  # opponent player vehicle position
    plr_dist = info.Rf2Scor.mVehicles[index_player].mLapDist  # player vehicle position
    rel_dist = abs(opv_dist - plr_dist)  # get relative distance between opponent & player

    # Opponent is ahead of player
    if opv_dist > plr_dist:
        # Relative dist is greater than half of track length
        if rel_dist > track_half:
            rel_dist = track_length - opv_dist + plr_dist
    # Opponent is behind player
    elif opv_dist < plr_dist:
        if rel_dist > track_half:
            rel_dist = track_length + opv_dist - plr_dist
    else:
        rel_dist = 0

    # Time gap = Relative dist / player speed
    speed = int(calc.vel2speed(
                info.Rf2Scor.mVehicles[index_player].mLocalVel.x,
                info.Rf2Scor.mVehicles[index_player].mLocalVel.y,
                info.Rf2Scor.mVehicles[index_player].mLocalVel.z))
    if speed != 0:
        time_gap = f"{rel_dist / speed:.01f}"
    else:
        time_gap = "0.0"
    return time_gap
