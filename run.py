#!/usr/bin/env python3

#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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
Run program
"""

import os
import sys


def override_pyside_version(version: int = 6):
    """Override PySide version 2 to 6"""
    if version != 6:
        return
    original = "PySide2"
    override = f"PySide{version}"
    override_module(original, override)
    override_module(f"{original}.QtCore", f"{override}.QtCore")
    override_module(f"{original}.QtGui", f"{override}.QtGui")
    override_module(f"{original}.QtWidgets", f"{override}.QtWidgets")
    override_module(f"{original}.QtMultimedia", f"{override}.QtMultimedia")


def override_module(original: str, override: str):
    """Manual import & override module"""
    sys.modules[original] = __import__(override, fromlist=[override])


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))

    # Load command line arguments
    from tinypedal.cli_argument import get_cli_argument

    cli_args = get_cli_argument()

    # Check whether to override PySide version
    pyside_override = getattr(cli_args, "pyside", 2)
    os.environ["PYSIDE_OVERRIDE"] = f"{pyside_override}"  # store to env
    override_pyside_version(pyside_override)

    # Start
    from tinypedal.main import start_app

    start_app(cli_args)
