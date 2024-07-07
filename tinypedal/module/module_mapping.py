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

import logging
import xml.dom.minidom
from functools import partial

from ._base import DataModule
from ..module_info import minfo
from ..const import PATH_TRACKMAP
from ..api_control import api
from .. import calculation as calc
from .. import formatter as fmt

MODULE_NAME = "module_mapping"

logger = logging.getLogger(__name__)
round4 = partial(round, ndigits=4)


class Realtime(DataModule):
    """Mapping data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        recorder = MapRecorder()
        update_interval = self.active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    recorder.map.load(api.read.check.track_id())
                    if recorder.map.exist:
                        update_interval = self.idle_interval
                        minfo.mapping.coordinates = recorder.map.raw_coords
                        minfo.mapping.coordinatesHash = hash(minfo.mapping.coordinates)
                        minfo.mapping.elevations = recorder.map.raw_dists
                        minfo.mapping.elevationsHash = hash(minfo.mapping.elevations)
                        minfo.mapping.sectors = recorder.map.sectors_index
                    else:
                        recorder.reset()
                        minfo.mapping.coordinates = None
                        minfo.mapping.coordinatesHash = None
                        minfo.mapping.elevations = None
                        minfo.mapping.elevationsHash = None
                        minfo.mapping.sectors = None

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

    def __init__(self):
        self.map = MapData()
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
        # Read telemetry
        lap_stime = api.read.timing.start()
        lap_etime = api.read.timing.elapsed()
        laptime_valid = api.read.timing.last_laptime()
        sector_idx = api.read.lap.sector_index()
        pos_curr = round4(api.read.lap.distance())
        gps_curr = (round4(api.read.vehicle.position_longitudinal()),
                    round4(api.read.vehicle.position_lateral()))
        elv_curr = round4(api.read.vehicle.position_vertical())

        # Update map data
        self.__start(lap_stime)
        if self._validating:
            self.__validate(lap_etime, laptime_valid)
        if self._recording:
            self.__record_sector(sector_idx)
            self.__record_path(pos_curr, gps_curr, elv_curr)

    def __start(self, lap_stime):
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

    def __validate(self, lap_etime, laptime_valid):
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

    def __record_sector(self, sector_idx):
        """Record sector index"""
        if self._last_sector_idx != sector_idx:
            if sector_idx == 1:
                self.map.sectors_index[0] = len(self.map.raw_coords) - 1
            elif sector_idx == 2:
                self.map.sectors_index[1] = len(self.map.raw_coords) - 1
            self._last_sector_idx = sector_idx

    def __record_path(self, pos_curr, gps_curr, elv_curr):
        """Record driving path"""
        # Update if position value is different & positive
        if 0 <= pos_curr != self._pos_last:
            if pos_curr > self._pos_last:  # position further
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

    def __init__(self):
        self.exist = False
        # Raw data
        self.raw_coords = None
        self.raw_dists = None
        self.sectors_index = None
        # File info
        self._filepath = PATH_TRACKMAP
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

    def load(self, filename):
        """Load map data file"""
        self._filename = filename
        # Load map file
        raw_coords, raw_dists, sectors_index = load_svg_file(self._filename, self._filepath)
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
        save_svg_file(
            self._filename,
            self._filepath,
            self.raw_coords,
            self.raw_dists,
            calc.svg_view_box(self.raw_coords, 20),
            self.sectors_index
        )
        #logger.info("map saved, stopped map recording")


def load_svg_file(filename, pathname):
    """Load svg file"""
    try:
        dom = xml.dom.minidom.parse(f"{pathname}{filename}.svg")
        desc_col = dom.documentElement.getElementsByTagName("desc")
        path_col = dom.documentElement.getElementsByTagName("polyline")

        for tags in path_col:
            if tags.getAttribute("id") == "map":
                svg_coords = tags.getAttribute("points")
                continue
            if tags.getAttribute("id") == "dist":
                svg_dists = tags.getAttribute("points")
                continue

        # Convert to coordinates list
        raw_coords = fmt.points_to_coords(svg_coords)
        raw_dists = fmt.points_to_coords(svg_dists)
        sector_index = fmt.string_pair_to_int(desc_col[0].childNodes[0].nodeValue)

        return raw_coords, raw_dists, sector_index
    except (FileNotFoundError, IndexError, ValueError, xml.parsers.expat.ExpatError):
        logger.info("MISSING: track map data")
        return None, None, None


def save_svg_file(filename, pathname, raw_coords, raw_dists, view_box, sector_index):
    """Save svg file"""
    # Convert to svg coordinates
    svg_coords = fmt.coords_to_points(raw_coords)
    svg_dists = fmt.coords_to_points(raw_dists)

    # Create new svg file
    new_svg = xml.dom.minidom.Document()

    # Create comments
    root_comment = new_svg.createComment(" Track map generated with TinyPedal ")
    new_svg.appendChild(root_comment)

    # Create svg
    root_node = new_svg.createElement("svg")
    root_node.setAttribute("viewBox", view_box)
    root_node.setAttribute("version", "1.1")
    root_node.setAttribute("xmlns", "http://www.w3.org/2000/svg")
    new_svg.appendChild(root_node)

    # Create title
    title_node = new_svg.createElement("title")
    title_text = new_svg.createTextNode(filename)
    title_node.appendChild(title_text)
    root_node.appendChild(title_node)

    # Create desc
    desc_comment = new_svg.createComment(" Sector coordinates index ")
    root_node.appendChild(desc_comment)

    desc_node = new_svg.createElement("desc")
    desc_text = new_svg.createTextNode(f"{sector_index[0]},{sector_index[1]}")
    desc_node.appendChild(desc_text)
    root_node.appendChild(desc_node)

    # Create map
    map_comment = new_svg.createComment(" Raw global coordinates ")
    root_node.appendChild(map_comment)

    map_node = new_svg.createElement("polyline")
    map_node.setAttribute("id", "map")
    map_node.setAttribute("fill", "none")
    map_node.setAttribute("stroke", "black")
    map_node.setAttribute("stroke-width", "10")
    map_node.setAttribute("points", svg_coords)
    root_node.appendChild(map_node)

    # Create distance
    dist_comment = new_svg.createComment(" Raw distance reference points ")
    root_node.appendChild(dist_comment)

    dist_node = new_svg.createElement("polyline")
    dist_node.setAttribute("id", "dist")
    dist_node.setAttribute("fill", "none")
    dist_node.setAttribute("stroke", "none")
    dist_node.setAttribute("stroke-width", "0")
    dist_node.setAttribute("points", svg_dists)
    root_node.appendChild(dist_node)

    # Save svg
    with open(f"{pathname}{filename}.svg", "w", encoding="utf-8") as svgfile:
        new_svg.writexml(svgfile, indent="", addindent="\t", newl="\n", encoding="utf-8")
