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
Mapping module
"""

from functools import partial

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc
from ..userfile.track_map import load_track_map_file, save_track_map_file

MODULE_NAME = "module_mapping"

round4 = partial(round, ndigits=4)


class Realtime(DataModule):
    """Mapping data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        userpath_track_map = self.cfg.path.track_map
        output = minfo.mapping

        recorder = MapRecorder(userpath_track_map)

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    recorder.map.load(api.read.check.track_id())
                    if recorder.map.exist:
                        update_interval = self.idle_interval
                        output.coordinates = recorder.map.raw_coords
                        output.coordinatesHash = hash(output.coordinates)
                        output.elevations = recorder.map.raw_dists
                        output.elevationsHash = hash(output.elevations)
                        output.sectors = recorder.map.sectors_index
                    else:
                        recorder.reset()
                        output.coordinates = None
                        output.coordinatesHash = None
                        output.elevations = None
                        output.elevationsHash = None
                        output.sectors = None

                if not recorder.map.exist:
                    recorder.update()
                    if recorder.map.exist:
                        reset = False  # load recorded map in next loop
            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


class MapRecorder:
    """Map data recorder"""

    def __init__(self, filepath: str):
        self.map = MapData(filepath)
        self._recording = False
        self._validating = False
        self._last_lap_stime = -1  # last lap start time
        self._last_sector_idx = -1
        self._pos_last = 0  # last checked player vehicle position

    def reset(self):
        """Reset to defaults"""
        self._recording = False
        self._validating = False
        self._last_sector_idx = -1
        self._last_lap_stime = -1
        self._pos_last = 0

    def update(self):
        """Update map data"""
        self.__start(api.read.timing.start())
        if self._validating:
            self.__validate(api.read.timing.elapsed(), api.read.timing.last_laptime())
        if self._recording:
            self.__record_sector(api.read.lap.sector_index())
            self.__record_path(round4(api.read.lap.distance()))

    def __start(self, lap_stime: float):
        """Lap start & finish detection"""
        # Init reset
        if self._last_lap_stime == -1:
            self.map.reset()
            self._last_lap_stime = lap_stime
        # New lap
        if lap_stime > self._last_lap_stime:
            self.__record_end()
            self.map.reset()
            self._last_lap_stime = lap_stime
            self._pos_last = 0
            self._recording = True
            #logger.info("map recording")

    def __validate(self, lap_etime: float, laptime_valid: float):
        """Validate map data after crossing finish line"""
        laptime_curr = lap_etime - self._last_lap_stime
        if 1 < laptime_curr <= 8 and laptime_valid > 0:
            self.map.save()
            self.map.exist = True
            self._recording = False
            self._validating = False
        # Switch off validating after 8s
        elif 8 < laptime_curr < 10:
            self._validating = False

    def __record_sector(self, sector_idx: int):
        """Record sector index"""
        if self._last_sector_idx != sector_idx:
            if sector_idx == 1:
                self.map.sectors_index[0] = len(self.map.raw_coords) - 1
            elif sector_idx == 2:
                self.map.sectors_index[1] = len(self.map.raw_coords) - 1
            self._last_sector_idx = sector_idx

    def __record_path(self, pos_curr: float):
        """Record driving path"""
        # Update if position value is different & positive
        if 0 <= pos_curr != self._pos_last:
            if pos_curr > self._pos_last:  # position further
                gps_curr = (round4(api.read.vehicle.position_longitudinal()),
                            round4(api.read.vehicle.position_lateral()))
                elv_curr = round4(api.read.vehicle.position_vertical())
                self.map.raw_coords.append(gps_curr)
                self.map.raw_dists.append((pos_curr, elv_curr))
            self._pos_last = pos_curr  # reset last position

    def __record_end(self):
        """End recording"""
        if self.map.raw_coords:
            self.map.copy()
            self._validating = True


class MapData:
    """Map data"""

    def __init__(self, filepath: str):
        self.exist = False
        # Raw data
        self.raw_coords = None
        self.raw_dists = None
        self.sectors_index = None
        # File info
        self._filepath = filepath
        self._filename = None
        # Temp data
        self._temp_raw_coords = None
        self._temp_raw_dists = None
        self._temp_sectors_index = None

    def reset(self):
        """Reset map data"""
        self.exist = False
        self.raw_coords = []
        self.raw_dists = []
        self.sectors_index = [0,0]

    def copy(self):
        """Copy map data to temp and convert to tuple for hash"""
        self._temp_raw_coords = tuple(self.raw_coords)
        self._temp_raw_dists = tuple(self.raw_dists)
        self._temp_sectors_index = tuple(self.sectors_index)

    def load(self, filename: str):
        """Load map data file"""
        self._filename = filename
        # Load map file
        raw_coords, raw_dists, sectors_index = load_track_map_file(
            filepath=self._filepath,
            filename=self._filename,
        )
        if raw_coords and raw_dists:
            self.raw_coords = raw_coords
            self.raw_dists = raw_dists
            self.sectors_index = sectors_index
            self.exist = True
            #logger.info("map exist")
        else:
            self.exist = False
            #logger.info("map not exist")

    def save(self):
        """Store & convert raw coordinates to svg points data"""
        self.raw_coords = self._temp_raw_coords
        self.raw_dists = self._temp_raw_dists
        self.sectors_index = self._temp_sectors_index
        # Save to svg file
        save_track_map_file(
            filepath=self._filepath,
            filename=self._filename,
            view_box=calc.svg_view_box(self.raw_coords, 20),
            raw_coords=self.raw_coords,
            raw_dists=self.raw_dists,
            sector_index=self.sectors_index,
        )
        #logger.info("map saved, stopped map recording")
