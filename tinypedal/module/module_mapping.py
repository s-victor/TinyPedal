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
        self.map_coordinates = raw_coords
        self.map_distance = raw_dists
        self.map_sectors = sector_index

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
        map_data = MapData()
        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not reset:
                    reset = True
                    update_interval = active_interval

                    map_data.reset()
                    map_data.load()
                    if map_data.exist:
                        update_interval = idle_interval
                        self.set_output(
                            map_data.raw_coords,
                            map_data.raw_dists,
                            map_data.sector_index
                        )
                    else:
                        self.set_output()

                if not map_data.exist:
                    map_data.update()
                    if map_data.exist:
                        update_interval = idle_interval
                        self.set_output(
                            map_data.raw_coords,
                            map_data.raw_dists,
                            map_data.sector_index
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


class MapData:
    """Map data"""
    filepath = PATH_TRACKMAP

    def __init__(self):
        self._map_exist = False
        self.recording = False
        self.validating = False

        self.coords_list_curr = []  # coordinates list, current lap
        self.coords_list_last = []  # for verification only
        self.dist_list_curr = []  # distance list, current lap
        self.dist_list_last = []  # for verification only
        self.pos_last = 0  # last checked player vehicle position
        self.last_lap_stime = 0  # last lap start time
        self.last_sector_idx = -1

        self.raw_coords = None
        self.raw_dists = None
        self.map_file = None
        self.svg_path_coords = None
        self.svg_path_dist = None
        self.sector_index = [0,0]

    def update(self):
        """Update map data"""
        # Read telemetry
        (sector_idx, lap_stime, lap_etime, lastlap_check,
         pos_curr, gps_curr, elv_curr) = self.__telemetry()

        # Reset lap start time
        if 0 == self.last_lap_stime != lap_stime:
            self.last_lap_stime = lap_stime

        # Update map data
        self.__start(lap_stime, pos_curr, gps_curr, elv_curr)
        if self.validating:
            self.__validate(lap_etime, lastlap_check)
        if self.recording:
            self.__record(sector_idx, pos_curr, gps_curr, elv_curr)

    @property
    def exist(self):
        """Check map existence"""
        return self._map_exist

    def reset(self):
        """Reset to defaults"""
        self._map_exist = False
        self.recording = False
        self.validating = False
        self.coords_list_curr = []
        self.dist_list_curr = []
        self.last_sector_idx = -1
        self.last_lap_stime = 0
        self.svg_path_coords = None
        self.svg_path_dist = None
        self.sector_index = [0,0]

    def load(self):
        """Load map data file"""
        self.map_file = fmt.strip_invalid_char(
            cs2py(info.LastScor.mScoringInfo.mTrackName))
        # Load map file
        (self.svg_path_coords, self.svg_path_dist, self.sector_index
            ) = load_svg(self.map_file, self.filepath)
        if self.svg_path_coords:
            self.raw_coords = fmt.points_to_coords(self.svg_path_coords)
            self.raw_dists = fmt.points_to_coords(self.svg_path_dist)
            self._map_exist = True
            #logger.info("map exist")
        else:
            self._map_exist = False
            #logger.info("map not exist")

    def __start(self, lap_stime, pos_curr, gps_curr, elv_curr):
        """Lap start & finish detection"""
        if lap_stime > self.last_lap_stime:  # difference of lap-start-time
            # End last lap recording
            if self.coords_list_curr:
                if calc.distance(self.coords_list_curr[0], gps_curr) > 500:
                    self.coords_list_curr.append(gps_curr)
                    self.dist_list_curr.append((pos_curr, elv_curr))
                self.coords_list_last = self.coords_list_curr
                self.dist_list_last = self.dist_list_curr
                self.validating = True
            # Reset data
            self.coords_list_curr = []
            self.dist_list_curr = []
            self.last_lap_stime = lap_stime
            self.pos_last = 0
            self.recording = True  # Activate recording
            #logger.info("map recording")

    def __validate(self, lap_etime, lastlap_check):
        """Validate map data after crossing finish line"""
        laptime_curr = lap_etime - self.last_lap_stime
        if 1 < laptime_curr <= 8 and lastlap_check > 0:
            # Store & convert raw coordinates to svg points data
            self.raw_coords = self.coords_list_last
            self.raw_dists = self.dist_list_last
            self.svg_path_coords = fmt.coords_to_points(self.raw_coords)
            self.svg_path_dist = fmt.coords_to_points(self.raw_dists)
            # Save to svg file
            save_svg(
                self.map_file,
                self.filepath,
                self.svg_path_coords,
                self.svg_path_dist,
                calc.map_view_box(self.raw_coords, 20),
                self.sector_index
            )
            # Reset data
            self.validating = False
            self.recording = False
            self._map_exist = True
            #logger.info("map saved, stopped map recording")
        elif 8 < laptime_curr < 10:  # switch off validating after 8s
            self.validating = False

    def __record(self, sector_idx, pos_curr, gps_curr, elv_curr):
        """Recording only from beginning of a lap"""
        # Sector index
        if self.last_sector_idx != sector_idx:
            if sector_idx == 1:
                self.sector_index[0] = len(self.coords_list_curr) - 1
            elif sector_idx == 2:
                self.sector_index[1] = len(self.coords_list_curr) - 1
            self.last_sector_idx = sector_idx
        # Update if position value is different & positive
        if 0 <= pos_curr != self.pos_last:
            if pos_curr > self.pos_last:  # position further
                self.coords_list_curr.append(gps_curr)
                self.dist_list_curr.append((pos_curr, elv_curr))
            self.pos_last = pos_curr  # reset last position

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


def load_svg(filename, pathname):
    """Load svg file"""
    try:
        dom = xml.dom.minidom.parse(f"{pathname}{filename}.svg")
        desc_col = dom.documentElement.getElementsByTagName("desc")
        path_col = dom.documentElement.getElementsByTagName("polyline")
        sector_index = fmt.string_pair_to_int(desc_col[0].childNodes[0].nodeValue)

        for tags in path_col:
            if tags.getAttribute("id") == "map":
                svg_path_coords = tags.getAttribute("points")
                continue
            if tags.getAttribute("id") == "dist":
                svg_path_dist = tags.getAttribute("points")
                continue

        return svg_path_coords, svg_path_dist, sector_index
    except (FileNotFoundError, IndexError, xml.parsers.expat.ExpatError):
        logger.info("no valid map data file found")
        return None, None, [0,0]


def save_svg(filename, pathname, svg_path_coords, svg_path_dist, view_box, sector_index):
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
    map_node.setAttribute("points", svg_path_coords)
    root_node.appendChild(map_node)

    # Create distance
    dist_comment = new_svg.createComment(" Raw distance reference points ")
    root_node.appendChild(dist_comment)

    dist_node = new_svg.createElement("polyline")
    dist_node.setAttribute("id", "dist")
    dist_node.setAttribute("fill", "none")
    dist_node.setAttribute("stroke", "none")
    dist_node.setAttribute("stroke-width", "0")
    dist_node.setAttribute("points", svg_path_dist)
    root_node.appendChild(dist_node)

    # Save svg
    with open(f"{pathname}{filename}.svg", "w", encoding="utf-8") as svgfile:
        new_svg.writexml(svgfile, indent="", addindent="\t", newl="\n", encoding="utf-8")
