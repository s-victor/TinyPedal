#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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

from typing import Any, NamedTuple

from PySide2.QtCore import QBasicTimer, Qt, Slot
from PySide2.QtGui import QFont, QFontMetrics, QPalette, QPixmap
from PySide2.QtWidgets import QGridLayout, QLabel, QLayout, QWidget

from .. import regex_pattern as rxp
from ..const_app import APP_NAME
from ..overlay_control import octrl
from ..setting import Setting

FONT_WEIGHT_LIST = rxp.CHOICE_COMMON[rxp.CFG_FONT_WEIGHT]


class Overlay(QWidget):
    """Overlay window"""

    def __init__(self, config: Setting, widget_name: str):
        super().__init__()
        self.widget_name = widget_name
        self.closed = False
        self.state = octrl.state

        # Base config
        self.cfg = config

        # Widget config
        self.wcfg = self.cfg.user.setting[widget_name]
        validate_column_order(self.wcfg)

        # Base setting
        self.setWindowTitle(f"{APP_NAME} - {widget_name.capitalize()}")
        self.move(self.wcfg["position_x"], self.wcfg["position_y"])

        # Widget mouse event
        self._mouse_pos = None

        # Set update timer
        self._update_timer = QBasicTimer()

    def start(self):
        """Set initial widget state in orders, and start update"""
        self.__connect_signal()
        self.__set_window_style()
        self.__set_window_attributes()  # 1
        self.__set_window_flags()  # 2
        update_interval = max(
            self.wcfg["update_interval"],
            self.cfg.application["minimum_update_interval"],
        )
        self._update_timer.start(update_interval, self)

    def stop(self):
        """Stop and close widget"""
        self._update_timer.stop()
        self.__break_signal()
        self.unload_resource()
        self.wcfg = None
        self.cfg = None
        self.state = None
        self.closed = self.close()

    def unload_resource(self):
        """Unload resource (such as images) on close, can re-implement in widget"""
        instance_var_list = dir(self)
        for var in instance_var_list:
            if var.startswith("pixmap_"):  # unload all pixmap instance
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
        # Unhide taskbar widget window & icon if VR compatibility option enabled
        self.setWindowFlag(Qt.Tool, not self.cfg.overlay["vr_compatibility"])
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        if self.cfg.compatibility["enable_bypass_window_manager"]:
            self.setWindowFlag(Qt.X11BypassWindowManagerHint, True)
        if self.cfg.overlay["fixed_position"]:  # load overlay lock state
            self.setWindowFlag(Qt.WindowTransparentForInput, True)

    def __set_window_style(self):
        """Set window style"""
        background_color = QPalette()
        background_color.setColor(
            QPalette.Window,
            self.cfg.compatibility["global_bkg_color"],
        )
        self.setPalette(background_color)

    def mouseMoveEvent(self, event):
        """Update widget position"""
        if self._mouse_pos and event.buttons() == Qt.LeftButton:
            pos = event.globalPos() - self._mouse_pos
            if self.cfg.overlay["enable_grid_move"]:
                move_size = max(self.cfg.application["grid_move_size"], 1)
                pos = pos / move_size * move_size
            self.move(pos)

    def mousePressEvent(self, event):
        """Set offset position & press state"""
        # Make sure overlay cannot be dragged while "fixed_position" enabled
        if self.cfg.overlay["fixed_position"]:
            return
        if event.buttons() == Qt.LeftButton:
            self._mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        """Save position on release"""
        if self._mouse_pos:
            self._mouse_pos = None
            self.wcfg["position_x"] = self.x()
            self.wcfg["position_y"] = self.y()
            self.cfg.save()

    @Slot(bool)
    def __toggle_lock(self, locked: bool):
        """Toggle widget lock state"""
        self.setWindowFlag(Qt.WindowTransparentForInput, locked)

    @Slot(bool)
    def __toggle_vr_compat(self, enabled: bool):
        """Toggle widget VR compatibility"""
        self.setWindowFlag(Qt.Tool, not enabled)

    def __connect_signal(self):
        """Connect overlay lock and hide signal"""
        self.state.locked.connect(self.__toggle_lock)
        self.state.hidden.connect(self.setHidden)
        self.state.vr_compat.connect(self.__toggle_vr_compat)

    def __break_signal(self):
        """Disconnect overlay lock and hide signal"""
        self.state.locked.disconnect(self.__toggle_lock)
        self.state.hidden.disconnect(self.setHidden)
        self.state.vr_compat.disconnect(self.__toggle_vr_compat)

    def closeEvent(self, event):
        """Ignore attempts to close via window Close button when VR compatibility enabled"""
        if self.state is not None:
            event.ignore()

    # Common GUI methods
    @staticmethod
    def config_font(name: str = "", size: int = 1, weight: str = "") -> QFont:
        """Config font

        Used for draw text in widget that uses QPainter,
        or get font metrics reading for sizing elements.

        Args:
            name: font name string.
            size: font size in pixel, minimum limit 1px.
            weight (optional): font weight name string, convert name to capital.

        Returns:
            QFont object.
        """
        font = QFont()
        font.setFamily(name)
        font.setPixelSize(max(size, 1))
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
            width=font_metrics.averageCharWidth(),
            height=font_metrics.height(),
            leading=font_metrics.leading(),
            capital=font_metrics.capHeight(),
            descent=font_metrics.descent(),
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
            return (
                metrics.capital
                + metrics.descent * 2
                + metrics.leading * 2
                - metrics.height
            )
        return self.wcfg["font_offset_vertical"]

    @staticmethod
    def set_padding(size: int, scale: float, side: int = 2) -> int:
        """Set padding

        Args:
            size: reference font size in pixel.
            scale: scale font size for relative padding.
            side: number of sides to add padding.

        Returns:
            Padding size in pixel.
        """
        return round(size * scale) * side

    @staticmethod
    def set_text_alignment(align: int | str = 0) -> Qt.Alignment:
        """Set text alignment

        Args:
            align: 0 or "Center", 1 or "Left", 2 or "Right".

        Returns:
            Qt alignment.
        """
        if align == 0 or align == "Center":
            return Qt.AlignCenter
        if align == 1 or align == "Left":
            return Qt.AlignLeft
        return Qt.AlignRight

    @staticmethod
    def set_qss(
        fg_color: str = "",
        bg_color: str = "",
        font_family: str = "",
        font_size: int = -1,
        font_weight: str = "",
    ) -> str:
        """Set qt style sheet

        Args:
            fg_color: foreground color.
            bg_color: background color.
            font_family: font family name string.
            font_size: font size in pixel, minimum limit 1px.
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
            font_size_pixel = f"font-size:{max(font_size, 1)}px;"
        else:
            font_size_pixel = ""
        if font_weight in FONT_WEIGHT_LIST:
            font_weight = f"font-weight:{font_weight};"
        return f"{fg_color}{bg_color}{font_family}{font_size_pixel}{font_weight}"

    def __add_qlabel(
        self,
        *,
        text: str | None = None,
        pixmap: QPixmap | None = None,
        style: str | None = None,
        width: int = 0,
        height: int = 0,
        fixed_width: int = 0,
        fixed_height: int = 0,
        align: int | str = 0,
        last: Any | None = None,
    ) -> QLabel:
        """Add a single qlabel instance, keyword arguments only

        Args:
            text: label text.
            pixmap: pixmap image.
            style: qt style sheet.
            width: minimum label width in pixel.
            height: minimum label height in pixel.
            fixed_width: fixed label width in pixel, takes priority over width.
            fixed_height: fixed label height in pixel, takes priority over height.
            align: 0 or "Center", 1 or "Left", 2 or "Right".
            last: cache last data for comparison.

        Returns:
            QLabel instance.
        """
        bar_temp = QLabel(self)
        bar_temp.setTextFormat(Qt.PlainText)
        bar_temp.setTextInteractionFlags(Qt.NoTextInteraction)

        if text is not None:
            bar_temp.setText(text)

        if pixmap is not None:
            bar_temp.setPixmap(pixmap)

        if style is not None:
            bar_temp.setStyleSheet(style)

        if fixed_width > 0:
            bar_temp.setFixedWidth(fixed_width)
        elif width > 0:
            bar_temp.setMinimumWidth(width)

        if fixed_height > 0:
            bar_temp.setFixedHeight(fixed_height)
        elif height > 0:
            bar_temp.setMinimumHeight(height)

        bar_temp.setAlignment(self.set_text_alignment(align))
        bar_temp.last = last
        return bar_temp

    def set_qlabel(
        self,
        *,
        text: str | None = None,
        pixmap: QPixmap | None = None,
        style: str | None = None,
        width: int = 0,
        height: int = 0,
        fixed_width: int = 0,
        fixed_height: int = 0,
        align: int | str = 0,
        last: Any | None = None,
        count: int = 1,
    ) -> tuple[QLabel, ...] | QLabel:
        """Set qlabel, keyword arguments only

        Args:
            text: label text.
            pixmap: pixmap image.
            style: qt style sheet.
            width: minimum label width in pixel.
            height: minimum label height in pixel.
            fixed_width: fixed label width in pixel, takes priority over width.
            fixed_height: fixed label height in pixel, takes priority over height.
            align: 0 or "Center", 1 or "Left", 2 or "Right".
            last: cache last data for comparison.
            count: number of qlabel to set.

        Returns:
            A single or multiple(tuple) QLabel instances,
            depends on count value (default 1).
        """
        bar_set = (
            self.__add_qlabel(
                text=text,
                pixmap=pixmap,
                style=style,
                width=width,
                height=height,
                fixed_width=fixed_width,
                fixed_height=fixed_height,
                align=align,
                last=last,
            )
            for _ in range(count)
        )
        if count > 1:
            return tuple(bar_set)
        return next(bar_set)

    @staticmethod
    def set_grid_layout_vert(
        layout: QGridLayout,
        targets: tuple[QWidget, ...],
        row_start: int = 1,
        column: int = 4,
    ):
        """Set grid layout - vertical

        Default row index start from 1; reserve row index 0 for caption.
        """
        for index, target in enumerate(targets):
            layout.addWidget(target, index + row_start, column)

    @staticmethod
    def set_grid_layout_quad(
        layout: QGridLayout,
        targets: tuple[QWidget | QLayout, ...],
        row_start: int = 1,
        column_left: int = 0,
        column_right: int = 9,
    ):
        """Set grid layout - quad - (0,1), (2,3), (4,5), ...

        Default row index start from 1; reserve row index 0 for caption.
        """
        for index, target in enumerate(targets):
            row_index = row_start + (index // 2)
            column_index = column_left + (index % 2) * column_right
            if isinstance(target, QWidget):
                layout.addWidget(target, row_index, column_index)
            else:
                layout.addLayout(target, row_index, column_index)

    @staticmethod
    def set_grid_layout_table_row(
        layout: QGridLayout,
        targets: tuple[QWidget, ...],
        row_index: int = 0,
        right_to_left: bool = False,
        hide_start: int = 99999,
    ):
        """Set grid layout - table by keys of each row"""
        if right_to_left:
            targets = reversed(targets)
        for column_index, target in enumerate(targets):
            layout.addWidget(target, row_index, column_index)
            if hide_start <= column_index:
                target.hide()

    @staticmethod
    def set_grid_layout_table_column(
        layout: QGridLayout,
        targets: tuple[QWidget, ...],
        column_index: int = 0,
        bottom_to_top: bool = False,
        hide_start: int = 99999,
    ):
        """Set grid layout - table by keys of each column"""
        if bottom_to_top:
            targets = reversed(targets)
        for row_index, target in enumerate(targets):
            layout.addWidget(target, row_index, column_index)
            if hide_start <= row_index:
                target.hide()

    @staticmethod
    def set_grid_layout(
        gap: int = 0,
        gap_hori: int = -1,
        gap_vert: int = -1,
        margin: int = -1,
        align: Qt.Alignment | None = None,
    ) -> QGridLayout:
        """Set grid layout (QGridLayout)"""
        layout = QGridLayout()
        layout.setSpacing(gap)
        if gap_hori >= 0:
            layout.setHorizontalSpacing(gap_hori)
        if gap_vert >= 0:
            layout.setVerticalSpacing(gap_vert)
        if margin >= 0:
            layout.setContentsMargins(margin, margin, margin, margin)
        if align is not None:
            layout.setAlignment(align)
        return layout

    def set_primary_layout(
        self,
        layout: QLayout,
        margin: int = 0,
        align: Qt.Alignment | None = Qt.AlignLeft | Qt.AlignTop,
    ):
        """Set primary layout"""
        layout.setContentsMargins(margin, margin, margin, margin)
        if align is not None:
            layout.setAlignment(align)
        self.setLayout(layout)

    def set_primary_orient(
        self,
        target: QWidget | QGridLayout,
        column: int = 0,
        row: int = 0,
        option: str = "layout",
        default: str | int = 0,
    ):
        """Set primary layout (QGridLayout) orientation

        Orientation is defined by "layout" option in Widget JSON.
        0 = vertical, 1 = horizontal.

        Args:
            target: QWidget or QGridLayout that adds to primary layout.
            column: column index determines display order.
            row: row index determines side display order.
            option: layout option name in Widget JSON.
            default: default layout value.
        """
        if self.wcfg.get(option, 0) == default:
            order = column, row  # Vertical layout
        else:
            order = row, column  # Horizontal layout
        if isinstance(target, QWidget):
            self.layout().addWidget(target, *order)
        else:
            self.layout().addLayout(target, *order)


def validate_column_order(config: dict):
    """Validate column/row index order, correct any overlapping indexes"""
    column_set = []
    for key in config.keys():
        if key.startswith("column_index"):
            while config[key] in column_set:
                config[key] += 1
            column_set.append(config[key])


class FontMetrics(NamedTuple):
    """Font metrics info"""

    width: int = 0
    height: int = 0
    leading: int = 0
    capital: int = 0
    descent: int = 0
