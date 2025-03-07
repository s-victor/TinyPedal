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
Fuel/Energy delta file function
"""

from __future__ import annotations
import logging
import csv

from ..module_info import ConsumptionDataSet
from ..formatter import qfile_filter
from .. import validator as val

QFILTER_CONSUMPTION = qfile_filter(".consumption", "Consumption History")

logger = logging.getLogger(__name__)


def load_fuel_delta_file(
    filepath: str, filename: str, extension: str, defaults: tuple
) -> tuple[tuple, float, float]:
    """Load fuel/energy delta file (*.fuel, *.energy)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            temp_list = list(csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC))
        # Validate data
        temp_list_size = len(temp_list)
        lastlist = tuple(val.delta_list(temp_list))
        used_last = lastlist[-1][1]
        laptime_last = lastlist[-1][2]
        # Save data if modified
        if temp_list_size != len(lastlist):
            save_fuel_delta_file(
                filepath=filepath,
                filename=filename,
                extension=extension,
                dataset=lastlist,
            )
        return lastlist, used_last, laptime_last
    except FileNotFoundError:
        logger.info("MISSING: consumption delta (%s) data", extension)
    except (IndexError, ValueError, TypeError):
        logger.info("MISSING: invalid consumption delta (%s) data", extension)
    return defaults


def save_fuel_delta_file(
    filepath: str, filename: str, extension: str, dataset: tuple
) -> None:
    """Save fuel/energy delta file (*.fuel, *.energy)"""
    if len(dataset) < 10:
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        data_writer = csv.writer(csvfile)
        data_writer.writerows(dataset)
        logger.info("USERDATA: %s%s saved", filename, extension)


def load_consumption_history_file(
    filepath: str, filename: str, extension: str = ".consumption"
) -> tuple[ConsumptionDataSet, ...]:
    """Load fuel/energy consumption history file (*.consumption)"""
    try:
        with open(f"{filepath}{filename}{extension}", newline="", encoding="utf-8") as csvfile:
            data_reader = csv.DictReader(csvfile, restval="", restkey="unknown")
            default_data = ConsumptionDataSet._field_defaults
            dataset = tuple(
                ConsumptionDataSet(**val.dict_value_type(data, default_data))
                for data in data_reader
            )
        return dataset
    except FileNotFoundError:
        logger.info("MISSING: consumption history (%s) data", extension)
    except (IndexError, KeyError, ValueError, TypeError):
        logger.info("MISSING: invalid consumption history (%s) data", extension)
    return (ConsumptionDataSet(),)


def save_consumption_history_file(
    dataset: tuple, filepath: str, filename: str, extension: str = ".consumption"
) -> None:
    """Save fuel/energy consumption history file (*.consumption)"""
    if len(dataset) < 2:
        return
    with open(f"{filepath}{filename}{extension}", "w", newline="", encoding="utf-8") as csvfile:
        data_writer = csv.writer(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        data_writer.writerow(ConsumptionDataSet._fields)  # write field name as column header
        data_writer.writerows(dataset)
        logger.info("USERDATA: %s%s saved", filename, extension)
