from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QMetaObject
from ..api_control import api
import asyncio
import logging

logger = logging.getLogger(__name__)

PMC_KEYS = [1, 4, 5, 6, 7, 12, 13, 14, 15, 32]
PMC_NAMES = {
    1: "DAMAGE:",
    4: "DRIVER:",
    5: "VIRTUAL ENERGY:",
    6: "FUEL RATIO:",
    7: "TIRES:",
    12: "FRONT LEFT:",
    13: "FRONT RIGHT:",
    14: "REAR LEFT:",
    15: "REAR RIGHT:",
    32: "REPLACE BRAKES",
}


class PitMenuRemoteControl(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ws_client = None
        self._pit_menu_data = []  # Full JSON pit menu list

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

        # PMC combo boxes with labels
        self._combo_boxes = {}
        for key in PMC_KEYS:
            row = QHBoxLayout()
            label = QLabel(PMC_NAMES.get(key, f"PMC {key}"))
            combo = QComboBox()
            combo.setEnabled(False)  # Disabled until data fetched
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
            if self._ws_client is None:
                logger.warning("WebSocket client not found in api._api.info")
        except Exception as e:
            logger.error(f"Failed to get WebSocket client: {e}")
            self._ws_client = None

    def _fetch_pit_menu(self):
        if not self._ws_client:
            self._show_error("No WebSocket client available")
            return

        async def callback_wrapper(data):
            try:
                logger.debug(f"Pit menu data received: {data}")
                result = data.get("result")
                if not result or not isinstance(result, list):
                    raise ValueError("Invalid or missing 'result' in pit_menu_data")

                self._pit_menu_data = result  # Save full list

                def update_ui():
                    logger.debug("Updating UI combos...")
                    # First disable and clear all combos
                    for key in PMC_KEYS:
                        combo = self._combo_boxes.get(key)
                        if combo:
                            combo.clear()
                            combo.setEnabled(False)

                    # Populate combos for each relevant PMC item
                    for item in self._pit_menu_data:
                        pmc_val = item.get("PMC Value")
                        if pmc_val not in PMC_KEYS:
                            continue
                        combo = self._combo_boxes.get(pmc_val)
                        if not combo:
                            continue
                        settings = item.get("settings", [])
                        for setting in settings:
                            combo.addItem(setting.get("text", ""))
                        current_index = item.get("currentSetting", 0)
                        if 0 <= current_index < combo.count():
                            combo.setCurrentIndex(current_index)
                        else:
                            combo.setCurrentIndex(0)
                        combo.setEnabled(True)
                    logger.debug("UI combos updated.")

                    QMessageBox.information(self, "Success", "Pit menu data received and loaded.")

                QMetaObject.invokeMethod(self, update_ui, Qt.QueuedConnection)

            except Exception as e:
                logger.error(f"Error processing pit menu response: {e}")
                self._show_error("Failed to parse pit menu response")

        # Hook callback to intercept pit_menu_data messages
        self._ws_client._session_callback = lambda msg: (
            callback_wrapper(msg) if isinstance(msg, dict) and msg.get("type") == "pit_menu_data" else None
        )
        # Send fetch request safely on websocket event loop thread
        self._ws_client._loop.call_soon_threadsafe(
            lambda: asyncio.create_task(self._ws_client._send_json({"type": "fetch_pit_menu"}))
        )

    def _send_pit_menu(self):
        if not self._pit_menu_data:
            self._show_error("No pit menu loaded. Use Fetch first.")
            return

        # Build modified list by updating currentSetting only for changed combos
        modified_list = []
        for item in self._pit_menu_data:
            pmc_val = item.get("PMC Value")
            if pmc_val in PMC_KEYS:
                combo = self._combo_boxes.get(pmc_val)
                if combo and combo.isEnabled():
                    new_item = dict(item)  # shallow copy
                    new_item["currentSetting"] = combo.currentIndex()
                    modified_list.append(new_item)
                    continue
            # Otherwise keep original item
            modified_list.append(item)

        if self._ws_client:
            self._ws_client._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._ws_client._send_json({
                    "type": "send_pit_menu",
                    "payload": modified_list
                }))
            )
            QMessageBox.information(self, "Sent", "Pit menu POST request sent.")
        else:
            self._show_error("No WebSocket client available")

    def _show_error(self, msg):
        QMessageBox.critical(self, "Error", msg)

    def refresh(self):
        self._init_ws_client()
        if self._ws_client:
            self._fetch_pit_menu()
        else:
            logger.warning("Cannot refresh: WebSocket client not available")