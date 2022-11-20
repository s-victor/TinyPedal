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
Instrument Widget
"""

import tkinter as tk
from PIL import Image, ImageTk

import tinypedal.calculation as calc
import tinypedal.readapi as read_data
from tinypedal.base import Widget, MouseEvent


class Draw(Widget, MouseEvent):
    """Draw widget"""
    widget_name = "instrument"

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self)
        self.cfg = config
        self.wcfg = self.cfg.setting_user[self.widget_name]

        # Config title & background
        self.title("TinyPedal - " + self.widget_name.capitalize())
        self.attributes("-alpha", self.wcfg["opacity"])

        # Config size & position
        self.geometry(f"+{self.wcfg['position_x']}+{self.wcfg['position_y']}")

        # Config style & variable
        self.icon_size = int(max(self.wcfg["icon_size"], 16) / 2) * 2
        icon_source = Image.open("images/icon_instrument.png")
        icon_resize = icon_source.resize((self.icon_size * 2, self.icon_size * 5), resample=1)
        icon_image = ImageTk.PhotoImage(icon_resize)
        self.image = icon_image

        bar_style = {"bd":0, "highlightthickness":0, "bg":self.wcfg["bkg_color"],
                     "height":self.icon_size, "width":self.icon_size}

        self.list_radius_f = []
        self.list_radius_r = []
        self.avg_wheel_radius_f = self.wcfg["wheel_radius_front"]
        self.avg_wheel_radius_r = self.wcfg["wheel_radius_rear"]
        self.checked = False

        # Set state for drawing optimization
        self.state_hl = True  # headlights
        self.state_ig = True  # ignition
        self.state_st = True  # starter
        self.state_cl = True  # clutch
        self.state_ac = True  # auto clutch
        self.state_wl = True  # wheel lock
        self.state_ws = True  # wheel slip

        # Draw widget

        # Headlights
        self.bar_headlights = tk.Canvas(self, bar_style)
        self.icon_headlights = self.bar_headlights.create_image(
                               0, self.icon_size * 5, image=icon_image, anchor="s")

        # Ignition
        self.bar_ignition = tk.Canvas(self, bar_style)
        self.icon_ignition = self.bar_ignition.create_image(
                             0, self.icon_size * 4, image=icon_image, anchor="s")

        # Clutch
        self.bar_clutch = tk.Canvas(self, bar_style)
        self.icon_clutch = self.bar_clutch.create_image(
                           0, self.icon_size * 3, image=icon_image, anchor="s")

        # Lock
        self.bar_lock = tk.Canvas(self, bar_style)
        self.icon_lock = self.bar_lock.create_image(
                         0, self.icon_size * 2, image=icon_image, anchor="s")

        # Slip
        self.bar_slip = tk.Canvas(self, bar_style)
        self.icon_slip = self.bar_slip.create_image(
                         0, self.icon_size, image=icon_image, anchor="s")

        column_hl = self.wcfg["column_index_headlights"]
        column_ig = self.wcfg["column_index_ignition"]
        column_cl = self.wcfg["column_index_clutch"]
        column_wl = self.wcfg["column_index_wheel_lock"]
        column_ws = self.wcfg["column_index_wheel_slip"]

        if self.wcfg["layout"] == "0":
            self.bar_headlights.grid(row=0, column=column_hl, padx=(0, self.wcfg["bar_gap"]), pady=0)
            self.bar_ignition.grid(row=0, column=column_ig, padx=(0, self.wcfg["bar_gap"]), pady=0)
            self.bar_clutch.grid(row=0, column=column_cl, padx=(0, self.wcfg["bar_gap"]), pady=0)
            self.bar_lock.grid(row=0, column=column_wl, padx=(0, self.wcfg["bar_gap"]), pady=0)
            self.bar_slip.grid(row=0, column=column_ws, padx=(0, self.wcfg["bar_gap"]), pady=0)
        else:
            self.bar_headlights.grid(row=column_hl, column=0, padx=0, pady=(0, self.wcfg["bar_gap"]))
            self.bar_ignition.grid(row=column_ig, column=0, padx=0, pady=(0, self.wcfg["bar_gap"]))
            self.bar_clutch.grid(row=column_cl, column=0, padx=0, pady=(0, self.wcfg["bar_gap"]))
            self.bar_lock.grid(row=column_wl, column=0, padx=0, pady=(0, self.wcfg["bar_gap"]))
            self.bar_slip.grid(row=column_ws, column=0, padx=0, pady=(0, self.wcfg["bar_gap"]))

        self.update_data()

        # Assign mouse event
        MouseEvent.__init__(self)

    def update_data(self):
        """Update when vehicle on track"""
        if read_data.state() and self.wcfg["enable"]:

            # Save switch
            if not self.checked:
                self.checked = True

            # Read instrument data
            (headlights, ignition, rpm, autoclutch, clutch, brake, wheel_rot, speed
             ) = read_data.instrument()

            # Start updating
            if speed > self.wcfg["minimum_speed"]:
                # Get wheel rotation difference
                diff_rot_f = calc.max_vs_avg_rotation(wheel_rot[0], wheel_rot[1])
                diff_rot_r = calc.max_vs_avg_rotation(wheel_rot[2], wheel_rot[3])
                # Record radius value for targeted rotation difference
                if 0 < diff_rot_f < 0.1:
                    self.list_radius_f.append(abs(speed * 2 / (wheel_rot[0] + wheel_rot[1])))
                if 0 < diff_rot_r < 0.1:
                    self.list_radius_r.append(abs(speed * 2 / (wheel_rot[2] + wheel_rot[3])))

                # Calc average wheel radius reading
                minimum_samples = max(self.wcfg["minimum_samples"], 100)

                if len(self.list_radius_f) >= minimum_samples:
                    radius_samples_f = sorted(self.list_radius_f)[int(minimum_samples*0.25):int(minimum_samples*0.75)]
                    self.avg_wheel_radius_f = round(sum(radius_samples_f) / len(radius_samples_f), 3)
                    self.list_radius_f = []  # reset list

                if len(self.list_radius_r) >= minimum_samples:
                    radius_samples_r = sorted(self.list_radius_r)[int(minimum_samples*0.25):int(minimum_samples*0.75)]
                    self.avg_wheel_radius_r = round(sum(radius_samples_r) / len(radius_samples_r), 3)
                    self.list_radius_r = []

            slipratio = max(calc.slip_ratio(wheel_rot[0], self.avg_wheel_radius_f, speed),
                            calc.slip_ratio(wheel_rot[1], self.avg_wheel_radius_f, speed),
                            calc.slip_ratio(wheel_rot[2], self.avg_wheel_radius_r, speed),
                            calc.slip_ratio(wheel_rot[3], self.avg_wheel_radius_r, speed))

            # Headlights
            if headlights == 1 and self.state_hl:
                self.bar_headlights.coords(self.icon_headlights, self.icon_size, self.icon_size * 5)
                self.state_hl = False
            elif headlights == 0 and not self.state_hl:
                self.bar_headlights.coords(self.icon_headlights, 0, self.icon_size * 5)
                self.state_hl = True

            # Ignition
            if ignition > 0 and self.state_ig:
                self.bar_ignition.coords(self.icon_ignition, self.icon_size, self.icon_size * 4)
                self.state_ig = False
            elif ignition == 0 and not self.state_ig:
                self.bar_ignition.coords(self.icon_ignition, 0, self.icon_size * 4)
                self.state_ig = True

            if rpm < 10 and self.state_st:
                self.bar_ignition.config(bg=self.wcfg["warning_color_ignition"])
                self.state_st = False
            elif rpm > 10 and not self.state_st:
                self.bar_ignition.config(bg=self.wcfg["bkg_color"])
                self.state_st = True

            # Clutch
            if autoclutch == 1 and self.state_cl:
                self.bar_clutch.coords(self.icon_clutch, self.icon_size, self.icon_size * 3)
                self.state_cl = False
            elif autoclutch == 0 and not self.state_cl:
                self.bar_clutch.coords(self.icon_clutch, 0, self.icon_size * 3)
                self.state_cl = True

            if clutch > 0.01 and self.state_ac:
                self.bar_clutch.config(bg=self.wcfg["warning_color_clutch"])
                self.state_ac = False
            elif clutch <= 0.01 and not self.state_ac:
                self.bar_clutch.config(bg=self.wcfg["bkg_color"])
                self.state_ac = True

            # Wheel lock
            if brake > 0 and slipratio >= self.wcfg["wheel_lock_threshold"] and self.state_wl:
                self.bar_lock.coords(self.icon_lock, self.icon_size, self.icon_size * 2)
                self.bar_lock.config(bg=self.wcfg["warning_color_wheel_lock"])
                self.state_wl = False
            elif not self.state_wl:
                self.bar_lock.coords(self.icon_lock, 0, self.icon_size * 2)
                self.bar_lock.config(bg=self.wcfg["bkg_color"])
                self.state_wl = True

            # Wheel slip
            if slipratio >= self.wcfg["wheel_slip_threshold"] and self.state_ws:
                self.bar_slip.coords(self.icon_slip, self.icon_size, self.icon_size)
                self.bar_slip.config(bg=self.wcfg["warning_color_wheel_slip"])
                self.state_ws = False
            elif not self.state_ws:
                self.bar_slip.coords(self.icon_slip, 0, self.icon_size)
                self.bar_slip.config(bg=self.wcfg["bkg_color"])
                self.state_ws = True

        else:
            if self.checked:
                self.checked = False

                self.state_hl = True
                self.state_ig = True
                self.state_st = True
                self.state_cl = True
                self.state_ac = True
                self.state_wl = True
                self.state_ws = True

                self.bar_headlights.coords(self.icon_headlights, 0, self.icon_size * 5)
                self.bar_ignition.coords(self.icon_ignition, 0, self.icon_size * 4)
                self.bar_clutch.coords(self.icon_clutch, 0, self.icon_size * 3)
                self.bar_lock.coords(self.icon_lock, 0, self.icon_size * 2)
                self.bar_slip.coords(self.icon_slip, 0, self.icon_size)

                self.bar_ignition.config(bg=self.wcfg["bkg_color"])
                self.bar_clutch.config(bg=self.wcfg["bkg_color"])
                self.bar_lock.config(bg=self.wcfg["bkg_color"])
                self.bar_slip.config(bg=self.wcfg["bkg_color"])

                self.wcfg["wheel_radius_front"] = self.avg_wheel_radius_f
                self.wcfg["wheel_radius_rear"] = self.avg_wheel_radius_r
                self.cfg.save()

        # Update rate
        self.after(self.wcfg["update_delay"], self.update_data)
