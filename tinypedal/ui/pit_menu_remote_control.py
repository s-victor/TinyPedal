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
        self._pit_menu_data = {}  # keyed by PMC Value

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

        # Fixed combo boxes for PMC_KEYS
        self._combo_boxes = {}
        self._labels = {}

        for key in PMC_KEYS:
            row = QHBoxLayout()
            label = QLabel(f"PMC {key}")
            combo = QComboBox()
            combo.setEnabled(False)  # Disable until data is fetched

            row.addWidget(label)
            row.addWidget(combo)
            layout.addLayout(row)

            self._combo_boxes[key] = combo
            self._labels[key] = label

        self.setLayout(layout)

    def get_ws_client(self):
        try:
            info = api._api.info
            client = getattr(info, "_ws_client", None)
            if client:
                return client
        except Exception as e:
            logger.error(f"Failed to get WebSocket client: {e}")
        return None

    def _fetch_pit_menu(self):
        ws_client = self.get_ws_client()
        if not ws_client:
            self._show_error("No WebSocket client available")
            return

        async def callback_wrapper(data):
            try:
                result = data.get("result")
                if not result:
                    raise ValueError("Missing result in pit_menu_data")

                # Convert result list to dict keyed by PMC Value
                self._pit_menu_data = {item["PMC Value"]: item for item in result}

                # Update each combo box
                for key in PMC_KEYS:
                    combo = self._combo_boxes.get(key)
                    label = self._labels.get(key)
                    pmc_item = self._pit_menu_data.get(key)

                    if pmc_item:
                        # Update label name
                        label.setText(pmc_item.get("name", f"PMC {key}"))

                        settings = pmc_item.get("settings", [])
                        combo.clear()
                        for setting in settings:
                            combo.addItem(setting.get("text", "Unknown"))

                        current_index = pmc_item.get("currentSetting", 0)
                        if 0 <= current_index < combo.count():
                            combo.setCurrentIndex(current_index)
                        else:
                            combo.setCurrentIndex(0)

                        combo.setEnabled(True)
                    else:
                        # No data for this PMC key: clear and disable
                        label.setText(f"PMC {key} (no data)")
                        combo.clear()
                        combo.setEnabled(False)

                QMessageBox.information(self, "Success", "Pit menu data received.")

            except Exception as e:
                logger.error(f"Error in GET response: {e}")
                self._show_error("Failed to parse pit menu response")

        # Set the callback to intercept pit_menu_data
        ws_client._session_callback = lambda msg: (
            callback_wrapper(msg) if isinstance(msg, dict) and msg.get("type") == "pit_menu_data" else None
        )
        ws_client._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(ws_client._send_json({"type": "fetch_pit_menu"}))
        )

    def _send_pit_menu(self):
        if not self._pit_menu_data:
            self._show_error("No pit menu loaded. Use Fetch first.")
            return

        ws_client = self.get_ws_client()
        if not ws_client:
            self._show_error("No WebSocket client available")
            return

        modified = []
        for key in PMC_KEYS:
            pmc_item = self._pit_menu_data.get(key)
            combo = self._combo_boxes.get(key)

            if pmc_item and combo:
                pmc_item["currentSetting"] = combo.currentIndex()
                modified.append(pmc_item)

        ws_client._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(ws_client._send_json({
                "type": "send_pit_menu",
                "payload": modified
            }))
        )
        QMessageBox.information(self, "Sent", "Pit menu POST request sent.")

    def _show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def refresh(self):
        pass
