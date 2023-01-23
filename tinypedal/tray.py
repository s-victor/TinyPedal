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
Tray icon
"""

import threading
import signal
from PIL import Image
import pystray

from .setting import cfg
from .const import VERSION
from .about import LoadPreset
from .load_func import module
from .readapi import info
from .widget_control import WIDGET_PACK, WidgetControl

wctrl = WidgetControl()


class TrayIcon:
    """System tray icon

    Activate overlay widgets via system tray icon.
    """

    def __init__(self, master):
        self.master = master
        self.preset_window = False

        # Config tray icon
        name = f"TinyPedal v{VERSION}"
        image = Image.open("icon.ico")
        menu = pystray.Menu
        item = pystray.MenuItem
        separator = pystray.Menu.SEPARATOR

        # Add widget menu items
        widget_items = tuple(
                            item(
                                obj.WIDGET_NAME.capitalize(),  # widget name
                                lambda: wctrl.toggle(obj.WIDGET_NAME),  # call widget toggle
                                checked=lambda _: cfg.setting_user[obj.WIDGET_NAME]["enable"]  # check toggle state
                                )
                            for obj in WIDGET_PACK
                            )
        widget_menu = menu(*widget_items)

        main_menu = (
            item("Load Preset", self.open_preset_window),
            separator,
            item("Lock Overlay", module.overlay_lock.toggle,
                 checked=lambda enabled: cfg.overlay["fixed_position"]),
            item("Auto Hide", module.overlay_hide.toggle,
                 checked=lambda enabled: cfg.overlay["auto_hide"]),
            separator,
            item("Widgets", widget_menu),
            separator,
            item("About", self.master.deiconify),
            item("Quit", self.quit_app),
        )

        self.tray = pystray.Icon("icon", icon=image, title=name, menu=main_menu)

        signal.signal(signal.SIGINT, self.int_signal_handler)

    def open_preset_window(self):
        """Open preset window"""
        if not self.preset_window:
            preset_manager = LoadPreset(self.master, self)
            preset_manager.protocol("WM_DELETE_WINDOW", lambda: self.close_preset_window(preset_manager))
            self.preset_window = True

    def close_preset_window(self, window_name):
        """Close preset window"""
        window_name.destroy()
        self.preset_window = False

    def start_tray(self):
        """Start tray icon"""
        # self.tray.run_detached()
        threading.Thread(target=self.tray.run).start()

    def start_widget(self):
        """Start widget"""
        module.start()  # 1 start module
        wctrl.start()  # 2 start widget
        self.tray.update_menu()  # 3 update tray menu

    def close_widget(self):
        """Close widget"""
        module.stop()  # 1 stop module
        wctrl.close()  # 2 close widget

    def quit_app(self):
        """Quit tray icon"""
        module.stop()  # stop module
        self.master.quit()  # must close root window first
        info.stopUpdating()  # stop sharedmemory synced player data updating thread
        info.close()  # stop sharedmemory mapping
        self.tray.stop()  # quit tray icon

    def int_signal_handler(self, signal, frame):
        self.quit_app()
