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
Pace notes view & player
"""

import logging

from PySide2.QtCore import Qt, QBasicTimer
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent
from PySide2.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QFrame,
    QCheckBox,
    QComboBox,
    QSlider,
    QDoubleSpinBox,
)

from ..setting import cfg
from ..module_info import minfo
from .. import validator as val
from ..overlay_control import octrl
from ..module_control import mctrl
from ..userfile.track_notes import QFILTER_TPPN, COLUMN_PACENOTE
from ._common import QSS_EDITOR_BUTTON

SOUND_FORMATS = "wav", "mp3", "aac"

logger = logging.getLogger(__name__)


class PaceNotesPlayer(QMediaPlayer):
    """Pace notes player"""

    def __init__(self, config):
        super().__init__()
        self._active_state = octrl.state
        self.mcfg = config

        # Set update timer
        self._update_timer = QBasicTimer()

        # Last data
        self.checked = False
        self.last_notes_index = None
        self.play_queue = []

    def reset_playback(self):
        """Reset"""
        self.checked = False
        self.last_notes_index = None
        self.play_queue.clear()
        self.stop()
        self.setVolume(self.mcfg["pace_notes_sound_volume"])

    def start_playback(self):
        """Start playback"""
        self.reset_playback()
        update_interval = max(
            self.mcfg["update_interval"],
            cfg.application["minimum_update_interval"])
        self._update_timer.start(update_interval, self)
        logger.info("ACTIVE: pace notes sounds playback")

    def stop_playback(self):
        """Stop playback"""
        self.reset_playback()
        self._update_timer.stop()
        logger.info("STOPPED: pace notes sounds playback")

    def timerEvent(self, event):
        """Update when vehicle on track"""
        if self._active_state.active:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Playback
            notes_index = minfo.pacenotes.currentIndex
            if self.last_notes_index != notes_index:
                pace_note = minfo.pacenotes.currentNote.get(COLUMN_PACENOTE, None)
                self.__update_queue(pace_note)
                self.last_notes_index = notes_index

            if self.play_queue:
                self.__play_next_in_queue()

        else:
            if self.checked:
                self.reset_playback()

    def __update_queue(self, pace_note):
        """Update playback queue"""
        if (pace_note is not None
            and len(self.play_queue) < self.mcfg["pace_notes_sound_max_queue"]):
            self.play_queue.append(pace_note)

    def __play_next_in_queue(self):
        """Play next sound in playback queue"""
        # Wait if is playing & not exceeded max duration
        if self.state() == QMediaPlayer.State.PlayingState:
            if self.position() < self.mcfg["pace_notes_sound_max_duration"] * 1000:
                return
        # Play next sound in queue
        pace_note = self.play_queue[0]
        sound_path = self.mcfg["pace_notes_sound_path"]
        sound_format = self.mcfg["pace_notes_sound_format"].strip(".")
        self.setMedia(QMediaContent(f"{sound_path}{pace_note}.{sound_format}"))
        self.play()
        self.play_queue.pop(0)  # remove playing notes from queue


class PaceNotesControl(QWidget):
    """Pace notes control"""

    def __init__(self):
        super().__init__()
        self.mcfg = cfg.user.setting["pace_notes_playback"]
        self.pace_notes_player = PaceNotesPlayer(self.mcfg)

        # Pace notes file selector
        self.checkbox_file = QCheckBox("Manually Select Pace Notes File")
        self.checkbox_file.toggled.connect(self.toggle_selector_state)

        self.file_selector = QLineEdit()
        self.file_selector.setReadOnly(True)
        self.button_openfile = QPushButton("Open")
        self.button_openfile.setStyleSheet(QSS_EDITOR_BUTTON)
        self.button_openfile.clicked.connect(self.set_notes_path)

        # Sound path selector
        label_path = QLabel("Sound File Path:")
        self.path_selector = QLineEdit()
        self.path_selector.setReadOnly(True)
        button_openpath = QPushButton("Open")
        button_openpath.setStyleSheet(QSS_EDITOR_BUTTON)
        button_openpath.clicked.connect(self.set_sound_path)

        # Sound file format
        label_format = QLabel("Sound Format:")
        self.combobox_format = QComboBox()
        self.combobox_format.setEditable(True)
        self.combobox_format.addItems(SOUND_FORMATS)
        button_setformat = QPushButton("Set")
        button_setformat.setStyleSheet(QSS_EDITOR_BUTTON)
        button_setformat.clicked.connect(self.set_playback_setting)

        # Global Offset
        label_offset = QLabel("Global Offset:")
        self.spinbox_offset = QDoubleSpinBox()
        self.spinbox_offset.setRange(-9999, 9999)
        self.spinbox_offset.setSingleStep(1)
        self.spinbox_offset.setDecimals(2)
        self.spinbox_offset.setSuffix("m")
        button_setoffset = QPushButton("Set")
        button_setoffset.setStyleSheet(QSS_EDITOR_BUTTON)
        button_setoffset.clicked.connect(self.set_playback_setting)

        # Max playback duration per sound
        label_max_duration = QLabel("Max Duration:")
        self.spinbox_max_duration = QDoubleSpinBox()
        self.spinbox_max_duration.setRange(0.2, 60)
        self.spinbox_max_duration.setSingleStep(1)
        self.spinbox_max_duration.setDecimals(3)
        self.spinbox_max_duration.setSuffix("s")
        button_setduration = QPushButton("Set")
        button_setduration.setStyleSheet(QSS_EDITOR_BUTTON)
        button_setduration.clicked.connect(self.set_playback_setting)

        # Max playback queue
        label_max_queue = QLabel("Max Queue:")
        self.spinbox_max_queue = QDoubleSpinBox()
        self.spinbox_max_queue.setRange(1, 50)
        self.spinbox_max_queue.setSingleStep(1)
        self.spinbox_max_queue.setDecimals(0)
        button_setqueue = QPushButton("Set")
        button_setqueue.setStyleSheet(QSS_EDITOR_BUTTON)
        button_setqueue.clicked.connect(self.set_playback_setting)

        # Sound volumn slider
        self.label_volume = QLabel("Playback Volume: 0%")
        self.slider_volume = QSlider(Qt.Horizontal)
        self.slider_volume.setRange(0, 100)
        self.slider_volume.valueChanged.connect(self.set_sound_volume)

        # Frame layout
        layout_file = QGridLayout()
        layout_file.setAlignment(Qt.AlignTop)
        layout_file.addWidget(self.checkbox_file, 0, 0, 1, 2)
        layout_file.addWidget(self.file_selector, 1, 0)
        layout_file.addWidget(self.button_openfile, 1, 1)

        layout_file.addWidget(label_path, 2, 0, 1, 2)
        layout_file.addWidget(self.path_selector, 3, 0)
        layout_file.addWidget(button_openpath, 3, 1)

        layout_inner = QGridLayout()
        layout_inner.addWidget(label_format, 0, 0, 1, 2)
        layout_inner.addWidget(self.combobox_format, 1, 0)
        layout_inner.addWidget(button_setformat, 1, 1)
        layout_inner.setColumnStretch(0, 1)
        layout_inner.setColumnStretch(2, 1)

        layout_inner.addWidget(label_offset, 0, 2, 1, 2)
        layout_inner.addWidget(self.spinbox_offset, 1, 2)
        layout_inner.addWidget(button_setoffset, 1, 3)

        layout_inner.addWidget(label_max_duration, 2, 0, 1, 2)
        layout_inner.addWidget(self.spinbox_max_duration, 3, 0)
        layout_inner.addWidget(button_setduration, 3, 1)

        layout_inner.addWidget(label_max_queue, 2, 2, 1, 2)
        layout_inner.addWidget(self.spinbox_max_queue, 3, 2)
        layout_inner.addWidget(button_setqueue, 3, 3)

        layout_setting = QVBoxLayout()
        layout_setting.setContentsMargins(5,5,5,5)
        layout_setting.addLayout(layout_file)
        layout_setting.addLayout(layout_inner)
        layout_setting.addStretch(1)
        layout_setting.addWidget(self.label_volume)
        layout_setting.addWidget(self.slider_volume)

        self.frame_control = QFrame()
        self.frame_control.setFrameShape(QFrame.StyledPanel)
        self.frame_control.setLayout(layout_setting)

        # Button
        self.button_toggle = QPushButton("")
        self.button_toggle.setCheckable(True)
        self.button_toggle.clicked.connect(self.toggle_button_state)

        layout_button = QHBoxLayout()
        layout_button.addWidget(self.button_toggle)

        # Layout
        layout_main = QVBoxLayout()
        layout_main.addWidget(self.frame_control, stretch=1)
        layout_main.addLayout(layout_button)
        self.setLayout(layout_main)
        self.refresh_state()

    def refresh_state(self):
        """Refresh state"""
        self.mcfg = cfg.user.setting["pace_notes_playback"]
        self.pace_notes_player.mcfg = self.mcfg
        self.toggle_selector_state(self.mcfg["enable_manual_file_selector"])
        self.file_selector.setText(self.mcfg["pace_notes_file_name"])
        self.path_selector.setText(self.mcfg["pace_notes_sound_path"])
        self.combobox_format.setEditText(self.mcfg["pace_notes_sound_format"])
        self.spinbox_offset.setValue(self.mcfg["pace_notes_global_offset"])
        self.spinbox_max_duration.setValue(self.mcfg["pace_notes_sound_max_duration"])
        self.spinbox_max_queue.setValue(self.mcfg["pace_notes_sound_max_queue"])
        self.slider_volume.setValue(self.mcfg["pace_notes_sound_volume"])
        self.set_enable_state(self.mcfg["enable"])

    def set_notes_path(self):
        """Set pace notes file path"""
        filepath = self.mcfg["pace_notes_file_name"]
        filename_full = QFileDialog.getOpenFileName(self, dir=filepath, filter=QFILTER_TPPN)[0]
        if not filename_full:
            return
        self.file_selector.setText(filename_full)
        self.pace_notes_player.reset_playback()
        if self.mcfg["pace_notes_file_name"] != filename_full:
            self.mcfg["pace_notes_file_name"] = filename_full
            cfg.save()
            mctrl.reload("module_notes")  # reload path in module notes

    def set_sound_path(self):
        """Set sounds folder path"""
        filepath = self.mcfg["pace_notes_sound_path"]
        filename_full = QFileDialog.getExistingDirectory(self, dir=filepath)
        if not filename_full:
            return
        filename_full = val.relative_path(filename_full)
        self.path_selector.setText(filename_full)
        if self.mcfg["pace_notes_sound_path"] != filename_full:
            self.mcfg["pace_notes_sound_path"] = filename_full
            cfg.save()

    def set_playback_setting(self):
        """Set sound playback setting"""
        sound_format = self.combobox_format.currentText()
        if self.mcfg["pace_notes_sound_format"] != sound_format:
            self.mcfg["pace_notes_sound_format"] = sound_format
            cfg.save()

        offset = self.spinbox_offset.value()
        if self.mcfg["pace_notes_global_offset"] != offset:
            self.mcfg["pace_notes_global_offset"] = offset
            cfg.save()

        max_duration = self.spinbox_max_duration.value()
        if self.mcfg["pace_notes_sound_max_duration"] != max_duration:
            self.mcfg["pace_notes_sound_max_duration"] = max_duration
            cfg.save()

        max_queue = int(self.spinbox_max_queue.value())
        if self.mcfg["pace_notes_sound_max_queue"] != max_queue:
            self.mcfg["pace_notes_sound_max_queue"] = max_queue
            cfg.save()

    def set_sound_volume(self, value: int):
        """Set sound volume"""
        self.label_volume.setText(f"Playback Volume: {value}%")
        if self.mcfg["pace_notes_sound_volume"] != value:
            self.mcfg["pace_notes_sound_volume"] = value
            self.pace_notes_player.setVolume(value)
            cfg.save()

    def toggle_selector_state(self, checked: bool):
        """Toggle file selector state"""
        self.checkbox_file.setChecked(checked)
        self.file_selector.setText(self.mcfg["pace_notes_file_name"])
        if checked:
            self.file_selector.setDisabled(False)
            self.button_openfile.setDisabled(False)
        else:
            self.file_selector.setDisabled(True)
            self.button_openfile.setDisabled(True)
        if self.mcfg["enable_manual_file_selector"] != checked:
            self.mcfg["enable_manual_file_selector"] = checked
            cfg.save()
            mctrl.reload("module_notes")  # reload file in module notes

    def toggle_button_state(self, checked: bool):
        """Toggle button state"""
        self.set_enable_state(checked)
        if self.mcfg["enable"] != checked:
            self.mcfg["enable"] = checked
            cfg.save()

    def set_enable_state(self, enabled: bool):
        """Set pace notes enabled state"""
        if enabled:
            self.button_toggle.setChecked(True)
            self.button_toggle.setText("Enabled Playback")
            self.frame_control.setDisabled(False)
            self.pace_notes_player.start_playback()
        else:
            self.button_toggle.setChecked(False)
            self.button_toggle.setText("Disabled Playback")
            self.frame_control.setDisabled(True)
            self.pace_notes_player.stop_playback()
