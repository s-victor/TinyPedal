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
import re
import xml.dom.minidom

from ..const import PATH_TRACKMAP
from ..readapi import info, chknm, cs2py, state
from .. import calculation as calc
from .. import validator as val

MODULE_NAME = "module_mapping"

logger = logging.getLogger(__name__)


class Realtime:
    """Mapping data"""
    module_name = MODULE_NAME
    filepath = PATH_TRACKMAP

    def __init__(self, mctrl, config):
        self.mctrl = mctrl
        self.cfg = config
        self.mcfg = self.cfg.setting_user[self.module_name]
        self.stopped = True
        self.running = False
        self.set_default()

    def set_default(self):
        """Set default output"""
        self.map_coordinates = None
        self.map_distance = None
        self.map_sectors = None

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
        recording = False  # set recording state
        verified = False  # additional check for conserving resources
        validating = False  # validate after cross finish line
        map_exist = False

        sector_index = [0,0]
        coords_list_curr = []  # coordinates list, current lap
        coords_list_last = []  # coordinates list, last lap, used for verification only
        dist_list_curr = []  # distance list, current lap
        dist_list_last = []  # distance list, last lap, used for verification only
        pos_last = 0  # last checked player vehicle position
        last_lap_stime = 0  # last lap start time
        last_lap_etime = 0  # last elapsed time
        last_sector_idx = -1

        raw_coords = None
        raw_dists = None
        map_file = None
        svg_path_coords = None
        svg_path_dist = None

        active_interval = self.mcfg["update_interval"] / 1000
        idle_interval = self.mcfg["idle_update_interval"] / 1000
        update_interval = idle_interval

        while self.running:
            if state():

                if not map_exist:
                    (sector_idx, lap_stime, lap_etime, lastlap_check,
                     pos_curr, gps_curr, elv_curr) = self.__telemetry()

                    # Load & verify track map data
                    if not verified:
                        update_interval = active_interval  # shorter delay
                        verified = True
                        last_lap_stime = lap_stime  # reset lap-start-time
                        last_sector_idx = -1

                        map_file = val.format_invalid_char(
                            cs2py(info.LastScor.mScoringInfo.mTrackName))
                        # Load map file
                        (svg_path_coords, svg_path_dist, sector_index
                         ) = load_svg(map_file, self.filepath)
                        if svg_path_coords:
                            #logger.info("map exist")
                            raw_coords = points_to_coords(svg_path_coords)
                            raw_dists = points_to_coords(svg_path_dist)
                            self.update_output_data(raw_coords, raw_dists, sector_index)
                            map_exist = True
                            update_interval = idle_interval
                            continue
                        else:
                            #logger.info("map not exist")
                            map_exist = False
                            self.update_output_data(None, None, None)

                    laptime_curr = max(lap_etime - last_lap_stime, 0)

                    # Lap start & finish detection
                    if lap_stime > last_lap_stime:  # difference of lap-start-time
                        # End last lap recording
                        if coords_list_curr:
                            if calc.distance_xy(coords_list_curr[0], gps_curr) > 500:
                                coords_list_curr.append(gps_curr)
                                dist_list_curr.append((pos_curr, elv_curr))
                            coords_list_last = coords_list_curr
                            dist_list_last = dist_list_curr
                            validating = True

                        # Reset data
                        coords_list_curr = []
                        dist_list_curr = []
                        last_lap_stime = lap_stime
                        pos_last = 0
                        last_lap_etime = 0

                        # Activate recording
                        recording = True
                        #logger.info("map recording")

                    if validating:
                        if 1 < laptime_curr <= 8 and lastlap_check > 0:
                            # Store & convert raw coordinates to svg points data
                            raw_coords = coords_list_last
                            raw_dists = dist_list_last
                            svg_path_coords = coords_to_points(raw_coords)
                            svg_path_dist = coords_to_points(raw_dists)

                            # Save to svg file
                            view_box = self.scale_map(raw_coords, False)
                            save_svg(
                                map_file, self.filepath,
                                svg_path_coords, svg_path_dist,
                                view_box, sector_index
                            )

                            # Reset data
                            validating = False
                            recording = False
                            self.update_output_data(raw_coords, raw_dists, sector_index)
                            map_exist = True
                            update_interval = idle_interval
                            continue
                            #logger.info("map saved, stopped map recording")
                        elif 8 < laptime_curr < 10:  # switch off validating after 8s
                            validating = False

                    # Recording only from the beginning of a lap
                    if recording:
                        # Sector index
                        if last_sector_idx != sector_idx:
                            if sector_idx == 1:
                                sector_index[0] = len(coords_list_curr) - 1
                            elif sector_idx == 2:
                                sector_index[1] = len(coords_list_curr) - 1
                            last_sector_idx = sector_idx

                        # Update position if current dist value is diff & positive
                        if pos_curr != pos_last and pos_curr >= 0:
                            # Record if position & time is further
                            if pos_curr > pos_last and lap_etime > last_lap_etime:
                                coords_list_curr.append(gps_curr)
                                dist_list_curr.append((pos_curr, elv_curr))

                            pos_last = pos_curr  # reset last position
                            last_lap_etime = lap_etime  # reset last elapsed time

            else:
                if verified:
                    recording = False
                    verified = False
                    validating = False
                    map_exist = False
                    update_interval = idle_interval  # longer delay while inactive
                    coords_list_curr = []
                    dist_list_curr = []

            time.sleep(update_interval)

        self.set_default()
        self.cfg.active_module_list.remove(self)
        self.stopped = True
        logger.info("mapping module closed")

    def update_output_data(self, raw_coords, raw_dists, sector_index):
        """Update output data"""
        self.map_coordinates = raw_coords
        self.map_distance = raw_dists
        self.map_sectors = sector_index

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

    @staticmethod
    def scale_map(map_data, area_size, margin=0):
        """Scale map data"""
        # Separate X & Y coordinates
        x_range, y_range = list(zip(*map_data))

        # Map size: x=width, y=height
        map_range = min(x_range), max(x_range), min(y_range), max(y_range)
        map_size = map_range[1] - map_range[0], map_range[3] - map_range[2]

        if area_size:
            # Display area / map_size
            map_scale = (area_size - margin * 2) / max(map_size[0], map_size[1])

            if map_size[0] > map_size[1]:
                map_offset = margin, (area_size - map_size[1] * map_scale) * 0.5
            else:
                map_offset = (area_size - map_size[0] * map_scale) * 0.5, margin

            x_range_scaled = [(x_pos - map_range[0]) * map_scale + map_offset[0]
                              for x_pos in x_range]
            y_range_scaled = [(y_pos - map_range[2]) * map_scale + map_offset[1]
                              for y_pos in y_range]

            # Output scaled map data
            return list(zip(x_range_scaled, y_range_scaled)), map_range, map_scale, map_offset

        # Output svg view box info
        return f"{map_range[0]-20} {map_range[2]-20} {map_size[0]+40} {map_size[1]+40}"


