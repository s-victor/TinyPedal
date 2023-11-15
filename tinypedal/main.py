#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
from PySide2.QtGui import QIcon, QRegExpValidator
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

from .setting import cfg
from .const import APP_NAME, VERSION, APP_ICON, PATH_SETTINGS
from .about import About
from .api_control import api
from .module_control import mctrl
from .widget_control import wctrl
from .overlay_control import octrl
from .config import FontConfig, UnitsConfig, WidgetConfig
from . import formatter as fmt
from . import validator as val


class AppWindow(QMainWindow):
    """Main window"""

    def __init__(self):
        super().__init__()
        self.resize(290,450)
        self.setMinimumWidth(290)
        self.setMinimumHeight(450)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)  # disable maximize
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setWindowIcon(QIcon(APP_ICON))

        # Start
        self.start_app()

        # Create menu
        self.main_menubar()

        # Add status bar
        self.label_api_version = QLabel("")
        self.statusBar().addPermanentWidget(self.label_api_version)
        self.set_status_text()

        # Create tabs
        self.main_tab = QTabWidget()
        self.widget_tab = WidgetList()
        self.module_tab = ModuleList()
        self.preset_tab = PresetList(self)
        self.spectate_tab = SpectateList(self)
        self.main_tab.addTab(self.widget_tab, 'Widget')
        self.main_tab.addTab(self.module_tab, 'Module')
        self.main_tab.addTab(self.preset_tab, 'Preset')
        self.main_tab.addTab(self.spectate_tab, 'Spectate')
        self.setCentralWidget(self.main_tab)

    def main_menubar(self):
        """Create menu bar"""
        menu = self.menuBar()

        # Overlay menu
        menu_overlay = menu.addMenu("Overlay")

        self.overlay_lock = QAction("Lock overlay", self)
        self.overlay_lock.setCheckable(True)
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_lock.triggered.connect(self.is_locked)
        menu_overlay.addAction(self.overlay_lock)

        self.overlay_hide = QAction("Auto hide", self)
        self.overlay_hide.setCheckable(True)
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])
        self.overlay_hide.triggered.connect(self.is_hidden)
        menu_overlay.addAction(self.overlay_hide)

        menu_overlay.aboutToShow.connect(self.refresh_overlay_menu)

        reload_preset = QAction("Reload", self)
        reload_preset.triggered.connect(self.reload_preset)
        menu_overlay.addAction(reload_preset)

        menu_overlay.addSeparator()

        restart_api = QAction("Restart API", self)
        restart_api.triggered.connect(self.restart_api)
        menu_overlay.addAction(restart_api)

        menu_overlay.addSeparator()

        app_quit = QAction("Quit", self)
        app_quit.triggered.connect(self.quit_app)
        menu_overlay.addAction(app_quit)

        # Config menu
        menu_config = menu.addMenu("Config")

        config_units = QAction("Display units", self)
        config_units.triggered.connect(self.open_config_units)
        menu_config.addAction(config_units)

        config_font = QAction("Global font override", self)
        config_font.triggered.connect(self.open_config_font)
        menu_config.addAction(config_font)

        config_sharedmem = QAction("Shared memory API", self)
        config_sharedmem.triggered.connect(self.open_config_sharedmemory)
        menu_config.addAction(config_sharedmem)

        config_compat = QAction("Compatibility", self)
        config_compat.triggered.connect(self.open_config_compatibility)
        menu_config.addAction(config_compat)

        # Window menu
        menu_window = menu.addMenu("Window")
        self.show_window = QAction("Show at startup", self)
        self.show_window.setCheckable(True)
        self.show_window.setChecked(cfg.application["show_at_startup"])
        self.show_window.triggered.connect(self.is_show_at_startup)
        menu_window.addAction(self.show_window)

        self.minimize_to_tray = QAction("Minimize to tray", self)
        self.minimize_to_tray.setCheckable(True)
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.minimize_to_tray.triggered.connect(self.is_minimize_to_tray)
        menu_window.addAction(self.minimize_to_tray)

        self.remember_position = QAction("Remember position", self)
        self.remember_position.setCheckable(True)
        self.remember_position.setChecked(cfg.application["remember_position"])
        self.remember_position.triggered.connect(self.is_remember_position)
        menu_window.addAction(self.remember_position)

        menu_window.aboutToShow.connect(self.refresh_window_menu)

        # Help menu
        menu_help = menu.addMenu("Help")
        app_about = QAction("About", self)
        app_about.triggered.connect(self.show_about)
        menu_help.addAction(app_about)

    def refresh_window_menu(self):
        """Refresh window menu"""
        self.show_window.setChecked(cfg.application["show_at_startup"])
        self.minimize_to_tray.setChecked(cfg.application["minimize_to_tray"])
        self.remember_position.setChecked(cfg.application["remember_position"])

    def refresh_overlay_menu(self):
        """Refresh overlay menu"""
        self.overlay_lock.setChecked(cfg.overlay["fixed_position"])
        self.overlay_hide.setChecked(cfg.overlay["auto_hide"])

    def start_app(self):
        """Start modules & widgets"""
        api.connect(cfg.shared_memory_api["api_name"])
        api.start()

        mctrl.start()  # 1 start module
        octrl.enable()  # 2 enable overlay control
        wctrl.start()  # 3 start widget

        self.about = About(hideonclose=True)
        self.start_tray_icon()
        self.set_initial_window_state()

    def set_initial_window_state(self):
        """Set initial window state"""
        if cfg.application["show_at_startup"]:
            self.show()
        elif not cfg.application["minimize_to_tray"]:
            self.showMinimized()

        if cfg.application["remember_position"]:
            app_pos_x = int(cfg.application["position_x"])
            app_pos_y = int(cfg.application["position_y"])
            if app_pos_x + app_pos_y:
                self.move(app_pos_x, app_pos_y)
            else:
                self.save_window_position()

    def set_status_text(self):
        """Set status text"""
        self.label_api_version.setText(f"API: {api.name} - {api.version}")

    def show_about(self):
        """Show about"""
        self.about.show()

    def start_tray_icon(self):
        """Start tray icon (for Windows)"""
        from .tray import TrayIcon
        self.tray_icon = TrayIcon(self, cfg)
        self.tray_icon.show()

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
        api.restart()
        self.set_status_text()

    @staticmethod
    def is_locked():
        """Check lock state"""
        octrl.overlay_lock.toggle()

    @staticmethod
    def is_hidden():
        """Check hide state"""
        octrl.overlay_hide.toggle()

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

    def open_config_units(self):
        """Config display units"""
        window_units_config = UnitsConfig(self)
        window_units_config.exec_()

    def open_config_font(self):
        """Config global font"""
        window_font_config = FontConfig(self)
        window_font_config.exec_()

    def open_config_sharedmemory(self):
        """Config sharedmemory"""
        window_sharedmemory_config = WidgetConfig(
            self, "shared_memory_api", "api")
        window_sharedmemory_config.exec_()

    def open_config_compatibility(self):
        """Config compatibility"""
        window_compat_config = WidgetConfig(
            self, "compatibility", "misc")
        window_compat_config.exec_()


