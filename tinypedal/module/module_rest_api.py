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
Rest API module
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
from .. import validator as val

MODULE_NAME = "module_rest_api"

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Wheels data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        task_once = (
            ("COMMON", "sessions", output_sessions),
            ("LMU", "garage/chassis", output_garage_chassis),
        )

        task_repeat = (
            ("LMU", "garage/UIScreen/DriverHandOffStintEnd", output_garage_fuel),
        )

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    (sim_name, url_rest, time_out, retry, retry_delay
                     ) = self.__connection_setup()
                    sorted_task_once = self.__sort_task(sim_name, task_once)
                    sorted_task_repeat = self.__sort_task(sim_name, task_repeat)
                    # Run task once per garage out
                    asyncio.run(self.__task_once(sorted_task_once, url_rest, time_out, retry, retry_delay))

                # Run repeatedly while on track
                if sorted_task_repeat:
                    asyncio.run(self.__task_repeat(sorted_task_repeat, url_rest, time_out))

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    self.cleanup()

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

    def __sort_task(self, sim_name: str, task_list: tuple) -> list:
        """Sort task list"""
        return [task for task in task_list if task[0] == "COMMON" or task[0] == sim_name]

    async def __task_once(self, task_list: tuple, url: str,
        time_out: int, retry: int, retry_delay: float) -> None:
        """Update task once"""
        if not url:
            return None
        tasks = (self.__fetch_retry(url, time_out, retry, retry_delay, task[1], task[2])
                 for task in task_list)
        await asyncio.gather(*tasks)
        return None

    async def __task_repeat(self, task_list: tuple, url: str, time_out: int) -> None:
        """Update task repeatedly"""
        if not url:
            return None
        tasks = (self.__fetch(url, time_out, task[1], task[2]) for task in task_list)
        await asyncio.gather(*tasks)
        return None

    async def __fetch(self, url_rest: str, time_out: int,
        resource_name: str, update_func: object) -> None:
        """Fetch data without retry"""
        resource_output = get_resource(f"{url_rest}{resource_name}", time_out)
        if isinstance(resource_output, dict):
            update_func(resource_output)

    async def __fetch_retry(self, url_rest: str, time_out: int, retry: int,
        retry_delay: float, resource_name: str, update_func: object) -> None:
        """Fetch data with retry"""
        full_url = f"{url_rest}{resource_name}"
        while not self.event.wait(0) and retry >= 0:
            resource_output = get_resource(full_url, time_out)
            if isinstance(resource_output, dict):
                update_func(resource_output)
                logger.info("Rest API: %s data updated", resource_name.upper())
                break
            logger.info("Rest API: %s %s, %s retry", resource_name.upper(), resource_output, retry)
            retry -= 1
            await asyncio.sleep(retry_delay)

    def cleanup(self):
        """Reset data to default"""
        minfo.restapi.timeScale = 1
        minfo.restapi.privateQualifying = 0
        minfo.restapi.steeringWheelRange = 0
        minfo.restapi.currentVirtualEnergy = 0
        minfo.restapi.maxVirtualEnergy = 0


def output_sessions(data: dict) -> None:
    """Output sessions data"""
    minfo.restapi.timeScale = get_value(data, "SESSSET_race_timescale", "currentValue", 1)
    minfo.restapi.privateQualifying = get_value(data, "SESSSET_private_qual", "currentValue", 0)


def output_garage_chassis(data: dict) -> None:
    """Output garage chassis data"""
    minfo.restapi.steeringWheelRange = get_value(data, "VM_STEER_LOCK", "stringValue", 0.0, steerlock_to_number)


def output_garage_fuel(data: dict) -> None:
    """Output garage fuel data"""
    minfo.restapi.currentVirtualEnergy = get_value(data, "fuelInfo", "currentVirtualEnergy", 0.0)
    minfo.restapi.maxVirtualEnergy = get_value(data, "fuelInfo", "maxVirtualEnergy", 0.0)


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
    data: dict, key: str, sub_key:str, default: any, mod_func: object | None = None) -> any:
    """Get value from resource dictionary, fallback to default value if invalid"""
    info = data.get(key, None)
    if not info:
        return default

    value = info.get(sub_key, None)
    if mod_func:
        return val.value_type(mod_func(value), default)
    return val.value_type(value, default)


def steerlock_to_number(value: str) -> float:
    """Convert steerlock string to float value"""
    try:
        deg = re.split(" ", value)[0]
        return float(deg)
    except ValueError:
        return 0.0
