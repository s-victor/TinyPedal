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
Overlay base window, events.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from PySide2.QtCore import Qt, Slot, QBasicTimer
from PySide2.QtGui import QPalette, QFont, QFontMetrics
from PySide2.QtWidgets import QWidget, QLabel, QLayout

from ..const import APP_NAME
from ..regex_pattern import FONT_WEIGHT_LIST
from ..overlay_control import octrl


@dataclass(frozen=True)
class FontMetrics:
    """Font metrics info"""
    width: int = 0
    height: int = 0
    leading: int = 0
    capital: int = 0
    descent: int = 0


class Overlay(QWidget):
    """Overlay window"""

    def __init__(self, config: object, widget_name: str):
        super().__init__()
        self.widget_name = widget_name
        self.closed = False
        self.state = octrl.state

        # Base config
        self.cfg = config

        # Widget config
        self.wcfg = self.cfg.user.setting[self.widget_name]

        # Base setting
        self.setWindowTitle(f"{APP_NAME} - {self.widget_name.capitalize()}")
        self.move(self.wcfg["position_x"], self.wcfg["position_y"])

        # Widget mouse event
        self._mouse_pos = (0, 0)
        self._mouse_pressed = 0
        self._move_size = max(self.cfg.compatibility["grid_move_size"], 1)

        # Set update timer
        self._update_timer = QBasicTimer()
        self._update_interval = max(
            self.wcfg["update_interval"],
            self.cfg.compatibility["minimum_update_interval"])

    def start(self):
        """Set initial widget state in orders, and start update"""
        self.__connect_signal()
        self.__set_window_style()
        self.__set_window_attributes()  # 1
        self.__set_window_flags()       # 2
        self.show()                     # 3 show before starting update
        self._update_timer.start(self._update_interval, self)

    def stop(self):
        """Stop and close widget"""
        self._update_timer.stop()
        self.__break_signal()
        self.unload_resource()
        self.closed = self.close()

    def unload_resource(self):
        """Unload resource (such as images) on close, can re-implement in widget"""
        instance_var_list = dir(self)
        for var in instance_var_list:
            # Unload all pixmap
            if re.search("pixmap_", var):
                setattr(self, var, None)

    def __set_window_attributes(self):
        """Set window attributes"""
        self.setWindowOpacity(self.wcfg["opacity"])
        if self.cfg.compatibility["enable_translucent_background"]:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def __set_window_flags(self):
        """Set window flags"""
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)  # remove taskbar icon
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        if self.cfg.compatibility["enable_bypass_window_manager"]:
            self.setWindowFlag(Qt.X11BypassWindowManagerHint, True)
        if self.cfg.overlay["fixed_position"]:  # load overlay lock state
            self.setWindowFlag(Qt.WindowTransparentForInput, True)

    def __set_window_style(self):
        """Set window style"""
        background_color = QPalette()
        background_color.setColor(QPalette.Window, self.cfg.compatibility["global_bkg_color"])
        self.setPalette(background_color)

    def mouseMoveEvent(self, event):
        """Update widget position"""
        if event.buttons() == Qt.LeftButton:
            pos = event.globalPos() - self._mouse_pos
            if self.cfg.overlay["enable_grid_move"]:
                pos = pos / self._move_size * self._move_size
            self.move(pos)

    def mousePressEvent(self, event):
        """Set offset position & press state"""
        if event.buttons() == Qt.LeftButton:
            self._mouse_pos = event.pos()
            self._mouse_pressed = 1

    def mouseReleaseEvent(self, event):
        """Save position on release"""
        if self._mouse_pressed:
            self._mouse_pressed = 0
            self.wcfg["position_x"] = self.x()
            self.wcfg["position_y"] = self.y()
            self.cfg.save()

    @Slot(bool)
    def __toggle_lock(self, locked: bool):
        """Toggle widget lock state"""
        self.setWindowFlag(Qt.WindowTransparentForInput, locked)

    @Slot(bool)
    def __toggle_hide(self, hidden: bool):
        """Toggle widget hidden state"""
        if hidden:
            if self.isVisible():
                self.hide()
        else:
            if not self.isVisible():
                self.show()

    def __connect_signal(self):
        """Connect overlay lock and hide signal"""
        octrl.state.locked.connect(self.__toggle_lock)
        octrl.state.hidden.connect(self.__toggle_hide)

    def __break_signal(self):
        """Disconnect overlay lock and hide signal"""
        octrl.state.locked.disconnect(self.__toggle_lock)
        octrl.state.hidden.disconnect(self.__toggle_hide)

    # Common GUI methods
    @staticmethod
    def config_font(name: str = "", size: int = 1, weight: str = "") -> QFont:
        """Config font

        Used for draw text in widget that uses QPainter,
        or get font metrics reading for sizing elements.

        Args:
            name: font name string.
            size: font size in pixel.
            weight (optional): font weight name string, convert name to capital.

        Returns:
            QFont object.
        """
        font = QFont()
        font.setFamily(name)
        font.setPixelSize(size)
        if weight:
            font.setWeight(getattr(QFont, weight.capitalize()))
        return font

    @staticmethod
    def get_font_metrics(qfont: QFont) -> FontMetrics:
        """Get font metrics

        Args:
            qfont: QFont object.

        Returns:
            FontMetrics object.
        """
        font_metrics = QFontMetrics(qfont)
        return FontMetrics(
            width = font_metrics.averageCharWidth(),
            height = font_metrics.height(),
            leading = font_metrics.leading(),
            capital = font_metrics.capHeight(),
            descent = font_metrics.descent(),
        )

    def calc_font_offset(self, metrics: FontMetrics) -> int:
        """Calculate auto font vertical offset

        Find difference between actual height and height reading
        and use as offset for center vertical alignment position
        for overlay that uses QPainter drawing.

        Args:
            metrics: FontMetrics object.

        Returns:
            Calculated font offset in pixel.
        """
        if self.wcfg["enable_auto_font_offset"]:
            return metrics.capital + metrics.descent * 2 + metrics.leading * 2 - metrics.height
        return self.wcfg["font_offset_vertical"]

    @staticmethod
    def set_text_alignment(align: int | str = 0) -> Qt.AlignmentFlag:
        """Set text alignment

        Args:
            align:
            0 (center alignment).
            1 or "Left" (left alignment).
            2 or "Right" (right alignment).

        Returns:
            Qt alignment.
        """
        if align in (1, "Left"):
            return Qt.AlignLeft
        if align in (2, "Right"):
            return Qt.AlignRight
        return Qt.AlignCenter

    @staticmethod
    def set_qss(
        fg_color: str = "", bg_color: str = "",
        font_family: str = "", font_size: int = -1, font_weight: str = "") -> str:
        """Set qt style sheet

        Args:
            fg_color: foreground color.
            bg_color: background color.
            font_family: font family name string.
            font_size: font size in pixel.
            font_weight: font weight string, "normal" or "bold".

        Returns:
            Qt style sheet string.
        """
        if fg_color:
            fg_color = f"color:{fg_color};"
        if bg_color:
            bg_color = f"background:{bg_color};"
        if font_family:
            font_family = f"font-family:{font_family};"
        if font_size >= 0:
            font_size = f"font-size:{font_size}px;"
        else:
            font_size = ""
        if font_weight in FONT_WEIGHT_LIST:
            font_weight = f"font-weight:{font_weight};"
        return f"{fg_color}{bg_color}{font_family}{font_size}{font_weight}"

    def add_qlabel(
        self, text: str = "", style: str = "", width: int = 0,
        align: int = 0) -> QLabel:
        """Add a single qlabel instance

        Args:
            text: label text.
            style: qt style sheet.
            width: label width in pixel.
            align: 0 (center), 1 (left), 2 (right).

        Returns:
            QLabel instance.
        """
        bar_temp = QLabel(text)
        bar_temp.setAlignment(self.set_text_alignment(align))
        bar_temp.setStyleSheet(style)
        if width > 0:
            bar_temp.setMinimumWidth(width)
        return bar_temp

    def set_qlabel(
        self, text: str = "", style: str = "", width: int = 0,
        align: int = 0, count: int = 1) -> (tuple[QLabel] | QLabel):
        """Set qlabel

        Args:
            text: label text.
            style: qt style sheet.
            width: label width in pixel.
            align: 0 (center), 1 (left), 2 (right)
            count: number of qlabel to set.

        Returns:
            A single or multiple(tuple) QLabel instances,
            depends on count value (default 1).
        """
        if count > 1:
            return tuple(
                self.add_qlabel(text, style, width, align)
                for _ in range(count)
            )
        return self.add_qlabel(text, style, width, align)

    def set_layout_orient(
        self, layout: QLayout, target: QWidget | QLayout, column: int):
        """Set widget or layout orientation in vertical or horizontal

        Args:
            target_type: 0 (widget), 1 (layout).
            layout: primary layout.
            target: QWidget or QLayout.
            column: column index.
        """
        if self.wcfg["layout"] == 0:  # Vertical layout
            if isinstance(target, QWidget):
                layout.addWidget(target, column, 0)
            else:
                layout.addLayout(target, column, 0)
        else:  # Horizontal layout
            if isinstance(target, QWidget):
                layout.addWidget(target, 0, column)
            else:
                layout.addLayout(target, 0, column)
