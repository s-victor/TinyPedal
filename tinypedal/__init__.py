#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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
Init
"""
import sys
import logging

logger = logging.getLogger("tinypedal")

log_format = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S")
cli_handler = logging.StreamHandler(sys.stdout)

#logger.setLevel(logging.NOTSET)
logger.setLevel(logging.INFO)
logger.addHandler(cli_handler)

cli_handler.setLevel(logging.INFO)
cli_handler.setFormatter(log_format)
