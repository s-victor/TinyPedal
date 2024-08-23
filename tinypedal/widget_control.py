#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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

import logging
import time
import pkgutil

from .setting import cfg
from . import widget
from . import validator as val

logger = logging.getLogger(__name__)


class WidgetControl:
    """Widget control

    Attributes:
        PACK:
            Widget module reference dictionary.
            key = module name string. value = module.
    """
    PACK = {
        name: getattr(widget, name)
        for _, name, _ in pkgutil.iter_modules(widget.__path__)
        if val.is_imported_module(widget, name)
    }
    active_list = {}

    def start(self, name: str = ""):
        """Start widget, specify name for selected widget"""
        if name:
            self.__start_selected(name)
        else:
            self.__start_enabled()

    def close(self, name: str = ""):
        """Close widget, specify name for selected widget"""
        if name:
            self.__close_selected(name)
        else:
            self.__close_enabled()

    def reload(self, name: str = ""):
        """Reload widget"""
        self.close(name)
        self.start(name)

    def toggle(self, name: str):
        """Toggle widget"""
        if cfg.user.setting[name]["enable"]:
            cfg.user.setting[name]["enable"] = False
            self.__close_selected(name)
        else:
            cfg.user.setting[name]["enable"] = True
            self.__start_selected(name)
        cfg.save()

    def enable_all(self):
        """Enable all widgets"""
        for _name in self.PACK.keys():
            cfg.user.setting[_name]["enable"] = True
        self.start()
        cfg.save()
        logger.info("ACTIVE: all widgets")

    def disable_all(self):
        """Disable all widgets"""
        for _name in self.PACK.keys():
            cfg.user.setting[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all widgets")

    def __start_enabled(self):
        """Start all enabled widget"""
        for _name in self.PACK.keys():
            self.__start_selected(_name)

    def __start_selected(self, name: str):
        """Start selected widget"""
        if cfg.user.setting[name]["enable"] and name not in self.active_list:
            # Create widget instance and add to dict
            self.active_list[name] = self.PACK[name].Draw(cfg)

    def __close_enabled(self):
        """Close all enabled widget"""
        for _name in tuple(self.active_list):
            self.__close_selected(_name)

    def __close_selected(self, name: str):
        """Close selected widget"""
        if name in self.active_list:
            _widget = self.active_list[name]  # get instance
            self.active_list.pop(name)  # remove active reference
            _widget.closing()  # close widget
            while not _widget.closed:  # wait finish
                time.sleep(0.01)
            _widget = None  # remove final reference

    @property
    def count_active(self) -> int:
        """Count active widgets"""
        return len(self.active_list)

    @property
    def count_total(self) -> int:
        """Count total widgets"""
        return len(self.PACK)

    @property
    def name_list(self) -> set:
        """List of widget names"""
        return self.PACK.keys()


wctrl = WidgetControl()
