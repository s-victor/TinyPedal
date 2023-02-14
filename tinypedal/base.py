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
import tkinter.font as tkfont

from .const import PLATFORM
from .module_control import module


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
        self.title("TinyPedal - " + widget_name.capitalize())
        self.configure(bg=self.cfg.overlay["transparent_color"])  # set transparent background
        self.resizable(False, False)  # disable resize
        self.overrideredirect(True)  # remove window frame
        self.attributes("-topmost", 1)  # set window always on top
        if PLATFORM == "Windows":
            self.attributes("-transparentcolor", self.cfg.overlay["transparent_color"])

        self.lift()
        self.attributes("-alpha", self.wcfg["opacity"])  # set window opacity after lift

    def add_caption(self, frame, toggle, value):
        """Create caption"""
        if self.wcfg[toggle]:
            font_desc = tkfont.Font(family=self.wcfg["font_name"],
                                    size=-int(self.wcfg["font_size"] * 0.8),
                                    weight=self.wcfg["font_weight"])
            bar_style_desc = {"bd":0, "height":1, "font":font_desc, "padx":0, "pady":0,
                              "fg":self.wcfg["font_color_caption"],
                              "bg":self.wcfg["bkg_color_caption"]}
            bar_desc = tk.Label(frame, bar_style_desc, text=value)
            bar_desc.grid(row=0, column=0, columnspan=2, padx=0, pady=0, sticky="we")


class MouseEvent:
    """Widget mouse event

    Event binding located in overlay_toggle
    """

    def __init__(self):
        self.cfg.active_widget_list.append(self)  # add to active widget list
        module.overlay_lock.load_state()  # load overlay lock state
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

    def hover_enter(self, event):
        """Show cover"""
        self.hover_bg.place(x=0, y=0, relwidth=1, relheight=1)

    def hover_leave(self, event):
        """Hide cover if not pressed"""
        if not self.mouse_pressed:
            self.hover_bg.place(x=-9999, y=0)

    def release_mouse(self, event):
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
