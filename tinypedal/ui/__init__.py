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
Application UI
"""


def set_app_style(base_font_pt) -> str:
    """Set APP style"""
    # Scale font (point size)
    font_pt_item_name = 1.2 * base_font_pt
    font_pt_item_button = 1.05 * base_font_pt
    font_pt_text_browser = 0.9 * base_font_pt
    font_pt_app_name = 1.4 * base_font_pt

    style = f"""
        /* Notify bar */
        NotifyBar QPushButton {{
            font-weight: bold;
            padding: 0.2em;
            border: none;
            color: #FFF;
        }}
        NotifyBar #notifySpectate {{
            background: #09C;
        }}
        NotifyBar #notifyPacenotes {{
            background: #290;
        }}
        NotifyBar #notifyPresetLocked {{
            background: #888;
        }}

        /* Module list (tab) */
        ModuleList QListView {{
            outline: none;
        }}
        ModuleList QListView::item {{
            height: 1.75em;
            border: none;
            padding: 0 0.25em;
        }}
        ModuleList QListView::item:selected, QListView::item:hover {{
            background: transparent;
        }}
        ModuleControlItem QLabel {{
            font-size: {font_pt_item_name}pt;
        }}
        ModuleControlItem QPushButton {{
            font-size: {font_pt_item_button}pt;
            border-radius: 0.2em;
            padding: 0.125em 0.2em;
        }}
        ModuleControlItem #buttonToggle {{
            color: #555;
            background: #CCC;
            min-width: 1.875em;
            margin-left: 0.25em;
        }}
        ModuleControlItem #buttonConfig {{
            color: #AAA;
        }}
        ModuleControlItem #buttonToggle::hover, #buttonConfig::hover {{
            color: #FFF;
            background: #F20;
        }}
        ModuleControlItem #buttonToggle::pressed, #buttonConfig::pressed {{
            color: #FFF;
            background: #555;
        }}
        ModuleControlItem #buttonToggle::checked, #buttonConfig::checked {{
            color: #FFF;
            background: #555;
        }}
        ModuleControlItem #buttonToggle::checked:hover, #buttonConfig::checked:hover {{
            color: #FFF;
            background: #F20;
        }}

        /* Preset list (tab) */
        PresetList QListView {{
            font-size: {font_pt_item_name}pt;
            outline: none;
        }}
        PresetList QListView::item {{
            height: 1.75em;
            border: none;
            padding: 0 0.25em;
        }}
        PresetList QListView::item:selected {{
            selection-color: #FFF;
            background: #F20;
        }}
        PresetTagItem QLabel {{
            font-size: {font_pt_item_button}pt;
            color: #FFF;
            margin: 0.25em 0 0.25em 0.25em;
            border-radius: 0.2em;
        }}
        PresetTagItem QLabel#LMU {{
            background: #F20;
        }}
        PresetTagItem QLabel#RF2 {{
            background: #0AF;
        }}
        PresetTagItem QLabel#LOCKED {{
            background: #888;
        }}

        /* Spectate list (tab) */
        SpectateList QListView {{
            font-size: {font_pt_item_button}pt;
            outline: none;
        }}
        SpectateList QListView::item {{
            height: 1.75em;
            border: none;
            padding: 0 0.25em;
        }}
        SpectateList QListView::item:selected {{
            selection-color: #FFF;
            background: #F20;
        }}

        /* Base dialog */
        BaseDialog QStatusBar {{
            font-weight:bold;
        }}
        BaseDialog QTextBrowser {{
            font-size: {font_pt_text_browser}pt;
        }}
        BaseEditor QTableWidget DoubleClickEdit {{
            border: none;
        }}
        About QLabel {{
            font-size: {font_pt_text_browser}pt;
        }}
        About QTextBrowser {{
            border: none;
        }}
        About #labelAppName {{
            font-size: {font_pt_app_name}pt;
        }}
    """
    return style
