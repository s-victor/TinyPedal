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
        """Start module

        Specify name for selected module
        """
        if name:
            self.__start_selected(name)
        else:
            self.__start_enabled()

    def close(self, name: str = ""):
        """Close module

        Specify name for selected module
        """
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
        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, name).stop()
            while not getattr(self, name).stopped:  # make sure stopped
                time.sleep(0.01)
        else:
            cfg.setting_user[name]["enable"] = True
            self.__create_instance(self.PACK[name])
        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for _name, _module in self.PACK.items():
            if not cfg.setting_user[_name]["enable"]:
                cfg.setting_user[_name]["enable"] = True
                self.__create_instance(_module)
        cfg.save()
        logger.info("ACTIVE: all modules")

    def disable_all(self):
        """Disable all modules"""
        for _name in self.PACK.keys():
            cfg.setting_user[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all modules")

    def __start_enabled(self):
        """Start all enabled module"""
        for _name, _module in self.PACK.items():
            if cfg.setting_user[_name]["enable"]:
                self.__create_instance(_module)

    def __start_selected(self, name: str):
        """Start selected module"""
        if cfg.setting_user[name]["enable"]:
            self.__create_instance(self.PACK[name])

    @staticmethod
    def __close_enabled():
        """Close all enabled module

        Reverse iterate over active list.
        """
        for _module in reversed(cfg.active_module_list):
            _module.stop()
        while cfg.active_module_list:
            time.sleep(0.01)

    @staticmethod
    def __close_selected(name: str):
        """Close selected module"""
        if not cfg.active_module_list:
            return None
        for _module in cfg.active_module_list:
            if _module.module_name == name:
                _module.stop()
                while not _module.stopped:
                    time.sleep(0.01)
                break
        return None

    def __create_instance(self, _module: object):
        """Create module instance"""
        setattr(self, _module.MODULE_NAME, _module.Realtime(cfg))
        getattr(self, _module.MODULE_NAME).start()


mctrl = ModuleControl()
