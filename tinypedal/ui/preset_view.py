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
Preset list view
"""

import os
import shutil
import time

from PySide2.QtCore import QPoint, Qt
from PySide2.QtWidgets import (
    QCheckBox,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .. import regex_pattern as rxp
from ..const_app import VERSION
from ..const_file import FileExt
from ..formatter import strip_filename_extension
from ..setting import ConfigType, cfg
from ..validator import is_allowed_filename
from ._common import FONT_BASE_SIZE_POINT, QVAL_FILENAME, BaseDialog, ui_scale

QSS_LISTBOX = (
    f"QListView {{font-size: {FONT_BASE_SIZE_POINT * 1.2}pt;outline: none;}}"
    "QListView::item {height: 1.75em;border-radius: 0;padding: 0 0.25em;}"
    "QListView::item:selected {selection-color: #FFF;background: #F20;}"
)
QSS_TAGGED_ITEM = (
    f"font-size: {FONT_BASE_SIZE_POINT * 1.05}pt;"
    "color: #FFF;margin: 0.25em 0 0.25em 0.25em;border-radius: 0.2em;"
)
QSS_TAGGED_STYLE = {
    "LMU": "background: #F20;",
    "RF2": "background: #0AF;",
    "LOCKED": "background: #888;",
}


class PresetList(QWidget):
    """Preset list view"""

    def __init__(self, parent):
        super().__init__(parent)
        self.reload_preset = parent.reload_preset
        self.preset_list = []

        # Label
        self.label_loaded = QLabel("")

        # Button
        button_load = QPushButton("Load")
        button_load.clicked.connect(self.load_preset)

        button_refresh = QPushButton("Refresh")
        button_refresh.clicked.connect(self.refresh_list)

        button_create = QPushButton("New Preset")
        button_create.clicked.connect(self.open_create_preset)

        # Check box
        self.checkbox_autoload = QCheckBox("Auto Load Primary Preset")
        self.checkbox_autoload.setChecked(cfg.application["enable_auto_load_preset"])
        self.checkbox_autoload.toggled.connect(self.toggle_autoload)

        # List box
        self.listbox_preset = QListWidget(self)
        self.listbox_preset.setAlternatingRowColors(True)
        self.listbox_preset.setStyleSheet(QSS_LISTBOX)
        self.listbox_preset.itemDoubleClicked.connect(self.load_preset)
        self.refresh_list()

        # Layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.label_loaded)
        layout_main.addWidget(self.listbox_preset)
        layout_main.addWidget(self.checkbox_autoload)
        layout_button.addWidget(button_load)
        layout_button.addWidget(button_refresh)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_create)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

        self.listbox_preset.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listbox_preset.customContextMenuRequested.connect(self.open_context_menu)

    def refresh_list(self):
        """Refresh preset list"""
        self.preset_list = cfg.preset_list
        self.listbox_preset.clear()

        for preset_name in self.preset_list:
            # Add preset name
            item = QListWidgetItem()
            item.setText(preset_name)
            self.listbox_preset.addItem(item)
            # Add primary preset tag
            label_item = PrimaryPresetTag(self, preset_name)
            self.listbox_preset.setItemWidget(item, label_item)

        loaded_preset = cfg.filename.last_setting
        locked_tag = " (locked)" if loaded_preset in cfg.user.filelock else ""
        self.label_loaded.setText(f"Loaded: <b>{loaded_preset[:-5]}{locked_tag}</b>")
        self.checkbox_autoload.setChecked(cfg.application["enable_auto_load_preset"])

    def load_preset(self):
        """Load selected preset"""
        selected_index = self.listbox_preset.currentRow()
        if selected_index >= 0:
            cfg.filename.setting = f"{self.preset_list[selected_index]}{FileExt.JSON}"
            self.reload_preset()
        else:
            QMessageBox.warning(
                self, "Error",
                "No preset selected.\nPlease select a preset to continue.")

    def open_create_preset(self):
        """Create new preset"""
        _dialog = CreatePreset(self, title="Create new default preset")
        _dialog.open()

    @staticmethod
    def toggle_autoload(checked: bool):
        """Toggle auto load preset"""
        cfg.application["enable_auto_load_preset"] = checked
        cfg.save(cfg_type=ConfigType.CONFIG)

    def open_context_menu(self, position: QPoint):
        """Open context menu"""
        if not self.listbox_preset.itemAt(position):
            return

        selected_index = self.listbox_preset.currentRow()
        selected_preset_name = self.preset_list[selected_index]
        selected_filename = f"{selected_preset_name}{FileExt.JSON}"
        is_locked = (selected_filename in cfg.user.filelock)

        # Create context menu
        menu = QMenu()  # no parent for temp menu
        menu.addAction("Unlock Preset" if is_locked else "Lock Preset")
        menu.addSeparator()
        menu.addAction("Set Primary for LMU")
        menu.addAction("Set Primary for RF2")
        menu.addAction("Clear Primary Tag")
        menu.addSeparator()
        menu.addAction("Duplicate")
        if not is_locked:
            menu.addAction("Rename")
            menu.addAction("Delete")

        selected_action = menu.exec_(self.listbox_preset.mapToGlobal(position))
        if not selected_action:
            return
        action = selected_action.text()

        # Set primary preset LMU
        if action == "Set Primary for LMU":
            cfg.primary_preset["LMU"] = selected_preset_name
            cfg.save(cfg_type=ConfigType.CONFIG)
            self.refresh_list()
        # Set primary preset RF2
        elif action == "Set Primary for RF2":
            cfg.primary_preset["RF2"] = selected_preset_name
            cfg.save(cfg_type=ConfigType.CONFIG)
            self.refresh_list()
        # Clear primary preset tag
        elif action == "Clear Primary Tag":
            tag_found = False
            for sim_name, primary_preset in cfg.primary_preset.items():
                if selected_preset_name == primary_preset:
                    cfg.primary_preset[sim_name] = ""
                    tag_found = True
            if tag_found:
                cfg.save(cfg_type=ConfigType.CONFIG)
                self.refresh_list()
        # Lock/unlock preset
        elif action == "Lock Preset":
            msg_text = (
                f"Lock <b>{selected_filename}</b> preset?<br><br>"
                "Changes to locked preset will not be saved."
            )
            if self.confirm_operation(title="Lock Preset", message=msg_text):
                cfg.user.filelock[selected_filename] = {"version": VERSION}
                cfg.save(cfg_type=ConfigType.FILELOCK)
                self.refresh_list()
        elif action == "Unlock Preset":
            msg_text = f"Unlock <b>{selected_filename}</b> preset?"
            if self.confirm_operation(title="Unlock Preset", message=msg_text):
                if cfg.user.filelock.pop(selected_filename, None):
                    cfg.save(cfg_type=ConfigType.FILELOCK)
                self.refresh_list()
        # Duplicate preset
        elif action == "Duplicate":
            _dialog = CreatePreset(
                self,
                title="Duplicate Preset",
                mode="duplicate",
                source_filename=selected_filename
            )
            _dialog.open()
        # Rename preset
        elif action == "Rename":
            _dialog = CreatePreset(
                self,
                title="Rename Preset",
                mode="rename",
                source_filename=selected_filename
            )
            _dialog.open()
        # Delete preset
        elif action == "Delete":
            msg_text = (
                f"Delete <b>{selected_filename}</b> preset permanently?<br><br>"
                "This cannot be undone!"
            )
            if self.confirm_operation(title="Delete Preset", message=msg_text):
                if os.path.exists(f"{cfg.path.settings}{selected_filename}"):
                    os.remove(f"{cfg.path.settings}{selected_filename}")
                self.refresh_list()

    def confirm_operation(self, title: str = "Confirm", message: str = "") -> bool:
        """Confirm operation"""
        confirm = QMessageBox.question(
            self, title, message,
            buttons=QMessageBox.Yes | QMessageBox.No,
            defaultButton=QMessageBox.No,
        )
        return confirm == QMessageBox.Yes


class CreatePreset(BaseDialog):
    """Create preset"""

    def __init__(self, parent, title: str = "", mode: str = "", source_filename: str = ""):
        """Initialize create preset dialog setting

        Args:
            title: Dialog title string.
            mode: Edit mode, either "duplicate", "rename", or "" for new preset.
            source_filename: Source setting filename.
        """
        super().__init__(parent)
        self._parent = parent
        self.edit_mode = mode
        self.source_filename = source_filename

        self.setWindowTitle(title)
        self.setMinimumWidth(ui_scale(21))

        # Entry box
        self.preset_entry = QLineEdit()
        self.preset_entry.setMaxLength(40)
        self.preset_entry.setPlaceholderText("Enter a new preset name")
        self.preset_entry.setValidator(QVAL_FILENAME)

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
        entered_filename = strip_filename_extension(self.preset_entry.text(), FileExt.JSON)

        if is_allowed_filename(rxp.CFG_INVALID_FILENAME, entered_filename):
            self.__saving(cfg.path.settings, entered_filename, self.source_filename)
        else:
            QMessageBox.warning(self, "Error", "Invalid preset name.")

    def __saving(self, filepath: str, entered_filename: str, source_filename: str):
        """Saving new preset"""
        # Check existing preset
        temp_list = cfg.preset_list
        for preset in temp_list:
            if entered_filename.lower() == preset.lower():
                QMessageBox.warning(self, "Error", "Preset already exists.")
                return None
        # Duplicate preset
        if self.edit_mode == "duplicate":
            shutil.copy(
                f"{filepath}{source_filename}",
                f"{filepath}{entered_filename}{FileExt.JSON}"
            )
            self._parent.refresh_list()
        # Rename preset
        elif self.edit_mode == "rename":
            os.rename(
                f"{filepath}{source_filename}",
                f"{filepath}{entered_filename}{FileExt.JSON}"
            )
            # Reload if renamed file was loaded
            if cfg.filename.setting == source_filename:
                cfg.filename.setting = f"{entered_filename}{FileExt.JSON}"
                self._parent.reload_preset()
            else:
                self._parent.refresh_list()
        # Create new preset
        else:
            cfg.filename.setting = f"{entered_filename}{FileExt.JSON}"
            cfg.create()
            cfg.save(0)  # save setting
            while cfg.is_saving:  # wait saving finish
                time.sleep(0.01)
            self._parent.refresh_list()
        # Close window
        self.accept()
        return None


class PrimaryPresetTag(QWidget):
    """Primary preset tag"""

    def __init__(self, parent, preset_name: str):
        super().__init__(parent)
        layout_item = QHBoxLayout()
        layout_item.setContentsMargins(0, 0, 0, 0)
        layout_item.setSpacing(0)
        layout_item.addStretch(stretch=1)

        for sim_name, primary_preset in cfg.primary_preset.items():
            if preset_name == primary_preset:
                label_sim_name = QLabel(sim_name)
                label_sim_name.setStyleSheet(QSS_TAGGED_STYLE[sim_name])
                layout_item.addWidget(label_sim_name)

        preset_filename = f"{preset_name}{FileExt.JSON}"
        if preset_filename in cfg.user.filelock:
            label_locked = QLabel(f"{cfg.user.filelock[preset_filename]['version']}")
            label_locked.setStyleSheet(QSS_TAGGED_STYLE["LOCKED"])
            layout_item.addWidget(label_locked)

        self.setStyleSheet(QSS_TAGGED_ITEM)
        self.setLayout(layout_item)
