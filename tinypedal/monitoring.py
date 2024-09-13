from __future__ import annotations
import logging
import time
import psutil

from .setting_validator import PresetValidator

from .api_control import api
from .setting import cfg

logger = logging.getLogger(__name__)
preset_validator = PresetValidator()

# def monitor_process(exe_names, config_window):

#     # set of detected game exe
#     detected = set()
    
#     while True:
#         procs = [proc.name() for proc in psutil.process_iter()]
#         try:
#             for exe_name in exe_names:
#                 if exe_name in procs:
#                     # set preset and add exe name to detected if it is running
#                     if exe_name not in detected:
#                         set_preset(exe_name)
#                         config_window.preset_tab.refresh_list()  # refresh UI
#                         detected.add(exe_name)
#                 else:
#                     # delete exe name from detected if it is not running
#                     if exe_name in detected:
#                         detected.discard(exe_name)
#         except (psutil.NoSuchProcess, psutil.AccessDenied):
#             pass

#         time.sleep(1)

#     time.sleep(1)  # Adjust the sleep interval as needed

def monitor_process(config_window):
    while True:
        sim_name = api.read.check.sim_name()  # returns "" if no game running

        # Available sim_name: "RF2", "LMU"
        if sim_name:
            # Set preset and assign sim name to last detected if game running
            if sim_name != cfg.last_detected_sim:
                logger.info(f"SETTING: game detected: {cfg.last_detected_sim}")
                set_preset(sim_name)
                cfg.last_detected_sim = sim_name
                config_window.preset_tab.refresh_list()  # refresh UI
        else:
            # Clear detected name if no game found
            if cfg.last_detected_sim:
                cfg.last_detected_sim = None

        time.sleep(1)

def set_preset(sim_name):
    # set preset according to detected exe
    preset_name = cfg.sim_specific_preset[sim_name]
    cfg.filename.setting = f"{preset_name}.json"
    cfg.load()
