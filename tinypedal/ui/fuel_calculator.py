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
from PySide2.QtGui import QIcon, QBrush, QColor
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

PANEL_LEFT_WIDTH = 300


class FuelCalculator(QDialog):
    """Fuel calculator"""

    def __init__(self, master):
        super().__init__(master)
        # Base setting
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setWindowIcon(QIcon(APP_ICON))
        self.setWindowTitle("Fuel Calculator")
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.read_only_color = self.palette().window().color().name(QColor.HexRgb)
        self.history_data = minfo.fuel.consumptionHistory

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
        if not self.panel_table.isVisible():
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
        # Check index of selected column
        column_indices = set(data.column() for data in selected_data)
        if len(column_indices) > 1:
            QMessageBox.warning(
                self, "Error",
                "Cannot add data from different columns.\n\nPlease select data from same column.")
            return None
        if len(column_indices) < 1:
            QMessageBox.warning(
                self, "Error",
                "No data selected.")
            return None
        # Send data to calculator
        column_index = list(column_indices)[0]
        if column_index == 1:  # laptime
            dataset = [fmt.laptime_string_to_seconds(data.text()) for data in selected_data]
            output_value = calc.mean(dataset) if len(selected_data) > 1 else dataset[0]
            self.spinbox_minutes.setValue(output_value // 60)
            self.spinbox_seconds.setValue(output_value % 60)
            self.spinbox_mseconds.setValue(output_value % 1 * 1000)
        elif column_index == 2:  # used fuel
            dataset = [float(data.text()) for data in selected_data]
            output_value = calc.mean(dataset) if len(selected_data) > 1 else dataset[0]
            self.spinbox_consumption.setValue(output_value)
        return None

    def reload_data(self):
        """Reload history data"""
        self.refresh_table()
        # Load laptime if exists
        laptime = self.history_data[0][1]
        if laptime > 0 and self.history_data[0][5]:
            self.spinbox_minutes.setValue(laptime // 60)
            self.spinbox_seconds.setValue(laptime % 60)
            self.spinbox_mseconds.setValue(laptime % 1 * 1000)
        # Load tank capacity
        capacity = max(api.read.vehicle.tank_capacity(), self.history_data[0][4])
        if capacity:
            self.spinbox_capacity.setValue(self.fuel_units(capacity))
        # Load consumption
        consumption = self.history_data[0][2]
        if consumption:
            self.spinbox_consumption.setValue(self.fuel_units(consumption))

    def refresh_table(self):
        """Refresh history data table"""
        self.history_data = minfo.fuel.consumptionHistory
        self.table_history.clear()
        self.table_history.setRowCount(len(self.history_data))
        row_index = 0

        for lap in self.history_data:
            lapnumber = QTableWidgetItem()
            lapnumber.setText(f"{lap[0]}")
            lapnumber.setTextAlignment(Qt.AlignCenter)
            lapnumber.setFlags(Qt.ItemFlags(0))

            laptime = QTableWidgetItem()
            laptime.setText(calc.sec2laptime(lap[1]))
            laptime.setTextAlignment(Qt.AlignCenter)
            laptime.setFlags(Qt.ItemFlags(33))

            consumption = QTableWidgetItem()
            consumption.setText(f"{self.fuel_units(lap[2]):.03f}")
            consumption.setTextAlignment(Qt.AlignCenter)
            consumption.setFlags(Qt.ItemFlags(33))

            fuel_in_tank = QTableWidgetItem()
            fuel_in_tank.setText(f"{self.fuel_units(lap[3]):.03f}")
            fuel_in_tank.setTextAlignment(Qt.AlignCenter)
            fuel_in_tank.setFlags(Qt.ItemFlags(0))

            if not lap[5]:  # set invalid lap text color
                laptime.setForeground(QBrush("#C40", Qt.SolidPattern))
                consumption.setForeground(QBrush("#C40", Qt.SolidPattern))

            self.table_history.setItem(row_index, 0, lapnumber)
            self.table_history.setItem(row_index, 1, laptime)
            self.table_history.setItem(row_index, 2, consumption)
            self.table_history.setItem(row_index, 3, fuel_in_tank)
            row_index += 1

        self.table_history.setHorizontalHeaderLabels((
            "Lap",
            "Time",
            f"Used({self.fuel_unit_text()})",
            f"Remain({self.fuel_unit_text()})"
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

        frame_output1 = QFrame()
        frame_output1.setFrameShape(QFrame.StyledPanel)
        frame_output1.setFixedWidth(PANEL_LEFT_WIDTH)

        frame_output2 = QFrame()
        frame_output2.setFrameShape(QFrame.StyledPanel)
        frame_output2.setFixedWidth(PANEL_LEFT_WIDTH)

        self.set_input_laptime(frame_laptime)
        self.set_input_fuel(frame_fuel)
        self.set_input_race(frame_race)
        self.set_output1(frame_output1)
        self.set_output2(frame_output2)

        button_reload = QPushButton("Reload")
        button_reload.clicked.connect(self.reload_data)
        button_reload.setFocusPolicy(Qt.NoFocus)

        self.button_toggle = QPushButton("Hide history")
        self.button_toggle.clicked.connect(self.toggle_history_panel)
        self.button_toggle.setFocusPolicy(Qt.NoFocus)

        layout_calculator = QVBoxLayout()
        layout_calculator.setAlignment(Qt.AlignTop)
        layout_calculator.addWidget(frame_laptime)
        layout_calculator.addWidget(frame_fuel)
        layout_calculator.addWidget(frame_race)
        layout_calculator.addWidget(frame_output1)
        layout_calculator.addWidget(frame_output2)

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
        self.table_history.setColumnCount(4)
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_history.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setColumnWidth(0, 40)
        self.table_history.setFixedWidth(self.table_history.sizeHint().width())

        button_add = QPushButton("Add selected data")
        button_add.clicked.connect(self.add_selected_data)
        button_add.setFocusPolicy(Qt.NoFocus)

        layout_panel = QVBoxLayout()
        layout_panel.setContentsMargins(0,0,0,0)
        layout_panel.addWidget(self.table_history)
        layout_panel.addWidget(button_add)
        panel.setLayout(layout_panel)

    def carry_over_laptime(self):
        """Carry over lap time value"""
        if self.spinbox_seconds.value() > 59:
            self.spinbox_seconds.setValue(0)
            self.spinbox_minutes.setValue(self.spinbox_minutes.value() + 1)
        elif self.spinbox_seconds.value() < 0:
            if self.spinbox_minutes.value() > 0:
                self.spinbox_seconds.setValue(59)
                self.spinbox_minutes.setValue(self.spinbox_minutes.value() - 1)
            else:
                self.spinbox_seconds.setValue(0)

        if self.spinbox_mseconds.value() > 999:
            self.spinbox_mseconds.setValue(0)
            self.spinbox_seconds.setValue(self.spinbox_seconds.value() + 1)
        elif self.spinbox_mseconds.value() < 0:
            if self.spinbox_seconds.value() > 0 or self.spinbox_minutes.value() > 0:
                self.spinbox_mseconds.setValue(900)
                self.spinbox_seconds.setValue(self.spinbox_seconds.value() - 1)
            else:
                self.spinbox_mseconds.setValue(0)

    def set_input_laptime(self, frame):
        """Set input laptime"""
        self.spinbox_minutes = QSpinBox()
        self.spinbox_minutes.setAlignment(Qt.AlignRight)
        self.spinbox_minutes.setRange(0, 9999)
        self.spinbox_minutes.valueChanged.connect(self.output_results)

        self.spinbox_seconds = QSpinBox()
        self.spinbox_seconds.setAlignment(Qt.AlignRight)
        self.spinbox_seconds.setRange(-1, 60)
        self.spinbox_seconds.valueChanged.connect(self.output_results)

        self.spinbox_mseconds = QSpinBox()
        self.spinbox_mseconds.setAlignment(Qt.AlignRight)
        self.spinbox_mseconds.setRange(-1, 1000)
        self.spinbox_mseconds.setSingleStep(100)
        self.spinbox_mseconds.valueChanged.connect(self.output_results)

        layout_laptime = QGridLayout()
        layout_laptime.setColumnStretch(0, 1)
        layout_laptime.setColumnStretch(2, 1)
        layout_laptime.setColumnStretch(4, 1)

        layout_laptime.addWidget(QLabel("Lap Time:"), 0, 0, 1, 6)

        layout_laptime.addWidget(self.spinbox_minutes, 1, 0)
        layout_laptime.addWidget(QLabel("m"), 1, 1)

        layout_laptime.addWidget(self.spinbox_seconds, 1, 2)
        layout_laptime.addWidget(QLabel("s"), 1, 3)

        layout_laptime.addWidget(self.spinbox_mseconds, 1, 4)
        layout_laptime.addWidget(QLabel("ms"), 1, 5)

        frame.setLayout(layout_laptime)

    def set_input_fuel(self, frame):
        """Set input fuel"""
        self.spinbox_capacity = QDoubleSpinBox()
        self.spinbox_capacity.setRange(0, 9999)
        self.spinbox_capacity.setDecimals(2)
        self.spinbox_capacity.setAlignment(Qt.AlignRight)
        self.spinbox_capacity.valueChanged.connect(self.output_results)

        self.spinbox_consumption = QDoubleSpinBox()
        self.spinbox_consumption.setRange(0, 9999)
        self.spinbox_consumption.setDecimals(3)
        self.spinbox_consumption.setSingleStep(0.1)
        self.spinbox_consumption.setAlignment(Qt.AlignRight)
        self.spinbox_consumption.valueChanged.connect(self.output_results)

        layout_grid = QGridLayout()
        layout_grid.setColumnStretch(0, 1)
        layout_grid.setColumnStretch(2, 1)

        layout_grid.addWidget(QLabel("Tank Capacity:"), 0, 0, 1, 2)
        layout_grid.addWidget(self.spinbox_capacity, 1, 0)
        layout_grid.addWidget(QLabel(self.fuel_unit_text()), 1, 1)

        layout_grid.addWidget(QLabel("Fuel Consumption:"), 0, 2, 1, 2)
        layout_grid.addWidget(self.spinbox_consumption, 1, 2)
        layout_grid.addWidget(QLabel(self.fuel_unit_text()), 1, 3)

        frame.setLayout(layout_grid)

    def set_input_race(self, frame):
        """Set input race"""
        self.spinbox_race_minutes = QSpinBox()
        self.spinbox_race_minutes.setRange(0, 9999)
        self.spinbox_race_minutes.setAlignment(Qt.AlignRight)
        self.spinbox_race_minutes.valueChanged.connect(self.output_results)
        self.spinbox_race_minutes.valueChanged.connect(self.disable_race_lap)

        self.spinbox_race_laps = QSpinBox()
        self.spinbox_race_laps.setRange(0, 9999)
        self.spinbox_race_laps.setAlignment(Qt.AlignRight)
        self.spinbox_race_laps.valueChanged.connect(self.output_results)
        self.spinbox_race_laps.valueChanged.connect(self.disable_race_minute)

        self.spinbox_formation = QDoubleSpinBox()
        self.spinbox_formation.setRange(0, 9999)
        self.spinbox_formation.setDecimals(2)
        self.spinbox_formation.setSingleStep(0.1)
        self.spinbox_formation.setAlignment(Qt.AlignRight)
        self.spinbox_formation.valueChanged.connect(self.output_results)

        self.spinbox_pit_seconds = QDoubleSpinBox()
        self.spinbox_pit_seconds.setRange(0, 9999)
        self.spinbox_pit_seconds.setDecimals(1)
        self.spinbox_pit_seconds.setAlignment(Qt.AlignRight)
        self.spinbox_pit_seconds.valueChanged.connect(self.output_results)

        layout_grid = QGridLayout()
        layout_grid.setColumnStretch(0, 1)
        layout_grid.setColumnStretch(2, 1)

        layout_grid.addWidget(QLabel("Race Minutes:"), 0, 0, 1, 2)
        layout_grid.addWidget(self.spinbox_race_minutes, 1, 0)
        layout_grid.addWidget(QLabel("min"), 1, 1)

        layout_grid.addWidget(QLabel("Race Laps:"), 0, 2, 1, 2)
        layout_grid.addWidget(self.spinbox_race_laps, 1, 2)
        layout_grid.addWidget(QLabel("lap"), 1, 3)

        layout_grid.addWidget(QLabel("Formation/Rolling:"), 2, 0, 1, 2)
        layout_grid.addWidget(self.spinbox_formation, 3, 0)
        layout_grid.addWidget(QLabel("lap"), 3, 1)

        layout_grid.addWidget(QLabel("Average Pit Seconds:"), 2, 2, 1, 2)
        layout_grid.addWidget(self.spinbox_pit_seconds, 3, 2)
        layout_grid.addWidget(QLabel("sec"), 3, 3)

        frame.setLayout(layout_grid)

    def set_output1(self, frame):
        """Set output display"""
        self.lineedit_total_fuel = QLineEdit("0.000 ≈ 0")
        self.lineedit_total_fuel.setAlignment(Qt.AlignRight)
        self.lineedit_total_fuel.setReadOnly(True)
        self.set_read_only_style(self.lineedit_total_fuel)

        self.lineedit_end_fuel = QLineEdit("0.000")
        self.lineedit_end_fuel.setAlignment(Qt.AlignRight)
        self.lineedit_end_fuel.setReadOnly(True)
        self.set_read_only_style(self.lineedit_end_fuel)

        self.lineedit_pit_stops = QLineEdit("0.000 ≈ 0")
        self.lineedit_pit_stops.setAlignment(Qt.AlignRight)
        self.lineedit_pit_stops.setReadOnly(True)
        self.set_read_only_style(self.lineedit_pit_stops)

        self.lineedit_one_less = QLineEdit("0.000")
        self.lineedit_one_less.setAlignment(Qt.AlignRight)
        self.lineedit_one_less.setReadOnly(True)
        self.set_read_only_style(self.lineedit_one_less)

        self.lineedit_total_laps = QLineEdit("0.000")
        self.lineedit_total_laps.setAlignment(Qt.AlignRight)
        self.lineedit_total_laps.setReadOnly(True)
        self.set_read_only_style(self.lineedit_total_laps)

        self.lineedit_total_minutes = QLineEdit("0.000")
        self.lineedit_total_minutes.setAlignment(Qt.AlignRight)
        self.lineedit_total_minutes.setReadOnly(True)
        self.set_read_only_style(self.lineedit_total_minutes)

        layout_output = QGridLayout()
        layout_output.setColumnStretch(0, 1)
        layout_output.setColumnStretch(2, 1)

        layout_output.addWidget(QLabel("Total Race Fuel:"), 5, 0, 1, 2)
        layout_output.addWidget(self.lineedit_total_fuel, 6, 0)
        layout_output.addWidget(QLabel(self.fuel_unit_text()), 6, 1)

        layout_output.addWidget(QLabel("End Stint Fuel:"), 5, 2, 1, 2)
        layout_output.addWidget(self.lineedit_end_fuel, 6, 2)
        layout_output.addWidget(QLabel(self.fuel_unit_text()), 6, 3)

        layout_output.addWidget(QLabel("Total Pit Stops:"), 7, 0, 1, 2)
        layout_output.addWidget(self.lineedit_pit_stops, 8, 0)
        layout_output.addWidget(QLabel("pit"), 8, 1)

        layout_output.addWidget(QLabel("One Less Pit Stop:"), 7, 2, 1, 2)
        layout_output.addWidget(self.lineedit_one_less, 8, 2)
        layout_output.addWidget(QLabel(self.fuel_unit_text()), 8, 3)

        layout_output.addWidget(QLabel("Total Laps:"), 9, 0, 1, 2)
        layout_output.addWidget(self.lineedit_total_laps, 10, 0)
        layout_output.addWidget(QLabel("lap"), 10, 1)

        layout_output.addWidget(QLabel("Total Minutes:"), 9, 2, 1, 2)
        layout_output.addWidget(self.lineedit_total_minutes, 10, 2)
        layout_output.addWidget(QLabel("min"), 10, 3)

        frame.setLayout(layout_output)

    def set_output2(self, frame):
        """Set output display"""
        self.spinbox_start_fuel = QDoubleSpinBox()
        self.spinbox_start_fuel.setRange(0, 9999)
        self.spinbox_start_fuel.setDecimals(2)
        self.spinbox_start_fuel.setAlignment(Qt.AlignRight)
        self.spinbox_start_fuel.valueChanged.connect(self.validate_starting_fuel)
        self.spinbox_start_fuel.valueChanged.connect(self.output_results)

        self.lineedit_average_refuel = QLineEdit("0.000")
        self.lineedit_average_refuel.setAlignment(Qt.AlignRight)
        self.lineedit_average_refuel.setReadOnly(True)
        self.set_read_only_style(self.lineedit_average_refuel)

        layout_output = QGridLayout()
        layout_output.setColumnStretch(0, 1)
        layout_output.setColumnStretch(2, 1)

        layout_output.addWidget(QLabel("Starting Fuel:"), 0, 0, 1, 2)
        layout_output.addWidget(self.spinbox_start_fuel, 1, 0)
        layout_output.addWidget(QLabel(self.fuel_unit_text()), 1, 1)

        layout_output.addWidget(QLabel("Average Refueling:"), 0, 2, 1, 2)
        layout_output.addWidget(self.lineedit_average_refuel, 1, 2)
        layout_output.addWidget(QLabel(self.fuel_unit_text()), 1, 3)

        frame.setLayout(layout_output)

    def output_results(self):
        """Calculate and output results"""
        self.carry_over_laptime()
        tank_capacity = self.spinbox_capacity.value()
        consumption = self.spinbox_consumption.value()
        fuel_start = self.spinbox_start_fuel.value() if self.spinbox_start_fuel.value() else tank_capacity
        total_race_seconds = self.spinbox_race_minutes.value() * 60
        total_race_laps = self.spinbox_race_laps.value()
        total_formation_laps = self.spinbox_formation.value()
        average_pit_seconds = self.spinbox_pit_seconds.value()
        laptime = (
            self.spinbox_minutes.value() * 60
            + self.spinbox_seconds.value()
            + self.spinbox_mseconds.value() * 0.001
        )
        # Skip if required values not filled
        if not all((laptime, tank_capacity, consumption, total_race_seconds + total_race_laps)):
            return None

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
            average_refuel = (total_need_full - fuel_start + minimum_pit_counts * end_stint_fuel) / minimum_pit_counts
        elif fuel_start < total_need_full <= tank_capacity:
            average_refuel = total_need_full - fuel_start
        else:
            average_refuel = 0
        # Output
        self.lineedit_total_fuel.setText(
            f"{total_need_frac:.03f} ≈ {total_need_full}")
        self.lineedit_end_fuel.setText(
            f"{end_stint_fuel:.03f}")
        self.lineedit_pit_stops.setText(
            f"{max(estimate_pit_counts, 0):.03f} ≈ {max(math.ceil(minimum_pit_counts), 0)}")
        self.lineedit_one_less.setText(
            f"{max(used_one_less, 0):.03f}")
        self.lineedit_total_laps.setText(
            f"{total_runlaps:.03f}")
        self.lineedit_total_minutes.setText(
            f"{total_runmins:.03f}")
        self.lineedit_average_refuel.setText(
            f"{average_refuel:.03f}")
        # Set warning color
        if average_refuel > tank_capacity:  # exceeded tank capacity
            self.lineedit_average_refuel.setStyleSheet("background: #F40;")
        else:
            self.set_read_only_style(self.lineedit_average_refuel)
        return None

    def disable_race_lap(self):
        """Disable race laps if race minutes is set"""
        if self.spinbox_race_minutes.value() > 0:
            if self.spinbox_race_laps.isEnabled():
                self.spinbox_race_laps.setValue(0)
                self.spinbox_race_laps.setDisabled(True)
        else:
            self.spinbox_race_laps.setDisabled(False)

    def disable_race_minute(self):
        """Disable race minutes if race laps is set"""
        if self.spinbox_race_laps.value() > 0:
            if self.spinbox_race_minutes.isEnabled():
                self.spinbox_race_minutes.setValue(0)
                self.spinbox_race_minutes.setDisabled(True)
        else:
            self.spinbox_race_minutes.setDisabled(False)

    @staticmethod
    def fuel_unit_text():
        """Set fuel unit text"""
        if cfg.units["fuel_unit"] == "Gallon":
            return "gal"
        return "L"

    def fuel_units(self, fuel):
        """2 different fuel unit conversion, default is Liter"""
        if cfg.units["fuel_unit"] == "Gallon":
            return calc.liter2gallon(fuel)
        return fuel

    def validate_starting_fuel(self):
        """Validate starting fuel"""
        if self.spinbox_start_fuel.value() > self.spinbox_capacity.value():
            self.spinbox_start_fuel.setValue(self.spinbox_capacity.value())

    def set_read_only_style(self, line_edit):
        """Set read only style"""
        line_edit.setStyleSheet(f"background: {self.read_only_color};")
