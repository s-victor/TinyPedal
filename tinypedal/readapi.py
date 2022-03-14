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
Access rF2 shared memory data using:
 - The Iron Wolf’s rF2 Shared Memory Map Plugin
   https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin

 - Tony Whitley’s pyRfactor2SharedMemory Library
   https://github.com/TonyWhitley/pyRfactor2SharedMemory

   Note: TinyPedal currently requires a forked version of pyRfactor2SharedMemory
   that enables access to FFB & additional functions:
   https://github.com/s-victor/pyRfactor2SharedMemory
"""

from pyRfactor2SharedMemory.sharedMemoryAPI import SimInfoAPI, Cbytestring2Python
import tinypedal.calculation as calc


class ReadData:
    """Read rF2 shared memory

    Sort data into groups for different widgets.
    """
    info = SimInfoAPI()

    def state(self):
        """Check game state"""
        state = self.info.Rf2Ext.mInRealtimeFC
        return state

    def pedal(self):
        """Pedal data"""
        plr_tele = self.info.playersVehicleTelemetry()

        throttle = plr_tele.mFilteredThrottle
        brake = plr_tele.mFilteredBrake
        clutch = plr_tele.mFilteredClutch
        raw_throttle = plr_tele.mUnfilteredThrottle
        raw_brake = plr_tele.mUnfilteredBrake
        raw_clutch = plr_tele.mUnfilteredClutch
        ffb = self.info.Rf2Ffb.mForceValue
        return throttle, brake, clutch, raw_throttle, raw_brake, raw_clutch, ffb

    def steering(self):
        """Steering data"""
        plr_tele = self.info.playersVehicleTelemetry()

        raw_steering = plr_tele.mUnfilteredSteering
        steering_wheel_rot_range = plr_tele.mPhysicalSteeringWheelRange
        return raw_steering, steering_wheel_rot_range

    def gear(self):
        """Gear data"""
        plr_tele = self.info.playersVehicleTelemetry()

        pit_limiter = plr_tele.mSpeedLimiter
        gear = plr_tele.mGear
        speed = calc.vel2speed(plr_tele.mLocalVel.x, plr_tele.mLocalVel.y, plr_tele.mLocalVel.z)
        rpm = plr_tele.mEngineRPM
        rpm_max = plr_tele.mEngineMaxRPM
        return pit_limiter, gear, speed, rpm, rpm_max

    def timing(self):
        """Timing data"""
        plr_scor = self.info.playersVehicleScoring()
        rf2_scor = self.info.Rf2Scor.mScoringInfo

        start_curr = plr_scor.mLapStartET  # current lap start time stamp
        laps_total = rf2_scor.mMaxLaps  # total race laps
        laps_left = laps_total - plr_scor.mTotalLaps  # remaining laps
        time_left = rf2_scor.mEndET - rf2_scor.mCurrentET  #session timer (sec)
        return start_curr, laps_total, laps_left, time_left

    def laptime(self):
        """Laptime data"""
        plr_scor = self.info.playersVehicleScoring()
        plr_tele = self.info.playersVehicleTelemetry()

        laptime_curr = plr_tele.mElapsedTime - plr_tele.mLapStartET
        laptime_last = max(plr_scor.mLastLapTime, 0)
        laptime_best = max(plr_scor.mBestLapTime, 0)
        return laptime_curr, laptime_last, laptime_best

    def fuel(self):
        """Fuel data"""
        plr_tele = self.info.playersVehicleTelemetry()

        amount_curr = plr_tele.mFuel
        capacity = plr_tele.mFuelCapacity
        return amount_curr, capacity

    def camber(self):
        """Camber data"""
        plr_tele = self.info.playersVehicleTelemetry()

        camber_fl = plr_tele.mWheels[0].mCamber
        camber_fr = plr_tele.mWheels[1].mCamber
        camber_rl = plr_tele.mWheels[2].mCamber
        camber_rr = plr_tele.mWheels[3].mCamber
        return camber_fl, camber_fr, camber_rl, camber_rr

    def toe(self):
        """Toe data"""
        plr_tele = self.info.playersVehicleTelemetry()

        toe_fl = plr_tele.mWheels[0].mToe
        toe_fr = -plr_tele.mWheels[1].mToe
        toe_rl = plr_tele.mWheels[2].mToe
        toe_rr = -plr_tele.mWheels[3].mToe
        return toe_fl, toe_fr, toe_rl, toe_rr

    def ride_height(self):
        """Ride height data"""
        plr_tele = self.info.playersVehicleTelemetry()

        rideh_fl = plr_tele.mWheels[0].mRideHeight
        rideh_fr = plr_tele.mWheels[1].mRideHeight
        rideh_rl = plr_tele.mWheels[2].mRideHeight
        rideh_rr = plr_tele.mWheels[3].mRideHeight
        rake = (rideh_rr + rideh_rl - rideh_fr - rideh_fl) * 0.5
        return rideh_fl, rideh_fr, rideh_rl, rideh_rr, rake

    def temp(self):
        """Temperature data"""
        plr_tele = self.info.playersVehicleTelemetry()

        ttemp_fl = sum([plr_tele.mWheels[0].mTemperature[data] for data in range(3)]) / 3
        ttemp_fr = sum([plr_tele.mWheels[1].mTemperature[data] for data in range(3)]) / 3
        ttemp_rl = sum([plr_tele.mWheels[2].mTemperature[data] for data in range(3)]) / 3
        ttemp_rr = sum([plr_tele.mWheels[3].mTemperature[data] for data in range(3)]) / 3
        btemp_fl = plr_tele.mWheels[0].mBrakeTemp
        btemp_fr = plr_tele.mWheels[1].mBrakeTemp
        btemp_rl = plr_tele.mWheels[2].mBrakeTemp
        btemp_rr = plr_tele.mWheels[3].mBrakeTemp
        return ttemp_fl, ttemp_fr, ttemp_rl, ttemp_rr, btemp_fl, btemp_fr, btemp_rl, btemp_rr

    def wear(self):
        """Tyre wear data"""
        plr_tele = self.info.playersVehicleTelemetry()

        wear_fl = plr_tele.mWheels[0].mWear * 100
        wear_fr = plr_tele.mWheels[1].mWear * 100
        wear_rl = plr_tele.mWheels[2].mWear * 100
        wear_rr = plr_tele.mWheels[3].mWear * 100
        return wear_fl, wear_fr, wear_rl, wear_rr

    def pressure(self):
        """Tyre pressure data"""
        plr_tele = self.info.playersVehicleTelemetry()

        pres_fl = plr_tele.mWheels[0].mPressure
        pres_fr = plr_tele.mWheels[1].mPressure
        pres_rl = plr_tele.mWheels[2].mPressure
        pres_rr = plr_tele.mWheels[3].mPressure
        return pres_fl, pres_fr, pres_rl, pres_rr

    def force(self):
        """Force data"""
        plr_tele = self.info.playersVehicleTelemetry()

        gf_lgt = plr_tele.mLocalAccel.z / 9.8  # long g-force
        gf_lat = plr_tele.mLocalAccel.x / 9.8  # lat g-force
        df_ratio = calc.downforce_ratio(plr_tele.mFrontDownforce, plr_tele.mRearDownforce)
        return gf_lgt, gf_lat, df_ratio

    def drs(self):
        """DRS data"""
        plr_tele = self.info.playersVehicleTelemetry()

        drs_on = plr_tele.mRearFlapActivated
        drs_status = plr_tele.mRearFlapLegalStatus
        return drs_on, drs_status

    def engine(self):
        """Engine data"""
        plr_tele = self.info.playersVehicleTelemetry()

        temp_oil = plr_tele.mEngineOilTemp
        temp_water = plr_tele.mEngineWaterTemp
        e_turbo = plr_tele.mTurboBoostPressure
        e_rpm = plr_tele.mEngineRPM
        return temp_oil, temp_water, e_turbo, e_rpm

    def weather(self):
        """Weather data"""
        rf2_scor = self.info.Rf2Scor.mScoringInfo

        amb_temp = rf2_scor.mAmbientTemp
        trk_temp = rf2_scor.mTrackTemp
        rain = rf2_scor.mRaining * 100
        min_wet = rf2_scor.mMinPathWetness * 100
        max_wet = rf2_scor.mMaxPathWetness * 100
        avg_wet = rf2_scor.mAvgPathWetness * 100
        return amb_temp, trk_temp, rain, min_wet, max_wet, avg_wet

    def relative_list(self):
        """Create relative list"""
        # Get total number of vehicles in session
        total_veh = self.info.Rf2Scor.mScoringInfo.mNumVehicles

        # Create vehicle dict based on total vehicles
        # Use "vehicle index" as key, "distance position" as value
        # Filter out negative distance value to zero
        veh_dict = {index:max(self.info.Rf2Scor.mVehicles[index].mLapDist, 0)
                    for index in range(0, total_veh)}

        # Reverse-sort dict by values
        re_veh_dict = dict(sorted(veh_dict.items(), key=lambda item: item[1], reverse=True))

        # Extract keys (vehicle index) to create new sorted vehicle list
        sorted_veh_list = list(re_veh_dict.keys())

        # Append with -1 if sorted vehicle list has less than 7 items
        if len(sorted_veh_list) < 7:
            for index in range(7-len(sorted_veh_list)):
                sorted_veh_list.append(-1)

        # Double extend list
        sorted_veh_list *= 2

        # Locate player vehicle index in list
        try:
            plr_num = sorted_veh_list.index(self.info.playersDriverNum())
        except TypeError:
            plr_num = 0

        # Center selection range on player index from sorted vehicle list
        selected_list = [sorted_veh_list[index] for index in range(plr_num - 3, plr_num + 4)]
        return selected_list

    def relative_data(self, index, index_player):
        """Relative data"""
        rf2_scor = self.info.Rf2Scor

        if index >= 0:
            # Driver place position
            place = f"{rf2_scor.mVehicles[index].mPlace:02d}"

            # Driver name
            driver = Cbytestring2Python(rf2_scor.mVehicles[index].mDriverName)

            # Lap time
            laptime = calc.sec2laptime(max(rf2_scor.mVehicles[index].mLastLapTime, 0))

            # Vehicle class
            veh_class = Cbytestring2Python(rf2_scor.mVehicles[index].mVehicleClass)

            # Relative distance position
            track_length = rf2_scor.mScoringInfo.mLapDist  # track length
            track_half = track_length * 0.5  # half of track length
            opv_dist = rf2_scor.mVehicles[index].mLapDist  # opponent player vehicle position
            plr_dist = rf2_scor.mVehicles[index_player].mLapDist  # player vehicle position
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

            # Player speed
            speed = int(calc.vel2speed(
                        rf2_scor.mVehicles[index_player].mLocalVel.x,
                        rf2_scor.mVehicles[index_player].mLocalVel.y,
                        rf2_scor.mVehicles[index_player].mLocalVel.z))

            # Calculate relative time gap
            try:
                time_gap = f"{rel_dist / speed:.01f}"
            except ZeroDivisionError:
                time_gap = "0.0"

            # Number of completed
            num_lap = self.info.Rf2Tele.mVehicles[index].mLapNumber
        else:
            # Assign empty value to -1 player index
            place, driver, laptime, veh_class, time_gap, num_lap = "", "", "", "", "", 0
        return place, driver, laptime, veh_class, time_gap, num_lap
