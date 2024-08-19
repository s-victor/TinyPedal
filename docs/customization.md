**Note: following guide is updated to match latest released version.**

TinyPedal offers a wide range of customization options for widget & module controls, which can be accessed from corresponding tabs in main window.


# Preset management
TinyPedal stores all customization options in `JSON` format preset files, and can be managed from `Preset` tab in main window.

All `JSON` preset files are located in `TinyPedal\settings` folder. Those `JSON` files can also be manually edited with text editor.

`Right-Click` on a preset name in `Preset` tab opens up a context menu that provides additional preset file management options:

* Duplicate  
    Duplicate selected preset with a new name.

* Rename  
    Rename selected preset with a new name.

* Delete  
    Delete selected preset with confirmation.


## Saving JSON file
TinyPedal automatically saves setting when user makes changes to widget position, or has toggled widget visibility, auto-hide, overlay-lock, etc. Changes will only take effect after `Reload` preset, or clicked `save` or `apply` button in `Config` dialog, or `Restart` APP.


## Backup JSON file
TinyPedal will automatically create backup file with time stamp suffix if old setting file fails to load, and new default `JSON` with same filename will be generated.

A newer released version will auto-update old setting and add new setting after loading. It may still be a good idea to manually backup files before updating.


## Editing JSON file
Starting from version 2.0, TinyPedal provides a new `Config` dialog for easy customization. Manual editing is no longer necessary.

To edit manually, open `JSON` setting file with text editor, then editing `values` on the right side of colon.

Do not modify anything (keys) on the left side of colon (except classes.json & heatmap.json), any changes to those keys will be reverted back to default setting automatically.

If APP fails to launch after editing `JSON`, check for typo error or invalid values; or delete `JSON` to let APP generate a new default file.

If a value is surrounded by quotation marks, make sure not to remove those quotation marks, otherwise may cause error.

Any boolean type value will only accept: `true` or `false` in lowercase.


## Brands preset
**Brands preset is used for displaying brand name that matches specific vehicle name.**

Brands preset can be customized by accessing `Vehicle brand editor` from `Tools` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

`brands.json` file will be generated and saved in `TinyPedal\settings` folder after first time launch of the APP.

To modify brands setting, open `Vehicle brand editor` and edit entries from each rows and columns. Each row represents a vehicle. First column is full vehicle name that must match in-game vehicle name. Second column is brand name.

To import vehicle brand data from `Rest API`, click `Import from` menu, and select either `RF2 Rest API` or `LMU Rest API`. Note, game must be running in order to import from `Rest API`. Newly imported data will be appended on top of existing data, existing data will not be changed.

Alternatively, to import vehicle brand data from vehicle `JSON` file, click `Import from` menu, and select `JSON file`.

    How to manually export vehicle brand data from RF2 Rest API:
    1. Start RF2, then open following link in web browser:
    localhost:5397/rest/race/car
    2. Click "Save" button which saves vehicle data to JSON file.

    How to manually export vehicle brand data from LMU Rest API:
    1. Start LMU, then open following link in web browser:
    localhost:6397/rest/sessions/getAllAvailableVehicles
    2. Click "Save" button which saves vehicle data to JSON file.

    Note: importing feature is experimental. Maximum acceptable JSON file size is limited to "5MB".

To add new brand name, click `Add` button. Note, the editor can auto-detect and fill-in all vehicle names found from current active session, existing data will not be changed.

To sort brand name in orders, click `Sort` button.

To remove a brand name, select a vehicle name and click `Delete` button.

To batch rename brand name, click `Rename` button.

To reset all brands setting to default, click `Reset` button; or manually delete `brands.json` file.


## Classes preset
**Classes preset is used for displaying name & color that matches specific vehicle classes.**

Classes preset can be customized by accessing `Vehicle class editor` from `Tools` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

`classes.json` file will be generated and saved in `TinyPedal\settings` folder after first time launch of the APP.

To modify class setting, open `Vehicle class editor` and edit entries from each rows and columns. Each row represents a vehicle class. First column is full vehicle class name that must match in-game vehicle class name. Second column is abbreviation name. Third column is color (HEX code). Double-click on color to open color dialog.

To add new class, click `Add` button. Note, the editor can auto-detect and fill-in all vehicle classes found from current active session, existing data will not be changed.

To remove a class, click `X` button of a row.

To reset all classes setting to default, click `Reset` button; or manually delete `classes.json` file.


## Heatmap preset
**Heatmap preset is used for displaying color that matches specific value range of telemetry data, such as brake and tyre temperature.**

Heatmap preset can be customized by accessing `Heatmap editor` from `Tools` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

`heatmap.json` file will be generated and saved in `TinyPedal\settings` folder after first time launch of the APP.

To modify heatmap setting, open `Heatmap editor` and edit entries from each rows and columns. Each row represents a target temperature and corresponding color. First column is temperature degree value in Celsius. Second column is corresponding color (HEX code). Double-click on color to open color dialog.

To add temperature, click `Add` button.

To sort temperature list in orders, click `Sort` button.

To remove a temperature, click `X` button of a temperature row.

To select a different heatmap preset, click `drop-down list` at top, and select a preset name. Note: by selecting a different preset, any changes to previously selected heatmap will be saved in cache, and only be saved to file after clicking `Apply` or `Save` Button.

To create a new heatmap preset, click `New` button. Note: only alphabetic characters, numbers, underscores are accepted in preset name, and renaming preset is not supported.

To delete selected heatmap preset, click `Delete` button. Note: built-in presets cannot be deleted.

To reset selected heatmap preset, click `Reset` button. Note: only built-in presets can be reset.

To assign a heatmap preset to specific widget, select corresponding `heatmap name` in widget config dialog.

In case of errors found in `heatmap.json` file, the APP will automatically fall back to built-in default heatmap preset.

To restore all heatmap settings back to default, just delete `heatmap.json` file.


# User files
TinyPedal generates & saves user session data in specific folders. Session data can be reset by accessing `Reset data` submenu from `Overlay` menu in main window; or, delete data file from corresponding folder.


