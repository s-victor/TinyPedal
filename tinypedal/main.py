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
Main window
"""

import os
import shutil
import time

from PySide2.QtCore import Qt, QRegExp
from PySide2.QtGui import QIcon, QRegExpValidator, QDesktopServices
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMenu,
    QAction,
    QListWidget,
    QMessageBox,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QTabWidget,
    QListWidgetItem,
)

from .const import APP_NAME, VERSION, APP_ICON, PATH_SETTINGS, PATH_DELTABEST, PATH_TRACKMAP
from .about import About
from .setting import cfg
from .api_control import api
from .module_control import mctrl
from .widget_control import wctrl
from .overlay_control import octrl
from .config import VehicleClassEditor, FontConfig, UserConfig
from . import formatter as fmt
from . import regex_pattern as rxp
from . import validator as val


class AppWindow(QMainWindow):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(300)
        self.setMinimumHeight(450)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # disable maximize
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setWindowIcon(QIcon(APP_ICON))

        # Create menu
        self.main_menubar()

        # Start
        self.start_app()

        # Add status bar
        self.label_api_version = QLabel("")
        self.statusBar().addPermanentWidget(self.label_api_version)
        self.set_status_text()

        # Create tabs
        main_tab = QTabWidget()
        self.widget_tab = WidgetList()
        self.module_tab = ModuleList()
        self.preset_tab = PresetList(self)
        self.spectate_tab = SpectateList(self)
        main_tab.addTab(self.widget_tab, "Widget")
        main_tab.addTab(self.module_tab, "Module")
        main_tab.addTab(self.preset_tab, "Preset")
        main_tab.addTab(self.spectate_tab, "Spectate")
        self.setCentralWidget(main_tab)

    def main_menubar(self):
        """Create menu bar"""
        menu = self.menuBar()

        # Overlay menu
        menu_overlay = menu.addMenu("Overlay")
        self.overlay_menu = OverlayMenu
        self.overlay_menu(self, menu_overlay)
        menu_overlay.addSeparator()

        # Sub-menu
        menu_reset_data = menu_overlay.addMenu("Reset data")
        ResetDataMenu(self, menu_reset_data)
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

    def start_app(self):
        """Start modules & widgets"""
        api.connect(cfg.shared_memory_api["api_name"])
        api.start()

        mctrl.start()  # 1 start module
        octrl.enable()  # 2 enable overlay control
        wctrl.start()  # 3 start widget

        self.start_tray_icon()
        self.set_initial_window_state()

    def start_tray_icon(self):
        """Start tray icon (for Windows)"""
        from .tray import TrayIcon
        self.tray_icon = TrayIcon(self, cfg)
        self.tray_icon.show()

    def set_initial_window_state(self):
        """Set initial window state"""
        if cfg.application["remember_position"]:
            app_pos_x = cfg.application["position_x"]
            app_pos_y = cfg.application["position_y"]
            if app_pos_x + app_pos_y:
                self.move(app_pos_x, app_pos_y)
            else:
                self.save_window_position()

        if cfg.application["show_at_startup"]:
            self.show()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

    def set_status_text(self):
        """Set status text"""
        self.label_api_version.setText(f"API: {api.name} - {api.version}")

    def quit_app(self):
        """Quit manager"""
        self.save_window_position()
        mctrl.close()  # stop module
        octrl.disable()  # disable overlay control
        wctrl.close()  # close widget
        QApplication.quit()  # close app
        api.stop()  # stop sharedmemory mapping

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

    def save_window_position(self):
        """Save window position"""
        if cfg.application["remember_position"]:
            cfg.application["position_x"] = self.x()
            cfg.application["position_y"] = self.y()
            cfg.save(0)

    def restart_api(self):
        """Restart shared memory api"""
        mctrl.close()
        api.restart()
        mctrl.start()
        self.set_status_text()

    def reload_preset(self):
        """Reload current preset"""
        # Close modules & widgets in order
        mctrl.close()
        octrl.disable()
        wctrl.close()
        # Load new setting
        cfg.load()
        self.restart_api()
        # Start modules & widgets
        mctrl.start()
        octrl.enable()
        wctrl.start()
        # Refresh menu & preset list
        self.preset_tab.refresh_preset_list()
        self.widget_tab.refresh_widget_list()
        self.module_tab.refresh_module_list()
        self.spectate_tab.refresh_spectate_list()


class WidgetList(QWidget):
    """Widget list box"""
    CFG_TYPE = "widget"

    def __init__(self):
        super().__init__()

        # Label
        self.label_loaded = QLabel("")

        # List box
        self.listbox_widget = QListWidget(self)
        self.listbox_widget.setAlternatingRowColors(True)
        self.listbox_widget.setStyleSheet(
            "QListView {outline: none;}"
            "QListView::item {height: 28px;border-radius: 0;}"
            "QListView::item:selected {background-color: transparent;}"
            "QListView::item:hover {background-color: transparent;}"
        )
        self.refresh_widget_list()
        self.listbox_widget.setCurrentRow(0)

        # Button
        button_enable = QPushButton("Enable All")
        button_enable.clicked.connect(self.widget_button_enable_all)

        button_disable = QPushButton("Disable All")
        button_disable.clicked.connect(self.widget_button_disable_all)

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_widget)
        layout_button.addWidget(button_enable)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_disable)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def toggle_control(self, obj=None):
        """Toggle control & update label"""
        if obj:
            wctrl.toggle(obj)
        self.label_loaded.setText(
            f"Enabled: <b>{len(cfg.active_widget_list)}/{len(wctrl.WIDGET_PACK)}</b>")

    def refresh_widget_list(self):
        """Refresh preset list"""
        self.listbox_widget.clear()

        for obj in wctrl.WIDGET_PACK:
            widget_item = ListItemControl(self, obj, obj.WIDGET_NAME)
            item = QListWidgetItem()
            self.listbox_widget.addItem(item)
            self.listbox_widget.setItemWidget(item, widget_item)

    def widget_button_enable_all(self):
        """Enable all widgets"""
        if len(cfg.active_widget_list) != len(wctrl.WIDGET_PACK):
            wctrl.enable_all()
            self.refresh_widget_list()

    def widget_button_disable_all(self):
        """Disable all widgets"""
        if cfg.active_widget_list:
            wctrl.disable_all()
            self.refresh_widget_list()


class ModuleList(QWidget):
    """Module list box"""
    CFG_TYPE = "module"

    def __init__(self):
        super().__init__()

        # Label
        self.label_loaded = QLabel("")

        # List box
        self.listbox_module = QListWidget(self)
        self.listbox_module.setAlternatingRowColors(True)
        self.listbox_module.setStyleSheet(
            "QListView {outline: none;}"
            "QListView::item {height: 28px;border-radius: 0;}"
            "QListView::item:selected {background-color: transparent;}"
            "QListView::item:hover {background-color: transparent;}"
        )
        self.refresh_module_list()
        self.listbox_module.setCurrentRow(0)

        # Button
        button_enable = QPushButton("Enable All")
        button_enable.clicked.connect(self.module_button_enable_all)

        button_disable = QPushButton("Disable All")
        button_disable.clicked.connect(self.module_button_disable_all)

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_module)
        layout_button.addWidget(button_enable)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_disable)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def toggle_control(self, obj=None):
        """Toggle control & update label"""
        if obj:
            mctrl.toggle(obj)
        self.label_loaded.setText(
            f"Enabled: <b>{len(cfg.active_module_list)}/{len(mctrl.MODULE_PACK)}</b>")

    def refresh_module_list(self):
        """Refresh module list"""
        self.listbox_module.clear()

        for obj in mctrl.MODULE_PACK:
            module_item = ListItemControl(self, obj, obj.MODULE_NAME)
            item = QListWidgetItem()
            self.listbox_module.addItem(item)
            self.listbox_module.setItemWidget(item, module_item)

    def module_button_enable_all(self):
        """Enable all modules"""
        if len(cfg.active_module_list) != len(mctrl.MODULE_PACK):
            mctrl.enable_all()
            self.refresh_module_list()

    def module_button_disable_all(self):
        """Disable all modules"""
        if cfg.active_module_list:
            mctrl.disable_all()
            self.refresh_module_list()


class ListItemControl(QWidget):
    """List box item control"""

    def __init__(self, master, obj, obj_name):
        super().__init__()
        self.master = master
        self.obj_name = obj_name

        label_obj = QLabel(fmt.format_module_name(self.obj_name))
        button_toggle = self.add_toggle_button(obj, cfg.setting_user[self.obj_name]["enable"])
        button_config = self.add_config_button()

        layout_item = QHBoxLayout()
        layout_item.setContentsMargins(4,0,4,0)
        layout_item.addWidget(label_obj, stretch=1)
        layout_item.addWidget(button_config)
        layout_item.addWidget(button_toggle)
        layout_item.setSpacing(4)

        self.setStyleSheet("font-size: 16px;")
        self.setLayout(layout_item)

    def add_toggle_button(self, obj, state):
        """Add toggle button"""
        button = QPushButton("")
        button.setCheckable(True)
        button.setChecked(state)
        self.set_toggle_state(state, button)
        button.toggled.connect(
            lambda checked=state: self.set_toggle_state(checked, button, obj))
        button.setStyleSheet(
            "QPushButton {color: #555;background-color: #CCC;font-size: 14px;"
            "min-width: 30px;max-width: 30px;padding: 2px 3px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
        )
        return button

    def add_config_button(self):
        """Add config button"""
        button = QPushButton("Config")
        button.pressed.connect(self.open_config_dialog)
        button.setStyleSheet(
            "QPushButton {color: #AAA;font-size: 14px;"
            "padding: 2px 5px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
        )
        return button

    def set_toggle_state(self, checked, button, obj=None):
        """Set toggle state"""
        self.master.toggle_control(obj)
        button.setText("ON" if checked else "OFF")

    def open_config_dialog(self):
        """Config dialog"""
        _dialog = UserConfig(self.master, self.obj_name, self.master.CFG_TYPE)
        _dialog.open()


class SpectateList(QWidget):
    """Spectate list box"""

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.spectate_list = []

        # Label
        self.label_spectateed = QLabel("")

        # List box
        self.listbox_spectate = QListWidget(self)
        self.listbox_spectate.setAlternatingRowColors(True)
        self.listbox_spectate.setStyleSheet(
            "QListView {font-size: 14px;outline: none;}"
            "QListView::item {height: 26px;border-radius: 0;}"
            "QListView::item:selected {selection-color:#FFF;background-color: #F20;}"
        )
        self.listbox_spectate.itemDoubleClicked.connect(self.spectate_selected)

        # Button
        self.button_spectate = QPushButton("Spectate")
        self.button_spectate.clicked.connect(self.spectate_selected)

        self.button_refresh = QPushButton("Refresh")
        self.button_refresh.clicked.connect(self.refresh_spectate_list)

        self.button_toggle = QPushButton("")
        self.button_toggle.setCheckable(True)
        self.button_toggle.clicked.connect(self.spectate_toggle_state)
        self.refresh_spectate_list()

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_spectateed)
        layout_main.addWidget(self.listbox_spectate)
        layout_button.addWidget(self.button_spectate)
        layout_button.addWidget(self.button_refresh)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(self.button_toggle)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def set_button_state(self):
        """Set button state"""
        if cfg.shared_memory_api["enable_player_index_override"]:
            self.button_toggle.setChecked(True)
            self.button_toggle.setText("Enabled")
            self.listbox_spectate.setDisabled(False)
            self.button_spectate.setDisabled(False)
            self.button_refresh.setDisabled(False)
            self.label_spectateed.setDisabled(False)
        else:
            self.button_toggle.setChecked(False)
            self.button_toggle.setText("Disabled")
            self.listbox_spectate.setDisabled(True)
            self.button_spectate.setDisabled(True)
            self.button_refresh.setDisabled(True)
            self.label_spectateed.setDisabled(True)

    def spectate_toggle_state(self):
        """Spectate state toggle"""
        if cfg.shared_memory_api["enable_player_index_override"]:
            cfg.shared_memory_api["enable_player_index_override"] = False
        else:
            cfg.shared_memory_api["enable_player_index_override"] = True
        cfg.save()  # save only if toggled
        api.setup()
        self.refresh_spectate_list()

    def refresh_spectate_list(self):
        """Refresh spectate list"""
        if cfg.shared_memory_api["enable_player_index_override"]:
            temp_list = ["Anonymous", *api.read.vehicle.driver_list()]
            if temp_list != self.spectate_list:
                self.spectate_list = temp_list
                self.listbox_spectate.clear()
                self.listbox_spectate.addItems(self.spectate_list)
            index = cfg.shared_memory_api["player_index"] + 1
            if index >= len(temp_list):  # prevent index out of range
                index = 0
            self.listbox_spectate.setCurrentRow(index)
            self.label_spectateed.setText(
                f"Spectating: <b>{self.spectate_list[index]}</b>")
        else:
            self.spectate_list = []
            self.listbox_spectate.clear()
            self.label_spectateed.setText(
                "Spectating: <b>Disabled</b>")

        self.set_button_state()

    def spectate_selected(self):
        """Spectate selected player"""
        selected_index = self.listbox_spectate.currentRow()
        if selected_index >= 0:
            cfg.shared_memory_api["player_index"] = selected_index - 1
        else:
            cfg.shared_memory_api["player_index"] = -1
        api.setup()
        self.refresh_spectate_list()
        cfg.save()  # save only if selected


class PresetList(QWidget):
    """Preset list box"""

    def __init__(self, master):
        super().__init__()
        self.master = master
        self.preset_list = []

        # Label
        self.label_loaded = QLabel("")

        # List box
        self.listbox_preset = QListWidget(self)
        self.listbox_preset.setAlternatingRowColors(True)
        self.listbox_preset.setStyleSheet(
            "QListView {font-size: 16px;outline: none;}"
            "QListView::item {height: 28px;border-radius: 0;}"
            "QListView::item:selected {selection-color:#FFF;background-color: #F20;}"
        )
        self.refresh_preset_list()
        self.listbox_preset.setCurrentRow(0)
        self.listbox_preset.itemDoubleClicked.connect(self.load_preset)

        # Button
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)

        button_refresh = QPushButton("Refresh")
        button_refresh.clicked.connect(self.refresh_preset_list)

        button_new = QPushButton("New Preset")
        button_new.clicked.connect(self.open_create_preset)

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_preset)
        layout_button.addWidget(button_load)
        layout_button.addWidget(button_refresh)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_new)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

        self.listbox_preset.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listbox_preset.customContextMenuRequested.connect(self.context_menu)

    def refresh_preset_list(self):
        """Refresh preset list"""
        temp_list = cfg.load_preset_list()
        if temp_list != self.preset_list:
            self.preset_list = temp_list
            self.listbox_preset.clear()
            self.listbox_preset.addItems(self.preset_list)
        self.label_loaded.setText(
            f"Loaded: <b>{cfg.last_loaded_setting[:-5]}</b>")

    def load_preset(self):
        """Load selected preset"""
        selected_index = self.listbox_preset.currentRow()
        if selected_index >= 0:
            cfg.filename_setting = f"{self.preset_list[selected_index]}.json"
            self.master.reload_preset()
        else:
            QMessageBox.warning(
                self, "Error",
                "No preset selected.\nPlease select a preset to continue.")

    def open_create_preset(self):
        """Create new preset"""
        _dialog = CreatePreset(self, title="Create new default preset")
        _dialog.open()

    def context_menu(self, position):
        """Preset context menu"""
        if bool(self.listbox_preset.itemAt(position)):
            menu = QMenu()
            option_duplicate = menu.addAction("Duplicate")
            option_rename = menu.addAction("Rename")
            option_delete = menu.addAction("Delete")

            action = menu.exec_(self.listbox_preset.mapToGlobal(position))
            selected_index = self.listbox_preset.currentRow()
            selected_filename = f"{self.preset_list[selected_index]}.json"

            # Duplicate preset
            if action == option_duplicate:
                _dialog = CreatePreset(
                    self,
                    title="Duplicate Preset",
                    mode="duplicate",
                    src_filename=selected_filename
                )
                _dialog.open()
            # Rename preset
            elif action == option_rename:
                _dialog = CreatePreset(
                    self,
                    title="Rename Preset",
                    mode="rename",
                    src_filename=selected_filename
                )
                _dialog.open()
            # Delete preset
            elif action == option_delete:
                message_text = (
                    "<font style='font-size: 15px;'><b>"
                    "Are you sure you want to delete<br>"
                    f"\"{self.preset_list[selected_index]}.json\""
                    " permanently?</b></font>"
                    "<br><br>This cannot be undone!"
                )
                delete_msg = QMessageBox.question(
                    self, "Delete Preset", message_text,
                    button=QMessageBox.Yes | QMessageBox.No)

                if delete_msg == QMessageBox.Yes:
                    if os.path.exists(f"{PATH_SETTINGS}{selected_filename}"):
                        os.remove(f"{PATH_SETTINGS}{selected_filename}")
                    self.refresh_preset_list()


class CreatePreset(QDialog):
    """Create preset"""

    def __init__(self, master, title="", mode=None, src_filename=None):
        super().__init__(master)
        self.master = master
        self.edit_mode = mode
        self.src_filename = src_filename
        self.setFixedWidth(280)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Entry box
        self.preset_entry = QLineEdit()
        self.preset_entry.setMaxLength(40)
        self.preset_entry.setPlaceholderText("Enter a new preset name")
        exclude_char = QRegExp('[^\\\\/:*?"<>|]*')
        self.preset_entry.setValidator(QRegExpValidator(exclude_char))

        # Button
        button_create = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        button_create.accepted.connect(self.creating)
        button_create.rejected.connect(self.reject)

        # Layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.preset_entry)
        layout_main.addWidget(button_create)
        self.setLayout(layout_main)

    def creating(self):
        """Creating new preset"""
        entered_filename = fmt.strip_filename_extension(self.preset_entry.text(), ".json")

        if val.allowed_filename(rxp.CFG_INVALID_FILENAME, entered_filename):
            self.__saving(entered_filename)
        else:
            QMessageBox.warning(
                self, "Error", "Invalid preset name.")

    def __saving(self, entered_filename):
        """Saving new preset"""
        # Check existing preset
        temp_list = cfg.load_preset_list()
        for preset in temp_list:
            if entered_filename.lower() == preset.lower():
                QMessageBox.warning(
                    self, "Error", "Preset already exists.")
                return None
        # Duplicate preset
        if self.edit_mode == "duplicate":
            shutil.copy(
                f"{PATH_SETTINGS}{self.src_filename}",
                f"{PATH_SETTINGS}{entered_filename}.json"
            )
            self.master.refresh_preset_list()
        # Rename preset
        elif self.edit_mode == "rename":
            os.rename(
                f"{PATH_SETTINGS}{self.src_filename}",
                f"{PATH_SETTINGS}{entered_filename}.json"
            )
            # Reload if renamed file was loaded
            if cfg.filename_setting == self.src_filename:
                cfg.filename_setting = f"{entered_filename}.json"
                self.master.master.reload_preset()
            else:
                self.master.refresh_preset_list()
        # Create new preset
        else:
            cfg.filename_setting = f"{entered_filename}.json"
            cfg.create()
            cfg.save(0)  # save setting
            while cfg.is_saving:  # wait saving finish
                time.sleep(0.01)
            self.master.refresh_preset_list()
        # Close window
        self.accept()
        return None


class OverlayMenu(QMenu):
    """Overlay menu, shared between main & tray menu"""

    def __init__(self, master, menu):
        super().__init__(master)
        self.master = master

        # Lock overlay
        self.overlay_lock = QAction("Lock overlay", self)
        self.overlay_lock.setCheckable(True)
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_lock.triggered.connect(self.is_locked)
        menu.addAction(self.overlay_lock)

        # Auto hide
        self.overlay_hide = QAction("Auto hide", self)
        self.overlay_hide.setCheckable(True)
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])
        self.overlay_hide.triggered.connect(self.is_hidden)
        menu.addAction(self.overlay_hide)

        # Grid move
        self.overlay_grid = QAction("Grid move", self)
        self.overlay_grid.setCheckable(True)
        self.overlay_grid.setChecked(cfg.overlay["enable_grid_move"])
        self.overlay_grid.triggered.connect(self.has_grid)
        menu.addAction(self.overlay_grid)

        # Reload preset
        reload_preset = QAction("Reload", self)
        reload_preset.triggered.connect(self.master.reload_preset)
        menu.addAction(reload_preset)
        menu.addSeparator()

        # Restart API
        restart_api = QAction("Restart API", self)
        restart_api.triggered.connect(self.master.restart_api)
        menu.addAction(restart_api)

        # Refresh menu
        menu.aboutToShow.connect(self.refresh_overlay_menu)

    def refresh_overlay_menu(self):
        """Refresh overlay menu"""
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])
        self.overlay_grid.setChecked(cfg.overlay["enable_grid_move"])

    @staticmethod
    def is_locked():
        """Check lock state"""
        octrl.overlay_lock.toggle()

    @staticmethod
    def is_hidden():
        """Check hide state"""
        octrl.overlay_hide.toggle()

    @staticmethod
    def has_grid():
        """Check hide state"""
        octrl.overlay_grid.toggle()


class ResetDataMenu(QMenu):
    """Reset user data menu"""

    def __init__(self, master, menu):
        super().__init__(master)
        self.master = master

        # Deltabest
        reset_deltabest = QAction("Deltabest", self)
        reset_deltabest.triggered.connect(self.reset_deltabest)
        menu.addAction(reset_deltabest)

        # Fuel delta
        reset_fueldelta = QAction("Fuel delta", self)
        reset_fueldelta.triggered.connect(self.reset_fueldelta)
        menu.addAction(reset_fueldelta)

        # Track map
        reset_trackmap = QAction("Track map", self)
        reset_trackmap.triggered.connect(self.reset_trackmap)
        menu.addAction(reset_trackmap)

    def reset_deltabest(self):
        """Reset deltabest data"""
        self.__confirmation(
            "deltabest", "csv", PATH_DELTABEST, api.read.check.combo_id())

    def reset_fueldelta(self):
        """Reset fuel delta data"""
        self.__confirmation(
            "fuel delta", "fuel", PATH_DELTABEST, api.read.check.combo_id())

    def reset_trackmap(self):
        """Reset trackmap data"""
        self.__confirmation(
            "track map", "svg", PATH_TRACKMAP, api.read.check.track_id())

    def __confirmation(self, data_type, file_ext, file_path, combo_name):
        """Message confirmation"""
        # Check if on track
        if api.state:
            QMessageBox.warning(
                self.master, "Error",
                "Cannot reset data while on track.")
            return None
        # Check if file exist
        if not os.path.exists(f"{file_path}{combo_name}.{file_ext}"):
            QMessageBox.warning(
                self.master, "Error",
                f"No {data_type} data found.<br><br>You can only reset data from active session.")
            return None
        # Confirm reset
        message_text = (
            f"Are you sure you want to reset {data_type} data for<br>"
            f"<b>{combo_name}</b>"
            " ?<br><br>This cannot be undone!"
        )
        delete_msg = QMessageBox.question(
            self.master, f"Reset {data_type.title()}", message_text,
            button=QMessageBox.Yes | QMessageBox.No)
        if delete_msg == QMessageBox.Yes:
            os.remove(f"{file_path}{combo_name}.{file_ext}")
            QMessageBox.information(
                self.master, f"Reset {data_type.title()}",
                f"{data_type.capitalize()} data has been reset for<br><b>{combo_name}</b>")
            combo_name = None
        return None


class ConfigMenu(QMenu):
    """Config menu"""

    def __init__(self, master, menu):
        super().__init__(master)
        self.master = master

        config_units = QAction("Units and symbols", self)
        config_units.triggered.connect(self.open_config_units)
        menu.addAction(config_units)

        config_font = QAction("Global font override", self)
        config_font.triggered.connect(self.open_config_font)
        menu.addAction(config_font)

        config_sharedmem = QAction("Shared memory API", self)
        config_sharedmem.triggered.connect(self.open_config_sharedmemory)
        menu.addAction(config_sharedmem)

        config_compat = QAction("Compatibility", self)
        config_compat.triggered.connect(self.open_config_compatibility)
        menu.addAction(config_compat)

        menu.addSeparator()
        config_classes = QAction("Vehicle class editor", self)
        config_classes.triggered.connect(self.open_config_classes)
        menu.addAction(config_classes)

    def open_config_font(self):
        """Config global font"""
        _dialog = FontConfig(self.master)
        _dialog.open()

    def open_config_units(self):
        """Config display units"""
        _dialog = UserConfig(self.master, "units", "misc")
        _dialog.open()

    def open_config_sharedmemory(self):
        """Config sharedmemory"""
        _dialog = UserConfig(self.master, "shared_memory_api", "api")
        _dialog.open()

    def open_config_compatibility(self):
        """Config compatibility"""
        _dialog = UserConfig(self.master, "compatibility", "misc")
        _dialog.open()

    def open_config_classes(self):
        """Config classes preset"""
        _dialog = VehicleClassEditor(self.master)
        _dialog.open()


class WindowMenu(QMenu):
    """Window menu"""

    def __init__(self, master, menu):
        super().__init__(master)

        # Show at startup
        self.show_window = QAction("Show at startup", self)
        self.show_window.setCheckable(True)
        self.show_window.setChecked(cfg.application["show_at_startup"])
        self.show_window.triggered.connect(self.is_show_at_startup)
        menu.addAction(self.show_window)

        # Minimize to tray
        self.minimize_to_tray = QAction("Minimize to tray", self)
        self.minimize_to_tray.setCheckable(True)
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.minimize_to_tray.triggered.connect(self.is_minimize_to_tray)
        menu.addAction(self.minimize_to_tray)

        # Remember position
        self.remember_position = QAction("Remember position", self)
        self.remember_position.setCheckable(True)
        self.remember_position.setChecked(cfg.application["remember_position"])
        self.remember_position.triggered.connect(self.is_remember_position)
        menu.addAction(self.remember_position)

        # Refresh menu
        menu.aboutToShow.connect(self.refresh_window_menu)

    def refresh_window_menu(self):
        """Refresh window menu"""
        self.show_window.setChecked(cfg.application["show_at_startup"])
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.remember_position.setChecked(cfg.application["remember_position"])

    @staticmethod
    def is_show_at_startup():
        """Toggle config window startup state"""
        if not cfg.application["show_at_startup"]:
            cfg.application["show_at_startup"] = True
        else:
            cfg.application["show_at_startup"] = False
        cfg.save()

    @staticmethod
    def is_minimize_to_tray():
        """Toggle minimize to tray state"""
        if not cfg.application["minimize_to_tray"]:
            cfg.application["minimize_to_tray"] = True
        else:
            cfg.application["minimize_to_tray"] = False
        cfg.save()

    @staticmethod
    def is_remember_position():
        """Toggle config window remember position state"""
        if not cfg.application["remember_position"]:
            cfg.application["remember_position"] = True
        else:
            cfg.application["remember_position"] = False
        cfg.save()


class HelpMenu(QMenu):
    """Help menu"""

    def __init__(self, master, menu):
        super().__init__(master)

        app_guide = QAction("User guide", self)
        app_guide.triggered.connect(self.open_user_guide)
        menu.addAction(app_guide)

        app_faq = QAction("FAQ", self)
        app_faq.triggered.connect(self.open_faq)
        menu.addAction(app_faq)

        menu.addSeparator()
        # Load about window in background
        self.about = About(hideonclose=True)
        app_about = QAction("About", self)
        app_about.triggered.connect(self.show_about)
        menu.addAction(app_about)

    def show_about(self):
        """Show about"""
        self.about.show()

    def open_user_guide(self):
        """Open user guide link"""
        QDesktopServices.openUrl(
            "https://github.com/s-victor/TinyPedal/wiki/User-Guide"
        )

    def open_faq(self):
        """Open FAQ link"""
        QDesktopServices.openUrl(
            "https://github.com/s-victor/TinyPedal/wiki/Frequently-Asked-Questions"
        )
