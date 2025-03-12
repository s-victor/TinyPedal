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
from ..validator import file_last_modified
from ..file_constants import FILE_EXT
from .. import calculation as calc
from ..userfile.track_map import load_track_map_file, save_track_map_file

round4 = partial(round, ndigits=4)


class Realtime(DataModule):
    """Mapping data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)

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

                    recorder.load_map(api.read.check.track_id())
                    if recorder.map_exist:
                        update_interval = self.idle_interval
                        output.coordinates = recorder.output.coords
                        output.elevations = recorder.output.dists
                        output.sectors = recorder.output.sectors
                        output.lastModified = recorder.last_modified
                    else:
                        recorder.reset()
                        output.reset()

                if not recorder.map_exist:
                    recorder.update()
                    if recorder.map_exist:
                        reset = False  # load recorded map in next loop
            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


class MapCoords:
    """Map coords data"""

    __slots__ = (
        "coords",
        "dists",
        "sectors",
    )

    def __init__(self, coords=None, dists=None, sectors=None):
        """
        Args:
            coords: x,y coordinates list.
            dists: distance,elevation list.
            sectors: sector node index reference list.
        """
        self.coords = coords
        self.dists = dists
        self.sectors = sectors

    def clear(self):
        """Clear coords data"""
        self.coords = None
        self.dists = None
        self.sectors = None

    def reset(self):
        """Reset coords data"""
        self.coords = []
        self.dists = []
        self.sectors = [0, 0]


class MapRecorder:
    """Map data recorder"""

    def __init__(self, filepath: str):
        self._recording = False
        self._validating = False
        self._last_sector_idx = -1
        self._last_lap_stime = -1.0  # last lap start time
        self._pos_last = 0.0  # last checked player vehicle position
        # File info
        self.map_exist = False
        self.last_modified = 0.0
        self._filepath = filepath
        self._filename = ""
        # Map data
        self.output = MapCoords()
        self._recorder_data = MapCoords()
        self._temp_data = MapCoords()

    def reset(self):
        """Reset to defaults"""
        self._recording = False
        self._validating = False
        self._last_sector_idx = -1
        self._last_lap_stime = -1.0
        self._pos_last = 0.0

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
            self._recorder_data.reset()
            self._last_lap_stime = lap_stime
        # New lap
        if lap_stime > self._last_lap_stime:
            self.__record_end()
            self._recorder_data.reset()
            self._last_lap_stime = lap_stime
            self._pos_last = 0
            self._recording = True
            #logger.info("map recording")

    def __validate(self, lap_etime: float, laptime_valid: float):
        """Validate map data after crossing finish line"""
        laptime_curr = lap_etime - self._last_lap_stime
        if 1 < laptime_curr <= 8 and laptime_valid > 0:
            self.save_map()
            self._temp_data.clear()
            self._recorder_data.clear()
            self.map_exist = True
            self._recording = False
            self._validating = False
        # Switch off validating after 8s
        elif 8 < laptime_curr < 10:
            self._temp_data.clear()
            self._validating = False

    def __record_sector(self, sector_idx: int):
        """Record sector index"""
        if self._last_sector_idx != sector_idx:
            if sector_idx == 1:
                self._recorder_data.sectors[0] = len(self._recorder_data.coords) - 1
            elif sector_idx == 2:
                self._recorder_data.sectors[1] = len(self._recorder_data.coords) - 1
            self._last_sector_idx = sector_idx

    def __record_path(self, pos_curr: float):
        """Record driving path"""
        # Update if position value is different & positive
        if 0 <= pos_curr != self._pos_last:
            if pos_curr > self._pos_last:  # position further
                gps_curr = (round4(api.read.vehicle.position_longitudinal()),
                            round4(api.read.vehicle.position_lateral()))
                elv_curr = round4(api.read.vehicle.position_vertical())
                self._recorder_data.coords.append(gps_curr)
                self._recorder_data.dists.append((pos_curr, elv_curr))
            self._pos_last = pos_curr  # reset last position

    def __record_end(self):
        """End recording"""
        if self._recorder_data.coords:
            self._temp_data.coords = tuple(self._recorder_data.coords)
            self._temp_data.dists = tuple(self._recorder_data.dists)
            self._temp_data.sectors = tuple(self._recorder_data.sectors)
            self._validating = True

    def load_map(self, filename: str):
        """Load map data file"""
        self._filename = filename
        # Check if same map loaded
        modified = file_last_modified(
            filepath=self._filepath,
            filename=filename,
            extension=FILE_EXT.SVG,
        )
        is_loaded = self.last_modified == modified > 0
        self.last_modified = modified
        if is_loaded:
            self.map_exist = True
            return
        # Load map file
        raw_coords, raw_dists, sectors_index = load_track_map_file(
            filepath=self._filepath,
            filename=filename,
        )
        if raw_coords and raw_dists:
            self.output.coords = raw_coords
            self.output.dists = raw_dists
            self.output.sectors = sectors_index
            self.map_exist = True
            #logger.info("map exist")
        else:
            self.output.clear()
            self.map_exist = False
            #logger.info("map not exist")

    def save_map(self):
        """Store & convert raw coordinates to svg points data"""
        self.output.coords = self._temp_data.coords
        self.output.dists = self._temp_data.dists
        self.output.sectors = self._temp_data.sectors
        # Save to svg file
        save_track_map_file(
            filepath=self._filepath,
            filename=self._filename,
            view_box=calc.svg_view_box(self._temp_data.coords, 20),
            raw_coords=self._temp_data.coords,
            raw_dists=self._temp_data.dists,
            sector_index=self._temp_data.sectors,
        )
        #logger.info("map saved, stopped map recording")
