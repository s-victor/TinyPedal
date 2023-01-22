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
Widget control
"""

import time

from .setting import cfg
from .widget import (cruise,
                     deltabest,
                     drs,
                     engine,
                     force,
                     fuel,
                     gear,
                     instrument,
                     pedal,
                     pressure,
                     radar,
                     relative,
                     sectors,
                     session,
                     steering,
                     stint,
                     temperature,
                     timing,
                     wear,
                     weather,
                     wheel
                     )

WIDGET_PACK = (
    cruise,
    deltabest,
    drs,
    engine,
    force,
    fuel,
    gear,
    instrument,
    pedal,
    pressure,
    radar,
    relative,
    sectors,
    session,
    steering,
    stint,
    temperature,
    timing,
    wear,
    weather,
    wheel
    )


class WidgetControl:
    """Widget control"""

    def start(self):
        """Start widget"""
        for obj in WIDGET_PACK:
            if cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))

    def close(self):
        """Close widget"""
        while cfg.active_widget_list:
            for widgets in cfg.active_widget_list:
                widgets.destroy()
                cfg.active_widget_list.remove(widgets)
            time.sleep(0.1)
        print("all widgets closed")

    def toggle(self, name):
        """Toggle widget"""
        for obj in WIDGET_PACK:
            if name == obj.WIDGET_NAME:
                if not cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                    setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))
                    cfg.setting_user[obj.WIDGET_NAME]["enable"] = True  # set True after widget enabled
                else:
                    widget_instance = getattr(self, f"widget_{obj.WIDGET_NAME}")
                    cfg.setting_user[obj.WIDGET_NAME]["enable"] = False  # set False before widget disabled
                    cfg.active_widget_list.remove(widget_instance)
                    widget_instance.destroy()
                cfg.save()
                break
