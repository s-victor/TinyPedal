#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022-2024 TinyPedal developers, see contributors.md file
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
import time
import threading
import json
import shutil
from dataclasses import dataclass

from .const import APP_NAME, PLATFORM, PATH_GLOBAL
from .setting_validator import PresetValidator
from . import regex_pattern as rxp
from . import validator as val

from .template.setting_global import GLOBAL_DEFAULT
from .template.setting_common import COMMON_DEFAULT
from .template.setting_module import MODULE_DEFAULT
from .template.setting_widget import WIDGET_DEFAULT
from .template.setting_classes import CLASSES_DEFAULT
from .template.setting_heatmap import HEATMAP_DEFAULT

logger = logging.getLogger(__name__)
preset_validator = PresetValidator()


@dataclass
class FileName:
    """File name"""
    config: str = "config.json"
    setting: str = "default.json"
    classes: str = "classes.json"
    heatmap: str = "heatmap.json"
    brands: str = "brands.json"
    last_setting: str = "None.json"


class FilePath:
    """File path"""

    def __init__(self):
        self.config: str = PATH_GLOBAL  # reference only, should never change
        self.settings: str = ""
        self.brand_logo: str = ""
        self.delta_best: str = ""
        self.sector_best: str = ""
        self.energy_delta: str = ""
        self.fuel_delta: str = ""
        self.track_map: str = ""

    def update(self, user_path: dict, default_path: dict):
        """Update path variables from global user path dictionary"""
        for key in user_path.keys():
            key_name = key.replace("_path", "")
            # Verify loaded path
            if not val.user_data_path(user_path[key]):
                # Reset to default if invalid
                user_path[key] = default_path[key]
                # Re-verify
                val.user_data_path(user_path[key])
            # Assign path
            setattr(self, key_name, user_path[key])


class Preset:
    """Preset setting"""

    def __init__(self):
        self.config: dict | None = None
        self.setting: dict | None = None
        self.classes: dict | None = None
        self.heatmap: dict | None = None
        self.brands: dict | None = None
        self.brands_logo: list | None = None

    def set_default(self):
        """Set default setting"""
        self.config = GLOBAL_DEFAULT
        self.setting = {**COMMON_DEFAULT, **MODULE_DEFAULT, **WIDGET_DEFAULT}
        self.classes = CLASSES_DEFAULT
        self.heatmap = HEATMAP_DEFAULT
        self.brands = {}
        self.set_platform_default()

    def set_platform_default(self):
        """Set platform default setting"""
        if PLATFORM != "Windows":
            # Global config
            self.config["application"]["show_at_startup"] = True
            self.config["application"]["minimize_to_tray"] = False
            # Compatibility
            self.config["compatibility"]["enable_bypass_window_manager"] = True
            # Global path
            from xdg import BaseDirectory as BD
            for key in self.config["user_path"].keys():
                default_path = self.config["user_path"][key]
                if key in ("settings_path", "brand_logo_path"):
                    self.config["user_path"][key] = BD.save_config_path(APP_NAME, default_path)
                else:
                    self.config["user_path"][key] = BD.save_data_path(APP_NAME, default_path)


