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

from .setting import cfg
from .module import (
    module_delta,
    module_force,
    module_fuel,
    module_hybrid,
    module_mapping,
    module_relative,
    module_sectors,
    module_vehicles,
)

logger = logging.getLogger(__name__)


class ModuleControl:
    """Module control"""
    MODULE_PACK = (
        module_delta,
        module_force,
        module_fuel,
        module_hybrid,
        module_mapping,
        module_relative,
        module_sectors,
        module_vehicles,
    )

    def start(self):
        """Start module"""
        for obj in self.MODULE_PACK:
            if cfg.setting_user[obj.MODULE_NAME]["enable"]:
                self.__create_instance(obj)

    @staticmethod
    def close():
        """Close module"""
        while cfg.active_module_list:
            for module in cfg.active_module_list:
                module.running = False
            time.sleep(0.01)

    def toggle(self, module):
        """Toggle module"""
        if cfg.setting_user[module.MODULE_NAME]["enable"]:
            cfg.setting_user[module.MODULE_NAME]["enable"] = False
            getattr(self, module.MODULE_NAME).running = False
            while not getattr(self, module.MODULE_NAME).stopped:
                time.sleep(0.01)
        else:
            cfg.setting_user[module.MODULE_NAME]["enable"] = True
            self.__create_instance(module)
        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for obj in self.MODULE_PACK:
            if not cfg.setting_user[obj.MODULE_NAME]["enable"]:
                cfg.setting_user[obj.MODULE_NAME]["enable"] = True
                self.__create_instance(obj)
        cfg.save()
        logger.info("all modules enabled")

    def disable_all(self):
        """Disable all modules"""
        for obj in self.MODULE_PACK:
            cfg.setting_user[obj.MODULE_NAME]["enable"] = False
        self.close()
        cfg.save()
        logger.info("all modules disabled")

    def start_selected(self, module_name):
        """Start selected module"""
        for obj in self.MODULE_PACK:
            if (cfg.setting_user[module_name]["enable"]
                and obj.MODULE_NAME == module_name):
                self.__create_instance(obj)
                break

    @staticmethod
    def close_selected(module_name):
        """Close selected module"""
        if not cfg.active_module_list:
            return None
        for module in cfg.active_module_list:
            if module.module_name == module_name:
                module.running = False
                while not module.stopped:
                    time.sleep(0.01)
                return None

    def __create_instance(self, obj):
        """Create module instance"""
        setattr(self, obj.MODULE_NAME, obj.Realtime(cfg))
        getattr(self, obj.MODULE_NAME).start()


mctrl = ModuleControl()
