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
Application UI, style
"""

from PySide2.QtGui import QGuiApplication, QPalette
from PySide2.QtWidgets import QApplication


def set_style_palette(color_theme: str):
    """Set style palette"""
    if color_theme == "Dark":
        get_palette_style = palette_dark
    else:
        get_palette_style = palette_light

    palette_color = get_palette_style()
    palatte_roles = get_palatte_role()
    palette = QGuiApplication.palette()
    for color_role, (color_active, color_inactive, color_disabled) in zip(
        palatte_roles, palette_color
    ):
        palette.setColor(QPalette.Active, color_role, color_active)
        palette.setColor(QPalette.Inactive, color_role, color_inactive)
        palette.setColor(QPalette.Disabled, color_role, color_disabled)
    QApplication.setPalette(palette)


def palette_light():
    """Set palette light"""
    return (
        #   Active   Inactive   Disabled
        ("#F0F0F0", "#F0F0F0", "#F0F0F0"),  # Window
        ("#050505", "#050505", "#777777"),  # WindowText
        ("#FFFFFF", "#FFFFFF", "#E8E8E8"),  # Base
        ("#E8E8E8", "#E8E8E8", "#F7F7F7"),  # AlternateBase
        ("#FFFFFF", "#FFFFFF", "#FFFFFF"),  # ToolTipBase
        ("#050505", "#050505", "#050505"),  # ToolTipText
        ("#050505", "#050505", "#050505"),  # PlaceholderText
        ("#050505", "#050505", "#777777"),  # Text
        ("#F0F0F0", "#F0F0F0", "#F0F0F0"),  # Button
        ("#050505", "#050505", "#777777"),  # ButtonText
        ("#FFFFFF", "#FFFFFF", "#FFFFFF"),  # BrightText
        ("#FFFFFF", "#FFFFFF", "#FFFFFF"),  # Light
        ("#E3E3E3", "#E3E3E3", "#F7F7F7"),  # Midlight
        ("#A0A0A0", "#A0A0A0", "#A0A0A0"),  # Dark
        ("#CCCCCC", "#CCCCCC", "#CCCCCC"),  # Mid
        ("#111111", "#111111", "#050505"),  # Shadow
        ("#0088DD", "#555555", "#CCCCCC"),  # Highlight
        ("#FFFFFF", "#F0F0F0", "#555555"),  # HighlightedText
        ("#0088DD", "#0088DD", "#777777"),  # Link
        ("#FF00FF", "#FF00FF", "#777777"),  # LinkVisited
    )


def palette_dark():
    """Set palette dark"""
    return (
        #   Active   Inactive   Disabled
        ("#333333", "#333333", "#303030"),  # Window
        ("#FAFAFA", "#FAFAFA", "#777777"),  # WindowText
        ("#222222", "#222222", "#333333"),  # Base
        ("#2A2A2A", "#2A2A2A", "#282828"),  # AlternateBase
        ("#333333", "#333333", "#333333"),  # ToolTipBase
        ("#FAFAFA", "#FAFAFA", "#FAFAFA"),  # ToolTipText
        ("#FAFAFA", "#FAFAFA", "#FAFAFA"),  # PlaceholderText
        ("#FAFAFA", "#FAFAFA", "#777777"),  # Text
        ("#333333", "#333333", "#303030"),  # Button
        ("#FAFAFA", "#FAFAFA", "#888888"),  # ButtonText
        ("#FFFFFF", "#FFFFFF", "#FFFFFF"),  # BrightText
        ("#AAAAAA", "#AAAAAA", "#484848"),  # Light
        ("#999999", "#999999", "#383838"),  # Midlight
        ("#555555", "#555555", "#181818"),  # Dark
        ("#444444", "#444444", "#222222"),  # Mid
        ("#222222", "#222222", "#0E0E0E"),  # Shadow
        ("#0088DD", "#CCCCCC", "#444444"),  # Highlight
        ("#FAFAFA", "#181818", "#999999"),  # HighlightedText
        ("#22AAFF", "#22AAFF", "#777777"),  # Link
        ("#FF22FF", "#FF22FF", "#777777"),  # LinkVisited
    )


def get_palatte_role():
    """Get palatte color role"""
    return (
        QPalette.Window,
        QPalette.WindowText,
        QPalette.Base,
        QPalette.AlternateBase,
        QPalette.ToolTipBase,
        QPalette.ToolTipText,
        QPalette.PlaceholderText,
        QPalette.Text,
        QPalette.Button,
        QPalette.ButtonText,
        QPalette.BrightText,
        QPalette.Light,
        QPalette.Midlight,
        QPalette.Dark,
        QPalette.Mid,
        QPalette.Shadow,
        QPalette.Highlight,
        QPalette.HighlightedText,
        QPalette.Link,
        QPalette.LinkVisited,
    )


def set_style_window(base_font_pt: int) -> str:
    """Set style window (not affecting overlay)"""
    # Scale font (point size)
    font_pt_item_name = 1.2 * base_font_pt
    font_pt_item_button = 1.05 * base_font_pt
    font_pt_text_browser = 0.9 * base_font_pt
    font_pt_app_name = 1.4 * base_font_pt

    # Set color
    palette = QApplication.palette()
    palette.setCurrentColorGroup(QPalette.Active)
    color_active_text = palette.windowText().color().name()
    color_active_window = palette.window().color().name()
    color_active_highlight_fg = palette.highlightedText().color().name()
    color_active_highlight_bg = palette.highlight().color().name()

    palette.setCurrentColorGroup(QPalette.Inactive)
    color_inactive_highlight_fg = palette.highlightedText().color().name()
    color_inactive_highlight_bg = palette.highlight().color().name()

    palette.setCurrentColorGroup(QPalette.Disabled)
    color_disabled_text = palette.windowText().color().name()
    color_disabled_highlight_fg = palette.highlightedText().color().name()
    color_disabled_highlight_bg = palette.highlight().color().name()

    style = f"""
        /* Misc */
        QSizeGrip {{
            image: none;
            width: 4px;
        }}
        QToolTip {{
            color: {color_active_text};
            background: {color_active_window};
            border: 1px solid {color_disabled_text};
        }}

        /* Main status bar */
        AppWindow QStatusBar QPushButton {{
            font-size: {font_pt_text_browser}pt;
            border: none;
            padding: 0.1em 0.4em;
        }}
        AppWindow QStatusBar QPushButton::hover {{
            color: {color_active_highlight_fg};
            background: {color_active_highlight_bg};
        }}

        /* Notify bar */
        NotifyBar QPushButton {{
            font-weight: bold;
            padding: 0.2em;
            border: none;
            color: {color_active_highlight_fg};
        }}
        NotifyBar #notifySpectate {{
            background: #08C;
        }}
        NotifyBar #notifyPacenotes {{
            background: #290;
        }}
        NotifyBar #notifyPresetLocked {{
            background: #777;
        }}

        /* Module list (tab) */
        ModuleList QListView {{
            font-size: {font_pt_item_name}pt;
            outline: none;
        }}
        ModuleList QListView::item {{
            border: none;
            min-height: 1.75em;
        }}
        ModuleList QListView::item:selected,
        ModuleList QListView::item:hover {{
            color: {color_active_text};
            background: transparent;
        }}
        ModuleControlItem QPushButton {{
            font-size: {font_pt_item_button}pt;
            border-radius: 0.2em;
            padding: 0.125em 0.2em;
            margin: 0.25em 0.25em 0.25em 0;
        }}
        ModuleControlItem #buttonConfig {{
            color: {color_disabled_text};
        }}
        ModuleControlItem #buttonToggle {{
            color: {color_disabled_highlight_fg};
            background: {color_disabled_highlight_bg};
            min-width: 1.875em;
        }}
        ModuleControlItem #buttonToggle::checked,
        ModuleControlItem #buttonConfig::checked {{
            color: {color_inactive_highlight_fg};
            background: {color_inactive_highlight_bg};
        }}
        ModuleControlItem #buttonToggle::hover,
        ModuleControlItem #buttonConfig::hover,
        ModuleControlItem #buttonToggle::checked:hover,
        ModuleControlItem #buttonConfig::checked:hover {{
            color: {color_active_highlight_fg};
            background: {color_active_highlight_bg};
        }}

        /* Preset list (tab) */
        PresetList QListView {{
            font-size: {font_pt_item_name}pt;
            outline: none;
        }}
        PresetList QListView::item {{
            border: none;
            min-height: 1.75em;
        }}
        PresetList QListView::item:selected {{
            selection-color: {color_active_highlight_fg};
            background: {color_active_highlight_bg};
        }}
        PresetTagItem QLabel {{
            font-size: {font_pt_item_button}pt;
            color: {color_active_highlight_fg};
            margin: 0.25em 0.25em 0.25em 0;
            border-radius: 0.2em;
        }}
        PresetTagItem QLabel#LMU {{
            background: #F40;
        }}
        PresetTagItem QLabel#RF2 {{
            background: #0AF;
        }}
        PresetTagItem QLabel#LOCKED {{
            background: #777;
        }}

        /* Spectate list (tab) */
        SpectateList QListView {{
            font-size: {font_pt_item_button}pt;
            outline: none;
        }}
        SpectateList QListView::item {{
            min-height: 1.75em;
            border: none;
        }}
        SpectateList QListView::item:selected {{
            selection-color: {color_active_highlight_fg};
            background: {color_active_highlight_bg};
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
        FuelCalculator QLineEdit[readOnly="true"]{{
            background: {color_active_window};
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
