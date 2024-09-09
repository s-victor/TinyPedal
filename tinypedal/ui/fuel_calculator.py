#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
Fuel calculator
"""

import math
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QBrush, QColor, QPalette
from PySide2.QtWidgets import (
    QWidget,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QFrame,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)

from ..api_control import api
from ..const import APP_ICON
from ..setting import cfg
from ..module_info import minfo
from .. import calculation as calc
from .. import formatter as fmt

PANEL_LEFT_WIDTH = 350
READ_ONLY_COLOR = QPalette().window().color().name(QColor.HexRgb)
HIGHLIGHT_COLOR = "#F40"


def set_read_only_style(line_edit, highlight=False):
    """Set read only style"""
    if highlight:
        color = HIGHLIGHT_COLOR
    else:
        color = READ_ONLY_COLOR
    line_edit.setStyleSheet(f"background:{color};")


def fuel_units(fuel):
    """2 different fuel unit conversion, default is Liter"""
    if cfg.units["fuel_unit"] == "Gallon":
        return calc.liter2gallon(fuel)
    return fuel


def fuel_unit_text():
    """Set fuel unit text"""
    if cfg.units["fuel_unit"] == "Gallon":
        return "gal"
    return "L"


class FuelCalculator(QDialog):
    """Fuel calculator"""

    def __init__(self, master):
        super().__init__(master)
        # Base setting
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setWindowTitle("Fuel Calculator")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.history_data = minfo.history.consumption

        # Set view
        self.panel_calculator = QWidget()
        self.set_panel_calculator(self.panel_calculator)

        # Panel table
        self.panel_table = QWidget()
        self.set_panel_table(self.panel_table)

        # Load data
        self.reload_data()

        # Layout
        layout_main = QHBoxLayout()
        layout_main.addWidget(self.panel_calculator)
        layout_main.addWidget(self.panel_table)
        self.setLayout(layout_main)
        self.setFixedWidth(self.sizeHint().width())

    def toggle_history_panel(self):
        """Toggle history data panel"""
        if self.panel_table.isHidden():
            self.panel_table.show()
            self.setFixedWidth(self.sizeHint().width())
            self.button_toggle.setText("Hide history")
        else:
            self.panel_table.hide()
            self.setFixedWidth(self.sizeHint().width())
            self.button_toggle.setText("Show history")

    def add_selected_data(self):
        """Add selected history data"""
        selected_data = self.table_history.selectedItems()
        if not selected_data:
            QMessageBox.warning(
                self, "Error",
                "No data selected.")
            return None

        data_laptime = [data for data in selected_data if data.column() == 1]
        data_fuel = [data for data in selected_data if data.column() == 2]
        data_energy = [data for data in selected_data if data.column() == 3]

        # Send data to calculator
        if data_laptime:
            dataset = [fmt.laptime_string_to_seconds(data.text()) for data in data_laptime]
            output_value = calc.mean(dataset) if len(data_laptime) > 1 else dataset[0]
            self.input_laptime.minutes.setValue(output_value // 60)
            self.input_laptime.seconds.setValue(output_value % 60)
            self.input_laptime.mseconds.setValue(output_value % 1 * 1000)
        if data_fuel:
            dataset = [float(data.text()) for data in data_fuel]
            output_value = calc.mean(dataset) if len(data_fuel) > 1 else dataset[0]
            self.input_fuel.fuel_used.setValue(output_value)
        if data_energy:
            dataset = [float(data.text()) for data in data_energy]
            output_value = calc.mean(dataset) if len(data_energy) > 1 else dataset[0]
            self.input_fuel.energy_used.setValue(output_value)
        return None

    def reload_data(self):
        """Reload history data"""
        self.refresh_table()
        # Load laptime from last valid lap
        laptime = self.history_data[0][2]
        if laptime > 0 and self.history_data[0][1]:
            self.input_laptime.minutes.setValue(laptime // 60)
            self.input_laptime.seconds.setValue(laptime % 60)
            self.input_laptime.mseconds.setValue(laptime % 1 * 1000)
        # Load tank capacity
        capacity = api.read.vehicle.tank_capacity()
        if capacity:
            self.input_fuel.capacity.setValue(fuel_units(capacity))
        # Load consumption from last valid lap
        if self.history_data[0][1]:
            fuel_used = self.history_data[0][3]
            self.input_fuel.fuel_used.setValue(fuel_units(fuel_used))
            energy_used = self.history_data[0][4]
            self.input_fuel.energy_used.setValue(energy_used)

    def refresh_table(self):
        """Refresh history data table"""
        self.history_data = minfo.history.consumption
        self.table_history.clear()
        self.table_history.setRowCount(len(self.history_data))
        row_index = 0
        style_invalid = QBrush("#C40", Qt.SolidPattern)

        for lap in self.history_data:
            lapnumber = QTableWidgetItem()
            lapnumber.setText(f"{lap[0]}")
            lapnumber.setTextAlignment(Qt.AlignCenter)
            lapnumber.setFlags(Qt.ItemFlags(0))

            laptime = QTableWidgetItem()
            laptime.setText(calc.sec2laptime(lap[2]))
            laptime.setTextAlignment(Qt.AlignCenter)
            laptime.setFlags(Qt.ItemFlags(33))

            used_fuel = QTableWidgetItem()
            used_fuel.setText(f"{fuel_units(lap[3]):.3f}")
            used_fuel.setTextAlignment(Qt.AlignCenter)
            used_fuel.setFlags(Qt.ItemFlags(33))

            used_energy = QTableWidgetItem()
            used_energy.setText(f"{lap[4]:.3f}")
            used_energy.setTextAlignment(Qt.AlignCenter)
            used_energy.setFlags(Qt.ItemFlags(33))

            battery_drain = QTableWidgetItem()
            battery_drain.setText(f"{lap[5]:.3f}")
            battery_drain.setTextAlignment(Qt.AlignCenter)
            battery_drain.setFlags(Qt.ItemFlags(0))

            battery_regen = QTableWidgetItem()
            battery_regen.setText(f"{lap[6]:.3f}")
            battery_regen.setTextAlignment(Qt.AlignCenter)
            battery_regen.setFlags(Qt.ItemFlags(0))

            if not lap[1]:  # set invalid lap text color
                laptime.setForeground(style_invalid)
                used_fuel.setForeground(style_invalid)
                used_energy.setForeground(style_invalid)

            self.table_history.setItem(row_index, 0, lapnumber)
            self.table_history.setItem(row_index, 1, laptime)
            self.table_history.setItem(row_index, 2, used_fuel)
            self.table_history.setItem(row_index, 3, used_energy)
            self.table_history.setItem(row_index, 4, battery_drain)
            self.table_history.setItem(row_index, 5, battery_regen)
            row_index += 1

        self.table_history.setHorizontalHeaderLabels((
            "Lap",
            "Time",
            f"Fuel({fuel_unit_text()})",
            "Energy(%)",
            "Drain(%)",
            "Regen(%)"
        ))

    def set_panel_calculator(self, panel):
        """Set panel calculator"""
        frame_laptime = QFrame()
        frame_laptime.setFrameShape(QFrame.StyledPanel)
        frame_laptime.setFixedWidth(PANEL_LEFT_WIDTH)

        frame_fuel = QFrame()
        frame_fuel.setFrameShape(QFrame.StyledPanel)
        frame_fuel.setFixedWidth(PANEL_LEFT_WIDTH)

        frame_race = QFrame()
        frame_race.setFrameShape(QFrame.StyledPanel)
        frame_race.setFixedWidth(PANEL_LEFT_WIDTH)

        frame_output_fuel = QFrame()
        frame_output_fuel.setFrameShape(QFrame.StyledPanel)

        frame_output_energy = QFrame()
        frame_output_energy.setFrameShape(QFrame.StyledPanel)

        frame_output_start_fuel = QFrame()
        frame_output_start_fuel.setFrameShape(QFrame.StyledPanel)

        frame_output_start_energy = QFrame()
        frame_output_start_energy.setFrameShape(QFrame.StyledPanel)

        self.input_laptime = InputLapTime(self, frame_laptime)
        self.input_fuel = InputFuel(self, frame_fuel)
        self.input_race = InputRace(self, frame_race)

        self.usage_fuel = OutputUsage(frame_output_fuel, "Fuel")
        self.usage_energy = OutputUsage(frame_output_energy, "Energy")
        self.refill_fuel = OutputRefill(self, frame_output_start_fuel, "Fuel")
        self.refill_energy = OutputRefill(self, frame_output_start_energy, "Energy")

        button_reload = QPushButton("Reload")
        button_reload.clicked.connect(self.reload_data)
        button_reload.setFocusPolicy(Qt.NoFocus)

        self.button_toggle = QPushButton("Hide history")
        self.button_toggle.clicked.connect(self.toggle_history_panel)
        self.button_toggle.setFocusPolicy(Qt.NoFocus)

        layout_split1 = QHBoxLayout()
        layout_split1.addWidget(frame_output_fuel)
        layout_split1.addWidget(frame_output_energy)

        layout_split2 = QHBoxLayout()
        layout_split2.addWidget(frame_output_start_fuel)
        layout_split2.addWidget(frame_output_start_energy)

        layout_calculator = QVBoxLayout()
        layout_calculator.setAlignment(Qt.AlignTop)
        layout_calculator.addWidget(frame_laptime)
        layout_calculator.addWidget(frame_fuel)
        layout_calculator.addWidget(frame_race)
        layout_calculator.addLayout(layout_split1)
        layout_calculator.addLayout(layout_split2)

        layout_button = QHBoxLayout()
        layout_button.addWidget(button_reload, stretch=1)
        layout_button.addStretch(stretch=1)
        layout_button.addWidget(self.button_toggle, stretch=1)

        layout_panel = QVBoxLayout()
        layout_panel.setContentsMargins(0,0,0,0)
        layout_panel.addLayout(layout_calculator)
        layout_panel.addLayout(layout_button)
        panel.setLayout(layout_panel)

    def set_panel_table(self, panel):
        """Set panel table"""
        self.table_history = QTableWidget(self)
        self.table_history.setColumnCount(6)
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setColumnWidth(0, 40)
        self.table_history.setFixedWidth(380)

        button_add = QPushButton("Add selected data")
        button_add.clicked.connect(self.add_selected_data)
        button_add.setFocusPolicy(Qt.NoFocus)

        layout_panel = QVBoxLayout()
        layout_panel.setContentsMargins(0,0,0,0)
        layout_panel.addWidget(self.table_history)
        layout_panel.addWidget(button_add)
        panel.setLayout(layout_panel)

    def update_input(self):
        """Calculate and output results"""
        self.input_laptime.carry_over()
        # Get lap time setup
        laptime = (
            self.input_laptime.minutes.value() * 60
            + self.input_laptime.seconds.value()
            + self.input_laptime.mseconds.value() * 0.001
        )
        # Get race setup
        total_race_seconds = self.input_race.minutes.value() * 60
        total_race_laps = self.input_race.laps.value()
        total_formation_laps = self.input_race.formation.value()
        average_pit_seconds = self.input_race.pit_seconds.value()

        # Get fuel setup
        tank_capacity = self.input_fuel.capacity.value()
        fuel_used = self.input_fuel.fuel_used.value()
        fuel_start = self.refill_fuel.amount_start.value(
            ) if self.refill_fuel.amount_start.value() else tank_capacity
        energy_used = self.input_fuel.energy_used.value()
        energy_start = self.refill_energy.amount_start.value(
            ) if self.refill_energy.amount_start.value() else 100

        # Calc fuel ratio
        if cfg.units["fuel_unit"] == "Gallon":
            fuel_ratio = calc.fuel_to_energy_ratio(fuel_used * 3.785411784, energy_used)
        else:
            fuel_ratio = calc.fuel_to_energy_ratio(fuel_used, energy_used)
        self.input_fuel.fuel_ratio.setText(f"{fuel_ratio:.3f}")

        # Calc fuel
        self.run_calculation(
            "fuel", tank_capacity, fuel_used, fuel_start, total_race_seconds,
            total_race_laps, total_formation_laps, average_pit_seconds, laptime)

        # Calc energy
        self.run_calculation(
            "energy", 100, energy_used, energy_start, total_race_seconds,
            total_race_laps, total_formation_laps, average_pit_seconds, laptime)

    def run_calculation(self, output_type, tank_capacity, consumption, fuel_start,
        total_race_seconds, total_race_laps, total_formation_laps, average_pit_seconds, laptime):
        """Calculate and output results"""
        estimate_pit_counts = 0
        minimum_pit_counts = 0  # minimum pit stop required to finish race
        loop_counts = 10  # max loop limit

        # Total pit seconds depends on estimated pit counts
        # Recalculate and find nearest minimum pit counts on previous loop
        while loop_counts:
            minimum_pit_counts = math.ceil(estimate_pit_counts)
            if total_race_seconds:  # time-type race
                total_pit_seconds = minimum_pit_counts * average_pit_seconds
                total_race_laps = total_formation_laps + calc.time_type_full_laps_remain(
                    0, laptime, total_race_seconds - total_pit_seconds)
            else:  # lap-type race
                total_race_laps = total_formation_laps + total_race_laps

            total_need_frac = calc.total_fuel_needed(total_race_laps, consumption, 0)

            # Keep 1 decimal place for Gallon
            if cfg.units["fuel_unit"] == "Gallon" and output_type == "fuel":
                total_need_full = math.ceil(total_need_frac * 10) / 10
            else:
                total_need_full = math.ceil(total_need_frac)

            amount_refuel = total_need_full - tank_capacity

            amount_curr = min(total_need_full, tank_capacity)

            end_stint_fuel = calc.end_stint_fuel(amount_curr, 0, consumption)

            estimate_pit_counts = calc.end_stint_pit_counts(
                amount_refuel, tank_capacity - end_stint_fuel)

            loop_counts -= 1
            # Set one last loop to revert back to last minimum pit counts
            # If new rounded up minimum pit counts is not enough to finish race
            if (minimum_pit_counts < estimate_pit_counts and
                minimum_pit_counts == math.floor(estimate_pit_counts)):
                loop_counts = 1

            if minimum_pit_counts == math.ceil(estimate_pit_counts):
                break

        total_runlaps = calc.end_stint_laps(total_need_full, consumption)

        total_runmins = calc.end_stint_minutes(total_runlaps, laptime)

        used_one_less = calc.one_less_pit_stop_consumption(
            estimate_pit_counts, tank_capacity, amount_curr, total_race_laps)

        if minimum_pit_counts:
            average_refuel = (
                total_need_full - fuel_start + minimum_pit_counts * end_stint_fuel
                ) / minimum_pit_counts
        elif fuel_start < total_need_full <= tank_capacity:
            average_refuel = total_need_full - fuel_start
        else:
            average_refuel = 0

        # Output
        if output_type == "fuel":
            output_usage = self.usage_fuel
            output_refill = self.refill_fuel
        else:
            output_usage = self.usage_energy
            output_refill = self.refill_energy

        output_usage.total_needed.setText(
            f"{total_need_frac:.3f} ≈ {total_need_full}")
        output_usage.end_stint.setText(
            f"{end_stint_fuel:.3f}")
        output_usage.pit_stops.setText(
            f"{max(estimate_pit_counts, 0):.3f} ≈ {max(math.ceil(minimum_pit_counts), 0)}")
        output_usage.one_less_stint.setText(
            f"{max(used_one_less, 0):.3f}")
        output_usage.total_laps.setText(
            f"{total_runlaps:.3f}")
        output_usage.total_minutes.setText(
            f"{total_runmins:.3f}")
        output_refill.average_refill.setText(
            f"{average_refuel:.3f}")
        # Set warning color if exceeded tank capacity
        set_read_only_style(
            output_refill.average_refill, average_refuel > tank_capacity)

    def validate_starting_fuel(self):
        """Validate starting fuel"""
        if self.refill_fuel.amount_start.value() > self.input_fuel.capacity.value():
            self.refill_fuel.amount_start.setValue(self.input_fuel.capacity.value())


class InputLapTime():
    """Input lap time setup"""

    def __init__(self, master, frame) -> None:
        """Set input lap time"""
        self.minutes = QSpinBox()
        self.minutes.setAlignment(Qt.AlignRight)
        self.minutes.setRange(0, 9999)
        self.minutes.valueChanged.connect(master.update_input)

        self.seconds = QSpinBox()
        self.seconds.setAlignment(Qt.AlignRight)
        self.seconds.setRange(-1, 60)
        self.seconds.valueChanged.connect(master.update_input)

        self.mseconds = QSpinBox()
        self.mseconds.setAlignment(Qt.AlignRight)
        self.mseconds.setRange(-1, 1000)
        self.mseconds.setSingleStep(100)
        self.mseconds.valueChanged.connect(master.update_input)

        layout_laptime = QGridLayout()
        layout_laptime.setColumnStretch(0, 1)
        layout_laptime.setColumnStretch(2, 1)
        layout_laptime.setColumnStretch(4, 1)

        layout_laptime.addWidget(QLabel("Lap Time:"), 0, 0, 1, 6)

        layout_laptime.addWidget(self.minutes, 1, 0)
        layout_laptime.addWidget(QLabel("m"), 1, 1)

        layout_laptime.addWidget(self.seconds, 1, 2)
        layout_laptime.addWidget(QLabel("s"), 1, 3)

        layout_laptime.addWidget(self.mseconds, 1, 4)
        layout_laptime.addWidget(QLabel("ms"), 1, 5)

        frame.setLayout(layout_laptime)

    def carry_over(self):
        """Carry over lap time value"""
        if self.seconds.value() > 59:
            self.seconds.setValue(0)
            self.minutes.setValue(self.minutes.value() + 1)
        elif self.seconds.value() < 0:
            if self.minutes.value() > 0:
                self.seconds.setValue(59)
                self.minutes.setValue(self.minutes.value() - 1)
            else:
                self.seconds.setValue(0)

        if self.mseconds.value() > 999:
            self.mseconds.setValue(0)
            self.seconds.setValue(self.seconds.value() + 1)
        elif self.mseconds.value() < 0:
            if self.seconds.value() > 0 or self.minutes.value() > 0:
                self.mseconds.setValue(900)
                self.seconds.setValue(self.seconds.value() - 1)
            else:
                self.mseconds.setValue(0)


class InputFuel():
    """Input fuel setup"""

    def __init__(self, master, frame) -> None:
        """Set input fuel"""
        self.capacity = QDoubleSpinBox()
        self.capacity.setRange(0, 9999)
        self.capacity.setDecimals(2)
        self.capacity.setAlignment(Qt.AlignRight)
        self.capacity.valueChanged.connect(master.update_input)

        self.fuel_ratio = QLineEdit("0.000")
        self.fuel_ratio.setAlignment(Qt.AlignRight)
        self.fuel_ratio.setReadOnly(True)
        set_read_only_style(self.fuel_ratio)

        self.fuel_used = QDoubleSpinBox()
        self.fuel_used.setRange(0, 9999)
        self.fuel_used.setDecimals(3)
        self.fuel_used.setSingleStep(0.1)
        self.fuel_used.setAlignment(Qt.AlignRight)
        self.fuel_used.valueChanged.connect(master.update_input)

        self.energy_used = QDoubleSpinBox()
        self.energy_used.setRange(0, 100)
        self.energy_used.setDecimals(3)
        self.energy_used.setSingleStep(0.1)
        self.energy_used.setAlignment(Qt.AlignRight)
        self.energy_used.valueChanged.connect(master.update_input)

        layout_grid = QGridLayout()
        layout_grid.setColumnStretch(0, 1)
        layout_grid.setColumnStretch(2, 1)

        layout_grid.addWidget(QLabel("Tank Capacity:"), 0, 0, 1, 2)
        layout_grid.addWidget(self.capacity, 1, 0)
        layout_grid.addWidget(QLabel(fuel_unit_text()), 1, 1)

        layout_grid.addWidget(QLabel("Fuel Ratio:"), 2, 0, 1, 2)
        layout_grid.addWidget(self.fuel_ratio, 3, 0)

        layout_grid.addWidget(QLabel("Fuel Consumption:"), 0, 2, 1, 2)
        layout_grid.addWidget(self.fuel_used, 1, 2)
        layout_grid.addWidget(QLabel(fuel_unit_text()), 1, 3)

        layout_grid.addWidget(QLabel("Energy Consumption:"), 2, 2, 1, 2)
        layout_grid.addWidget(self.energy_used, 3, 2)
        layout_grid.addWidget(QLabel("%"), 3, 3)

        frame.setLayout(layout_grid)


class InputRace():
    """Input race setup"""

    def __init__(self, master, frame) -> None:
        """Set input race"""
        self.minutes = QSpinBox()
        self.minutes.setRange(0, 9999)
        self.minutes.setAlignment(Qt.AlignRight)
        self.minutes.valueChanged.connect(master.update_input)
        self.minutes.valueChanged.connect(self.disable_race_lap)

        self.laps = QSpinBox()
        self.laps.setRange(0, 9999)
        self.laps.setAlignment(Qt.AlignRight)
        self.laps.valueChanged.connect(master.update_input)
        self.laps.valueChanged.connect(self.disable_race_minute)

        self.formation = QDoubleSpinBox()
        self.formation.setRange(0, 9999)
        self.formation.setDecimals(2)
        self.formation.setSingleStep(0.1)
        self.formation.setAlignment(Qt.AlignRight)
        self.formation.valueChanged.connect(master.update_input)

        self.pit_seconds = QDoubleSpinBox()
        self.pit_seconds.setRange(0, 9999)
        self.pit_seconds.setDecimals(1)
        self.pit_seconds.setAlignment(Qt.AlignRight)
        self.pit_seconds.valueChanged.connect(master.update_input)

        layout_grid = QGridLayout()
        layout_grid.setColumnStretch(0, 1)
        layout_grid.setColumnStretch(2, 1)

        layout_grid.addWidget(QLabel("Race Minutes:"), 0, 0, 1, 2)
        layout_grid.addWidget(self.minutes, 1, 0)
        layout_grid.addWidget(QLabel("min"), 1, 1)

        layout_grid.addWidget(QLabel("Race Laps:"), 0, 2, 1, 2)
        layout_grid.addWidget(self.laps, 1, 2)
        layout_grid.addWidget(QLabel("lap"), 1, 3)

        layout_grid.addWidget(QLabel("Formation/Rolling:"), 2, 0, 1, 2)
        layout_grid.addWidget(self.formation, 3, 0)
        layout_grid.addWidget(QLabel("lap"), 3, 1)

        layout_grid.addWidget(QLabel("Average Pit Seconds:"), 2, 2, 1, 2)
        layout_grid.addWidget(self.pit_seconds, 3, 2)
        layout_grid.addWidget(QLabel("sec"), 3, 3)

        frame.setLayout(layout_grid)

    def disable_race_lap(self):
        """Disable race laps if race minutes is set"""
        if self.minutes.value() > 0:
            if self.laps.isEnabled():
                self.laps.setValue(0)
                self.laps.setDisabled(True)
        else:
            self.laps.setDisabled(False)

    def disable_race_minute(self):
        """Disable race minutes if race laps is set"""
        if self.laps.value() > 0:
            if self.minutes.isEnabled():
                self.minutes.setValue(0)
                self.minutes.setDisabled(True)
        else:
            self.minutes.setDisabled(False)


class OutputUsage():
    """Output usage display"""

    def __init__(self, frame, type_name) -> None:
        """Set output display"""
        if type_name == "Fuel":
            unit_text = fuel_unit_text()
        else:
            unit_text = "%"

        self.total_needed = QLineEdit("0.000 ≈ 0")
        self.total_needed.setAlignment(Qt.AlignRight)
        self.total_needed.setReadOnly(True)
        set_read_only_style(self.total_needed)

        self.pit_stops = QLineEdit("0.000 ≈ 0")
        self.pit_stops.setAlignment(Qt.AlignRight)
        self.pit_stops.setReadOnly(True)
        set_read_only_style(self.pit_stops)

        self.total_laps = QLineEdit("0.000")
        self.total_laps.setAlignment(Qt.AlignRight)
        self.total_laps.setReadOnly(True)
        set_read_only_style(self.total_laps)

        self.total_minutes = QLineEdit("0.000")
        self.total_minutes.setAlignment(Qt.AlignRight)
        self.total_minutes.setReadOnly(True)
        set_read_only_style(self.total_minutes)

        self.end_stint = QLineEdit("0.000")
        self.end_stint.setAlignment(Qt.AlignRight)
        self.end_stint.setReadOnly(True)
        set_read_only_style(self.end_stint)

        self.one_less_stint = QLineEdit("0.000")
        self.one_less_stint.setAlignment(Qt.AlignRight)
        self.one_less_stint.setReadOnly(True)
        set_read_only_style(self.one_less_stint)

        layout_output = QGridLayout()

        layout_output.addWidget(QLabel(f"Total Race {type_name}:"), 0, 0, 1, 2)
        layout_output.addWidget(self.total_needed, 1, 0)
        layout_output.addWidget(QLabel(unit_text), 1, 1)

        layout_output.addWidget(QLabel("Total Pit Stops:"), 2, 0, 1, 2)
        layout_output.addWidget(self.pit_stops, 3, 0)
        layout_output.addWidget(QLabel("pit"), 3, 1)

        layout_output.addWidget(QLabel("Total Laps:"), 4, 0, 1, 2)
        layout_output.addWidget(self.total_laps, 5, 0)
        layout_output.addWidget(QLabel("lap"), 5, 1)

        layout_output.addWidget(QLabel("Total Minutes:"), 6, 0, 1, 2)
        layout_output.addWidget(self.total_minutes, 7, 0)
        layout_output.addWidget(QLabel("min"), 7, 1)

        layout_output.addWidget(QLabel(f"End Stint {type_name}:"), 8, 0, 1, 2)
        layout_output.addWidget(self.end_stint, 9, 0)
        layout_output.addWidget(QLabel(unit_text), 9, 1)

        layout_output.addWidget(QLabel("One Less Pit Stop:"), 10, 0, 1, 2)
        layout_output.addWidget(self.one_less_stint, 11, 0)
        layout_output.addWidget(QLabel(unit_text), 11, 1)

        frame.setLayout(layout_output)


class OutputRefill():
    """Output refill display"""

    def __init__(self, master, frame, type_name) -> None:
        """Set output display"""
        self.amount_start = QDoubleSpinBox()
        self.amount_start.setDecimals(2)
        self.amount_start.setAlignment(Qt.AlignRight)

        if type_name == "Fuel":
            start_range = 9999
            unit_text = fuel_unit_text()
            self.amount_start.valueChanged.connect(master.validate_starting_fuel)
        else:
            start_range = 100
            unit_text = "%"
        self.amount_start.setRange(0, start_range)
        self.amount_start.valueChanged.connect(master.update_input)

        self.average_refill = QLineEdit("0.000")
        self.average_refill.setAlignment(Qt.AlignRight)
        self.average_refill.setReadOnly(True)
        set_read_only_style(self.average_refill)

        layout_output = QGridLayout()

        layout_output.addWidget(QLabel(f"Starting {type_name}:"), 0, 0, 1, 2)
        layout_output.addWidget(self.amount_start, 1, 0)
        layout_output.addWidget(QLabel(unit_text), 1, 1)

        layout_output.addWidget(QLabel("Average Refilling:"), 2, 0, 1, 2)
        layout_output.addWidget(self.average_refill, 3, 0)
        layout_output.addWidget(QLabel(unit_text), 3, 1)

        frame.setLayout(layout_output)
