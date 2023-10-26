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
Widget control
"""

import logging
import time

from .setting import cfg
from .widget import (
    battery,
    brake_bias,
    brake_pressure,
    brake_temperature,
    cruise,
    deltabest,
    drs,
    electric_motor,
    engine,
    flag,
    force,
    friction_circle,
    fuel,
    gear,
    instrument,
    lap_time_history,
    p2p,
    pedal,
    radar,
    rake_angle,
    relative,
    ride_height,
    sectors,
    session,
    speedometer,
    standings,
    steering,
    stint_history,
    timing,
    track_map,
    tyre_load,
    tyre_pressure,
    tyre_temperature,
    tyre_wear,
    weather,
    wheel_alignment,
)

logger = logging.getLogger(__name__)


class WidgetControl:
    """Widget control"""
    WIDGET_PACK = (
        battery,
        brake_bias,
        brake_pressure,
        brake_temperature,
        cruise,
        deltabest,
        drs,
        electric_motor,
        engine,
        flag,
        force,
        friction_circle,
        fuel,
        gear,
        instrument,
        lap_time_history,
        p2p,
        pedal,
        radar,
        rake_angle,
        relative,
        ride_height,
        sectors,
        session,
        speedometer,
        standings,
        steering,
        stint_history,
        timing,
        track_map,
        tyre_load,
        tyre_pressure,
        tyre_temperature,
        tyre_wear,
        weather,
        wheel_alignment,
    )

    def start(self):
        """Start widget"""
        for obj in self.WIDGET_PACK:
            if cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                self.__create_instance(obj)

    @staticmethod
    def close():
        """Close widget"""
        while cfg.active_widget_list:
            for widget in cfg.active_widget_list:
                widget.closing()
            time.sleep(0.01)

    def toggle(self, widget):
        """Toggle widget"""
        if cfg.setting_user[widget.WIDGET_NAME]["enable"]:
            cfg.setting_user[widget.WIDGET_NAME]["enable"] = False
            getattr(self, f"widget_{widget.WIDGET_NAME}").closing()
        else:
            cfg.setting_user[widget.WIDGET_NAME]["enable"] = True
            self.__create_instance(widget)
        cfg.save()

    def enable_all(self):
        """Enable all widgets"""
        for obj in self.WIDGET_PACK:
            if not cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                cfg.setting_user[obj.WIDGET_NAME]["enable"] = True
                self.__create_instance(obj)
        cfg.save()
        logger.info("all widgets enabled")

    def disable_all(self):
        """Disable all widgets"""
        for obj in self.WIDGET_PACK:
            cfg.setting_user[obj.WIDGET_NAME]["enable"] = False
        self.close()
        cfg.save()
        logger.info("all widgets disabled")

    def start_selected(self, widget_name):
        """Start selected widget"""
        for obj in self.WIDGET_PACK:
            if (cfg.setting_user[widget_name]["enable"]
                and obj.WIDGET_NAME == widget_name):
                self.__create_instance(obj)
                break

    @staticmethod
    def close_selected(widget_name):
        """Close selected widget"""
        if not cfg.active_widget_list:
            return None
        for widget in cfg.active_widget_list:
            if widget.widget_name == widget_name:
                widget.closing()
                return None

    def __create_instance(self, obj):
        """Create widget instance"""
        setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))


wctrl = WidgetControl()
