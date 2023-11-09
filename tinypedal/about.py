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
About window
"""

import os

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from .const import APP_NAME, VERSION, APP_ICON

COPYRIGHT = "Copyright (C) 2022-2023 Xiang"
DESCRIPTION = "An open-source overlay application for racing simulation."
LICENSE = "Licensed under the GNU General Public License v3.0 or later."


class About(QWidget):
    """Create about window

    Hide window at startup.
    """

    def __init__(self, hideonclose=False):
        super().__init__()
        self.hideonclose = hideonclose

        # Base setting
        self.setFixedWidth(226)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setWindowTitle("About")

        # Logo
        logo_image = QPixmap(APP_ICON)
        logo_image = logo_image.scaled(64,64, mode=Qt.SmoothTransformation)
        label_logo = QLabel(self)
        label_logo.setPixmap(logo_image)
        label_logo.setFixedSize(74,74)
        label_logo.setStyleSheet("padding: 5px 0 5px 10px;")

        # Title
        label_title = QLabel(APP_NAME)
        label_title.setAlignment(Qt.AlignLeft)
        label_title.setStyleSheet("padding: 12px 0 0 3px; font-size: 20px;")
        label_title.setFixedHeight(34)

        label_version = QLabel(f"Version: {VERSION}")
        label_version.setAlignment(Qt.AlignLeft)
        label_version.setStyleSheet("padding: 0 0 0 6px; font-size: 11px;")
        label_version.setFixedHeight(30)

        # Description
        label_desc = QLabel(f"<p>{COPYRIGHT}</p><p>{DESCRIPTION}</p><p>{LICENSE}</p>")
        label_desc.setWordWrap(True)
        label_desc.setStyleSheet("padding: 5px; font-size: 11px;")

        # Add button
        button_lic = QPushButton("License")
        button_lic.setStyleSheet("padding: 4px 6px")
        button_lic.clicked.connect(self.open_license_text)

        button_3rd = QPushButton("Third-Party Notices")
        button_3rd.setStyleSheet("padding: 4px 6px")
        button_3rd.clicked.connect(self.open_thirdparty_text)

        # Create layout
        layout_main = QVBoxLayout()
        layout_logo = QHBoxLayout()
        layout_title = QVBoxLayout()
        layout_button = QHBoxLayout()
        layout_button.setContentsMargins(5,5,5,5)

        # Add to layout
        layout_title.addWidget(label_title)
        layout_title.addWidget(label_version)

        layout_logo.addWidget(label_logo)
        layout_logo.addLayout(layout_title)

        layout_button.addWidget(button_lic, stretch=1)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_3rd, stretch=2)

        layout_main.addLayout(layout_logo)
        layout_main.addWidget(label_desc)
        layout_main.addLayout(layout_button)
        #layout_main.setSpacing(0)

        self.setLayout(layout_main)

    @staticmethod
    def open_license_text():
        """Open LICENSE file"""
        os.startfile("LICENSE.txt")

    @staticmethod
    def open_thirdparty_text():
        """Open THIRDPARTYNOTICES file"""
        os.startfile("docs\\licenses\\THIRDPARTYNOTICES.txt")

    def closeEvent(self, event):
        """Minimize to tray"""
        if self.hideonclose:
            event.ignore()
            self.hide()