class Setting:
    """Overlay setting"""

    def __init__(self):
        self.is_saving = False
        self._save_delay = 0
        self._save_queue = set()

        self.filename = FileName()
        self.default = Preset()
        self.default.set_default()
        self.user = Preset()
        self.path = FilePath()

        self.app_loaded = False  # set to true after app main window fully loaded
        self.last_detected_sim = None

    def get_primary_preset_name(self, sim_name: str) -> str:
        """Get primary preset name and verify"""
        preset_name = self.primary_preset.get(sim_name, "")
        if val.allowed_filename(rxp.CFG_INVALID_FILENAME, preset_name):
            full_preset_name = f"{preset_name}.json"
            if os.path.exists(f"{self.path.settings}{full_preset_name}"):
                return full_preset_name
        return ""

    def load_global(self):
        """Load global setting, should only done once per launch"""
        self.user.config = load_setting_json_file(
            self.filename.config, self.path.config, self.default.config)
        # Assign global path
        self.path.update(self.user.config["user_path"], self.default.config["user_path"])
        # Assign global setting
        self.application = self.user.config["application"]
        self.compatibility = self.user.config["compatibility"]
        self.primary_preset = self.user.config["primary_preset"]
        # Save setting to JSON file
        logger.info("SETTING: %s loaded (global settings)", self.filename.config)
        self.save(0, "config")

    def update_path(self):
        """Update global path, call this if "user_path" changed"""
        old_settings_path = os.path.abspath(self.path.settings)
        self.path.update(self.user.config["user_path"], self.default.config["user_path"])
        new_settings_path = os.path.abspath(self.path.settings)
        # Update preset name if settings path changed
        if new_settings_path != old_settings_path:
            self.filename.setting = f"{self.preset_list[0]}.json"

    def load(self):
        """Load all setting files"""
        self.user.setting = load_setting_json_file(
            self.filename.setting, self.path.settings, self.default.setting)
        # Assign base setting
        self.overlay = self.user.setting["overlay"]
        self.shared_memory_api = self.user.setting["shared_memory_api"]
        self.units = self.user.setting["units"]
        self.filename.last_setting = self.filename.setting
        # Load style JSON file
        self.user.brands = load_style_json_file(
            self.filename.brands, self.path.settings, self.default.brands)
        self.user.classes = load_style_json_file(
            self.filename.classes, self.path.settings, self.default.classes)
        self.user.heatmap = load_style_json_file(
            self.filename.heatmap, self.path.settings, self.default.heatmap)
        self.user.brands_logo = load_brands_logo_list(self.path.brand_logo)
        # Save setting to JSON file
        logger.info("SETTING: %s loaded (user preset)", self.filename.last_setting)
        self.save(0)

    @property
    def preset_list(self) -> list[str]:
        """Load user preset JSON filename list, sort by modified date in descending order

        Returns:
            JSON filename (without file extension) list.
        """
        gen_cfg_list = (
            (os.path.getmtime(f"{self.path.settings}{_filename}"), _filename[:-5])
            for _filename in os.listdir(self.path.settings)
            if _filename.lower().endswith(".json")
        )
        valid_cfg_list = [
            _filename[1] for _filename in sorted(gen_cfg_list, reverse=True)
            if val.allowed_filename(rxp.CFG_INVALID_FILENAME, _filename[1])
        ]
        if valid_cfg_list:
            return valid_cfg_list
        return ["default"]

    def create(self):
        """Create default setting"""
        self.user.setting = copy_setting(self.default.setting)

    def save(self, delay: int = 66, filetype: str = "setting"):
        """Save trigger, limit to one save operation for a given period.

        Args:
            count:
                Set time delay(count) that can be refreshed before start saving thread.
                Default is roughly one sec delay, use 0 for instant saving.
            filetype:
                Available type: "config", "setting", "brands", "classes", "heatmap".
        """
        self._save_delay = delay
        self._save_queue.add(filetype)

        if filetype == "config":  # save to global config path
            filepath = self.path.config
        else:  # save to settings (preset) path
            filepath = self.path.settings

        if not self.is_saving:
            self.is_saving = True
            threading.Thread(
                target=self.__saving,
                args=(
                    filetype,
                    getattr(self.filename, filetype),
                    filepath,
                    getattr(self.user, filetype)
                )
            ).start()

    def __saving(self, filetype: str, filename: str, filepath: str, dict_user: dict):
        """Saving thread"""
        attempts = max_attempts = max(self.application["maximum_saving_attempts"], 3)

        # Update save delay
        while self._save_delay > 0:
            self._save_delay -= 1
            time.sleep(0.01)

        # Start saving attempts
        timer_start = time.perf_counter()
        backup_old_json_file(filename, filepath)

        while attempts > 0:
            save_json_file(filename, filepath, dict_user)
            if verify_json_file(filename, filepath, dict_user):
                break
            attempts -= 1
            logger.error("SETTING: failed saving, %s attempt(s) left", attempts)
            time.sleep(0.05)
        timer_end = round((time.perf_counter() - timer_start) * 1000)

        # Finalize
        if attempts > 0:
            logger.info(
                "SETTING: %s saved (took %sms, %s/%s attempts)",
                filename, timer_end, max_attempts - attempts, attempts)
        else:
            restore_old_json_file(filename, filepath)
            logger.info(
                "SETTING: %s failed saving (took %sms, %s/%s attempts)",
                filename, timer_end, max_attempts - attempts, attempts)
        delete_old_json_file(filename, filepath)

        self._save_queue.discard(filetype)
        self.is_saving = False

        # Run next task in save queue if any
        for save_task in self._save_queue:
            self.save(0, save_task)
            break


