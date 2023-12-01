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
About window
"""

import logging

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QPixmap
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextBrowser,
)

from .const import APP_NAME, VERSION, APP_ICON, COPYRIGHT, DESCRIPTION, LICENSE

logger = logging.getLogger(__name__)


class About(QWidget):
    """Create about window

    Hide window at startup.
    """

    def __init__(self, hideonclose=False):
        super().__init__()
        self.hideonclose = hideonclose

        # Base setting
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setWindowTitle(f"About {APP_NAME}")

        # Logo
        icon_size = 100
        logo_image = QPixmap(APP_ICON)
        logo_image = logo_image.scaled(icon_size,icon_size, mode=Qt.SmoothTransformation)

        label_logo = QLabel(self)
        label_logo.setPixmap(logo_image)
        label_logo.setFixedSize(icon_size+10,icon_size+10)
        label_logo.setStyleSheet("padding: 5px;")

        # Description
        label_name = QLabel(f"{APP_NAME}  v{VERSION}")
        label_name.setStyleSheet("font-size: 16px;padding:5px 0 2px 0;")

        label_desc = QLabel(f"<p>{COPYRIGHT}</p><p>{DESCRIPTION}</p><p>{LICENSE}</p>")
        label_desc.setStyleSheet("font-size: 11px;padding:2px 0 10px 0;")

        self._last_text = None
        self._lics_text = ""
        self._thrd_text = ""
        self._ctrb_text = ""
        self.load_text_files()

        # Add button
        button_ctrb = QPushButton("Contributors")
        button_ctrb.clicked.connect(self.open_contributors_text)

        button_lics = QPushButton("License")
        button_lics.clicked.connect(self.open_license_text)

        button_thrd = QPushButton("Third-Party Notices")
        button_thrd.clicked.connect(self.open_thirdparty_text)

        # Text view box
        self.text_view = QTextBrowser(self)
        self.text_view.setStyleSheet("font-size: 11px;")
        self.text_view.setMinimumHeight(300)
        self.text_view.hide()

        # Create layout
        layout_main = QVBoxLayout()
        layout_title = QVBoxLayout()
        layout_about = QHBoxLayout()
        layout_button = QHBoxLayout()
        #layout_button.setContentsMargins(5,5,5,5)

        # Add to layout
        layout_title.addWidget(label_name)
        layout_title.addWidget(label_desc)

        layout_about.addWidget(label_logo)
        layout_about.addLayout(layout_title)
        layout_about.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        layout_button.addWidget(button_lics)
        layout_button.addWidget(button_thrd)
        #layout_button.addStretch(stretch=1)
        layout_button.addWidget(button_ctrb)

        layout_main.addLayout(layout_about)
        layout_main.addLayout(layout_button)
        layout_main.addWidget(self.text_view)
        #layout_main.setSpacing(0)

        self.setLayout(layout_main)
        self.setFixedWidth(self.sizeHint().width())

    def load_text_files(self):
        """Load text file"""
        try:
            with open("LICENSE.txt", "r", encoding="utf-8") as text_file:
                self._lics_text = text_file.read()
            with open("docs\\licenses\\THIRDPARTYNOTICES.txt", "r", encoding="utf-8") as text_file:
                self._thrd_text = text_file.read()
            with open("docs\\contributors.md", "r", encoding="utf-8") as text_file:
                self._ctrb_text = text_file.read()
        except FileNotFoundError:
            logger.error("file not found")

    def open_license_text(self):
        """Open LICENSE file"""
        self.set_text_view(self._lics_text, "licence")

    def open_thirdparty_text(self):
        """Open THIRDPARTYNOTICES file"""
        self.set_text_view(self._thrd_text, "notices")

    def open_contributors_text(self):
        """Open CONTRIBUTORS file"""
        self.set_text_view(self._ctrb_text, "contributors")

    def set_text_view(self, text, name):
        """Set text"""
        if self._last_text != name or not self.text_view.isVisible():
            self._last_text = name
            self.text_view.setText(text)
            self.text_view.show()
        else:
            self.text_view.hide()
            self.adjustSize()

    def closeEvent(self, event):
        """Minimize to tray"""
        if self.hideonclose:
            event.ignore()
            self.text_view.hide()
            self.adjustSize()
            self.hide()
