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
Mapping module
"""

import logging
import time
import threading
import xml.dom.minidom

from ..const import PATH_TRACKMAP
from ..readapi import info, chknm, cs2py, state
from .. import calculation as calc
from .. import formatter as fmt

MODULE_NAME = "module_mapping"

logger = logging.getLogger(__name__)


class Realtime:
    """Mapping data"""
    module_name = MODULE_NAME

    def __init__(self, mctrl, config):
        self.mctrl = mctrl
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False
        self.set_output()

    def set_output(self, raw_coords=None, raw_dists=None, sector_index=None):
        """Set output"""
        self.coordinates = raw_coords
        self.elevations = raw_dists
        self.sectors = sector_index

    def start(self):
        """Start calculation thread"""
        if self.stopped:
            self.stopped = False
            self.running = True
            _thread = threading.Thread(target=self.__calculation, daemon=True)
            _thread.start()
            self.cfg.active_module_list.append(self)
            logger.info("mapping module started")

    def __calculation(self):
        """Mapping calculation"""
        reset = False
        map_recorder = MapRecorder()
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    MapData.load()
                    if MapData.exist:
                        update_interval = idle_interval
                        self.set_output(
                            MapData.raw_coords,
                            MapData.raw_dists,
                            MapData.sector_index
                        )
                    else:
                        map_recorder.reset()
                        self.set_output()

                if not MapData.exist:
                    map_recorder.update()
                    if MapData.exist:
                        update_interval = idle_interval
                        self.set_output(
                            MapData.raw_coords,
                            MapData.raw_dists,
                            MapData.sector_index
                        )
            else:
                if reset:
                    reset = False
                    update_interval = idle_interval

            time.sleep(update_interval)

        self.set_output()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("mapping module closed")


class MapRecorder:
    """Map data recorder"""

    def __init__(self):
        self.recording = False
        self.validating = False
        self.last_lap_stime = -1  # last lap start time
        self.last_sector_idx = -1
        self.pos_last = 0  # last checked player vehicle position

    def reset(self):
        """Reset to defaults"""
        self.recording = False
        self.validating = False
        self.last_sector_idx = -1
        self.last_lap_stime = -1
        self.pos_last = 0

    def update(self):
        """Update map data"""
        # Read telemetry
        (sector_idx, lap_stime, lap_etime, lastlap_check,
         pos_curr, gps_curr, elv_curr) = self.__telemetry()
        # Update map data
        self.__start(lap_stime)
        if self.validating:
            self.__validate(lap_etime, lastlap_check)
        if self.recording:
            self.__record_sector(sector_idx)
            self.__record_path(pos_curr, gps_curr, elv_curr)

    def __start(self, lap_stime):
        """Lap start & finish detection"""
        # Init reset
        if self.last_lap_stime == -1:
            MapData.reset()
            self.last_lap_stime = lap_stime
        # New lap
        if lap_stime > self.last_lap_stime:
            self.__record_end()
            MapData.reset()
            self.last_lap_stime = lap_stime
            self.pos_last = 0
            self.recording = True
            #logger.info("map recording")

    def __validate(self, lap_etime, lastlap_check):
        """Validate map data after crossing finish line"""
        laptime_curr = lap_etime - self.last_lap_stime
        if 1 < laptime_curr <= 8 and lastlap_check > 0:
            MapData.save()
            MapData.exist = True
            self.recording = False
            self.validating = False
        # Switch off validating after 8s
        elif 8 < laptime_curr < 10:
            self.validating = False

    def __record_sector(self, sector_idx):
        """Record sector index"""
        if self.last_sector_idx != sector_idx:
            if sector_idx == 1:
                MapData.sector_index[0] = len(MapData.list_coords) - 1
            elif sector_idx == 2:
                MapData.sector_index[1] = len(MapData.list_coords) - 1
            self.last_sector_idx = sector_idx

    def __record_path(self, pos_curr, gps_curr, elv_curr):
        """Record driving path"""
        # Update if position value is different & positive
        if 0 <= pos_curr != self.pos_last:
            if pos_curr > self.pos_last:  # position further
                MapData.list_coords.append(gps_curr)
                MapData.list_dists.append((pos_curr, elv_curr))
            self.pos_last = pos_curr  # reset last position

    def __record_end(self):
        """End recording"""
        if MapData.list_coords:
            MapData.copy()
            self.validating = True

    @staticmethod
    def __telemetry():
        """Telemetry data"""
        sector_idx = (2,0,1)[min(max(chknm(info.syncedVehicleScoring().mSector), 0), 2)]
        lap_stime = chknm(info.syncedVehicleTelemetry().mLapStartET)
        lap_etime = chknm(info.syncedVehicleTelemetry().mElapsedTime)
        lastlap_check = chknm(info.syncedVehicleScoring().mLastLapTime)
        pos_curr = round(chknm(info.syncedVehicleScoring().mLapDist), 4)
        gps_curr = (round(chknm(info.syncedVehicleScoring().mPos.x), 4),
                    -round(chknm(info.syncedVehicleScoring().mPos.z), 4))
        elv_curr = round(chknm(info.syncedVehicleScoring().mPos.y), 4)
        return sector_idx, lap_stime, lap_etime, lastlap_check, pos_curr, gps_curr, elv_curr


class MapData:
    """Map data"""
    filepath = PATH_TRACKMAP
    filename = None
    exist = False
    # Output data
    svg_coords = None
    svg_dists = None
    raw_coords = None
    raw_dists = None
    sector_index = None
    # Data list current lap
    list_coords = None  # coordinates
    list_dists = None  # distances
    # For verification only
    list_coords_temp = None
    list_dists_temp = None
    sector_index_temp = None

    @classmethod
    def reset(cls):
        """Reset map data"""
        cls.exist = False
        cls.svg_coords = None
        cls.svg_dists = None
        cls.raw_coords = None
        cls.raw_dists = None
        cls.sector_index = [0,0]

        cls.list_coords = []
        cls.list_dists = []

    @classmethod
    def copy(cls):
        """Copy (reference) map data"""
        cls.list_coords_temp = cls.list_coords
        cls.list_dists_temp = cls.list_dists
        cls.sector_index_temp = cls.sector_index

    @classmethod
    def load(cls):
        """Load map data file"""
        cls.filename = fmt.strip_invalid_char(
            cs2py(info.LastScor.mScoringInfo.mTrackName))
        # Load map file
        (cls.svg_coords, cls.svg_dists, cls.sector_index
         ) = load_svg_file(cls.filename, cls.filepath)
        if cls.svg_coords:
            cls.raw_coords = fmt.points_to_coords(cls.svg_coords)
            cls.raw_dists = fmt.points_to_coords(cls.svg_dists)
            cls.exist = True
            #logger.info("map exist")
        else:
            cls.exist = False
            #logger.info("map not exist")

    @classmethod
    def save(cls):
        """Store & convert raw coordinates to svg points data"""
        cls.raw_coords = cls.list_coords_temp
        cls.raw_dists = cls.list_dists_temp
        cls.svg_coords = fmt.coords_to_points(cls.raw_coords)
        cls.svg_dists = fmt.coords_to_points(cls.raw_dists)
        cls.sector_index = cls.sector_index_temp
        # Save to svg file
        save_svg_file(
            cls.filename,
            cls.filepath,
            cls.svg_coords,
            cls.svg_dists,
            calc.map_view_box(cls.raw_coords, 20),
            cls.sector_index
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
        logger.info("no valid map data file found")
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
