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
Fuel Widget
"""

from PySide2.QtCore import Qt, Slot, QRectF
from PySide2.QtGui import QPainter, QPixmap, QColor, QFont, QFontMetrics
from PySide2.QtWidgets import (
    QLabel,
    QGridLayout,
)

from .. import calculation as calc
from .. import readapi as read_data
from ..base import Widget
from ..module_control import mctrl

WIDGET_NAME = "fuel"


class Draw(Widget):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Widget.__init__(self, config, WIDGET_NAME)

        # Config font
        self.font = QFont()
        self.font.setFamily(self.wcfg['font_name'])
        self.font.setPixelSize(self.wcfg['font_size'])
        font_w = QFontMetrics(self.font).averageCharWidth()

        # Config variable
        text_def = "-.--"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )
        self.bar_font_size = f"font-size: {self.wcfg['font_size']}px;"
        self.bar_width = f"min-width: {font_w * 5}px;max-width: {font_w * 5}px;"

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_upper = QGridLayout()
        layout_lower = QGridLayout()
        layout_upper.setSpacing(0)
        layout_lower.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
                f"{self.bar_width}"
            )
            caption_list = ("start", "fuel", "refuel", "used", "delta",
                            "end", "laps", "mins","save", "pits")
            for index, caption in enumerate(caption_list):
                setattr(self, f"bar_desc_{caption}", QLabel(caption))
                getattr(self, f"bar_desc_{caption}").setAlignment(Qt.AlignCenter)
                getattr(self, f"bar_desc_{caption}").setStyleSheet(bar_style_desc)
                if index < 5:
                    layout_upper.addWidget(getattr(self, f"bar_desc_{caption}"), 0, index)
                else:
                    layout_lower.addWidget(getattr(self, f"bar_desc_{caption}"), 1, index - 5)

        # Start fuel
        self.bar_fuel_start = QLabel(text_def)
        self.bar_fuel_start.setAlignment(Qt.AlignCenter)
        self.bar_fuel_start.setStyleSheet(
            f"color: {self.wcfg['font_color_start']};"
            f"background: {self.wcfg['bkg_color_start']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Fuel
        self.bar_fuel_curr = QLabel(text_def)
        self.bar_fuel_curr.setAlignment(Qt.AlignCenter)
        self.bar_fuel_curr.setStyleSheet(
            f"color: {self.wcfg['font_color_fuel']};"
            f"background: {self.wcfg['bkg_color_fuel']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Fuel required
        self.bar_fuel_need = QLabel(text_def)
        self.bar_fuel_need.setAlignment(Qt.AlignCenter)
        self.bar_fuel_need.setStyleSheet(
            f"color: {self.wcfg['font_color_fuel']};"
            f"background: {self.wcfg['bkg_color_fuel']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Fuel consumption
        self.bar_fuel_used = QLabel(text_def)
        self.bar_fuel_used.setAlignment(Qt.AlignCenter)
        self.bar_fuel_used.setStyleSheet(
            f"color: {self.wcfg['font_color_consumption']};"
            f"background: {self.wcfg['bkg_color_consumption']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Fuel delta
        self.bar_fuel_delta = QLabel(text_def)
        self.bar_fuel_delta.setAlignment(Qt.AlignCenter)
        self.bar_fuel_delta.setStyleSheet(
            f"color: {self.wcfg['font_color_delta']};"
            f"background: {self.wcfg['bkg_color_delta']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # End fuel
        self.bar_fuel_end = QLabel(text_def)
        self.bar_fuel_end.setAlignment(Qt.AlignCenter)
        self.bar_fuel_end.setStyleSheet(
            f"color: {self.wcfg['font_color_end']};"
            f"background: {self.wcfg['bkg_color_end']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Estimated laps
        self.bar_fuel_laps = QLabel(text_def)
        self.bar_fuel_laps.setAlignment(Qt.AlignCenter)
        self.bar_fuel_laps.setStyleSheet(
            f"color: {self.wcfg['font_color_estimate_laps']};"
            f"background: {self.wcfg['bkg_color_estimate_laps']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Estimated minutes
        self.bar_fuel_mins = QLabel(text_def)
        self.bar_fuel_mins.setAlignment(Qt.AlignCenter)
        self.bar_fuel_mins.setStyleSheet(
            f"color: {self.wcfg['font_color_estimate_mins']};"
            f"background: {self.wcfg['bkg_color_estimate_mins']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # One less pit fuel consumption
        self.bar_fuel_save = QLabel(text_def)
        self.bar_fuel_save.setAlignment(Qt.AlignCenter)
        self.bar_fuel_save.setStyleSheet(
            f"color: {self.wcfg['font_color_one_less_pit_consumption']};"
            f"background: {self.wcfg['bkg_color_one_less_pit_consumption']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Estimated pits
        self.bar_fuel_pits = QLabel(text_def)
        self.bar_fuel_pits.setAlignment(Qt.AlignCenter)
        self.bar_fuel_pits.setStyleSheet(
            f"color: {self.wcfg['font_color_pits']};"
            f"background: {self.wcfg['bkg_color_pits']};"
            f"{self.bar_width}"
            f"{self.bar_font_size}"
        )

        # Fuel level bar
        if self.wcfg["show_fuel_level_bar"]:
            self.fuel_level_width = font_w * (5+5+5+5+5) + bar_padx * (5*2)
            self.fuel_level_height = self.wcfg["fuel_level_bar_height"]
            blank_fuel_level = QPixmap(self.fuel_level_width, self.fuel_level_height)

            self.fuel_level = QLabel()
            self.fuel_level.setFixedSize(self.fuel_level_width, self.fuel_level_height)
            self.fuel_level.setStyleSheet("padding: 0;")
            self.fuel_level.setPixmap(blank_fuel_level)
            self.draw_fuel_level(self.fuel_level, [0,0])

        # Set layout
        layout_upper.addWidget(self.bar_fuel_start, 1, 0)
        layout_upper.addWidget(self.bar_fuel_curr, 1, 1)
        layout_upper.addWidget(self.bar_fuel_need, 1, 2)
        layout_upper.addWidget(self.bar_fuel_used, 1, 3)
        layout_upper.addWidget(self.bar_fuel_delta, 1, 4)
        layout_lower.addWidget(self.bar_fuel_end, 0, 0)
        layout_lower.addWidget(self.bar_fuel_laps, 0, 1)
        layout_lower.addWidget(self.bar_fuel_mins, 0, 2)
        layout_lower.addWidget(self.bar_fuel_save, 0, 3)
        layout_lower.addWidget(self.bar_fuel_pits, 0, 4)
        layout.addLayout(layout_upper, 0, 0)
        if self.wcfg["show_fuel_level_bar"]:
            layout.addWidget(self.fuel_level, 1, 0)
        layout.addLayout(layout_lower, 2, 0)
        self.setLayout(layout)

        # Last data
        self.last_amount_start = None
        self.last_amount_curr = None
        self.last_amount_need = None
        self.last_used_last = None
        self.last_delta_fuel = None
        self.last_amount_end = None
        self.last_est_runlaps = None
        self.last_est_runmins = None
        self.last_fuel_save = None
        self.last_pit_required = None
        self.last_fuel_level = None

        # Set widget state & start update
        self.set_widget_state()
        self.update_timer.start()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if self.wcfg["enable"] and read_data.state():

            # Read fuel data from fuel usage module
            fuel_info = mctrl.module_fuel.output

            # Start fuel
            amount_start = f"{self.fuel_units(fuel_info.AmountFuelStart):.1f}"
            self.update_fuel_misc("start", amount_start, self.last_amount_start)
            self.last_amount_start = amount_start

            # Current remaining fuel
            amount_curr = f"{self.fuel_units(fuel_info.AmountFuelCurrent):.2f}"
            self.update_fuel_curr(
                "curr", amount_curr, self.last_amount_curr, fuel_info.EstimatedLaps)
            self.last_amount_curr = amount_curr

            # Total needed fuel
            amount_need = f"{min(max(self.fuel_units(fuel_info.AmountFuelNeeded), -9999), 9999):+0.2f}"
            self.update_fuel_curr(
                "need", amount_need, self.last_amount_need, fuel_info.EstimatedLaps)
            self.last_amount_need = amount_need

            # Estimated fuel consumption
            used_last = f"{self.fuel_units(fuel_info.EstimatedFuelConsumption):.2f}"
            self.update_fuel_misc("used", used_last, self.last_used_last)
            self.last_used_last = used_last

            # Delta fuel consumption
            delta_fuel = f"{self.fuel_units(fuel_info.DeltaFuelConsumption):+.2f}"
            self.update_fuel_misc("delta", delta_fuel, self.last_delta_fuel)
            self.last_delta_fuel = delta_fuel

            # End fuel
            amount_end = f"{self.fuel_units(fuel_info.AmountFuelBeforePitstop):.2f}"
            self.update_fuel_misc("end", amount_end, self.last_amount_end)
            self.last_amount_end = amount_end

            # Estimated laps current fuel can last
            est_runlaps = f"{min(fuel_info.EstimatedLaps, 9999):.1f}"
            self.update_fuel_misc("laps", est_runlaps, self.last_est_runlaps)
            self.last_est_runlaps = est_runlaps

            # Estimated minutes current fuel can last
            est_runmins = f"{min(fuel_info.EstimatedMinutes, 9999):.1f}"
            self.update_fuel_misc("mins", est_runmins, self.last_est_runmins)
            self.last_est_runmins = est_runmins

            # One less pit fuel consumption
            fuel_save = f"{min(max(self.fuel_units(fuel_info.OneLessPitFuelConsumption), 0), 99.99):.2f}"
            self.update_fuel_misc("save", fuel_save, self.last_fuel_save)
            self.last_fuel_save = fuel_save

            # Estimated pitstops required to finish race
            pit_required = f"{min(max(fuel_info.RequiredPitStops, 0), 99.99):.2f}"
            self.update_fuel_misc("pits", pit_required, self.last_pit_required)
            self.last_pit_required = pit_required

            # Fuel level bar
            if self.wcfg["show_fuel_level_bar"]:
                fuel_level = (
                    round((fuel_info.AmountFuelCurrent / max(fuel_info.Capacity, 1)), 3),
                    round((fuel_info.AmountFuelStart / max(fuel_info.Capacity, 1)), 3)
                )
                self.update_fuel_level(fuel_level, self.last_fuel_level)
                self.last_fuel_level = fuel_level

    # GUI update methods
    def update_fuel_curr(self, suffix, curr, last, state):
        """Update fuel data"""
        if curr != last:
            if state:  # low fuel warning
                getattr(self, f"bar_fuel_{suffix}").setStyleSheet(
                    f"color: {self.wcfg['font_color_fuel']};"
                    f"background: {self.color_lowfuel(state)};"
                    f"{self.bar_width}{self.bar_font_size}"
                )
            getattr(self, f"bar_fuel_{suffix}").setText(
                calc.del_decimal_point(curr[:5]))

    def update_fuel_misc(self, suffix, curr, last):
        """Update fuel data"""
        if curr != last:
            getattr(self, f"bar_fuel_{suffix}").setText(
                calc.del_decimal_point(curr[:5]))

    def update_fuel_level(self, curr, last):
        """Fuel level update"""
        if curr != last:
            self.draw_fuel_level(self.fuel_level, curr)

    def draw_fuel_level(self, canvas, fuel_data):
        """Fuel level"""
        fuel_level = canvas.pixmap()
        painter = QPainter(fuel_level)
        #painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setPen(Qt.NoPen)

        # Set fuel level size
        rect_fuel_level = QRectF(0, 0, self.fuel_level_width, self.fuel_level_height)
        rect_fuel_left = QRectF(0, 0, fuel_data[0] * self.fuel_level_width, self.fuel_level_height)

        # Update fuel level background
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(rect_fuel_level, QColor(self.wcfg["bkg_color_fuel_level"]))
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)

        # Update starting fuel level mark
        if self.wcfg["show_starting_fuel_level_mark"]:
            rect_fuel_start = QRectF(
                fuel_data[1] * self.fuel_level_width,
                0,
                max(self.wcfg["starting_fuel_level_mark_width"], 1),
                self.fuel_level_height
            )
            painter.fillRect(rect_fuel_start, QColor(self.wcfg["starting_fuel_level_mark_color"]))

        # Update fuel level highlight
        painter.fillRect(rect_fuel_left, QColor(self.wcfg["highlight_color_fuel_level"]))

        canvas.setPixmap(fuel_level)

    # Additional methods
    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if self.cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def color_lowfuel(self, fuel):
        """Low fuel warning color"""
        if fuel > self.wcfg["low_fuel_lap_threshold"]:
            return self.wcfg["bkg_color_fuel"]
        return self.wcfg["warning_color_low_fuel"]
