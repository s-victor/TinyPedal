from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from ..api_control import api
import asyncio
import logging

logger = logging.getLogger(__name__)


class PitMenuRemoteControl(QWidget):
    """Remote Pit Menu Control Widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pit_menu_data = []  # List of PMC dicts

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

        # Container for combo boxes keyed by PMC Value
        self._combo_boxes = {}

        self._combo_container = QVBoxLayout()
        layout.addLayout(self._combo_container)

        self.setLayout(layout)

    def get_ws_client(self):
        """Try to get the current WebSocket client dynamically."""
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

                # Assume result is a list of PMC dicts now
                self._pit_menu_data = result

                # Clear old combo boxes
                for i in reversed(range(self._combo_container.count())):
                    item = self._combo_container.itemAt(i)
                    if item is not None:
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                        else:
                            # If it's a layout, remove widgets from it:
                            layout = item.layout()
                            if layout:
                                while layout.count():
                                    child = layout.takeAt(0)
                                    if child.widget():
                                        child.widget().deleteLater()
                        self._combo_container.removeItem(item)

                self._combo_boxes.clear()

                # Create new rows for each PMC item
                for item in self._pit_menu_data:
                    pmc_value = item.get("PMC Value")
                    name = item.get("name", f"PMC {pmc_value}")
                    current_setting = item.get("currentSetting", 0)
                    settings = item.get("settings", [])

                    row = QHBoxLayout()
                    label = QLabel(name)
                    combo = QComboBox()

                    # Fill combo box with setting texts
                    for setting in settings:
                        text = setting.get("text", "Unknown")
                        combo.addItem(text)

                    # Set current index safely
                    if 0 <= current_setting < len(settings):
                        combo.setCurrentIndex(current_setting)
                    else:
                        combo.setCurrentIndex(0)

                    row.addWidget(label)
                    row.addWidget(combo)
                    self._combo_container.addLayout(row)

                    self._combo_boxes[pmc_value] = combo

                QMessageBox.information(self, "Success", "Pit menu data received.")
            except Exception as e:
                logger.error(f"Error in GET response: {e}")
                self._show_error("Failed to parse pit menu response")

        # Hook session callback for pit menu data messages
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

        # Update currentSetting in pit_menu_data from combo boxes
        modified = []
        for item in self._pit_menu_data:
            pmc_value = item.get("PMC Value")
            combo = self._combo_boxes.get(pmc_value)
            if combo:
                item["currentSetting"] = combo.currentIndex()
            modified.append(item)

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
        # This could be used to reset or re-check connection if you want
        pass
