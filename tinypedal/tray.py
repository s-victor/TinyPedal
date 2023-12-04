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
Tray icon
"""

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QSystemTrayIcon, QMenu, QAction

from .const import APP_NAME, VERSION, APP_ICON


class TrayIcon(QSystemTrayIcon):
    """System tray icon

    Activate overlay widgets via system tray icon.
    """

    def __init__(self, master, config):
        super().__init__()
        self.cfg = config
        self.master = master

        # Config tray icon
        self.setIcon(QIcon(APP_ICON))
        self.setToolTip(f"{APP_NAME} v{VERSION}")

        # Create tray menu
        menu = QMenu()

        # Loaded preset name
        self.loaded_preset = QAction("", self)
        self.loaded_preset.setDisabled(True)
        menu.addAction(self.loaded_preset)
        menu.addSeparator()

        # Overlay menu
        self.master.overlay_menu(self.master, menu)
        menu.addSeparator()

        # Config
        app_config = QAction("Config", self)
        app_config.triggered.connect(self.show_config)
        menu.addAction(app_config)
        menu.addSeparator()

        # Quit
        app_quit = QAction("Quit", self)
        app_quit.triggered.connect(self.master.quit_app)
        menu.addAction(app_quit)

        self.setContextMenu(menu)
        menu.aboutToShow.connect(self.refresh_menu)

    def show_config(self):
        """Show config window"""
        self.master.show()
        self.master.activateWindow()

    def refresh_menu(self):
        """Refresh menu"""
        self.loaded_preset.setText(
            self.format_preset_name(self.cfg.last_loaded_setting))

    @staticmethod
    def format_preset_name(filename):
        """Format preset name"""
        loaded_preset = filename[:-5]
        if len(loaded_preset) > 16:
            loaded_preset = f"{loaded_preset[:16]}..."
        return loaded_preset
