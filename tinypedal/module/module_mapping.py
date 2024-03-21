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
import threading
import xml.dom.minidom

from ..module_info import minfo
from ..const import PATH_TRACKMAP
from ..api_control import api
from .. import calculation as calc
from .. import formatter as fmt

MODULE_NAME = "module_mapping"

logger = logging.getLogger(__name__)


class Realtime:
    """Mapping data"""
    module_name = MODULE_NAME

    def __init__(self, config):
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.event = threading.Event()

    def start(self):
        """Start update thread"""
        if self.stopped:
            self.stopped = False
            self.event.clear()
            threading.Thread(target=self.__update_data, daemon=True).start()
            self.cfg.active_module_list.append(self)
            logger.info("ACTIVE: module mapping")

    def stop(self):
        """Stop thread"""
        self.event.set()

    def __update_data(self):
        """Update module data"""
        reset = False
        recorder = MapRecorder()
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = active_interval

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = active_interval

                    recorder.map.load(api.read.check.track_id())
                    if recorder.map.exist:
                        update_interval = idle_interval
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
                    update_interval = idle_interval

        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("CLOSED: module mapping")


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
        pos_curr = round(api.read.lap.distance(), 4)
        gps_curr = (round(api.read.vehicle.position_longitudinal(), 4),
                    round(api.read.vehicle.position_lateral(), 4))
        elv_curr = round(api.read.vehicle.position_vertical(), 4)

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
        # SVG data
        self._svg_coords = None
        self._svg_dists = None
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
        self._svg_coords = None
        self._svg_dists = None

    def copy(self):
        """Copy map data to temp and convert to tuple for hash"""
        self._temp_raw_coords = tuple(self.raw_coords)
        self._temp_raw_dists = tuple(self.raw_dists)
        self._temp_sectors_index = tuple(self.sectors_index)

    def load(self, filename):
        """Load map data file"""
        self._filename = filename
        # Load map file
        (self._svg_coords, self._svg_dists, self.sectors_index
         ) = load_svg_file(self._filename, self._filepath)
        if self._svg_coords:
            self.raw_coords = fmt.points_to_coords(self._svg_coords)
            self.raw_dists = fmt.points_to_coords(self._svg_dists)
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
        # Convert to svg coordinates
        self._svg_coords = fmt.coords_to_points(self.raw_coords)
        self._svg_dists = fmt.coords_to_points(self.raw_dists)
        # Save to svg file
        save_svg_file(
            self._filename,
            self._filepath,
            self._svg_coords,
            self._svg_dists,
            calc.map_view_box(self.raw_coords, 20),
            self.sectors_index
        )
        #logger.info("map saved, stopped map recording")


def load_svg_file(filename, pathname):
    """Load svg file"""
    try:
        dom = xml.dom.minidom.parse(f"{pathname}{filename}.svg")
        desc_col = dom.documentElement.getElementsByTagName("desc")
        path_col = dom.documentElement.getElementsByTagName("polyline")
        sector_index = fmt.string_pair_to_int(desc_col[0].childNodes[0].nodeValue)

        for tags in path_col:
            if tags.getAttribute("id") == "map":
                svg_coords = tags.getAttribute("points")
                continue
            if tags.getAttribute("id") == "dist":
                svg_dists = tags.getAttribute("points")
                continue

        return svg_coords, svg_dists, sector_index
    except (FileNotFoundError, IndexError, xml.parsers.expat.ExpatError):
        logger.info("MISSING: track map data")
        return None, None, None


def save_svg_file(filename, pathname, svg_coords, svg_dists, view_box, sector_index):
    """Save svg file"""
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
