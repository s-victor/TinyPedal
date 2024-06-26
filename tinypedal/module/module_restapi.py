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

MODULE_NAME = "module_restapi"

logger = logging.getLogger(__name__)

# Define output set
# 0 - minfo.restapi, 1 - default value, 2 - key, 3 - sub key, 4 - function
SET_TIMESCALE = (
    ("timeScale", 1, "currentValue"),
)
SET_PRIVATEQUALIFY = (
    ("privateQualifying", 0, "currentValue"),
)
SET_CHASSIS = (
    ("steeringWheelRange", 0.0, "VM_STEER_LOCK", "stringValue", fmt.steerlock_to_number),
)
SET_CONSUMPTION = (
    ("currentVirtualEnergy", 0.0, "fuelInfo", "currentVirtualEnergy"),
    ("maxVirtualEnergy", 0.0, "fuelInfo", "maxVirtualEnergy"),
)

# Define task set
# 0 - regex pattern (sim name), 1 - url path, 2 - output set
TASK_ONCE = (
    ("LMU|RF2", "sessions/setting/SESSSET_race_timescale", SET_TIMESCALE),
    ("LMU|RF2", "sessions/setting/SESSSET_private_qual", SET_PRIVATEQUALIFY),
    ("LMU", "garage/chassis", SET_CHASSIS),
)
TASK_REPEAT = (
    ("LMU", "garage/UIScreen/DriverHandOffStintEnd", SET_CONSUMPTION),
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

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    self.task_delete.clear()

                    (sim_name, url_rest, time_out, retry, retry_delay
                     ) = self.__connection_setup()
                    sorted_task_once = sort_tasks(sim_name, TASK_ONCE)
                    sorted_task_repeat = sort_tasks(sim_name, TASK_REPEAT)
                    # Run task once per garage out, and check availability
                    asyncio.run(self.__task_once(sorted_task_once, url_rest, time_out, retry, retry_delay))
                    asyncio.run(self.__task_once(sorted_task_repeat, url_rest, time_out, retry, retry_delay))
                    # Remove unavailable task
                    self.__remove_unavailable_task(sorted_task_once)
                    self.__remove_unavailable_task(sorted_task_repeat)

                # Run repeatedly while on track
                if sorted_task_repeat:
                    asyncio.run(self.__task_repeat(sorted_task_repeat, url_rest, time_out))

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    self.reset_to_default()

        # Reset to default on close
        self.reset_to_default()

    def __remove_unavailable_task(self, active_task: dict) -> None:
        """Remove unavailable task"""
        for resource_name in self.task_delete:
            if resource_name in active_task:
                active_task.pop(resource_name, None)
                logger.info("Rest API: %s unavailable", resource_name.upper())

    def __connection_setup(self) -> tuple:
        """Connection setup"""
        url_host = self.mcfg["url_host"]
        time_out = min(max(self.mcfg["connection_timeout"], 0.1), 10)
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

    async def __task_once(self, active_task: dict, url: str,
        time_out: int, retry: int, retry_delay: float) -> None:
        """Update task once"""
        if not url:
            return None
        tasks = (self.__fetch_retry(url, time_out, retry, retry_delay, resource_name, active_task[resource_name])
                 for resource_name in active_task)
        return await asyncio.gather(*tasks)

    async def __task_repeat(self, active_task: dict, url: str, time_out: int) -> None:
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
                if not get_value(resource_output, *output):
                    self.task_delete.add(resource_name)
            logger.info("Rest API: %s data updated", resource_name.upper())
            break

    def reset_to_default(self):
        """Reset data to default"""
        minfo.restapi.timeScale = 1
        minfo.restapi.privateQualifying = 0
        minfo.restapi.steeringWheelRange = 0
        minfo.restapi.currentVirtualEnergy = 0
        minfo.restapi.maxVirtualEnergy = 0


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
    data: dict, output: str, default: any,
    key: str | None = None, sub_key: str | None = None,
    mod_func: object | None = None) -> any:
    """Get value from resource dictionary, fallback to default value if invalid"""
    value = data.get(key, None)

    if sub_key and isinstance(value, dict):
        value = value.get(sub_key, None)

    if value is None:
        setattr(minfo.restapi, output, default)
        return False

    if mod_func:
        setattr(minfo.restapi, output, val.value_type(mod_func(value), default))
    else:
        setattr(minfo.restapi, output, val.value_type(value, default))
    return True


def sort_tasks(sim_name: str, task_set: tuple) -> dict:
    """Sort task set into dictionary"""
    return {task[1]:task[2] for task in task_set
            if re.search(task[0], sim_name)}
