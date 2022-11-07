#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Load module & function
"""

from tinypedal.setting import cfg
from tinypedal.realtime_delta import DeltaTime
from tinypedal.realtime_fuel import FuelUsage
from tinypedal.realtime_relative import RelativeInfo
from tinypedal.overlay_toggle import OverlayLock, OverlayAutoHide


# Load delta module
delta_time = DeltaTime()
if cfg.overlay["delta_module"]:
    delta_time.start()

# Load fuel module
fuel_usage = FuelUsage()
if cfg.overlay["fuel_module"]:
    fuel_usage.start()

# Load relative module
relative_info = RelativeInfo()
if cfg.overlay["relative_module"]:
    relative_info.start()

# Load overlay lock
overlay_lock = OverlayLock()

# Load overlay auto hide
overlay_hide = OverlayAutoHide(cfg.active_widget_list)
