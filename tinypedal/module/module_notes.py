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
Notes module
"""

from __future__ import annotations

from ._base import DataModule
from ..module_info import minfo
from ..api_control import api
from .. import calculation as calc
from ..userfile.track_notes import (
    load_notes_file,
    parse_csv_notes_only,
    COLUMN_DISTANCE,
    HEADER_PACE_NOTES,
    HEADER_TRACK_NOTES,
)

MODULE_NAME = "module_notes"


class Realtime(DataModule):
    """Notes data"""

    def __init__(self, config):
        super().__init__(config, MODULE_NAME)

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        userpath_pace_notes = self.cfg.path.pace_notes
        userpath_track_notes = self.cfg.path.track_notes
        output = minfo.notes

        setting_playback = self.cfg.user.setting["pace_notes_playback"]
        position_sync = PositionSync()

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    position_sync.reset()
                    filename_track = api.read.check.track_id()

                    # Load pace notes
                    if setting_playback["enable_manual_file_selector"]:
                        filename_pace = setting_playback["pace_notes_file_name"]
                        filepath_pace = ""
                        fileext = ""
                    else:
                        filename_pace = filename_track
                        filepath_pace = userpath_pace_notes
                        fileext = ".tppn"
                    pace_notes = load_notes_file(
                        filepath=filepath_pace,
                        filename=filename_pace,
                        table_header=HEADER_PACE_NOTES,
                        parser=parse_csv_notes_only,
                        extension=fileext
                    )
                    pace_notes_last_idx = 0
                    pace_notes_end_idx = end_note_index(pace_notes)
                    pace_notes_dist_ref = reference_notes_index(pace_notes)
                    if not pace_notes:
                        output.reset_pace_notes()

                    # Load track notes
                    track_notes = load_notes_file(
                        filepath=userpath_track_notes,
                        filename=filename_track,
                        table_header=HEADER_TRACK_NOTES,
                        parser=parse_csv_notes_only,
                        extension=".tptn"
                    )
                    track_notes_last_idx = 0
                    track_notes_end_idx = end_note_index(track_notes)
                    track_notes_dist_ref = reference_notes_index(track_notes)
                    if not track_notes:
                        output.reset_track_notes()

                # Update position
                pos_synced = position_sync.sync(minfo.delta.lapDistance)

                # Update pace notes
                if pace_notes:
                    pace_pos_curr = pos_synced + setting_playback["pace_notes_global_offset"]
                    pace_notes_curr_idx = calc.binary_search_lower(
                        pace_notes_dist_ref, pace_pos_curr, 0, pace_notes_end_idx)

                    if pace_notes_last_idx != pace_notes_curr_idx:
                        pace_notes_last_idx = pace_notes_curr_idx
                        pace_notes_next_idx = next_note_index(
                            pace_pos_curr, pace_notes_curr_idx, pace_notes_dist_ref)

                        output.paceNoteCurrentIndex = pace_notes_curr_idx
                        output.paceNoteCurrent = pace_notes[pace_notes_curr_idx]
                        output.paceNoteNextIndex = pace_notes_next_idx
                        output.paceNoteNext = pace_notes[pace_notes_next_idx]

                # Update track notes
                if track_notes:
                    track_pos_curr = pos_synced
                    track_notes_curr_idx = calc.binary_search_lower(
                        track_notes_dist_ref, track_pos_curr, 0, track_notes_end_idx)

                    if track_notes_last_idx != track_notes_curr_idx:
                        track_notes_last_idx = track_notes_curr_idx
                        track_notes_next_idx = next_note_index(
                            track_pos_curr, track_notes_curr_idx, track_notes_dist_ref)

                        output.trackNoteCurrentIndex = track_notes_curr_idx
                        output.trackNoteCurrent = track_notes[track_notes_curr_idx]
                        output.trackNoteNextIndex = track_notes_next_idx
                        output.trackNoteNext = track_notes[track_notes_next_idx]

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    output.reset_pace_notes()
                    output.reset_track_notes()


class PositionSync:
    """Position synchronization"""

    def __init__(self, max_diff: float = 200, max_desync: int = 20):
        """
        Args:
            max_diff: max delta position (meters). Exceeding max delta counts as new lap.
            max_desync: max desync counts.
        """
        self._max_diff = max_diff
        self._max_desync = max_desync
        self._desync_count = 0
        self._pos_synced = 0

    def sync(self, pos_curr: float) -> float:
        """Synchronize position

        Args:
            pos_curr: current position (meters).

        Returns:
            Synchronized position (meters).
        """
        if self._pos_synced > pos_curr:
            if (self._desync_count > self._max_desync
                or self._pos_synced - pos_curr > self._max_diff):
                self._desync_count = 0  # reset
                self._pos_synced = pos_curr
            else:
                self._desync_count += 1
        elif self._pos_synced < pos_curr:
            self._pos_synced = pos_curr
            if self._desync_count:
                self._desync_count = 0
        return self._pos_synced

    def reset(self):
        """Reset position & desync count"""
        self._desync_count = 0
        self._pos_synced = 0


def next_note_index(pos_curr: float, curr_idx: int, dist_ref: list) -> int:
    """Next note line index"""
    return (curr_idx + 1) * (pos_curr < dist_ref[-1])


def end_note_index(notes: list) -> int:
    """End note line index"""
    if notes is None:
        return 0
    return len(notes) - 1


def reference_notes_index(notes: list | None) -> list | None:
    """Reference notes index"""
    if notes is None:
        return None
    return [note_line[COLUMN_DISTANCE] for note_line in notes]
