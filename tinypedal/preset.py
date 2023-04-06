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
Preset window
"""

import threading
import signal
import re
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from .setting import cfg
from .const import APP_NAME, VERSION, PLATFORM
from .readapi import info
from .module_control import module
from .widget_control import wctrl, WIDGET_PACK


class LoadPreset(tk.Toplevel):
    """Load setting preset window"""

    def __init__(self, master):
        tk.Toplevel.__init__(self)
        self.master = master

        # Base setting
        fg_color = "#222"
        bg_color = "#FFF"
        bd_color = "#AAA"
        btn_color = "#E0E0E0"
        hi_color = "#ff2b00"
        font_list = ("Tahoma", 12, "normal")
        font_btn = ("Tahoma", 11, "normal")

        self.title(f"{APP_NAME} v{VERSION}")
        self.configure(bg="#EEE")
        self.resizable(False, False)

        # Menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        menu_config = tk.Menu(menubar, tearoff=0)
        menu_widgets = tk.Menu(menubar, tearoff=0)
        menu_help = tk.Menu(menubar, tearoff=0)

        # Config menu
        menubar.add_cascade(label="Config", menu=menu_config)

        self.chk_lock = tk.BooleanVar()
        self.chk_lock.set(cfg.overlay["fixed_position"])
        menu_config.add_checkbutton(label="Lock Overlay", onvalue=1, offvalue=0,
                                    variable=self.chk_lock,
                                    command=module.overlay_lock.toggle)

        self.chk_autohide = tk.BooleanVar()
        self.chk_autohide.set(cfg.overlay["auto_hide"])
        menu_config.add_checkbutton(label="Auto Hide", onvalue=1, offvalue=0,
                                    variable=self.chk_autohide,
                                    command=module.overlay_hide.toggle)

        # Widgets menu
        menubar.add_cascade(label="Widgets", menu=menu_widgets)
        for obj in WIDGET_PACK:
            setattr(self, f"chk_{obj.WIDGET_NAME}", tk.BooleanVar())
            getattr(self, f"chk_{obj.WIDGET_NAME}").set(cfg.setting_user[obj.WIDGET_NAME]["enable"])
            menu_widgets.add_checkbutton(label=self.format_widget_name(obj.WIDGET_NAME),
                                         onvalue=1, offvalue=0,
                                         variable=getattr(self, f"chk_{obj.WIDGET_NAME}"),
                                         command=lambda wname=obj.WIDGET_NAME: wctrl.toggle(wname)
                                         )

        # Help menu
        menubar.add_cascade(label="Help", menu=menu_help)
        menu_help.add_command(label="About", command=self.master.deiconify)

        # Create stripe background
        stripe_bg = tk.Canvas(self, bd=0, highlightthickness=0, bg="#E0E0E0")
        for lines in range(50):
            stripe_bg.create_line(lines*-25 + 1200, -10,
                                  lines*-25 + 200, 990,
                                  fill="#EAEAEA", width=10)
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

        # Center window position
        wnd_posx = int((self.winfo_screenwidth() / 2) - self.winfo_reqwidth())
        wnd_posy = int((self.winfo_screenheight() / 2) - self.winfo_reqheight())
        self.geometry(f"+{wnd_posx}+{wnd_posy}")

        # Start modules & widgets
        signal.signal(signal.SIGINT, self.int_signal_handler)
        module.start()  # 1 start module
        wctrl.start()  # 2 start widget
        module.overlay_hide.widget_loaded = True

        # Platform specify
        if PLATFORM == "Windows":
            self.iconbitmap("icon.ico")
            self.protocol("WM_DELETE_WINDOW", self.hide)
            self.withdraw()
            self.start_tray_icon()
        else:
            self.iconphoto(True, tk.PhotoImage(file="icon.png"))
            self.protocol("WM_DELETE_WINDOW", self.quit_app)
            self.iconify()

    def open_create_window(self):
        """Create new preset window"""
        createpreset = CreatePreset(self, self.preset_list)
        createpreset.focus_set()

    def refresh_list(self):
        """Refresh preset list"""
        self.preset_list, self.preset_list_var = self.load_file_list()
        self.preset_box.config(listvariable=self.preset_list_var)

    def refresh_menu(self):
        """Refresh menu"""
        self.chk_lock.set(cfg.overlay["fixed_position"])
        self.chk_autohide.set(cfg.overlay["auto_hide"])
        for obj in WIDGET_PACK:
            getattr(self, f"chk_{obj.WIDGET_NAME}").set(cfg.setting_user[obj.WIDGET_NAME]["enable"])

    def start_tray_icon(self):
        """Start tray icon (for Windows)"""
        from tinypedal.tray import TrayIcon
        self.tray_icon = TrayIcon(self.master, self)
        self.tray_icon.start()

    def hide(self):
        """Hide preset manager & refresh tray menu (for Windows)"""
        self.tray_icon.tray.update_menu()
        self.withdraw()

    def unhide(self):
        """Unhide preset manager & refresh (for Windows)"""
        self.refresh_menu()
        self.refresh_list()
        self.deiconify()

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
            # Close modules & widgets in order
            module.stop()
            wctrl.close()
            module.overlay_hide.widget_loaded = False

            # Load new setting
            selected_index = self.preset_box.curselection()[0]
            cfg.filename = f"{self.preset_list[selected_index]}.json"
            cfg.load()

            # Start modules & widgets
            module.start()
            wctrl.start()
            module.overlay_hide.widget_loaded = True

            # Refresh menu & preset list
            self.refresh_menu()
            self.refresh_list()

            # Update tray icon menu & hide preset window
            if PLATFORM == "Windows":
                self.hide()

        else:
            messagebox.showwarning(
                title="Warning",
                message="No preset selected.\nPlease select a preset to continue.",
                parent=self
                )

    def quit(self):
        """Quit manager"""
        if not cfg.active_widget_list:
            self.deiconify()  # prevent app hanging if no widgets enabled while exiting
        module.stop()  # stop module
        self.master.quit()  # close root window
        info.stopUpdating()  # stop sharedmemory synced player data updating thread
        info.close()  # stop sharedmemory mapping
        if PLATFORM == "Windows":
            self.tray_icon.tray.stop()  # quit tray icon

    def quit_app(self):
        """Create quit thread"""
        quit_thread = threading.Thread(target=self.quit)
        quit_thread.start()

    def int_signal_handler(self, sign, frame):
        """Quit by keyboard interrupt"""
        self.quit_app()

    @staticmethod
    def format_widget_name(name):
        """Format widget name"""
        uppercase = ["drs","p2p"]
        name = re.sub("_", " ", name)

        if name in uppercase:
            return name.upper()
        return name.capitalize()


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

        # Platform specify
        if PLATFORM == "Windows":
            self.iconbitmap("icon.ico")
        else:
            self.iconphoto(True, tk.PhotoImage(file="icon.png"))

        # Center window
        wnd_posx = int((self.winfo_screenwidth() / 2) - self.winfo_reqwidth())
        wnd_posy = int((self.winfo_screenheight() / 2) - self.winfo_reqheight() + 100)
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
                cfg.save(0)  # save setting
                self.master.refresh_list()  # refresh preset list
                self.destroy()  # close window
            else:
                messagebox.showwarning(
                    title="Warning",
                    message="Preset already exists.",
                    parent=self
                    )
