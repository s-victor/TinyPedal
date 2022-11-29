#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Widget toggle
"""

import time

from .setting import cfg
from .widget import (cruise,
                     deltabest,
                     drs,
                     engine,
                     force,
                     fuel,
                     gear,
                     instrument,
                     pedal,
                     pressure,
                     radar,
                     relative,
                     session,
                     steering,
                     stint,
                     temperature,
                     timing,
                     wear,
                     weather,
                     wheel
                     )


class WidgetToggle:
    """Widget toggle"""

    def __init__(self):
        """Widget list"""
        self.widget_cruise = None
        self.widget_deltabest = None
        self.widget_drs = None
        self.widget_engine = None
        self.widget_force = None
        self.widget_fuel = None
        self.widget_gear = None
        self.widget_instrument = None
        self.widget_pedal = None
        self.widget_pressure = None
        self.widget_radar = None
        self.widget_relative = None
        self.widget_session = None
        self.widget_steering = None
        self.widget_stint = None
        self.widget_temperature = None
        self.widget_timing = None
        self.widget_wear = None
        self.widget_weather = None
        self.widget_wheel = None

    def start(self):
        """Start widget"""
        if cfg.setting_user["cruise"]["enable"]:
            self.widget_cruise = cruise.Draw(cfg)

        if cfg.setting_user["deltabest"]["enable"]:
            self.widget_deltabest = deltabest.Draw(cfg)

        if cfg.setting_user["drs"]["enable"]:
            self.widget_drs = drs.Draw(cfg)

        if cfg.setting_user["engine"]["enable"]:
            self.widget_engine = engine.Draw(cfg)

        if cfg.setting_user["force"]["enable"]:
            self.widget_force = force.Draw(cfg)

        if cfg.setting_user["fuel"]["enable"]:
            self.widget_fuel = fuel.Draw(cfg)

        if cfg.setting_user["gear"]["enable"]:
            self.widget_gear = gear.Draw(cfg)

        if cfg.setting_user["instrument"]["enable"]:
            self.widget_instrument = instrument.Draw(cfg)

        if cfg.setting_user["pedal"]["enable"]:
            self.widget_pedal = pedal.Draw(cfg)

        if cfg.setting_user["pressure"]["enable"]:
            self.widget_pressure = pressure.Draw(cfg)

        if cfg.setting_user["radar"]["enable"]:
            self.widget_radar = radar.Draw(cfg)

        if cfg.setting_user["relative"]["enable"]:
            self.widget_relative = relative.Draw(cfg)

        if cfg.setting_user["session"]["enable"]:
            self.widget_session = session.Draw(cfg)

        if cfg.setting_user["steering"]["enable"]:
            self.widget_steering = steering.Draw(cfg)

        if cfg.setting_user["stint"]["enable"]:
            self.widget_stint = stint.Draw(cfg)

        if cfg.setting_user["temperature"]["enable"]:
            self.widget_temperature = temperature.Draw(cfg)

        if cfg.setting_user["timing"]["enable"]:
            self.widget_timing = timing.Draw(cfg)

        if cfg.setting_user["wear"]["enable"]:
            self.widget_wear = wear.Draw(cfg)

        if cfg.setting_user["weather"]["enable"]:
            self.widget_weather = weather.Draw(cfg)

        if cfg.setting_user["wheel"]["enable"]:
            self.widget_wheel = wheel.Draw(cfg)

    def close(self):
        """Close widget"""
        while cfg.active_widget_list:
            for widgets in cfg.active_widget_list:
                widgets.destroy()
                cfg.active_widget_list.remove(widgets)
            time.sleep(0.1)
        print("all widgets closed")

    def cruise(self):
        """Toggle cruise"""
        if not cfg.setting_user["cruise"]["enable"]:
            self.widget_cruise = cruise.Draw(cfg)
            cfg.setting_user["cruise"]["enable"] = True
        else:
            cfg.setting_user["cruise"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_cruise)
            self.widget_cruise.destroy()
        cfg.save()

    def deltabest(self):
        """Toggle deltabest"""
        if not cfg.setting_user["deltabest"]["enable"]:
            self.widget_deltabest = deltabest.Draw(cfg)
            cfg.setting_user["deltabest"]["enable"] = True  # set True after widget enabled
        else:
            cfg.setting_user["deltabest"]["enable"] = False  # set False before widget disabled
            cfg.active_widget_list.remove(self.widget_deltabest)
            self.widget_deltabest.destroy()
        cfg.save()

    def drs(self):
        """Toggle DRS"""
        if not cfg.setting_user["drs"]["enable"]:
            self.widget_drs = drs.Draw(cfg)
            cfg.setting_user["drs"]["enable"] = True
        else:
            cfg.setting_user["drs"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_drs)
            self.widget_drs.destroy()
        cfg.save()

    def engine(self):
        """Toggle engine"""
        if not cfg.setting_user["engine"]["enable"]:
            self.widget_engine = engine.Draw(cfg)
            cfg.setting_user["engine"]["enable"] = True
        else:
            cfg.setting_user["engine"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_engine)
            self.widget_engine.destroy()
        cfg.save()

    def force(self):
        """Toggle force"""
        if not cfg.setting_user["force"]["enable"]:
            self.widget_force = force.Draw(cfg)
            cfg.setting_user["force"]["enable"] = True
        else:
            cfg.setting_user["force"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_force)
            self.widget_force.destroy()
        cfg.save()

    def fuel(self):
        """Toggle fuel"""
        if not cfg.setting_user["fuel"]["enable"]:
            self.widget_fuel = fuel.Draw(cfg)
            cfg.setting_user["fuel"]["enable"] = True
        else:
            cfg.setting_user["fuel"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_fuel)
            self.widget_fuel.destroy()
        cfg.save()

    def gear(self):
        """Toggle gear"""
        if not cfg.setting_user["gear"]["enable"]:
            self.widget_gear = gear.Draw(cfg)
            cfg.setting_user["gear"]["enable"] = True
        else:
            cfg.setting_user["gear"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_gear)
            self.widget_gear.destroy()
        cfg.save()

    def instrument(self):
        """Toggle instrument"""
        if not cfg.setting_user["instrument"]["enable"]:
            self.widget_instrument = instrument.Draw(cfg)
            cfg.setting_user["instrument"]["enable"] = True
        else:
            cfg.setting_user["instrument"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_instrument)
            self.widget_instrument.destroy()
        cfg.save()

    def pedal(self):
        """Toggle pedal"""
        if not cfg.setting_user["pedal"]["enable"]:
            self.widget_pedal = pedal.Draw(cfg)
            cfg.setting_user["pedal"]["enable"] = True
        else:
            cfg.setting_user["pedal"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_pedal)
            self.widget_pedal.destroy()
        cfg.save()

    def pressure(self):
        """Toggle pressure"""
        if not cfg.setting_user["pressure"]["enable"]:
            self.widget_pressure = pressure.Draw(cfg)
            cfg.setting_user["pressure"]["enable"] = True
        else:
            cfg.setting_user["pressure"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_pressure)
            self.widget_pressure.destroy()
        cfg.save()

    def radar(self):
        """Toggle radar"""
        if not cfg.setting_user["radar"]["enable"]:
            self.widget_radar = radar.Draw(cfg)
            cfg.setting_user["radar"]["enable"] = True
        else:
            cfg.setting_user["radar"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_radar)
            self.widget_radar.destroy()
        cfg.save()

    def relative(self):
        """Toggle relative"""
        if not cfg.setting_user["relative"]["enable"]:
            self.widget_relative = relative.Draw(cfg)
            cfg.setting_user["relative"]["enable"] = True
        else:
            cfg.setting_user["relative"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_relative)
            self.widget_relative.destroy()
        cfg.save()

    def session(self):
        """Toggle session"""
        if not cfg.setting_user["session"]["enable"]:
            self.widget_session = session.Draw(cfg)
            cfg.setting_user["session"]["enable"] = True
        else:
            cfg.setting_user["session"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_session)
            self.widget_session.destroy()
        cfg.save()

    def steering(self):
        """Toggle steering"""
        if not cfg.setting_user["steering"]["enable"]:
            self.widget_steering = steering.Draw(cfg)
            cfg.setting_user["steering"]["enable"] = True
        else:
            cfg.setting_user["steering"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_steering)
            self.widget_steering.destroy()
        cfg.save()

    def stint(self):
        """Toggle stint"""
        if not cfg.setting_user["stint"]["enable"]:
            self.widget_stint = stint.Draw(cfg)
            cfg.setting_user["stint"]["enable"] = True
        else:
            cfg.setting_user["stint"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_stint)
            self.widget_stint.destroy()
        cfg.save()

    def temperature(self):
        """Toggle temperature"""
        if not cfg.setting_user["temperature"]["enable"]:
            self.widget_temperature = temperature.Draw(cfg)
            cfg.setting_user["temperature"]["enable"] = True
        else:
            cfg.setting_user["temperature"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_temperature)
            self.widget_temperature.destroy()
        cfg.save()

    def timing(self):
        """Toggle timing"""
        if not cfg.setting_user["timing"]["enable"]:
            self.widget_timing = timing.Draw(cfg)
            cfg.setting_user["timing"]["enable"] = True
        else:
            cfg.setting_user["timing"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_timing)
            self.widget_timing.destroy()
        cfg.save()

    def wear(self):
        """Toggle wear"""
        if not cfg.setting_user["wear"]["enable"]:
            self.widget_wear = wear.Draw(cfg)
            cfg.setting_user["wear"]["enable"] = True
        else:
            cfg.setting_user["wear"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_wear)
            self.widget_wear.destroy()
        cfg.save()

    def weather(self):
        """Toggle weather"""
        if not cfg.setting_user["weather"]["enable"]:
            self.widget_weather = weather.Draw(cfg)
            cfg.setting_user["weather"]["enable"] = True
        else:
            cfg.setting_user["weather"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_weather)
            self.widget_weather.destroy()
        cfg.save()

    def wheel(self):
        """Toggle wheel"""
        if not cfg.setting_user["wheel"]["enable"]:
            self.widget_wheel = wheel.Draw(cfg)
            cfg.setting_user["wheel"]["enable"] = True
        else:
            cfg.setting_user["wheel"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_wheel)
            self.widget_wheel.destroy()
        cfg.save()
