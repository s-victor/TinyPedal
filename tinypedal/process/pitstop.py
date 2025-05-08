#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2025 TinyPedal developers, see contributors.md file
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
Pit stop function
"""

from __future__ import annotations

from ..const_common import EMPTY_DICT, PITEST_DEFAULT
from ..regex_pattern import rex_number_split


def estimate_pit_stop_time(dataset: dict):
    """Estimate pit stop time"""
    try:
        # Get data
        pit_menu = dataset.get("pitMenu", EMPTY_DICT).get("pitMenu", None)
        ref_time = dataset.get("pitStopTimes", EMPTY_DICT).get("times", None)
        fuel_info = dataset.get("fuelInfo", EMPTY_DICT)
        stopgo_time = dataset.get("pitStopLength", EMPTY_DICT).get("timeInSeconds", 10.0)
        if not isinstance(pit_menu, list) or not isinstance(ref_time, dict):
            return PITEST_DEFAULT
        # Setup parser
        total_concurrent = 0.0
        total_separate = 0.0
        total_concurrent_delay = 0.0
        total_separate_delay = 0.0
        rel_refill = [0.0, 0.0]
        gen_pit_time = parse_pit_time(fuel_info, pit_menu, ref_time, stopgo_time, rel_refill)
        # Parse data & calculate pit time
        for service_time, random_delay, is_concurrent in gen_pit_time:
            service_time_delay = service_time + random_delay
            # Set longest concurrent service time
            if is_concurrent:
                if total_concurrent < service_time:
                    total_concurrent = service_time
                if total_concurrent_delay < service_time_delay:
                    total_concurrent_delay = service_time_delay
            # Add up non-concurrent service time
            else:
                total_separate += service_time
                total_separate_delay += service_time_delay
        pit_stop_time = total_concurrent + total_separate
        pit_stop_time_delay = total_concurrent_delay + total_separate_delay
        return pit_stop_time, pit_stop_time_delay, rel_refill[0], rel_refill[1]
    except (AttributeError, TypeError, IndexError, KeyError, ValueError):
        return PITEST_DEFAULT


def parse_pit_time(
    fuel_info: dict, pit_menu: list, ref_time: dict, stopgo_time: float, rel_refill: list
):
    """Parse & analyse pit time data"""
    tyre_count = 0
    adjust_pressure = 0
    nrg_abs_refill = 0
    fuel_abs_refill = 0
    nrg_current = fuel_info.get("currentVirtualEnergy", 0.0)
    nrg_max = fuel_info.get("maxVirtualEnergy", 0.0)
    nrg_remaining = nrg_current / nrg_max * 100 if nrg_max else 0.0
    fuel_remaining = fuel_info.get("currentFuel", 0.0)
    for data in pit_menu:
        var_name = data.get("name", "n/a")
        var_current = data.get("currentSetting", 0)
        var_default = data.get("default", 0)
        if var_name == "STOP/GO:":
            stop_go = set_time_stopgo(var_current, stopgo_time)
            yield stop_go
            if var_current > 0:  # serve stop go penalty
                return
        if var_name == "DAMAGE:":
            yield set_time_damage(ref_time, var_current)
            continue
        if var_name == "DRIVER:":
            yield set_time_driver(ref_time, var_current, var_default)
            continue
        if var_name == "VIRTUAL ENERGY:":
            nrg_abs_refill = var_current
            rel_refill[1] = nrg_abs_refill - nrg_remaining
            yield set_time_virtual_energy(ref_time, nrg_abs_refill, nrg_remaining)
            continue
        if var_name == "FUEL RATIO:":
            fuel_ratio = get_fuel_ratio(var_current, data.get("settings", None))
            yield set_time_fuel(ref_time, nrg_abs_refill * fuel_ratio, fuel_remaining)
            continue
        if var_name == "FUEL:":
            fuel_abs_refill = get_absolute_refuel(var_current, data.get("settings", None))
            rel_refill[0] = fuel_abs_refill - fuel_remaining
            yield set_time_fuel(ref_time, fuel_abs_refill, fuel_remaining)
            continue
        if var_name in "FL TIRE:|FR TIRE:|RL TIRE:|RR TIRE:":
            tyre_count += (var_current != var_default)
            continue
        if var_name in "FL PRESS:|FR PRESS:|RL PRESS:|RR PRESS:":
            adjust_pressure += (var_current != var_default)
            continue
        if var_name == "F WING:":
            yield set_time_front_wing(ref_time, var_current, var_default)
            continue
        if var_name == "R WING:":
            yield set_time_rear_wing(ref_time, var_current, var_default)
            continue
        if var_name == "GRILLE:":
            yield set_time_radiator(ref_time, var_current, var_default)
            continue
        if var_name == "REPLACE BRAKES:":
            yield set_time_brake(ref_time, var_current)
            continue
    yield set_time_tyre(ref_time, tyre_count, adjust_pressure)


# Set pit time in order:
# service time (seconds), random delay (seconds), whether concurrent (0=no, 1=yes)
def set_time_stopgo(current: int, stopgo_time: float):
    """Set time - stop go penalty"""
    if current > 0:
        seconds = stopgo_time
    else:
        seconds = 0.0
    return seconds, 0.0, 0


def set_time_damage(ref_time: dict, current: int):
    """Set time - damage fix"""
    delay = ref_time.get("FixRandomDelay", 0)
    concurrent = ref_time.get("FixTimeConcurrent", 0)
    if current == 1:
        seconds = ref_time.get("FixAeroDamage", 0)
    elif current == 2:
        seconds = ref_time.get("FixAllDamage", 0)
    else:
        delay = seconds = 0.0
    return seconds, delay, concurrent


def set_time_driver(ref_time: dict, current: int, default: int):
    """Set time - driver swap"""
    delay = ref_time.get("DriverRandom", 0)
    concurrent = ref_time.get("DriverConcurrent", 0)
    if current != default:
        seconds = ref_time.get("DriverChange", 0)
    else:
        delay = seconds = 0.0
    return seconds, delay, concurrent


def set_time_virtual_energy(ref_time: dict, current: int, remaining: float):
    """Set time - virtual energy (percentage)"""
    delay = ref_time.get("virtualEnergyRandomDelay", 0)
    concurrent = ref_time.get("virtualEnergyTimeConcurrent", 0)
    seconds = ref_time.get("virtualEnergyInsert", 0)
    seconds += ref_time.get("virtualEnergyRemove", 0)
    fill_rate = ref_time.get("virtualEnergyFillRate", 0) * 100
    refill = current - remaining
    if refill > 0 < fill_rate:
        seconds += refill / fill_rate
    else:
        delay = seconds = 0.0
    return seconds, delay, concurrent


def set_time_tyre(ref_time: dict, tyre_count: int, adjust_pressure: int):
    """Set time - tyre change (with pressure adjustment)"""
    delay = ref_time.get("RandomTireDelay", 0)
    concurrent = ref_time.get("TireTimeConcurrent", 0)
    if adjust_pressure > 0 < tyre_count:  # only adjust pressure if change tyre
        pres_seconds = ref_time.get("PressureChange", 0)
    else:
        pres_seconds = 0.0
    if 0 < tyre_count <= 2:
        seconds = ref_time.get("TwoTireChange", 0)
    elif 2 < tyre_count:
        seconds = ref_time.get("FourTireChange", 0)
    else:
        delay = seconds = 0.0
    return max(seconds, pres_seconds), delay, concurrent


def set_time_front_wing(ref_time: dict, current: int, default: int):
    """Set time - front wing adjust"""
    if current != default:
        seconds = ref_time.get("FrontWingAdjust", 0)
    else:
        seconds = 0.0
    return seconds, 0.0, 1


def set_time_rear_wing(ref_time: dict, current: int, default: int):
    """Set time - rear wing adjust"""
    if current != default:
        seconds = ref_time.get("RearWingAdjust", 0)
    else:
        seconds = 0.0
    return seconds, 0.0, 1


def set_time_radiator(ref_time: dict, current: int, default: int):
    """Set time - radiator adjust"""
    if current != default:
        seconds = ref_time.get("RadiatorChange", 0)
    else:
        seconds = 0.0
    return seconds, 0.0, 1


def set_time_brake(ref_time: dict, current: int):
    """Set time - brake change"""
    delay = ref_time.get("RandomBrakeDelay", 0)
    concurrent = ref_time.get("BrakeTimeConcurrent", 0)
    if current > 0:
        seconds = ref_time.get("BrakeChange", 0)
    else:
        delay = seconds = 0.0
    return seconds, delay, concurrent


def get_fuel_ratio(current: int, ratio_set: list):
    """Get fuel ratio from data string"""
    try:
        ratio = float(ratio_set[current].get("text", "0.0").strip(" "))
    except (AttributeError, TypeError, IndexError, ValueError):
        ratio = 0.0
    return ratio


def get_absolute_refuel(current: int, ratio_set: list):
    """Get absolute refuel (liter) from data string"""
    try:
        raw = ratio_set[current].get("text", "0L").strip(" ")
        fuel = float(rex_number_split(raw)[0])
        if "gal" in raw.lower():  # convert to liter
            fuel *= 3.7854118
    except (AttributeError, TypeError, IndexError, ValueError):
        fuel = 0.0
    return fuel


def set_time_fuel(ref_time: dict, current: float, remaining: float):
    """Set time - fuel (liter)"""
    delay = ref_time.get("FuelRandomDelay", 0)
    concurrent = ref_time.get("FuelTimeConcurrent", 0)
    seconds = ref_time.get("FuelInsert", 0)
    seconds += ref_time.get("FuelRemove", 0)
    fill_rate = ref_time.get("FuelFillRate", 0)
    refill = current - remaining
    if refill > 0 < fill_rate:
        seconds += refill / fill_rate
    else:
        delay = seconds = 0.0
    return seconds, delay, concurrent
