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
Preset list view
"""

import os
import shutil
import time

from PySide2.QtCore import Qt, QRegularExpression
from PySide2.QtGui import QIcon, QRegularExpressionValidator
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QMenu,
    QListWidget,
    QMessageBox,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
)

from ..const import APP_ICON, PATH_SETTINGS
from ..setting import cfg
from .. import formatter as fmt
from .. import regex_pattern as rxp
from .. import validator as val

# Option validator
preset_name_valid = QRegularExpressionValidator(QRegularExpression('[^\\\\/:*?"<>|]*'))


class PresetList(QWidget):
    """Preset list view"""

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
            "QListView::item:selected {selection-color: #FFF;background: #F20;}"
        )
        self.refresh_list()
        self.listbox_preset.setCurrentRow(0)
        self.listbox_preset.itemDoubleClicked.connect(self.load_preset)

        # Button
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)

        button_refresh = QPushButton("Refresh")
        button_refresh.clicked.connect(self.refresh_list)

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

    def refresh_list(self):
        """Refresh preset list"""
        temp_list = cfg.load_preset_list()
        if temp_list != self.preset_list:
            self.preset_list = temp_list
            self.listbox_preset.clear()
            self.listbox_preset.addItems(self.preset_list)
        self.label_loaded.setText(
            f"Loaded: <b>{cfg.filename.last_setting[:-5]}</b>")

    def load_preset(self):
        """Load selected preset"""
        selected_index = self.listbox_preset.currentRow()
        if selected_index >= 0:
            cfg.filename.setting = f"{self.preset_list[selected_index]}.json"
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
                    buttons=QMessageBox.Yes | QMessageBox.No)

                if delete_msg == QMessageBox.Yes:
                    if os.path.exists(f"{PATH_SETTINGS}{selected_filename}"):
                        os.remove(f"{PATH_SETTINGS}{selected_filename}")
                    self.refresh_list()


class CreatePreset(QDialog):
    """Create preset"""

    def __init__(self, master, title: str = "", mode: str = "", src_filename: str = ""):
        """Initialize create preset dialog setting

        Args:
            title: Dialog title string.
            mode: Edit mode, either "duplicate", "rename", or "" for new preset.
            src_filename: Source setting filename.
        """
        super().__init__(master)
        self.master = master
        self.edit_mode = mode
        self.src_filename = src_filename

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setFixedWidth(280)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Entry box
        self.preset_entry = QLineEdit()
        self.preset_entry.setMaxLength(40)
        self.preset_entry.setPlaceholderText("Enter a new preset name")
        self.preset_entry.setValidator(preset_name_valid)

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

    def __saving(self, entered_filename: str):
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
            self.master.refresh_list()
        # Rename preset
        elif self.edit_mode == "rename":
            os.rename(
                f"{PATH_SETTINGS}{self.src_filename}",
                f"{PATH_SETTINGS}{entered_filename}.json"
            )
            # Reload if renamed file was loaded
            if cfg.filename.setting == self.src_filename:
                cfg.filename.setting = f"{entered_filename}.json"
                self.master.master.reload_preset()
            else:
                self.master.refresh_list()
        # Create new preset
        else:
            cfg.filename.setting = f"{entered_filename}.json"
            cfg.create()
            cfg.save(0)  # save setting
            while cfg.is_saving:  # wait saving finish
                time.sleep(0.01)
            self.master.refresh_list()
        # Close window
        self.accept()
        return None
