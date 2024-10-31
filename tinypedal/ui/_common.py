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
Common
"""

import os
from collections import deque

from PySide2.QtCore import Qt, QRegularExpression, QLocale
from PySide2.QtGui import (
    QIcon,
    QColor,
    QRegularExpressionValidator,
    QIntValidator,
    QDoubleValidator,
    qGray,
)
from PySide2.QtWidgets import (
    QLabel,
    QDialog,
    QMessageBox,
    QFileDialog,
    QLineEdit,
    QColorDialog,
    QDoubleSpinBox,
    QSpinBox,
    QDialogButtonBox,
    QHBoxLayout,
    QVBoxLayout,
)

from .. import validator as val
from ..const import APP_ICON

# Validator
QLOC_NUMBER = QLocale(QLocale.C)
QLOC_NUMBER.setNumberOptions(QLocale.RejectGroupSeparator)
QVAL_INTEGER = QIntValidator(-999999, 999999)
QVAL_INTEGER.setLocale(QLOC_NUMBER)
QVAL_FLOAT = QDoubleValidator(-999999.9999, 999999.9999, 6)
QVAL_FLOAT.setLocale(QLOC_NUMBER)
QVAL_COLOR = QRegularExpressionValidator(QRegularExpression('^#[0-9a-fA-F]*'))
QVAL_HEATMAP = QRegularExpressionValidator(QRegularExpression('[0-9a-zA-Z_]*'))
QVAL_PRESET = QRegularExpressionValidator(QRegularExpression('[^\\\\/:*?"<>|]*'))

# QStyleSheet
QSS_EDITOR_BUTTON = "padding: 3px 7px;"
QSS_EDITOR_LISTBOX = (
    "QListView {outline: none;}"
    "QListView::item {height: 32px;border-radius: 0;}"
    "QListView::item:selected {background: transparent;}"
    "QListView::item:hover {background: transparent;}"
)

# Misc
color_pick_history = deque(
    ["#FFF"] * QColorDialog.customCount(),
    maxlen=QColorDialog.customCount()
)

# Function
def update_preview_color(color_str, option):
    """Update preview background color"""
    if val.hex_color(color_str):
        # Set foreground color based on background color lightness
        qcolor = QColor(color_str)
        if qcolor.alpha() > 128 > qGray(qcolor.rgb()):
            fg_color = "#FFF"
        else:
            fg_color = "#000"
        # Apply style
        option.setStyleSheet(
            f"QLineEdit {{color: {fg_color};background: {color_str};}}"
        )


# Class
class BaseDialog(QDialog):
    """Base dialog class"""

    def __init__(self, master):
        super().__init__(master)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)


class BaseEditor(BaseDialog):
    """Base editor class"""

    def __init__(self, master):
        super().__init__(master)
        self._is_modified = False

    def confirm_discard(self) -> bool:
        """Confirm save or discard changes"""
        if not self._is_modified:
            return True

        confirm = QMessageBox.question(
            self, "Confirm", "<b>Save changes before continue?</b>",
            buttons=QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if confirm == QMessageBox.Save:
            self.saving()
            return self.confirm_discard()

        return confirm == QMessageBox.Discard

    def confirm_deletion(self, message: str = "Delete selection?") -> bool:
        """Confirm deletion"""
        confirm = QMessageBox.question(
            self, "Confirm", f"<b>{message}</b>",
            buttons=QMessageBox.Yes | QMessageBox.No)
        return confirm == QMessageBox.Yes

    def is_modified(self) -> bool:
        """Is modified"""
        return self._is_modified

    def set_modified(self):
        """Set modified state"""
        if not self._is_modified:
            self._is_modified = True

    def set_unmodified(self):
        """Set unmodified state"""
        if self._is_modified:
            self._is_modified = False

    def saving(self):
        """Save changes"""

    def closeEvent(self, event):
        """Close editor"""
        if not self.confirm_discard():
            event.ignore()


class BatchOffset(BaseDialog):
    """Batch offset"""

    def __init__(self, master, offset_func: object):
        super().__init__(master)
        self.setWindowTitle("Batch Offset")
        self.offset_func = offset_func
        self.edit_offset = None
        self.last_offset = QLabel("0")
        self.decimals = 0

    def config(self, decimals: int, step: float, min_range: int, max_range: int):
        """Config offset"""
        self.decimals = decimals

        if self.decimals > 0:
            self.edit_offset = QDoubleSpinBox()
            self.edit_offset.setDecimals(self.decimals)
        else:
            self.edit_offset = QSpinBox()

        self.edit_offset.setRange(min_range, max_range)
        self.edit_offset.setSingleStep(step)
        self.edit_offset.setAlignment(Qt.AlignRight)

        # Label
        last_label = QLabel("Last Offset:")

        layout_label = QHBoxLayout()
        layout_label.addWidget(last_label)
        layout_label.addStretch(1)
        layout_label.addWidget(self.last_offset)

        # Button
        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_close = QDialogButtonBox(QDialogButtonBox.Close)
        button_close.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_apply)
        layout_button.addStretch(1)
        layout_button.addWidget(button_close)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_label)
        layout_main.addWidget(self.edit_offset)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setFixedSize(150, self.sizeHint().height())

    def applying(self):
        """Apply offset"""
        value = self.edit_offset.value()
        if value != 0:
            self.last_offset.setText(f"{value:+.{self.decimals}f}")
            self.offset_func(value)
            self.edit_offset.setValue(0)


class DoubleClickEdit(QLineEdit):
    """Line edit with double click dialog trigger"""

    def __init__(self, mode: str, init: str):
        """Set dialog mode and initial value

        Args:
            mode: "color", "path".
            init: initial value.
        """
        super().__init__()
        self.open_mode = mode
        self.init_value = init

    def mouseDoubleClickEvent(self, event):
        """Double click to open dialog"""
        if event.buttons() == Qt.LeftButton:
            if self.open_mode == "color":
                self.open_dialog_color()
            elif self.open_mode == "path":
                self.open_dialog_path()

    def open_dialog_color(self):
        """Open color dialog"""
        color_dialog = QColorDialog()
        # Load color history to custom color slot
        for index, old_color in enumerate(color_pick_history):
            color_dialog.setCustomColor(index, QColor(old_color))
        # Open color selector dialog
        color_get = color_dialog.getColor(
            initial=QColor(self.init_value),
            options=QColorDialog.ShowAlphaChannel
        )
        if color_get.isValid():
            # Add new color to color history
            if color_pick_history[0] != color_get:
                color_pick_history.appendleft(color_get)
            # Set output format
            if color_get.alpha() == 255:  # without alpha value
                color = color_get.name(QColor.HexRgb).upper()
            else:  # with alpha value
                color = color_get.name(QColor.HexArgb).upper()
            # Update edit box and init value
            self.setText(color)
            self.init_value = color

    def open_dialog_path(self):
        """Open file path dialog"""
        path_selected = QFileDialog.getExistingDirectory(self, dir=self.init_value)
        if os.path.exists(path_selected):
            # Convert to relative path if in APP root folder
            path_valid = val.relative_path(path_selected)
            # Update edit box and init value
            self.setText(path_valid)
            self.init_value = path_valid
