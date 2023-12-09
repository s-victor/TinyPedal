#!/usr/bin/env python3

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
Run program
"""

import os
import sys
import signal
import logging
import psutil

from PySide2.QtGui import QFont
from PySide2.QtWidgets import (
    QApplication,
    QMessageBox,
)
from tinypedal.const import APP_NAME, VERSION

logger = logging.getLogger("tinypedal")


def is_tinypedal_running(app_name: str) -> bool:
    """Check if is already running"""
    for app in psutil.process_iter(["name", "pid"]):
        # Compare found APP name & pid
        if app.info["name"] == app_name and app.info["pid"] != os.getpid():
            return True
    return False


def load_tinypedal():
    """Start tinypedal"""
    root = QApplication(sys.argv)
    root.setApplicationName(APP_NAME)
    font = QFont("sans-serif", 10)
    font.setStyleHint(QFont.SansSerif)
    root.setFont(font)
    root.setStyle('Fusion')

    if is_tinypedal_running("tinypedal.exe"):
        QMessageBox.warning(
            None,
            f"{APP_NAME} v{VERSION}",
            "TinyPedal is already running.\n\n"
            "Only one TinyPedal may be run at a time.\n"
            "Check system tray for hidden icon."
        )
    else:
        logger.info("starting tinypedal")
        # Start main window
        from tinypedal.main import AppWindow
        config_window = AppWindow()
        signal.signal(signal.SIGINT, config_window.int_signal_handler)
        # Start mainloop
        sys.exit(root.exec_())


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
    load_tinypedal()
