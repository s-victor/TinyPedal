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
        PACK: widget module reference dictionary.
        key = module name string. value = module.
    """
    PACK = {
        name: getattr(widget, name)
        for _, name, _ in pkgutil.iter_modules(widget.__path__)
        if val.is_imported_module(widget, name)
    }

    def start(self, name: str = ""):
        """Start widget

        Specify name for selected widget
        """
        if name:
            self.__start_selected(name)
        else:
            self.__start_enabled()

    def close(self, name: str = ""):
        """Close widget

        Specify name for selected widget
        """
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
        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, f"widget_{name}").closing()
        else:
            cfg.setting_user[name]["enable"] = True
            self.__create_instance(self.PACK[name])
        cfg.save()

    def enable_all(self):
        """Enable all widgets"""
        for _name, _widget in self.PACK.items():
            if not cfg.setting_user[_name]["enable"]:
                cfg.setting_user[_name]["enable"] = True
                self.__create_instance(_widget)
        cfg.save()
        logger.info("ACTIVE: all widgets")

    def disable_all(self):
        """Disable all widgets"""
        for _name in self.PACK.keys():
            cfg.setting_user[_name]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all widgets")

    def __start_enabled(self):
        """Start all enabled widget"""
        for _name, _widget in self.PACK.items():
            if cfg.setting_user[_name]["enable"]:
                self.__create_instance(_widget)

    def __start_selected(self, name: str):
        """Start selected widget"""
        if cfg.setting_user[name]["enable"]:
            self.__create_instance(self.PACK[name])

    @staticmethod
    def __close_enabled():
        """Close all enabled widget

        Reverse iterate over active list.
        """
        for _widget in reversed(cfg.active_widget_list):
            _widget.closing()
        while cfg.active_widget_list:
            time.sleep(0.01)

    @staticmethod
    def __close_selected(name: str):
        """Close selected widget"""
        if not cfg.active_widget_list:
            return None
        for _widget in cfg.active_widget_list:
            if _widget.widget_name == name:
                _widget.closing()
                break
        return None

    def __create_instance(self, _widget: object):
        """Create widget instance"""
        setattr(self, f"widget_{_widget.WIDGET_NAME}", _widget.Draw(cfg))


wctrl = WidgetControl()
