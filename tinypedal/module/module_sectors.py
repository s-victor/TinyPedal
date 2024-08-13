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
Sectors module
"""

import logging
import csv
from functools import partial

from ._base import DataModule
from ..module_info import minfo
from ..const import PATH_SECTORBEST
from ..api_control import api
from .. import validator as val

MODULE_NAME = "module_sectors"
MAGIC_NUM = 99999  # magic number for default variable not updated by rF2

logger = logging.getLogger(__name__)
round6 = partial(round, ndigits=6)


class Realtime(DataModule):
    """Sectors data"""
    filepath = PATH_SECTORBEST

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self.event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    combo_id = api.read.check.combo_id()  # current car & track combo
                    session_id = api.read.check.session_id()  # session identity
                    (best_s_tb, best_s_pb, all_best_s_tb, all_best_s_pb
                     ) = load_sectors(self.filepath, combo_id, session_id)

                    if self.mcfg["enable_all_time_best_sectors"]:
                        gen_calc_sectors_session = calc_sectors(None, best_s_tb, best_s_pb)
                        gen_calc_sectors_alltime = calc_sectors(minfo.sectors, all_best_s_tb, all_best_s_pb)
                    else:
                        gen_calc_sectors_session = calc_sectors(minfo.sectors, best_s_tb, best_s_pb)
                        gen_calc_sectors_alltime = calc_sectors(None, all_best_s_tb, all_best_s_pb)
                    next(gen_calc_sectors_session)
                    next(gen_calc_sectors_alltime)

                # Run calculation
                tele_sectors = telemetry_sectors()
                gen_calc_sectors_session.send(tele_sectors)
                gen_calc_sectors_alltime.send(tele_sectors)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

                    best_s_tb, best_s_pb, new_best_session = gen_calc_sectors_session.send(tele_sectors)
                    all_best_s_tb, all_best_s_pb, new_best_all = gen_calc_sectors_alltime.send(tele_sectors)
                    if new_best_all or new_best_session:
                        save_sectors((
                            session_id,
                            list(map(round6, best_s_tb)),
                            list(map(round6, best_s_pb)),
                            list(map(round6, all_best_s_tb)),
                            list(map(round6, all_best_s_pb))),
                            self.filepath, combo_id)


def telemetry_sectors():
    """Telemetry sectors"""
    sector_idx = api.read.lap.sector_index()
    laptime_valid = api.read.timing.last_laptime()
    curr_sector1 = api.read.timing.current_sector1()
    curr_sector2 = api.read.timing.current_sector2()
    last_sector2 = api.read.timing.last_sector2()
    return sector_idx, laptime_valid, curr_sector1, curr_sector2, last_sector2


def calc_sectors(output, best_s_tb, best_s_pb):
    """Calculate sectors data"""
    no_delta_s = True
    new_best = False  # save check whether new sector best time is set
    last_sector_idx = -1  # previous recorded sector index value
    delta_s_tb = [0,0,0]  # deltabest times against all time best sector
    delta_s_pb = [0,0,0]  # deltabest times against best laptime sector
    prev_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]  # previous sector times
    laptime_best = sum(best_s_pb)

    while True:
        (sector_idx, laptime_valid, curr_sector1, curr_sector2, last_sector2
         ) = yield best_s_tb, best_s_pb, new_best

        # Update previous & best sector time
        if last_sector_idx != sector_idx:  # keep checking until conditions met

            # While vehicle in S1, update S3 data
            if sector_idx == 0 and laptime_valid > 0 and last_sector2 > 0:
                last_sector_idx = sector_idx  # reset & stop checking

                prev_s[2] = laptime_valid - last_sector2

                # Update (time gap) deltabest bestlap sector 3
                if val.sector_time(best_s_pb[2]):
                    delta_s_pb[2] = prev_s[2] - best_s_pb[2]

                # Update deltabest sector 3
                if val.sector_time(best_s_tb[2]):
                    delta_s_tb[2] = prev_s[2] - best_s_tb[2]
                    no_delta_s = False
                else:
                    no_delta_s = True

                # Save best sector 3 time
                if prev_s[2] < best_s_tb[2]:
                    best_s_tb[2] = prev_s[2]
                    new_best = True

                # Save sector time from personal best laptime
                if laptime_valid < laptime_best and val.sector_time(prev_s):
                    laptime_best = laptime_valid
                    best_s_pb = prev_s.copy()
                    new_best = True

            # While vehicle in S2, update S1 data
            elif sector_idx == 1 and curr_sector1 > 0:
                last_sector_idx = sector_idx  # reset

                prev_s[0] = curr_sector1

                # Update (time gap) deltabest bestlap sector 1
                if val.sector_time(best_s_pb[0]):
                    delta_s_pb[0] = prev_s[0] - best_s_pb[0]

                # Update deltabest sector 1
                if val.sector_time(best_s_tb[0]):
                    delta_s_tb[0] = prev_s[0] - best_s_tb[0]
                    no_delta_s = False
                else:
                    no_delta_s = True

                # Save best sector 1 time
                if prev_s[0] < best_s_tb[0]:
                    best_s_tb[0] = prev_s[0]
                    new_best = True

            # While vehicle in S3, update S2 data
            elif sector_idx == 2 and curr_sector2 > 0 and curr_sector1 > 0:
                last_sector_idx = sector_idx  # reset

                prev_s[1] = curr_sector2 - curr_sector1

                # Update (time gap) deltabest bestlap sector 2
                if val.sector_time(best_s_pb[1]):
                    delta_s_pb[1] = prev_s[1] - best_s_pb[1]

                # Update deltabest sector 2
                if val.sector_time(best_s_tb[1]):
                    delta_s_tb[1] = prev_s[1] - best_s_tb[1]
                    no_delta_s = False
                else:
                    no_delta_s = True

                # Save best sector 2 time
                if prev_s[1] < best_s_tb[1]:
                    best_s_tb[1] = prev_s[1]
                    new_best = True

            # Output sectors data
            if output:
                output.sectorIndex = sector_idx
                output.deltaSectorBestPB = delta_s_pb
                output.deltaSectorBestTB = delta_s_tb
                output.sectorBestTB = best_s_tb
                output.sectorBestPB = best_s_pb
                output.sectorPrev = prev_s
                output.noDeltaSector = no_delta_s


def load_sectors(filepath:str, combo: str, session_id: tuple):
    """Load sectors data"""
    temp_s = [MAGIC_NUM,MAGIC_NUM,MAGIC_NUM]
    try:
        with open(f"{filepath}{combo}.sector", newline="", encoding="utf-8") as csvfile:
            temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
            # Check if same session
            if (temp_list[0][0] == session_id[0] and  # session_stamp
                temp_list[0][1] <= session_id[1] and  # session_etime
                temp_list[0][2] <= session_id[2]):    # session_tlaps
                # Session best data
                best_s_tb = [temp_list[1][0], temp_list[1][1], temp_list[1][2]]
                best_s_pb = [temp_list[2][0], temp_list[2][1], temp_list[2][2]]
            else:
                best_s_tb = temp_s.copy()
                best_s_pb = temp_s.copy()
            # All time best data
            all_best_s_tb = [temp_list[3][0], temp_list[3][1], temp_list[3][2]]
            all_best_s_pb = [temp_list[4][0], temp_list[4][1], temp_list[4][2]]
    except (FileNotFoundError, IndexError, ValueError, TypeError):
        logger.info("MISSING: sectors best data")
        best_s_tb = temp_s.copy()
        best_s_pb = temp_s.copy()
        all_best_s_tb = temp_s.copy()
        all_best_s_pb = temp_s.copy()
    return best_s_tb, best_s_pb, all_best_s_tb, all_best_s_pb


def save_sectors(dataset: tuple, filepath: str, combo: str):
    """Save sectors best

    sector(CSV) file structure:
        Line 0: session stamp, session elapsed time, session total laps
        Line 1: session theoretical best sector time
        Line 2: session personal best sector time
        Line 3: all time theoretical best sector time
        Line 4: all time personal best sector time
    """
    if len(dataset) == 5:
        with open(f"{filepath}{combo}.sector", "w", newline="", encoding="utf-8") as csvfile:
            sectorwrite = csv.writer(csvfile)
            sectorwrite.writerows(dataset)
