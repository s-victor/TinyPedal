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

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import formatter as fmt
from .. import validator as val
from .. import weather as wthr

MODULE_NAME = "module_restapi"

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
    """Wheels data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)
        self.task_delete = set()

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval
        sorted_task_runonce = {}
        sorted_task_repeats = {}

        while not self.event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    self.task_delete.clear()

                    (sim_name, url_rest, time_out, retry, retry_delay
                     ) = self.__connection_setup()
                    sorted_task_runonce = sort_tasks(sim_name, TASK_RUNONCE)
                    sorted_task_repeats = sort_tasks(sim_name, TASK_REPEATS)
                    # Run all tasks once per garage out, and check availability
                    if sorted_task_runonce:
                        asyncio.run(self.__task_runonce(
                            sorted_task_runonce, url_rest, time_out, retry, retry_delay))
                        self.__remove_unavailable_task(sorted_task_runonce)
                    if sorted_task_repeats:
                        asyncio.run(self.__task_runonce(
                            sorted_task_repeats, url_rest, time_out, retry, retry_delay))
                        self.__remove_unavailable_task(sorted_task_repeats)

                # Run repeatedly while on track
                if sorted_task_repeats:
                    asyncio.run(self.__task_repeats(sorted_task_repeats, url_rest, time_out))

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    reset_to_default((sorted_task_runonce, sorted_task_repeats))

        # Reset to default on close
        reset_to_default((sorted_task_runonce, sorted_task_repeats))

    def __remove_unavailable_task(self, active_task: dict) -> None:
        """Remove unavailable task"""
        for resource_name in self.task_delete:
            if resource_name in active_task:
                active_task.pop(resource_name, None)
                logger.info("Rest API: %s unavailable", resource_name.upper())

    def __connection_setup(self) -> tuple:
        """Connection setup"""
        url_host = self.mcfg["url_host"]
        time_out = min(max(self.mcfg["connection_timeout"], 0.5), 10)
        retry = min(max(self.mcfg["connection_retry"], 0), 10)
        retry_delay = min(max(self.mcfg["connection_retry_delay"], 0), 60)
        sim_name = api.read.check.sim_name()

        if sim_name == "LMU":
            url_port = self.mcfg["url_port_lmu"]
            url_rest = f"http://{url_host}:{url_port}/rest/"
        elif sim_name == "RF2":
            url_port = self.mcfg["url_port_rf2"]
            url_rest = f"http://{url_host}:{url_port}/rest/"
        else:
            logger.info("Rest API: game session not found")
            url_rest = ""
        return sim_name, url_rest, time_out, retry, retry_delay

    async def __task_runonce(self, active_task: dict, url: str,
        time_out: int, retry: int, retry_delay: float) -> any:
        """Update task runonce"""
        if not url:
            return None
        tasks = (self.__fetch_retry(url, time_out, retry, retry_delay, resource_name, active_task[resource_name])
                 for resource_name in active_task)
        return await asyncio.gather(*tasks)

    async def __task_repeats(self, active_task: dict, url: str, time_out: int) -> any:
        """Update task repeatedly"""
        if not url:
            return None
        tasks = (self.__fetch(url, time_out, resource_name, active_task[resource_name])
                 for resource_name in active_task)
        return await asyncio.gather(*tasks)

    async def __fetch(self, url_rest: str, time_out: int,
        resource_name: str, output_set: tuple) -> None:
        """Fetch data without retry"""
        resource_output = get_resource(f"{url_rest}{resource_name}", time_out)
        if isinstance(resource_output, dict):
            for output in output_set:
                get_value(resource_output, *output)

    async def __fetch_retry(self, url_rest: str, time_out: int, retry: int,
        retry_delay: float, resource_name: str, output_set: tuple) -> None:
        """Fetch data with retry"""
        data_available = False
        full_url = f"{url_rest}{resource_name}"
        while not self.event.wait(0) and retry >= 0:
            resource_output = get_resource(full_url, time_out)
            # Verify & retry
            if not isinstance(resource_output, dict):
                logger.info("Rest API: %s %s, %s retry",
                    resource_name.upper(), resource_output, retry)
                retry -= 1
                if retry < 0:  # add to unavailable task delete list
                    self.task_delete.add(resource_name)
                    break
                await asyncio.sleep(retry_delay)
                continue
            # Output
            for output in output_set:
                if get_value(resource_output, *output):
                    data_available = True
            # Add to unavailable task delete list
            if not data_available:
                self.task_delete.add(resource_name)
            logger.info("Rest API: %s data updated", resource_name.upper())
            break


def reset_to_default(task_dict_list: tuple):
    """Reset active task data to default"""
    for active_task in task_dict_list:
        for output_set in active_task.values():
            for output in output_set:
                setattr(output[0], output[1], output[2])


def get_resource(url: str, time_out: int) -> (dict | str):
    """Get resource from REST API"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            if raw_resource.getcode() != 200:
                raise ValueError
            return json.loads(raw_resource.read().decode("utf-8"))
    except (TypeError, AttributeError, KeyError, ValueError):
        return "data not found"
    except (OSError, TimeoutError, socket.timeout):
        return "connection failed"


def get_value(
    data: dict, target: object, output: str, default: any,
    mod_func: object | None, *keys) -> bool:
    """Get value from resource dictionary, fallback to default value if invalid"""
    for key in keys:
        data = data.get(key, None)
        if data is None:  # not exist, set to default
            setattr(target, output, default)
            return False
        if not isinstance(data, dict):
            break

    if mod_func:
        setattr(target, output, val.value_type(mod_func(data), default))
    else:
        setattr(target, output, val.value_type(data, default))
    return True


def sort_tasks(sim_name: str, task_set: tuple) -> dict:
    """Sort task set into dictionary, key - resource_name, value - output_set"""
    return {task[1]:task[2] for task in task_set if re.search(task[0], sim_name)}