def load_svg(filename, pathname):
    """Load svg file"""
    try:
        dom = xml.dom.minidom.parse(f"{pathname}{filename}.svg")
        desc_col = dom.documentElement.getElementsByTagName("desc")
        path_col = dom.documentElement.getElementsByTagName("polyline")

        sector_index = string_pair_to_int(desc_col[0].childNodes[0].nodeValue)

        for tags in path_col:
            if tags.getAttribute("id") == "map":
                svg_path_coords = tags.getAttribute("points")
                continue
            if tags.getAttribute("id") == "dist":
                svg_path_dist = tags.getAttribute("points")
                continue

        return svg_path_coords, svg_path_dist, sector_index
    except (FileNotFoundError, IndexError, xml.parsers.expat.ExpatError):
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


def string_pair_to_int(string):
    """Convert string "x,y" to int"""
    value = re.split(",", string)
    return int(value[0]), int(value[1])


def string_pair_to_float(string):
    """Convert string "x,y" to float"""
    value = re.split(",", string)
    return float(value[0]), float(value[1])


def points_to_coords(points):
    """Convert svg points to raw coordinates"""
    string = re.split(" ", points)
    return list(map(string_pair_to_float, string))


def coords_to_points(coords):
    """Convert raw coordinates (x,y),(x,y) to svg points x,y x,y"""
    output = ""
    for data in coords:
        if output:
            output += " "
        output += f"{data[0]},{data[1]}"
    return output
