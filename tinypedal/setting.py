#  TinyPedal is an open-source overlay application for racing simulation.
#  Copyright (C) 2022  Xiang
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
Overlay setting
"""

import time
import json
import shutil


class Setting:
    """Overlay setting

    Call load() to load last saved setting before assigning changes.
    """
    filename = "config.json"
    setting_default = {
        "overlay": {
            "fixed_position": False,
            "auto_hide": True,
            "delta_timing": True,
            "hover_color_1": "#FFB913",
            "hover_color_2": "#F6AD00",
        },
        "deltabest": {
            "enable": True,
            "update_delay": 40,
            "position_x": "932",
            "position_y": "228",
            "opacity": 0.9,
            "layout": "0",
            "color_swap": "0",
            "font_name": "consolas",
            "font_size": 17,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color_deltabest": "#000000",
            "bkg_color_deltabest": "#222222",
            "bkg_color_time_gain": "#44FF00",
            "bkg_color_time_loss": "#FF4400",
            "show_delta_bar": True,
            "bar_length_scale": 2.0,
            "bar_height_scale": 1.0,
            "bar_display_range": 2,
        },
        "drs": {
            "enable": True,
            "update_delay": 50,
            "position_x": "1113",
            "position_y": "527",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 30,
            "font_weight": "bold",
            "font_color_activated": "#000000",
            "font_color_allowed": "#000000",
            "font_color_available": "#000000",
            "font_color_not_available": "#000000",
            "bkg_color_activated": "#44FF00",
            "bkg_color_allowed": "#FF4400",
            "bkg_color_available": "#00CCFF",
            "bkg_color_not_available": "#555555",
        },
        "engine": {
            "enable": True,
            "update_delay": 50,
            "position_x": "933",
            "position_y": "526",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color": "#FFFFFF",
            "bkg_color": "#222222",
            "bkg_color_overheat": "#FF2200",
            "overheat_threshold_oil": 110,
            "overheat_threshold_water": 110,
            "show_rpm": True,
            "show_turbo": True,
        },
        "force": {
            "enable": True,
            "update_delay": 50,
            "position_x": "1035",
            "position_y": "526",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color_g_force": "#FFCC00",
            "bkg_color_g_force": "#222222",
            "show_downforce_ratio": True,
            "font_color_downforce": "#000000",
            "bkg_color_downforce": "#DDDDDD",
        },
        "fuel": {
            "enable": True,
            "update_delay": 20,
            "position_x": "1024",
            "position_y": "362",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 0,
            "fuel_unit": "0",
            "font_color_fuel": "#FFFFFF",
            "font_color_consumption": "#555555",
            "font_color_estimate": "#DDDDDD",
            "font_color_pits": "#DDDDDD",
            "bkg_color_fuel": "#009900",
            "bkg_color_consumption": "#FFFFFF",
            "bkg_color_estimate": "#222222",
            "bkg_color_pits": "#555555",
            "bkg_color_low_fuel": "#FF2200",
            "show_caption": True,
            "font_color_caption": "#CCCCCC",
            "bkg_color_caption": "#777777",
        },
        "gear": {
            "enable": True,
            "update_delay": 20,
            "position_x": "933",
            "position_y": "452",
            "opacity": 0.9,
            "layout": "0",
            "speed_unit": "0",
            "font_name": "consolas",
            "font_size": 44,
            "font_weight_gear": "bold",
            "font_weight_gauge": "normal",
            "font_color_gear": "#FFFFFF",
            "font_color_gauge": "#FFFFFF",
            "bkg_color": "#222222",
            "speed_limiter_text": "LIMITER",
            "show_rpm_bar": True,
            "rpm_bar_gap": 2,
            "rpm_bar_height": 7,
            "rpm_bar_edge_height": 2,
            "rpm_safe_multiplier": 0.91,
            "rpm_warn_multiplier": 0.97,
            "bkg_color_rpm_bar": "#FFFFFF",
            "bkg_color_rpm_safe": "#FF2200",
            "bkg_color_rpm_warn": "#00FFFF",
            "bkg_color_rpm_over_rev": "#FF00FF",
        },
        "pedal": {
            "enable": True,
            "update_delay": 20,
            "position_x": "934",
            "position_y": "321",
            "opacity": 0.9,
            "throttle_color": "#77FF00",
            "brake_color": "#FF2200",
            "clutch_color": "#00C2F2",
            "bkg_color": "#222222",
            "bar_length_scale": 1.0,
            "bar_width_scale": 1.0,
            "bar_gap": 2,
            "full_pedal_height": 5,
            "show_ffb_meter": True,
            "ffb_color": "#888888",
            "ffb_clipping_color": "#FFAA00",
        },
        "relative": {
            "enable": True,
            "update_delay": 200,
            "position_x": "564",
            "position_y": "451",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "font_color_player": "#000000",
            "font_color_same_lap": "#FFFFFF",
            "font_color_laps_ahead": "#FF44CC",
            "font_color_laps_behind": "#00CCFF",
            "bkg_color_place": "#333333",
            "bkg_color_player_place": "#DDDDDD",
            "bkg_color_name": "#222222",
            "bkg_color_player_name": "#CCCCCC",
            "bkg_color_gap": "#222222",
            "bkg_color_player_gap": "#CCCCCC",
            "bar_driver_name_width": 18,
            "bar_gap": 1,
            "show_laptime": True,
            "font_color_laptime": "#AAAAAA",
            "bkg_color_laptime": "#2A2A2A",
            "show_class": True,
            "bar_class_name_width": 4,
            "font_color_class": "#FFFFFF",
            "bkg_color_class": "#333333",
        },
        "steering": {
            "enable": True,
            "update_delay": 20,
            "position_x": "1023",
            "position_y": "329",
            "opacity": 0.9,
            "steering_color": "#FFAA00",
            "bkg_color": "#222222",
            "bar_length_scale": 0.5,
            "bar_height_scale": 1.0,
            "bar_edge_width": 2,
            "bar_edge_color": "#FFAA00",
            "show_scale_mark": True,
            "scale_mark_color": "#555555",
        },
        "temperature": {
            "enable": True,
            "update_delay": 50,
            "position_x": "729",
            "position_y": "611",
            "opacity": 0.9,
            "layout": "0",
            "temp_unit": "0",
            "color_swap_tyre": "0",
            "color_swap_brake": "0",
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color_tyre": "#000000",
            "bkg_color_tyre": "#222222",
            "font_color_brake": "#000000",
            "bkg_color_brake": "#222222",
        },
        "timing": {
            "enable": True,
            "update_delay": 50,
            "position_x": "680",
            "position_y": "350",
            "opacity": 0.9,
            "layout": "0",
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color_best": "#000000",
            "font_color_last": "#FFFFFF",
            "font_color_current": "#88FF88",
            "font_color_estimated": "#FFFF88",
            "bkg_color_best": "#FFFFFF",
            "bkg_color_last": "#222222",
            "bkg_color_current": "#222222",
            "bkg_color_estimated": "#222222",
        },
        "wear": {
            "enable": True,
            "update_delay": 50,
            "position_x": "830",
            "position_y": "610",
            "opacity": 0.9,
            "layout": "0",
            "pressure_unit": "0",
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "font_color_pressure": "#CCCCCC",
            "bar_gap": 2,
            "bkg_color_wear": "#222222",
            "bkg_color_pressure": "#222222",
        },
        "weather": {
            "enable": True,
            "update_delay": 200,
            "position_x": "933",
            "position_y": "284",
            "opacity": 0.9,
            "temp_unit": "0",
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "bar_gap": 2,
            "font_color": "#FFFFFF",
            "bkg_color": "#222222",
        },
        "wheel": {
            "enable": True,
            "update_delay": 50,
            "position_x": "799",
            "position_y": "240",
            "opacity": 0.9,
            "font_name": "consolas",
            "font_size": 15,
            "font_weight": "bold",
            "font_color": "#FFFFFF",
            "bar_gap": 2,
            "bkg_color": "#222222",
            "bkg_color_bottoming": "#FF2200",
            "rideheight_offset_front": 0,
            "rideheight_offset_rear": 0,
            "wheelbase": 2800,
            "show_caption": True,
            "font_color_caption": "#CCCCCC",
            "bkg_color_caption": "#777777",
        },
    }

    def __init__(self):
        self.active_widget_list = []  # create active widget list
        self.setting = {}
        self.load()

    def load(self):
        """Load & validate setting"""
        try:
            # Load file
            with open(self.filename, "r", encoding="utf-8") as jsonfile:
                self.setting = json.load(jsonfile)
                # Compare root key
                if self.setting.keys() == self.setting_default.keys():
                    for key in self.setting_default:
                        # Compare sub key
                        if self.setting[key].keys() != self.setting_default[key].keys():
                            self.backup()
                            self.restore()
                            self.save()
                            break
                else:
                    self.backup()
                    self.restore()
                    self.save()
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.restore()
            self.save()

        # Assign sub key setting group
        self.overlay = self.setting["overlay"]
        self.deltabest = self.setting["deltabest"]
        self.drs = self.setting["drs"]
        self.engine = self.setting["engine"]
        self.force = self.setting["force"]
        self.fuel = self.setting["fuel"]
        self.gear = self.setting["gear"]
        self.pedal = self.setting["pedal"]
        self.relative = self.setting["relative"]
        self.steering = self.setting["steering"]
        self.temp = self.setting["temperature"]
        self.timing = self.setting["timing"]
        self.wear = self.setting["wear"]
        self.weather = self.setting["weather"]
        self.wheel = self.setting["wheel"]

    def save(self):
        """Save setting to file"""
        with open(self.filename, "w", encoding="utf-8") as jsonfile:
            json.dump(self.setting, jsonfile, indent=4)

    def restore(self):
        """Restore default setting"""
        self.setting = self.setting_default.copy()

    def backup(self):
        """Backup invalid file"""
        time_stamp = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
        shutil.copy(self.filename, f"config-backup {time_stamp}.json")


class VehicleClass:
    """Vehicle class dictionary"""
    filename = "classes.json"
    classdict_default = {
            "Hypercar": {
                "HP": "#FF4400"
            },
            "LMP1": {
                "LMP1": "#FF00AA"
            },
            "LMP2": {
                "LMP2": "#0088FF"
            },
            "LMP3": {
                "LMP3": "#0044AA"
            },
            "GTE": {
                "GTE": "#00CC44"
            },
            "GT3": {
                "GT3": "#CC6600"
            },
            "DPi": {
                "DPi": "#0044AA"
            },
            "FR3.5_2014": {
                "FR35": "#4488AA"
            },
            "Formula Pro": {
                "FPro": "#FF3300"
            },
            "WriteMatchedNameHere": {
                "ReplaceClassNameHere": "#FFFFFF"
            },
        }

    def __init__(self):
        self.classdict = {}
        self.load()

    def load(self):
        """Load dictionary file"""
        try:
            # Load file
            with open(self.filename, "r", encoding="utf-8") as jsonfile:
                self.classdict = json.load(jsonfile)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # create a default copy if not found
            self.classdict = self.classdict_default.copy()
            self.save()

    def save(self):
        """Save dictionary to file"""
        with open(self.filename, "w", encoding="utf-8") as jsonfile:
            json.dump(self.classdict, jsonfile, indent=4)
