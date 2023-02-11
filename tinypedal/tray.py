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
from PIL import Image
import pystray

from .setting import cfg
from .const import VERSION
from .module_control import module
from .widget_control import WIDGET_PACK, wctrl


class TrayIcon:
    """System tray icon

    Activate overlay widgets via system tray icon.
    """

    def __init__(self, master, preset_manager):
        self.preset_manager = preset_manager

        # Config tray icon
        name = f"TinyPedal v{VERSION}"
        image = Image.open("icon.ico")
        menu = pystray.Menu
        item = pystray.MenuItem
        separator = pystray.Menu.SEPARATOR

        # Create widget menu
        widget_items = tuple(map(self.create_widget_menu, WIDGET_PACK))
        widget_menu = menu(*widget_items)

        # Create main menu
        main_menu = (
            item("Load Preset", self.preset_manager.unhide),
            separator,
            item("Lock Overlay", module.overlay_lock.toggle,
                 checked=lambda enabled: cfg.overlay["fixed_position"]),
            item("Auto Hide", module.overlay_hide.toggle,
                 checked=lambda enabled: cfg.overlay["auto_hide"]),
            separator,
            item("Widgets", widget_menu),
            separator,
            item("About", master.deiconify),
            item("Quit", self.preset_manager.quit_app),
        )

        self.tray = pystray.Icon("icon", icon=image, title=name, menu=main_menu)

    def start(self):
        """Start tray icon"""
        threading.Thread(target=self.tray.run).start()

    def create_widget_menu(self, obj):
        """Create widget menu"""
        widget_name = obj.WIDGET_NAME
        display_name = self.preset_manager.format_widget_name(widget_name)

        return pystray.MenuItem(
                display_name,  # widget name
                lambda: wctrl.toggle(widget_name),  # call widget toggle
                checked=lambda _: cfg.setting_user[widget_name]["enable"]  # check toggle state
                )
