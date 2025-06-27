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
Overlay base common class.
"""

from __future__ import annotations


class WarningFlash:
    """Warning flash state"""

    __slots__ = (
        "_last_condition",
        "_highlight",
        "_highlight_seconds",
        "_highlight_timer",
        "_interval_seconds",
        "_interval_timer",
        "_flash_count",
        "_flash_max",
    )

    def __init__(self, duration: float, interval: float, max_count: int):
        self._last_condition = False
        self._highlight = False
        self._highlight_seconds = max(duration, 0.2)
        self._highlight_timer = 0.0
        self._interval_seconds = max(interval, 0.2)
        self._interval_timer = 0.0
        self._flash_count = 0
        self._flash_max = max(max_count, 3)

    def state(self, elapsed: float, condition: bool) -> bool:
        """Update warning flash state"""
        if self._last_condition != condition:
            self._last_condition = condition
            if condition:
                self._highlight_timer = elapsed
                self._highlight = False
                self._interval_timer = 0
                self._flash_count = 0

        if not condition:
            return False
        elif self._flash_count >= self._flash_max:
            return True

        if elapsed - self._highlight_timer < self._highlight_seconds:
            if not self._highlight:
                self._flash_count += 1
            self._highlight = True
            self._interval_timer = elapsed
        else:
            self._highlight = False
            if elapsed - self._interval_timer >= self._interval_seconds:
                self._highlight_timer = elapsed

        return self._highlight
