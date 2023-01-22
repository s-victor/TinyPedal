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

from .const import PLATFORM
from .load_func import module


class Widget(tk.Toplevel):
    """Widget window

    Create borderless, topmost window without title bar.
    Use tk.Label to create flexible text-based widget.
    Use tk.Canvas to draw shape-based widget for better performance.
    """

    def __init__(self, config, widget_name):
        tk.Toplevel.__init__(self)

        # Load config
        self.cfg = config

        # Assign widget specific config
        self.wcfg = self.cfg.setting_user[widget_name]

        # Base setting
        self.configure(bg=self.cfg.overlay["transparent_color"])
        self.resizable(False, False)
        self.overrideredirect(True)
        self.attributes("-topmost", 1)
        if PLATFORM == "Windows":
            self.attributes("-transparentcolor", self.cfg.overlay["transparent_color"])
        self.lift()


class MouseEvent:
    """Widget mouse event"""

    def __init__(self):
        self.cfg.active_widget_list.append(self)  # add to active widget list
        module.overlay_lock.load_state()  # load overlay lock state

        self.bind("<Enter>", lambda event: self.hover_enter())
        self.bind("<Leave>", lambda event: self.hover_leave())
        self.bind("<ButtonRelease-1>", lambda event: self.release_mouse())
        self.bind("<ButtonPress-1>", self.set_offset)
        self.bind("<B1-Motion>", self.update_pos)

        self.mouse_pos = (0, 0)
        self.mouse_pressed = 0

        # Create hover cover & stripe pattern
        self.hover_bg = tk.Canvas(self, bd=0, highlightthickness=0, cursor="fleur",
                                  bg=self.cfg.overlay["hover_color_1"])
        for lines in range(50):
            self.hover_bg.create_line(lines*-25 + 1200, -10,
                                      lines*-25 + 200, 990,
                                      fill=self.cfg.overlay["hover_color_2"],
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
        self.wcfg["position_x"] = str(self.winfo_x())
        self.wcfg["position_y"] = str(self.winfo_y())
        self.cfg.save()
        self.mouse_pressed = 0

    def set_offset(self, event):
        """Set offset position & press state"""
        self.mouse_pos = (event.x, event.y)
        self.mouse_pressed = 1

    def update_pos(self, event):
        """Update widget position"""
        self.geometry(f"+{event.x_root - self.mouse_pos[0]}+{event.y_root - self.mouse_pos[1]}")
