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
Tray icon
"""

from PIL import Image
import pystray

from tinypedal.setting import cfg
from tinypedal.load_func import overlay_lock, overlay_hide

from tinypedal.widget import (cruise,
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


class TrayIcon:
    """System tray icon

    Activate overlay widgets via system tray icon.
    """

    def __init__(self, master):
        self.master = master

        # Preset name
        loaded_preset = cfg.filename[:-5].upper()
        if len(loaded_preset) > 16:
            loaded_preset = f"{loaded_preset[:16]}..."

        # Load overlay widget
        wtoggle = WidgetToggle()

        # Load overlay auto hide state
        if cfg.overlay["auto_hide"]:
            overlay_hide.start()

        # Config tray icon
        name = "TinyPedal"
        image = Image.open("icon.ico")
        menu = pystray.Menu
        item = pystray.MenuItem
        separator = pystray.Menu.SEPARATOR

        # Add widget toggle items
        widget_menu = menu(
            item("Cruise", wtoggle.cruise, checked=lambda _: cfg.setting_user["cruise"]["enable"]),
            item("Delta best", wtoggle.deltabest, checked=lambda _: cfg.setting_user["deltabest"]["enable"]),
            item("DRS", wtoggle.drs, checked=lambda _: cfg.setting_user["drs"]["enable"]),
            item("Engine", wtoggle.engine, checked=lambda _: cfg.setting_user["engine"]["enable"]),
            item("Force", wtoggle.force, checked=lambda _: cfg.setting_user["force"]["enable"]),
            item("Fuel", wtoggle.fuel, checked=lambda _: cfg.setting_user["fuel"]["enable"]),
            item("Gear", wtoggle.gear, checked=lambda _: cfg.setting_user["gear"]["enable"]),
            item("Instrument", wtoggle.instrument, checked=lambda _: cfg.setting_user["instrument"]["enable"]),
            item("Pedal", wtoggle.pedal, checked=lambda _: cfg.setting_user["pedal"]["enable"]),
            item("Pressure", wtoggle.pressure, checked=lambda _: cfg.setting_user["pressure"]["enable"]),
            item("Radar", wtoggle.radar, checked=lambda _: cfg.setting_user["radar"]["enable"]),
            item("Relative", wtoggle.relative, checked=lambda _: cfg.setting_user["relative"]["enable"]),
            item("Session", wtoggle.session, checked=lambda _: cfg.setting_user["session"]["enable"]),
            item("Steering", wtoggle.steering, checked=lambda _: cfg.setting_user["steering"]["enable"]),
            item("Stint", wtoggle.stint, checked=lambda _: cfg.setting_user["stint"]["enable"]),
            item("Temperature", wtoggle.temperature, checked=lambda _: cfg.setting_user["temperature"]["enable"]),
            item("Timing", wtoggle.timing, checked=lambda _: cfg.setting_user["timing"]["enable"]),
            item("Wear", wtoggle.wear, checked=lambda _: cfg.setting_user["wear"]["enable"]),
            item("Weather", wtoggle.weather, checked=lambda _: cfg.setting_user["weather"]["enable"]),
            item("Wheel", wtoggle.wheel, checked=lambda _: cfg.setting_user["wheel"]["enable"]),
        )

        main_menu = (
            item(f"Preset: {loaded_preset}", "", enabled=False),
            separator,
            item("Lock Overlay", lambda: overlay_lock.toggle(cfg.active_widget_list),
                 checked=lambda enabled: cfg.overlay["fixed_position"]),
            item("Auto Hide", overlay_hide.toggle,
                 checked=lambda enabled: cfg.overlay["auto_hide"]),
            separator,
            item("Widgets", widget_menu),
            separator,
            item("About", self.master.deiconify),
            item("Quit", self.quit),
        )

        self.tray = pystray.Icon("icon", icon=image, title=name, menu=main_menu)

    def run(self):
        """Start tray icon"""
        self.tray.run_detached()

    def quit(self):
        """Quit tray icon

        Must quit root window first.
        """
        self.master.quit()
        self.tray.stop()


class WidgetToggle:
    """Widget toggle"""

    def __init__(self):
        """Activate widgets at startup"""
        if cfg.setting_user["cruise"]["enable"]:
            self.widget_cruise = cruise.DrawWidget()

        if cfg.setting_user["deltabest"]["enable"]:
            self.widget_deltabest = deltabest.DrawWidget()

        if cfg.setting_user["drs"]["enable"]:
            self.widget_drs = drs.DrawWidget()

        if cfg.setting_user["engine"]["enable"]:
            self.widget_engine = engine.DrawWidget()

        if cfg.setting_user["force"]["enable"]:
            self.widget_force = force.DrawWidget()

        if cfg.setting_user["fuel"]["enable"]:
            self.widget_fuel = fuel.DrawWidget()

        if cfg.setting_user["gear"]["enable"]:
            self.widget_gear = gear.DrawWidget()

        if cfg.setting_user["instrument"]["enable"]:
            self.widget_instrument = instrument.DrawWidget()

        if cfg.setting_user["pedal"]["enable"]:
            self.widget_pedal = pedal.DrawWidget()

        if cfg.setting_user["pressure"]["enable"]:
            self.widget_pressure = pressure.DrawWidget()

        if cfg.setting_user["radar"]["enable"]:
            self.widget_radar = radar.DrawWidget()

        if cfg.setting_user["relative"]["enable"]:
            self.widget_relative = relative.DrawWidget()

        if cfg.setting_user["session"]["enable"]:
            self.widget_session = session.DrawWidget()

        if cfg.setting_user["steering"]["enable"]:
            self.widget_steering = steering.DrawWidget()

        if cfg.setting_user["stint"]["enable"]:
            self.widget_stint = stint.DrawWidget()

        if cfg.setting_user["temperature"]["enable"]:
            self.widget_temperature = temperature.DrawWidget()

        if cfg.setting_user["timing"]["enable"]:
            self.widget_timing = timing.DrawWidget()

        if cfg.setting_user["wear"]["enable"]:
            self.widget_wear = wear.DrawWidget()

        if cfg.setting_user["weather"]["enable"]:
            self.widget_weather = weather.DrawWidget()

        if cfg.setting_user["wheel"]["enable"]:
            self.widget_wheel = wheel.DrawWidget()

    def cruise(self):
        """Toggle cruise"""
        if not cfg.setting_user["cruise"]["enable"]:
            self.widget_cruise = cruise.DrawWidget()
            cfg.setting_user["cruise"]["enable"] = True
        else:
            cfg.setting_user["cruise"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_cruise)
            self.widget_cruise.destroy()
        cfg.save()

    def deltabest(self):
        """Toggle deltabest"""
        if not cfg.setting_user["deltabest"]["enable"]:
            self.widget_deltabest = deltabest.DrawWidget()
            cfg.setting_user["deltabest"]["enable"] = True  # set True after widget enabled
        else:
            cfg.setting_user["deltabest"]["enable"] = False  # set False before widget disabled
            cfg.active_widget_list.remove(self.widget_deltabest)
            self.widget_deltabest.destroy()
        cfg.save()

    def drs(self):
        """Toggle DRS"""
        if not cfg.setting_user["drs"]["enable"]:
            self.widget_drs = drs.DrawWidget()
            cfg.setting_user["drs"]["enable"] = True
        else:
            cfg.setting_user["drs"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_drs)
            self.widget_drs.destroy()
        cfg.save()

    def engine(self):
        """Toggle engine"""
        if not cfg.setting_user["engine"]["enable"]:
            self.widget_engine = engine.DrawWidget()
            cfg.setting_user["engine"]["enable"] = True
        else:
            cfg.setting_user["engine"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_engine)
            self.widget_engine.destroy()
        cfg.save()

    def force(self):
        """Toggle force"""
        if not cfg.setting_user["force"]["enable"]:
            self.widget_force = force.DrawWidget()
            cfg.setting_user["force"]["enable"] = True
        else:
            cfg.setting_user["force"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_force)
            self.widget_force.destroy()
        cfg.save()

    def fuel(self):
        """Toggle fuel"""
        if not cfg.setting_user["fuel"]["enable"]:
            self.widget_fuel = fuel.DrawWidget()
            cfg.setting_user["fuel"]["enable"] = True
        else:
            cfg.setting_user["fuel"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_fuel)
            self.widget_fuel.destroy()
        cfg.save()

    def gear(self):
        """Toggle gear"""
        if not cfg.setting_user["gear"]["enable"]:
            self.widget_gear = gear.DrawWidget()
            cfg.setting_user["gear"]["enable"] = True
        else:
            cfg.setting_user["gear"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_gear)
            self.widget_gear.destroy()
        cfg.save()

    def instrument(self):
        """Toggle instrument"""
        if not cfg.setting_user["instrument"]["enable"]:
            self.widget_instrument = instrument.DrawWidget()
            cfg.setting_user["instrument"]["enable"] = True
        else:
            cfg.setting_user["instrument"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_instrument)
            self.widget_instrument.destroy()
        cfg.save()

    def pedal(self):
        """Toggle pedal"""
        if not cfg.setting_user["pedal"]["enable"]:
            self.widget_pedal = pedal.DrawWidget()
            cfg.setting_user["pedal"]["enable"] = True
        else:
            cfg.setting_user["pedal"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_pedal)
            self.widget_pedal.destroy()
        cfg.save()

    def pressure(self):
        """Toggle pressure"""
        if not cfg.setting_user["pressure"]["enable"]:
            self.widget_pressure = pressure.DrawWidget()
            cfg.setting_user["pressure"]["enable"] = True
        else:
            cfg.setting_user["pressure"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_pressure)
            self.widget_pressure.destroy()
        cfg.save()

    def radar(self):
        """Toggle radar"""
        if not cfg.setting_user["radar"]["enable"]:
            self.widget_radar = radar.DrawWidget()
            cfg.setting_user["radar"]["enable"] = True
        else:
            cfg.setting_user["radar"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_radar)
            self.widget_radar.destroy()
        cfg.save()

    def relative(self):
        """Toggle relative"""
        if not cfg.setting_user["relative"]["enable"]:
            self.widget_relative = relative.DrawWidget()
            cfg.setting_user["relative"]["enable"] = True
        else:
            cfg.setting_user["relative"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_relative)
            self.widget_relative.destroy()
        cfg.save()

    def session(self):
        """Toggle session"""
        if not cfg.setting_user["session"]["enable"]:
            self.widget_session = session.DrawWidget()
            cfg.setting_user["session"]["enable"] = True
        else:
            cfg.setting_user["session"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_session)
            self.widget_session.destroy()
        cfg.save()

    def steering(self):
        """Toggle steering"""
        if not cfg.setting_user["steering"]["enable"]:
            self.widget_steering = steering.DrawWidget()
            cfg.setting_user["steering"]["enable"] = True
        else:
            cfg.setting_user["steering"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_steering)
            self.widget_steering.destroy()
        cfg.save()

    def stint(self):
        """Toggle stint"""
        if not cfg.setting_user["stint"]["enable"]:
            self.widget_stint = stint.DrawWidget()
            cfg.setting_user["stint"]["enable"] = True
        else:
            cfg.setting_user["stint"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_stint)
            self.widget_stint.destroy()
        cfg.save()

    def temperature(self):
        """Toggle temperature"""
        if not cfg.setting_user["temperature"]["enable"]:
            self.widget_temperature = temperature.DrawWidget()
            cfg.setting_user["temperature"]["enable"] = True
        else:
            cfg.setting_user["temperature"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_temperature)
            self.widget_temperature.destroy()
        cfg.save()

    def timing(self):
        """Toggle timing"""
        if not cfg.setting_user["timing"]["enable"]:
            self.widget_timing = timing.DrawWidget()
            cfg.setting_user["timing"]["enable"] = True
        else:
            cfg.setting_user["timing"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_timing)
            self.widget_timing.destroy()
        cfg.save()

    def wear(self):
        """Toggle wear"""
        if not cfg.setting_user["wear"]["enable"]:
            self.widget_wear = wear.DrawWidget()
            cfg.setting_user["wear"]["enable"] = True
        else:
            cfg.setting_user["wear"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_wear)
            self.widget_wear.destroy()
        cfg.save()

    def weather(self):
        """Toggle weather"""
        if not cfg.setting_user["weather"]["enable"]:
            self.widget_weather = weather.DrawWidget()
            cfg.setting_user["weather"]["enable"] = True
        else:
            cfg.setting_user["weather"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_weather)
            self.widget_weather.destroy()
        cfg.save()

    def wheel(self):
        """Toggle wheel"""
        if not cfg.setting_user["wheel"]["enable"]:
            self.widget_wheel = wheel.DrawWidget()
            cfg.setting_user["wheel"]["enable"] = True
        else:
            cfg.setting_user["wheel"]["enable"] = False
            cfg.active_widget_list.remove(self.widget_wheel)
            self.widget_wheel.destroy()
        cfg.save()
