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

logger = logging.getLogger(__name__)


class ModuleControl:
    """Module control"""
    MODULE_PACK = tuple(
        getattr(module, name) for _, name, _ in pkgutil.iter_modules(module.__path__))

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
            for obj in self.MODULE_PACK:
                if obj.MODULE_NAME == name:
                    self.__create_instance(obj)
                    break
        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for obj in self.MODULE_PACK:
            if not cfg.setting_user[obj.MODULE_NAME]["enable"]:
                cfg.setting_user[obj.MODULE_NAME]["enable"] = True
                self.__create_instance(obj)
        cfg.save()
        logger.info("ACTIVE: all modules")

    def disable_all(self):
        """Disable all modules"""
        for obj in self.MODULE_PACK:
            cfg.setting_user[obj.MODULE_NAME]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all modules")

    def start_enabled(self):
        """Start enabled module"""
        for obj in self.MODULE_PACK:
            if cfg.setting_user[obj.MODULE_NAME]["enable"]:
                self.__create_instance(obj)

    def start_selected(self, name: str):
        """Start selected module"""
        for obj in self.MODULE_PACK:
            if (cfg.setting_user[name]["enable"]
                and obj.MODULE_NAME == name):
                self.__create_instance(obj)
                break

    @staticmethod
    def close_enabled():
        """Close enabled module"""
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
