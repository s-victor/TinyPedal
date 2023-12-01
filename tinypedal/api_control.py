#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2023 TinyPedal developers, see contributors.md file
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

    def connect(self, name):
        """Connect to API with matching name in API_PACK"""
        name_found = False
        for _api in API_PACK:
            if _api.NAME == name:
                self._api = _api()
                name_found = True
                break
        if not name_found:
            logger.info("Invalid API name, fall back to default API")
            self._api = API_PACK[0]()

    def start(self):
        """Start API"""
        self.setup()
        self._api.start()
        logger.info("activated API: %s (%s)", self._api.NAME, self.version)

    def stop(self):
        """Stop API"""
        self._api.stop()

    def restart(self):
        """Restart API"""
        self.stop()
        self.connect(cfg.shared_memory_api["api_name"])
        self.start()

    def setup(self):
        """Setup & apply API changes"""
        access_mode = cfg.shared_memory_api["access_mode"]
        process_id = cfg.shared_memory_api["process_id"]
        player_override = cfg.shared_memory_api["enable_player_index_override"]
        player_index = cfg.shared_memory_api["player_index"]
        self._api.setup(
            access_mode,
            process_id,
            player_override,
            player_index
        )

    @property
    def read(self):
        """API info reader"""
        return self._api.read

    @property
    def name(self):
        """API name output"""
        return self._api.NAME

    @property
    def state(self):
        """API state output"""
        if cfg.shared_memory_api["enable_active_state_override"]:
            return cfg.shared_memory_api["active_state"]
        return self._api.state()

    @property
    def version(self):
        """API version output"""
        version = self._api.version()
        return version if version else "unknown ver."


api = APIControl()
