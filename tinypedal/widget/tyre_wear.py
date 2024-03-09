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
Tyre Wear Widget
"""

from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QGridLayout, QLabel

from ..api_control import api
from ..module_info import minfo
from ._base import Overlay

WIDGET_NAME = "tyre_wear"


class Draw(Overlay):
    """Draw widget"""

    def __init__(self, config):
        # Assign base setting
        Overlay.__init__(self, config, WIDGET_NAME)

        # Config font
        font_m = self.get_font_metrics(
            self.config_font(self.wcfg["font_name"], self.wcfg["font_size"]))

        # Config variable
        text_def = "n/a"
        bar_padx = round(self.wcfg["font_size"] * self.wcfg["bar_padding"])
        bar_gap = self.wcfg["bar_gap"]
        self.bar_width = font_m.width * 4

        # Base style
        self.setStyleSheet(
            f"font-family: {self.wcfg['font_name']};"
            f"font-size: {self.wcfg['font_size']}px;"
            f"font-weight: {self.wcfg['font_weight']};"
            f"padding: 0 {bar_padx}px;"
        )

        # Create layout
        layout = QGridLayout()
        layout.setContentsMargins(0,0,0,0)  # remove border
        layout_twear = QGridLayout()
        layout_tdiff = QGridLayout()
        layout_tlaps = QGridLayout()
        layout_tmins = QGridLayout()
        layout_twear.setSpacing(0)
        layout_tdiff.setSpacing(0)
        layout_tlaps.setSpacing(0)
        layout_tmins.setSpacing(0)
        layout.setSpacing(bar_gap)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        column_twear = self.wcfg["column_index_remaining"]
        column_tdiff = self.wcfg["column_index_wear_difference"]
        column_tlaps = self.wcfg["column_index_lifespan_laps"]
        column_tmins = self.wcfg["column_index_lifespan_minutes"]

        # Caption
        if self.wcfg["show_caption"]:
            bar_style_desc = (
                f"color: {self.wcfg['font_color_caption']};"
                f"background: {self.wcfg['bkg_color_caption']};"
                f"font-size: {int(self.wcfg['font_size'] * 0.8)}px;"
            )
            bar_desc_twear = QLabel("tyre wear")
            bar_desc_twear.setAlignment(Qt.AlignCenter)
            bar_desc_twear.setStyleSheet(bar_style_desc)
            layout_twear.addWidget(bar_desc_twear, 0, 0, 1, 0)

            bar_desc_tdiff = QLabel("wear diff")
            bar_desc_tdiff.setAlignment(Qt.AlignCenter)
            bar_desc_tdiff.setStyleSheet(bar_style_desc)
            layout_tdiff.addWidget(bar_desc_tdiff, 0, 0, 1, 0)

            bar_desc_tlaps = QLabel("est. laps")
            bar_desc_tlaps.setAlignment(Qt.AlignCenter)
            bar_desc_tlaps.setStyleSheet(bar_style_desc)
            layout_tlaps.addWidget(bar_desc_tlaps, 0, 0, 1, 0)

            bar_desc_tmins = QLabel("est. mins")
            bar_desc_tmins.setAlignment(Qt.AlignCenter)
            bar_desc_tmins.setStyleSheet(bar_style_desc)
            layout_tmins.addWidget(bar_desc_tmins, 0, 0, 1, 0)

        # Remaining tyre wear
        if self.wcfg["show_remaining"]:
            bar_style_twear = (
                f"color: {self.wcfg['font_color_remaining']};"
                f"background: {self.wcfg['bkg_color_remaining']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_twear_fl = QLabel(text_def)
            self.bar_twear_fl.setAlignment(Qt.AlignCenter)
            self.bar_twear_fl.setStyleSheet(bar_style_twear)
            self.bar_twear_fr = QLabel(text_def)
            self.bar_twear_fr.setAlignment(Qt.AlignCenter)
            self.bar_twear_fr.setStyleSheet(bar_style_twear)
            self.bar_twear_rl = QLabel(text_def)
            self.bar_twear_rl.setAlignment(Qt.AlignCenter)
            self.bar_twear_rl.setStyleSheet(bar_style_twear)
            self.bar_twear_rr = QLabel(text_def)
            self.bar_twear_rr.setAlignment(Qt.AlignCenter)
            self.bar_twear_rr.setStyleSheet(bar_style_twear)

            layout_twear.addWidget(self.bar_twear_fl, 1, 0)
            layout_twear.addWidget(self.bar_twear_fr, 1, 1)
            layout_twear.addWidget(self.bar_twear_rl, 2, 0)
            layout_twear.addWidget(self.bar_twear_rr, 2, 1)

        # Tyre wear difference
        if self.wcfg["show_wear_difference"]:
            bar_style_tdiff = (
                f"color: {self.wcfg['font_color_wear_difference']};"
                f"background: {self.wcfg['bkg_color_wear_difference']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_tdiff_fl = QLabel(text_def)
            self.bar_tdiff_fl.setAlignment(Qt.AlignCenter)
            self.bar_tdiff_fl.setStyleSheet(bar_style_tdiff)
            self.bar_tdiff_fr = QLabel(text_def)
            self.bar_tdiff_fr.setAlignment(Qt.AlignCenter)
            self.bar_tdiff_fr.setStyleSheet(bar_style_tdiff)
            self.bar_tdiff_rl = QLabel(text_def)
            self.bar_tdiff_rl.setAlignment(Qt.AlignCenter)
            self.bar_tdiff_rl.setStyleSheet(bar_style_tdiff)
            self.bar_tdiff_rr = QLabel(text_def)
            self.bar_tdiff_rr.setAlignment(Qt.AlignCenter)
            self.bar_tdiff_rr.setStyleSheet(bar_style_tdiff)

            layout_tdiff.addWidget(self.bar_tdiff_fl, 1, 0)
            layout_tdiff.addWidget(self.bar_tdiff_fr, 1, 1)
            layout_tdiff.addWidget(self.bar_tdiff_rl, 2, 0)
            layout_tdiff.addWidget(self.bar_tdiff_rr, 2, 1)

        # Estimated tyre lifespan in laps
        if self.wcfg["show_lifespan_laps"]:
            bar_style_tlaps = (
                f"color: {self.wcfg['font_color_lifespan_laps']};"
                f"background: {self.wcfg['bkg_color_lifespan_laps']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_tlaps_fl = QLabel(text_def)
            self.bar_tlaps_fl.setAlignment(Qt.AlignCenter)
            self.bar_tlaps_fl.setStyleSheet(bar_style_tlaps)
            self.bar_tlaps_fr = QLabel(text_def)
            self.bar_tlaps_fr.setAlignment(Qt.AlignCenter)
            self.bar_tlaps_fr.setStyleSheet(bar_style_tlaps)
            self.bar_tlaps_rl = QLabel(text_def)
            self.bar_tlaps_rl.setAlignment(Qt.AlignCenter)
            self.bar_tlaps_rl.setStyleSheet(bar_style_tlaps)
            self.bar_tlaps_rr = QLabel(text_def)
            self.bar_tlaps_rr.setAlignment(Qt.AlignCenter)
            self.bar_tlaps_rr.setStyleSheet(bar_style_tlaps)

            layout_tlaps.addWidget(self.bar_tlaps_fl, 1, 0)
            layout_tlaps.addWidget(self.bar_tlaps_fr, 1, 1)
            layout_tlaps.addWidget(self.bar_tlaps_rl, 2, 0)
            layout_tlaps.addWidget(self.bar_tlaps_rr, 2, 1)

        # Estimated tyre lifespan in minutes
        if self.wcfg["show_lifespan_minutes"]:
            bar_style_tmins = (
                f"color: {self.wcfg['font_color_lifespan_minutes']};"
                f"background: {self.wcfg['bkg_color_lifespan_minutes']};"
                f"min-width: {self.bar_width}px;"
            )
            self.bar_tmins_fl = QLabel(text_def)
            self.bar_tmins_fl.setAlignment(Qt.AlignCenter)
            self.bar_tmins_fl.setStyleSheet(bar_style_tmins)
            self.bar_tmins_fr = QLabel(text_def)
            self.bar_tmins_fr.setAlignment(Qt.AlignCenter)
            self.bar_tmins_fr.setStyleSheet(bar_style_tmins)
            self.bar_tmins_rl = QLabel(text_def)
            self.bar_tmins_rl.setAlignment(Qt.AlignCenter)
            self.bar_tmins_rl.setStyleSheet(bar_style_tmins)
            self.bar_tmins_rr = QLabel(text_def)
            self.bar_tmins_rr.setAlignment(Qt.AlignCenter)
            self.bar_tmins_rr.setStyleSheet(bar_style_tmins)

            layout_tmins.addWidget(self.bar_tmins_fl, 1, 0)
            layout_tmins.addWidget(self.bar_tmins_fr, 1, 1)
            layout_tmins.addWidget(self.bar_tmins_rl, 2, 0)
            layout_tmins.addWidget(self.bar_tmins_rr, 2, 1)

        # Set layout
        if self.wcfg["layout"] == 0:
            # Vertical layout
            if self.wcfg["show_remaining"]:
                layout.addLayout(layout_twear, column_twear, 0)
            if self.wcfg["show_wear_difference"]:
                layout.addLayout(layout_tdiff, column_tdiff, 0)
            if self.wcfg["show_lifespan_laps"]:
                layout.addLayout(layout_tlaps, column_tlaps, 0)
            if self.wcfg["show_lifespan_minutes"]:
                layout.addLayout(layout_tmins, column_tmins, 0)
        else:
            # Horizontal layout
            if self.wcfg["show_remaining"]:
                layout.addLayout(layout_twear, 0, column_twear)
            if self.wcfg["show_wear_difference"]:
                layout.addLayout(layout_tdiff, 0, column_tdiff)
            if self.wcfg["show_lifespan_laps"]:
                layout.addLayout(layout_tlaps, 0, column_tlaps)
            if self.wcfg["show_lifespan_minutes"]:
                layout.addLayout(layout_tmins, 0, column_tmins)
        self.setLayout(layout)

        # Last data
        self.checked = False
        self.last_lap_stime = 0  # last lap start time
        self.wear_remain = [0,0,0,0]  # last recorded remaining tyre wear
        self.wear_live = [0,0,0,0]  # live tyre wear update of current lap
        self.wear_last = [0,0,0,0]  # total tyre wear of last lap
        self.wear_laps = [0,0,0,0]  # estimated tyre lifespan in laps
        self.wear_mins = [0,0,0,0]  # estimated tyre lifespan in minutes

        self.last_wear_curr = [None] * 4
        self.last_wear_live = [None] * 4
        self.last_wear_last = [None] * 4
        self.last_wear_laps = [None] * 4
        self.last_wear_mins = [None] * 4

        # Set widget state & start update
        self.set_widget_state()

    @Slot()
    def update_data(self):
        """Update when vehicle on track"""
        if api.state:

            # Reset switch
            if not self.checked:
                self.checked = True

            # Read tyre wear data
            lap_stime = api.read.timing.start()
            lap_etime = api.read.timing.elapsed()
            wear_curr = tuple(map(self.round2decimal, api.read.tyre.wear()))

            # Update tyre wear differences
            self.wear_remain, self.wear_live = zip(
                *map(self.wear_diff, wear_curr, self.wear_remain, self.wear_live))

            if lap_stime != self.last_lap_stime:  # time stamp difference
                self.wear_last = self.wear_live
                self.wear_live = [0,0,0,0]  # reset real time wear
                self.last_lap_stime = lap_stime  # reset time stamp counter

            # Remaining tyre wear
            if self.wcfg["show_remaining"]:
                self.update_wear("fl", wear_curr[0], self.last_wear_curr[0],
                                 self.wcfg["warning_threshold_remaining"])
                self.update_wear("fr", wear_curr[1], self.last_wear_curr[1],
                                 self.wcfg["warning_threshold_remaining"])
                self.update_wear("rl", wear_curr[2], self.last_wear_curr[2],
                                 self.wcfg["warning_threshold_remaining"])
                self.update_wear("rr", wear_curr[3], self.last_wear_curr[3],
                                 self.wcfg["warning_threshold_remaining"])
                self.last_wear_curr = wear_curr

            # Tyre wear differences
            if self.wcfg["show_wear_difference"]:
                # Realtime diff
                if (self.wcfg["show_live_wear_difference"] and
                    lap_etime - lap_stime > self.wcfg["freeze_duration"]):
                    self.update_diff("fl", self.wear_live[0], self.last_wear_live[0],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("fr", self.wear_live[1], self.last_wear_live[1],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("rl", self.wear_live[2], self.last_wear_live[2],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("rr", self.wear_live[3], self.last_wear_live[3],
                                     self.wcfg["warning_threshold_wear"])
                    self.last_wear_live = self.wear_live
                else:
                    # Last lap diff
                    self.update_diff("fl", self.wear_last[0], self.last_wear_last[0],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("fr", self.wear_last[1], self.last_wear_last[1],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("rl", self.wear_last[2], self.last_wear_last[2],
                                     self.wcfg["warning_threshold_wear"])
                    self.update_diff("rr", self.wear_last[3], self.last_wear_last[3],
                                     self.wcfg["warning_threshold_wear"])
                    self.last_wear_last = self.wear_last

            # Estimated tyre lifespan in laps
            if self.wcfg["show_lifespan_laps"]:
                self.wear_laps = tuple(
                    map(self.estimated_laps, wear_curr, self.wear_last, self.wear_live))
                self.update_laps("fl", self.wear_laps[0], self.last_wear_laps[0],
                                 self.wcfg["warning_threshold_laps"])
                self.update_laps("fr", self.wear_laps[1], self.last_wear_laps[1],
                                 self.wcfg["warning_threshold_laps"])
                self.update_laps("rl", self.wear_laps[2], self.last_wear_laps[2],
                                 self.wcfg["warning_threshold_laps"])
                self.update_laps("rr", self.wear_laps[3], self.last_wear_laps[3],
                                 self.wcfg["warning_threshold_laps"])
                self.last_wear_laps = self.wear_laps

            # Estimated tyre lifespan in minutes
            if self.wcfg["show_lifespan_minutes"]:
                self.wear_mins = tuple(
                    map(self.estimated_mins, wear_curr, self.wear_last, self.wear_live))
                self.update_mins("fl", self.wear_mins[0], self.last_wear_mins[0],
                                 self.wcfg["warning_threshold_minutes"])
                self.update_mins("fr", self.wear_mins[1], self.last_wear_mins[1],
                                 self.wcfg["warning_threshold_minutes"])
                self.update_mins("rl", self.wear_mins[2], self.last_wear_mins[2],
                                 self.wcfg["warning_threshold_minutes"])
                self.update_mins("rr", self.wear_mins[3], self.last_wear_mins[3],
                                 self.wcfg["warning_threshold_minutes"])
                self.last_wear_mins = self.wear_mins

        else:
            if self.checked:
                self.checked = False
                self.wear_remain = [0,0,0,0]
                self.wear_live = [0,0,0,0]
                self.wear_last = [0,0,0,0]
                self.wear_laps = [0,0,0,0]
                self.wear_mins = [0,0,0,0]

    # GUI update methods
    def update_wear(self, suffix, curr, last, color):
        """Remaining tyre wear"""
        if curr != last:
            getattr(self, f"bar_twear_{suffix}").setText(self.format_num(curr))
            getattr(self, f"bar_twear_{suffix}").setStyleSheet(
                f"color: {self.color_wear(curr, color)};"
                f"background: {self.wcfg['bkg_color_remaining']};"
                f"min-width: {self.bar_width}px;"
            )

    def update_diff(self, suffix, curr, last, color):
        """Tyre wear differences"""
        if curr != last:
            getattr(self, f"bar_tdiff_{suffix}").setText(f"{curr:.02f}"[:4].rjust(4))
            getattr(self, f"bar_tdiff_{suffix}").setStyleSheet(
                f"color: {self.color_diff(curr, color)};"
                f"background: {self.wcfg['bkg_color_wear_difference']};"
                f"min-width: {self.bar_width}px;"
            )

    def update_laps(self, suffix, curr, last, color):
        """Estimated tyre lifespan in laps"""
        if curr != last:
            getattr(self, f"bar_tlaps_{suffix}").setText(self.format_num(curr))
            getattr(self, f"bar_tlaps_{suffix}").setStyleSheet(
                f"color: {self.color_laps(curr, color)};"
                f"background: {self.wcfg['bkg_color_lifespan_laps']};"
                f"min-width: {self.bar_width}px;"
            )

    def update_mins(self, suffix, curr, last, color):
        """Estimated tyre lifespan in minutes"""
        if curr != last:
            getattr(self, f"bar_tmins_{suffix}").setText(self.format_num(curr))
            getattr(self, f"bar_tmins_{suffix}").setStyleSheet(
                f"color: {self.color_mins(curr, color)};"
                f"background: {self.wcfg['bkg_color_lifespan_minutes']};"
                f"min-width: {self.bar_width}px;"
            )

    # Additional methods
    @staticmethod
    def wear_diff(wear_curr, wear_remain, wear_live):
        """Tyre wear differences"""
        if wear_remain < wear_curr:
            wear_remain = wear_curr
        elif wear_remain > wear_curr:
            wear_live += wear_remain - wear_curr
            wear_remain = wear_curr
        return wear_remain, wear_live

    @staticmethod
    def estimated_laps(wear_curr, wear_last, wear_live):
        """Estimated tyre lifespan in laps

        = remaining / last lap wear"""
        if wear_live > wear_last > 0:
            return min(wear_curr / wear_live, 999)
        if wear_last > 0:
            return min(wear_curr / wear_last, 999)
        return 999

    @staticmethod
    def estimated_mins(wear_curr, wear_last, wear_live):
        """Estimated tyre lifespan in minutes

        = remaining / last lap wear * est laptime / 60"""
        if wear_live > wear_last > 0:
            return min(wear_curr / wear_live * minfo.delta.lapTimeEstimated / 60, 999)
        if wear_last > 0:
            if minfo.delta.isValidLap:  # last laptime is valid
                return min(wear_curr / wear_last * minfo.delta.lapTimeLast / 60, 999)
            if minfo.delta.lapTimeBest > 0:  # use best laptime if available
                return min(wear_curr / wear_last * minfo.delta.lapTimeBest / 60, 999)
        return 999

    @staticmethod
    def round2decimal(value):
        """Round 2 decimal"""
        return round(value * 100, 2)

    @staticmethod
    def format_num(value):
        """Format number"""
        if value > 99.9:
            return f"{value:.0f}"
        return f"{value:.01f}"

    def color_wear(self, tyre_wear, threshold):
        """Warning color for remaining tyre"""
        if tyre_wear <= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_remaining"]

    def color_diff(self, tyre_wear, threshold):
        """Warning color for tyre wear differences"""
        if tyre_wear >= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_wear_difference"]

    def color_laps(self, tyre_wear, threshold):
        """Warning color for estimated tyre lifespan laps"""
        if tyre_wear <= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_lifespan_laps"]

    def color_mins(self, tyre_wear, threshold):
        """Warning color for estimated tyre lifespan minutes"""
        if tyre_wear <= threshold:
            return self.wcfg["font_color_warning"]
        return self.wcfg["font_color_lifespan_minutes"]
