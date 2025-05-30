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
RestAPI module
"""

from __future__ import annotations

import asyncio
import json
import logging
import socket
from typing import Any
from urllib.request import urlopen

from ..api_control import api
from ..const_common import TYPE_JSON
from ._base import DataModule
from ._task import TASK_REPEATS, TASK_RUNONCE, ResRawOutput

logger = logging.getLogger(__name__)


class Realtime(DataModule):
    """Rest API data"""

    __slots__ = (
        "task_deletion",
        "task_cancel",
    )

    def __init__(self, config, module_name):
        super().__init__(config, module_name)
        self.task_deletion = set()
        self.task_cancel = False

    def update_data(self):
        """Update module data"""
        _event_wait = self._event.wait
        reset = False
        update_interval = self.active_interval

        sorted_task_runonce = {}
        sorted_task_repeats = {}

        while not _event_wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval
                    self.__run_tasks(
                        api.read.check.sim_name(),
                        sorted_task_runonce,
                        sorted_task_repeats,
                    )

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

    def __sort_tasks(self, sim_name: str, active_task: dict, task_set: tuple):
        """Sort task set into dictionary, key - resource_name, value - output_set"""
        for pattern, resource_name, output_set, condition in task_set:
            if sim_name in pattern and self.mcfg.get(condition, True):
                active_task[resource_name] = output_set

    def __run_tasks(self, sim_name: str, task_runonce: dict, task_repeats: dict):
        """Run tasks"""
        self.task_deletion.clear()
        self.task_cancel = False
        # Load connection setting
        url_host = self.mcfg["url_host"]
        time_out = min(max(self.mcfg["connection_timeout"], 0.5), 10)
        retry = min(max(int(self.mcfg["connection_retry"]), 0), 10)
        retry_delay = min(max(self.mcfg["connection_retry_delay"], 0), 60)
        url_port = self.mcfg.get(f"url_port_{sim_name.lower()}", -1)
        if url_port < 0:
            logger.info("RestAPI: game session not found")
            return
        # Sort tasks
        self.__sort_tasks(sim_name, task_runonce, TASK_RUNONCE)
        self.__sort_tasks(sim_name, task_repeats, TASK_REPEATS)
        # Run all tasks once per garage out, and check availability
        if task_runonce:
            asyncio.run(self.__task_runonce(
                task_runonce, url_host, url_port, time_out, retry, retry_delay))
            remove_unavailable_task(task_runonce, self.task_deletion)
        if task_repeats:
            asyncio.run(self.__task_runonce(
                task_repeats, url_host, url_port, time_out, retry, retry_delay))
            remove_unavailable_task(task_repeats, self.task_deletion)
        # Run repeatedly while on track
        if task_repeats:
            asyncio.run(self.__task_repeats(
                task_repeats, url_host, url_port, time_out))

    async def __task_runonce(self, active_task: dict, url_host: str, url_port: int,
        time_out: float, retry: int, retry_delay: float):
        """Update task runonce"""
        tasks = (
            self.__fetch_retry(
                url_host, url_port, time_out, retry, retry_delay, resource_name, output_set
            )
            for resource_name, output_set in active_task.items()
        )
        return await asyncio.gather(*tasks)

    async def __task_control(self, task_group: tuple[asyncio.Task, ...]):
        """Control task running state"""
        _event_is_set = self._event.is_set
        while not _event_is_set() and self.state.active:
            await asyncio.sleep(0.1)  # check every 100ms
        # Set cancel state to exit loop in case failed to cancel
        self.task_cancel = True
        # Cancel all running tasks
        for task in task_group:
            task.cancel()

    async def __task_repeats(self, active_task: dict, url_host: str, url_port: int, time_out: float):
        """Update task repeatedly"""
        task_group = tuple(
            asyncio.create_task(
                self.__fetch(url_host, url_port, time_out, resource_name, output_set)
            )
            for resource_name, output_set in active_task.items()
        )
        # Task control
        await asyncio.create_task(self.__task_control(task_group))
        for task in task_group:
            try:
                await task
            except asyncio.CancelledError:
                pass

    async def __fetch(self, url_host: str, url_port: int, time_out: float,
        resource_name: str, output_set: tuple[ResRawOutput, ...]):
        """Fetch data without retry"""
        try:
            full_url = f"http://{url_host}:{url_port}{resource_name}"
            delay = min_delay = self.active_interval
            last_hash = new_hash = -1
            while not self.task_cancel:  # use task control to cancel & exit loop
                new_hash = output_resource(output_set, full_url, time_out)
                if last_hash != new_hash:
                    last_hash = new_hash
                    delay = min_delay
                elif delay < 2:  # increase update delay while no new data
                    delay += delay / 2
                    if delay > 2:
                        delay = 2
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass

    async def __fetch_retry(self, url_host: str, url_port: int, time_out: float, retry: int,
        retry_delay: float, resource_name: str, output_set: tuple[ResRawOutput, ...]):
        """Fetch data with retry"""
        data_available = False
        total_retry = retry
        full_url = f"http://{url_host}:{url_port}{resource_name}"
        while not self._event.is_set() and retry >= 0:
            resource_output = get_resource(full_url, time_out)
            # Verify & retry
            if not isinstance(resource_output, TYPE_JSON):
                logger.info("RestAPI: ERROR: %s %s (%s/%s retries left)",
                    resource_name.upper(), resource_output, retry, total_retry)
                retry -= 1
                if retry < 0:  # add to unavailable task delete list
                    self.task_deletion.add(resource_name)
                    break
                await asyncio.sleep(retry_delay)
                continue
            # Output
            for res in output_set:
                if res.update(resource_output):
                    data_available = True
            # Add to unavailable task delete list
            if not data_available:
                self.task_deletion.add(resource_name)
            else:
                logger.info("RestAPI: UPDATE: %s", resource_name.upper())
            break


def reset_to_default(active_task: dict[str, tuple[ResRawOutput, ...]]):
    """Reset active task data to default"""
    if active_task:
        for resource_name, output_set in active_task.items():
            for res in output_set:
                res.reset()
            logger.info("RestAPI: RESET: %s", resource_name.upper())
        active_task.clear()


def remove_unavailable_task(active_task: dict, task_deletion: set):
    """Remove unavailable task from deletion list"""
    for resource_name in task_deletion:
        if active_task.pop(resource_name, None):
            logger.info("RestAPI: MISSING: %s", resource_name.upper())


def get_resource(url: str, time_out: float) -> Any | str:
    """Get resource from REST API"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            return json.load(raw_resource)
    except (AttributeError, TypeError, IndexError, KeyError, ValueError):
        return "data not found"
    except (OSError, TimeoutError, socket.timeout, BaseException):
        return "connection timeout"


def output_resource(output_set: tuple[ResRawOutput, ...], url: str, time_out: float) -> int:
    """Get resource from REST API and output data, skip unnecessary checking"""
    try:
        with urlopen(url, timeout=time_out) as raw_resource:
            raw_bytes = raw_resource.read()
            if raw_bytes:
                resource_output = json.loads(raw_bytes)
                for res in output_set:
                    res.update(resource_output)
            return hash(raw_bytes)
    except (AttributeError, TypeError, IndexError, KeyError, ValueError,
            OSError, TimeoutError, socket.timeout, BaseException):
        return -1
