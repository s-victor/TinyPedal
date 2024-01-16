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
Main application window
"""

import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QAction,
    QTabWidget,
)

from ..const import APP_NAME, VERSION, APP_ICON
from ..setting import cfg
from ..api_control import api
from ..module_control import mctrl
from ..widget_control import wctrl
from .. import loader
from .tray_icon import TrayIcon
from .module_view import ModuleList
from .spectate_view import SpectateList
from .preset_view import PresetList
from .menu import OverlayMenu, ConfigMenu, WindowMenu, HelpMenu


WINDOW_MIN_WIDTH = 300
WINDOW_MIN_HEIGHT = 450

logger = logging.getLogger("tinypedal")


class AppWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setWindowIcon(QIcon(APP_ICON))

        # Create menu
        self.main_menubar()

        # Add status bar
        self.label_api_version = QLabel("")
        self.statusBar().addPermanentWidget(self.label_api_version)
        self.set_status_text()

        # Create tabs
        main_tab = QTabWidget()
        self.widget_tab = ModuleList(wctrl, cfg.active_widget_list, "widget")
        self.module_tab = ModuleList(mctrl, cfg.active_module_list, "module")
        self.preset_tab = PresetList(self)
        self.spectate_tab = SpectateList(self)
        main_tab.addTab(self.widget_tab, "Widget")
        main_tab.addTab(self.module_tab, "Module")
        main_tab.addTab(self.preset_tab, "Preset")
        main_tab.addTab(self.spectate_tab, "Spectate")
        self.setCentralWidget(main_tab)

        self.start_tray_icon()
        self.set_window_state()

    def main_menubar(self):
        """Create menu bar"""
        logger.info("GUI: loading menu")
        menu = self.menuBar()

        # Overlay menu
        menu_overlay = menu.addMenu("Overlay")
        self.overlay_menu = OverlayMenu
        self.overlay_menu(self, menu_overlay)
        menu_overlay.addSeparator()

        app_quit = QAction("Quit", self)
        app_quit.triggered.connect(self.quit_app)
        menu_overlay.addAction(app_quit)

        # Config menu
        menu_config = menu.addMenu("Config")
        ConfigMenu(self, menu_config)

        # Window menu
        menu_window = menu.addMenu("Window")
        WindowMenu(self, menu_window)

        # Help menu
        menu_help = menu.addMenu("Help")
        HelpMenu(self, menu_help)

    def start_tray_icon(self):
        """Start tray icon (for Windows)"""
        logger.info("GUI: loading tray icon")
        self.tray_icon = TrayIcon(self, cfg)
        self.tray_icon.show()

    def set_window_state(self):
        """Set initial window state"""
        self.setMinimumWidth(WINDOW_MIN_WIDTH)
        self.setMinimumHeight(WINDOW_MIN_HEIGHT)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # disable maximize

        if cfg.application["remember_position"]:
            self.load_window_position()
            self.verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()
        logger.info("GUI: loaded")

    def load_window_position(self):
        """Load window position"""
        logger.info("GUI: loading last window position")
        # Get position from preset
        app_pos_x = cfg.application["position_x"]
        app_pos_y = cfg.application["position_y"]
        # Check whether x,y position at 0,0 (new preset value)
        # Ignore moving if at 0,0
        if 0 == app_pos_x == app_pos_y:
            self.save_window_position()
        else:
            self.move(app_pos_x, app_pos_y)

    def verify_window_position(self):
        """Verify window position"""
        # Get screen size from the screen where app window located
        screen_geo = self.screen().geometry()
        # Limiting position value if out of screen range
        app_pos_x = min(
            max(self.x(), screen_geo.left()),
            screen_geo.right() - WINDOW_MIN_WIDTH)
        app_pos_y = min(
            max(self.y(), screen_geo.top()),
            screen_geo.bottom() - WINDOW_MIN_HEIGHT)
        # Re-adjust position only if mismatched
        if self.x() != app_pos_x or self.y() != app_pos_y:
            self.move(app_pos_x, app_pos_y)
            logger.info("GUI: auto corrected window position")

    def save_window_position(self):
        """Save window position"""
        if cfg.application["remember_position"]:
            cfg.application["position_x"] = self.x()
            cfg.application["position_y"] = self.y()
            cfg.save(0)

    def set_status_text(self):
        """Set status text"""
        self.label_api_version.setText(f"API: {api.name} - {api.version}")

    def quit_app(self):
        """Quit manager"""
        self.save_window_position()
        loader.unload()
        QApplication.quit()  # close app

    def int_signal_handler(self, sign, frame):
        """Quit by keyboard interrupt"""
        self.quit_app()

    def closeEvent(self, event):
        """Minimize to tray"""
        if cfg.application["minimize_to_tray"]:
            event.ignore()
            self.hide()
        else:
            self.quit_app()

    def restart_api(self):
        """Restart shared memory api"""
        api.restart()
        self.set_status_text()

    def reload_preset(self):
        """Reload current preset"""
        loader.reload()
        self.set_status_text()
        # Refresh menu & preset list
        self.preset_tab.refresh_list()
        self.widget_tab.refresh_list()
        self.module_tab.refresh_list()
        self.spectate_tab.refresh_list()
