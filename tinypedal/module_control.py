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
Module and widget control
"""

import logging
from pkgutil import iter_modules
from time import sleep

from .setting import cfg
from .validator import is_imported_module
from . import module
from . import widget

logger = logging.getLogger(__name__)


def create_module_pack(target: any) -> dict:
    """Create module reference pack as dictionary

    Args:
        target: module.

    Returns:
        Dictionary, key = module name. value = module.
    """
    return {
        name: getattr(target, name)
        for _, name, _ in iter_modules(target.__path__)
        if is_imported_module(target, name)
    }


class ModuleControl:
    """Module and widget control

    Args:
        target: module.

    Attributes:
        pack: module reference pack (dictionary)
        active_list: list of active modules.
        type_id: module type indentifier, either "module" or "widget".
    """

    __slots__ = "pack", "active_list", "type_id"

    def __init__(self, target: any, type_id: str):
        self.pack = create_module_pack(target)
        self.active_list = {}
        self.type_id = type_id

    def start(self, name: str = ""):
        """Start module, specify name for selected module"""
        if name:
            self.__start_selected(name)
        else:
            self.__start_enabled()

    def close(self, name: str = ""):
        """Close module, specify name for selected module"""
        if name:
            self.__close_selected(name)
        else:
            self.__close_enabled()

    def reload(self, name: str = ""):
        """Reload module"""
        self.close(name)
        self.start(name)

    def toggle(self, name: str):
        """Toggle module"""
        if cfg.user.setting[name]["enable"]:
            cfg.user.setting[name]["enable"] = False
            self.__close_selected(name)
        else:
            cfg.user.setting[name]["enable"] = True
            self.__start_selected(name)
        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for _name in self.pack.keys():
            cfg.user.setting[_name]["enable"] = True
        self.start()
        cfg.save()
        logger.info("ACTIVE: all %s(s)", self.type_id)

    def disable_all(self):
        """Disable all modules"""
        for _name in self.pack.keys():
            cfg.user.setting[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all %s(s)", self.type_id)

    def __start_enabled(self):
        """Start all enabled module"""
        for _name in self.pack.keys():
            self.__start_selected(_name)

    def __start_selected(self, name: str):
        """Start selected module"""
        if cfg.user.setting[name]["enable"] and name not in self.active_list:
            # Create module instance and add to dict
            self.active_list[name] = self.pack[name].Realtime(cfg)
            self.active_list[name].start()

    def __close_enabled(self):
        """Close all enabled module"""
        for _name in tuple(self.active_list):
            self.__close_selected(_name)

    def __close_selected(self, name: str):
        """Close selected module"""
        if name in self.active_list:
            _module = self.active_list[name]  # get instance
            self.active_list.pop(name)  # remove active reference
            _module.stop()  # close module
            while not _module.closed:  # wait finish
                sleep(0.01)
            _module = None  # remove final reference

    @property
    def count_active(self) -> int:
        """Count active modules"""
        return len(self.active_list)

    @property
    def count_total(self) -> int:
        """Count total modules"""
        return len(self.pack)

    @property
    def name_list(self) -> set:
        """List of module names"""
        return self.pack.keys()


mctrl = ModuleControl(module, "module")
wctrl = ModuleControl(widget, "widget")
