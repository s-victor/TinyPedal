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
Pace notes Widget
"""

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay
from ..userfile.track_notes import COLUMN_DISTANCE, COLUMN_PACENOTE, COLUMN_COMMENT

WIDGET_NAME = "pace_notes"
NA = "NOT AVAILABLE"


class Realtime(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        bar_padx = self.set_padding(self.wcfg["font_size"], self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        notes_width = max(int(self.wcfg["pace_notes_width"]), 1)
        comments_width = max(int(self.wcfg["comments_width"]), 1)
        debugging_width = max(int(self.wcfg["debugging_width"]), 1)

        # Base style
        self.setStyleSheet(self.set_qss(
            font_family=self.wcfg["font_name"],
            font_size=self.wcfg["font_size"],
            font_weight=self.wcfg["font_weight"])
        )
        if self.wcfg["show_background"]:
            bg_color_notes = self.wcfg["bkg_color_pace_notes"]
            bg_color_comments = self.wcfg["bkg_color_comments"]
            bg_color_debugging = self.wcfg["bkg_color_debugging"]
        else:
            bg_color_notes = ""
            bg_color_comments = ""
            bg_color_debugging = ""

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.setLayout(layout)

        # Pace notes
        if self.wcfg["show_pace_notes"]:
            bar_style_notes = self.set_qss(
                fg_color=self.wcfg["font_color_pace_notes"],
                bg_color=bg_color_notes
            )
            self.bar_notes = self.set_qlabel(
                text="PACE NOTES",
                style=bar_style_notes,
                width=font_m.width * notes_width + bar_padx,
            )
            self.bar_notes.setAlignment(
                self.set_text_alignment(self.wcfg["pace_notes_text_alignment"])
            )
            self.set_primary_orient(
                target=self.bar_notes,
                column=self.wcfg["column_index_pace_notes"],
            )

        # Comments
        if self.wcfg["show_comments"]:
            bar_style_comments = self.set_qss(
                fg_color=self.wcfg["font_color_comments"],
                bg_color=bg_color_comments
            )
            self.bar_comments = self.set_qlabel(
                text="COMMENTS",
                style=bar_style_comments,
                width=font_m.width * comments_width + bar_padx,
            )
            self.bar_comments.setAlignment(
                self.set_text_alignment(self.wcfg["comments_text_alignment"])
            )
            self.set_primary_orient(
                target=self.bar_comments,
                column=self.wcfg["column_index_comments"],
            )

        # Debugging info
        if self.wcfg["show_debugging"]:
            bar_style_debugging = self.set_qss(
                fg_color=self.wcfg["font_color_debugging"],
                bg_color=bg_color_debugging
            )
            self.bar_debugging = self.set_qlabel(
                text="DEBUGGING",
                style=bar_style_debugging,
                width=font_m.width * debugging_width + bar_padx,
            )
            self.bar_debugging.setAlignment(
                self.set_text_alignment(self.wcfg["debugging_text_alignment"])
            )
            self.set_primary_orient(
                target=self.bar_debugging,
                column=self.wcfg["column_index_debugging"],
            )

        # Last data
        self.last_notes_index = None
        self.last_comments = None
        self.last_debugging = None
        self.last_auto_hide = False

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self.state.active:

            if self.wcfg["auto_hide_if_not_available"]:
                auto_hide = not api.read.vehicle.in_garage() and not minfo.notes.paceNoteCurrent
                self.update_auto_hide(auto_hide, self.last_auto_hide)
                self.last_auto_hide = auto_hide

            if self.wcfg["show_pace_notes"]:
                notes_index = minfo.notes.paceNoteCurrentIndex
                self.update_notes(notes_index, self.last_notes_index)
                self.last_notes_index = notes_index

            if self.wcfg["show_comments"]:
                comments = minfo.notes.paceNoteCurrent.get(COLUMN_COMMENT, NA)
                self.update_comments(comments, self.last_comments)
                self.last_comments = comments

            if self.wcfg["show_debugging"]:
                debugging = minfo.notes.paceNoteCurrent.get(COLUMN_DISTANCE, NA)
                self.update_debugging(debugging, self.last_debugging)
                self.last_debugging = debugging

    # GUI update methods
    def update_notes(self, curr, last):
        """Pace notes"""
        if curr != last:
            text = minfo.notes.paceNoteCurrent.get(COLUMN_PACENOTE, NA)
            self.bar_notes.setText(text)

    def update_comments(self, curr, last):
        """Comments"""
        if curr != last:
            if self.wcfg["enable_comments_line_break"]:
                curr = curr.replace("\\n", "\n")
            self.bar_comments.setText(curr)

    def update_debugging(self, curr, last):
        """Debugging info"""
        if curr != last:
            if curr == NA:
                text = NA
            else:
                text = (
                    f"IDX:{minfo.notes.paceNoteCurrentIndex + 1} "
                    f"POS:{curr:.0f}>>{minfo.notes.paceNoteNext.get(COLUMN_DISTANCE, 0):.0f}m"
                )
            self.bar_debugging.setText(text)

    def update_auto_hide(self, curr, last):
        """Auto hide"""
        if curr != last:
            if self.wcfg["show_pace_notes"]:
                self.toggle_visibility(curr, self.bar_notes)
            if self.wcfg["show_comments"]:
                self.toggle_visibility(curr, self.bar_comments)
            if self.wcfg["show_debugging"]:
                self.toggle_visibility(curr, self.bar_debugging)

    # Additional methods
    def toggle_visibility(self, state, row_bar):
        """Hide row bar if empty data"""
        if state:
            if not row_bar.isHidden():
                row_bar.hide()
        else:
            if row_bar.isHidden():
                row_bar.show()
