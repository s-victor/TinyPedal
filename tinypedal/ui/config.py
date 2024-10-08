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
Config window
"""

import os
import re
import time
from collections import deque

from PySide2.QtCore import Qt, QRegularExpression, QLocale
from PySide2.QtGui import (
    QIcon, QRegularExpressionValidator, QIntValidator, QDoubleValidator, QColor)
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QDialog,
    QLineEdit,
    QDialogButtonBox,
    QCheckBox,
    QComboBox,
    QScrollArea,
    QColorDialog,
    QFontComboBox,
    QSpinBox,
    QMenu,
    QMessageBox,
    QFileDialog
)

from .. import regex_pattern as rxp
from .. import validator as val
from .. import formatter as fmt
from ..setting import cfg
from ..const import APP_ICON
from ..module_control import mctrl, wctrl


OPTION_WIDTH = 120
COLUMN_LABEL = 0  # grid layout column index
COLUMN_OPTION = 1

# Option validator
number_locale = QLocale(QLocale.C)
number_locale.setNumberOptions(QLocale.RejectGroupSeparator)
integer_valid = QIntValidator(-999999, 999999)
integer_valid.setLocale(number_locale)
float_valid = QDoubleValidator(-999999.9999, 999999.9999, 6)
float_valid.setLocale(number_locale)
color_valid = QRegularExpressionValidator(QRegularExpression('^#[0-9a-fA-F]*'))
heatmap_name_valid = QRegularExpressionValidator(QRegularExpression('[0-9a-zA-Z_]*'))
color_pick_history = deque(
    ["#FFF"] * QColorDialog.customCount(),
    maxlen=QColorDialog.customCount()
)


class FontConfig(QDialog):
    """Config global font setting"""

    def __init__(self, master, user_setting: dict):
        super().__init__(master)
        self.user_setting = user_setting

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(f"Global Font Override - {cfg.filename.last_setting}")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Label & combobox
        self.label_fontname = QLabel("Font Name")
        self.edit_fontname = QFontComboBox()
        self.edit_fontname.setCurrentText("no change")
        self.edit_fontname.setFixedWidth(OPTION_WIDTH)

        self.label_fontsize = QLabel("Font Size Addend")
        self.edit_fontsize = QSpinBox()
        self.edit_fontsize.setRange(-999,999)
        self.edit_fontsize.setFixedWidth(OPTION_WIDTH)

        self.label_fontweight = QLabel("Font Weight")
        self.edit_fontweight = QComboBox()
        self.edit_fontweight.addItems(
            ("no change", *rxp.CHOICE_COMMON[rxp.CFG_FONT_WEIGHT]))
        self.edit_fontweight.setFixedWidth(OPTION_WIDTH)

        layout_option = QGridLayout()
        layout_option.setAlignment(Qt.AlignTop)
        layout_option.addWidget(self.label_fontname, 0, 0)
        layout_option.addWidget(self.edit_fontname, 0, 1)
        layout_option.addWidget(self.label_fontsize, 1, 0)
        layout_option.addWidget(self.edit_fontsize, 1, 1)
        layout_option.addWidget(self.label_fontweight, 2, 0)
        layout_option.addWidget(self.edit_fontweight, 2, 1)

        # Button
        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_save = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.reject)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)

        # Set layout
        layout_main = QVBoxLayout()
        layout_main.addLayout(layout_option)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)

    def applying(self):
        """Save & apply"""
        self.save_setting(self.user_setting)

    def saving(self):
        """Save & close"""
        self.applying()
        self.accept()  # close

    def save_setting(self, dict_user):
        """Save setting"""
        for item in dict_user.keys():
            key_list_user = tuple(dict_user[item])
            for key in key_list_user:
                if (re.search(rxp.CFG_FONT_NAME, key) and
                    self.edit_fontname.currentText() != "no change"):
                    dict_user[item][key] = self.edit_fontname.currentFont().family()
                    continue
                if (re.search(rxp.CFG_FONT_WEIGHT, key) and
                    self.edit_fontweight.currentText() != "no change"):
                    dict_user[item][key] = self.edit_fontweight.currentText()
                    continue
                if re.search("font_size", key):
                    dict_user[item][key] = max(
                        dict_user[item][key] + self.edit_fontsize.value(), 1)
                    continue
        self.edit_fontsize.setValue(0)
        cfg.save(0)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        wctrl.reload()


class UserConfig(QDialog):
    """User configuration"""

    def __init__(
        self, master, key_name: str, cfg_type: str, user_setting: dict,
        default_setting: dict, option_width: int = OPTION_WIDTH):
        super().__init__(master)
        self.master = master
        self.key_name = key_name
        self.cfg_type = cfg_type
        self.user_setting = user_setting
        self.default_setting = default_setting
        self.option_width = option_width

        if self.cfg_type == "global":
            preset_filename = f"{cfg.filename.config} (global)"
        else:
            preset_filename = cfg.filename.last_setting

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowTitle(f"{fmt.format_option_name(key_name)} - {preset_filename}")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Option type
        self.option_bool = []
        self.option_color = []
        self.option_path = []
        self.option_fontname = []
        self.option_droplist = []
        self.option_string = []
        self.option_integer = []
        self.option_float = []

        # Button
        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_setting)

        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_save = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.reject)

        # Create options
        layout_option = QGridLayout()
        layout_option.setAlignment(Qt.AlignTop)
        self.create_options(layout_option)
        option_box = QWidget()
        option_box.setLayout(layout_option)

        # Create scroll box
        scroll_box = QScrollArea()
        scroll_box.setWidget(option_box)
        scroll_box.setWidgetResizable(True)

        # Set layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(scroll_box)
        layout_button.addWidget(button_reset)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setMinimumWidth(self.sizeHint().width() + 20)

    def applying(self):
        """Save & apply"""
        self.save_setting(is_apply=True)

    def saving(self):
        """Save & close"""
        self.save_setting(is_apply=False)

    def reset_setting(self):
        """Reset setting"""
        message_text = (
            "Are you sure you want to reset options to default? <br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        reset_msg = QMessageBox.question(
            self, "Reset Options", message_text,
            buttons=QMessageBox.Yes | QMessageBox.No)

        if reset_msg == QMessageBox.Yes:
            for key in self.option_bool:
                getattr(self, f"checkbox_{key}").setChecked(
                    self.default_setting[self.key_name][key])

            for key in self.option_color:
                getattr(self, f"lineedit_{key}").setText(
                    self.default_setting[self.key_name][key])

            for key in self.option_path:
                getattr(self, f"lineedit_{key}").setText(
                    self.default_setting[self.key_name][key])

            for key in self.option_fontname:
                getattr(self, f"fontedit_{key}").setCurrentFont(
                    self.default_setting[self.key_name][key])

            for key in self.option_droplist:
                curr_index = getattr(self, f"combobox_{key}").findText(
                    f"{self.default_setting[self.key_name][key]}", Qt.MatchExactly)
                if curr_index != -1:
                    getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)

            for key in self.option_string:
                getattr(self, f"lineedit_{key}").setText(
                    self.default_setting[self.key_name][key])

            for key in self.option_integer:
                getattr(self, f"lineedit_{key}").setText(
                    str(self.default_setting[self.key_name][key]))

            for key in self.option_float:
                getattr(self, f"lineedit_{key}").setText(
                    str(self.default_setting[self.key_name][key]))

    def save_setting(self, is_apply):
        """Save setting"""
        error_found = False
        for key in self.option_bool:
            self.user_setting[self.key_name][key] = getattr(
                self, f"checkbox_{key}").isChecked()

        for key in self.option_color:
            value = getattr(self, f"lineedit_{key}").text()
            if val.hex_color(value):
                self.user_setting[self.key_name][key] = value
            else:
                self.value_error_message("color", key)
                error_found = True

        for key in self.option_path:
            # Try convert to relative path again, in case user manually sets path
            value = val.relative_path(getattr(self, f"lineedit_{key}").text())
            if val.user_data_path(value):
                # Make sure path end with "/"
                if not value.endswith("/"):
                    value += "/"
                self.user_setting[self.key_name][key] = value
                # Update reformatted path to edit box
                getattr(self, f"lineedit_{key}").setText(value)
            else:
                self.value_error_message("path", key)
                error_found = True

        for key in self.option_fontname:
            self.user_setting[self.key_name][key] = getattr(
                self, f"fontedit_{key}").currentFont().family()

        for key in self.option_droplist:
            self.user_setting[self.key_name][key] = getattr(
                self, f"combobox_{key}").currentText()

        for key in self.option_string:
            value = getattr(self, f"lineedit_{key}").text()
            if re.search(rxp.CFG_CLOCK_FORMAT, key) and not val.clock_format(value):
                self.value_error_message("clock format", key)
                error_found = True
                continue
            self.user_setting[self.key_name][key] = value

        for key in self.option_integer:
            value = getattr(self, f"lineedit_{key}").text()
            if val.string_number(value):
                self.user_setting[self.key_name][key] = int(value)
            else:
                self.value_error_message("number", key)
                error_found = True

        for key in self.option_float:
            value = getattr(self, f"lineedit_{key}").text()
            if val.string_number(value):
                value = float(value)
                if value % 1 == 0:  # remove unnecessary decimal points
                    value = int(value)
                self.user_setting[self.key_name][key] = value
            else:
                self.value_error_message("number", key)
                error_found = True

        # Abort saving if error found
        if error_found:
            return None
        # Save global settings
        if self.cfg_type == "global":
            cfg.update_path()
            cfg.save(0, "config")
        # Save user preset settings
        else:
            cfg.save(0)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        self.reloading()
        # Close
        if not is_apply:
            self.accept()
        return None

    def value_error_message(self, value_type, option_name):
        """Value error message"""
        message = (
            f"Invalid {value_type} for <b>{fmt.format_option_name(option_name)}</b> option."
            "<br><br>Changes are not saved.")
        QMessageBox.warning(self, "Error", message)

    def reloading(self):
        """Reloading depends on setting types"""
        # Select type
        if self.cfg_type == "global":
            self.master.reload_preset()
        elif self.cfg_type == wctrl.type_id:
            wctrl.reload(self.key_name)
            self.master.refresh_state()
        elif self.cfg_type == mctrl.type_id:
            mctrl.reload(self.key_name)
            self.master.refresh_state()
        elif self.cfg_type == "misc":
            wctrl.reload()
        elif self.cfg_type == "api":
            self.master.restart_api()
            self.master.spectate_tab.refresh_list()

    def create_options(self, layout):
        """Create options"""
        key_list_user = tuple(self.user_setting[self.key_name])  # create user key list

        for idx, key in enumerate(key_list_user):
            self.__add_option_label(
                idx, key, layout)
            # Bool
            if re.search(rxp.CFG_BOOL, key):
                self.__add_option_bool(
                    idx, key, layout)
                continue
            # Color string
            if re.search(rxp.CFG_COLOR, key):
                self.__add_option_color(
                    idx, key, layout)
                continue
            # User path string
            if re.search(rxp.CFG_USER_PATH, key):
                self.__add_option_path(
                    idx, key, layout)
                continue
            # Font name string
            if re.search(rxp.CFG_FONT_NAME, key):
                self.__add_option_fontname(
                    idx, key, layout)
                continue
            # Units choice list string
            if self.__choice_match(rxp.CHOICE_UNITS, idx, key, layout):
                continue
            # Common choice list string
            if self.__choice_match(rxp.CHOICE_COMMON, idx, key, layout):
                continue
            # Heatmap string
            if re.search(rxp.CFG_HEATMAP, key):
                self.__add_option_combolist(
                    idx, key, layout, tuple(cfg.user.heatmap))
                continue
            # Clock format string
            if re.search(rxp.CFG_CLOCK_FORMAT, key):
                self.__add_option_string(
                    idx, key, layout)
                continue
            # String
            if re.search(rxp.CFG_STRING, key):
                self.__add_option_string(
                    idx, key, layout)
                continue
            # Int
            if re.search(rxp.CFG_INTEGER, key):
                self.__add_option_integer(
                    idx, key, layout)
                continue
            # Anything else
            self.__add_option_float(
                idx, key, layout)

    def __choice_match(self, choice_dict, idx, key, layout):
        """Choice match"""
        for ref_key, choice_list in choice_dict.items():
            if re.search(ref_key, key):
                self.__add_option_combolist(
                    idx, key, layout, choice_list)
                return True
        return False

    def __add_option_label(self, idx, key, layout):
        """Option label"""
        setattr(self, f"label_{key}", QLabel(f"{fmt.format_option_name(key)}"))
        layout.addWidget(getattr(self, f"label_{key}"), idx, COLUMN_LABEL)

    def __add_option_bool(self, idx, key, layout):
        """Bool"""
        setattr(self, f"checkbox_{key}", QCheckBox())
        getattr(self, f"checkbox_{key}").setFixedWidth(self.option_width)
        getattr(self, f"checkbox_{key}").setChecked(self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"checkbox_{key}"),
            self.default_setting[self.key_name][key],
            "set_check")
        # Add layout
        layout.addWidget(
            getattr(self, f"checkbox_{key}"), idx, COLUMN_OPTION)
        self.option_bool.append(key)

    def __add_option_color(self, idx, key, layout):
        """Color string"""
        setattr(self, f"lineedit_{key}", DoubleClickEdit(
            mode="color", init=self.user_setting[self.key_name][key]))
        getattr(self, f"lineedit_{key}").setFixedWidth(self.option_width)
        getattr(self, f"lineedit_{key}").setMaxLength(9)
        getattr(self, f"lineedit_{key}").setValidator(color_valid)
        getattr(self, f"lineedit_{key}").textChanged.connect(
            lambda color_str, option=getattr(self, f"lineedit_{key}"):
            update_preview_color(color_str, option))
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(self.default_setting[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_color.append(key)

    def __add_option_path(self, idx, key, layout):
        """Path string"""
        setattr(self, f"lineedit_{key}", DoubleClickEdit(
            mode="path", init=self.user_setting[self.key_name][key]))
        getattr(self, f"lineedit_{key}").setFixedWidth(self.option_width)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(self.default_setting[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_path.append(key)

    def __add_option_fontname(self, idx, key, layout):
        """Font name string"""
        setattr(self, f"fontedit_{key}", QFontComboBox())
        getattr(self, f"fontedit_{key}").setFixedWidth(self.option_width)
        # Load selected option
        getattr(self, f"fontedit_{key}").setCurrentFont(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"fontedit_{key}"),
            self.default_setting[self.key_name][key],
            "set_font")
        # Add layout
        layout.addWidget(
            getattr(self, f"fontedit_{key}"), idx, COLUMN_OPTION)
        self.option_fontname.append(key)

    def __add_option_combolist(self, idx, key, layout, item_list):
        """Combo droplist string"""
        setattr(self, f"combobox_{key}", QComboBox())
        getattr(self, f"combobox_{key}").setFixedWidth(self.option_width)
        getattr(self, f"combobox_{key}").addItems(item_list)
        # Load selected option
        curr_index = getattr(self, f"combobox_{key}").findText(
            f"{self.user_setting[self.key_name][key]}", Qt.MatchExactly)
        if curr_index != -1:
            getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)
        # Context menu
        add_context_menu(
            getattr(self, f"combobox_{key}"),
            self.default_setting[self.key_name][key],
            "set_combo")
        # Add layout
        layout.addWidget(
            getattr(self, f"combobox_{key}"), idx, COLUMN_OPTION)
        self.option_droplist.append(key)

    def __add_option_string(self, idx, key, layout):
        """String"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(self.option_width)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            self.default_setting[self.key_name][key],
            "set_text")
        # Add layout
        layout.addWidget(getattr(
            self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_string.append(key)

    def __add_option_integer(self, idx, key, layout):
        """Integer"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(self.option_width)
        getattr(self, f"lineedit_{key}").setValidator(integer_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(self.user_setting[self.key_name][key]))
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(self.default_setting[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_integer.append(key)

    def __add_option_float(self, idx, key, layout):
        """Float"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(self.option_width)
        getattr(self, f"lineedit_{key}").setValidator(float_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(self.user_setting[self.key_name][key]))
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(self.default_setting[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_float.append(key)


class DoubleClickEdit(QLineEdit):
    """Line edit with double click dialog trigger"""

    def __init__(self, mode: str, init: str):
        """Set dialog mode and initial value

        Args:
            mode: "color", "path".
            init: initial value.
        """
        super().__init__()
        self.open_dialog = getattr(self, f"open_dialog_{mode}")
        self.init_value = init

    def mouseDoubleClickEvent(self, event):
        """Double click to open dialog"""
        if event.buttons() == Qt.LeftButton:
            self.open_dialog()

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
            path_valid = f"{val.relative_path(path_selected)}/"
            # Update edit box and init value
            self.setText(path_valid)
            self.init_value = path_valid


def add_context_menu(target, default, mode):
    """Add context menu"""
    target.setContextMenuPolicy(Qt.CustomContextMenu)
    target.customContextMenuRequested.connect(
        lambda pos,
        target=target,
        default=default,
        mode=mode:
        context_menu_reset_option(pos, target, default, mode)
    )


def context_menu_reset_option(pos, target, default, mode):
    """Context menu reset option"""
    menu = QMenu()
    option_reset = menu.addAction("Reset to Default")
    action = menu.exec_(target.mapToGlobal(pos))

    if action == option_reset:
        if mode == "set_check":
            target.setChecked(default)
        elif mode == "set_font":
            target.setCurrentText(default)
        elif mode == "set_text":
            target.setText(default)
        elif mode == "set_combo":
            curr_index = target.findText(default, Qt.MatchExactly)
            if curr_index != -1:
                target.setCurrentIndex(curr_index)


def adaptive_foreground_color(color_str):
    """Set foreground color based on background color lightness"""
    if QColor(color_str).alpha() > 128 > QColor(color_str).lightness():
        return "#FFF"
    return "#000"


def update_preview_color(color_str, option):
    """Update preview background color"""
    if val.hex_color(color_str):
        option.setStyleSheet(
            f"color: {adaptive_foreground_color(color_str)};"
            f"background: {color_str};"
        )
