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
Log window
"""

from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QTextCursor
from PySide2.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QDialogButtonBox,
    QTextBrowser,
    QPushButton,
)

from ..const import APP_NAME, APP_ICON
from .. import log_stream


class LogInfo(QDialog):
    """Create log info dialog"""

    def __init__(self, master):
        super().__init__(master)
        # Base setting
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setWindowTitle(f"{APP_NAME} Log")
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Text view
        self.log_view = QTextBrowser()
        self.log_view.setStyleSheet("font-size: 12px;")
        self.log_view.setMinimumSize(550, 300)
        self.refresh_log()

        # Button
        button_refresh = QPushButton("Refresh")
        button_refresh.clicked.connect(self.refresh_log)
        button_clear = QPushButton("Clear")
        button_clear.clicked.connect(self.clear_log)
        button_close = QDialogButtonBox(QDialogButtonBox.Close)
        button_close.rejected.connect(self.reject)

        # Layout
        layout_button = QHBoxLayout()
        layout_button.addWidget(button_refresh)
        layout_button.addWidget(button_clear)
        layout_button.addWidget(button_close)
        layout_button.setContentsMargins(5,5,5,5)

        layout_main = QVBoxLayout()
        layout_main.addWidget(self.log_view)
        layout_main.addLayout(layout_button)
        layout_main.setContentsMargins(3,3,3,7)
        self.setLayout(layout_main)

    def refresh_log(self):
        """Refresh log"""
        self.log_view.setText(log_stream.getvalue())
        self.log_view.moveCursor(QTextCursor.End)

    def clear_log(self):
        """Clear log"""
        log_stream.truncate(0)
        log_stream.seek(0)
        self.refresh_log()
