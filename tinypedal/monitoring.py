from __future__ import annotations
import logging
import time
import threading
import psutil
from dataclasses import dataclass

from .const import PLATFORM, PATH_SETTINGS, PATH_BRANDLOGO
from .setting_validator import PresetValidator

from .template.setting_application import APPLICATION_DEFAULT
from .template.setting_module import MODULE_DEFAULT
from .template.setting_widget import WIDGET_DEFAULT
from .template.setting_classes import CLASSES_DEFAULT
from .template.setting_heatmap import HEATMAP_DEFAULT

from .setting import cfg

logger = logging.getLogger(__name__)
preset_validator = PresetValidator()

def monitor_process(exe_names):
    """
    Monitors processes in real-time and notifies when the specified executable is launched.

    Args:
        exe_name: The name of the executable to monitor.
    """

    while True:
        procs = [proc.name() for proc in psutil.process_iter()]
        try:
            for exe_name in exe_names:
                if exe_name in procs:
                    # set preset and add exe name to detected if it is running
                    if exe_name not in detected:
                        set_preset(exe_name)
                        detected.add(exe_name)
                else:
                    # delete exe name from detected if it is not running
                    if exe_name in detected:
                        detected.discard(exe_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

        time.sleep(1)

    time.sleep(1)  # Adjust the sleep interval as needed

def set_preset(exe_name):
    # set preset according to detected exe
    preset_name = preset_dict[exe_name]
    cfg.filename.setting = f"{preset_name}.json"
    cfg.load()


# {exe_name: preset_name} dictionary
preset_dict = {"Le Mans Ultimate.exe": "Le Mans Ultimate", "rFactor2.exe": "rFactor 2"}

# set of detected game exe
detected = set()

# Create a thread to run the monitoring function in the background
monitor_thread = threading.Thread(target=monitor_process, args=(["rFactor2.exe", "Le Mans Ultimate.exe"],))
monitor_thread.daemon = True
