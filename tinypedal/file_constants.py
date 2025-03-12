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
File constants
"""


def qfile_filter(extension: str, description: str) -> str:
    """File format filter for QFile dialog

    Returns:
        "File description (*.extension)"
    """
    return f"{description} (*{extension})"


class FileExtension:
    """File Extension constants"""

    __slots__ = ()
    # Common
    ALL = ".*"
    LOG = ".log"
    CSV = ".csv"
    TXT = ".txt"
    INI = ".ini"
    BAK = ".bak"
    JSON = ".json"
    # Image
    SVG = ".svg"
    PNG = ".png"
    # Specific
    CONSUMPTION = ".consumption"
    ENERGY = ".energy"
    FUEL = ".fuel"
    SECTOR = ".sector"
    TPPN = ".tppn"
    TPTN = ".tptn"
    STATS = ".stats"


FILE_EXT = FileExtension()


class FileFilter:
    """File filter constants (for used in QFileDialog)"""

    __slots__ = ()
    # Common
    ALL = qfile_filter(FILE_EXT.ALL, "All files")
    LOG = qfile_filter(FILE_EXT.LOG, "LOG file")
    TXT = qfile_filter(FILE_EXT.TXT, "Text file")
    CSV = qfile_filter(FILE_EXT.CSV, "CSV file")
    INI = qfile_filter(FILE_EXT.INI, "INI file")
    JSON = qfile_filter(FILE_EXT.JSON, "JSON file")
    # Image
    SVG = qfile_filter(FILE_EXT.SVG, "SVG image")
    PNG = qfile_filter(FILE_EXT.PNG, "PNG image")
    # Specific
    CONSUMPTION = qfile_filter(FILE_EXT.CONSUMPTION, "Consumption History")
    TPPN = qfile_filter(FILE_EXT.TPPN, "TinyPedal Pace Notes")
    TPTN = qfile_filter(FILE_EXT.TPTN, "TinyPedal Track Notes")
    GPLINI = qfile_filter(FILE_EXT.INI, "GPL Pace Notes")


QFILTER = FileFilter()
