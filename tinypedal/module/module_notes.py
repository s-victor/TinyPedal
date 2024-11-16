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
        self.filepath_pace = self.cfg.path.pace_notes
        self.filepath_track = self.cfg.path.track_notes

    def update_data(self):
        """Update module data"""
        reset = False
        update_interval = self.active_interval

        while not self._event.wait(update_interval):
            if self.state.active:

                if not reset:
                    reset = True
                    update_interval = self.active_interval

                    filename_track = api.read.check.track_id()

                    # Load pace notes
                    if self.cfg.user.setting["pace_notes_playback"]["enable_manual_file_selector"]:
                        filename_pace = self.cfg.user.setting["pace_notes_playback"]["pace_notes_file_name"]
                        filepath_pace = ""
                        fileext = ""
                    else:
                        filename_pace = filename_track
                        filepath_pace = self.filepath_pace
                        fileext = ".tppn"
                    pace_notes_last_idx = 0
                    pace_notes = load_notes_file(
                        filepath=filepath_pace,
                        filename=filename_pace,
                        table_header=HEADER_PACE_NOTES,
                        parser=parse_csv_notes_only,
                        extension=fileext
                    )
                    pace_notes_end_idx, pace_notes_dist_ref = reference_notes_index(pace_notes)
                    if not pace_notes:
                        minfo.notes.reset_pace_notes()

                    # Load track notes
                    track_notes_last_idx = 0
                    track_notes = load_notes_file(
                        filepath=self.filepath_track,
                        filename=filename_track,
                        table_header=HEADER_TRACK_NOTES,
                        parser=parse_csv_notes_only,
                        extension=".tptn"
                    )
                    track_notes_end_idx, track_notes_dist_ref = reference_notes_index(track_notes)
                    if not track_notes:
                        minfo.notes.reset_track_notes()

                # Current position
                pos_curr = (
                    minfo.delta.lapDistance
                    + self.cfg.user.setting["pace_notes_playback"]["pace_notes_global_offset"]
                )

                # Update pace notes
                if pace_notes:
                    pace_notes_curr_idx = calc.binary_search_lower(
                        pace_notes_dist_ref, pos_curr, 0, pace_notes_end_idx)
                    pace_notes_next_idx = next_dist_index(
                        pos_curr, pace_notes_curr_idx, pace_notes_dist_ref)

                    if pace_notes_last_idx != pace_notes_curr_idx:
                        pace_notes_last_idx = pace_notes_curr_idx

                        minfo.notes.paceNoteCurrentIndex = pace_notes_curr_idx
                        minfo.notes.paceNoteCurrent = pace_notes[pace_notes_curr_idx]
                        minfo.notes.paceNoteNextIndex = pace_notes_next_idx
                        minfo.notes.paceNoteNext = pace_notes[pace_notes_next_idx]

                # Update track notes
                if track_notes:
                    track_notes_curr_idx = calc.binary_search_lower(
                        track_notes_dist_ref, pos_curr, 0, track_notes_end_idx)
                    track_notes_next_idx = next_dist_index(
                        pos_curr, track_notes_curr_idx, track_notes_dist_ref)

                    if track_notes_last_idx != track_notes_curr_idx:
                        track_notes_last_idx = track_notes_curr_idx

                        minfo.notes.trackNoteCurrentIndex = track_notes_curr_idx
                        minfo.notes.trackNoteCurrent = track_notes[track_notes_curr_idx]
                        minfo.notes.trackNoteNextIndex = track_notes_next_idx
                        minfo.notes.trackNoteNext = track_notes[track_notes_next_idx]

            else:
                if reset:
                    reset = False
                    update_interval = self.idle_interval


def next_dist_index(pos_curr: float, curr_idx: int, dist_ref: list):
    """Next distance index"""
    return (curr_idx + 1) * (pos_curr < dist_ref[-1])


def reference_notes_index(notes: list):
    """Reference notes index"""
    if notes is not None:
        end_idx = len(notes) - 1
        dist_ref = [note_line[COLUMN_DISTANCE] for note_line in notes]
    else:
        end_idx = 0
        dist_ref = None
    return end_idx, dist_ref
