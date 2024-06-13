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

        task_list = (
            ("COMMON", "sessions", output_sessions),
            ("LMU", "garage/chassis", output_garage),
        )

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    asyncio.run(self.__tasks(task_list))

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

    def __connection_setup(self, sim_name: str) -> tuple:
        """Connection setup"""
        url_host = self.mcfg["url_host"]
        time_out = min(max(self.mcfg["connection_timeout"], 0.1), 10)
        retry = min(max(self.mcfg["connection_retry"], 0), 10)
        retry_delay = min(max(self.mcfg["connection_retry_delay"], 0), 60)

        if sim_name == "LMU":
            url_port = self.mcfg["url_port_lmu"]
        elif sim_name == "RF2":
            url_port = self.mcfg["url_port_rf2"]
        else:
            logger.info("Rest API: game session not found, abort")
            return None
        return url_host, url_port, time_out, retry, retry_delay

    async def __tasks(self, task_list) -> None:
        """Update tasks"""
        sim_name = api.read.check.sim_name()
        connection_info = self.__connection_setup(sim_name)
        if not connection_info:
            return None

        async_tasks = set()
        for task in task_list:
            if task[0] == "COMMON" or task[0] == sim_name:
                async_tasks.add(self.__fetch(*connection_info, task[1], task[2]))
        await asyncio.gather(*async_tasks)
        return None

    async def __fetch(self, host: str, port: int, time_out: int, retry: int,
        retry_delay: float, resource_name: str, update_func: object) -> None:
        """Fetch data"""
        url = f"http://{host}:{port}/rest/{resource_name}"
        while not self.event.wait(0) and retry >= 0:
            resource_data = get_resource(url, time_out, retry, resource_name)
            if resource_data:
                update_func(resource_data)
                break
            retry -= 1
            await asyncio.sleep(retry_delay)


def output_sessions(data: dict) -> None:
    """Output sessions data"""
    minfo.restapi.timeScale = get_value(data, "SESSSET_race_timescale", "currentValue", 1)
    minfo.restapi.privateQualifying = get_value(data, "SESSSET_private_qual", "currentValue", 0)


def output_garage(data: dict) -> None:
    """Output garage data"""
    minfo.restapi.steeringWheelRange = get_value(data, "VM_STEER_LOCK", "stringValue", 0.0, steerlock_to_number)


def get_resource(url: str, time_out: int, retry: int, resource_name: str) -> (dict | None):
    """Get resource from REST API"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            if raw_resource.getcode() != 200:
                raise ValueError
            output = json.loads(raw_resource.read().decode("utf-8"))
            if not isinstance(output, dict):
                raise AttributeError
            logger.info("Rest API: %s data updated", resource_name.upper())
            return output
    except (TypeError, AttributeError, KeyError, ValueError):
        retry_text = f"{retry} retry" if retry > 0 else "abort"
        logger.info("Rest API: %s data not found, %s", resource_name.upper(), retry_text)
    except (OSError, TimeoutError, socket.timeout):
        retry_text = f"{retry} retry" if retry > 0 else "abort"
        logger.info("Rest API: %s connection timed out, %s", resource_name.upper(), retry_text)
    return None


def get_value(
    data: dict, key: str, sub_key:str, default: any, mod_func: object | None = None) -> any:
    """Get value from resource dictionary, fallback to default value if invalid"""
    info = data.get(key, None)
    if not info:
        logger.info("Rest API: %s value not found, fallback to default", key)
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