## Deltabest
Deltabest data is stored as `CSV` format (.csv extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.


## Energy delta
Energy delta data is stored as `CSV` format (.energy extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.


## Fuel delta
Fuel delta data is stored as `CSV` format (.fuel extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.


## Sector best
Sector best data is stored as `CSV` format (.sector extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.


## Track map
Track map is stored as `SVG` vector image format (.svg extension) under `TinyPedal\trackmap` folder.

The SVG vector map file contains two coordinate paths:
* First is global x,y position path, used for drawing track map.
* Second is corresponding track distance & elevation path, used for drawing elevation plot.

Each sector position index is also stored in SVG file for finding sector coordinates.


## Brand logo
TinyPedal supports user-defined brand logo image in `PNG` format (.png extension) which is placed under `TinyPedal\brandlogo` folder.

Note: TinyPedal does not provide brand logo image assets, it is up to user to prepare images. Maximum `PNG` file size is limited to `1MB`.

How to prepare brand logo image:  
1. Brand logo image should have all transparent borders cropped. For example, in `GIMP` this can be done by selecting `Image` > `Crop to Content`.
2. Make sure image dimension is not too big, usually around 100 pixel width or height is good enough. Bigger dimension may consume more RAM or exceed maximum supported file size.
3. Save image to `TinyPedal\brandlogo` folder, image filename must match corresponding `brand name` that defined in `Vehicle brand editor`. For cross-platform compatibility, filename matching is set to be case-sensitive, make sure filename has the same upper or lower case as set in `brand name`.
4. `Reload` preset to load newly added brand logo images for displaying in overlay.


# Command line arguments
**Command line arguments can be passed to script or executable to enable additional features.**

    -h, --help
List all available command line arguments.

Usage: `python .\run.py -h` or `.\tinypedal.exe --help`

    -l, --log-level
Set logging output level. Supported values are:
  * `--log-level 0` outputs only warning or error log to `console`.
  * `--log-level 1` outputs all log to `console`.
  * `--log-level 2` outputs all log to both `console` and `tinypedal.log` file.

Log location:
  * On windows, `tinypedal.log` is located under APP root folder.
  * On linux, `tinypedal.log` is located under `/home/.config/TinyPedal/` folder.

Default logging output level is set on `1` if argument is not set.

Usage: `python .\run.py -l 2` or `.\tinypedal.exe --log-level 2`

    -s, --single-instance
Set running mode. `0` allows running multiple instances (copies) of TinyPedal. `1` allows only single instance (default).

To run multiple copies of TinyPedal at same time: `python .\run.py -s 0` or `.\tinypedal.exe --single-instance 0`

Single instance mode saves `pid.log` file in the same folder as `tinypedal.log`, which is used for instance identification.


# General options
**General options can be accessed from main window menu.**

## Common terms and keywords
**These are the commonly used setting terms and keywords.**

    enable
Check whether a widget or module will be loaded at startup.

    update_interval
Set refresh rate for widget or module in milliseconds. A value of `20` means refreshing every 20ms, which equals 50fps. Since most data from sharedmemory plugin is capped at 50fps, and most operation system has a roughly 15ms minimum sleep time, setting value less than `10` has no benefit, and extreme low value may result significant increase of CPU usage.

    idle_update_interval
Set refresh rate for module while idling for conserving resources.

    position_x, position_y
Define widget position on screen in pixels. Those values will be auto updated and saved.

    opacity
Set opacity for entire widget. By default, all widgets have a 90% opacity setting, which equals value `0.9`. Lower value adds more transparency to widget. Acceptable value range in `0.0` to `1.0`. Note, opacity can also be set by adjusting alpha value in `color` options for individual elements.

    bar_gap, inner_gap
Set gap (screen pixel) between elements in a widget, only accept integer, `1` = 1 pixel.

    font_name
Mono type font is highly recommended. To set custom font, write `full font name` inside quotation marks. If a font name is invalid, a default fallback font will be used by program.

    font_size
Set font size, increase or decrease font size will also apply to widget size. Value only accept `integer`, do not put any decimal place.

    font_weight
Acceptable value: `normal` or `bold`.

    enable_auto_font_offset
Automatically adjust font vertical offset based on font geometry for better vertical alignment, and should give good result in most case. This option is enabled by default, and only available to certain widgets. Set `false` to disable.

    font_offset_vertical
Manually set font vertical offset. Default is `0`. Negative value will offset font upward, and position value for downward. This option only takes effect when `enable_auto_font_offset` is set to `false`.

    bar_padding
Set widget edge padding value that multiplies & scales with `font_size`. Default is `0.2` for most widgets. Increase padding value will further increase each element width in widget.

    color
Set color in hexadecimal color codes with alpha value (opacity). The color code format starts with `#`, then follows by two-digit hexadecimal numbers for each channel in the order of `alpha`, `red`, `green`, `blue`. Note, `alpha` is optional and can be omitted. User can select a new color without manual editing, by double-clicking on color entry box in `Config` dialog.

    prefix
Set prefix text that displayed beside corresponding data. Set to `""` to hide prefix text.

    show_caption
Show short caption description on widget.

    column_index
Set order of each info column(or row). Must keep index number unique to each column, otherwise columns may overlap.

    decimal_places
Set amount decimal places to keep.


## Application
**Application options can be accessed from `Window` menu in main window.**

    show_at_startup
Show main window at startup, otherwise hides to tray icon.

    minimize_to_tray
Minimize to tray when user clicks `X` close button.

    remember_position
Remember last window position.


## Overlay
**Overlay options can be accessed from `Overlay` menu in main window, or from tray icon menu.**

    fixed_position
Check whether widget is locked at startup. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.

    auto_hide
Check whether auto hide is enabled. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.

    enable_grid_move
Enable grid-snap effect while moving widget for easy alignment and repositioning.


## Compatibility
**Compatibility options can be accessed from `Config` menu in main window.**

    enable_bypass_window_manager
Set `true` to bypass window manager on X11 system, such as linux. This option does not affect windows system. This option is enabled by default on linux. Note, while this option is enabled, OBS may not be able to capture overlay widgets in streaming on linux.

    enable_translucent_background
Set `false` to disable translucent background.

    enable_window_position_correction
Set `true` to enable main application window position correction, which is used to correct window-off-screen issue with multi-screen. This option is enabled by default.

    global_bkg_color
Sets global background color for all widgets.

Note, global background color will only be visible when `enable_translucent_background` option is disabled or translucent background is not supported. Some widgets with own background setting may override this option.

    grid_move_size
Set grid size for grid move, value in pixel. Default is `8` pixel. Minimum value is limited to `1`.

    minimum_update_interval
Set minimum refresh rate limit for widget and module in milliseconds. This option is used for preventing extremely low refresh rate that may cause performance issues in case user incorrectly sets `update_interval` and `idle_update_interval` values. Default value is `10`, and should not be modified.

    maximum_saving_attempts
Set maximum retry attempts for preset saving. Default value is `10`. Minimum value is limited to `3` maximum attempts. Note, each attempt has a roughly 50ms delay. If all saving attempts failed, saving will be aborted, and old preset file will be restored to avoid preset file corruption.


## Shared memory API
**Shared Memory API options can be accessed from `Config` menu in main window. Some options may only be relevant to certain API.**

    api_name
Set API name for accessing data from supported API.

| API name | Requirement |
|:-:|---|
| rFactor 2 | Requires `rF2 Shared Memory Map Plugin` to work. |
| Le Mans Ultimate | Currently a placehoder, the underlying code uses the same RF2 API which requires `rF2 Shared Memory Map Plugin` to work. |

    access_mode
Set access mode for API. Mode value `0` uses copy access and additional data check to avoid data desynchronized or interruption issues. Mode value `1` uses direct access, which may result data desynchronized or interruption issues. Default mode is copy access.

    process_id
Set process ID string for accessing API from server. Currently this option is only relevant to RF2.

    enable_active_state_override
Set `true` to enable `active state` manual override.

    active_state
This option overrides local player on-track status check, and updates or stops overlay & data processing accordingly. Set `true` to activate state. Set `false` to deactivate state. This option works only when `enable_active_state_override` enabled.

    enable_player_index_override
Set `true` to enable `player index` manual override.

    player_index
Set `player index` override for displaying data from specific player. Valid player index range starts from `0` to max number players minus one, and must not exceed `127`. Set value to `-1` for unspecified player, which can be useful for display general standings and trackmap data (ex. broadcasting). This option works only when `enable_player_index_override` enabled.

    character_encoding
Set character encoding for displaying text in correct encoding. Available encoding: `UTF-8`, `ISO-8859-1`. Default encoding is `UTF-8`, which works best in LMU game. Note, `UTF-8` may not work well for some Latin characters in RF2, try use `ISO-8859-1` instead.


## Units and symbols
**Units and symbols options can be accessed from `Config` menu in main window.**

    distance_unit
2 unit types are available: `Meter`, `Feet`.

    fuel_unit
2 unit types are available: `Liter`, `Gallon`.

    odometer_unit
3 unit types are available: `Kilometer`, `Mile`, `Meter`.

    power_unit
3 unit types are available: `Kilowatt`, `Horsepower`, `Metric Horsepower`.

    speed_unit
3 unit types are available: `KPH`, `MPH`, `m/s`.

    temperature_unit
2 unit types are available: `Celsius`, `Fahrenheit`.

    turbo_pressure_unit
3 unit types are available: `bar`, `psi`, `kPa`.

    tyre_pressure_unit
3 unit types are available: `kPa`, `psi`, `bar`.

    tyre_compound_symbol
Set custom tire compound index letter. One letter corresponds to one compound index. Note: since most vehicle mods don't share a common tire compound types or list order, it is impossible to have a tyre compound letter list that matches every vehicle.


## Global font override
**Global font override options can be accessed from `Config` menu in main window, which allow changing font setting globally for all widgets.**

    Font Name
Select a font name to replace `font_name` setting of all widgets. Default selection is `no change`, which no changes will be applied.

    Font Size Addend
Set a value that will be added (or subtracted if negative) to `font_size` value of all widgets. Default is `0`, which no changes will be applied.

    Font Weight
Set font weight to replace `font_weight` setting of all widgets. Default selection is `no change`, which no changes will be applied.


## Spectate mode
**Spectate mode can be accessed from `Spectate` tab in main window.**

Click `Enabled` or `Disabled` button to toggle spectate mode on & off. Note, spectate mode can also be enabled by setting `enable_player_index_override` option to `true` in `Shared Memory API` config.

While Spectate mode is enabled, `double-click` on a player name in the list to access telemetry data and overlay readings from selected player; alternatively, select a player name and click `Spectate` button. Current spectating player name is displayed on top of player name list.

Select `Anonymous` for unspecified player, which is equivalent to player index `-1` in JSON file.

Click `Refresh` button to manually refresh player name list.


## Fuel calculator
**Fuel calculator can be accessed from `Tools` menu in main window.**

On the left side is calculation panel, which handles `fuel` and `virtual energy` usage calculation and results display.

Fuel value and unit symbol depend on `Fuel Unit` setting from `Units and symbols` config dialog, `L` = liter, `gal` = gallon. Virtual energy unit is `%` = percentage.

On the right side is fuel consumption history table, which lists `lap number`, `lap time`, `fuel consumption`, `virtual energy consumption`, `battery drain`, `battery regen` data from recent sessions.
Invalid lap time or consumption data is highlighted in red.

Click `Reload` button to reload history table and automatically fill in last data to calculator.

Select any `lap time` or `consumption` values from history table and click `Add selected data` button to send value to calculator.

Select multiple values from history table and click `Add selected data` button to calculate average reading of selected values and send to calculator.

    Lap time
Set lap time in `minutes` : `seconds` : `milliseconds` format. Values are automatically carried over between spin boxes when exceeded min or max value range.

    Tank capacity
Set vehicle fuel tank capacity.

    Fuel consumption
Set fuel consumption per lap.

    Energy consumption
Set energy consumption per lap.

    Fuel ratio
Show fuel ratio between fuel and energy consumption.

    Race minutes
Set race length in minutes for time-based race. Note, option is disabled if `Race laps` is set.

    Race laps
Set race length in laps for lap-based race. Note, option is disabled if `Race minutes` is set.

    Formation/Rolling
Set number of formation or rolling start laps.

    Average pit seconds
Set average pit stop time in seconds.

    Total race fuel, Total race energy
Show total required fuel or energy to finish race. First value is raw reading with decimal places, second value behind `≈` sign is rounded up integer reading.

    End stint fuel, End stint energy
Show remaining fuel or energy at the end of stint or race.

    Total Pit stops
Show total number of pit stops required to finish race. First value is raw reading with decimal places, second value behind `≈` sign is rounded up integer reading. Note, sometimes when `Average pit seconds` is set to longer duration, ceiling integer reading may be rounded up `2` units higher than raw reading, this is not an error. For example, it may show `5.978 ≈ 7` instead of `5.978 ≈ 6`, this is because when calculating from `6` pit stops, due to less amount time spent in pit stop compare to `7`, more fuel is required per pit stop which would exceed tank capacity, hence calculator adds 1 more pit stop.

    One less pit stop
Show theoretical fuel or energy consumption in order to make one less pit stop.

    Total laps
Show total laps can run based on `Total race fuel` or `Total race energy` value.

    Total minutes
Show total minutes can run based on `Total race fuel` or `Total race energy` value.

    Starting fuel, Starting energy
Set starting fuel or energy. This value is only used for calculating `Average refueling` or `Average replenishing` per pit stop. Maximum value cannot exceed `Tank capacity` for fuel, or `100%` for energy. If value is set to `0`, `Tank capacity` value will be used as starting fuel for `Average refueling` calculation.

    Average refueling, Average replenishing
Show average refueling or replenishing per pit stop, and display warning color if value exceeds `Tank capacity` (fuel) or `100%` (energy).


# Modules
Modules provide important data that updated in real-time for other widgets. Widgets may stop updating or receiving readings if corresponding modules were turned off. Each module can be configured by accessing `Config` button from `Module` tab in main window.


## Delta
**This module provides deltabest & timing data.**

    module_delta
Enable delta module.

    delta_smoothing_samples
Set number of samples for delta data smoothing calculation using exponential moving average (EMA) method. Value range in `1` to `100`. Higher value results more smoothness, but may lose accuracy. Default is `30` samples. Set to `1` to disable smoothing.

    laptime_pace_samples
Set number of samples for average laptime pace calculation (EMA). Value range in `1` to `20`. Default is `6` samples. Set to `1` to disable averaging. Note, initial laptime pace is always based on player's all time personal best laptime if available. If a new laptime is faster than current laptime pace, it will replace current laptime pace without calculating average. Invalid lap, pit-in/out laps are always excluded from laptime pace calculation.

    laptime_pace_margin
Set additional margin for current laptime that cannot exceed the sum of `laptime pace` and `margin`. This option is used to minimize the impact of unusually slow laptime. Default value is `5` seconds. Minimum value is limited to `0.1`.


## Energy
**This module provides vehicle virtual energy usage data.**

    module_energy
Enable energy module.


## Force
**This module provides vehicle g force, downforce, braking rate data.**

    module_force
Enable force module.

    gravitational_acceleration
Set gravitational acceleration value on earth.

    max_g_force_reset_delay
Set time delay in seconds for resetting max g force reading.

    max_average_g_force_samples
Set amount samples for calculating max average g force. Minimum value is limited to `3`.

    max_average_g_force_difference
Set max average g force difference threshold which compares with the standard deviation calculated from max average g force samples. Default is `0.2` g.

    max_average_g_force_reset_delay
Set time delay in seconds for resetting max average g force. Default is `30` seconds.

    max_braking_rate_reset_delay
Set time delay in seconds for resetting max braking rate. Default is `60` seconds.


## Fuel
**This module provides vehicle fuel usage data.**

    module_fuel
Enable fuel module.


## Hybrid
**This module provides vehicle battery usage & electric motor data.**

    module_hybrid
Enable hybrid module.


## Mapping
**This module records and processes track map data.**

    module_mapping
Enable mapping module.


## Relative
**This module provides vehicle relative & standings data.**

    module_relative
Enable relative module.


## RestAPI
**This module connects to game's Rest API for accessing additional data that is not available through Sharedmemory API.**

    module_restapi
Enable RestAPI module.

    url_host*
Set RF2 or LMU Rest API host address. Default is `localhost`.

    url_port*
Set port for host address. The port value for RF2 is `5397`, and `6397` for LMU.

    connection_timeout
Set connection timeout duration in seconds. Value range in `0.5` to `10`. Default is `1` second.

    connection_retry
Set number of attempts to retry connection. Value range in `0` to `10`. Default is `3` retries.

    connection_retry_delay
Set time delay in seconds to retry connection. Value range in `0` to `60`. Default is `1` second.


## Sectors
**This module provides sectors timing data.**

    module_sectors
Enable sectors module.

    enable_all_time_best_sectors
Calculate sectors timing based on all time best sectors and affects `Sectors Widget` display. This option is enabled by default. Set `false` to calculate sectors timing from current session only. Note, both session best and all time best sectors data are saved no matter the setting.


## Vehicles
**This module provides additional processed vehicles data.**

    module_vehicles
Enable vehicles module.

    lap_difference_ahead_threshold
Lap difference (percentage) threshold for tagging opponents as ahead. Default is `0.9` lap.

    lap_difference_behind_threshold
Lap difference (percentage) threshold for tagging opponents as behind. Default is `0.9` lap.


## Wheels
**This module provides wheel radius and slip ratio data.**

    last_vehicle_info
Last saved vehicle identifier. This option is not for manual editing.

    last_wheel_radius_front, last_wheel_radius_rear
Last saved radius of front and rear wheels. This option is not for manual editing.


# Widgets
Each widget can be configured by accessing `Config` button from `Widget` tab in main window.


## Battery
**This widget displays battery usage info.**

    show_battery_charge
Show percentage available battery charge.

    show_battery_drain
Show percentage battery charge drained in current lap.

    show_battery_regen
Show percentage battery charge regenerated in current lap.

    show_activation_timer
Show electric boost motor activation timer.

    low_battery_threshold
Set percentage threshold for low battery charge warning indicator.

    freeze_duration
Set freeze duration (seconds) for displaying previous lap total drained/regenerated battery charge after crossing finish line. Value range in `0` to `30` seconds. Default is `10` seconds.


## Brake bias
**This widget displays brake bias info.**

    show_front_and_rear
Show both front and rear bias. Default is `false`.

    show_percentage_sign
Set `true` to show percentage sign for brake bias value.

    show_brake_migration
Show real-time brake migration change, as commonly seen in LMH and LMDh classes.

Note, brake migration is calculated based on brake input and brake pressure telemetry data, and is affected by pedal force setting from car setup and electric braking allocation of specific vehicle.

To get accurate brake migration reading, it is necessary for brake pedal to reach fully pressed state for at least once while entering track to recalibrate brake pressure scaling for brake migration calculation. It is normally not required to do manually, as game's auto-hold brake assist is on by default. However if auto-hold brake assist is off, or the APP was reloaded while player was already on track, then it is required to do a full braking for at least once to get accurate brake migration reading.

    electric_braking_allocation
Set allocation for calculating brake migration under different electric braking allocation from specific vehicle. Note, vehicle that has not electric braking, or has disabled regeneration, is not affected by this option. Incorrect allocation value will result wrong brake migration reading from vehicle that has electric braking activated.

Set value to `-1` to enable auto-detection, which automatically checks whether electric braking is activated on either axles while braking, and sets allocation accordingly. This is enabled by default. Note, it may take a few brakes to detect correct allocation.

Set value to `0` to manual override and use front allocation, which is commonly seen in LMH class.

Set value to `1` to manual override and use rear allocation, which is commonly seen in LMDh class.


## Brake performance
**This widget displays brake performance info.**

    show_transient_max_braking_rate
Show transient max braking rate (g) from last braking input, and resets after 3 seconds.

    show_max_braking_rate
Show max braking rate (g), and resets after a set period of time that defined by `max_braking_rate_reset_delay` value in Force Module.

    show_delta_braking_rate
Show max braking rate difference (g) against transient max braking rate, and resets on the next braking.

    show_delta_braking_rate_in_percentage
Show max braking rate difference (g) in percentage (%) instead.

    show_front_wheel_lock_duration, show_rear_wheel_lock_duration
Show front and rear wheel lock duration (seconds) per lap under braking. Duration increases when tyre slip ratio has exceeded `wheel_lock_threshold` value, and resets on first braking input of a new lap.

    wheel_lock_threshold
Set percentage threshold for counting wheel lock duration under braking. `0.3` means 30% of tyre slip ratio.


## Brake pressure
**This widget displays visualized percentage brake pressure info.**


## Brake temperature
**This widget displays brake temperature info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    heatmap_name
Set heatmap preset name that is defined in `heatmap.json` file.

    swap_style
Swap heatmap color between font & background color.

    show_degree_sign
Set `true` to show degree sign for each temperature value.

    leading_zero
Set amount leading zeros for each temperature value. Default is `2`. Minimum value is limited to `1`.

    show_average
Show average brake temperature calculated from a full lap.

    highlight_duration
Set duration (seconds) for highlighting average brake temperature from previous lap after crossing finish line. Default is `5` seconds.


## Cruise
**This widget displays track clock, compass, elevation, odometer info.**

    show_track_clock
Show current in-game clock time of the circuit.

    track_clock_time_scale
Set time multiplier for time-scaled session. Default is `1`, which matches `Time Scale: Normal` setting in-game. Note, this option will only be used if RestAPI module is disabled or Rest API data is not available.

    track_clock_format
Set track clock format string. To show seconds, add `%S`, such as `%H:%M:%S %p`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

    show_compass
Show compass directions with three-figure bearings that matches game's cardinal directions.

    show_elevation
Show elevation difference in game's coordinate system.

    show_odometer
Show odometer that displays total driven distance of local player. 

    meters_driven
This value holds the total distance(meters) that local player has driven. Accept manual editing.


## Damage
**This widget displays visualized vehicle damage info.**

    display_margin
Set display margin in pixels.

    inner_gap
Set body parts inner gap in pixels.

    part_width
Set body parts width in pixels.

    parts_max_width, parts_max_height
Set maximum body parts width, height in pixels.

    show_background
Show widget background.

    show_integrity_reading
Show vehicle body integrity reading in percentage.

    show_inverted_integrity
Invert vehicle body integrity reading.


## Deltabest
**This widget displays deltabest info.**

    layout
2 layouts are available: `0` = delta bar above deltabest text, `1` = delta bar below deltabest text.

    swap_style
Swap time gain & loss color between font & background color.

    deltabest_source
Set lap time source for deltabest display. Available values are: `Best` = all time best lap time, `Session` = session best lap time, `Stint` = stint best lap time, `Last` = last lap time.

    show_delta_bar
Show visualized delta bar.

    bar_length, bar_height
Set delta bar length & height in pixels.

    bar_display_range
Set max display range (gain or loss) in seconds for delta bar, accepts decimal place. Default is `2` seconds.

    delta_display_range
Set max display range (gain or loss) in seconds for delta reading, accepts decimal place. Default is `99.999` seconds.

    freeze_duration
Set freeze duration (seconds) for displaying previous lap time difference against best lap time source after crossing finish line. Value range in `0` to `30` seconds. Default is `3` seconds. Set to `0` to disable.

    show_animated_deltabest
Deltabest display follows delta bar progress.


## Deltabest extended
**This widget displays deltabest info against multiple lap time sources.**

    show_all_time_deltabest
Show deltabest against personal all time best lap time.

    show_session_deltabest
Show deltabest against current personal session best lap time. Note: session deltabest will be reset upon changing session, or reload preset/restart APP.

    show_stint_deltabest
Show deltabest against current personal stint best lap time. Note: stint deltabest will be reset if vehicle stops in pit lane.

    show_deltalast
Show delta against personal last lap time (deltalast). Note: deltalast will be reset upon ESC.


## DRS
**This widget displays DRS(rear flap) usage info.**

    font_color_activated, bkg_color_activated
Set color when DRS is activated by player.

    font_color_allowed, bkg_color_allowed
Set color when DRS is allowed but not yet activated by player.

    font_color_available, bkg_color_available
Set color when DRS is available but current disallowed to use.

    font_color_not_available, bkg_color_not_available
Set color when DRS is unavailable for current track or car.


## Electric motor
**This widget displays electric motor usage info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_motor_temperature
Show electric motor temperature.

    show_water_temperature
Show electric motor cooler water temperature.

    overheat_threshold_motor, overheat_threshold_water
Set temperature threshold for electric motor & water overheat color indicator, unit in Celsius.

    show_rpm
Show electric motor RPM.

    show_torque
Show electric motor torque.

    show_power
Show electric motor power.


## Elevation
**This widget displays elevation plot. Note: elevation plot data is recorded together with track map. At least one complete & valid lap is required to generate elevation plot.**

    display_detail_level
Sets detail level for track map. Default value is `1`, which auto adjusts map detail according to display size. Higher value reduces map detail and RAM usage, and may also help reduce rough edges from large map. Set to `0` for full detail.

    display_width
Set widget display width in pixels. Minimum width is limited to `20`.

    display_height
Set widget display height in pixels. Minimum height is limited to `10`.

    display_margin_*
Set widget display margin in pixels. Maximum margin is limited to half of `display_height` value.

    show_elevation_reading
Show elevation difference in game's coordinate system.

    show_elevation_scale
Show elevation plot scale reading, which is ratio between screen pixel and real world elevation. A `1:10.5` reading means 1 pixel equals 10.5 meters (or feet, depends on distance unit setting).

    *_offset_x, *_offset_y
Set reading text offset position (percentage), value range in `0.0` to `1.0`.

    *_text_alignment
Set reading text alignment. Acceptable value: `Left`, `Center`, `Right`.

    show_background
Show widget background.

    show_elevation_background
Show background of elevation plot.

    show_elevation_progress
Show elevation progress bar according player's current position.

    show_elevation_progress_line
Show elevation progress line according player's current position.

    show_elevation_line
Show elevation reference line.

    show_zero_elevation_line
Show zero elevation reference line in game's coordinate system.

    show_start_line
Show start line mark.

    show_sector_line
Show sector line mark.

    show_position_mark
Show player's current position line mark.


## Engine
**This widget displays engine usage info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_temperature
Show oil & water temperature.

    overheat_threshold_oil, overheat_threshold_water
Set temperature threshold for oil & water overheat color indicator, unit in Celsius.

    show_turbo_pressure
Show turbo pressure.

    show_rpm
Show engine RPM.

    show_rpm_maximum
shows maximum engine RPM (rev limit).

    show_torque
Show engine torque.

    show_power
Show engine power.


## Flag
**This widget displays flags, pit state, warnings, start lights info.**

    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    show_pit_timer
Show pit timer, and total amount time spent in pit after exit pit.

    pit_time_highlight_duration
Set highlight duration for total amount time spent in pit after exit pit.

    pit_closed_text
Set custom pit closed text.

    font_color_pit_closed, bkg_color_pit_closed
Set color indicator on pit timer when pit lane is closed.

    show_low_fuel
Show low fuel (or low virtual energy if available) indicator when below certain amount value. Only one indicator will be displayed for low fuel (LF) or low virtual energy (LE), depends on which one would deplete sooner.

    show_low_fuel_for_race_only
Only show low fuel indicator during race session.

    low_fuel_volume_threshold
Set fuel volume threshold (in Liter) to show low fuel indicator when total amount of remaining fuel is equal or less than this value. This setting is used to limit low fuel warning when racing on lengthy tracks, where fuel tank may only hold for a lap or two. Default is `20` Liter.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default is `2` laps before running out of fuel.

    show_speed_limiter
Show speed limiter indicator.

    speed_limiter_text
Set custom pit speed limiter text which shows when speed limiter is engaged.

    show_yellow_flag
Show yellow flag indicator and distance display which shows nearest yellow flag vehicle distance.

    show_yellow_flag_for_race_only
Only show yellow flag indicator during race session.

    yellow_flag_maximum_range
Only show yellow flag indicator when there is yellow flag within the maximum range (track distance in meters).

    show_blue_flag
Show blue flag indicator with timer.

    show_blue_flag_for_race_only
Only show blue flag indicator during race session.

    show_startlights
Show race start lights indicator with light frame number for standing-type start.

    green_flag_duration
Set display duration(seconds) for green flag text before it disappears. Default is `3`.

    red_lights_text
Set custom text for red lights.

    green_flag_text
Set custom text for green flag.

    show_traffic
Show nearest incoming on-track traffic indicator (time gap) while in pit lane or after pit-out.

    traffic_maximum_time_gap
Set maximum time gap (seconds) of incoming on-track traffic.

    traffic_pitout_duration
Set traffic indicator extended duration (seconds) after pit-out.

    traffic_low_speed_threshold
Set low speed threshold for showing nearest incoming traffic indicator. Default is `8` m/s (roughly 28kph). Set to `0` to disable. This option can be useful to quickly determine nearby traffic situation after a spin or crash.

    show_pit_request
Show pit request indicator and `pit-in laps countdown` alongside `estimated remaining laps` reading that current fuel or energy can run. Note, `pit-in laps countdown` value is always calculated towards the finish line of current stint's final lap, and thus is always less than or equal to `estimated remaining laps` reading. If countdown drops below 1.0 (laps), it indicates the final lap of current stint, and driver should pit in before the end of current lap to refuel. If countdown reaches zero or negative, there may still be some fuel or energy left in tank, however it will not be enough to complete another full lap.

    show_finish_state
Show finish or disqualify state.


## Force
**This widget displays g force and downforce info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_g_force
Show longitudinal & lateral g force with direction indicator.

    show_downforce_ratio
Show front vs rear downforce ratio. 50% means equal downforce; higher than 50% means front has more downforce.

    show_front_downforce, show_rear_downforce
Show front & rear downforce reading in Newtons.

    warning_color_liftforce
Set lift force indicator color.


## Friction circle
**This widget displays g force in circle diagram.**

    display_size
Set widget size in pixels.

    display_radius_g
Set viewable g force range by radius(g).

    display_orientation
Set display orientation for longitudinal & lateral g force axis. Default is `0`, which shows brake at top, acceleration at bottom, right-turn at left, left-turn at right. Set to `1` to inverted orientation.

    show_readings
Show values from g force reading. Value at top is current longitudinal g force, and value at bottom is max longitudinal g force. Value at left is max lateral g force, and value at right is current lateral g force.

    show_background
Show background color that covers entire widget.

    show_circle_background
Show circle background color.

    show_fade_out
Fade out circle background edge.

    fade_in_radius, fade_out_radius
Set fade in/out radius, value range in `0.0` to `1.0`.

    show_max_average_lateral_g_circle
Show max average lateral g force reference circle.

    max_average_lateral_g_circle_style
Set circle line style. `0` for dashed line, `1` for solid line.

    max_average_lateral_g_circle_width
Set circle line width in pixels.

    show_dot
Show g force dot.

    dot_size
Set g force dot size in pixels.

    show_trace
Show g force trace.

    trace_max_samples
Set max amount g force trace samples.

    trace_style
Set g force trace style. `0` for line style. `1` for point style.

    trace_width
Set g force trace width in pixels.

    show_trace_fade_out
Show trace fade out effect.

    trace_fade_out_step
Set trace fade out speed. Value range in `0.1` to `0.9`, higher value increases trace fade out speed. Default value is `0.2`.

    show_center_mark
Show center mark.

    center_mark_radius_g
Set center mark size by radius(g).

    center_mark_style
Set center mark line style. `0` for dashed line, `1` for solid line.

    center_mark_width
Set center mark line width in pixels.

    show_reference_circle
Show reference circle.

    reference_circle_*_radius_g
Set reference circle size by radius(g). Circle will not be displayed if radius is bigger than `display_radius_g`.

    reference_circle_*_style
Set reference circle line style. `0` for dashed line, `1` for solid line.

    reference_circle_*_width
Set reference circle line width in pixels.


## Fuel
**This widget displays fuel usage info.**

    *end
Estimated remaining fuel reading at the end of current stint before pit.

    *remain
Remaining fuel reading.

    *refuel
Estimated refueling reading, which is the total amount additional fuel required to finish race. Note, positive value indicates additional refueling and pit-stop would be required, while negative value indicates total extra fuel would left at the end of race and no extra pit-stop required.

    *used
Estimated fuel consumption reading, which is calculated from last-valid-lap fuel consumption and delta fuel consumption. Note, when vehicle is in garage stall, this reading only shows last-valid-lap fuel consumption without delta calculation.

    *delta
Estimated delta fuel consumption reading. Positive value indicates an increase in consumption, while negative indicates a decrease in consumption.

    *early
Estimate number of pit stop counts when making an early pit stop at end of current lap. This value can be used to determine whether an early pit stop is worth performing comparing to `pits` value.

Example 1: When this value is just below `1.0` (such as `0.97`), it indicates an early pit stop can be made right at the end of current lap with enough empty capacity to refuel according to `refuel` reading which would last to the end of race.

Example 2: When this value is just below `2.0` (such as `1.96`), and `pits` value is also in `1.x` range (such as `1.32`),  it indicates 2 required pit stops, and an early pit stop can be made right at the end of current lap with tank fully refueled according to `refuel` reading. After refueling, `pits` reading would show an approximately `0.96` value which indicates one more required pit stop.

Example 3: If this value is one or more integers higher than `pits` value, then additional pit stops would be required after making a pit stop at the end of current lap.

    *laps
Estimated laps reading that current fuel can last.

    *minutes
Estimated minutes reading that current fuel can last.

    *save
Estimated fuel consumption reading for one less pit stop.

    *pits
Estimate number of pit stop counts when making a pit stop at end of current stint. Any non-zero decimal places would be considered for an additional pit stop.

    bar_width
Set each column width, value in chars, such as 10 = 10 chars. Default is `5`. Minimum width is limited to `3`.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default is `2` laps before running out of fuel.

    warning_color_low_fuel
Set low fuel color indicator, which changes widget background color when there is just 2 laps of fuel left.

    show_fuel_level_bar
Show visualized horizontal fuel level bar.

    fuel_level_bar_height
Set fuel level bar height in pixels.

    show_starting_fuel_level_mark
Show starting fuel level mark of current stint. Default mark color is red.

    show_refueling_level_mark
Show estimated fuel level mark after refueling. If the mark is not visible on fuel level bar, it indicates total refueling has exceeded fuel tank capacity. Default mark color is green.

    starting_fuel_level_mark_width, refueling_level_mark_width
Set fuel level mark width in pixels.

    caption_text
Set custom caption text.

    swap_upper_caption, swap_lower_caption
Swap caption row position.


## Fuel energy saver
**This widget displays fuel or virtual energy saving info.**

Show current stint estimated total completable laps and completed laps based on current consumption.

Show estimated target lap consumption to save (extend) one or more total stint laps.

Show delta consumption against target lap consumption, which allows fuel or energy saving to be visualized and easily controlled in real-time.

Show consumption type in `FUEL` or `NRG` (if virtual energy available).

Show last lap consumption.

    minimum_reserve
Set minimum amount fuel or virtual energy in tank that is excluded from saving calculation and reserved for the end of stint. Default is `0.2` Liter for fuel (or % for virtual energy).

    number_of_more_laps
Set number of target slots for more completable laps. Default is `3`. Range in `1` to `10`.

    number_of_less_laps
Set number of target slots for less completable laps. Default is `0`. Range in `0` to `5`.


## Gear
**This widget displays gear, RPM, speed, battery info.**

    inner_gap
Set inner gap between gear & speed readings. Negative value reduces gap, while positive value increases gap. Default is `0`.

    show_speed
Show speed reading.

    show_speed_below_gear
Show speed reading below gear.

    font_scale_speed
Set font scale for speed reading. This option only takes effect when `show_speed_below_gear` is enabled. Default is `0.5`.

    show_battery_bar
Show battery bar, which is only visible if electric motor available.

    battery_bar_height
Set battery bar height in pixels.

    show_speed_limiter
Show pit speed limiter indicator.

    speed_limiter_text
Set custom pit speed limiter text which shows when speed limiter is engaged.

    show_rpm_bar
Show a RPM bar at bottom of gear widget, which moves when RPM reaches range between safe & max RPM.

    rpm_bar_height
RPM bar height, in pixel.

    rpm_multiplier_safe
This value multiplies max RPM value, which sets relative safe RPM range for RPM color indicator (changes gear widget background color upon reaching this RPM value).

    rpm_multiplier_redline
This value multiplies max RPM value, which sets relative near-max RPM range for RPM color indicator.

    rpm_multiplier_critical
This value multiplies max RPM value, which sets critical RPM range for RPM color indicator.

    show_rpm_flickering_above_critical
Show flickering effects when RPM is above critical range and gear is lower than max gear.

    neutral_warning_speed_threshold, neutral_warning_time_threshold
Set speed/time threshold value for neutral gear color warning, which activates color warning when speed & time-in-neutral is higher than threshold. Speed unit in meters per second, Default is `28`. Time unit in seconds, Default is `0.3` seconds.


## Heading
**This widget displays vehicle yaw angle, slip angle, heading info.**

    display_size
Set widget size in pixels.

    show_yaw_angle_reading
Show yaw angle reading in degrees.

    show_slip_angle_reading
Show slip angle reading in degrees.

    *_offset_x, *_offset_y
Set reading text offset position (percentage), value range in `0.0` to `1.0`.

    show_degree_sign
Set `true` to show degree sign for yaw angle reading.

    show_background
Show background color that covers entire widget.

    show_circle_background
Show circle background color.

    show_yaw_line
Show yaw line (vehicle heading).

    show_direction_line
Show vehicle's direction of travel line.

    show_slip_angle_line
Show slip angle (average of the front tyres) line.

    *_line_head_scale
Set line length scale from center to head, value range in `0.0` to `1.0`.

    *_line_tail_scale
Set line length scale from center to tail, value range in `0.0` to `1.0`.

    *_line_width
Set line width in pixels.

    show_dot
Show center dot.

    show_center_mark
Show center mark.

    center_mark_length_scale
Set center mark length scale, value range in `0.0` to `1.0`.

    center_mark_style
Set center mark line style. `0` for dashed line, `1` for solid line.

    center_mark_width
Set center mark line width in pixels.


## Instrument
**This widget displays vehicle instruments info.**

    icon_size
Set size of instrument icon in pixel. Minimum value is limited to `16`.

    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    show_headlights
Show Headlights state.

    show_ignition
Show Ignition & Starter state.

    show_clutch
Show Auto-Clutch state.

    show_wheel_lock
Show Wheel Lock state.

    show_wheel_slip
Show Wheel Slip state.

    wheel_lock_threshold
Set percentage threshold for triggering wheel lock warning under braking. `0.3` means 30% of tyre slip ratio.

    wheel_slip_threshold
Set percentage threshold for triggering wheel slip warning. `0.1` means 10% of tyre slip ratio.


## Lap time history
**This widget displays lap time history info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = reversed vertical layout.

    lap_time_history_count
Set the number of lap time history display. Default is to show `10` most recent lap times.

    show_virtual_energy_if_available
Show virtual energy consumption instead of fuel consumption if available. This option is enabled by default.

    show_empty_history
Show empty lap time history. Default is `false`, which hides empty rows.


## Navigation
**This widget displays a zoomed navigation map that centered on player's vehicle. Note: at least one complete & valid lap is required to generate map.**

    display_size
Set widget size in pixels.

    view_radius
Set viewable area by radius(unit meter). Default is `500` meters. Minimum value is limited to `5`.

    show_background
Show background color that covers entire widget.

    show_circle_background
Show circle background color.

    circle_outline_width
Set circle background outline width. Set value to `0` to hide outline.

    show_fade_out
Fade out view edge.

    fade_in_radius, fade_out_radius
Set fade in/out radius, value range in `0.0` to `1.0`.

    map_width
Set navigation map line width.

    map_outline_width
Set navigation map outline width.

    show_start_line
Show start line mark.

    show_sector_line
Show sector line mark.

    show_vehicle_standings
Show vehicle standings info on navigation map.

    show_circle_vehicle_shape
Set `True` to show vehicle in circle shape, set `False` for arrow shape.

    vehicle_size
Set vehicle size in pixels.

    vehicle_offset
Set vehicle vertical position offset (percentage) relative to display size, value range in `0.0` to `1.0`.

    vehicle_outline_width
Set vehicle outline width.


## P2P
**This widget displays push to pass usage info.**

    show_battery_charge
Show percentage available battery charge.

    show_activation_timer
Show electric boost motor activation timer.

    activation_threshold_gear
Set minimum gear threshold for P2P ready indicator.

    activation_threshold_speed
Set minimum speed threshold for P2P ready indicator, unit in KPH.

    activation_threshold_throttle
Set minimum throttle input percentage threshold for P2P ready indicator, value range in `0.0` to `1.0`.

    minimum_activation_time_delay
Set minimum time delay between each P2P activation, unit in seconds.

    maximum_activation_time_per_lap
Set maximum P2P activation time per lap, unit in seconds.


## Pedal
**This widget displays pedal input and force feedback info.**

    show_readings
Show pedal input and force feedback readings. Note, while `show_*_filtered` option is enabled, only the highest reading between filtered & raw input is displayed.

    readings_offset
Set reading text offset position (percentage), value range in `0.0` to `1.0`.

    enable_horizontal_style
Show pedal bar in horizontal style.

    bar_length, bar_width_unfiltered, bar_width_filtered
Set pedal bar length & width in pixels.

    inner_gap
Set gap between pedal and max indicator.

    max_indicator_height
This is the indicator height when pedal reaches 100% travel, value in pixel.

    show_brake_pressure
Show brake pressure changes applied on all wheels, which auto scales with max brake pressure and indicates amount brake released by ABS on all wheels. This option is enabled by default, which replaces game's filtered brake input that cannot show ABS.

    show_throttle
Show throttle bar.

    show_brake
Show brake bar.

    show_clutch
Show clutch bar.

    show_ffb_meter
Show Force Feedback meter.


## Radar
**This widget displays vehicle radar info.**

    global_scale
Sets global scale of radar display. Default is `6`, which is 6 times of original size.

    radar_radius
Set the radar display area by radius(unit meter). Default is `30` meters. Minimum value is limited to `5`.

    vehicle_length, vehicle_width
Set vehicle overall size (length & width), value in meters.

    vehicle_border_radius
Set vehicle round border radius.

    vehicle_outline_width
Set vehicle outline width.

    show_background
Show background color that covers entire widget.

    show_circle_background
Show circle background color.

    show_fade_out
Fade out Radar edge.

    fade_in_radius, fade_out_radius
Set fade in/out radius, value range in `0.0` to `1.0`.

    show_overlap_indicator
Show overlap indicator when there is nearby side by side vehicle.

    overlap_detection_range_multiplier
Set overlap detection range multiplier that scales with vehicle width.

    indicator_size_multiplier
Set indicator size multiplier that scales with vehicle width.

    show_center_mark
Show center mark on radar.

    center_mark_style
Set center mark line style. `0` for dashed line, `1` for solid line.

    center_mark_radius
Set center mark size by radius(unit meter).

    center_mark_width
Set center mark line width in pixels.

    show_distance_circle
Show distance circle line on radar for distance reference.

    distance_circle_*_style
Set distance circle line style. `0` for dashed line, `1` for solid line.

    distance_circle_*_radius
Set distance circle size by radius(unit meter). Circle will not be displayed if radius is bigger than `radar_radius`.

    distance_circle_*_width
Set distance circle line width in pixels.

    auto_hide
Auto hides radar display when no nearby vehicles.

    auto_hide_in_private_qualifying
Auto hides radar in private qualifying session, requires both `auto_hide` and `RestAPI Module` enabled.

    auto_hide_time_threshold
Set amount time(unit second) before triggering auto hide. Default is `1` second.

    auto_hide_minimum_distance_ahead, behind, side
The three values define an invisible rectangle area(unit meter) that auto hides radar if no vehicle is within the rectangle area. Default value is `-1`, which auto scales with `radar_radius` value. Set to any positive value to customize radar auto-hide range. Note, each value is measured from center of player's vehicle position.

    vehicle_maximum_visible_distance_ahead, behind, side
The three values define an invisible rectangle area(unit meter) that hides any vehicle outside the rectangle area. Default value is `-1`, which auto scales with `radar_radius` value. Set to any positive value to customize vehicle visible range. Note, each value is measured from center of player's vehicle position.


## Rake angle
**This widget displays vehicle rake info.**

    wheelbase
Set wheelbase in millimeters, for used in rake angle calculation.

    show_degree_sign
Set `true` to show degree sign for rake angle value.

    show_ride_height_difference
Show average front & rear ride height difference in millimeters.


## Relative
**This widget displays relative standings info.**

    show_player_highlighted
Highlight player row with customizable specific color.

    show_lap_difference
Show different font color based on lap difference between player and opponents. Note, this option will override `font_color` setting from `position`, `driver name`, `vehicle name`, `time gap`.

    font_color_same_lap, font_color_laps_ahead, font_color_laps_behind
Set font color for lap difference. Note, `font_color_laps_ahead` & `font_color_laps_behind` applies to race session only.

    show_position
Show overall position standings.

    show_driver_name
Show driver name.

    driver_name_shorten
Shorten driver's first name to a single letter with a period separating driver's last name, and any middle names will not be displayed. Note, if a driver is using nickname that consists only a single word, the name will not be shortened.

    driver_name_uppercase
Set driver name to uppercase.

    driver_name_width
Set drive name display width, value in chars, such as 10 = 10 chars.

    driver_name_align_center
Align driver name in the center when enabled. Default is left alignment when disabled.

    show_vehicle_name
Show vehicle name. Note, game API outputs `skin livery name` as `vehicle name`, which means actual displayed name depends on what skin livery name is called. For example, some vehicles may add `team name` and/or `class name` in `skin livery name`, some may not.

    show_vehicle_brand_as_name
Show vehicle brand name instead of vehicle name. If brand name does not exist, vehicle name will be displayed instead.

    vehicle_name_uppercase
Set vehicle name to uppercase.

    vehicle_name_width
Set vehicle name display width, value in chars, such as 10 = 10 chars.

    vehicle_name_align_center
Align vehicle name in the center when enabled. Default is left alignment when disabled.

    show_brand_logo
Show user-defined brand logo if available.

    brand_logo_width
Set maximum brand logo display width in pixels. Note, maximum brand logo display height is automatically adapted to `font_size`.

    show_time_gap
Show relative time gap between player and opponents.

    time_gap_width
Set time gap display width, value is in chars, 5 = 5 chars wide.

    show_laptime
Show driver's last lap time & pit timer if available.

    show_position_in_class
Show driver's position standing in class.

    show_class
Show vehicle class categories. Class name & color are fully customizable, see Classes section for details.

    show_random_color_for_unknown_class
Show random color for unknown class name that is not defined in `classes.json`.

    class_width
Set class name display width, value is in chars, 4 = 4 chars wide.

    show_pit_status
Show indicator whether driver is currently in pit.

    pit_status_text
Set custom pit status text which shows when driver is in pit.

    show_tyre_compound
Show tyre compound index (front/rear).

    show_pitstop_count
Show each driver's pitstop count.

    show_pit_request
Show pit request color indicator on pitstop count column.

    show_vehicle_in_garage_for_race
Show vehicles that are stored in garage stall during race (for example, DNF or DQ). Default is `false`.

    additional_players_front, additional_players_behind
Set additional players shown on relative list. Each value is limited to a maximum of 60 additional players (for a total of 120 additional players). Default is `0`.


## Relative finish order
**This widget displays estimated relative finish order between leader and local player with corresponding refilling estimate in a table view.**

The table consists of 5 fixed rows, 3 fixed columns, and 10 optional predication columns that can be customized. Example:

| TIME |   0s  |  30s  |  40s  |  50s  |  60s  |  54s  |
|:----:|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|
|  LDR |  0.49 |  0.20 |  0.11 |  0.02 |  0.92 |  0.98 |
| 0.04 |  0.91 |  0.64 |  0.55 |  0.46 |  0.37 |  0.51 |
| DIFF |   0s  |  30s  |  40s  |  50s  |  60s  |  43s  |
|  NRG | +18.1 | +18.1 | +18.1 | +18.1 | +18.1 | +18.1 |

First and fourth rows, starting from second cell, show estimated `leader's pit time` and `local player's pit time`, where first row first cell shows current session type in `TIME` or `LAPS`. Last cell shows last recorded total time that leader and local player had spent in pit. Note, last recorded total pit time counts from pit entry to pit exit point, it doesn't include the extra few seconds that spent while approaching or exiting from pit.

Second and third rows, starting from second cell, show estimated `leader's final lap progress` (fraction of lap) and `local player's final lap progress` that depend on current session type:
* For `TIME` type race, it shows final lap progress at the moment when session timer ended.
* For `LAPS` type race, it shows relative final total lap difference between leader and local player.  
Leader's value from second row second cell always shows `integer value`, because laps-type race has no timer, and the end of race is determined at the moment when leader crossed finish line, which can only be full laps.  
Local player's value from third row second cell always shows final lap progress relative to leader's value from second row second cell.  
Both leader's and local player's `final lap progress` values starting from third cell are offset from second cell of same row.

Third row, first cell shows `relative lap difference` between leader and local player that is calculated from lap time pace difference of both players, which can be used to determine whether leader has the chance to overtake local player on final lap. For example:
* If relative lap difference value shows 0.25, that means for every full lap, leader is faster than local player by 0.25 lap. If leader is at start line and player is just within 0.25 lap distance from leader, that means leader can catch up and overtake player before the end of lap.
* If relative lap difference value shows 0.25 and leader is at middle of current lap (0.5 lap), that means leader now only has roughly half of the lap distance (0.12 lap) to make successful overtake before the end of lap. If player is not within this 0.12 lap distance, then leader may not be able to overtake.

Fifth row, first cell shows refilling type in `FUEL` or `NRG` (if virtual energy available). Starting from second cell, shows estimated `local player's refilling` that depends on current session type:
* For `TIME` type race, refilling value from each column is calculated based on local player's current `laptime pace`, `consumption`, and `local player's final lap progress` from third row of same column. Note, each refilling value has no relation to `leader's final lap progress` value from same column. Refilling value from `0s` column gives same reading as seen from `Fuel` or `Virtual Energy` Widget in time-type race.
* For `LAPS` type race, only refilling value from `0s` column is calculated and displayed according to leader's `leader's final lap progress` value.  
Other column values are not displayed, this is done to avoid confusion. Because unlike `TIME` type race where all `final lap progress` values are within `0.0` to `1.0` range, in `LAPS` type race values can exceed `1.0` or below `0.0` (negative), which the number of possible lap differences would increase exponentially and not possible to list all of them in the widget.

See `TIME` or `LAPS` type race example usages below for details.

---

**Important notes**

* Predication accuracy depends on many variables and is meant for final stint estimate. Such as laptime pace, pit time, penalties, weather condition, safety car, yellow flag, can all affect predication accuracy. It requires at least 2-3 laps to get sensible readings, and more laps to have better accuracy. **Do not expect accurate readings or plan fuel strategy from first few laps.**

* `Final lap progress` values will not be displayed if no corresponding vaild lap time pace data found, which requires at least 1 or 2 laps to record. If local player is the leader, then all values from leader's row will not be displayed. Refilling values will not be displayed during formation lap for the reasons mentioned in first note.

* Refilling estimate calculation is different between `TIME` and `LAPS` type races, make sure to look at the correct value, check out `example usage` below for details.

* `LMU` currently uses `absolute-refueling` mechanism (how much `total` fuel to fill tank up to), as opposite to relative fuel (how much to `add` on top of remaining fuel in tank). This means user has to manually add up both `remaining` and `refuel/refill` values for total fuel/energy refill.

* This widget is meant for used in complex and endurance race situations. To avoid human error, it is necessary to have a good understanding of this widget and practicing proficiency before attempting to use any provided data in actual race. Once with enough practicing, it should be fairly easy to make the most out of it.

* **Avoid using this widget if unfamiliar or unsure any of the usage or data it provides.**

---

**Time-type race example usage**

| TIME | 0s   | 30s  | 40s  | 50s  | 60s  | 0s   |
|:----:|:----:|:----:|:----:|:----:|:----:|:----:|
| LDR  | 0.38 | 0.10 | 0.01 | 0.91 | 0.82 | 0.38 |
| 0.11 | 0.72 | 0.47 | 0.39 | 0.31 | 0.22 | 0.37 |
| DIFF | 0s   | 30s  | 40s  | 50s  | 60s  | 43s  |
| FUEL | +7.4 | +7.4 | +7.4 | +7.4 | +7.4 | +7.4 |

1. Determine leader's next pit time and select `leader's final lap progress` (second row) value from corresponding pit time (first row) column. `0s` column means no pit stop.

2. Determine local player's next pit time and select `local player's final lap progress` (third row) value from corresponding pit time (fourth row) column.

3. Compare the two `final lap progress` values from leader and local player:

    * If leader's `final lap progress` value is greater than local player, such as leader's 0.91 (50s column) vs player's 0.47 (30s column), it indicates that leader will be ahead of local player when timer ended, and there will be no extra final lap. So `local player's refilling` value from corresponding `30s` column can be used, in this case, it's `+7.4` fuel to add.  
    However, if leader is closer to finish line (as show in orange color indicator), there is a chance that leader may be fast enough to cross finish line before the end of timer, which would result an extra final lap for local player, and requires adding an extra lap of fuel on top of `+7.4` fuel in this case.

    * If local player's `final lap progress` value is greater than leader, such as leader's 0.10 (30s column) vs player's 0.72 (0s column), it indicates that local player will be ahead of leader when timer ended, and there will be an extra final lap for local player, and requires adding an extra lap of fuel on top of `+7.4` fuel from `0s` column.  
    However, if the difference between the two `final lap progress` values is smaller than `relative lap difference` (from third row first cell) value, it may indicate that leader could overtake local player on final lap, which would result no extra final lap.

4. To sum up, if comparison shows no extra final lap, then just refill according to `local player's refilling` (fifth row) value from the same column of `local player's final lap progress` (third row). If comparison shows an extra final lap, then just add an extra lap of fuel on top of `local player's refilling` value.


**Laps-type race example usage**

Note, there is generally no reason to use this widget in `LAPS` type race unless you are doing multi-class laps-type race which is very rarely seen.

| LAPS | 0s    | 30s  | 40s   | 50s   | 60s   | 0s   |
|:----:|:-----:|:----:|:-----:|:-----:|:-----:|:----:|
| LDR  | 2.00  | 1.57 | 1.43  | 1.28  | 1.14  | 2.00 |
| 0.11 | 0.40  | 0.02 | -0.11 | -0.24 | -0.37 | 0.40 |
| DIFF | 0s    | 30s  | 40s   | 50s   | 60s   | 43s  |
| FUEL | +12.8 | -    | -     | -     | -     | -    |

1. Determine leader's next pit time and select `leader's final lap progress` (second row) value from corresponding pit time (first row) column. `0s` means no pit stop.

2. Determine local player's next pit time and select `local player's final lap progress` (third row) value from corresponding pit time (fourth row) column.

3. Subtract `local player's final lap progress` value from `leader's final lap progress`, then round down value:

    * If leader's `final lap progress` value is 2.00 (0s column), and local player's `final lap progress` value is 0.40 (0s column), then after subtracting (2 - 0.4 = 1.6) and rounding down, the final value is `1` lap difference, which means local player will do `one less lap` than leader.  
    As mentioned earlier, for laps-type race, refilling value from `0s column` is calculated according to leader's `leader's final lap progress` value, which any lap difference is already included in the result from `local player's refilling` value (fifth row second cell), in this case, it's `+12.8` fuel to add.  

    * If leader's `final lap progress` value is 1.43 (40s column), and local player's `final lap progress` value is -0.24 (50s column), then after subtracting (1.43 - -0.24 = 1.67) and rounding down, the final value is also `1` lap difference, which means local player will do the same `one less lap` than leader. So in this case, it's still `+12.8` fuel to add.  

    * If leader's `final lap progress` value is 2.00 (0s column), and local player's `final lap progress` value is -0.11 (40s column), then after subtracting (2 - -0.11 = 2.11) and rounding down, the final value is `2` lap difference, which means local player will do `two less laps` than leader. So an extra lap of fuel may be removed from `local player's refilling` value from fifth row second cell, in this case, it's `12.8` minus one lap of fuel `2.2`, equals `+10.6` fuel to add. Alternatively, it can be calculated from full lap refuel (as show in Fuel Widget), which will be `15.0` minus two lap of fuel `4.4`, and equals `+10.6` fuel to add.  
    Be aware that carrying less fuel is risky in laps-type race due to reasons below.

4. Last note, since the end of laps-type race is determined by the moment that leader completed all race laps, leader can greatly affect final predication outcome. To give an extreme example, if leader is ahead of everyone by a few laps, and decides to wait a few minutes on his final lap before finish line, then everyone else will be catching up and do a few `extra laps` which would require more fuel. Thus it is always risky to carry less fuel in laps-type race.

---

    layout
2 layouts are available: `0` = show columns from left to right, `1` = show columns from right to left.

    near_start_range
Set detection range (in seconds) near (after) start/finish line to show color indicator when vehicle is within the range (or less). Default is `20` seconds. Default color is green.

    near_finish_range
Set detection range (in seconds) near (before) start/finish line to show color indicator when vehicle is within the range (or less). Default is `20` seconds. Default color is orange.

    leader_laptime_pace_samples
Set number of samples for average laptime pace calculation (EMA). Value range in `1` to `20`. Default is `6` samples. Set to `1` to disable averaging. Note, initial laptime pace is always based on leader's session personal best laptime if available. If a new laptime is faster than current laptime pace, it will replace current laptime pace without calculating average. Invalid lap, pit-in/out laps are always excluded from laptime pace calculation.

    leader_laptime_pace_margin
Set additional margin for current laptime that cannot exceed the sum of `laptime pace` and `margin`. This option is used to minimize the impact of unusually slow laptime. Default value is `5` seconds. Minimum value is limited to `0.1`.

    number_of_predication
Set number of optional predication columns with customizable pit time. Value range in `0` to `10`. Default is `4` extra customizable columns.

    predication_*_leader_pit_time, predication_*_player_pit_time
Set predication pit time for leader or local player.


## Ride height
**This widget displays visualized ride height info.**

    ride_height_max_range
Set visualized maximum ride height range (millimeter).

    rideheight_offset*
Set ride height offset for bottoming indicator. Value in millimeters, but without decimal place.


## Rivals
**This widget displays standings info from opponent ahead and behind local player from same vehicle class. Most options are inherited from relative & standings widget, with some additions noted below.**

    *_color_time_interval_ahead, *_color_time_interval_behind
Set custom time interval color of opponent ahead and behind.


## Sectors
**This widget displays sectors timing info.**

    layout
2 layouts are available: `0` = target & current sectors above deltabest sectors, `1` = deltabest sectors above target & current sectors.

    target_laptime
Set target laptime for display target reference lap and sector time. Set `Theoretical` to show theoretical best sector time. Set `Personal` to show sector time from personal best lap time. Note, if `enable_all_time_best_sectors` option is enabled in `Sectors Module`, all time best sectors data will be displayed instead, otherwise only current session best sectors data will be displayed.

    freeze_duration
Set freeze duration (seconds) for displaying previous sector time. Default is `5` seconds.


## Session
**This widget displays system clock, session name, timing, lap number, overall position info.**

    show_session_name
Show current session name that includes testday, practice, qualify, warmup, race.

    session_text_*
Set custom session name text.

    show_system_clock
Show current system clock time.

    system_clock_format
Set clock format string. To show seconds, add `%S`, such as `%H:%M:%S %p`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

    show_session_timer
Show session timer, accuracy may be limited by specific sim API.

    show_lapnumber
Show your current lap number & max laps (if available).

    bkg_color_maxlap_warn
Set warning color that shows 1 lap before exceeding max-lap in qualify (or indicates the last lap of a lap-type race).

    show_position
Show your current position against all drivers in a session.


## Speedometer
**This widget displays conditional speed info.**

    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    show_speed
Show current vehicle speed.

    show_speed_minimum
Show minimum speed that is updated while off throttle.

    show_speed_maximum
Show maximum speed that is updated while on throttle.

    show_speed_fastest
Show fastest recorded speed. To reset current record, shift gear into reverse, or reload preset.

    off_throttle_threshold
Set throttle threshold which counts as off throttle if throttle position is lower, value range in `0.0` to `1.0`. Default is `0.5`.

    on_throttle_threshold
Set throttle threshold which counts as on throttle if throttle position is higher, value range in `0.0` to `1.0`. Default is `0.01`.

    speed_minimum_reset_cooldown
Set cooldown duration (seconds) before resetting minimum speed value.

    speed_maximum_reset_cooldown
Set cooldown duration (seconds) before resetting maximum speed value.


## Standings
**This widget displays standings info. Most options are inherited from relative widget, with some additions noted below.**

    max_vehicles_combined_mode
Set maximum amount vehicles to display, which takes effect when `enable_multi_class_split_mode` is not enabled. When total vehicle number is lower than this value, extra rows will auto-hide. When total vehicle number is above this value, the top 3 vehicles will always show, and rest of the vehicles will be selected from the nearest front and behind places related to player.

    max_vehicles_split_mode
Set maximum amount vehicles to display, which takes effect when in multi-class session and `enable_multi_class_split_mode` is enabled. If total vehicle number is above this value, any extra vehicles will not be shown. Default is `50`, which is sufficient in most case.

    min_top_vehicles
Set minimum amount top place vehicles to display. This value has higher priority than other `max_vehicles` settings. Default is `3`, which always shows top 3 vehicles if present.

    enable_multi_class_split_mode
Enable multi-class split mode, which splits and displays each vehicle class in separated groups. This mode will only take effect when there is more than one vehicle class present in a session, otherwise it will automatically fall back to normal single class mode.

    max_vehicles_per_split_player
Set maximum amount vehicles to display for class where player is in. Default is `7`. Note that, if player is not in first place, then at least one opponent ahead of player will always be displayed, even if this value sets lower.

    max_vehicles_per_split_others
Set maximum amount vehicles to display for classes where player is not in. Default is `3`.

    split_gap
Set split gap between each class.

    show_time_gap
For race session, this option shows time gap between leader and all other drivers. For other none race sessions, this option shows the time gap between session's best lap time and all other drivers.

    show_time_gap_from_class_best
Show time gap from none race session's best lap time of the same vehicle class.

    time_gap_leader_text
Set text indicator for race leader in time gap column.

    show_time_interval
Show time interval between each closest driver in order.

    show_time_interval_from_same_class
Show time interval from same class. This option only takes effect while `enable_multi_class_split_mode` is enabled.

    time_interval_leader_text
Set text indicator for race leader in time interval column.

    show_laptime
Show driver's last lap time or pit timer if available. If `show_best_laptime` is not enabled, this option will show driver's session best lap time in none-race sessions.

    show_best_laptime
Show driver's session best lap time.


## Steering
**This widget displays steering input info.**

    bar_width, bar_height
Set steering bar width & height in pixels.

    bar_edge_width
Set left and right edge boundary width.

    manual_steering_range
Manually set steering display range in degrees. Set to `0` to read physical steering range from API. This option may be useful when steering range value is not provided by some vehicles.

    show_steering_angle
Show steering angle text in degree.

    show_scale_mark
This enables scale marks on steering bar.

    scale_mark_degree
Set gap between each scale mark in degree. Default is `90` degree. Minimum value is limited to `10` degree.


## Stint history
**This widget displays stint history info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = reversed vertical layout.

    stint_history_count
Set the number of stint history display. Default is to show `2` most recent stints.

    show_virtual_energy_if_available
Show virtual energy consumption instead of fuel consumption if available. This option is enabled by default.

    show_empty_history
Show empty stint history. Default is `false`, which hides empty rows.

    minimum_stint_threshold_minutes
Set the minimum stint time threshold in minutes for updating stint history. This only affects ESC.


## Suspension position
**This widget displays visualized suspension position info.**

    position_max_range
Set visualized maximum suspension position range (millimeter).


## Timing
**This widget displays lap time info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_session_best
Show current session best lap time from all vehicle classes.

    show_session_best_from_same_class_only
Show current session best lap time from same vehicle class only.

    show_best
Show personal all time best lap time.

    show_last
Show personal last lap time.

    show_current
Show personal current lap time.

    show_estimated
Show personal current estimated lap time.

    show_session_personal_best
Show personal current session best lap time.

    show_stint_best
Show personal current stint best lap time.

    show_average_pace
Show personal current average lap time pace, this reading is also used in real-time fuel calculation. Note, additional `average lap time pace` calculation setting can be found in `Delta Module` config. After ESC or session ended, lap time pace reading will be reset, and aligned to `all time personal best lap time` if available.


## Track map
**This widget displays track map and standings. Note: at least one complete & valid lap is required to generate track map.**

    display_detail_level
Sets detail level for track map. Default value is `1`, which auto adjusts map detail according to display size. Higher value reduces map detail and RAM usage, and may also help reduce rough edges from large map. Set to `0` for full detail.

    area_size
Set area display size.

    area_margin
Set area margin size.

    show_background
Show widget background.

    show_map_background
Show background of the inner map area. This option only works for circular type tracks.

    map_width
Set track map line width.

    map_outline_width
Set track map outline width.

    show_start_line
Show start line mark.

    show_sector_line
Show sector line mark.

    show_vehicle_standings
Show vehicle standings info on track map.


## Trailing
**This widget displays pedal input and force feedback plots.**

    display_width
Set pedal plot display width in pixels.

    display_height
Set pedal plot display height in pixels.

    display_margin
Set pedal plot display margin (vertical relative to pedal) in pixels.

    display_scale
Set plot display scale. Default scale is `2`. Minimum scale is limited to `1`.

    show_inverted_pedal
Invert pedal range display.

    show_inverted_trailing
Invert trailing direction.

    show_throttle
Show throttle plot.

    show_raw_throttle
Show unfiltered throttle instead.

    *_line_width
Set trailing line width in pixels.

    *_line_style
Set trailing line style. `0` for solid line, `1` for dashed line.

    show_wheel_lock
Show wheel lock (slip ratio) plot under braking when slip ratio has exceeded `wheel_lock_threshold` value.

    wheel_lock_threshold
Set percentage threshold for triggering wheel lock warning under braking. `0.3` means 30% of tyre slip ratio.

    show_wheel_slip
Show wheel slip (slip ratio) plot under acceleration when slip ratio has exceeded `wheel_slip_threshold` value.

    wheel_slip_threshold
Set percentage threshold for triggering wheel slip warning under acceleration. `0.1` means 10% of tyre slip ratio.

    show_reference_line
Show reference line.

    reference_line_*_style
Set reference line vertical offset relative to pedal, value in percentage.

    reference_line_*_style
Set reference line style. `0` for solid line, `1` for dashed line.

    reference_line_*_width
Set reference line width in pixels. Set value to `0` to hide line.

    draw_order_index_*
Set draw order of plot lines.


## Tyre carcass temperature
**This widget displays tyre carcass temperature info.**

    heatmap_name
Set heatmap preset name that is defined in `heatmap.json` file.

    show_degree_sign
Set `true` to show degree sign for each temperature value.

    leading_zero
Set amount leading zeros for each temperature value. Default is `2`. Minimum value is limited to `1`.

    show_rate_of_change
Show carcass temeperature rate of change for a specific time interval.

    rate_of_change_interval
Set time interval in seconds for rate of change calculation. Default interval is `5` seconds. Minimum interval is limited to `1` second, maximum interval is limited to `60` seconds.

    show_tyre_compound
Show tyre compound index (front/rear).


## Tyre load
**This widget displays visualized tyre load info.**

    show_tyre_load_ratio
Show percentage ratio of tyre load between each and total tyre load. Set `false` to show individual tyre load in Newtons.


## Tyre pressure
**This widget displays tyre pressure info.**


## Tyre temperature
**This widget displays tyre surface and inner layer temperature info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    heatmap_name
Set heatmap preset name that is defined in `heatmap.json` file.

    swap_style
Swap heatmap color between font & background color.

    show_inner_center_outer
Set inner, center, outer temperature display mode. Set `false` to show average temperature instead.

    show_degree_sign
Set `true` to show degree sign for each temperature value.

    leading_zero
Set amount leading zeros for each temperature value. Default is `2`. Minimum value is limited to `1`.

    show_innerlayer
Show tyre inner layer temperature.

    show_tyre_compound
Show tyre compound index (front/rear).


## Tyre wear
**This widget displays tyre wear info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_remaining
Show total remaining tyre in percentage that changes color according to wear.

    show_wear_difference
Show total tyre wear difference of previous lap.

    show_live_wear_difference
Show tyre wear difference of current lap that constantly updated.

    freeze_duration
Set freeze duration (seconds) for displaying previous lap tyre wear if `show_live_wear_difference` is enabled. Value range in `0` to `30` seconds. Default is `10` seconds.

    show_lifespan_laps
Show estimated tyre lifespan in laps.

    show_lifespan_minutes
Show estimated tyre lifespan in minutes.

    warning_threshold_remaining
Set warning threshold for total remaining tyre in percentage. Default is `30` percent.

    warning_threshold_wear
Set warning threshold for total amount tyre wear of last lap in percentage. Default is `3` percent.

    warning_threshold_laps
Set warning threshold for estimated tyre lifespan in laps. Default is `5` laps.

    warning_threshold_minutes
Set warning threshold for estimated tyre lifespan in minutes. Default is `5` laps.


## Virtual energy
**This widget displays virtual energy usage info. Most options are inherited from fuel widget, with some additions noted below.**

    *ratio
Show fuel ratio between estimated fuel and energy consumption, which can help balance fuel and energy usage, as well as providing refueling reference for adjusting pitstop `Fuel ratio` during race.

    *bias
Show fuel bias (estimated laps difference) between fuel and virtual energy. Positive value means more laps can be run on fuel than energy; in other words, energy is drained faster than fuel. General speaking, it is a good idea to keep bias close to `0.0` so that fuel and energy drains at same pace, and slightly towards positive side to avoid running out of fuel before energy does.


## Weather
**This widget displays weather info.**

    show_percentage_sign
Set `true` to show percentage sign for rain & wetness display.

    show_temperature
Show track & ambient temperature.

    show_rain
Show rain percentage.

    show_wetness
Show surface condition, minimum, maximum, and average wetness.


## Weather forecast
**This widget displays weather forecast info.**

    layout
2 layouts are available: `0` = show columns from left to right, `1` = show columns from right to left.

    show_estimated_time
Show estimated time reading for upcoming weather. Note, estimated time reading only works in time-based race. Other race type such as lap-based race shows `n/a` instead.

    show_ambient_temperature
Show estimated ambient temperature reading for upcoming weather.

    show_rain_chance_bar
Show visualized rain chance bar reading for upcoming weather.

    number_of_forecasts
Set number of forecasts to display. Value range in `1` to `4`. Default is `4` forecasts.

    show_unavailable_data
Show columns with unavailable weather data. Set `False` to auto hide columns with unavailable data. Note, auto hide only works for time-based race.


## Wheel alignment
**This widget displays camber and toe-in info.**

    show_camber
Show camber in degree.

    show_toe_in
Show toe-in in degree.
