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
Sectors module
"""

import re
import logging
import time
import threading

from ..module_info import minfo
from ..readapi import info, chknm, state, combo_check, session_check
from .. import validator as val

MODULE_NAME = "module_sectors"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2

logger = logging.getLogger(__name__)


class Realtime:
    """Sectors data"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("sectors module started")

    def __calculation(self):
        """Sectors calculation"""
        reset = False
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    last_sector_idx = -1                # previous recorded sector index value
                    combo_name = combo_check()          # current car & track combo
                    session_id = session_check()        # session identity
                    best_laptime, best_s_tb, best_s_pb = self.load_sector_data(
                        combo_name, session_id)
                    delta_s_tb = [0,0,0]                   # deltabest times against all time best sector
                    delta_s_pb = [0,0,0]           # deltabest times against best laptime sector
                    prev_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]  # previous sector times
                    no_delta_s = True

                # Read telemetry
                (sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime
                 ) = self.__telemetry()

                # Update previous & best sector time
                if last_sector_idx != sector_idx:  # keep checking until conditions met

                    # While vehicle in S1, update S3 data
                    if sector_idx == 0 and last_laptime > 0 and last_sector2 > 0:
                        last_sector_idx = sector_idx  # reset & stop checking

                        prev_s[2] = last_laptime - last_sector2

                        # Update (time gap) deltabest bestlap sector 3 text
                        if val.sector_time(best_s_pb[2]):
                            delta_s_pb[2] = prev_s[2] - best_s_pb[2] + delta_s_pb[1]

                        # Update deltabest sector 3 text
                        if val.sector_time(best_s_tb[2]):
                            delta_s_tb[2] = prev_s[2] - best_s_tb[2]
                            no_delta_s = False
                        else:
                            no_delta_s = True

                        # Save best sector 3 time
                        if prev_s[2] < best_s_tb[2]:
                            best_s_tb[2] = prev_s[2]

                        # Save sector time from personal best laptime
                        if last_laptime < best_laptime and val.sector_time(prev_s):
                            best_laptime = last_laptime
                            best_s_pb = prev_s.copy()

                    # While vehicle in S2, update S1 data
                    elif sector_idx == 1 and curr_sector1 > 0:
                        last_sector_idx = sector_idx  # reset

                        prev_s[0] = curr_sector1

                        # Update (time gap) deltabest bestlap sector 1 text
                        if val.sector_time(best_s_pb[0]):
                            delta_s_pb[0] = prev_s[0] - best_s_pb[0]

                        # Update deltabest sector 1 text
                        if val.sector_time(best_s_tb[0]):
                            delta_s_tb[0] = prev_s[0] - best_s_tb[0]
                            no_delta_s = False
                        else:
                            no_delta_s = True

                        # Save best sector 1 time
                        if prev_s[0] < best_s_tb[0]:
                            best_s_tb[0] = prev_s[0]

                    # While vehicle in S3, update S2 data
                    elif sector_idx == 2 and curr_sector2 > 0 and curr_sector1 > 0:
                        last_sector_idx = sector_idx  # reset

                        prev_s[1] = curr_sector2 - curr_sector1

                        # Update (time gap) deltabest bestlap sector 2 text
                        if val.sector_time(best_s_pb[1]):
                            delta_s_pb[1] = prev_s[1] - best_s_pb[1] + delta_s_pb[0]

                        # Update deltabest sector 2 text
                        if val.sector_time(best_s_tb[1]):
                            delta_s_tb[1] = prev_s[1] - best_s_tb[1]
                            no_delta_s = False
                        else:
                            no_delta_s = True

                        # Save best sector 2 time
                        if prev_s[1] < best_s_tb[1]:
                            best_s_tb[1] = prev_s[1]

                # Output sectors data
                minfo.sectors.SectorIndex = min(max(last_sector_idx, 0), 2)
                minfo.sectors.DeltaSectorBestPB = delta_s_pb
                minfo.sectors.DeltaSectorBestTB = delta_s_tb
                minfo.sectors.SectorBestTB = best_s_tb
                minfo.sectors.SectorBestPB = best_s_pb
                minfo.sectors.SectorPrev = prev_s
                minfo.sectors.NoDeltaSector = no_delta_s

            else:
                if reset:
                    reset = False
                    update_interval = idle_interval
                    # Save only valid sector data
                    self.save_sector_data(
                        combo_name, session_id, best_s_pb, best_laptime, best_s_tb)

            time.sleep(update_interval)

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("sectors module closed")

    @staticmethod
    def __telemetry():
        """Telemetry data

        Convert game sector index order to 0,1,2 for consistency.
        """
        sector_idx = (2,0,1)[min(max(chknm(info.playerScor.mSector), 0), 2)]
        curr_sector1 = chknm(info.playerScor.mCurSector1)
        curr_sector2 = chknm(info.playerScor.mCurSector2)
        last_sector2 = chknm(info.playerScor.mLastSector2)
        last_laptime = chknm(info.playerScor.mLastLapTime)
        return sector_idx, curr_sector1, curr_sector2, last_sector2, last_laptime

    def save_sector_data(self, combo_name, session_id, best_s_pb, best_laptime, best_s_tb):
        """Verify and save sector data"""
        if session_id and val.sector_time(best_s_pb):
            self.mcfg["sector_info"] = (
                str(combo_name)
                + "|" + str(session_id[0])
                + "|" + str(session_id[1])
                + "|" + str(session_id[2])
                + "|" + str(best_laptime)
                + "|" + str(best_s_tb[0])
                + "|" + str(best_s_tb[1])
                + "|" + str(best_s_tb[2])
                + "|" + str(best_s_pb[0])
                + "|" + str(best_s_pb[1])
                + "|" + str(best_s_pb[2])
                )
            self.cfg.save()

    def load_sector_data(self, combo_name, session_id):
        """Load and verify sector data

        Check if saved data is from same session, car, track combo, discard if not
        """
        saved_data = self.parse_save_string(self.mcfg["sector_info"])
        if (combo_name == saved_data[0] and
            saved_data[1] == session_id[0] and
            saved_data[2] <= session_id[1] and
            saved_data[3] <= session_id[2]):
            # Assign loaded data
            best_laptime = saved_data[4]  # best laptime (seconds)
            best_s_tb = saved_data[5]     # theory best sector times
            best_s_pb = saved_data[6]     # personal best sector times
        else:
            logger.info("no valid sectors data found")
            best_laptime = MAGIC_NUM
            best_s_tb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
            best_s_pb = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
        return best_laptime, best_s_tb, best_s_pb

    def parse_save_string(self, save_data):
        """Parse last saved sector data"""
        rex_string = re.split(r"(\|)", save_data)
        data_gen = self.split_save_string(rex_string)
        data = list(data_gen)

        try:  # fill in data
            final_list = [
                data[0],                    # 0 - combo name, str
                data[1],                    # 1 - session stamp, str
                data[2],                    # 2 - session elapsed time, float
                data[3],                    # 3 - session total laps, float
                data[4],                    # 4 - best_laptime, float
                [data[5],data[6],data[7]],  # 5 - best_s_tb, float
                [data[8],data[9],data[10]]  # 6 - best_s_pb, float
            ]
        except IndexError:  # reset data
            final_list = ["None"]

        return final_list

    @staticmethod
    def split_save_string(rex_string):
        """Split save string"""
        for index, value in enumerate(rex_string):
            if value != "|":
                if index <= 2:
                    yield value
                else:
                    yield float(value)
