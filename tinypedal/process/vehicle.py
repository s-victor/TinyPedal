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
Vehicle function
"""

from __future__ import annotations

from itertools import islice
from typing import Mapping

from ..const_common import EMPTY_DICT
from ..regex_pattern import rex_number_extract


def expected_usage(value: str) -> float:
    """Extract expected fuel or energy usage from car setup"""
    try:
        match_obj = rex_number_extract.findall(value)
        assert match_obj is not None
        return float(match_obj[0]) / float(match_obj[1])
    except (ZeroDivisionError, AttributeError, IndexError, TypeError, ValueError):
        return 0.0


def steerlock_to_number(value: str) -> float:
    """Convert steerlock (degree) string to float value from car setup"""
    try:
        match_obj = rex_number_extract.search(value)
        assert match_obj is not None
        return float(match_obj.group())
    except (AttributeError, TypeError, ValueError):
        return 0.0


def stint_ve_usage(dataset: dict) -> Mapping[str, tuple[float, float, float]]:
    """Stint virtual energy usage"""
    if not isinstance(dataset, dict) or not dataset:
        return EMPTY_DICT
    output = {}
    for player_name, player_dataset in dataset.items():
        # Set default
        ve_remaining = -100.0
        ve_used = -1.0
        laps_done = -1.0
        # Calculate usage
        try:
            ve_prev = 0.0
            ve_curr = 0.0
            prev_diff = 0.0
            skip_pit = False
            for data in islice(reversed(player_dataset), 6):
                ve_curr = data["ve"]
                # Initial check
                if ve_remaining == -100.0:
                    if ve_curr == 0:  # ve unavailable
                        raise ValueError
                    ve_remaining = ve_curr
                    ve_prev = ve_curr
                    laps_done = data["lap"]
                    continue
                # Skip pit refill
                if skip_pit:
                    ve_prev = ve_curr
                    skip_pit = False
                    continue
                # Skip 0 ve
                if ve_curr == 0 or ve_prev == 0:
                    ve_prev = ve_curr
                    continue
                # Calculate usage
                diff = ve_curr - ve_prev
                # Skip pit refill or usage greater than 50% of total capacity
                if diff <= 0 or diff > 0.5:
                    ve_prev = ve_curr
                    skip_pit = True
                    continue
                ve_prev = ve_curr
                # Validate usage
                if 0 < prev_diff / diff < 2:  # ignore usage twice higher
                    ve_used = prev_diff
                    break
                ve_used = diff  # in case prev_diff is 0
                prev_diff = diff
        except (AttributeError, TypeError, IndexError, ValueError):
            pass
        output[player_name] = (ve_remaining, ve_used, laps_done)
    return output
