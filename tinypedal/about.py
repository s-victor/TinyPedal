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
About window
"""

import os
import tkinter as tk
from PIL import Image, ImageTk

from tinypedal.base import Window
from tinypedal.__init__ import VERSION

class About(Window):
    """Create about window"""

    def __init__(self):
        # Assign base setting
        Window.__init__(self)

        # Config title & background
        fg_color = "#222"
        bg_color = "#ddd"
        self.title("About")
        self.configure(bg=bg_color, padx=22, pady=12)
        self.resizable(False, False)
        self.iconbitmap("icon.ico")

        description = ("\nCopyright (C) 2022 Xiang\n\n"
                       "An open-source overlay application for racing simulation.\n\n"
                       "Licensed under the GNU General Public License v3.0 or later.\n"
                       )

        icon_source = Image.open("icon.ico")
        icon_resize = icon_source.resize((54, 54), resample=1)
        icon_image = ImageTk.PhotoImage(icon_resize)
        icon_label = tk.Label(self, image=icon_image, bg=bg_color)
        icon_label.photo = icon_image
        icon_label.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        about_title1 = tk.Label(self, text="TinyPedal", font=("Tahoma",16, "normal"),
                                padx=0, pady=0, fg=fg_color, bg=bg_color)
        about_title1.grid(row=0, column=0, padx=(62, 0), pady=(7,0), sticky="wn")

        about_version = tk.Label(self, text=f"Version: {VERSION}", font=("Tahoma",8, "normal"),
                                 padx=0, pady=0, fg=fg_color, bg=bg_color)
        about_version.grid(row=0, column=0, padx=(63, 0), pady=(34, 0), sticky="wn")

        about_text = tk.Message(self, text=description, font=("Tahoma", 8, "normal"),
                                width=190, padx=2, pady=0, fg=fg_color, bg=bg_color)
        about_text.grid(row=1, column=0, padx=0, pady=0, sticky="w")

        lbutton = tk.Button(self, text="License", bd=0, padx=4, pady=0,
                            command=self.open_license_text)
        lbutton.grid(row=2, column=0, padx=0, pady=0, sticky="w")

        tbutton = tk.Button(self, text="Third-Party Notices", bd=0, padx=4, pady=0,
                            command=self.open_thirdparty_text)
        tbutton.grid(row=2, column=0, padx=0, pady=0, sticky="e")

    @staticmethod
    def open_license_text():
        """Open LICENSE file"""
        os.startfile("LICENSE.txt")

    @staticmethod
    def open_thirdparty_text():
        """Open THIRDPARTYNOTICES file"""
        os.startfile("docs\\licenses\\THIRDPARTYNOTICES.txt")
