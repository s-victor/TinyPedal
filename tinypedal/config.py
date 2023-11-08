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
    QMenu
)

from . import regex_pattern as rxp
from . import validator as val
from . import formatter as fmt
from .setting import cfg
from .const import APP_ICON
from .module_control import mctrl
from .widget_control import wctrl


class FontConfig(QDialog):
    """Config global font setting"""

    def __init__(self, master):
        super().__init__(master)
        self.setFixedWidth(260)
        self.setWindowTitle("Global Font Override")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Label & combobox
        self.label_fontname = QLabel("Font Name")
        self.edit_fontname = QFontComboBox()
        self.edit_fontname.setCurrentText("no change")

        self.label_fontsize = QLabel("Font Size Addend")
        self.edit_fontsize = QSpinBox()
        self.edit_fontsize.setRange(-999,999)

        self.label_fontweight = QLabel("Font Weight")
        self.edit_fontweight = QComboBox()
        self.edit_fontweight.addItems(["no change", "normal", "bold"])

        layout_option = QGridLayout()
        layout_option.setAlignment(Qt.AlignLeft | Qt.AlignTop)
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
                if (re.search(rxp.FONTNAME, key) and
                    self.edit_fontname.currentText() != "no change"):
                    dict_user[item][key] = self.edit_fontname.currentFont().family()
                if (re.search(rxp.FONTWEIGHT, key) and
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


class UnitsConfig(QDialog):
    """Config display units"""

    def __init__(self, master):
        super().__init__(master)
        self.setFixedWidth(260)
        self.setWindowTitle("Display Units")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Units type
        self.units_type = [
            "distance",
            "fuel",
            "odometer",
            "speed",
            "temperature",
            "turbo_pressure",
            "tyre_pressure",
        ]

        # Label & combobox
        self.label_distance = QLabel("Distance")
        self.combobox_distance = QComboBox()
        self.combobox_distance.addItems(["Meter", "Feet"])

        self.label_fuel = QLabel("Fuel")
        self.combobox_fuel = QComboBox()
        self.combobox_fuel.addItems(["Liter", "Gallon"])

        self.label_odometer = QLabel("Odometer")
        self.combobox_odometer = QComboBox()
        self.combobox_odometer.addItems(["Kilometer", "Mile", "Meter"])

        self.label_speed = QLabel("Speed")
        self.combobox_speed = QComboBox()
        self.combobox_speed.addItems(["KPH", "MPH", "m/s"])

        self.label_temperature = QLabel("Temperature")
        self.combobox_temperature = QComboBox()
        self.combobox_temperature.addItems(["Celsius", "Fahrenheit"])

        self.label_turbo_pressure = QLabel("Turbo Pressure")
        self.combobox_turbo_pressure = QComboBox()
        self.combobox_turbo_pressure.addItems(["bar", "psi", "kPa"])

        self.label_tyre_pressure = QLabel("Tyre Pressure")
        self.combobox_tyre_pressure = QComboBox()
        self.combobox_tyre_pressure.addItems(["kPa", "psi", "bar"])

        # Button
        button_reset = QDialogButtonBox(QDialogButtonBox.Reset)
        button_reset.clicked.connect(self.reset_setting)

        button_save = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_save.accepted.connect(self.save_setting)
        button_save.rejected.connect(self.reject)

        # Layout
        layout_main = QGridLayout()

        for idx, unit_type in enumerate(self.units_type):
            # Load selected units
            curr_index = getattr(self, f"combobox_{unit_type}").findText(
                cfg.units[f"{unit_type}_unit"], Qt.MatchExactly)
            if curr_index != -1:
                getattr(self, f"combobox_{unit_type}").setCurrentIndex(curr_index)

            # Add layout
            layout_main.addWidget(getattr(self, f"label_{unit_type}"), idx, 0)
            layout_main.addWidget(getattr(self, f"combobox_{unit_type}"), idx, 1)

        layout_main.addWidget(button_reset, len(self.units_type), 0)
        layout_main.addWidget(button_save, len(self.units_type), 1)
        self.setLayout(layout_main)

    def reset_setting(self):
        """Reset setting"""
        for unit_type in self.units_type:
            getattr(self, f"combobox_{unit_type}").setCurrentIndex(0)

    def save_setting(self):
        """Save setting"""
        for unit_type in self.units_type:
            cfg.units[f"{unit_type}_unit"] = getattr(
                self, f"combobox_{unit_type}").currentText()
        cfg.save(0)
        self.accept()  # close


class WidgetConfig(QDialog):
    """Config widget & module"""

    def __init__(self, master, obj_name, reload_mode):
        super().__init__(master)
        self.master = master
        self.obj_name = obj_name
        self.reload_mode = reload_mode

        self.number_locale = QLocale(QLocale.C)
        self.number_locale.setNumberOptions(QLocale.RejectGroupSeparator)
        self.int_valid = QIntValidator(-999999, 999999)
        self.int_valid.setLocale(self.number_locale)
        self.float_valid = QDoubleValidator(-999999.9999, 999999.9999, 4)
        self.float_valid.setLocale(self.number_locale)
        self.color_valid = QRegExpValidator(QRegExp('^#[0-9a-fA-F]*'))

        self.setWindowTitle(f"{fmt.format_option_name(obj_name)}")
        self.setWindowIcon(QIcon(APP_ICON))
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        # Option type
        self.option_bool = []
        self.option_color = []
        self.option_fontname = []
        self.option_fontweight = []
        self.option_heatmap = []
        self.option_string = []
        self.option_int = []
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
        self.create_options()
        option_box = QWidget()
        option_box.setLayout(self.layout_option)

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
        for key in self.option_bool:
            getattr(self, f"checkbox_{key}").setChecked(
                cfg.setting_default[self.obj_name][key])

        for key in self.option_color:
            getattr(self, f"lineedit_{key}").setText(
                cfg.setting_default[self.obj_name][key])

        for key in self.option_fontname:
            getattr(self, f"fontedit_{key}").setCurrentFont(
                cfg.setting_default[self.obj_name][key])

        for key in self.option_fontweight:
            curr_index = getattr(self, f"combobox_{key}").findText(
                f"{cfg.setting_default[self.obj_name][key]}", Qt.MatchExactly)
            if curr_index != -1:
                getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)

        for key in self.option_heatmap:
            curr_index = getattr(self, f"combobox_{key}").findText(
                f"{cfg.setting_default[self.obj_name][key]}", Qt.MatchExactly)
            if curr_index != -1:
                getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)

        for key in self.option_string:
            getattr(self, f"lineedit_{key}").setText(
                cfg.setting_default[self.obj_name][key])

        for key in self.option_int:
            getattr(self, f"lineedit_{key}").setText(
                str(cfg.setting_default[self.obj_name][key]))

        for key in self.option_float:
            getattr(self, f"lineedit_{key}").setText(
                str(cfg.setting_default[self.obj_name][key]))

    def save_setting(self):
        """Save setting"""
        for key in self.option_bool:
            value = getattr(self, f"checkbox_{key}").checkState()
            cfg.setting_user[self.obj_name][key] = bool(value)

        for key in self.option_color:
            cfg.setting_user[self.obj_name][key] = getattr(
                self, f"lineedit_{key}").text()

        for key in self.option_fontname:
            cfg.setting_user[self.obj_name][key] = getattr(
                self, f"fontedit_{key}").currentFont().family()

        for key in self.option_fontweight:
            cfg.setting_user[self.obj_name][key] = getattr(
                self, f"combobox_{key}").currentText()

        for key in self.option_heatmap:
            cfg.setting_user[self.obj_name][key] = getattr(
                self, f"combobox_{key}").currentText()

        for key in self.option_string:
            cfg.setting_user[self.obj_name][key] = getattr(
                self, f"lineedit_{key}").text()

        for key in self.option_int:
            cfg.setting_user[self.obj_name][key] = int(getattr(
                self, f"lineedit_{key}").text())

        for key in self.option_float:
            value = float(getattr(self, f"lineedit_{key}").text())
            if divmod(value, 1)[1] == 0:
                value = int(value)
            cfg.setting_user[self.obj_name][key] = value

        # Save changes
        cfg.save(0)
        while cfg.is_saving:  # wait saving finish
            time.sleep(0.01)

        # Select type
        if self.reload_mode == "widget":
            wctrl.close_selected(self.obj_name)
            wctrl.start_selected(self.obj_name)
            self.master.refresh_widget_list()
        elif self.reload_mode == "module":
            mctrl.close_selected(self.obj_name)
            mctrl.start_selected(self.obj_name)
            self.master.refresh_module_list()
        elif self.reload_mode == "misc":
            wctrl.close()
            wctrl.start()
        elif self.reload_mode == "api":
            self.master.restart_api()
            self.master.spectate_tab.refresh_spectate_list()

    def create_options(self):
        """Create options"""
        self.layout_option = QGridLayout()
        self.layout_option.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        key_list_user = tuple(cfg.setting_user[self.obj_name])  # create user key list
        option_width = 120
        column_index_label = 0
        column_index_option = 1

        for idx, key in enumerate(key_list_user):
            #print(key, cfg.setting_user[self.obj_name][key])
            self.__add_option_label(
                idx, key, column_index_label)
            # Bool
            if re.search(rxp.BOOL, key):
                self.__add_option_bool(
                    idx, key, option_width, column_index_option)
                continue
            # Color string
            if re.search(rxp.COLOR, key):
                self.__add_option_color(
                    idx, key, option_width, column_index_option)
                continue
            # Font name string
            if re.search(rxp.FONTNAME, key):
                self.__add_option_fontname(
                    idx, key, option_width, column_index_option)
                continue
            # Font weight string
            if re.search(rxp.FONTWEIGHT, key):
                self.__add_option_fontweight(
                    idx, key, option_width, column_index_option)
                continue
            # Heatmap string
            if re.search(rxp.HEATMAP, key):
                self.__add_option_heatmap(
                    idx, key, option_width, column_index_option)
                continue
            # String
            if re.search(rxp.STRING, key):
                self.__add_option_string(
                    idx, key, option_width, column_index_option)
                continue
            # Int
            if re.search(rxp.INTEGER, key):
                self.__add_option_integer(
                    idx, key, option_width, column_index_option)
                continue
            # Anything else
            self.__add_option_float(
                idx, key, option_width, column_index_option)

    def set_fg_color(self, color_str):
        """Set foreground color based on background color lightness"""
        if QColor(color_str).alpha() > 128 > QColor(color_str).lightness():
            return "#FFF"
        return "#000"

    def update_preview_color(self, color_str, option):
        """Update preview background color"""
        if val.color_validator(color_str):
            option.setStyleSheet(
                f"color: {self.set_fg_color(color_str)};"
                f"background-color: {color_str};"
            )

    def add_context_menu(self, target, default, mode):
        """Add context menu"""
        target.setContextMenuPolicy(Qt.CustomContextMenu)
        target.customContextMenuRequested.connect(
            lambda pos,
            target=target,
            default=default,
            mode=mode:
            self.context_menu(pos, target, default, mode)
        )

    def context_menu(self, pos, target, default, mode):
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

    def __add_option_label(self, idx, key, column_index):
        """Label"""
        setattr(self, f"label_{key}", QLabel(f"{fmt.format_option_name(key)}"))
        self.layout_option.addWidget(getattr(self, f"label_{key}"), idx, column_index)

    def __add_option_bool(self, idx, key, width, column_index):
        """Bool"""
        setattr(self, f"checkbox_{key}", QCheckBox())
        getattr(self, f"checkbox_{key}").setFixedWidth(width)
        getattr(self, f"checkbox_{key}").setChecked(cfg.setting_user[self.obj_name][key])
        # Context menu
        self.add_context_menu(
            getattr(self, f"checkbox_{key}"),
            cfg.setting_default[self.obj_name][key],
            "set_check")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"checkbox_{key}"), idx, column_index)
        self.option_bool.append(key)

    def __add_option_color(self, idx, key, width, column_index):
        """Color string"""
        setattr(self, f"lineedit_{key}", ColorEdit(cfg.setting_user[self.obj_name][key]))
        getattr(self, f"lineedit_{key}").setFixedWidth(width)
        getattr(self, f"lineedit_{key}").setMaxLength(9)
        getattr(self, f"lineedit_{key}").setValidator(self.color_valid)
        getattr(self, f"lineedit_{key}").textChanged.connect(
            lambda color_str, option=getattr(self, f"lineedit_{key}"):
            self.update_preview_color(color_str, option))
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            cfg.setting_user[self.obj_name][key])
        # Context menu
        self.add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.obj_name][key]),
            "set_text")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"lineedit_{key}"), idx, column_index)
        self.option_color.append(key)

    def __add_option_fontname(self, idx, key, width, column_index):
        """Font name string"""
        setattr(self, f"fontedit_{key}", QFontComboBox())
        getattr(self, f"fontedit_{key}").setFixedWidth(width)
        # Load selected option
        getattr(self, f"fontedit_{key}").setCurrentFont(
            cfg.setting_user[self.obj_name][key])
        # Context menu
        self.add_context_menu(
            getattr(self, f"fontedit_{key}"),
            cfg.setting_default[self.obj_name][key],
            "set_font")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"fontedit_{key}"), idx, column_index)
        self.option_fontname.append(key)

    def __add_option_fontweight(self, idx, key, width, column_index):
        """Font weight string"""
        setattr(self, f"combobox_{key}", QComboBox())
        getattr(self, f"combobox_{key}").setFixedWidth(width)
        getattr(self, f"combobox_{key}").addItems(["normal", "bold"])
        # Load selected option
        curr_index = getattr(self, f"combobox_{key}").findText(
            f"{cfg.setting_user[self.obj_name][key]}", Qt.MatchExactly)
        if curr_index != -1:
            getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)
        # Context menu
        self.add_context_menu(
            getattr(self, f"combobox_{key}"),
            cfg.setting_default[self.obj_name][key],
            "set_combo")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"combobox_{key}"), idx, column_index)
        self.option_fontweight.append(key)

    def __add_option_heatmap(self, idx, key, width, column_index):
        """Heatmap string"""
        setattr(self, f"combobox_{key}", QComboBox())
        getattr(self, f"combobox_{key}").setFixedWidth(width)
        getattr(self, f"combobox_{key}").addItems(tuple(cfg.heatmap_user))
        # Load selected option
        curr_index = getattr(self, f"combobox_{key}").findText(
            f"{cfg.setting_user[self.obj_name][key]}", Qt.MatchExactly)
        if curr_index != -1:
            getattr(self, f"combobox_{key}").setCurrentIndex(curr_index)
        # Context menu
        self.add_context_menu(
            getattr(self, f"combobox_{key}"),
            cfg.setting_default[self.obj_name][key],
            "set_combo")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"combobox_{key}"), idx, column_index)
        self.option_heatmap.append(key)

    def __add_option_string(self, idx, key, width, column_index):
        """String"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(width)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            cfg.setting_user[self.obj_name][key])
        # Context menu
        self.add_context_menu(
            getattr(self, f"lineedit_{key}"),
            cfg.setting_default[self.obj_name][key],
            "set_text")
        # Add layout
        self.layout_option.addWidget(getattr(
            self, f"lineedit_{key}"), idx, column_index)
        self.option_string.append(key)

    def __add_option_integer(self, idx, key, width, column_index):
        """Integer"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(width)
        getattr(self, f"lineedit_{key}").setValidator(self.int_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(cfg.setting_user[self.obj_name][key]))
        # Context menu
        self.add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.obj_name][key]),
            "set_text")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"lineedit_{key}"), idx, column_index)
        self.option_int.append(key)

    def __add_option_float(self, idx, key, width, column_index):
        """Float"""
        setattr(self, f"lineedit_{key}", QLineEdit())
        getattr(self, f"lineedit_{key}").setFixedWidth(width)
        getattr(self, f"lineedit_{key}").setValidator(self.float_valid)
        # Load selected option
        getattr(self, f"lineedit_{key}").setText(
            str(cfg.setting_user[self.obj_name][key]))
        # Context menu
        self.add_context_menu(
            getattr(self, f"lineedit_{key}"),
            str(cfg.setting_default[self.obj_name][key]),
            "set_text")
        # Add layout
        self.layout_option.addWidget(
            getattr(self, f"lineedit_{key}"), idx, column_index)
        self.option_float.append(key)


class ColorEdit(QLineEdit):
    """Color & line edit"""

    def __init__(self, color_str):
        super().__init__()
        self.color_str = color_str

    def mouseDoubleClickEvent(self, event):
        """Double click to open color dialog"""
        if event.buttons() == Qt.LeftButton:
            color_dialog = QColorDialog()
            color_dialog.setCustomColor(0, QColor(self.color_str))
            color_get = color_dialog.getColor(
                initial=QColor(self.color_str),
                options=QColorDialog.ShowAlphaChannel
            )
            # Update color to edit box
            if color_get.isValid():
                color_dialog.setCustomColor(1, color_get)
                if color_get.alpha() == 255:
                    color = color_get.name(QColor.HexRgb).upper()
                else:
                    color = color_get.name(QColor.HexArgb).upper()
                self.setText(color)
