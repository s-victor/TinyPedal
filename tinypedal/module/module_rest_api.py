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

import logging
import json
from urllib.request import urlopen
from urllib.error import URLError

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

        last_session_id = ("",-1,-1,-1)

        while not self.event.wait(update_interval):
            if api.state:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    combo_id = api.read.check.combo_id()
                    session_id = api.read.check.session_id()
                    if not val.same_session(combo_id, session_id, last_session_id):
                        self.__fetch_data()
                        last_session_id = (combo_id, *session_id)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval

    def __fetch_data(self):
        """Fetch data"""
        url_host = self.mcfg["url_host"]
        time_out = self.mcfg["connection_timeout"]
        sim_name = api.read.check.sim_name()

        if sim_name == "RF2":
            url_port = self.mcfg["url_port_rf2"]
        else:
            url_port = self.mcfg["url_port_lmu"]

        try:
            with urlopen(f"http://{url_host}:{url_port}/rest/sessions", timeout=time_out
                ) as session:
                if session.getcode() == 200:
                    _session_info = json.loads(session.read().decode("utf-8"))
                    self.__output(_session_info)
                    logger.info("Rest API: %s data updated", sim_name)
                else:
                    logger.error("Rest API: no matched data found")
        except KeyError:
            logger.error("Rest API: no matched data found")
        except URLError:
            logger.error("Rest API: connection timed out")

    def __output(self, _session_info):
        """Output data"""
        minfo.session.timeScale = _session_info["SESSSET_race_timescale"]["currentValue"]
        minfo.session.privateQualifying = _session_info["SESSSET_private_qual"]["currentValue"]
