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
                # Create widget instance
                setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))

    @staticmethod
    def close():
        """Close widget"""
        while cfg.active_widget_list:
            for widget in cfg.active_widget_list:
                widget.break_signal()
                widget.closing()
            time.sleep(0.01)
        logger.info("all widgets closed")

    def toggle(self, widget):
        """Toggle widget"""
        name = widget.WIDGET_NAME

        if cfg.setting_user[name]["enable"]:
            cfg.setting_user[name]["enable"] = False
            getattr(self, f"widget_{name}").break_signal()
            getattr(self, f"widget_{name}").closing()
        else:
            cfg.setting_user[name]["enable"] = True
            setattr(self, f"widget_{name}", widget.Draw(cfg))

        cfg.save()

    def enable_all(self):
        """Enable all widgets"""
        for obj in self.WIDGET_PACK:
            if not cfg.setting_user[obj.WIDGET_NAME]["enable"]:
                cfg.setting_user[obj.WIDGET_NAME]["enable"] = True
                setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))
        cfg.save()
        logger.info("all widgets enabled")

    def disable_all(self):
        """Disable all widgets"""
        while cfg.active_widget_list:
            for widget in cfg.active_widget_list:
                cfg.setting_user[widget.widget_name]["enable"] = False
                widget.break_signal()
                widget.closing()
            #time.sleep(0.01)
        cfg.save()
        logger.info("all widgets disabled")

    def start_widget(self, widget_name):
        """Start selected widget"""
        for obj in self.WIDGET_PACK:
            if obj.WIDGET_NAME == widget_name and cfg.setting_user[widget_name]["enable"]:
                setattr(self, f"widget_{obj.WIDGET_NAME}", obj.Draw(cfg))
                break

    def close_widget(self, widget_name):
        """Close selected widget"""
        if cfg.active_widget_list:
            for widget in cfg.active_widget_list:
                if widget.widget_name == widget_name:
                    widget.break_signal()
                    widget.closing()
                    break


wctrl = WidgetControl()
