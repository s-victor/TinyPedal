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
Menu
"""

import os

from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QMenu, QAction, QMessageBox

from ..const import LINK_USER_GUIDE, LINK_FAQ
from ..setting import cfg
from ..api_control import api
from ..overlay_control import octrl
from .about import About
from .config import FontConfig, UserConfig
from .log_info import LogInfo
from .fuel_calculator import FuelCalculator
from .heatmap_editor import HeatmapEditor
from .track_map_viewer import TrackMapViewer
from .track_notes_editor import TrackNotesEditor
from .brake_editor import BrakeEditor
from .tyre_compound_editor import TyreCompoundEditor
from .vehicle_brand_editor import VehicleBrandEditor
from .vehicle_class_editor import VehicleClassEditor


class OverlayMenu(QMenu):
    """Overlay menu, shared between main & tray menu"""

    def __init__(self, title, master, is_tray: bool = False):
        super().__init__(title, master)
        self.master = master

        if is_tray:
            self.loaded_preset = QAction("", self)
            self.loaded_preset.setDisabled(True)
            self.addAction(self.loaded_preset)
            self.aboutToShow.connect(self.refresh_preset_name)
            self.addSeparator()

        # Lock overlay
        self.overlay_lock = QAction("Lock Overlay", self)
        self.overlay_lock.setCheckable(True)
        self.overlay_lock.triggered.connect(self.is_locked)
        self.addAction(self.overlay_lock)

        # Auto hide
        self.overlay_hide = QAction("Auto Hide", self)
        self.overlay_hide.setCheckable(True)
        self.overlay_hide.triggered.connect(self.is_hidden)
        self.addAction(self.overlay_hide)

        # Grid move
        self.overlay_grid = QAction("Grid Move", self)
        self.overlay_grid.setCheckable(True)
        self.overlay_grid.triggered.connect(self.has_grid)
        self.addAction(self.overlay_grid)

        # Reload preset
        reload_preset = QAction("Reload", self)
        reload_preset.triggered.connect(self.master.reload_preset)
        self.addAction(reload_preset)
        self.addSeparator()

        # Restart API
        restart_api = QAction("Restart API", self)
        restart_api.triggered.connect(self.master.restart_api)
        self.addAction(restart_api)
        self.addSeparator()

        # Reset submenu
        menu_reset_data = ResetDataMenu("Reset Data", self.master)
        self.addMenu(menu_reset_data)
        self.addSeparator()

        # Config
        if is_tray:
            app_config = QAction("Config", self)
            app_config.triggered.connect(self.master.show_app)
            self.addAction(app_config)
            self.addSeparator()

        # Quit
        app_quit = QAction("Quit", self)
        app_quit.triggered.connect(self.master.quit_app)
        self.addAction(app_quit)

        # Refresh menu
        self.aboutToShow.connect(self.refresh_menu)

    def refresh_menu(self):
        """Refresh menu"""
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])
        self.overlay_grid.setChecked(cfg.overlay["enable_grid_move"])

    def refresh_preset_name(self):
        """Refresh preset name"""
        loaded_preset = cfg.filename.last_setting[:-5]
        if len(loaded_preset) > 16:
            loaded_preset = f"{loaded_preset[:16]}..."
        self.loaded_preset.setText(loaded_preset)

    @staticmethod
    def is_locked():
        """Check lock state"""
        octrl.toggle_lock()

    @staticmethod
    def is_hidden():
        """Check hide state"""
        octrl.toggle_hide()

    @staticmethod
    def has_grid():
        """Check grid move state"""
        octrl.toggle_grid()


class ResetDataMenu(QMenu):
    """Reset user data menu"""

    def __init__(self, title, master):
        super().__init__(title, master)
        self.master = master

        reset_deltabest = QAction("Delta Best", self)
        reset_deltabest.triggered.connect(self.reset_deltabest)
        self.addAction(reset_deltabest)

        reset_energydelta = QAction("Energy Delta", self)
        reset_energydelta.triggered.connect(self.reset_energydelta)
        self.addAction(reset_energydelta)

        reset_fueldelta = QAction("Fuel Delta", self)
        reset_fueldelta.triggered.connect(self.reset_fueldelta)
        self.addAction(reset_fueldelta)

        reset_sectorbest = QAction("Sector Best", self)
        reset_sectorbest.triggered.connect(self.reset_sectorbest)
        self.addAction(reset_sectorbest)

        reset_trackmap = QAction("Track Map", self)
        reset_trackmap.triggered.connect(self.reset_trackmap)
        self.addAction(reset_trackmap)

    def reset_deltabest(self):
        """Reset deltabest data"""
        self.__confirmation(
            data_type="delta best",
            extension="csv",
            filepath=cfg.path.delta_best,
            filename=api.read.check.combo_id(),
        )

    def reset_energydelta(self):
        """Reset energy delta data"""
        self.__confirmation(
            data_type="energy delta",
            extension="energy",
            filepath=cfg.path.energy_delta,
            filename=api.read.check.combo_id(),
        )

    def reset_fueldelta(self):
        """Reset fuel delta data"""
        self.__confirmation(
            data_type="fuel delta",
            extension="fuel",
            filepath=cfg.path.fuel_delta,
            filename=api.read.check.combo_id(),
        )

    def reset_sectorbest(self):
        """Reset sector best data"""
        self.__confirmation(
            data_type="sector best",
            extension="sector",
            filepath=cfg.path.sector_best,
            filename=api.read.check.combo_id(),
        )

    def reset_trackmap(self):
        """Reset trackmap data"""
        self.__confirmation(
            data_type="track map",
            extension="svg",
            filepath=cfg.path.track_map,
            filename=api.read.check.track_id(),
        )

    def __confirmation(self, data_type: str, extension: str, filepath: str, filename: str):
        """Message confirmation"""
        # Check if on track
        if api.state:
            QMessageBox.warning(
                self.master,
                "Error",
                "Cannot reset data while on track.",
            )
            return
        # Check if file exist
        filename_full = f"{filepath}{filename}.{extension}"
        if not os.path.exists(filename_full):
            QMessageBox.warning(
                self.master,
                "Error",
                f"No {data_type} data found.<br><br>You can only reset data from active session.",
            )
            return
        # Confirm reset
        msg_text = (
            f"Are you sure you want to reset {data_type} data for<br>"
            f"<b>{filename}</b> ?<br><br>This cannot be undone!"
        )
        delete_msg = QMessageBox.question(
            self.master,
            f"Reset {data_type.title()}",
            msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
        )
        if delete_msg == QMessageBox.Yes:
            os.remove(filename_full)
            QMessageBox.information(
                self.master,
                f"Reset {data_type.title()}",
                f"{data_type.capitalize()} data has been reset for<br><b>{filename}</b>",
            )


class ConfigMenu(QMenu):
    """Config menu"""

    def __init__(self, title, master):
        super().__init__(title, master)
        self.master = master

        config_app = QAction("Application", self)
        config_app.triggered.connect(self.open_config_application)
        self.addAction(config_app)

        config_compat = QAction("Compatibility", self)
        config_compat.triggered.connect(self.open_config_compatibility)
        self.addAction(config_compat)

        config_userpath = QAction("User Path", self)
        config_userpath.triggered.connect(self.open_config_userpath)
        self.addAction(config_userpath)
        self.addSeparator()

        config_units = QAction("Units and Symbols", self)
        config_units.triggered.connect(self.open_config_units)
        self.addAction(config_units)

        config_font = QAction("Global Font Override", self)
        config_font.triggered.connect(self.open_config_font)
        self.addAction(config_font)

        config_sharedmemory = QAction("Shared Memory API", self)
        config_sharedmemory.triggered.connect(self.open_config_sharedmemory)
        self.addAction(config_sharedmemory)

    def open_config_application(self):
        """Config global application"""
        _dialog = UserConfig(
            master=self.master,
            key_name="application",
            cfg_type="global",
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=self.master.reload_preset,
        )
        _dialog.open()

    def open_config_userpath(self):
        """Config global user path"""
        _dialog = UserConfig(
            master=self.master,
            key_name="user_path",
            cfg_type="global",
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=self.master.reload_preset,
            option_width=300,
        )
        _dialog.open()

    def open_config_font(self):
        """Config global font"""
        _dialog = FontConfig(
            master=self.master,
            user_setting=cfg.user.setting,
            reload_func=self.master.reload_preset,
        )
        _dialog.open()

    def open_config_units(self):
        """Config display units"""
        _dialog = UserConfig(
            master=self.master,
            key_name="units",
            cfg_type="preset",
            user_setting=cfg.user.setting,
            default_setting=cfg.default.setting,
            reload_func=self.master.reload_preset,
        )
        _dialog.open()

    def open_config_sharedmemory(self):
        """Config sharedmemory"""
        _dialog = UserConfig(
            master=self.master,
            key_name="shared_memory_api",
            cfg_type="preset",
            user_setting=cfg.user.setting,
            default_setting=cfg.default.setting,
            reload_func=self.master.restart_api,
        )
        _dialog.open()

    def open_config_compatibility(self):
        """Config compatibility"""
        _dialog = UserConfig(
            master=self.master,
            key_name="compatibility",
            cfg_type="global",
            user_setting=cfg.user.config,
            default_setting=cfg.default.config,
            reload_func=self.master.reload_preset,
        )
        _dialog.open()


class ToolsMenu(QMenu):
    """Tools menu"""

    def __init__(self, title, master):
        super().__init__(title, master)
        self.master = master

        utility_fuelcalc = QAction("Fuel Calculator", self)
        utility_fuelcalc.triggered.connect(self.open_utility_fuelcalc)
        self.addAction(utility_fuelcalc)

        utility_mapviewer = QAction("Track Map Viewer", self)
        utility_mapviewer.triggered.connect(self.open_utility_mapviewer)
        self.addAction(utility_mapviewer)
        self.addSeparator()

        editor_heatmap = QAction("Heatmap Editor", self)
        editor_heatmap.triggered.connect(self.open_editor_heatmap)
        self.addAction(editor_heatmap)

        editor_brakes = QAction("Brake Editor", self)
        editor_brakes.triggered.connect(self.open_editor_brakes)
        self.addAction(editor_brakes)

        editor_compounds = QAction("Tyre Compound Editor", self)
        editor_compounds.triggered.connect(self.open_editor_compounds)
        self.addAction(editor_compounds)

        editor_brands = QAction("Vehicle Brand Editor", self)
        editor_brands.triggered.connect(self.open_editor_brands)
        self.addAction(editor_brands)

        editor_classes = QAction("Vehicle Class Editor", self)
        editor_classes.triggered.connect(self.open_editor_classes)
        self.addAction(editor_classes)

        editor_tracknotes = QAction("Track Notes Editor", self)
        editor_tracknotes.triggered.connect(self.open_editor_tracknotes)
        self.addAction(editor_tracknotes)

    def open_utility_fuelcalc(self):
        """Fuel calculator"""
        _dialog = FuelCalculator(self.master)
        _dialog.show()

    def open_utility_mapviewer(self):
        """Track map viewer"""
        _dialog = TrackMapViewer(self.master)
        _dialog.show()

    def open_editor_heatmap(self):
        """Edit heatmap preset"""
        _dialog = HeatmapEditor(self.master)
        _dialog.show()

    def open_editor_brakes(self):
        """Edit brakes preset"""
        _dialog = BrakeEditor(self.master)
        _dialog.show()

    def open_editor_compounds(self):
        """Edit compounds preset"""
        _dialog = TyreCompoundEditor(self.master)
        _dialog.show()

    def open_editor_brands(self):
        """Edit brands preset"""
        _dialog = VehicleBrandEditor(self.master)
        _dialog.show()

    def open_editor_classes(self):
        """Edit classes preset"""
        _dialog = VehicleClassEditor(self.master)
        _dialog.show()

    def open_editor_tracknotes(self):
        """Edit track notes"""
        _dialog = TrackNotesEditor(self.master)
        _dialog.show()


class WindowMenu(QMenu):
    """Window menu"""

    def __init__(self, title, master):
        super().__init__(title, master)
        self.show_at_startup = QAction("Show at Startup", self)
        self.show_at_startup.setCheckable(True)
        self.show_at_startup.triggered.connect(self.is_show_at_startup)
        self.addAction(self.show_at_startup)

        self.minimize_to_tray = QAction("Minimize to Tray", self)
        self.minimize_to_tray.setCheckable(True)
        self.minimize_to_tray.triggered.connect(self.is_minimize_to_tray)
        self.addAction(self.minimize_to_tray)

        self.remember_position = QAction("Remember Position", self)
        self.remember_position.setCheckable(True)
        self.remember_position.triggered.connect(self.is_remember_position)
        self.addAction(self.remember_position)

        self.remember_size = QAction("Remember Size", self)
        self.remember_size.setCheckable(True)
        self.remember_size.triggered.connect(self.is_remember_size)
        self.addAction(self.remember_size)

        self.aboutToShow.connect(self.refresh_menu)

    def refresh_menu(self):
        """Refresh menu"""
        self.show_at_startup.setChecked(cfg.application["show_at_startup"])
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.remember_position.setChecked(cfg.application["remember_position"])
        self.remember_size.setChecked(cfg.application["remember_size"])

    def is_show_at_startup(self):
        """Toggle config window startup state"""
        self.__toggle_option("show_at_startup")

    def is_minimize_to_tray(self):
        """Toggle minimize to tray state"""
        self.__toggle_option("minimize_to_tray")

    def is_remember_position(self):
        """Toggle config window remember position state"""
        self.__toggle_option("remember_position")

    def is_remember_size(self):
        """Toggle config window remember size state"""
        self.__toggle_option("remember_size")

    @staticmethod
    def __toggle_option(option_name: str):
        """Toggle option"""
        cfg.application[option_name] = not cfg.application[option_name]
        cfg.save(filetype="config")


class HelpMenu(QMenu):
    """Help menu"""

    def __init__(self, title, master):
        super().__init__(title, master)
        self.master = master

        app_guide = QAction("User Guide", self)
        app_guide.triggered.connect(self.open_user_guide)
        self.addAction(app_guide)

        app_faq = QAction("FAQ", self)
        app_faq.triggered.connect(self.open_faq)
        self.addAction(app_faq)

        app_log = QAction("Show Log", self)
        app_log.triggered.connect(self.show_log)
        self.addAction(app_log)
        self.addSeparator()

        app_about = QAction("About", self)
        app_about.triggered.connect(self.show_about)
        self.addAction(app_about)

    def show_about(self):
        """Show about"""
        _dialog = About(self.master)
        _dialog.show()

    def show_log(self):
        """Show log"""
        _dialog = LogInfo(self.master)
        _dialog.show()

    def open_user_guide(self):
        """Open user guide link"""
        QDesktopServices.openUrl(LINK_USER_GUIDE)

    def open_faq(self):
        """Open FAQ link"""
        QDesktopServices.openUrl(LINK_FAQ)
