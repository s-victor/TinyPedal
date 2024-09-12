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
Launcher
"""

import os
import sys
import signal
import logging
import psutil
import threading

from PySide2.QtGui import QFont
from PySide2.QtWidgets import QApplication, QMessageBox

from . import log_stream
from .cli_argument import get_cli_argument
from .const import APP_NAME, PLATFORM, VERSION, PYTHON_VERSION, QT_VERSION, PATH_LOG
from .log_handler import set_logging_level

EXE_NAME = "tinypedal.exe"
PID_FILE = "pid.log"

cli_args = get_cli_argument()
logger = logging.getLogger("tinypedal")
set_logging_level(logger, log_stream, cli_args.log_level)


def save_pid_file():
    """Save PID info to file"""
    with open(f"{PATH_LOG}{PID_FILE}", "w", encoding="utf-8") as f:
        current_pid = os.getpid()
        pid_create_time = psutil.Process(current_pid).create_time()
        pid_str = f"{current_pid},{pid_create_time}"
        f.write(pid_str)


def is_pid_exist() -> bool:
    """Check and verify PID existence"""
    try:
        # Load last recorded PID and creation time from pid log file
        with open(f"{PATH_LOG}{PID_FILE}", "r", encoding="utf-8") as f:
            pid_read = f.readline()
        pid = pid_read.split(",")
        pid_last = int(pid[0])
        pid_last_create_time = pid[1]
        # Verify if last PID is running and belongs to TinyPedal
        if psutil.pid_exists(pid_last):
            if str(psutil.Process(pid_last).create_time()) == pid_last_create_time:
                return True  # already running
    except (ValueError, IndexError, FileNotFoundError):
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
        if app.info["name"] == EXE_NAME and app.info["pid"] != app_pid:
            return True
    return False


def single_instance_check():
    """Single instance check"""
    # Check if single instance mode enabled
    if not cli_args.single_instance:
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


def init_gui():
    """Initialize Qt Gui"""
    root = QApplication(sys.argv)
    root.setApplicationName(APP_NAME)
    root.setQuitOnLastWindowClosed(False)
    font = QFont("sans-serif", 10)
    font.setStyleHint(QFont.SansSerif)
    root.setFont(font)
    root.setStyle("Fusion")
    return root


def start_app():
    """Init main window"""
    root = init_gui()
    single_instance_check()
    version_check()

    # Load core modules
    from . import loader
    loader.load()

    # Start main window
    from tinypedal.ui.app import AppWindow
    config_window = AppWindow()
    signal.signal(signal.SIGINT, config_window.int_signal_handler)

    # start monitoring game launch
    # Create a thread to run the monitoring function in the background
    from .monitoring import monitor_process
    monitor_thread = threading.Thread(target=monitor_process, 
                                      args=(config_window,),
                                      daemon=True)
    monitor_thread.start()
    
    # Start mainloop
    sys.exit(root.exec_())
