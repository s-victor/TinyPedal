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
Setting
"""

from __future__ import annotations
import logging
import os
import threading
from time import sleep
from types import MappingProxyType

from .template.setting_global import GLOBAL_DEFAULT
from .template.setting_common import COMMON_DEFAULT
from .template.setting_module import MODULE_DEFAULT
from .template.setting_widget import WIDGET_DEFAULT
from .template.setting_brakes import BRAKES_DEFAULT
from .template.setting_classes import CLASSES_DEFAULT
from .template.setting_compounds import COMPOUNDS_DEFAULT
from .template.setting_heatmap import HEATMAP_DEFAULT

from . import set_user_data_path
from . import regex_pattern as rxp
from . import validator as val
from .const_app import APP_NAME, PLATFORM, PATH_GLOBAL
from .const_file import ConfigType, FileExt
from .setting_validator import StyleValidator
from .userfile.json_setting import (
    copy_setting,
    load_setting_json_file,
    load_style_json_file,
    save_and_verify_json_file,
)

logger = logging.getLogger(__name__)


class FileName:
    """File name"""

    __slots__ = (
        "config",
        "setting",
        "brakes",
        "brands",
        "classes",
        "compounds",
        "heatmap",
        "last_setting",
    )

    def __init__(self):
        self.config = f"config{FileExt.JSON}"
        self.setting = f"default{FileExt.JSON}"
        self.brakes = f"brakes{FileExt.JSON}"
        self.brands = f"brands{FileExt.JSON}"
        self.classes = f"classes{FileExt.JSON}"
        self.compounds = f"compounds{FileExt.JSON}"
        self.heatmap = f"heatmap{FileExt.JSON}"
        self.last_setting = f"None{FileExt.JSON}"


class FilePath:
    """File path"""

    __slots__ = (
        "config",
        "settings",
        "brand_logo",
        "delta_best",
        "energy_delta",
        "fuel_delta",
        "pace_notes",
        "sector_best",
        "track_map",
        "track_notes",
    )

    def __init__(self):
        # Fixed path, reference only
        self.config = PATH_GLOBAL
        # User setting path
        self.settings = ""
        # User data path
        self.brand_logo = ""
        self.delta_best = ""
        self.energy_delta = ""
        self.fuel_delta = ""
        self.pace_notes = ""
        self.sector_best = ""
        self.track_map = ""
        self.track_notes = ""

    def update(self, user_path: dict, default_path: dict):
        """Update path variables from global user path dictionary"""
        for key in user_path.keys():
            # Reset path if invalid
            if not set_user_data_path(user_path[key]):
                user_path[key] = default_path[key]
                set_user_data_path(user_path[key])
            # Assign path
            setattr(self, key.replace("_path", ""), user_path[key])


class Preset:
    """Preset setting"""

    __slots__ = (
        "config",
        "setting",
        "brakes",
        "brands",
        "classes",
        "compounds",
        "heatmap",
    )

    def set_default(self):
        """Set default setting"""
        self.set_platform_default(GLOBAL_DEFAULT)
        self.config = MappingProxyType(GLOBAL_DEFAULT)
        self.setting = MappingProxyType({**COMMON_DEFAULT, **MODULE_DEFAULT, **WIDGET_DEFAULT})
        self.brakes = MappingProxyType(BRAKES_DEFAULT)
        self.brands = MappingProxyType({})
        self.classes = MappingProxyType(CLASSES_DEFAULT)
        self.compounds = MappingProxyType(COMPOUNDS_DEFAULT)
        self.heatmap = MappingProxyType(HEATMAP_DEFAULT)

    @staticmethod
    def set_platform_default(global_def: dict):
        """Set platform default setting"""
        if PLATFORM != "Windows":
            # Global config
            global_def["application"]["show_at_startup"] = True
            global_def["application"]["minimize_to_tray"] = False
            global_def["compatibility"]["enable_bypass_window_manager"] = True
            # Global path
            from xdg import BaseDirectory as BD

            config_paths = (
                "settings_path",
                "brand_logo_path",
                "pace_notes_path",
                "track_notes_path",
            )
            user_path = global_def["user_path"]
            for key, path in user_path.items():
                if key in config_paths:
                    user_path[key] = BD.save_config_path(APP_NAME, path)
                else:
                    user_path[key] = BD.save_data_path(APP_NAME, path)


class Setting:
    """Overlay setting"""

    __slots__ = (
        "_save_delay",
        "_save_queue",
        "is_saving",
        "filename",
        "default",
        "user",
        "path",
        "application",
        "compatibility",
        "primary_preset",
        "overlay",
        "shared_memory_api",
        "units",
    )

    def __init__(self):
        # States
        self._save_delay = 0
        self._save_queue = {}
        self.is_saving = False
        # Settings
        self.filename = FileName()
        self.default = Preset()
        self.default.set_default()
        self.user = Preset()
        self.path = FilePath()
        # Quick references
        self.application = None
        self.compatibility = None
        self.primary_preset = None
        self.overlay = None
        self.shared_memory_api = None
        self.units = None

    def get_primary_preset_name(self, sim_name: str) -> str:
        """Get primary preset name and verify"""
        preset_name = self.primary_preset.get(sim_name, "")
        if val.allowed_filename(rxp.CFG_INVALID_FILENAME, preset_name):
            full_preset_name = f"{preset_name}{FileExt.JSON}"
            if os.path.exists(f"{self.path.settings}{full_preset_name}"):
                return full_preset_name
        return ""

    def load_global(self):
        """Load global setting, should only done once per launch"""
        self.user.config = load_setting_json_file(
            filename=self.filename.config,
            filepath=self.path.config,
            dict_def=self.default.config,
            is_global=True,
        )
        # Assign global path
        self.path.update(
            user_path=self.user.config["user_path"],
            default_path=self.default.config["user_path"],
        )
        # Assign global setting
        self.application = self.user.config["application"]
        self.compatibility = self.user.config["compatibility"]
        self.primary_preset = self.user.config["primary_preset"]
        self.__set_environ()

    def update_path(self):
        """Update global path, call this if "user_path" changed"""
        old_settings_path = os.path.abspath(self.path.settings)
        self.path.update(
            user_path=self.user.config["user_path"],
            default_path=self.default.config["user_path"],
        )
        new_settings_path = os.path.abspath(self.path.settings)
        # Update preset name if settings path changed
        if new_settings_path != old_settings_path:
            self.filename.setting = f"{self.preset_list[0]}{FileExt.JSON}"

    def load(self):
        """Load all setting files"""
        # Load preset JSON file
        self.user.setting = load_setting_json_file(
            filename=self.filename.setting,
            filepath=self.path.settings,
            dict_def=self.default.setting,
        )
        # Load style JSON file
        self.user.brakes = load_style_json_file(
            filename=self.filename.brakes,
            filepath=self.path.settings,
            dict_def=self.default.brakes,
            validator=StyleValidator.brakes,
        )
        self.user.brands = load_style_json_file(
            filename=self.filename.brands,
            filepath=self.path.settings,
            dict_def=self.default.brands,
        )
        self.user.classes = load_style_json_file(
            filename=self.filename.classes,
            filepath=self.path.settings,
            dict_def=self.default.classes,
            validator=StyleValidator.classes,
        )
        self.user.compounds = load_style_json_file(
            filename=self.filename.compounds,
            filepath=self.path.settings,
            dict_def=self.default.compounds,
            validator=StyleValidator.compounds,
        )
        self.user.heatmap = load_style_json_file(
            filename=self.filename.heatmap,
            filepath=self.path.settings,
            dict_def=self.default.heatmap,
            check_missing=True,
        )
        # Assign base setting
        self.overlay = self.user.setting["overlay"]
        self.shared_memory_api = self.user.setting["shared_memory_api"]
        self.units = self.user.setting["units"]
        self.filename.last_setting = self.filename.setting

    @property
    def preset_list(self) -> list[str]:
        """Load user preset JSON filename list, sort by modified date in descending order

        Returns:
            JSON filename (without file extension) list.
        """
        gen_cfg_list = (
            (os.path.getmtime(f"{self.path.settings}{_filename}"), _filename[:-5])
            for _filename in os.listdir(self.path.settings)
            if _filename.lower().endswith(FileExt.JSON)
        )
        valid_cfg_list = [
            _filename[1]
            for _filename in sorted(gen_cfg_list, reverse=True)
            if val.allowed_filename(rxp.CFG_INVALID_FILENAME, _filename[1])
        ]
        if valid_cfg_list:
            return valid_cfg_list
        return ["default"]

    def create(self):
        """Create default setting"""
        self.user.setting = copy_setting(self.default.setting)

    def save(self, delay: int = 66, cfg_type: str = ConfigType.SETTING, next_task: bool = False):
        """Save trigger, limit to one save operation for a given period.

        Args:
            count:
                Set time delay(count) that can be refreshed before starting saving thread.
                Default is roughly one sec delay, use 0 for instant saving.
            cfg_type:
                Set saving config type.
            next_task:
                Skip adding save task, run next save task in queue.
        """
        if not next_task:
            filename = getattr(self.filename, cfg_type, None)
            if filename is None:  # check if valid file name
                logger.error("USERDATA: invalid config type %s, abort saving", cfg_type)
            elif filename not in self._save_queue:  # add to save queue
                if cfg_type == ConfigType.CONFIG:  # save to global config path
                    filepath = self.path.config
                else:  # save to settings (preset) path
                    filepath = self.path.settings
                dict_user = getattr(self.user, cfg_type)
                self._save_queue[filename] = (filepath, dict_user)

        for queue_filename, queue_filedata in self._save_queue.items():
            break  # get next file in queue
        else:
            return

        self._save_delay = delay

        if not self.is_saving:
            self.is_saving = True
            threading.Thread(
                target=self.__saving,
                args=(queue_filename, *queue_filedata),
            ).start()

    def __saving(self, filename: str, filepath: str, dict_user: dict):
        """Saving thread"""
        # Update save delay
        while self._save_delay > 0:
            self._save_delay -= 1
            sleep(0.01)

        save_and_verify_json_file(
            dict_user=dict_user,
            filename=filename,
            filepath=filepath,
            max_attempts=self.max_saving_attempts,
            abort_without_backup=False,
        )

        self._save_queue.pop(filename, None)
        self.is_saving = False

        # Run next save task in save queue if any
        if self._save_queue:
            self.save(0, next_task=True)

    def __set_environ(self):
        """Set environment variable"""
        if PLATFORM == "Windows":
            if self.compatibility["multimedia_plugin_on_windows"] == "WMF":
                multimedia_plugin = "windowsmediafoundation"
            else:
                multimedia_plugin = "directshow"
            os.environ["QT_MULTIMEDIA_PREFERRED_PLUGINS"] = multimedia_plugin

    @property
    def max_saving_attempts(self) -> int:
        """Get max saving attempts"""
        return max(self.application["maximum_saving_attempts"], 3)


# Assign config setting
cfg = Setting()
