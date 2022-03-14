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
GUI window, events.
"""

import tkinter as tk
from ctypes import windll

from tinypedal.readapi import ReadData
from tinypedal.setting import Setting


# Access shared memory
read_data = ReadData()

# Load configuration
cfg = Setting()


class Window(tk.Tk):
    """Root window

    Hide window at startup.
    """

    def __init__(self):
        tk.Tk.__init__(self)
        self.withdraw()


class Widget(tk.Toplevel):
    """Widget window

    Create borderless, topmost window without title bar.
    Use tk.Label to create flexible text-based widget.
    Use tk.Canvas to draw shape-based widget for better performance.
    """

    def __init__(self):
        tk.Toplevel.__init__(self)

        # Base setting
        self.configure(bg="#000002")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", 1, "-transparentcolor", "#000002")
        self.lift()

        # Add to active widget list at startup
        cfg.active_widget_list.append(self)

        # Load overlay lock state at startup
        overlay_lock = OverlayLock(cfg.active_widget_list)
        overlay_lock.load_state()


class MouseEvent:
    """Widget mouse event"""

    def __init__(self):
        self.bind("<Enter>", lambda event: self.hover_enter())
        self.bind("<Leave>", lambda event: self.hover_leave())
        self.bind("<ButtonRelease-1>", lambda event: self.release_mouse())
        self.bind("<ButtonPress-1>", self.set_offset)
        self.bind("<B1-Motion>", self.update_pos)

        self.mouse_pos = (0, 0)
        self.mouse_pressed = 0

        # Create hover cover & stripe pattern
        self.hover_bg = tk.Canvas(self, bd=0, highlightthickness=0, cursor="fleur",
                                 bg=cfg.overlay["hover_color_1"])
        for lines in range(50):
            self.hover_bg.create_line(lines*-25 + 1200, -10,
                                      lines*-25 + 200, 990,
                                      fill=cfg.overlay["hover_color_2"],
                                      width=10)

    def hover_enter(self):
        """Show cover"""
        self.hover_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def hover_leave(self):
        """Hide cover if not pressed"""
        if not self.mouse_pressed:
            self.hover_bg.place(x=-9999, y=0)

    def release_mouse(self):
        """Save position on release"""
        self.save_widget_position()
        self.mouse_pressed = 0

    def set_offset(self, event):
        """Set offset position & press state"""
        self.mouse_pos = (event.x, event.y)
        self.mouse_pressed = 1

    def update_pos(self, event):
        """Update widget position"""
        self.geometry(f"+{event.x_root - self.mouse_pos[0]}+{event.y_root - self.mouse_pos[1]}")


class OverlayLock:
    """Overlay lock state"""

    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    WS_EX_NOACTIVATE = 0x08000000
    WS_EX_TRANSPARENT = 0x00000020

    def __init__(self, active_list):
        self.active_list = active_list

    def lock(self):
        """Lock overlay

        Call cfg.load() before modifying config & saving
        to avoid overriding user changes.
        """
        cfg.load()
        cfg.overlay["fixed_position"] = True
        cfg.save()

        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE | self.WS_EX_TRANSPARENT
        self.apply(ex_style)

    def unlock(self):
        """Unlock overlay"""
        cfg.load()
        cfg.overlay["fixed_position"] = False
        cfg.save()

        ex_style = self.WS_EX_LAYERED | self.WS_EX_NOACTIVATE
        self.apply(ex_style)

    def apply(self, style):
        """Apply lock

        Find HWND & loop through widget list to apply extended style.
        """
        for widget in self.active_list:
            hwnd = windll.user32.GetParent(widget.winfo_id())
            windll.user32.SetWindowLongPtrW(hwnd, self.GWL_EXSTYLE, style)

    def toggle(self):
        """Toggle lock state from tray menu"""
        if not cfg.overlay["fixed_position"]:
            self.lock()
        else:
            self.unlock()

    def load_state(self):
        """Load lock state when overlay widget is created"""
        if cfg.overlay["fixed_position"]:
            self.lock()
        else:
            self.unlock()


class OverlayAutoHide:
    """Auto hide overlay"""

    def __init__(self, active_list, master):
        self.active_list = active_list
        self.master = master

    def hide(self):
        """Hide overlay"""
        for widget in self.active_list:
            if widget.state() == "normal":  # check window state
                widget.withdraw()
            else:
                break

    def show(self):
        """Show/restore overlay"""
        for widget in self.active_list:
            if widget.state() != "normal":
                widget.deiconify()
            else:
                break

    def activate(self):
        """Auto hide overlay"""
        if cfg.overlay["auto_hide"]:
            if read_data.state():
                self.show()
            else:
                self.hide()
        else:
            self.show()

        self.master.after(500, self.activate)

    @staticmethod
    def toggle(_icon, enabled):
        """Toggle hide state"""
        cfg.load()
        cfg.overlay["auto_hide"] = not enabled.checked
        cfg.save()