class WidgetList(QWidget):
    """Widget list box"""

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
        layout_main = QVBoxLayout(self)
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_widget)
        layout_button.addWidget(button_enable)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_disable)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def refresh_widget_list(self):
        """Refresh preset list"""
        self.listbox_widget.clear()

        for obj in wctrl.WIDGET_PACK:
            widget_item = QWidget()
            widget_item.setStyleSheet("font-size: 16px;")
            label_widget = QLabel(fmt.format_widget_name(obj.WIDGET_NAME))
            button_toggle = self.widget_toggle_button(obj)
            button_config = self.widget_config_button(obj.WIDGET_NAME)

            layout_item = QHBoxLayout()
            layout_item.setContentsMargins(4,0,4,0)
            layout_item.addWidget(label_widget, stretch=1)
            layout_item.addWidget(button_config)
            layout_item.addWidget(button_toggle)
            layout_item.setSpacing(4)

            widget_item.setLayout(layout_item)

            item = QListWidgetItem()
            self.listbox_widget.addItem(item)
            self.listbox_widget.setItemWidget(item, widget_item)

    def widget_toggle_button(self, obj):
        """Widget toggle button"""
        button = QPushButton("")
        button.setCheckable(True)
        button.setChecked(cfg.setting_user[obj.WIDGET_NAME]["enable"])
        self.widget_toggle_state(
            cfg.setting_user[obj.WIDGET_NAME]["enable"], button)

        button.toggled.connect(
            lambda checked=cfg.setting_user[obj.WIDGET_NAME]["enable"],
            widget=obj: self.widget_toggle_state(checked, button, widget))

        button.setStyleSheet(
            "QPushButton {color: #555;background-color: #CCC;font-size: 14px;"
            "min-width: 30px;max-width: 30px;padding: 2px 3px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
            )
        return button

    def widget_toggle_state(self, checked, button, widget=None):
        """Widget state"""
        if widget:
            wctrl.toggle(widget)
        if checked:
            button.setText("ON")
        else:
            button.setText("OFF")
        self.label_loaded.setText(
            f"Enabled: <b>{len(cfg.active_widget_list)}/{len(wctrl.WIDGET_PACK)}</b>")

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

    def widget_config_button(self, widget_name):
        """Widget config button"""
        button = QPushButton("Config")
        button.pressed.connect(
            lambda name=widget_name: self.widget_config_dialog(name))
        button.setStyleSheet(
            "QPushButton {color: #AAA;font-size: 14px;"
            "padding: 2px 5px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
            )
        return button

    def widget_config_dialog(self, widget_name):
        """Widget config dialog"""
        window_widget_config = WidgetConfig(self, widget_name, "widget")
        window_widget_config.exec_()


