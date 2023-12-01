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
GUI window, events.
"""

from collections import namedtuple

from PySide2.QtCore import Qt, QTimer, Slot
from PySide2.QtGui import QColor, QPalette, QFont, QFontMetrics
from PySide2.QtWidgets import QWidget

from .const import APP_NAME
from .overlay_control import octrl


class Widget(QWidget):
    """Widget window"""

    def __init__(self, config, widget_name):
        super().__init__()
        self.widget_name = widget_name

        # Base config
        self.cfg = config
        self.cfg.active_widget_list.append(self)  # add to active widget list

        # Widget config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Base setting
        self.setWindowTitle(f"{APP_NAME} - {self.widget_name.capitalize()}")
        self.move(self.wcfg["position_x"], self.wcfg["position_y"])

        # Base window background color
        _pal_base = QPalette()
        _pal_base.setColor(
            QPalette.Window,
            QColor(self.cfg.compatibility["global_bkg_color"]))
        self.setPalette(_pal_base)

        # Widget mouse event
        self._mouse_pos = (0, 0)
        self._mouse_pressed = 0

        # Connect overlay-lock signal to slot
        self.__connect_signal()

        # Set update timer
        self._update_timer = QTimer(self)
        self._update_timer.setInterval(self.wcfg["update_interval"])
        self._update_timer.timeout.connect(self.update_data)

    def set_widget_state(self):
        """Set initial widget state"""
        self.__set_attribute_flag()     # window state
        octrl.overlay_lock.set_state()  # load lock state
        self._update_timer.start()      # start update
        #self.show()

    def __set_attribute_flag(self):
        """Set window flags & widget attributes"""
        self.setWindowOpacity(self.wcfg["opacity"])
        if self.cfg.compatibility["enable_translucent_background"]:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)  # remove taskbar icon
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        if self.cfg.compatibility["enable_bypass_window_manager"]:
            self.setWindowFlag(Qt.X11BypassWindowManagerHint, True)

    def mouseMoveEvent(self, event):
        """Update widget position"""
        if event.buttons() == Qt.LeftButton:
            pos = event.globalPos() - self._mouse_pos
            if self.cfg.overlay["enable_grid_move"]:
                move_size = max(int(self.cfg.compatibility["grid_move_size"]), 1)
                pos = pos / move_size * move_size
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
    def __toggle_lock(self, locked):
        """Toggle widget lock"""
        if locked:
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
        #if not self.cfg.overlay["auto_hide"]:
        #    self.show()

    @Slot(bool)
    def __toggle_hide(self, hidden):
        """Toggle widget hide"""
        if hidden:
            if self.isVisible():
                self.hide()
        else:
            if not self.isVisible():
                self.show()

    def __connect_signal(self):
        """Connect overlay-lock signal to slot"""
        octrl.overlay_lock.locked.connect(self.__toggle_lock)
        octrl.overlay_hide.hidden.connect(self.__toggle_hide)

    def __break_signal(self):
        """Disconnect signal"""
        octrl.overlay_lock.locked.disconnect(self.__toggle_lock)
        octrl.overlay_hide.hidden.disconnect(self.__toggle_hide)

    def closing(self):
        """Close widget"""
        self.__break_signal()
        self.cfg.active_widget_list.remove(self)
        self.close()

    @staticmethod
    def config_font(name="", size=1, weight=None):
        """Config font

        Two main uses:
            1. Draw text in widget that uses QPainter.
            2. Get font metrics reading for sizing elements.
        """
        font = QFont()
        font.setFamily(name)
        font.setPixelSize(size)
        if weight:
            font.setWeight(getattr(QFont, weight.capitalize()))
        return font

    @staticmethod
    def get_font_metrics(name):
        """Get font metrics"""
        return FontMetrics(
            width = QFontMetrics(name).averageCharWidth(),
            height = QFontMetrics(name).height(),
            leading = QFontMetrics(name).leading(),
            capital = QFontMetrics(name).capHeight(),
            descent = QFontMetrics(name).descent(),
        )

    def calc_font_offset(self, metrics):
        """Calculate auto font vertical offset

        Find center vertical alignment position offset
        for even space between top & bottom.
        """
        if self.wcfg["enable_auto_font_offset"]:
            return metrics.capital + metrics.descent * 2 + metrics.leading * 2 - metrics.height
        return self.wcfg["font_offset_vertical"]


FontMetrics = namedtuple(
    "FontMetrics",
    [
    "width",
    "height",
    "leading",
    "capital",
    "descent",
    ]
)
