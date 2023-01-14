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
Root window
"""

import os
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk

from .setting import cfg


VERSION = "1.10.1"


class About(tk.Tk):
    """Create about window

    Hide window at startup.
    """

    def __init__(self):
        # Assign base setting
        tk.Tk.__init__(self)
        self.withdraw()

        # Config title & background
        fg_color = "#222"
        bg_color = "#ddd"
        self.title("About")
        self.configure(bg=bg_color, padx=22, pady=12)
        self.resizable(False, False)
        self.iconbitmap("icon.ico")

        # Center window
        wnd_posx = int((self.winfo_screenwidth() / 2) - self.winfo_width())
        wnd_posy = int((self.winfo_screenheight() / 2) - self.winfo_height())
        self.geometry(f"+{wnd_posx}+{wnd_posy}")

        description = (
            "\nCopyright (C) 2022 Xiang\n\n"
            "An open-source overlay application for racing simulation.\n\n"
            "Licensed under the GNU General Public License v3.0 or later.\n"
            )

        with Image.open("icon.ico") as icon_source:
            icon_resize = icon_source.resize((54, 54), resample=1)
        icon_image = ImageTk.PhotoImage(icon_resize)
        icon_label = tk.Label(self, image=icon_image, bg=bg_color)
        icon_label.image = icon_image
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


def start_tray(master):
    """Start tray icon"""
    from tinypedal.tray import TrayIcon
    tray_icon = TrayIcon(master)
    tray_icon.start_tray()
    tray_icon.start_widget()


class LoadPreset(tk.Toplevel):
    """Load setting preset window"""

    def __init__(self, root, tray):
        tk.Toplevel.__init__(self)
        self.root = root
        self.tray = tray
        self.attributes("-topmost", 1)

        # Base setting
        fg_color = "#222"
        bg_color = "#FFF"
        bd_color = "#AAA"
        btn_color = "#E0E0E0"
        hi_color = "#ff2b00"
        font_list = ("Tahoma", 12, "normal")
        font_btn = ("Tahoma", 11, "normal")

        self.title("Preset Manager")
        self.configure(bg="#EEE")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")

        # Center window
        wnd_posx = int((self.winfo_screenwidth() / 2) - self.winfo_width())
        wnd_posy = int((self.winfo_screenheight() / 2) - self.winfo_height())
        self.geometry(f"+{wnd_posx}+{wnd_posy}")

        # Create stripe background
        stripe_bg = tk.Canvas(self, bd=0, highlightthickness=0, bg="#E0E0E0")
        for lines in range(50):
            stripe_bg.create_line(lines*-25 + 1200, -10,
                                  lines*-25 + 200, 990,
                                  fill="#EAEAEA",
                                  width=10)
        stripe_bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Button
        frame_btn1 = tk.Frame(self, bd=1, highlightthickness=1,
                              bg=bg_color, highlightbackground=bd_color)
        frame_btn1.grid(row=1, column=0, padx=(10,0), pady=(2,10), sticky="w")

        load_btn = tk.Button(frame_btn1, text="Load Preset", font=font_btn,
                             command=self.loading,
                             bd=0, width=12, highlightthickness=0,
                             activeforeground=bg_color, activebackground=hi_color,
                             fg=fg_color, bg=btn_color)
        load_btn.grid(row=0, column=0, padx=0, pady=0)

        refresh_btn = tk.Button(frame_btn1, text="Refresh", font=font_btn,
                                command=self.refresh_list,
                                bd=0, width=8, highlightthickness=0,
                                activeforeground=bg_color, activebackground=hi_color,
                                fg=fg_color, bg=btn_color)
        refresh_btn.grid(row=0, column=1, padx=(1,0), pady=0)

        frame_btn2 = tk.Frame(self, bd=1, highlightthickness=1,
                              bg=bg_color, highlightbackground=bd_color)
        frame_btn2.grid(row=1, column=0, padx=(0,10), pady=(2,10), sticky="e")

        create_btn = tk.Button(frame_btn2, text="New", font=font_btn,
                               command=self.open_create_window,
                               bd=0, width=5, highlightthickness=0,
                               activeforeground=bg_color, activebackground=hi_color,
                               fg=fg_color, bg=btn_color)
        create_btn.grid(row=0, column=0, padx=0, pady=0)

        # Assign config file list
        self.preset_list, self.preset_list_var = self.load_file_list()

        # Listbox
        self.preset_box = tk.Listbox(self, listvariable=self.preset_list_var, font=font_list,
                                     activestyle="none", bd=3, relief="flat",
                                     width=30, height=12, highlightthickness=1,
                                     fg=fg_color, bg=bg_color,
                                     highlightbackground=bd_color, highlightcolor=bd_color,
                                     selectbackground=hi_color)
        self.preset_box.grid(row=0, column=0, padx=10, pady=(10,0))

        sbar_p = ttk.Scrollbar(self, orient="vertical", command=self.preset_box.yview)
        self.preset_box.config(yscrollcommand=sbar_p.set)
        sbar_p.grid(column=0, row=0, padx=(0,11), pady=(11,1), sticky="ens")

        # Set default selection
        self.preset_box.selection_set(0)
        self.preset_box.see(0)

    def refresh_list(self):
        """Refresh preset list"""
        self.preset_list, self.preset_list_var = self.load_file_list()
        self.preset_box.config(listvariable=self.preset_list_var)

    @staticmethod
    def load_file_list():
        """Load config file list from app folder"""
        cfg_list = cfg.load_preset_list()
        cfg_list_var = tk.StringVar()
        cfg_list_var.set(cfg_list)
        return cfg_list, cfg_list_var

    def loading(self):
        """Load selected preset"""
        if self.preset_box.curselection():  # check whether selected
            self.tray.close_widget()

            selected_index = self.preset_box.curselection()[0]
            cfg.filename = f"{self.preset_list[selected_index]}.json"
            cfg.load()  # load new setting

            self.tray.close_preset_window(self)  # close window
            self.tray.start_widget()
        else:
            messagebox.showwarning(
                title="Warning",
                message="No preset selected.\nPlease select a preset to continue.",
                parent=self
                )

    def open_create_window(self):
        """Create new preset window"""
        createpreset = CreatePreset(self, self.preset_list)
        createpreset.focus_set()


class CreatePreset(tk.Toplevel):
    """Create preset window"""

    def __init__(self, master, preset_list):
        tk.Toplevel.__init__(self)
        self.master = master
        self.preset_list = preset_list
        self.grab_set()
        self.attributes("-topmost", 1)

        # Base setting
        fg_color = "#222"
        bg_color = "#FFF"
        bd_color = "#AAA"
        btn_color = "#E0E0E0"
        hi_color = "#ff2b00"

        self.title("New Preset")
        self.configure(bg="#EEE")
        self.resizable(False, False)
        self.iconbitmap("icon.ico")
        self.attributes("-toolwindow", 1)

        # Center window
        wnd_posx = int((self.winfo_screenwidth() / 2) - self.winfo_width())
        wnd_posy = int((self.winfo_screenheight() / 2) - self.winfo_height() + 100)
        self.geometry(f"+{wnd_posx}+{wnd_posy}")

        # Create stripe background
        stripe_bg = tk.Canvas(self, bd=0, highlightthickness=0, bg="#E0E0E0")
        for lines in range(50):
            stripe_bg.create_line(lines*-25 + 1200, -10,
                                  lines*-25 + 200, 990,
                                  fill="#EAEAEA",
                                  width=10)
        stripe_bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Button
        frame_btn = tk.Frame(self, bd=1, highlightthickness=1,
                             bg=bg_color, highlightbackground=bd_color)
        frame_btn.grid(row=1, column=0, padx=10, pady=(2,10), sticky="e")
        create_btn = tk.Button(frame_btn, text="Create Preset", font=("Tahoma", 11, "normal"),
                               command=self.creating,
                               bd=0, width=13, highlightthickness=0,
                               activeforeground=bg_color, activebackground=hi_color,
                               fg=fg_color, bg=btn_color)
        create_btn.grid(row=0, column=1, padx=0, pady=0)

        # Entry box
        valid_input = (self.register(self.is_valid_char), "%P")

        self.preset_name = tk.StringVar()
        preset_entry = tk.Entry(self, textvariable=self.preset_name, font=("Tahoma", 12, "normal"),
                                bd=2, relief="flat", width=30, highlightthickness=1,
                                fg=fg_color, bg=bg_color,
                                highlightbackground=bd_color, highlightcolor=bd_color,
                                validate="key",  validatecommand=valid_input)
        preset_entry.grid(row=0, column=0, padx=10, pady=(10,0))
        preset_entry.focus_set()

    @staticmethod
    def is_valid_char(input_char):
        """Validate input characters"""
        return re.search('[\\\\/:*?"<>|]', input_char) is None

    def creating(self):
        """Creating new preset"""
        valid = True
        entered_filename = self.preset_name.get()
        if entered_filename.endswith(".json"):
            entered_filename = entered_filename[:-5]

        invalid_filename = ("", "classes")

        if entered_filename.lower() not in invalid_filename:
            for preset in self.preset_list:
                if entered_filename.lower() == preset.lower():
                    valid = False
                    break

            if valid:
                cfg.filename = f"{entered_filename}.json"
                cfg.create()  # create setting
                cfg.save()  # save setting
                self.master.refresh_list()  # refresh preset list
                self.destroy()  # close window
            else:
                messagebox.showwarning(
                    title="Warning",
                    message="Preset already exists.",
                    parent=self
                    )
