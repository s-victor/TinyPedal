from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from ..api_control import api
import asyncio
import logging

logger = logging.getLogger(__name__)

PMC_KEYS = [1, 4, 5, 6, 7, 12, 13, 14, 15, 32]


class PitMenuRemoteControl(QWidget):
    """Remote Pit Menu Control Widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ws_client = None
        self._pit_menu_data = {}

        layout = QVBoxLayout()

        # Control buttons
        control_layout = QHBoxLayout()
        self.button_fetch = QPushButton("📥 Fetch Pit Menu")
        self.button_fetch.clicked.connect(self._fetch_pit_menu)
        self.button_post = QPushButton("📤 Send Pit Menu")
        self.button_post.clicked.connect(self._send_pit_menu)
        control_layout.addWidget(self.button_fetch)
        control_layout.addWidget(self.button_post)
        layout.addLayout(control_layout)

        # PMC value editors as ComboBoxes
        self._combo_boxes = {}
        for key in PMC_KEYS:
            row = QHBoxLayout()
            label = QLabel(f"PMC {key}")
            combo = QComboBox()
            combo.setEnabled(False)  # initially disabled until data fetched
            self._combo_boxes[key] = combo
            row.addWidget(label)
            row.addWidget(combo)
            layout.addLayout(row)

        self.setLayout(layout)
        self._init_ws_client()

    def _init_ws_client(self):
        try:
            info = api._api.info
            self._ws_client = getattr(info, "_ws_client", None)
        except Exception as e:
            logger.error(f"Failed to get WebSocket client: {e}")
            self._ws_client = None

    def _fetch_pit_menu(self):
        if not self._ws_client:
            self._show_error("No WebSocket client available")
            return

        async def callback_wrapper(data):
            try:
                result = data.get("result")
                if not result:
                    raise ValueError("Missing result in pit_menu_data")

                # result expected to be a dict mapping PMC keys (as string) to full objects
                self._pit_menu_data = result

                # Populate combo boxes for each PMC key
                for key in PMC_KEYS:
                    item = self._pit_menu_data.get(str(key))
                    combo = self._combo_boxes.get(key)
                    if not item or not combo:
                        continue

                    combo.clear()
                    settings = item.get("settings", [])
                    # Add the text of each setting to the combo box
                    for setting in settings:
                        combo.addItem(setting.get("text", ""))
                    # Set current selection to currentSetting
                    current_index = item.get("currentSetting", 0)
                    if 0 <= current_index < combo.count():
                        combo.setCurrentIndex(current_index)
                    else:
                        combo.setCurrentIndex(0)
                    combo.setEnabled(True)

                QMessageBox.information(self, "Success", "Pit menu data received and loaded.")
            except Exception as e:
                logger.error(f"Error in GET response: {e}")
                self._show_error("Failed to parse pit menu response")

        # Setup callback for pit_menu_data messages
        self._ws_client._session_callback = lambda msg: (
            callback_wrapper(msg) if isinstance(msg, dict) and msg.get("type") == "pit_menu_data" else None
        )
        self._ws_client._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(self._ws_client._send_json({"type": "fetch_pit_menu"}))
        )

    def _send_pit_menu(self):
        if not self._pit_menu_data:
            self._show_error("No pit menu loaded. Use Fetch first.")
            return

        # Prepare payload as list of full original objects with updated currentSetting only
        modified_payload = []

        for key in PMC_KEYS:
            pmc_item = self._pit_menu_data.get(str(key))
            combo = self._combo_boxes.get(key)
            if not pmc_item or not combo:
                continue

            updated_item = dict(pmc_item)  # shallow copy
            updated_item["currentSetting"] = combo.currentIndex()
            modified_payload.append(updated_item)

        if self._ws_client:
            self._ws_client._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._ws_client._send_json({
                    "type": "send_pit_menu",
                    "payload": modified_payload
                }))
            )
            QMessageBox.information(self, "Sent", "Pit menu POST request sent.")
        else:
            self._show_error("No WebSocket client available")

    def _show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def refresh(self):
        self._init_ws_client()
