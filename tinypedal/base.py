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
GUI window, events.
"""

from PySide2.QtCore import Qt, QTimer, Slot
from PySide2.QtGui import QColor, QPalette
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

        # Widget config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Base setting
        self.setWindowTitle(f"{APP_NAME} - {self.widget_name.capitalize()}")
        self.move(int(self.wcfg["position_x"]), int(self.wcfg["position_y"]))

        # Base window background color
        pal_base = QPalette()
        pal_base.setColor(QPalette.Window, QColor(self.cfg.compatibility["global_bkg_color"]))
        self.setPalette(pal_base)

        # Widget mouse event
        self.mouse_pos = (0, 0)
        self.mouse_pressed = 0

        # Connect overlay-lock signal and slot
        self.connect_signal_slot()

        # Set update timer
        self.update_timer = QTimer(self)
        self.update_timer.setInterval(self.wcfg["update_interval"])
        self.update_timer.timeout.connect(self.update_data)

    def mouseMoveEvent(self, event):
        """Update widget position"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.mouse_pos)

    def mousePressEvent(self, event):
        """Set offset position & press state"""
        if event.buttons() == Qt.LeftButton:
            self.mouse_pos = event.pos()
            self.mouse_pressed = 1

    def mouseReleaseEvent(self, event):
        """Save position on release"""
        if self.mouse_pressed:
            self.mouse_pressed = 0
            self.wcfg["position_x"] = self.x()
            self.wcfg["position_y"] = self.y()
            self.cfg.save()

    def set_widget_state(self):
        """Set initial widget state"""
        # Window flags
        self.setWindowOpacity(self.wcfg["opacity"])
        if self.cfg.compatibility["enable_translucent_background"]:
            self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)  # remove taskbar icon
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        if self.cfg.compatibility["enable_bypass_window_manager"]:
            self.setWindowFlag(Qt.X11BypassWindowManagerHint, True)

        self.cfg.active_widget_list.append(self)  # add to active widget list
        self.show()
        octrl.overlay_lock.set_state()  # load overlay lock state

    @Slot(bool)
    def toggle_lock(self, locked):
        """Toggle widget lock"""
        if locked:
            self.setWindowFlag(Qt.WindowTransparentForInput, True)
        else:
            self.setWindowFlag(Qt.WindowTransparentForInput, False)
        if not self.cfg.overlay["auto_hide"]:
            self.show()

    @Slot(bool)
    def toggle_hide(self, hidden):
        """Toggle widget hide"""
        if hidden:
            if self.isVisible():
                self.hide()
        else:
            if not self.isVisible():
                self.show()

    def connect_signal_slot(self):
        """Connect overlay-lock signal and slot"""
        octrl.overlay_lock.locked.connect(self.toggle_lock)
        octrl.overlay_hide.hidden.connect(self.toggle_hide)

    def break_signal(self):
        """Disconnect signal"""
        octrl.overlay_lock.locked.disconnect(self.toggle_lock)
        octrl.overlay_hide.hidden.disconnect(self.toggle_hide)

    def closing(self):
        """Close widget"""
        self.break_signal()
        self.cfg.active_widget_list.remove(self)
        self.close()
