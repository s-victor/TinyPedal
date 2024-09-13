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
Main application window
"""

import logging

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QAction,
    QTabWidget,
    QVBoxLayout,
    QPushButton,
)

from ..const import APP_NAME, VERSION, APP_ICON
from ..setting import cfg
from ..api_control import api
from ..overlay_control import octrl
from ..module_control import mctrl, wctrl
from .. import loader
from .tray_icon import TrayIcon
from .module_view import ModuleList
from .spectate_view import SpectateList
from .preset_view import PresetList
from .menu import OverlayMenu, ConfigMenu, ToolsMenu, WindowMenu, HelpMenu


WINDOW_MIN_WIDTH = 300
WINDOW_MIN_HEIGHT = 462

logger = logging.getLogger("tinypedal")


class AppWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setWindowIcon(QIcon(APP_ICON))

        # Menu bar
        self.main_menubar()

        # Status bar & notification
        label_api = QLabel("API:")
        self.button_api = QPushButton("")
        self.button_api.clicked.connect(self.config_menuitem.open_config_sharedmemory)
        self.button_api.clicked.connect(self.set_status_text)
        self.statusBar().insertPermanentWidget(0, label_api)
        self.statusBar().insertPermanentWidget(1, self.button_api)
        self.set_status_text()

        self.notify_spectate = QPushButton("Spectate Mode Enabled")
        self.notify_spectate.clicked.connect(self.goto_spectate_tab)
        self.notify_spectate.setStyleSheet(
            "font-weight: bold;color: #fff;background: #09C;padding: 4px;border-radius: 0;"
        )

        # Controller tabs
        self.tab_bar = QTabWidget()
        self.widget_tab = ModuleList(wctrl)
        self.module_tab = ModuleList(mctrl)
        self.preset_tab = PresetList(self)
        self.spectate_tab = SpectateList(self)
        self.tab_bar.addTab(self.widget_tab, "Widget")
        self.tab_bar.addTab(self.module_tab, "Module")
        self.tab_bar.addTab(self.preset_tab, "Preset")
        self.tab_bar.addTab(self.spectate_tab, "Spectate")

        # Main view
        main_view = QWidget()
        layout = QVBoxLayout(main_view)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)
        layout.addWidget(self.tab_bar)
        layout.addWidget(self.notify_spectate)
        self.setCentralWidget(main_view)

        # Tray icon & window state
        self.start_tray_icon()
        self.set_window_state()
        self.__connect_signal()
        cfg.app_loaded = True

    def goto_spectate_tab(self):
        """Go to spectate tab"""
        self.tab_bar.setCurrentWidget(self.spectate_tab)

    def main_menubar(self):
        """Create menu bar"""
        logger.info("GUI: loading main menu")
        menu = self.menuBar()

        # Overlay menu
        menu_overlay = menu.addMenu("Overlay")
        OverlayMenu(self, menu_overlay)
        menu_overlay.addSeparator()

        app_quit = QAction("Quit", self)
        app_quit.triggered.connect(self.quit_app)
        menu_overlay.addAction(app_quit)

        # Config menu
        menu_config = menu.addMenu("Config")
        self.config_menuitem = ConfigMenu(self, menu_config)

        # Tools menu
        menu_tools = menu.addMenu("Tools")
        ToolsMenu(self, menu_tools)

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
            if cfg.compatibility["enable_window_position_correction"]:
                self.verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()
        logger.info("GUI: loading finished")

    def load_window_position(self):
        """Load window position"""
        logger.info("GUI: loading window position")
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
            logger.info("GUI: window position corrected")

    def save_window_position(self):
        """Save window position"""
        if cfg.application["remember_position"]:
            last_pos = cfg.application["position_x"], cfg.application["position_y"]
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                cfg.application["position_x"] = self.x()
                cfg.application["position_y"] = self.y()
                cfg.save(0)

    def set_status_text(self):
        """Set status text"""
        self.button_api.setText(f"{api.name} - {api.version}")

    def quit_app(self):
        """Quit manager"""
        self.save_window_position()
        self.__break_signal()
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

    @Slot(bool)
    def reload_preset(self):
        """Reload current preset"""
        loader.reload()
        self.set_status_text()
        # Refresh menu & preset list
        self.preset_tab.refresh_list()
        self.widget_tab.refresh_state()
        self.module_tab.refresh_state()
        self.spectate_tab.refresh_list()

    def __connect_signal(self):
        """Connect overlay reload signal"""
        octrl.state.reload.connect(self.reload_preset)

    def __break_signal(self):
        """Disconnect overlay reload signal"""
        octrl.state.reload.disconnect(self.reload_preset)
