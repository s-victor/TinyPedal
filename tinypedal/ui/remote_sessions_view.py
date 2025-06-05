from typing import Callable
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QLineEdit,
    QWidget,
)
from PySide6.QtCore import Qt
from ..setting import cfg
from ..api_control import api
from ._common import UIScaler


class SessionBrowser(QWidget):
    """Widget for browsing and joining active telemetry sessions (via WebSocket)"""

    def __init__(self, parent, notify_toggle: Callable = lambda _: None):
        super().__init__(parent)
        self.notify_toggle = notify_toggle

        # --- Auth key UI ---
        self.input_auth_key = QLineEdit()
        self.input_auth_key.setPlaceholderText("Paste your activation key here")
        self.input_auth_key.setText(cfg.auth_key)

        self.button_set_key = QPushButton("Set Activation Key")
        self.button_set_key.clicked.connect(self.save_auth_key)

        self.label_instruction = QLabel(
            "You need a valid activation key to access remote telemetry.<br>"
            'Get your key by registering here: <a href="https://remote-pedal.spqracing.it/">remote-pedal.spqracing.it</a>'
        )
        self.label_instruction.setOpenExternalLinks(True)
        self.label_instruction.setWordWrap(True)

        self.auth_layout = QVBoxLayout()
        self.auth_layout.addWidget(self.input_auth_key)
        self.auth_layout.addWidget(self.button_set_key)
        self.auth_layout.addWidget(self.label_instruction)

        # --- Session browser UI ---
        self.label_status = QLabel("")

        self.listbox_sessions = QListWidget(self)
        self.listbox_sessions.setAlternatingRowColors(True)
        self.listbox_sessions.itemDoubleClicked.connect(self.join_selected)

        self.button_join = QPushButton("Join")
        self.button_join.clicked.connect(self.join_selected)

        self.button_refresh = QPushButton("Refresh")
        self.button_refresh.clicked.connect(self.refresh_sessions)

        self.button_toggle = QPushButton("")
        self.button_toggle.setCheckable(True)
        self.button_toggle.clicked.connect(self.toggle_remote_connection)
        self.update_toggle_button_text()

        self.session_layout = QVBoxLayout()
        self.session_layout.addWidget(self.label_status)
        self.session_layout.addWidget(self.listbox_sessions)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_join)
        layout_buttons.addWidget(self.button_refresh)
        layout_buttons.addWidget(self.button_toggle)
        layout_buttons.addStretch(1)
        self.session_layout.addLayout(layout_buttons)

        # --- Main layout ---
        self.layout_main = QVBoxLayout()
        self.layout_main.setContentsMargins(UIScaler.pixel(6), UIScaler.pixel(6), UIScaler.pixel(6), UIScaler.pixel(6))
        self.setLayout(self.layout_main)

        self.update_auth_ui()

    def update_auth_ui(self):
        """Show either the key input or the session browser"""
        for i in reversed(range(self.layout_main.count())):
            item = self.layout_main.itemAt(i)
            if isinstance(item, QVBoxLayout):
                continue  # remove only widgets, not layouts
            widget = item.widget()
            if widget:
                widget.setParent(None)

        if not cfg.auth_key.strip():
            self.layout_main.addLayout(self.auth_layout)
        else:
            self.layout_main.addLayout(self.session_layout)
            self.refresh_sessions()

    def save_auth_key(self):
        """Save the entered activation key and reload UI"""
        key = self.input_auth_key.text().strip()
        if key:
            cfg.shared_memory_api["auth_key"] = key
            cfg.save()
            api.restart()
            self.update_auth_ui()

    def refresh_sessions(self):
        """Send session list request over WebSocket"""
        try:
            info = api._api.info
            client = getattr(info, "_ws_client", None)
            if client and hasattr(client, "request_session_list"):
                client.request_session_list(self.update_sessions)
                self.label_status.setText("Requesting session list...")
            else:
                self.label_status.setText("WebSocket client not available.")
        except Exception as e:
            self.label_status.setText(f"Error: {e}")

    def update_sessions(self, sessions: list):
        """Update session list in UI"""
        self.listbox_sessions.clear()
        for sess in sessions:
            name = sess["name"]
            sender = sess.get("sender") or "No sender"
            viewers = sess.get("receivers", 0)
            label = f"{name} — {sender}, {viewers} viewers"
            self.listbox_sessions.addItem(label)
            self.listbox_sessions.item(self.listbox_sessions.count() - 1).setData(256, name)

        self.label_status.setText(f"Found {len(sessions)} active session(s)")

    def join_selected(self):
        """Join selected session"""
        selected_item = self.listbox_sessions.currentItem()
        if not selected_item:
            return

        session_name = selected_item.data(256)
        if not session_name:
            return

        cfg.shared_memory_api["websocket_session"] = session_name
        cfg.save()
        api.restart()
        self.label_status.setText(f"Joined session: <b>{session_name}</b>")

    def toggle_remote_connection(self):
        """Toggle remote connection on/off"""
        current = cfg.shared_memory_api.get("connect_to_remote", False)
        cfg.shared_memory_api["connect_to_remote"] = not current
        cfg.save()
        api.restart()
        self.update_toggle_button_text()
        self.refresh_sessions()

    def update_toggle_button_text(self):
        connected = cfg.shared_memory_api.get("connect_to_remote", False)
        self.button_toggle.setChecked(connected)
        self.button_toggle.setText("Connected" if connected else "Disconnected")

    def refresh(self):
        self.update_auth_ui()
