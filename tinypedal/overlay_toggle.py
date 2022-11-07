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
from ctypes import windll

import tinypedal.readapi as read_data
from tinypedal.setting import cfg


class OverlayLock:
    """Overlay lock state"""

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TRANSPARENT = 0x00000020

    def lock(self, active_list):
        """Lock overlay"""
        cfg.overlay["fixed_position"] = True
        cfg.save()

        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE | self.WS_EX_TRANSPARENT
        self.apply(ex_style, active_list)

    def unlock(self, active_list):
        """Unlock overlay"""
        cfg.overlay["fixed_position"] = False
        cfg.save()

        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE
        self.apply(ex_style, active_list)

    def apply(self, style, active_list):
        """Apply lock

        Find HWND & loop through widget list to apply extended style.
        """
        for widget in active_list:
            hwnd = windll.user32.GetParent(widget.winfo_id())
            windll.user32.SetWindowLongPtrW(hwnd, self.GWL_EXSTYLE, style)

    def toggle(self, active_list):
        """Toggle lock state from tray menu"""
        if not cfg.overlay["fixed_position"]:
            self.lock(active_list)
        else:
            self.unlock(active_list)

    def load_state(self, active_list):
        """Load lock state when overlay widget is created"""
        if cfg.overlay["fixed_position"]:
            self.lock(active_list)
        else:
            self.unlock(active_list)


class OverlayAutoHide:
    """Auto hide overlay"""

    def __init__(self, active_list):
        self.active_list = active_list

        if cfg.overlay["auto_hide"]:
            self.active_state = True
        else:
            self.active_state = False

    def start(self):
        """Start auto hide thread"""
        autohide_thread = threading.Thread(target=self.__autohide)
        autohide_thread.setDaemon(True)
        autohide_thread.start()

    def hide(self):
        """Hide overlay"""
        for widget in self.active_list:
            widget.withdraw()

    def show(self):
        """Show/restore overlay"""
        for widget in self.active_list:
            if widget.state() != "normal":
                widget.deiconify()
            else:
                break

    def __autohide(self):
        """Auto hide overlay"""
        while True:
            if not self.active_state:
                break

            if read_data.state():
                self.show()
            else:
                self.hide()

            time.sleep(0.5)

    def toggle(self):
        """Toggle hide state"""
        if not cfg.overlay["auto_hide"]:
            cfg.overlay["auto_hide"] = True
            cfg.save()

            self.active_state = True
            self.start()
        else:
            cfg.overlay["auto_hide"] = False
            cfg.save()

            self.show()
            self.active_state = False
