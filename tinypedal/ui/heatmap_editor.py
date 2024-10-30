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
Heatmap editor
"""

import time

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QDialogButtonBox,
    QComboBox,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)

from ..setting import cfg, copy_setting
from ..module_control import wctrl
from ._common import (
    BaseDialog,
    BaseEditor,
    BatchOffset,
    DoubleClickEdit,
    QVAL_INTEGER,
    QVAL_COLOR,
    QVAL_HEATMAP,
    QSS_EDITOR_BUTTON,
    QSS_EDITOR_LISTBOX,
    update_preview_color,
)


class HeatmapEditor(BaseEditor):
    """Heatmap editor"""

    def __init__(self, master):
        super().__init__(master)
        self.setWindowTitle(f"Heatmap Editor - {cfg.filename.heatmap}")
        self.setMinimumHeight(400)

        self.option_heatmap = []
        self.heatmap_temp = copy_setting(cfg.user.heatmap)
        self.selected_heatmap_name = "tyre_default"
        self.selected_heatmap = self.heatmap_temp[self.selected_heatmap_name]

        # Preset selector
        self.heatmap_list = QComboBox()
        self.heatmap_list.addItems(self.heatmap_temp.keys())
        self.heatmap_list.currentIndexChanged.connect(self.select_heatmap)

        # Heatmap list box
        self.listbox_heatmap = QListWidget(self)
        self.listbox_heatmap.setStyleSheet(QSS_EDITOR_LISTBOX)
        self.refresh_list()

        # Button
        button_create = QPushButton("New")
        button_create.clicked.connect(self.open_create_dialog)
        button_create.setFixedWidth(self.fontMetrics().boundingRect("New").width() + 12)

        button_copy = QPushButton("Copy")
        button_copy.clicked.connect(self.open_copy_dialog)
        button_copy.setFixedWidth(self.fontMetrics().boundingRect("Copy").width() + 12)

        button_delete = QPushButton("Delete")
        button_delete.clicked.connect(self.delete_heatmap)
        button_delete.setFixedWidth(self.fontMetrics().boundingRect("Delete").width() + 12)

        button_add = QPushButton("Add")
        button_add.clicked.connect(self.add_temperature)
        button_add.setStyleSheet(QSS_EDITOR_BUTTON)

        button_sort = QPushButton("Sort")
        button_sort.clicked.connect(self.sorting)
        button_sort.setStyleSheet(QSS_EDITOR_BUTTON)

        button_offset = QPushButton("Offset")
        button_offset.clicked.connect(self.open_offset_dialog)
        button_offset.setStyleSheet(QSS_EDITOR_BUTTON)

        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_heatmap)
        button_reset.setStyleSheet(QSS_EDITOR_BUTTON)

        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)
        button_apply.setStyleSheet(QSS_EDITOR_BUTTON)

        button_save = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Close)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.close)
        button_save.setStyleSheet(QSS_EDITOR_BUTTON)

        # Set layout
        layout_main = QVBoxLayout()
        layout_selector = QHBoxLayout()
        layout_button = QHBoxLayout()

        layout_selector.addWidget(self.heatmap_list)
        layout_selector.addWidget(button_create)
        layout_selector.addWidget(button_copy)
        layout_selector.addWidget(button_delete)

        layout_button.addWidget(button_add)
        layout_button.addWidget(button_sort)
        layout_button.addWidget(button_offset)
        layout_button.addWidget(button_reset)
        layout_button.addStretch(1)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)

        layout_main.addLayout(layout_selector)
        layout_main.addWidget(self.listbox_heatmap)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setMinimumWidth(self.sizeHint().width() + 20)

    def refresh_list(self):
        """Refresh temperature list"""
        self.listbox_heatmap.clear()
        self.option_heatmap.clear()
        already_modified = self.is_modified()
        row_index = 0

        for key, item in self.selected_heatmap.items():
            layout_item = QHBoxLayout()
            layout_item.setContentsMargins(4,4,4,4)
            layout_item.setSpacing(4)

            temperature_edit = self.__add_option_temperature(key, layout_item)
            color_edit = self.__add_option_color(item, layout_item, 100)
            self.__add_delete_button(row_index, layout_item)
            self.option_heatmap.append((temperature_edit, color_edit))
            row_index += 1

            heatmap_item = QWidget()
            heatmap_item.setLayout(layout_item)
            item = QListWidgetItem()
            self.listbox_heatmap.addItem(item)
            self.listbox_heatmap.setItemWidget(item, heatmap_item)

        if not already_modified:
            self.set_unmodified()

    def __add_option_temperature(self, key, layout):
        """Temperature integer"""
        line_edit = QLineEdit()
        line_edit.setValidator(QVAL_INTEGER)
        line_edit.textChanged.connect(self.set_modified)
        # Load selected option
        line_edit.setText(key)
        # Add layout
        layout.addWidget(line_edit)
        return line_edit

    def __add_option_color(self, key, layout, width):
        """Color string"""
        color_edit = DoubleClickEdit(mode="color", init=key)
        color_edit.setFixedWidth(width)
        color_edit.setMaxLength(9)
        color_edit.setValidator(QVAL_COLOR)
        color_edit.textChanged.connect(self.set_modified)
        color_edit.textChanged.connect(
            lambda color_str, option=color_edit:
            update_preview_color(color_str, option))
        # Load selected option
        color_edit.setText(key)
        # Add layout
        layout.addWidget(color_edit)
        return color_edit

    def __add_delete_button(self, idx, layout):
        """Delete button"""
        button = QPushButton("X")
        button.setFixedWidth(20)
        button.pressed.connect(
            lambda index=idx: self.delete_temperature(index))
        layout.addWidget(button)

    def open_create_dialog(self):
        """Create heatmap preset"""
        _dialog = CreateHeatmapPreset(self, "Create Heatmap Preset")
        _dialog.open()

    def open_copy_dialog(self):
        """Copy heatmap preset"""
        _dialog = CreateHeatmapPreset(self, "Duplicate Heatmap Preset", "duplicate")
        _dialog.open()

    def open_offset_dialog(self):
        """Open offset dialog"""
        self.sort_temperature()
        _dialog = BatchOffset(self, self.set_batch_offset)
        _dialog.config(0, 1, -99999, 99999)
        _dialog.open()

    def set_batch_offset(self, offset):
        """Set batch offset"""
        for edit in self.option_heatmap:
            edit[0].setText(str(int(edit[0].text()) + offset))
        self.update_heatmap()
        self.set_modified()
        self.refresh_list()

    def add_temperature(self):
        """Add new temperature"""
        self.sort_temperature()
        if self.selected_heatmap:
            last_key = str(int(list(self.selected_heatmap.keys())[-1]) + 10)
            self.selected_heatmap[last_key] = "#FFFFFF"
        else:
            self.selected_heatmap["-273"] = "#4444FF"
        self.set_modified()
        self.refresh_list()
        # Move focus to new heatmap row
        self.listbox_heatmap.setCurrentRow(len(self.selected_heatmap) - 1)

    def delete_temperature(self, index):
        """Delete temperature entry"""
        target = self.option_heatmap[index][0].text()
        if not self.confirm_deletion(f"Delete temperature '{target}' ?"):
            return

        self.update_heatmap()
        self.selected_heatmap.pop(target)
        self.set_modified()
        self.refresh_list()

    def sort_temperature(self):
        """Sort temperature"""
        self.update_heatmap()
        self.selected_heatmap = dict(
            sorted(self.selected_heatmap.items(), key=lambda keys: int(keys[0])))

    def select_heatmap(self):
        """Select heatmap list"""
        # Sort & apply previous preset first
        if self.selected_heatmap:
            self.sort_temperature()
            self.heatmap_temp[self.selected_heatmap_name] = self.selected_heatmap
        # Get newly selected preset name
        self.selected_heatmap_name = self.heatmap_list.currentText()
        self.selected_heatmap = self.heatmap_temp[self.selected_heatmap_name]
        self.refresh_list()

    def delete_heatmap(self):
        """Delete heatmap"""
        if self.selected_heatmap_name in cfg.default.heatmap:
            message_text = (
                "Cannot delete built-in heatmap preset."
            )
            QMessageBox.warning(self, "Error", message_text)
            return None

        message_text = (
            "Are you sure you want to delete selected heatmap preset? <br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        delete_msg = QMessageBox.question(
            self, "Delete Heatmap Preset", message_text,
            buttons=QMessageBox.Yes | QMessageBox.No)
        if delete_msg == QMessageBox.Yes:
            self.heatmap_temp.pop(self.selected_heatmap_name)  # remove from dict
            self.selected_heatmap.clear()
            self.heatmap_list.removeItem(self.heatmap_list.currentIndex())
            self.set_modified()
        return None

    def reset_heatmap(self):
        """Reset heatmap"""
        if cfg.default.heatmap.get(self.selected_heatmap_name, None) is None:
            message_text = (
                "Cannot reset selected heatmap preset. <br><br>"
                "Default preset does not exist."
            )
            QMessageBox.warning(self, "Error", message_text)
            return None

        message_text = (
            "Are you sure you want to reset selected heatmap preset to default? <br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        reset_msg = QMessageBox.question(
            self, "Reset Heatmap Preset", message_text,
            buttons=QMessageBox.Yes | QMessageBox.No)
        if reset_msg == QMessageBox.Yes:
            self.selected_heatmap = cfg.default.heatmap[self.selected_heatmap_name].copy()
            self.set_modified()
            self.refresh_list()
        return None

    def applying(self):
        """Save & apply"""
        self.save_heatmap()

    def saving(self):
        """Save & close"""
        self.save_heatmap()
        self.accept()  # close

    def sorting(self):
        """Sort & refresh"""
        self.sort_temperature()
        self.set_modified()
        self.refresh_list()

    def update_heatmap(self):
        """Update temporary changes to selected heatmap first"""
        self.selected_heatmap.clear()
        for edit in self.option_heatmap:
            key_name = edit[0].text()
            item_name = edit[1].text()
            self.selected_heatmap[key_name] = item_name

    def save_heatmap(self):
        """Save heatmap"""
        self.update_heatmap()
        self.refresh_list()
        # Apply changes to heatmap preset dictionary
        self.heatmap_temp[self.selected_heatmap_name] = self.selected_heatmap
        cfg.user.heatmap = copy_setting(self.heatmap_temp)
        cfg.save(0, "heatmap")
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        wctrl.reload()
        self.set_unmodified()


class CreateHeatmapPreset(BaseDialog):
    """Create heatmap preset

    Args:
        title: Dialog title string.
        mode: Edit mode, either "duplicate" or "" for new preset.
    """

    def __init__(self, master, title: str = "", mode: str = ""):
        super().__init__(master)
        self.master = master
        self.edit_mode = mode
        self.setWindowTitle(title)
        self.setFixedWidth(280)

        # Entry box
        self.preset_entry = QLineEdit()
        self.preset_entry.setMaxLength(40)
        self.preset_entry.setPlaceholderText("Enter a new preset name")
        self.preset_entry.setValidator(QVAL_HEATMAP)

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
        entered_name = self.preset_entry.text()
        if not entered_name:
            QMessageBox.warning(self, "Error", "Invalid preset name.")
        elif entered_name in cfg.user.heatmap:
            QMessageBox.warning(self, "Error", "Preset already exists.")
        else:
            self.__saving(entered_name)

    def __saving(self, entered_name: str):
        """Saving new preset"""
        # Duplicate preset
        if self.edit_mode == "duplicate":
            self.master.heatmap_temp[entered_name] = self.master.selected_heatmap.copy()
        # Create new preset
        else:
            self.master.heatmap_temp[entered_name] = {"-273": "#4444FF"}
        self.master.heatmap_list.addItem(entered_name)
        self.master.heatmap_list.setCurrentText(entered_name)
        self.master.set_modified()
        # Close window
        self.accept()