def save_json_file(filename: str, filepath: str, dict_user: dict) -> None:
    """Save setting to json file"""
    with open(f"{filepath}{filename}", "w", encoding="utf-8") as jsonfile:
        json.dump(dict_user, jsonfile, indent=4)


def verify_json_file(filename: str, filepath: str, dict_user: dict) -> bool:
    """Verify saved json file"""
    try:
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            return json.load(jsonfile) == dict_user
    except (FileNotFoundError, ValueError):
        logger.error("SETTING: failed saving verification")
        return False


def backup_invalid_json_file(filename: str, filepath: str) -> None:
    """Backup invalid json file before revert to default"""
    try:
        time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        shutil.copyfile(f"{filepath}{filename}",
                        f"{filepath}{filename[:-5]}-backup {time_stamp}.json")
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed invalid preset backup")


def backup_old_json_file(filename: str, filepath: str) -> None:
    """Backup old json file before saving"""
    try:
        shutil.copyfile(f"{filepath}{filename}",
                        f"{filepath}{filename}.bak")
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed old preset backup")


def restore_old_json_file(filename: str, filepath: str) -> None:
    """Restore old json file if saving failed"""
    try:
        shutil.copyfile(f"{filepath}{filename}.bak",
                        f"{filepath}{filename}")
    except (FileNotFoundError, OSError):
        logger.error("SETTING: failed old preset restoration")


def delete_old_json_file(filename: str, filepath: str) -> None:
    """Delete old (backup) json file"""
    file_path = f"{filepath}{filename}.bak"
    if os.path.exists(file_path):
        os.remove(file_path)


def load_setting_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load setting json file & verify"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            setting_user = json.load(jsonfile)
        # Verify & assign setting
        setting_user = preset_validator.validate(setting_user, dict_def)
    except (FileNotFoundError, ValueError):
        logger.error("SETTING: %s failed loading, create backup & revert to default", filename)
        backup_invalid_json_file(filename, filepath)
        setting_user = copy_setting(dict_def)
    return setting_user


def load_style_json_file(filename: str, filepath: str, dict_def: dict) -> dict:
    """Load style json file"""
    try:
        # Read JSON file
        with open(f"{filepath}{filename}", "r", encoding="utf-8") as jsonfile:
            style_user = json.load(jsonfile)
    except (FileNotFoundError, ValueError):
        style_user = copy_setting(dict_def)
        # Save to file if not found
        if not os.path.exists(f"{filepath}{filename}"):
            logger.info("SETTING: %s not found, create new default", filename)
            save_json_file(filename, filepath, style_user)
        else:
            logger.error("SETTING: %s failed loading, fall back to default", filename)
    return style_user


def load_brands_logo_list(filepath: str) -> list[str]:
    """Load brands logo list"""
    return [
        _filename[:-4] for _filename in os.listdir(filepath)
        if _filename.lower().endswith(".png")
        and os.path.getsize(f"{filepath}{_filename}") < 1024000]


def copy_setting(dict_user: dict) -> dict:
    """Copy setting"""
    for item in dict_user.values():
        if isinstance(item, dict):
            return {key: item.copy() for key, item in dict_user.items()}
        break
    return dict_user.copy()


# Assign config setting
cfg = Setting()
cfg.load_global()
cfg.filename.setting = f"{cfg.preset_list[0]}.json"
cfg.load()
