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
RestAPI module
"""

from __future__ import annotations
import asyncio
import logging
import json
import re
import socket
from urllib.request import urlopen
from typing import Any
from collections.abc import Callable

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from ..validator import value_type
from .. import formatter as fmt
from .. import weather as wthr

logger = logging.getLogger(__name__)

# Define output set
# 0 - minfo, 1 - output, 2 - default value, 3 - function, 4 - dict keys
SET_TIMESCALE = (
    (minfo.restapi, "timeScale", 1, None, "currentValue"),
)
SET_PRIVATEQUALIFY = (
    (minfo.restapi, "privateQualifying", 0, None, "currentValue"),
)
SET_CHASSIS = (
    (minfo.restapi, "steeringWheelRange", 0.0, fmt.steerlock_to_number, "VM_STEER_LOCK", "stringValue"),
)
SET_CURRENTSTINT = (
    (minfo.restapi, "currentVirtualEnergy", 0.0, None, "fuelInfo", "currentVirtualEnergy"),
    (minfo.restapi, "maxVirtualEnergy", 0.0, None, "fuelInfo", "maxVirtualEnergy"),
    (minfo.restapi, "aeroDamage", -1.0, None, "wearables", "body", "aero"),
    (minfo.restapi, "brakeWear", [-1] * 4, None, "wearables", "brakes"),
    (minfo.restapi, "suspensionDamage", [-1] * 4, None, "wearables", "suspension"),
)
SET_WEATHERFORECAST = (
    (minfo.restapi, "forecastPractice", wthr.DEFAULT, wthr.forecast_rf2, "PRACTICE"),
    (minfo.restapi, "forecastQualify", wthr.DEFAULT, wthr.forecast_rf2, "QUALIFY"),
    (minfo.restapi, "forecastRace", wthr.DEFAULT, wthr.forecast_rf2, "RACE"),
)
# Define task set
# 0 - regex pattern (sim name), 1 - url path, 2 - output set
TASK_RUNONCE = (
    ("LMU|RF2", "sessions/setting/SESSSET_race_timescale", SET_TIMESCALE),
    ("LMU|RF2", "sessions/setting/SESSSET_private_qual", SET_PRIVATEQUALIFY),
    ("LMU|RF2", "sessions/weather", SET_WEATHERFORECAST),
    ("LMU", "garage/chassis", SET_CHASSIS),
)
TASK_REPEATS = (
    ("LMU", "garage/UIScreen/DriverHandOffStintEnd", SET_CURRENTSTINT),
)


class Realtime(DataModule):
    """Rest API data"""

    def __init__(self, config, module_name):
        super().__init__(config, module_name)
        self.task_deletion = set()

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        sorted_task_runonce = {}
        sorted_task_repeats = {}

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    sim_name = api.read.check.sim_name()
                    sort_tasks(sim_name, TASK_RUNONCE, sorted_task_runonce)
                    sort_tasks(sim_name, TASK_REPEATS, sorted_task_repeats)
                    self.__run_tasks(sim_name, sorted_task_runonce, sorted_task_repeats)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    # Reset when finished
                    reset_to_default(sorted_task_runonce)
                    reset_to_default(sorted_task_repeats)

        # Reset to default on close
        reset_to_default(sorted_task_runonce)
        reset_to_default(sorted_task_repeats)

    def __run_tasks(self, sim_name: str, task_runonce: dict, task_repeats: dict):
        """Run tasks"""
        self.task_deletion.clear()
        url_rest, time_out, retry, retry_delay = self.__setup_connection(sim_name)
        if not url_rest:
            logger.info("RestAPI: game session not found")
            return
        # Run all tasks once per garage out, and check availability
        if task_runonce:
            asyncio.run(self.__task_runonce(
                task_runonce, url_rest, time_out, retry, retry_delay))
            remove_unavailable_task(task_runonce, self.task_deletion)
        if task_repeats:
            asyncio.run(self.__task_runonce(
                task_repeats, url_rest, time_out, retry, retry_delay))
            remove_unavailable_task(task_repeats, self.task_deletion)
        # Run repeatedly while on track
        if task_repeats:
            asyncio.run(self.__task_repeats(task_repeats, url_rest, time_out))

    def __setup_connection(self, sim_name: str) -> tuple[str, float, int, float]:
        """Connection setup"""
        url_host = self.mcfg["url_host"]
        time_out = min(max(self.mcfg["connection_timeout"], 0.5), 10)
        retry = min(max(int(self.mcfg["connection_retry"]), 0), 10)
        retry_delay = min(max(self.mcfg["connection_retry_delay"], 0), 60)
        if sim_name == "LMU":
            url_port = self.mcfg["url_port_lmu"]
            url_rest = f"http://{url_host}:{url_port}/rest/"
        elif sim_name == "RF2":
            url_port = self.mcfg["url_port_rf2"]
            url_rest = f"http://{url_host}:{url_port}/rest/"
        else:
            url_rest = ""
        return url_rest, time_out, retry, retry_delay

    async def __task_runonce(self, active_task: dict, url_rest: str,
        time_out: float, retry: int, retry_delay: float):
        """Update task runonce"""
        tasks = (
            self.__fetch_retry(
                url_rest, time_out, retry, retry_delay, resource_name, output_set
            )
            for resource_name, output_set in active_task.items()
        )
        return await asyncio.gather(*tasks)

    async def __task_repeats(self, active_task: dict, url_rest: str, time_out: float):
        """Update task repeatedly"""
        tasks = (
            self.__fetch(url_rest, time_out, resource_name, output_set)
            for resource_name, output_set in active_task.items()
        )
        return await asyncio.gather(*tasks)

    async def __fetch(self, url_rest: str, time_out: float,
        resource_name: str, output_set: tuple):
        """Fetch data without retry"""
        full_url = f"{url_rest}{resource_name}"
        while not self._event.is_set() and self.state.active:
            output_resource(output_set, full_url, time_out)
            await asyncio.sleep(self.active_interval)

    async def __fetch_retry(self, url_rest: str, time_out: float, retry: int,
        retry_delay: float, resource_name: str, output_set: tuple):
        """Fetch data with retry"""
        data_available = False
        total_retry = retry
        full_url = f"{url_rest}{resource_name}"
        while not self._event.is_set() and retry >= 0:
            resource_output = get_resource(full_url, time_out)
            # Verify & retry
            if not isinstance(resource_output, dict):
                logger.info("RestAPI: ERROR: %s %s (%s/%s retries left)",
                    resource_name.upper(), resource_output, retry, total_retry)
                retry -= 1
                if retry < 0:  # add to unavailable task delete list
                    self.task_deletion.add(resource_name)
                    break
                await asyncio.sleep(retry_delay)
                continue
            # Output
            for output in output_set:
                if get_value(resource_output, *output):
                    data_available = True
            # Add to unavailable task delete list
            if not data_available:
                self.task_deletion.add(resource_name)
            logger.info("RestAPI: UPDATE: %s", resource_name.upper())
            break


def reset_to_default(active_task: dict):
    """Reset active task data to default"""
    if active_task:
        for resource_name, output_set in active_task.items():
            for output in output_set:
                setattr(output[0], output[1], output[2])
            logger.info("RestAPI: RESET: %s", resource_name.upper())
        active_task.clear()


def remove_unavailable_task(active_task: dict, task_deletion: set):
    """Remove unavailable task from deletion list"""
    for resource_name in task_deletion:
        if resource_name in active_task:
            active_task.pop(resource_name, None)
            logger.info("RestAPI: MISSING: %s", resource_name.upper())


def get_resource(url: str, time_out: float) -> Any | str:
    """Get resource from REST API"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            return json.load(raw_resource)
    except (TypeError, AttributeError, KeyError, ValueError):
        return "data not found"
    except (OSError, TimeoutError, socket.timeout):
        return "connection failed"


def output_resource(output_set: tuple, url: str, time_out: float) -> None:
    """Get resource from REST API and output data, skip unnecessary checking"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            resource_output = json.load(raw_resource)
            for output in output_set:
                get_value(resource_output, *output)
    except (TypeError, AttributeError, KeyError, ValueError,
            OSError, TimeoutError, socket.timeout):
        return


def get_value(
    data: dict, target: object, output: str, default: Any,
    mod_func: Callable | None, *keys: tuple[str, ...]) -> bool:
    """Get value from resource dictionary, fallback to default value if invalid"""
    for key in keys:
        data = data.get(key, None)
        if data is None:  # not exist, set to default
            setattr(target, output, default)
            return False
        if not isinstance(data, dict):
            break

    if mod_func:
        setattr(target, output, value_type(mod_func(data), default))
    else:
        setattr(target, output, value_type(data, default))
    return True


def sort_tasks(sim_name: str, task_set: tuple, active_task: dict):
    """Sort task set into dictionary, key - resource_name, value - output_set"""
    for pattern, resource_name, output_set in task_set:
        if re.search(pattern, sim_name):
            active_task[resource_name] = output_set
