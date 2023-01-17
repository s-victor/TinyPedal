#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Overlay toggle
"""

import time
import threading
import platform

from . import readapi as read_data

if platform.system() == "Windows":
    from ctypes import windll

class OverlayLock:
    """Overlay lock state"""

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TRANSPARENT = 0x00000020

    def __init__(self, config):
        self.cfg = config

    def lock(self):
        """Lock overlay"""
        self.cfg.overlay["fixed_position"] = True
        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE | self.WS_EX_TRANSPARENT
        self.apply(ex_style)

    def unlock(self):
        """Unlock overlay"""
        self.cfg.overlay["fixed_position"] = False
        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE
        self.apply(ex_style)

    def apply(self, style):
        """Apply lock

        Find HWND & loop through widget list to apply extended style.
        """

        if platform.system() != "Windows":
            return

        if self.cfg.active_widget_list:
            for widget in self.cfg.active_widget_list:
                hwnd = windll.user32.GetParent(widget.winfo_id())
                windll.user32.SetWindowLongPtrW(hwnd, self.GWL_EXSTYLE, style)

    def toggle(self):
        """Toggle lock state from tray menu"""
        if not self.cfg.overlay["fixed_position"]:
            self.lock()
        else:
            self.unlock()
        self.cfg.save()

    def load_state(self):
        """Load lock state when overlay widget is created"""
        if self.cfg.overlay["fixed_position"]:
            self.lock()
        else:
            self.unlock()


class OverlayAutoHide:
    """Auto hide overlay"""

    def __init__(self, config):
        self.cfg = config
        self.running = False
        self.stopped = True

    def start(self):
        """Start auto hide thread"""
        self.running = True
        self.stopped = False
        autohide_thread = threading.Thread(target=self.__autohide)
        autohide_thread.setDaemon(True)
        autohide_thread.start()
        print("auto-hide module started")

    def hide(self):
        """Hide overlay"""
        for widget in self.cfg.active_widget_list:
            if widget.state() == "normal":  # check window state
                widget.withdraw()

    def show(self):
        """Show/restore overlay"""
        for widget in self.cfg.active_widget_list:
            if widget.state() != "normal":
                widget.deiconify()

    def __autohide(self):
        """Auto hide overlay"""
        while self.running:
            if self.cfg.active_widget_list:
                if self.cfg.overlay["auto_hide"]:
                    if read_data.state():
                        self.show()
                    else:
                        self.hide()
                else:
                    self.show()

            time.sleep(0.4)

        else:
            self.stopped = True
            print("auto-hide module closed")

    def toggle(self):
        """Toggle hide state"""
        if not self.cfg.overlay["auto_hide"]:
            self.cfg.overlay["auto_hide"] = True
        else:
            self.cfg.overlay["auto_hide"] = False
        self.cfg.save()
