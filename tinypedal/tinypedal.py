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
            item("Pedal", wtoggle.pedal, checked=lambda _: cfg.pedal["enable"]),
            item("Steering", wtoggle.steering, checked=lambda _: cfg.steering["enable"]),
            item("Gear", wtoggle.gear, checked=lambda _: cfg.gear["enable"]),
            item("Fuel", wtoggle.fuel, checked=lambda _: cfg.fuel["enable"]),
            item("Timing", wtoggle.timing, checked=lambda _: cfg.timing["enable"]),
            item("Relative", wtoggle.relative, checked=lambda _: cfg.relative["enable"]),
            item("Wheel", wtoggle.wheel, checked=lambda _: cfg.wheel["enable"]),
            item("Temperature", wtoggle.temp, checked=lambda _: cfg.temp["enable"]),
            item("Tyre Wear", wtoggle.wear, checked=lambda _: cfg.wear["enable"]),
            item("Weather", wtoggle.weather, checked=lambda _: cfg.weather["enable"]),
            item("Force", wtoggle.force, checked=lambda _: cfg.force["enable"]),
            item("Engine", wtoggle.engine, checked=lambda _: cfg.engine["enable"]),
            item("DRS", wtoggle.drs, checked=lambda _: cfg.drs["enable"]),
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
        if cfg.pedal["enable"]:
            self.widget_pedal = widget.Pedal()

        if cfg.steering["enable"]:
            self.widget_steering = widget.Steering()

        if cfg.gear["enable"]:
            self.widget_gear = widget.Gear()

        if cfg.fuel["enable"]:
            self.widget_fuel = widget.Fuel()

        if cfg.timing["enable"]:
            self.widget_timing = widget.Timing()

        if cfg.wheel["enable"]:
            self.widget_wheel = widget.Wheel()

        if cfg.temp["enable"]:
            self.widget_temp = widget.Temp()

        if cfg.wear["enable"]:
            self.widget_wear = widget.Wear()

        if cfg.relative["enable"]:
            self.widget_relative = widget.Relative()

        if cfg.weather["enable"]:
            self.widget_weather = widget.Weather()

        if cfg.force["enable"]:
            self.widget_force = widget.Force()

        if cfg.engine["enable"]:
            self.widget_engine = widget.Engine()

        if cfg.drs["enable"]:
            self.widget_drs = widget.DRS()

    def pedal(self):
        """Toggle pedal"""
        cfg.load()
        if not cfg.pedal["enable"]:
            self.widget_pedal = widget.Pedal()
            cfg.pedal["enable"] = True  # set True after widget enabled
        else:
            cfg.pedal["enable"] = False  # set False before widget disabled
            cfg.active_widget_list.remove(self.widget_pedal)
            self.widget_pedal.destroy()
        cfg.save()

    def steering(self):
        """Toggle steering"""
        cfg.load()
        if not cfg.steering["enable"]:
            self.widget_steering = widget.Steering()
            cfg.steering["enable"] = True
        else:
            cfg.steering["enable"] = False
            cfg.active_widget_list.remove(self.widget_steering)
            self.widget_steering.destroy()
        cfg.save()

    def gear(self):
        """Toggle gear"""
        cfg.load()
        if not cfg.gear["enable"]:
            self.widget_gear = widget.Gear()
            cfg.gear["enable"] = True
        else:
            cfg.gear["enable"] = False
            cfg.active_widget_list.remove(self.widget_gear)
            self.widget_gear.destroy()
        cfg.save()

    def fuel(self):
        """Toggle fuel"""
        cfg.load()
        if not cfg.fuel["enable"]:
            self.widget_fuel = widget.Fuel()
            cfg.fuel["enable"] = True
        else:
            cfg.fuel["enable"] = False
            cfg.active_widget_list.remove(self.widget_fuel)
            self.widget_fuel.destroy()
        cfg.save()

    def timing(self):
        """Toggle timing"""
        cfg.load()
        if not cfg.timing["enable"]:
            self.widget_timing = widget.Timing()
            cfg.timing["enable"] = True
        else:
            cfg.timing["enable"] = False
            cfg.active_widget_list.remove(self.widget_timing)
            self.widget_timing.destroy()
        cfg.save()

    def wheel(self):
        """Toggle wheel"""
        cfg.load()
        if not cfg.wheel["enable"]:
            self.widget_wheel = widget.Wheel()
            cfg.wheel["enable"] = True
        else:
            cfg.wheel["enable"] = False
            cfg.active_widget_list.remove(self.widget_wheel)
            self.widget_wheel.destroy()
        cfg.save()

    def temp(self):
        """Toggle temperature"""
        cfg.load()
        if not cfg.temp["enable"]:
            self.widget_temp = widget.Temp()
            cfg.temp["enable"] = True
        else:
            cfg.temp["enable"] = False
            cfg.active_widget_list.remove(self.widget_temp)
            self.widget_temp.destroy()
        cfg.save()

    def wear(self):
        """Toggle wear"""
        cfg.load()
        if not cfg.wear["enable"]:
            self.widget_wear = widget.Wear()
            cfg.wear["enable"] = True
        else:
            cfg.wear["enable"] = False
            cfg.active_widget_list.remove(self.widget_wear)
            self.widget_wear.destroy()
        cfg.save()

    def relative(self):
        """Toggle relative"""
        cfg.load()
        if not cfg.relative["enable"]:
            self.widget_relative = widget.Relative()
            cfg.relative["enable"] = True
        else:
            cfg.relative["enable"] = False
            cfg.active_widget_list.remove(self.widget_relative)
            self.widget_relative.destroy()
        cfg.save()

    def weather(self):
        """Toggle weather"""
        cfg.load()
        if not cfg.weather["enable"]:
            self.widget_weather = widget.Weather()
            cfg.weather["enable"] = True
        else:
            cfg.weather["enable"] = False
            cfg.active_widget_list.remove(self.widget_weather)
            self.widget_weather.destroy()
        cfg.save()

    def force(self):
        """Toggle force"""
        cfg.load()
        if not cfg.force["enable"]:
            self.widget_force = widget.Force()
            cfg.force["enable"] = True
        else:
            cfg.force["enable"] = False
            cfg.active_widget_list.remove(self.widget_force)
            self.widget_force.destroy()
        cfg.save()

    def engine(self):
        """Toggle engine"""
        cfg.load()
        if not cfg.engine["enable"]:
            self.widget_engine = widget.Engine()
            cfg.engine["enable"] = True
        else:
            cfg.engine["enable"] = False
            cfg.active_widget_list.remove(self.widget_engine)
            self.widget_engine.destroy()
        cfg.save()

    def drs(self):
        """Toggle DRS"""
        cfg.load()
        if not cfg.drs["enable"]:
            self.widget_drs = widget.DRS()
            cfg.drs["enable"] = True
        else:
            cfg.drs["enable"] = False
            cfg.active_widget_list.remove(self.widget_drs)
            self.widget_drs.destroy()
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
