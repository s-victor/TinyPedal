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
Main program & tray icon
"""

from PIL import Image
import pystray

from tinypedal.base import cfg, OverlayLock, OverlayAutoHide
from tinypedal.about import About
from tinypedal import widget


class TrayIcon:
    """System tray icon

    Activate overlay widgets via system tray icon.
    """

    def __init__(self, master):
        self.master = master

        # Load overlay widget
        wtoggle = WidgetToggle()

        # Load overlay lock state
        overlay_lock = OverlayLock(cfg.active_widget_list)

        # Load overlay auto hide state
        overlay_hide = OverlayAutoHide(cfg.active_widget_list, master)
        overlay_hide.activate()

        # Config tray icon
        name = "TinyPedal"
        image = Image.open("icon.ico")
        menu = pystray.Menu
        item = pystray.MenuItem
        separator = pystray.Menu.SEPARATOR

        # Add widget toggle items
        widget_menu = menu(
            item("Delta best", wtoggle.deltabest, checked=lambda _: cfg.deltabest["enable"]),
            item("DRS", wtoggle.drs, checked=lambda _: cfg.drs["enable"]),
            item("Engine", wtoggle.engine, checked=lambda _: cfg.engine["enable"]),
            item("Force", wtoggle.force, checked=lambda _: cfg.force["enable"]),
            item("Fuel", wtoggle.fuel, checked=lambda _: cfg.fuel["enable"]),
            item("Gear", wtoggle.gear, checked=lambda _: cfg.gear["enable"]),
            item("Pedal", wtoggle.pedal, checked=lambda _: cfg.pedal["enable"]),
            item("Pressure", wtoggle.pressure, checked=lambda _: cfg.pressure["enable"]),
            item("Relative", wtoggle.relative, checked=lambda _: cfg.relative["enable"]),
            item("Steering", wtoggle.steering, checked=lambda _: cfg.steering["enable"]),
            item("Temperature", wtoggle.temperature, checked=lambda _: cfg.temperature["enable"]),
            item("Timing", wtoggle.timing, checked=lambda _: cfg.timing["enable"]),
            item("Wear", wtoggle.wear, checked=lambda _: cfg.wear["enable"]),
            item("Weather", wtoggle.weather, checked=lambda _: cfg.weather["enable"]),
            item("Wheel", wtoggle.wheel, checked=lambda _: cfg.wheel["enable"]),
        )

        main_menu = (
            item("Lock Overlay", overlay_lock.toggle,
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
        if cfg.deltabest["enable"]:
            self.widget_deltabest = widget.Deltabest()

        if cfg.drs["enable"]:
            self.widget_drs = widget.DRS()

        if cfg.engine["enable"]:
            self.widget_engine = widget.Engine()

        if cfg.force["enable"]:
            self.widget_force = widget.Force()

        if cfg.fuel["enable"]:
            self.widget_fuel = widget.Fuel()

        if cfg.gear["enable"]:
            self.widget_gear = widget.Gear()

        if cfg.pedal["enable"]:
            self.widget_pedal = widget.Pedal()

        if cfg.pressure["enable"]:
            self.widget_pressure = widget.Pressure()

        if cfg.relative["enable"]:
            self.widget_relative = widget.Relative()

        if cfg.steering["enable"]:
            self.widget_steering = widget.Steering()

        if cfg.temperature["enable"]:
            self.widget_temperature = widget.Temperature()

        if cfg.timing["enable"]:
            self.widget_timing = widget.Timing()

        if cfg.wear["enable"]:
            self.widget_wear = widget.Wear()

        if cfg.weather["enable"]:
            self.widget_weather = widget.Weather()

        if cfg.wheel["enable"]:
            self.widget_wheel = widget.Wheel()

    def deltabest(self):
        """Toggle deltabest"""
        if not cfg.deltabest["enable"]:
            self.widget_deltabest = widget.Deltabest()
            cfg.deltabest["enable"] = True  # set True after widget enabled
        else:
            cfg.deltabest["enable"] = False  # set False before widget disabled
            cfg.active_widget_list.remove(self.widget_deltabest)
            self.widget_deltabest.destroy()
        cfg.save()

    def drs(self):
        """Toggle DRS"""
        if not cfg.drs["enable"]:
            self.widget_drs = widget.DRS()
            cfg.drs["enable"] = True
        else:
            cfg.drs["enable"] = False
            cfg.active_widget_list.remove(self.widget_drs)
            self.widget_drs.destroy()
        cfg.save()

    def engine(self):
        """Toggle engine"""
        if not cfg.engine["enable"]:
            self.widget_engine = widget.Engine()
            cfg.engine["enable"] = True
        else:
            cfg.engine["enable"] = False
            cfg.active_widget_list.remove(self.widget_engine)
            self.widget_engine.destroy()
        cfg.save()

    def force(self):
        """Toggle force"""
        if not cfg.force["enable"]:
            self.widget_force = widget.Force()
            cfg.force["enable"] = True
        else:
            cfg.force["enable"] = False
            cfg.active_widget_list.remove(self.widget_force)
            self.widget_force.destroy()
        cfg.save()

    def fuel(self):
        """Toggle fuel"""
        if not cfg.fuel["enable"]:
            self.widget_fuel = widget.Fuel()
            cfg.fuel["enable"] = True
        else:
            cfg.fuel["enable"] = False
            cfg.active_widget_list.remove(self.widget_fuel)
            self.widget_fuel.destroy()
        cfg.save()

    def gear(self):
        """Toggle gear"""
        if not cfg.gear["enable"]:
            self.widget_gear = widget.Gear()
            cfg.gear["enable"] = True
        else:
            cfg.gear["enable"] = False
            cfg.active_widget_list.remove(self.widget_gear)
            self.widget_gear.destroy()
        cfg.save()

    def pedal(self):
        """Toggle pedal"""
        if not cfg.pedal["enable"]:
            self.widget_pedal = widget.Pedal()
            cfg.pedal["enable"] = True
        else:
            cfg.pedal["enable"] = False
            cfg.active_widget_list.remove(self.widget_pedal)
            self.widget_pedal.destroy()
        cfg.save()

    def pressure(self):
        """Toggle pressure"""
        if not cfg.pressure["enable"]:
            self.widget_pressure = widget.Pressure()
            cfg.pressure["enable"] = True
        else:
            cfg.pressure["enable"] = False
            cfg.active_widget_list.remove(self.widget_pressure)
            self.widget_pressure.destroy()
        cfg.save()

    def relative(self):
        """Toggle relative"""
        if not cfg.relative["enable"]:
            self.widget_relative = widget.Relative()
            cfg.relative["enable"] = True
        else:
            cfg.relative["enable"] = False
            cfg.active_widget_list.remove(self.widget_relative)
            self.widget_relative.destroy()
        cfg.save()

    def steering(self):
        """Toggle steering"""
        if not cfg.steering["enable"]:
            self.widget_steering = widget.Steering()
            cfg.steering["enable"] = True
        else:
            cfg.steering["enable"] = False
            cfg.active_widget_list.remove(self.widget_steering)
            self.widget_steering.destroy()
        cfg.save()

    def temperature(self):
        """Toggle temperature"""
        if not cfg.temperature["enable"]:
            self.widget_temperature = widget.Temperature()
            cfg.temperature["enable"] = True
        else:
            cfg.temperature["enable"] = False
            cfg.active_widget_list.remove(self.widget_temperature)
            self.widget_temperature.destroy()
        cfg.save()

    def timing(self):
        """Toggle timing"""
        if not cfg.timing["enable"]:
            self.widget_timing = widget.Timing()
            cfg.timing["enable"] = True
        else:
            cfg.timing["enable"] = False
            cfg.active_widget_list.remove(self.widget_timing)
            self.widget_timing.destroy()
        cfg.save()

    def wear(self):
        """Toggle wear"""
        if not cfg.wear["enable"]:
            self.widget_wear = widget.Wear()
            cfg.wear["enable"] = True
        else:
            cfg.wear["enable"] = False
            cfg.active_widget_list.remove(self.widget_wear)
            self.widget_wear.destroy()
        cfg.save()

    def weather(self):
        """Toggle weather"""
        if not cfg.weather["enable"]:
            self.widget_weather = widget.Weather()
            cfg.weather["enable"] = True
        else:
            cfg.weather["enable"] = False
            cfg.active_widget_list.remove(self.widget_weather)
            self.widget_weather.destroy()
        cfg.save()

    def wheel(self):
        """Toggle wheel"""
        if not cfg.wheel["enable"]:
            self.widget_wheel = widget.Wheel()
            cfg.wheel["enable"] = True
        else:
            cfg.wheel["enable"] = False
            cfg.active_widget_list.remove(self.widget_wheel)
            self.widget_wheel.destroy()
        cfg.save()


def run():
    """Start program"""
    root = About()

    # Start tray icon
    tray_icon = TrayIcon(root)
    tray_icon.run()

    # Start tkinter mainloop
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    root.mainloop()


if __name__ == "__main__":
    run()
