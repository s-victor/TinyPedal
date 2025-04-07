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
Main application window
"""

import logging

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .. import loader
from ..api_control import api
from ..const_app import APP_NAME, VERSION
from ..module_control import mctrl, wctrl
from ..overlay_control import octrl
from ..setting import ConfigType, cfg
from .menu import ConfigMenu, HelpMenu, OverlayMenu, ToolsMenu, WindowMenu
from .module_view import ModuleList
from .pace_notes_view import PaceNotesControl
from .preset_view import PresetList
from .spectate_view import SpectateList
from .tray_icon import TrayIcon

logger = logging.getLogger(__name__)


class AppWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")

        # Status bar & notification
        self.button_api = QPushButton()
        self.button_api.clicked.connect(self.set_status_text)
        self.statusBar().addPermanentWidget(QLabel("API:"))
        self.statusBar().addPermanentWidget(self.button_api)
        self.set_status_text()

        # Menu bar
        self.main_menubar()

        # Notify bar
        self.notify_spectate = QPushButton("Spectate Mode Enabled")
        self.notify_spectate.clicked.connect(self.goto_spectate_tab)
        self.notify_spectate.setStyleSheet(
            "font-weight: bold;color: #fff;background: #09C;padding: 4px;border-radius: 0;"
        )
        self.notify_pacenotes = QPushButton("Pace Notes Playback Enabled")
        self.notify_pacenotes.clicked.connect(self.goto_pacenotes_tab)
        self.notify_pacenotes.setStyleSheet(
            "font-weight: bold;color: #fff;background: #290;padding: 4px;border-radius: 0;"
        )
        layout_notify = QVBoxLayout()
        layout_notify.addWidget(self.notify_spectate)
        layout_notify.addWidget(self.notify_pacenotes)

        # Controller tabs
        self.tab_bar = QTabWidget(self)
        self.widget_tab = ModuleList(self, wctrl)
        self.module_tab = ModuleList(self, mctrl)
        self.preset_tab = PresetList(self)
        self.spectate_tab = SpectateList(self)
        self.pacenotes_tab = PaceNotesControl(self)
        self.tab_bar.addTab(self.widget_tab, "Widget")
        self.tab_bar.addTab(self.module_tab, "Module")
        self.tab_bar.addTab(self.preset_tab, "Preset")
        self.tab_bar.addTab(self.spectate_tab, "Spectate")
        self.tab_bar.addTab(self.pacenotes_tab, "Pace Notes")

        # Main view
        main_view = QWidget(self)
        layout = QVBoxLayout(main_view)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.tab_bar)
        layout.addLayout(layout_notify)
        self.setCentralWidget(main_view)

        # Tray icon & window state
        self.start_tray_icon()
        self.set_window_state()
        self.__connect_signal()

    def goto_spectate_tab(self):
        """Go to spectate tab"""
        self.tab_bar.setCurrentWidget(self.spectate_tab)

    def goto_pacenotes_tab(self):
        """Go to pacenotes tab"""
        self.tab_bar.setCurrentWidget(self.pacenotes_tab)

    def main_menubar(self):
        """Create menu bar"""
        logger.info("GUI: loading main menu")
        menu = self.menuBar()

        # Overlay menu
        menu_overlay = OverlayMenu("Overlay", self)
        menu.addMenu(menu_overlay)

        # Config menu
        menu_config = ConfigMenu("Config", self)
        menu.addMenu(menu_config)
        self.button_api.clicked.connect(menu_config.open_config_sharedmemory)

        # Tools menu
        menu_tools = ToolsMenu("Tools", self)
        menu.addMenu(menu_tools)

        # Window menu
        menu_window = WindowMenu("Window", self)
        menu.addMenu(menu_window)

        # Help menu
        menu_help = HelpMenu("Help", self)
        menu.addMenu(menu_help)

    def start_tray_icon(self):
        """Start tray icon (for Windows)"""
        logger.info("GUI: loading tray icon")
        self.tray_icon = TrayIcon(self)
        self.tray_icon.show()

    def set_window_state(self):
        """Set initial window state"""
        self.setMinimumWidth(300)
        self.setMinimumHeight(462)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # disable maximize

        if cfg.application["remember_size"]:
            self.resize(
                cfg.application["window_width"],
                cfg.application["window_height"],
            )

        if cfg.application["remember_position"]:
            self.load_window_position()

        if cfg.compatibility["enable_window_position_correction"]:
            self.verify_window_position()

        if cfg.application["show_at_startup"]:
            self.showNormal()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def load_window_position(self):
        """Load window position"""
        logger.info("GUI: loading window setting")
        # Get position from preset
        app_pos_x = cfg.application["position_x"]
        app_pos_y = cfg.application["position_y"]
        # Check whether x,y position at 0,0 (new preset value)
        # Ignore moving if at 0,0
        if 0 == app_pos_x == app_pos_y:
            self.save_window_state()
        else:
            self.move(app_pos_x, app_pos_y)

    def verify_window_position(self):
        """Verify window position"""
        # Get screen size from the screen where app window located
        screen_geo = self.screen().geometry()
        # Limiting position value if out of screen range
        app_pos_x = min(
            max(self.x(), screen_geo.left()),
            screen_geo.right() - self.minimumWidth(),
        )
        app_pos_y = min(
            max(self.y(), screen_geo.top()),
            screen_geo.bottom() - self.minimumHeight(),
        )
        # Re-adjust position only if mismatched
        if self.x() != app_pos_x or self.y() != app_pos_y:
            self.move(app_pos_x, app_pos_y)
            logger.info("GUI: window position corrected")

    def save_window_state(self):
        """Save window state"""
        save_changes = False

        if cfg.application["remember_position"]:
            last_pos = cfg.application["position_x"], cfg.application["position_y"]
            new_pos = self.x(), self.y()
            if last_pos != new_pos:
                cfg.application["position_x"] = new_pos[0]
                cfg.application["position_y"] = new_pos[1]
                save_changes = True

        if cfg.application["remember_size"]:
            last_size = cfg.application["window_width"], cfg.application["window_height"]
            new_size = self.width(), self.height()
            if last_size != new_size:
                cfg.application["window_width"] = new_size[0]
                cfg.application["window_height"] = new_size[1]
                save_changes = True

        if save_changes:
            cfg.save(0, cfg_type=ConfigType.CONFIG)

    def set_status_text(self):
        """Set status text"""
        if cfg.shared_memory_api["enable_active_state_override"]:
            text = f"{api.name} (state overriding)"
        else:
            text = f"{api.name} ({api.version})"
        self.button_api.setText(text)

    def show_app(self):
        """Show app window"""
        self.showNormal()
        self.activateWindow()

    def quit_app(self):
        """Quit manager"""
        self.save_window_state()
        self.__break_signal()
        loader.close()
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
        self.spectate_tab.refresh_list()

    @Slot(bool)
    def reload_preset(self):
        """Reload current preset"""
        loader.reload(reload_preset=True)
        self.refresh_states()

    def reload_only(self):
        """Reload only api, module, widget"""
        loader.reload(reload_preset=False)
        self.refresh_states()

    def refresh_states(self):
        """Refresh state"""
        self.set_status_text()
        self.preset_tab.refresh_list()
        self.widget_tab.refresh_state()
        self.module_tab.refresh_state()
        self.spectate_tab.refresh_list()
        self.pacenotes_tab.refresh_state()

    def __connect_signal(self):
        """Connect overlay reload signal"""
        octrl.state.reload.connect(self.reload_preset)

    def __break_signal(self):
        """Disconnect overlay reload signal"""
        octrl.state.reload.disconnect(self.reload_preset)
