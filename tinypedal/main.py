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
Launcher
"""

import os
import sys
import io
import logging
import psutil

from PySide2.QtGui import QIcon, QFont, QPixmapCache
from PySide2.QtWidgets import QApplication, QMessageBox

from .cli_argument import get_cli_argument
from .const_app import (
    APP_NAME,
    PLATFORM,
    VERSION,
    EXE_FILE,
    PID_FILE,
    PATH_GLOBAL,
    PYTHON_VERSION,
    QT_VERSION,
    PSUTIL_VERSION,
)
from .const_file import ImageFile
from .log_handler import set_logging_level

logger = logging.getLogger("tinypedal")
log_stream = io.StringIO()


def save_pid_file():
    """Save PID info to file"""
    with open(f"{PATH_GLOBAL}{PID_FILE}", "w", encoding="utf-8") as f:
        current_pid = os.getpid()
        pid_create_time = psutil.Process(current_pid).create_time()
        pid_str = f"{current_pid},{pid_create_time}"
        f.write(pid_str)


def is_pid_exist() -> bool:
    """Check and verify PID existence"""
    try:
        # Load last recorded PID and creation time from pid log file
        with open(f"{PATH_GLOBAL}{PID_FILE}", "r", encoding="utf-8") as f:
            pid_read = f.readline()
        pid = pid_read.split(",")
        pid_last = int(pid[0])
        pid_last_create_time = pid[1]
        # Verify if last PID is running and belongs to TinyPedal
        if psutil.pid_exists(pid_last):
            if str(psutil.Process(pid_last).create_time()) == pid_last_create_time:
                return True  # already running
    except (ProcessLookupError, psutil.NoSuchProcess, ValueError, IndexError, FileNotFoundError):
        logger.info("PID not found or invalid")
    return False  # no running


def is_exe_running() -> bool:
    """Check running executable (windows only), this is only used as fallback"""
    # Skip exe check if not on windows system
    if PLATFORM != "Windows":
        return False
    app_pid = os.getpid()
    for app in psutil.process_iter(["name", "pid"]):
        # Compare found APP name & pid
        if app.info["name"] == EXE_FILE and app.info["pid"] != app_pid:
            return True
    return False


def single_instance_check(is_single_instance: bool):
    """Single instance check"""
    # Check if single instance mode enabled
    if not is_single_instance:
        logger.info("Single instance mode: OFF")
        return None
    logger.info("Single instance mode: ON")
    # Check existing PID file first, then exe PID
    if not (is_pid_exist() or is_exe_running()):
        save_pid_file()
        return None
    # Show warning to console and popup dialog
    warning_text = (
        "TinyPedal is already running.\n\n"
        "Only one TinyPedal may be run at a time.\n"
        "Check system tray for hidden icon."
    )
    logger.warning(warning_text)
    QMessageBox.warning(None, f"{APP_NAME} v{VERSION}", warning_text)
    sys.exit()


def version_check():
    """Check version"""
    logger.info("TinyPedal %s", VERSION)
    logger.info("Python %s", PYTHON_VERSION)
    logger.info("Qt %s", QT_VERSION)
    logger.info("psutil %s", PSUTIL_VERSION)


def init_gui() -> QApplication:
    """Initialize Qt Gui"""
    root = QApplication(sys.argv)
    root.setApplicationName(APP_NAME)
    root.setWindowIcon(QIcon(ImageFile.APP_ICON))
    root.setQuitOnLastWindowClosed(False)
    font = QFont("sans-serif", 10)
    font.setStyleHint(QFont.SansSerif)
    root.setFont(font)
    root.setStyle("Fusion")
    QPixmapCache.setCacheLimit(0)  # disable global cache
    return root


def start_app():
    """Init main window"""
    cli_args = get_cli_argument()
    set_logging_level(logger, log_stream, cli_args.log_level)
    # Main GUI
    root = init_gui()
    single_instance_check(cli_args.single_instance)
    version_check()
    # Load core modules
    from . import loader
    loader.start()
    # Start mainloop
    sys.exit(root.exec_())
