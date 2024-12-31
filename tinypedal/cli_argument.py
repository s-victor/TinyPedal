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
Command line argument
"""

import argparse


def get_cli_argument() -> argparse.Namespace:
    """Get command line argument"""
    parse = argparse.ArgumentParser(description="TinyPedal command line arguments")
    parse.add_argument(
        "-l",
        "--log-level",
        choices=range(3),
        default=1,
        type=int,
        help="set logging output level: 0 - warning and error only; 1 - all levels (default); 2 - output to file",
    )
    parse.add_argument(
        "-s",
        "--single-instance",
        choices=range(2),
        default=1,
        type=int,
        help="set running mode: 0 - allow running multiple instances; 1 - single instance (default)",
    )
    return parse.parse_args()
