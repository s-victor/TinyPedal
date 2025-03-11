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
Brake editor
"""

import logging
import time

from PySide2.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QComboBox,
)

from ..api_control import api
from ..setting import FileType, cfg, copy_setting
from ..module_control import wctrl
from ..heatmap import set_predefined_brake_name, HEATMAP_DEFAULT_BRAKE
from ._common import (
    BaseEditor,
    #TableBatchReplace,
    QTableFloatItem,
    QSS_EDITOR_BUTTON,
)

HEADER_BRAKES = "Brake name","Failure Thickness (mm)","Heatmap name"

logger = logging.getLogger(__name__)


class BrakeEditor(BaseEditor):
    """Brake editor"""

    def __init__(self, master):
        super().__init__(master)
        self.set_utility_title("Brake Editor")
        self.setMinimumSize(600, 500)

        self.brakes_temp = copy_setting(cfg.user.brakes)

        # Set table
        self.table_brakes = QTableWidget(self)
        self.table_brakes.setColumnCount(len(HEADER_BRAKES))
        self.table_brakes.setHorizontalHeaderLabels(HEADER_BRAKES)
        self.table_brakes.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.table_brakes.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        font_w = self.fontMetrics().averageCharWidth()
        self.table_brakes.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.table_brakes.setColumnWidth(2, font_w * 26)
        self.table_brakes.cellChanged.connect(self.verify_input)
        self.refresh_table()
        self.set_unmodified()

        # Set button
        layout_button = self.set_layout_button()

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.table_brakes)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def set_layout_button(self):
        """Set button layout"""
        button_add = QPushButton("Add")
        button_add.clicked.connect(self.add_brake)
        button_add.setStyleSheet(QSS_EDITOR_BUTTON)

        button_sort = QPushButton("Sort")
        button_sort.clicked.connect(self.sort_brake)
        button_sort.setStyleSheet(QSS_EDITOR_BUTTON)

        button_delete = QPushButton("Delete")
        button_delete.clicked.connect(self.delete_brake)
        button_delete.setStyleSheet(QSS_EDITOR_BUTTON)

        #button_replace = QPushButton("Replace")
        #button_replace.clicked.connect(self.open_replace_dialog)
        #button_replace.setStyleSheet(QSS_EDITOR_BUTTON)

        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_setting)
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
        layout_button = QHBoxLayout()
        layout_button.addWidget(button_add)
        layout_button.addWidget(button_sort)
        layout_button.addWidget(button_delete)
        #layout_button.addWidget(button_replace)
        layout_button.addWidget(button_reset)
        layout_button.addStretch(1)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)
        return layout_button

    def refresh_table(self):
        """Refresh brakes list"""
        self.table_brakes.setRowCount(0)
        row_index = 0
        for class_name, brake_data in self.brakes_temp.items():
            self.add_brake_entry(
                row_index,
                class_name,
                brake_data["failure_thickness"],
                brake_data["heatmap"],
            )
            row_index += 1

    def __add_option_combolist(self, key):
        """Combo droplist string"""
        combo_edit = QComboBox()
        combo_edit.addItems(cfg.user.heatmap.keys())
        combo_edit.setCurrentText(key)
        combo_edit.currentTextChanged.connect(self.set_modified)
        return combo_edit

    #def open_replace_dialog(self):
    #    """Open replace dialog"""
    #    selector = {HEADER_BRAKES[0]: 0}
    #    _dialog = TableBatchReplace(self, selector, self.table_brakes)
    #    _dialog.open()

    def add_brake(self):
        """Add new brake"""
        start_index = row_index = self.table_brakes.rowCount()
        # Add all missing vehicle name from active session
        veh_total = api.read.vehicle.total_vehicles()
        for index in range(veh_total):
            class_name = api.read.vehicle.class_name(index)
            brake_names = (
                set_predefined_brake_name(class_name, True),
                set_predefined_brake_name(class_name, False),
            )
            for brake in brake_names:
                if not self.is_value_in_table(brake, self.table_brakes):
                    self.add_brake_entry(row_index, brake, 0)
                    self.table_brakes.setCurrentCell(row_index, 0)
                    row_index += 1
        # Add new name entry
        if start_index == row_index:
            new_class_name = self.new_name_increment("New Brake Name", self.table_brakes)
            self.add_brake_entry(row_index, new_class_name, 0)
            self.table_brakes.setCurrentCell(row_index, 0)

    def add_brake_entry(
        self, row_index: int, class_name: str, failure_thickness: float,
        heatmap_name: str = HEATMAP_DEFAULT_BRAKE):
        """Add new brake entry to table"""
        self.table_brakes.insertRow(row_index)
        self.table_brakes.setItem(row_index, 0, QTableWidgetItem(class_name))
        self.table_brakes.setItem(row_index, 1, QTableFloatItem(failure_thickness))
        self.table_brakes.setCellWidget(row_index, 2, self.__add_option_combolist(heatmap_name))

    def sort_brake(self):
        """Sort brakes in ascending order"""
        if self.table_brakes.rowCount() > 1:
            self.table_brakes.sortItems(0)
            self.set_modified()

    def delete_brake(self):
        """Delete brake entry"""
        selected_rows = set(data.row() for data in self.table_brakes.selectedIndexes())
        if not selected_rows:
            QMessageBox.warning(self, "Error", "No data selected.")
            return

        if not self.confirm_operation(message="<b>Delete selected rows?</b>"):
            return

        for row_index in sorted(selected_rows, reverse=True):
            self.table_brakes.removeRow(row_index)
        self.set_modified()

    def reset_setting(self):
        """Reset setting"""
        msg_text = (
            "Are you sure you want to reset brake preset to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(message=msg_text):
            self.brakes_temp = copy_setting(cfg.default.brakes)
            self.set_modified()
            self.refresh_table()

    def applying(self):
        """Save & apply"""
        self.save_setting()

    def saving(self):
        """Save & close"""
        self.save_setting()
        self.accept()  # close

    def verify_input(self, row_index: int, column_index: int):
        """Verify input value"""
        self.set_modified()
        item = self.table_brakes.item(row_index, column_index)
        if column_index == 1:  # failure thickness column
            item.validate()

    def update_brakes_temp(self):
        """Update temporary changes to brakes temp first"""
        self.brakes_temp.clear()
        for index in range(self.table_brakes.rowCount()):
            class_name = self.table_brakes.item(index, 0).text()
            failure_thickness = self.table_brakes.item(index, 1).value()
            heatmap_name = self.table_brakes.cellWidget(index, 2).currentText()
            self.brakes_temp[class_name] = {
                "failure_thickness": failure_thickness,
                "heatmap": heatmap_name,
            }

    def save_setting(self):
        """Save setting"""
        self.update_brakes_temp()
        cfg.user.brakes = copy_setting(self.brakes_temp)
        cfg.save(0, filetype=FileType.BRAKES)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        wctrl.reload()
        self.set_unmodified()
