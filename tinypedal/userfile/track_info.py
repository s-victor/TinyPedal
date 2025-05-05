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
Track info preset function
"""

from __future__ import annotations

from ..const_file import ConfigType
from ..setting import cfg


def add_missing_track(track_name: str) -> dict:
    """Add missing track info to tracks preset"""
    cfg.user.tracks[track_name] = {}
    return cfg.user.tracks[track_name]


def load_track_info(track_name: str) -> tuple[float, float, float]:
    """Get track info from tracks preset"""
    track = cfg.user.tracks.get(track_name, None)
    if not isinstance(track, dict):
        track = add_missing_track(track_name)
    return (
        track.get("pit_entry", 0.0),
        track.get("pit_exit", 0.0),
        track.get("pit_speed", 0.0),
    )


def save_track_info(track_name: str, pit_entry: float, pit_exit: float, pit_speed: float) -> None:
    """Save track info to tracks preset"""
    if track_name == "":
        return
    track = cfg.user.tracks.get(track_name, None)
    if not isinstance(track, dict):
        track = add_missing_track(track_name)
    track["pit_entry"] = round(pit_entry, 3)
    track["pit_exit"] = round(pit_exit, 3)
    track["pit_speed"] = round(pit_speed, 3)
    cfg.save(cfg_type=ConfigType.TRACKS)
