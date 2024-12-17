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
from collections.abc import Callable

from ._base import DataModule
from ..module_info import minfo, NotesInfo
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
        output_pacenotes = minfo.pacenotes
        output_tracknotes = minfo.tracknotes

        setting_playback = self.cfg.user.setting["pace_notes_playback"]
        gen_position_sync = position_sync()

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    gen_position_sync.send(None)
                    track_name = api.read.check.track_id()

                    # Load pace notes
                    pace_notes = load_pace_notes_file(
                        config=setting_playback,
                        filepath=userpath_pace_notes,
                        filename=track_name,
                        table_header=HEADER_PACE_NOTES,
                        parser=parse_csv_notes_only,
                        extension=".tppn",
                    )
                    gen_pacenotes = notes_selector(
                        output=output_pacenotes,
                        dataset=pace_notes,
                    )
                    gen_pacenotes.send(None)

                    # Load track notes
                    track_notes = load_notes_file(
                        filepath=userpath_track_notes,
                        filename=track_name,
                        table_header=HEADER_TRACK_NOTES,
                        parser=parse_csv_notes_only,
                        extension=".tptn"
                    )
                    gen_tracknotes = notes_selector(
                        output=output_tracknotes,
                        dataset=track_notes,
                    )
                    gen_tracknotes.send(None)

                # Update position
                pos_synced = gen_position_sync.send(minfo.delta.lapDistance)

                # Update pace notes
                if pace_notes:
                    gen_pacenotes.send(pos_synced + setting_playback["pace_notes_global_offset"])

                # Update track notes
                if track_notes:
                    gen_tracknotes.send(pos_synced)

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval
                    output_pacenotes.reset()
                    output_tracknotes.reset()


def load_pace_notes_file(
    config: dict, filepath: str, filename: str,
    table_header: tuple, parser: Callable, extension: str):
    """Load pace notes"""
    if config["enable_manual_file_selector"]:
        filepath = ""
        filename = config["pace_notes_file_name"]
        extension = ""
    return load_notes_file(
        filepath=filepath,
        filename=filename,
        table_header=table_header,
        parser=parser,
        extension=extension,
    )


def notes_selector(output: NotesInfo, dataset: list[dict] | None):
    """Notes selector

    Args:
        output: module info.
        dataset: list of notes.
    """
    last_index = 0
    end_index = end_note_index(dataset)
    dist_ref = reference_notes_index(dataset)
    output.reset()  # initial reset before updating

    while True:
        pos_curr = yield
        curr_index = calc.binary_search_lower(dist_ref, pos_curr, 0, end_index)

        if last_index == curr_index:
            continue

        last_index = curr_index
        next_index = next_note_index(pos_curr, curr_index, dist_ref)

        output.currentIndex = curr_index
        output.currentNote = dataset[curr_index]
        output.nextIndex = next_index
        output.nextNote = dataset[next_index]


def position_sync(max_diff: float = 200, max_desync: int = 20):
    """Position synchronization

    Args:
        max_diff: max delta position (meters). Exceeding max delta counts as new lap.
        max_desync: max desync counts.

    Sends:
        pos_curr: current position (meters).

    Yields:
        Synchronized position (meters).
    """
    pos_synced = 0
    desync_count = 0

    while True:
        pos_curr = yield pos_synced
        if pos_curr is None:  # reset
            pos_curr = 0
            pos_synced = 0
            desync_count = 0
            continue
        if pos_synced > pos_curr:
            if desync_count > max_desync or pos_synced - pos_curr > max_diff:
                desync_count = 0  # reset
                pos_synced = pos_curr
            else:
                desync_count += 1
        elif pos_synced < pos_curr:
            pos_synced = pos_curr
            if desync_count:
                desync_count = 0


def next_note_index(pos_curr: float, curr_index: int, dist_ref: list) -> int:
    """Next note line index"""
    return (curr_index + 1) * (pos_curr < dist_ref[-1])


def end_note_index(notes: list | None) -> int:
    """End note line index"""
    if notes is None:
        return 0
    return len(notes) - 1


def reference_notes_index(notes: list | None) -> list | None:
    """Reference notes index"""
    if notes is None:
        return None
    return [note_line[COLUMN_DISTANCE] for note_line in notes]
