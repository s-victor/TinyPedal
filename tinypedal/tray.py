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
from .widget_control import WidgetControl


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

        # Add widget toggle items
        widget_menu = menu(
            item("Cruise", lambda: wctrl.toggle("cruise"), checked=lambda _: cfg.setting_user["cruise"]["enable"]),
            item("Delta best", lambda: wctrl.toggle("deltabest"), checked=lambda _: cfg.setting_user["deltabest"]["enable"]),
            item("DRS", lambda: wctrl.toggle("drs"), checked=lambda _: cfg.setting_user["drs"]["enable"]),
            item("Engine", lambda: wctrl.toggle("engine"), checked=lambda _: cfg.setting_user["engine"]["enable"]),
            item("Force", lambda: wctrl.toggle("force"), checked=lambda _: cfg.setting_user["force"]["enable"]),
            item("Fuel", lambda: wctrl.toggle("fuel"), checked=lambda _: cfg.setting_user["fuel"]["enable"]),
            item("Gear", lambda: wctrl.toggle("gear"), checked=lambda _: cfg.setting_user["gear"]["enable"]),
            item("Instrument", lambda: wctrl.toggle("instrument"), checked=lambda _: cfg.setting_user["instrument"]["enable"]),
            item("Pedal", lambda: wctrl.toggle("pedal"), checked=lambda _: cfg.setting_user["pedal"]["enable"]),
            item("Pressure", lambda: wctrl.toggle("pressure"), checked=lambda _: cfg.setting_user["pressure"]["enable"]),
            item("Radar", lambda: wctrl.toggle("radar"), checked=lambda _: cfg.setting_user["radar"]["enable"]),
            item("Relative", lambda: wctrl.toggle("relative"), checked=lambda _: cfg.setting_user["relative"]["enable"]),
            item("Sectors", lambda: wctrl.toggle("sectors"), checked=lambda _: cfg.setting_user["sectors"]["enable"]),
            item("Session", lambda: wctrl.toggle("session"), checked=lambda _: cfg.setting_user["session"]["enable"]),
            item("Steering", lambda: wctrl.toggle("steering"), checked=lambda _: cfg.setting_user["steering"]["enable"]),
            item("Stint", lambda: wctrl.toggle("stint"), checked=lambda _: cfg.setting_user["stint"]["enable"]),
            item("Temperature", lambda: wctrl.toggle("temperature"), checked=lambda _: cfg.setting_user["temperature"]["enable"]),
            item("Timing", lambda: wctrl.toggle("timing"), checked=lambda _: cfg.setting_user["timing"]["enable"]),
            item("Wear", lambda: wctrl.toggle("wear"), checked=lambda _: cfg.setting_user["wear"]["enable"]),
            item("Weather", lambda: wctrl.toggle("weather"), checked=lambda _: cfg.setting_user["weather"]["enable"]),
            item("Wheel", lambda: wctrl.toggle("wheel"), checked=lambda _: cfg.setting_user["wheel"]["enable"]),
        )

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
