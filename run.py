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
Run program
"""

import os
from tkinter import messagebox
import psutil
from tinypedal.about import About, LoadPreset


def is_tinypedal_running(app_name):
    """Check if is already running"""
    for app in psutil.process_iter(["name", "pid"]):
        # Compare found APP name
        if app.info["name"] == app_name:
            # Compare with current APP pid
            if app.info["pid"] != os.getpid():
                return True
    return None


def load_tinypedal():
    """Start tinypedal"""
    root = About()

    if is_tinypedal_running("tinypedal.exe"):
        messagebox.showwarning(
            "TinyPedal",
            "TinyPedal is already running.\n\n"
            "Only one TinyPedal may be run at a time.\n"
            "Check system tray for hidden icon."
            )
    else:
        load_preset = LoadPreset(root)
        load_preset.deiconify()
        load_preset.protocol("WM_DELETE_WINDOW", load_preset.closing)

        # Start tkinter mainloop
        root.protocol("WM_DELETE_WINDOW", root.withdraw)
        root.mainloop()


if __name__ == "__main__":
    load_tinypedal()
