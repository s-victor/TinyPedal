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
Config window
"""

import re
import time

from PySide2.QtCore import Qt, QRegExp, QLocale
from PySide2.QtGui import QIcon, QRegExpValidator, QIntValidator, QDoubleValidator, QColor
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
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)

from . import regex_pattern as rxp
from . import validator as val
from . import formatter as fmt
from .api_control import api
from .setting import cfg, copy_setting
from .const import APP_ICON
from .api_connector import API_NAME_LIST
from .module_control import mctrl
from .widget_control import wctrl


OPTION_WIDTH = 120
COLUMN_LABEL = 0  # grid layout column index
COLUMN_OPTION = 1

# Option validator
number_locale = QLocale(QLocale.C)
number_locale.setNumberOptions(QLocale.RejectGroupSeparator)
int_valid = QIntValidator(-999999, 999999)
int_valid.setLocale(number_locale)
float_valid = QDoubleValidator(-999999.9999, 999999.9999, 6)
float_valid.setLocale(number_locale)
color_valid = QRegExpValidator(QRegExp('^#[0-9a-fA-F]*'))


class VehicleClassEditor(QDialog):
    """Vehicle class editor"""

    def __init__(self, master):
        super().__init__(master)
        self.setWindowTitle("Vehicle Class Editor")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMinimumHeight(400)

        self.option_classes = []
        self.classes_temp = copy_setting(cfg.classes_user)

        # List box
        self.listbox_classes = QListWidget(self)
        self.refresh_classes_list()
        self.listbox_classes.setStyleSheet(
            "QListView {outline: none;}"
            "QListView::item {height: 32px;border-radius: 0;}"
            "QListView::item:selected {background-color: transparent;}"
            "QListView::item:hover {background-color: transparent;}"
        )

        # Button
        button_add = QPushButton("Add Class")
        button_add.clicked.connect(self.add_class)

        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_setting)

        button_apply = QDialogButtonBox(QDialogButtonBox.Apply)
        button_apply.clicked.connect(self.applying)

        button_save = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.saving)
        button_save.rejected.connect(self.reject)

        # Set layout
        layout_main = QVBoxLayout()
        layout_button = QHBoxLayout()

        layout_main.addWidget(self.listbox_classes)
        layout_button.addWidget(button_add)
        layout_button.addWidget(button_reset)
        layout_button.addWidget(button_apply)
        layout_button.addWidget(button_save)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.setMinimumWidth(self.sizeHint().width() + 20)

    def refresh_classes_list(self):
        """Refresh classes list"""
        self.listbox_classes.clear()
        self.option_classes.clear()

        for idx, key in enumerate(self.classes_temp):
            layout_item = QHBoxLayout()
            layout_item.setContentsMargins(4,4,4,4)
            layout_item.setSpacing(4)

            line_edit_key = self.__add_key_string(key, layout_item)
            for sub_key, sub_item in self.classes_temp[key].items():
                line_edit_sub_key = self.__add_key_string(sub_key, layout_item)
                color_edit = self.__add_option_color(sub_item, layout_item, 80)
                self.__add_delete_button(idx, layout_item)
                self.option_classes.append((line_edit_key, line_edit_sub_key, color_edit))

            classes_item = QWidget()
            classes_item.setLayout(layout_item)
            item = QListWidgetItem()
            self.listbox_classes.addItem(item)
            self.listbox_classes.setItemWidget(item, classes_item)

    def __add_key_string(self, key, layout):
        """Key string"""
        line_edit = QLineEdit()
        # Load selected option
        line_edit.setText(key)
        # Add layout
        layout.addWidget(line_edit)
        return line_edit

    def __add_option_color(self, key, layout, width):
        """Color string"""
        color_edit = ColorEdit(key)
        color_edit.setFixedWidth(width)
        color_edit.setMaxLength(9)
        color_edit.setValidator(color_valid)
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
            lambda index=idx: self.delete_class(index))
        layout.addWidget(button)

    def delete_class(self, index):
        """Delete class entry"""
        self.update_classes_temp()
        for idx, key in enumerate(self.classes_temp):
            if index == idx:
                self.classes_temp.pop(key)
                break
        self.refresh_classes_list()

    def add_class(self):
        """Add new class entry"""
        self.update_classes_temp()
        current_class_name = api.read.vehicle.class_name()
        # Check if class already exist or empty
        if self.classes_temp.get(current_class_name) or not current_class_name:
            current_class_name = "New Class Name"
        self.classes_temp[current_class_name] = {"NAME": "#00AAFF"}
        self.refresh_classes_list()
        # Move focus to new class row
        self.listbox_classes.setCurrentRow(len(self.classes_temp) - 1)

    def reset_setting(self):
        """Reset setting"""
        message_text = (
            "Are you sure you want to reset class preset to default? <br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        reset_msg = QMessageBox.question(
            self, "Delete Preset", message_text,
            button=QMessageBox.Yes | QMessageBox.No)
        if reset_msg == QMessageBox.Yes:
            self.classes_temp = copy_setting(cfg.classes_default)
            self.refresh_classes_list()

    def applying(self):
        """Save & apply"""
        self.save_setting()

    def saving(self):
        """Save & close"""
        self.save_setting()
        self.accept()  # close

    def update_classes_temp(self):
        """Update temporary changes to classes temp first"""
        self.classes_temp.clear()
        for edit in self.option_classes:
            key_name = edit[0].text()
            sub_key_name = edit[1].text()
            sub_item_name = edit[2].text()
            self.classes_temp[key_name] = {sub_key_name: sub_item_name}

    def save_setting(self):
        """Save setting"""
        self.update_classes_temp()
        self.refresh_classes_list()
        cfg.classes_user = copy_setting(self.classes_temp)
        cfg.save(0, "classes")
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        wctrl.close()
        wctrl.start()


class FontConfig(QDialog):
    """Config global font setting"""

    def __init__(self, master):
        super().__init__(master)
        self.setWindowTitle("Global Font Override")
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
        self.edit_fontweight.addItems(("no change", *rxp.FONT_WEIGHT_LIST))
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
        self.save_setting(cfg.setting_user)

    def saving(self):
        """Save & close"""
        self.save_setting(cfg.setting_user)
        self.accept()  # close

    def save_setting(self, dict_user):
        """Save setting"""
        for item in dict_user.keys():
            key_list_user = tuple(dict_user[item])
            for key in key_list_user:
                if (re.search(rxp.CFG_FONT_NAME, key) and
                    self.edit_fontname.currentText() != "no change"):
                    dict_user[item][key] = self.edit_fontname.currentFont().family()
                if (re.search(rxp.CFG_FONT_WEIGHT, key) and
                    self.edit_fontweight.currentText() != "no change"):
                    dict_user[item][key] = self.edit_fontweight.currentText()
                if key == "font_size":
                    dict_user[item][key] = max(
                        dict_user[item][key] + self.edit_fontsize.value(), 1)
        self.edit_fontsize.setValue(0)
        cfg.save(0)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        wctrl.close()
        wctrl.start()


class UserConfig(QDialog):
    """User configuration"""

    def __init__(self, master, key_name, cfg_type):
        super().__init__(master)
        self.master = master
        self.key_name = key_name
        self.cfg_type = cfg_type

        self.setWindowTitle(f"{fmt.format_option_name(key_name)}")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Option type
        self.option_bool = []
        self.option_color = []
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
        self.save_setting()

    def saving(self):
        """Save & close"""
        self.save_setting()
        self.accept()  # close

    def reset_setting(self):
        """Reset setting"""
        message_text = (
            "Are you sure you want to reset options to default? <br><br>"
            "Changes are only saved after clicking Apply or Save Button."
        )
        reset_msg = QMessageBox.question(
            self, "Delete Preset", message_text,
            button=QMessageBox.Yes | QMessageBox.No)

        if reset_msg == QMessageBox.Yes:
            for key in self.option_bool:
                getattr(self, f"checkbox_{key}").setChecked(
                    cfg.setting_default[self.key_name][key])

            for key in self.option_color:
                getattr(self, f"lineedit_{key}").setText(
                    cfg.setting_default[self.key_name][key])

            for key in self.option_fontname:
                getattr(self, f"fontedit_{key}").setCurrentFont(
                    cfg.setting_default[self.key_name][key])

            for key in self.option_droplist:
                curr_index = getattr(self, f"combobox_{key}").findText(
                    f"{cfg.setting_default[self.key_name][key]}", Qt.MatchExactly)
                if curr_index != -1:
                    getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)

            for key in self.option_string:
                getattr(self, f"lineedit_{key}").setText(
                    cfg.setting_default[self.key_name][key])

            for key in self.option_integer:
                getattr(self, f"lineedit_{key}").setText(
                    str(cfg.setting_default[self.key_name][key]))

            for key in self.option_float:
                getattr(self, f"lineedit_{key}").setText(
                    str(cfg.setting_default[self.key_name][key]))

    def save_setting(self):
        """Save setting"""
        for key in self.option_bool:
            value = getattr(self, f"checkbox_{key}").checkState()
            cfg.setting_user[self.key_name][key] = bool(value)

        for key in self.option_color:
            cfg.setting_user[self.key_name][key] = getattr(
                self, f"lineedit_{key}").text()

        for key in self.option_fontname:
            cfg.setting_user[self.key_name][key] = getattr(
                self, f"fontedit_{key}").currentFont().family()

        for key in self.option_droplist:
            cfg.setting_user[self.key_name][key] = getattr(
                self, f"combobox_{key}").currentText()

        for key in self.option_string:
            cfg.setting_user[self.key_name][key] = getattr(
                self, f"lineedit_{key}").text()

        for key in self.option_integer:
            cfg.setting_user[self.key_name][key] = int(getattr(
                self, f"lineedit_{key}").text())

        for key in self.option_float:
            value = float(getattr(self, f"lineedit_{key}").text())
            if divmod(value, 1)[1] == 0:
                value = int(value)
            cfg.setting_user[self.key_name][key] = value

        # Save changes
        cfg.save(0)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)
        self.reloading()

    def reloading(self):
        """Reloading depends on setting types"""
        # Select type
        if self.cfg_type == "widget":
            wctrl.close_selected(self.key_name)
            wctrl.start_selected(self.key_name)
            self.master.refresh_widget_list()
        elif self.cfg_type == "module":
            mctrl.close_selected(self.key_name)
            mctrl.start_selected(self.key_name)
            self.master.refresh_module_list()
        elif self.cfg_type == "misc":
            wctrl.close()
            wctrl.start()
        elif self.cfg_type == "api":
            self.master.restart_api()
            self.master.spectate_tab.refresh_spectate_list()

    def create_options(self, layout):
        """Create options"""
        key_list_user = tuple(cfg.setting_user[self.key_name])  # create user key list

        for idx, key in enumerate(key_list_user):
            #print(key, cfg.setting_user[self.key_name][key])
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
            # Font name string
            if re.search(rxp.CFG_FONT_NAME, key):
                self.__add_option_fontname(
                    idx, key, layout)
                continue
            # Units list string
            if key in rxp.UNITS_DICT:
                self.__add_option_combolist(
                    idx, key, layout, rxp.UNITS_DICT[key])
                continue
            # API name string
            if re.search(rxp.CFG_API_NAME, key):
                self.__add_option_combolist(
                    idx, key, layout, API_NAME_LIST)
                continue
            # Font weight string
            if re.search(rxp.CFG_FONT_WEIGHT, key):
                self.__add_option_combolist(
                    idx, key, layout, rxp.FONT_WEIGHT_LIST)
                continue
            # Heatmap string
            if re.search(rxp.CFG_HEATMAP, key):
                self.__add_option_combolist(
                    idx, key, layout, tuple(cfg.heatmap_user))
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

    def __add_option_label(self, idx, key, layout):
        """Option label"""
        setattr(self, f"label_{key}", QLabel(f"{fmt.format_option_name(key)}"))
        layout.addWidget(getattr(self, f"label_{key}"), idx, COLUMN_LABEL)

    def __add_option_bool(self, idx, key, layout):
        """Bool"""
        setattr(self, f"checkbox_{key}", QCheckBox())
        getattr(self, f"checkbox_{key}").setFixedWidth(OPTION_WIDTH)
        getattr(self, f"checkbox_{key}").setChecked(cfg.setting_user[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"checkbox_{key}"),
            cfg.setting_default[self.key_name][key],
            "set_check")
        # Add layout
        layout.addWidget(
            getattr(self, f"checkbox_{key}"), idx, COLUMN_OPTION)
        self.option_bool.append(key)

    def __add_option_color(self, idx, key, layout):
        """Color string"""
        setattr(self, f"lineedit_{key}", ColorEdit(cfg.setting_user[self.key_name][key]))
        getattr(self, f"lineedit_{key}").setFixedWidth(OPTION_WIDTH)
        getattr(self, f"lineedit_{key}").setMaxLength(9)
        getattr(self, f"lineedit_{key}").setValidator(color_valid)
        getattr(self, f"lineedit_{key}").textChanged.connect(
            lambda color_str, option=getattr(self, f"lineedit_{key}"):
            update_preview_color(color_str, option))
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            cfg.setting_user[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_color.append(key)

    def __add_option_fontname(self, idx, key, layout):
        """Font name string"""
        setattr(self, f"fontedit_{key}", QFontComboBox())
        getattr(self, f"fontedit_{key}").setFixedWidth(OPTION_WIDTH)
        # Load selected option
        getattr(self, f"fontedit_{key}").setCurrentFont(
            cfg.setting_user[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"fontedit_{key}"),
            cfg.setting_default[self.key_name][key],
            "set_font")
        # Add layout
        layout.addWidget(
            getattr(self, f"fontedit_{key}"), idx, COLUMN_OPTION)
        self.option_fontname.append(key)

    def __add_option_combolist(self, idx, key, layout, item_list):
        """Combo droplist string"""
        setattr(self, f"combobox_{key}", QComboBox())
        getattr(self, f"combobox_{key}").setFixedWidth(OPTION_WIDTH)
        getattr(self, f"combobox_{key}").addItems(item_list)
        # Load selected option
        curr_index = getattr(self, f"combobox_{key}").findText(
            f"{cfg.setting_user[self.key_name][key]}", Qt.MatchExactly)
        if curr_index != -1:
            getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)
        # Context menu
        add_context_menu(
            getattr(self, f"combobox_{key}"),
            cfg.setting_default[self.key_name][key],
            "set_combo")
        # Add layout
        layout.addWidget(
            getattr(self, f"combobox_{key}"), idx, COLUMN_OPTION)
        self.option_droplist.append(key)

    def __add_option_string(self, idx, key, layout):
        """String"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(OPTION_WIDTH)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            cfg.setting_user[self.key_name][key])
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            cfg.setting_default[self.key_name][key],
            "set_text")
        # Add layout
        layout.addWidget(getattr(
            self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_string.append(key)

    def __add_option_integer(self, idx, key, layout):
        """Integer"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(OPTION_WIDTH)
        getattr(self, f"lineedit_{key}").setValidator(int_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(cfg.setting_user[self.key_name][key]))
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_integer.append(key)

    def __add_option_float(self, idx, key, layout):
        """Float"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(OPTION_WIDTH)
        getattr(self, f"lineedit_{key}").setValidator(float_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(cfg.setting_user[self.key_name][key]))
        # Context menu
        add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.key_name][key]),
            "set_text")
        # Add layout
        layout.addWidget(
            getattr(self, f"lineedit_{key}"), idx, COLUMN_OPTION)
        self.option_float.append(key)


