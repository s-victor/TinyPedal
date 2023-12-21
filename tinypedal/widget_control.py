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

logger = logging.getLogger(__name__)


class WidgetControl:
    """Widget control"""
    WIDGET_PACK = tuple(
        getattr(widget, name) for _, name, _ in pkgutil.iter_modules(widget.__path__))

    def start(self, name: str = None):
        """Start widget

        Specify name for selected widget
        """
        if name:
            self.start_selected(name)
        else:
            self.start_enabled()

    def close(self, name: str = None):
        """Close widget

        Specify name for selected widget
        """
        if name:
            self.close_selected(name)
        else:
            self.close_enabled()

    def toggle(self, name: str):
        """Toggle widget"""
        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, f"widget_{name}").closing()
        else:
            cfg.setting_user[name]["enable"] = True
            for obj in self.WIDGET_PACK:
                if obj.WIDGET_NAME == name:
                    self.__create_instance(obj)
                    break
        cfg.save()

    def enable_all(self):
        """Enable all widgets"""
        for obj in self.WIDGET_PACK:
            if not cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                cfg.setting_user[obj.WIDGET_NAME]["enable"] = True
                self.__create_instance(obj)
        cfg.save()
        logger.info("ACTIVE: all widgets")

    def disable_all(self):
        """Disable all widgets"""
        for obj in self.WIDGET_PACK:
            cfg.setting_user[obj.WIDGET_NAME]["enable"] = False
        self.close()
        cfg.save()
        logger.info("CLOSED: all widgets")

    def start_enabled(self):
        """Start enabled widget"""
        for obj in self.WIDGET_PACK:
            if cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                self.__create_instance(obj)

    def start_selected(self, name: str):
        """Start selected widget"""
        for obj in self.WIDGET_PACK:
            if (cfg.setting_user[name]["enable"]
                and obj.WIDGET_NAME == name):
                self.__create_instance(obj)
                break

    @staticmethod
    def close_enabled():
        """Close enabled widget"""
        while cfg.active_widget_list:
            for _widget in cfg.active_widget_list:
                _widget.closing()
            time.sleep(0.01)

    @staticmethod
    def close_selected(name: str):
        """Close selected widget"""
        if not cfg.active_widget_list:
            return None
        for _widget in cfg.active_widget_list:
            if _widget.widget_name == name:
                _widget.closing()
                break
        return None

    def __create_instance(self, obj):
        """Create widget instance"""
        setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))


wctrl = WidgetControl()
