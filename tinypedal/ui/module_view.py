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
)

from ..setting import cfg
from .. import formatter as fmt
from .config import UserConfig


class ModuleList(QWidget):
    """Module & widget list view"""

    def __init__(self, module: any, module_list: list, module_type: str = ""):
        super().__init__()
        self.module = module
        self.module_list = module_list
        self.module_type = module_type

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
        self.refresh_list()
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

    def toggle_control(self, obj_name=None):
        """Toggle control & update label"""
        if obj_name:
            self.module.toggle(obj_name)
        self.label_loaded.setText(
            f"Enabled: <b>{len(self.module_list)}/{len(self.module.PACK)}</b>")

    def refresh_list(self):
        """Refresh module list"""
        self.listbox_module.clear()

        for _name in self.module.PACK.keys():
            module_item = ListItemControl(self, _name)
            item = QListWidgetItem()
            self.listbox_module.addItem(item)
            self.listbox_module.setItemWidget(item, module_item)

    def module_button_enable_all(self):
        """Enable all modules"""
        if len(self.module_list) != len(self.module.PACK):
            self.module.enable_all()
            self.refresh_list()

    def module_button_disable_all(self):
        """Disable all modules"""
        if self.module_list:
            self.module.disable_all()
            self.refresh_list()


class ListItemControl(QWidget):
    """List box item control"""

    def __init__(self, master, obj_name):
        super().__init__()
        self.master = master
        self.obj_name = obj_name

        label_obj = QLabel(fmt.format_module_name(self.obj_name))
        button_toggle = self.add_toggle_button(obj_name, cfg.setting_user[self.obj_name]["enable"])
        button_config = self.add_config_button()

        layout_item = QHBoxLayout()
        layout_item.setContentsMargins(4,0,4,0)
        layout_item.addWidget(label_obj, stretch=1)
        layout_item.addWidget(button_config)
        layout_item.addWidget(button_toggle)
        layout_item.setSpacing(4)

        self.setStyleSheet("font-size: 16px;")
        self.setLayout(layout_item)

    def add_toggle_button(self, obj_name, state):
        """Add toggle button"""
        button = QPushButton("")
        button.setCheckable(True)
        button.setChecked(state)
        self.set_toggle_state(state, button)
        button.toggled.connect(
            lambda checked=state: self.set_toggle_state(checked, button, obj_name))
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

    def set_toggle_state(self, checked, button, obj_name=None):
        """Set toggle state"""
        self.master.toggle_control(obj_name)
        button.setText("ON" if checked else "OFF")

    def open_config_dialog(self):
        """Config dialog"""
        _dialog = UserConfig(self.master, self.obj_name, self.master.module_type)
        _dialog.open()
