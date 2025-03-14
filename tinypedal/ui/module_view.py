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
Module & widget list view
"""

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from ..setting import cfg
from ..module_control import ModuleControl
from .. import formatter as fmt
from .config import UserConfig

BUTTON_STATE_TEXT = "OFF", "ON"
QSS_LISTBOX = (
    "QListView {outline: none;}"
    "QListView::item {height: 28px;border-radius: 0;}"
    "QListView::item:selected {background: transparent;}"
    "QListView::item:hover {background: transparent;}"
)
QSS_LISTBOX_ITEM = "font-size: 16px;"
QSS_BUTTON_TOGGLE = (
    "QPushButton {color: #555;background: #CCC;font-size: 14px;"
    "min-width: 30px;max-width: 30px;padding: 2px 3px;border-radius: 3px;}"
    "QPushButton::hover {color: #FFF;background: #F20;}"
    "QPushButton::pressed {color: #FFF;background: #555;}"
    "QPushButton::checked {color: #FFF;background: #555;}"
    "QPushButton::checked:hover {color: #FFF;background: #F20;}"
)
QSS_BUTTON_CONFIG = (
    "QPushButton {color: #AAA;font-size: 14px;"
    "padding: 2px 5px;border-radius: 3px;}"
    "QPushButton::hover {color: #FFF;background: #F20;}"
    "QPushButton::pressed {color: #FFF;background: #555;}"
    "QPushButton::checked {color: #FFF;background: #555;}"
    "QPushButton::checked:hover {color: #FFF;background: #F20;}"
)


class ModuleList(QWidget):
    """Module & widget list view"""

    def __init__(self, parent, module_control: ModuleControl):
        """Initialize module list setting

        Args:
            module_control: Module control (or widget) object.
        """
        super().__init__(parent)
        self.module_control = module_control

        # Label
        self.label_loaded = QLabel("")

        # List box
        self.listbox_buttons: list = []
        self.listbox_module = QListWidget(self)
        self.listbox_module.setAlternatingRowColors(True)
        self.listbox_module.setStyleSheet(QSS_LISTBOX)
        self.create_list()

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

    def create_list(self):
        """Create module list"""
        for _name in self.module_control.names:
            module_item = ListItemControl(self, _name, self.module_control)
            self.listbox_buttons.append(module_item)
            item = QListWidgetItem()
            self.listbox_module.addItem(item)
            self.listbox_module.setItemWidget(item, module_item)
        self.listbox_module.setCurrentRow(0)

    def refresh_state(self):
        """Refresh module & button toggle state"""
        for button in self.listbox_buttons:
            button.update_state()

    def refresh_label(self):
        """Refresh label text"""
        self.label_loaded.setText(
            f"Enabled: <b>{self.module_control.number_active}/{self.module_control.number_total}</b>"
        )

    def module_button_enable_all(self):
        """Enable all modules"""
        if self.module_control.number_active != self.module_control.number_total:
            if self.confirm_batch_toggle("Enable"):
                self.module_control.enable_all()
                self.refresh_state()

    def module_button_disable_all(self):
        """Disable all modules"""
        if self.module_control.number_active:
            if self.confirm_batch_toggle("Disable"):
                self.module_control.disable_all()
                self.refresh_state()

    def confirm_batch_toggle(self, confirm_type: str) -> bool:
        """Batch toggle confirmation"""
        if not cfg.application["show_confirmation_for_batch_toggle"]:
            return True
        msg_text = (
            f"Are you sure you want to <b>{confirm_type}</b> all "
            f"{self.module_control.type_id}s?"
        )
        confirm_msg = QMessageBox.question(
            self, "Confirm", msg_text,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        return confirm_msg == QMessageBox.Yes


class ListItemControl(QWidget):
    """List box item control"""

    def __init__(self, parent, module_name: str, module_control: ModuleControl):
        """Initialize list box setting

        Args:
            module_name: Module (or widget) name string.
            module_control: Module control (or widget) object.
        """
        super().__init__(parent)
        self._parent = parent
        self.module_name = module_name
        self.module_control = module_control
        self.allow_toggle = False

        label_module = QLabel(fmt.format_module_name(self.module_name))

        self.button_toggle = QPushButton("")
        self.set_button_toggle()
        button_config = QPushButton("Config")
        button_config.setStyleSheet(QSS_BUTTON_CONFIG)
        button_config.pressed.connect(self.open_config_dialog)

        layout_item = QHBoxLayout()
        layout_item.setContentsMargins(4, 0, 4, 0)
        layout_item.addWidget(label_module, stretch=1)
        layout_item.addWidget(button_config)
        layout_item.addWidget(self.button_toggle)
        layout_item.setSpacing(4)

        self.setStyleSheet(QSS_LISTBOX_ITEM)
        self.setLayout(layout_item)

    def set_button_toggle(self):
        """Set toggle button"""
        self.allow_toggle = False
        self.button_toggle.setStyleSheet(QSS_BUTTON_TOGGLE)
        self.button_toggle.setCheckable(True)
        self.button_toggle.setChecked(cfg.user.setting[self.module_name]["enable"])
        self.update_button_text()
        self.button_toggle.toggled.connect(self.toggle_state)
        self.allow_toggle = True

    def toggle_state(self):
        """Toggle button state"""
        if self.allow_toggle:
            self.module_control.toggle(self.module_name)
        self.update_button_text()

    def update_state(self):
        """Update button toggle state"""
        self.allow_toggle = False
        self.button_toggle.setChecked(cfg.user.setting[self.module_name]["enable"])
        self.allow_toggle = True

    def update_button_text(self):
        """Update button text"""
        self.button_toggle.setText(
            BUTTON_STATE_TEXT[cfg.user.setting[self.module_name]["enable"]]
        )
        self._parent.refresh_label()

    def open_config_dialog(self):
        """Config dialog"""
        _dialog = UserConfig(
            parent=self._parent,
            key_name=self.module_name,
            cfg_type=self.module_control.type_id,
            user_setting=cfg.user.setting,
            default_setting=cfg.default.setting,
            reload_func=self.reload,
        )
        _dialog.open()

    def reload(self):
        """Reload module & button state"""
        self.module_control.reload(self.module_name)
        self.update_state()
