#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023  Xiang
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
    module_fuel,
    module_hybrid,
    module_mapping,
    module_relative,
    module_standings,
)

logger = logging.getLogger(__name__)


class ModuleControl:
    """Module control"""
    MODULE_PACK = (
        module_delta,
        module_fuel,
        module_hybrid,
        module_mapping,
        module_relative,
        module_standings,
    )
    vehicle_classes = None

    def start(self):
        """Start module"""
        for obj in self.MODULE_PACK:
            # Initialize module
            setattr(self, obj.MODULE_NAME, obj.Realtime(self, cfg))
            # Start module
            if cfg.setting_user[obj.MODULE_NAME]["enable"]:
                getattr(self, obj.MODULE_NAME).start()

    def stop(self):
        """Stop module"""
        if cfg.active_module_list:
            for module in cfg.active_module_list:
                module.running = False
            while cfg.active_module_list:
                time.sleep(0.01)

    def toggle(self, module):
        """Toggle module"""
        name = module.MODULE_NAME

        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, name).running = False
            while not getattr(self, name).stopped:
                time.sleep(0.01)
        else:
            cfg.setting_user[name]["enable"] = True
            setattr(self, name, module.Realtime(self, cfg))
            getattr(self, name).start()

        cfg.save()

    def enable_all(self):
        """Enable all modules"""
        for obj in self.MODULE_PACK:
            if not cfg.setting_user[obj.MODULE_NAME]["enable"]:
                cfg.setting_user[obj.MODULE_NAME]["enable"] = True
                setattr(self, obj.MODULE_NAME, obj.Realtime(self, cfg))
                getattr(self, obj.MODULE_NAME).start()
        cfg.save()
        logger.info("all modules enabled")

    def disable_all(self):
        """Disable all modules"""
        for obj in self.MODULE_PACK:
            cfg.setting_user[obj.MODULE_NAME]["enable"] = False

        while cfg.active_module_list:
            for module in cfg.active_module_list:
                module.running = False
            #time.sleep(0.01)
        cfg.save()
        logger.info("all modules disabled")

    def start_module(self, module_name):
        """Start selected module"""
        for obj in self.MODULE_PACK:
            if obj.MODULE_NAME == module_name and cfg.setting_user[module_name]["enable"]:
                setattr(self, obj.MODULE_NAME, obj.Realtime(self, cfg))
                getattr(self, obj.MODULE_NAME).start()
                break

    def stop_module(self, module_name):
        """stop selected module"""
        if cfg.active_widget_list:
            for module in cfg.active_module_list:
                if module.module_name == module_name:
                    module.running = False
                    while not module.stopped:
                        time.sleep(0.01)
                    break


mctrl = ModuleControl()
