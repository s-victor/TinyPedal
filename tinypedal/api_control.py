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
API control
"""

import logging

from .setting import cfg
from .api_connector import API_PACK

logger = logging.getLogger(__name__)


class APIControl:
    """API Control"""

    def __init__(self):
        self._api = None
        self._read = None
        self._state = None

    def connect(self, name: str = ""):
        """Connect to API

        name: match api name in API_PACK
        """
        if not name:
            name = cfg.shared_memory_api["api_name"]

        for _api in API_PACK:
            if _api.NAME == name:
                self._api = _api()
                return None

        logger.warning("CONNECTING: Invalid API name, fall back to default")
        self._api = API_PACK[0]()
        return None

    def start(self):
        """Start API"""
        logger.info("ENCODING: %s", cfg.shared_memory_api["character_encoding"])
        logger.info("CONNECTING: %s API", self._api.NAME)
        self.setup()
        self._api.start()
        self._read = self._api.dataset()
        logger.info("CONNECTED: %s API (%s)", self._api.NAME, self.version)

    def stop(self):
        """Stop API"""
        logger.info("DISCONNECTING: %s API (%s)", self._api.NAME, self.version)
        self._api.stop()
        logger.info("DISCONNECTED: %s API", self._api.NAME)

    def restart(self):
        """Restart API"""
        self.stop()
        self.connect()
        self.start()

    def setup(self):
        """Setup & apply API changes"""
        api_config = (
            cfg.shared_memory_api["access_mode"],
            cfg.shared_memory_api["process_id"],
            cfg.shared_memory_api["enable_player_index_override"],
            cfg.shared_memory_api["player_index"],
            cfg.shared_memory_api["character_encoding"].lower(),
        )
        self._api.setup(api_config)
        if cfg.shared_memory_api["enable_active_state_override"]:
            self._state = self.__state_override
        else:
            self._state = self.__state_driving

    def __state_override(self):
        """API state override"""
        return cfg.shared_memory_api["active_state"]

    def __state_driving(self):
        """API state driving"""
        return not self._api.info.isPaused and self._read.vehicle.is_driving()

    @property
    def read(self):
        """API info reader"""
        return self._read

    @property
    def name(self):
        """API name output"""
        return self._api.NAME

    @property
    def state(self):
        """API state output"""
        return self._state()

    @property
    def version(self):
        """API version output"""
        version = self._read.check.version()
        return version if version else "not running"


api = APIControl()
