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
Config dialog
"""

import re
import time
from collections.abc import Callable

from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QDialogButtonBox,
    QCheckBox,
    QComboBox,
    QScrollArea,
    QFontComboBox,
    QSpinBox,
    QMenu,
    QMessageBox,
)

from .. import regex_pattern as rxp
from .. import validator as val
from .. import formatter as fmt
from ..setting import cfg
from ._common import (
    BaseDialog,
    DoubleClickEdit,
    QVAL_INTEGER,
    QVAL_FLOAT,
    QVAL_COLOR,
)

OPTION_WIDTH = 120
COLUMN_LABEL = 0  # grid layout column index
COLUMN_OPTION = 1


class FontConfig(BaseDialog):
    """Config global font setting"""

    def __init__(self, master, user_setting: dict, reload_func: Callable):
        super().__init__(master)
        self.set_config_title("Global Font Override", cfg.filename.last_setting)

        self.reloading = reload_func
        self.user_setting = user_setting

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

    def save_setting(self, dict_user: dict):
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
        self.reloading()


class UserConfig(BaseDialog):
    """User configuration"""

    def __init__(
        self, master, key_name: str, cfg_type: str, user_setting: dict,
        default_setting: dict, reload_func: Callable, option_width: int = OPTION_WIDTH):
        super().__init__(master)
        self.set_config_title(fmt.format_option_name(key_name), set_preset_name(cfg_type))

        self.reloading = reload_func
        self.key_name = key_name
        self.cfg_type = cfg_type
        self.user_setting = user_setting
        self.default_setting = default_setting
        self.option_width = option_width

        # Option dict (key: option editor)
        self.option_bool: dict = {}
        self.option_color: dict = {}
        self.option_path: dict = {}
        self.option_image: dict = {}
        self.option_fontname: dict = {}
        self.option_droplist: dict = {}
        self.option_string: dict = {}
        self.option_integer: dict = {}
        self.option_float: dict = {}

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
        msg_text = (
            "Are you sure you want to reset options to default?<br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        if self.confirm_operation(title="Reset Options", message=msg_text):
            for key, editor in self.option_bool.items():
                editor.setChecked(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_color.items():
                editor.setText(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_path.items():
                editor.setText(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_image.items():
                editor.setText(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_fontname.items():
                editor.setCurrentFont(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_droplist.items():
                editor.setCurrentText(
                    str(self.default_setting[self.key_name][key]))

            for key, editor in self.option_string.items():
                editor.setText(
                    self.default_setting[self.key_name][key])

            for key, editor in self.option_integer.items():
                editor.setText(
                    str(self.default_setting[self.key_name][key]))

            for key, editor in self.option_float.items():
                editor.setText(
                    str(self.default_setting[self.key_name][key]))

    def save_setting(self, is_apply: bool):
        """Save setting"""
        error_found = False
        for key, editor in self.option_bool.items():
            self.user_setting[self.key_name][key] = editor.isChecked()

        for key, editor in self.option_color.items():
            value = editor.text()
            if val.hex_color(value):
                self.user_setting[self.key_name][key] = value
            else:
                self.value_error_message("color", key)
                error_found = True

        for key, editor in self.option_path.items():
            # Try convert to relative path again, in case user manually sets path
            value = val.relative_path(editor.text())
            if val.user_data_path(value):
                self.user_setting[self.key_name][key] = value
                editor.setText(value)  # update reformatted path
            else:
                self.value_error_message("path", key)
                error_found = True

        for key, editor in self.option_image.items():
            self.user_setting[self.key_name][key] = editor.text()

        for key, editor in self.option_fontname.items():
            self.user_setting[self.key_name][key] = editor.currentFont().family()

        for key, editor in self.option_droplist.items():
            self.user_setting[self.key_name][key] = editor.currentText()

        for key, editor in self.option_string.items():
            value = editor.text()
            if re.search(rxp.CFG_CLOCK_FORMAT, key) and not val.clock_format(value):
                self.value_error_message("clock format", key)
                error_found = True
                continue
            self.user_setting[self.key_name][key] = value

        for key, editor in self.option_integer.items():
            value = editor.text()
            if val.string_number(value):
                self.user_setting[self.key_name][key] = int(value)
            else:
                self.value_error_message("number", key)
                error_found = True

        for key, editor in self.option_float.items():
            value = editor.text()
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
            return
        # Save global settings
        if self.cfg_type == "global":
            cfg.update_path()
            cfg.save(0, filetype="config")
        # Save user preset settings
        else:
            cfg.save(0)
        # Wait saving finish
        while cfg.is_saving:
            time.sleep(0.01)
        # Reload
        self.reloading()
        # Close
        if not is_apply:
            self.accept()

    def value_error_message(self, value_type: str, option_name: str):
        """Value error message"""
        msg_text = (
            f"Invalid {value_type} for <b>{fmt.format_option_name(option_name)}</b> option."
            "<br><br>Changes are not saved."
        )
        QMessageBox.warning(self, "Error", msg_text)

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
            # User image file path string
            if re.search(rxp.CFG_USER_IMAGE, key):
                self.__add_option_image(
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
        label = QLabel(fmt.format_option_name(key))
        layout.addWidget(label, idx, COLUMN_LABEL)

    def __add_option_bool(self, idx, key, layout):
        """Bool"""
        editor = QCheckBox()
        editor.setFixedWidth(self.option_width)
        editor.setChecked(self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, self.default_setting[self.key_name][key], "set_check")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_bool[key] = editor

    def __add_option_color(self, idx, key, layout):
        """Color string"""
        editor = DoubleClickEdit(
            mode="color", init=self.user_setting[self.key_name][key])
        editor.setFixedWidth(self.option_width)
        editor.setMaxLength(9)
        editor.setValidator(QVAL_COLOR)
        editor.textChanged.connect(editor.preview_color)
        # Load selected option
        editor.setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, str(self.default_setting[self.key_name][key]), "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_color[key] = editor

    def __add_option_path(self, idx, key, layout):
        """Path string"""
        editor = DoubleClickEdit(
            mode="path", init=self.user_setting[self.key_name][key])
        editor.setFixedWidth(self.option_width)
        # Load selected option
        editor.setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, str(self.default_setting[self.key_name][key]), "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_path[key] = editor

    def __add_option_image(self, idx, key, layout):
        """Image file path string"""
        editor = DoubleClickEdit(
            mode="image", init=self.user_setting[self.key_name][key])
        editor.setFixedWidth(self.option_width)
        # Load selected option
        editor.setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, str(self.default_setting[self.key_name][key]), "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_image[key] = editor

    def __add_option_fontname(self, idx, key, layout):
        """Font name string"""
        editor = QFontComboBox()
        editor.setFixedWidth(self.option_width)
        # Load selected option
        editor.setCurrentFont(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, self.default_setting[self.key_name][key], "set_combo")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_fontname[key] = editor

    def __add_option_combolist(self, idx, key, layout, item_list):
        """Combo droplist string"""
        editor = QComboBox()
        editor.setFixedWidth(self.option_width)
        editor.addItems(item_list)
        # Load selected option
        editor.setCurrentText(str(self.user_setting[self.key_name][key]))
        # Context menu
        add_context_menu(
            editor, self.default_setting[self.key_name][key], "set_combo")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_droplist[key] = editor

    def __add_option_string(self, idx, key, layout):
        """String"""
        editor = QLineEdit()
        editor.setFixedWidth(self.option_width)
        # Load selected option
        editor.setText(
            self.user_setting[self.key_name][key])
        # Context menu
        add_context_menu(
            editor, self.default_setting[self.key_name][key], "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_string[key] = editor

    def __add_option_integer(self, idx, key, layout):
        """Integer"""
        editor = QLineEdit()
        editor.setFixedWidth(self.option_width)
        editor.setValidator(QVAL_INTEGER)
        # Load selected option
        editor.setText(
            str(self.user_setting[self.key_name][key]))
        # Context menu
        add_context_menu(
            editor, str(self.default_setting[self.key_name][key]), "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_integer[key] = editor

    def __add_option_float(self, idx, key, layout):
        """Float"""
        editor = QLineEdit()
        editor.setFixedWidth(self.option_width)
        editor.setValidator(QVAL_FLOAT)
        # Load selected option
        editor.setText(
            str(self.user_setting[self.key_name][key]))
        # Context menu
        add_context_menu(
            editor, str(self.default_setting[self.key_name][key]), "set_text")
        # Add layout
        layout.addWidget(editor, idx, COLUMN_OPTION)
        self.option_float[key] = editor


def set_preset_name(cfg_type: str):
    """Set preset name"""
    if cfg_type == "global":
        return f"{cfg.filename.config} (global)"
    return cfg.filename.last_setting


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
        elif mode == "set_text":
            target.setText(default)
        elif mode == "set_combo":
            target.setCurrentText(default)