class ModuleList(QWidget):
    """Module list box"""

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
        layout_main = QVBoxLayout(self)
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_module)
        layout_button.addWidget(button_enable)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_disable)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def refresh_module_list(self):
        """Refresh module list"""
        self.listbox_module.clear()

        for obj in mctrl.MODULE_PACK:
            module_item = QWidget()
            module_item.setStyleSheet("font-size: 16px;")
            label_module = QLabel(fmt.format_module_name(obj.MODULE_NAME))
            button_toggle = self.module_toggle_button(obj)
            button_config = self.module_config_button(obj.MODULE_NAME)

            layout_item = QHBoxLayout()
            layout_item.setContentsMargins(4,0,4,0)
            layout_item.addWidget(label_module, stretch=1)
            layout_item.addWidget(button_config)
            layout_item.addWidget(button_toggle)
            layout_item.setSpacing(4)

            module_item.setLayout(layout_item)

            item = QListWidgetItem()
            self.listbox_module.addItem(item)
            self.listbox_module.setItemWidget(item, module_item)

    def module_toggle_button(self, obj):
        """Module toggle button"""
        button_toggle = QPushButton("")
        button_toggle.setCheckable(True)
        button_toggle.setChecked(
            cfg.setting_user[obj.MODULE_NAME]["enable"])
        self.module_toggle_state(
            cfg.setting_user[obj.MODULE_NAME]["enable"], button_toggle)

        button_toggle.toggled.connect(
            lambda checked=cfg.setting_user[obj.MODULE_NAME]["enable"],
            module=obj: self.module_toggle_state(checked, button_toggle, module))

        button_toggle.setStyleSheet(
            "QPushButton {color: #555;background-color: #CCC;font-size: 14px;"
            "min-width: 30px;max-width: 30px;padding: 2px 3px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
            )
        return button_toggle

    def module_toggle_state(self, checked, button, module=None):
        """Module state"""
        if module:
            mctrl.toggle(module)
        if checked:
            button.setText("ON")
        else:
            button.setText("OFF")
        self.label_loaded.setText(
            f"Enabled: <b>{len(cfg.active_module_list)}/{len(mctrl.MODULE_PACK)}</b>")

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

    def module_config_button(self, module_name):
        """Module config button"""
        button = QPushButton("Config")
        button.pressed.connect(
            lambda name=module_name: self.module_config_dialog(name))
        button.setStyleSheet(
            "QPushButton {color: #AAA;font-size: 14px;"
            "padding: 2px 5px;border-radius: 3px;}"
            "QPushButton::hover {color: #FFF;background-color: #F20;}"
            "QPushButton::pressed {color: #FFF;background-color: #555;}"
            "QPushButton::checked {color: #FFF;background-color: #555;}"
            "QPushButton::checked:hover {color: #FFF;background-color: #F20;}"
            )
        return button

    def module_config_dialog(self, module_name):
        """Module config dialog"""
        window_widget_config = WidgetConfig(self, module_name, "module")
        window_widget_config.exec_()


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
        layout_main = QVBoxLayout(self)
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
        button_new.clicked.connect(self.open_create_window)

        # Layout
        layout_main = QVBoxLayout(self)
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
                self, "Warning",
                "No preset selected.\nPlease select a preset to continue.")

    def open_create_window(self):
        """Create new preset"""
        window_preset = CreatePreset(self, title="Create new default preset")
        window_preset.exec_()

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
                window_preset = CreatePreset(
                    self,
                    title="Duplicate Preset",
                    mode="duplicate",
                    src_filename=selected_filename
                )
                window_preset.exec_()
            # Rename preset
            elif action == option_rename:
                window_preset = CreatePreset(
                    self,
                    title="Rename Preset",
                    mode="rename",
                    src_filename=selected_filename
                )
                window_preset.exec_()
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
        entered_filename = fmt.format_preset_name(self.preset_entry.text())

        if val.setting_filename(entered_filename):
            self.__saving(entered_filename)
        else:
            QMessageBox.warning(
                self, "Warning", "Invalid preset name.")

    def __saving(self, entered_filename):
        """Saving new preset"""
        # Check existing preset
        temp_list = cfg.load_preset_list()
        for preset in temp_list:
            if entered_filename.lower() == preset.lower():
                QMessageBox.warning(
                    self, "Warning", "Preset already exists.")
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