class ColorEdit(QLineEdit):
    """Line edit with color dialog"""

    def __init__(self, color_str):
        super().__init__()
        self.color_str = color_str

    def mouseDoubleClickEvent(self, event):
        """Double click to open color dialog"""
        if event.buttons() == Qt.LeftButton:
            color_dialog = QColorDialog()
            # Add loaded color to custom color slot 0
            color_dialog.setCustomColor(0, QColor(self.color_str))
            # Open color selector dialog
            color_get = color_dialog.getColor(
                initial=QColor(self.color_str),
                options=QColorDialog.ShowAlphaChannel
            )
            # Update color to edit box
            if color_get.isValid():
                # Add new color to custom color slot 1
                color_dialog.setCustomColor(1, color_get)
                if color_get.alpha() == 255:  # without alpha value
                    color = color_get.name(QColor.HexRgb).upper()
                else:  # with alpha value
                    color = color_get.name(QColor.HexArgb).upper()
                self.setText(color)


def add_context_menu(target, default, mode):
    """Add context menu"""
    target.setContextMenuPolicy(Qt.CustomContextMenu)
    target.customContextMenuRequested.connect(
        lambda pos,
        target=target,
        default=default,
        mode=mode:
        context_menu(pos, target, default, mode)
    )


def context_menu(pos, target, default, mode):
    """Context menu"""
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
            curr_index = target.findText(f"{default}", Qt.MatchExactly)
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
            f"background-color: {color_str};"
        )
