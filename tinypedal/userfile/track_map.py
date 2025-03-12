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
Track map file function
"""

import logging
import xml.dom.minidom
import xml.parsers.expat

from ..file_constants import FILE_EXT
from ..formatter import (
    coords_to_points,
    points_to_coords,
    string_pair_to_int,
)

logger = logging.getLogger(__name__)


def load_track_map_file(filepath: str, filename: str, extension: str = FILE_EXT.SVG):
    """Load svg track map file (*.svg)"""
    try:
        dom = xml.dom.minidom.parse(f"{filepath}{filename}{extension}")
        desc_col = dom.documentElement.getElementsByTagName("desc")
        path_col = dom.documentElement.getElementsByTagName("polyline")
        svg_coords = svg_dists = None

        for tags in path_col:
            if tags.getAttribute("id") == "map":
                svg_coords = tags.getAttribute("points")
                continue
            if tags.getAttribute("id") == "dist":
                svg_dists = tags.getAttribute("points")
                continue

        # Convert to coordinates list
        raw_coords = points_to_coords(svg_coords)
        raw_dists = points_to_coords(svg_dists)
        sector_index = string_pair_to_int(desc_col[0].childNodes[0].nodeValue)
        return raw_coords, raw_dists, sector_index
    except FileNotFoundError:
        logger.info("MISSING: track map (%s) data", extension)
    except (AttributeError, IndexError, ValueError, xml.parsers.expat.ExpatError):
        logger.info("MISSING: invalid track map (%s) data", extension)
    return None, None, None


def save_track_map_file(
    filepath: str, filename: str, view_box: str,
    raw_coords: tuple, raw_dists: tuple, sector_index: tuple,
    extension: str = FILE_EXT.SVG
) -> None:
    """Save track map file (*.svg)"""
    # Convert to svg coordinates
    svg_coords = coords_to_points(raw_coords)
    svg_dists = coords_to_points(raw_dists)

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
    with open(f"{filepath}{filename}{extension}", "w", encoding="utf-8") as svgfile:
        new_svg.writexml(svgfile, indent="", addindent="\t", newl="\n", encoding="utf-8")
        logger.info("USERDATA: %s%s saved", filename, extension)
