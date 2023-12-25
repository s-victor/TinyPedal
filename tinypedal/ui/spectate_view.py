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
Spectate list view
"""

from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
)

from ..setting import cfg
from ..api_control import api


class SpectateList(QWidget):
    """Spectate list view"""

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
        self.button_refresh.clicked.connect(self.refresh_list)

        self.button_toggle = QPushButton("")
        self.button_toggle.setCheckable(True)
        self.button_toggle.clicked.connect(self.spectate_toggle_state)
        self.refresh_list()

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
        self.refresh_list()

    def refresh_list(self):
        """Refresh spectate list"""
        if cfg.shared_memory_api["enable_player_index_override"]:
            temp_list = ["Anonymous", *self.driver_list()]
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
        self.refresh_list()
        cfg.save()  # save only if selected

    @staticmethod
    def driver_list():
        """Create driver list"""
        return [api.read.vehicle.driver_name(index)
                for index in range(api.read.vehicle.total_vehicles())]
