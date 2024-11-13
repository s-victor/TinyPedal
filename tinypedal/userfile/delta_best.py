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
Delta best file function
"""

import logging
import csv

from .. import validator as val

logger = logging.getLogger(__name__)


def load_delta_best_file(filepath:str, filename: str, defaults: tuple, extension: str = ".csv"):
    """Load delta best file (*.csv)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
            temp_list_size = len(temp_list)
            # Validate data
            bestlist = val.delta_list(temp_list)
            laptime_best = bestlist[-1][1]
            # Save data if modified
            if temp_list_size != len(bestlist):
                save_delta_best_file(
                    filepath=filepath,
                    filename=filename,
                    dataset=bestlist,
                    extension=extension,
                )
        return bestlist, laptime_best
    except (FileNotFoundError, IndexError, ValueError, TypeError):
        logger.info("MISSING: deltabest data")
        return defaults


def save_delta_best_file(filepath: str, filename: str, dataset: list, extension: str = ".csv"):
    """Save delta best file (*.csv)"""
    if len(dataset) < 10:
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        deltawrite = csv.writer(csvfile)
        deltawrite.writerows(dataset)
