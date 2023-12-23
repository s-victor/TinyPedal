#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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

    MODULE_PACK:
        key: name string
        value: module
    """
    MODULE_PACK = {
        name: getattr(module, name)
        for _, name, _ in pkgutil.iter_modules(module.__path__)
        if val.is_imported_module(module, name)
    }

    def start(self, name: str = None):
        """Start module

        Specify name for selected module
        """
        if name:
            self.start_selected(name)
        else:
            self.start_enabled()

    def close(self, name: str = None):
        """Close module

        Specify name for selected module
        """
        if name:
            self.close_selected(name)
        else:
            self.close_enabled()

    def toggle(self, name: str):
        """Toggle module"""
        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, name).stop()
            #while not getattr(self, name).stopped:
            #    time.sleep(0.01)
        else:
            cfg.setting_user[name]["enable"] = True
            self.__create_instance(self.MODULE_PACK[name])
        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for _name, _module in self.MODULE_PACK.items():
            if not cfg.setting_user[_name]["enable"]:
                cfg.setting_user[_name]["enable"] = True
                self.__create_instance(_module)
        cfg.save()
        logger.info("ACTIVE: all modules")

    def disable_all(self):
        """Disable all modules"""
        for _name in self.MODULE_PACK.keys():
            cfg.setting_user[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all modules")

    def start_enabled(self):
        """Start all enabled module"""
        for _name, _module in self.MODULE_PACK.items():
            if cfg.setting_user[_name]["enable"]:
                self.__create_instance(_module)

    def start_selected(self, name: str):
        """Start selected module"""
        if cfg.setting_user[name]["enable"]:
            self.__create_instance(self.MODULE_PACK[name])

    @staticmethod
    def close_enabled():
        """Close all enabled module"""
        while cfg.active_module_list:
            for _module in cfg.active_module_list:
                _module.stop()
            time.sleep(0.01)

    @staticmethod
    def close_selected(name: str):
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

    def __create_instance(self, obj):
        """Create module instance"""
        setattr(self, obj.MODULE_NAME, obj.Realtime(cfg))
        getattr(self, obj.MODULE_NAME).start()


mctrl = ModuleControl()
