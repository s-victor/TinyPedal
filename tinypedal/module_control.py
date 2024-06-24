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
Module control
"""

import logging
import time
import pkgutil

from .setting import cfg
from . import module
from . import validator as val

logger = logging.getLogger(__name__)


class ModuleControl:
    """Module control

    Attributes:
        PACK: Data module reference dictionary.
        key = module name string. value = module.
    """
    PACK = {
        name: getattr(module, name)
        for _, name, _ in pkgutil.iter_modules(module.__path__)
        if val.is_imported_module(module, name)
    }

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
        for _name in self.PACK.keys():
            cfg.user.setting[_name]["enable"] = True
        self.start()
        cfg.save()
        logger.info("ACTIVE: all modules")

    def disable_all(self):
        """Disable all modules"""
        for _name in self.PACK.keys():
            cfg.user.setting[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all modules")

    def __start_enabled(self):
        """Start all enabled module"""
        for _name in self.PACK.keys():
            self.__start_selected(_name)

    def __start_selected(self, name: str):
        """Start selected module"""
        if cfg.user.setting[name]["enable"]:
            self.__create_instance(name)

    @staticmethod
    def __close_enabled():
        """Close all enabled module"""
        name_list = tuple(cfg.active_module_list)
        for _name in name_list:
            if _name in cfg.active_module_list:
                cfg.active_module_list[_name].stop()
        while cfg.active_module_list:  # make sure stopped
            time.sleep(0.01)

    @staticmethod
    def __close_selected(name: str):
        """Close selected module"""
        _module = cfg.active_module_list.get(name, False)
        if _module:
            _module.stop()
            while not _module.stopped:  # make sure stopped
                time.sleep(0.01)

    def __create_instance(self, name: str):
        """Create module instance"""
        if name not in cfg.active_module_list:
            cfg.active_module_list[name] = self.PACK[name].Realtime(cfg)
            cfg.active_module_list[name].start()


mctrl = ModuleControl()
