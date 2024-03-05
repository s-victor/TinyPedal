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

Any boolean type value (true or false) will only accept: `true`, which can be substituted with `1`. And `false`, which can be substituted with `0`. All words must be in `lowercase`, otherwise will cause error.

Also important to note, not every setting allows float point value that contains decimal places. Usually if a number (default value) does not contain any decimal place, that means it only accepts `integer`. Make sure not to add any decimal place, otherwise error may occur.


## Brands preset
**Brands preset is used for displaying brand name that matches specific vehicle name.**

Brands preset can be customized by accessing `Vehicle brand editor` from `Config` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

`brands.json` file will be generated and saved in `TinyPedal\settings` folder after first time launch of the APP.

To modify brands setting, open `Vehicle brand editor` and edit entries from each rows and columns. Each row represents a vehicle. First column is full vehicle name that must match in-game vehicle name. Second column is brand name.

To import vehicle brand data, click `Import` button. Imported data will be appended on top of existing data, and same existing data will be updated with new name.

    How to export vehicle brand data from RF2 API:
    1. Start RF2, then open following link in web browser:
    localhost:5397/rest/race/car
    2. Click "Save" button which saves vehicle data to JSON file.

    How to export vehicle brand data from LMU API:
    1. Start LMU, then open following link in web browser:
    localhost:6397/rest/sessions/getAllAvailableVehicles
    2. Click "Save" button which saves vehicle data to JSON file.

Note, the importing feature is experimental, and currently only tested with LMU. Maximum importing file size is limited to 5mb.

To add new brand name, click `Add` button. Note, the editor can auto-detect and fill-in player's full vehicle name from current active session.

To sort brand name in orders, click `Sort` button.

To batch rename brand name, click `Rename` button.

To remove a brand name, click `X` button of a row.

To reset all brands setting to default, click `Reset` button; or manually delete `brands.json` file.


## Classes preset
**Classes preset is used for displaying name & color that matches specific vehicle classes.**

Classes preset can be customized by accessing `Vehicle class editor` from `Config` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

`classes.json` file will be generated and saved in `TinyPedal\settings` folder after first time launch of the APP.

To modify class setting, open `Vehicle class editor` and edit entries from each rows and columns. Each row represents a vehicle class. First column is full vehicle class name that must match in-game vehicle class name. Second column is abbreviation name. Third column is color (HEX code). Double-click on color to open color dialog.

To add new class, click `Add Class` button. Note, the editor can auto-detect and fill-in player's full vehicle class name from current active session.

To remove a class, click `X` button of a row.

To reset all classes setting to default, click `Reset` button; or manually delete `classes.json` file.


## Heatmap preset
**Heatmap preset is used for displaying color that matches specific value range of telemetry data, such as brake and tyre temperature.**

Heatmap preset can be customized by accessing `Heatmap editor` from `Config` menu in main window. Note, any changes will only be saved and take effect after clicking `Apply` or `Save` Button.

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


## User files
TinyPedal generates & saves user session data in specific folders. Session data can be reset by accessing `Reset data` submenu from `Overlay` menu in main window; or, delete data file from corresponding folder.

* Deltabest  
    Deltabest data is stored as `CSV` format (.csv extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.

* Fuel delta  
    Fuel delta data is stored as `CSV` format (.fuel extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.

* Track map  
    Track map is stored as `SVG` vector image format (.svg extension) under `TinyPedal\trackmap` folder.

    The SVG vector map file contains two coordinate paths:
    * First is the global x,y position path, used for drawing track map.
    * Second is the corresponding track distance & elevation path, which is recorded for future use.

    Each sector position index is also stored in SVG file for finding sector coordinates.


# Command line arguments
**Command line arguments can be passed to script or executable to enable additional features.**

    --log-level
Set logging output level. Supported values are:
  * `--log-level=0` outputs only warning or error log to `console`.
  * `--log-level=1` outputs all log to `console`.
  * `--log-level=2` = outputs all log to both `console` and `tinypedal.log` file.

Log file location:
  * On windows, `tinypedal.log` is located under APP root folder.
  * On linux, `tinypedal.log` is located under `/home/.config/TinyPedal/` folder.

Default logging output level is set on `1` if argument is not set.

Example usage: `python .\run.py --log-level=2` or `.\tinypedal.exe --log-level=2`


# General options
**General options can be accessed from main window menu.**

## Common terms and keywords
**These are the commonly used setting terms and keywords.**

    enable
This checks whether a widget or module will be loaded at startup.

    update_interval
This sets refresh rate for widget or module, value is in milliseconds. A value of `20` means refreshing every 20ms, which equals 50fps. Since most data from sharedmemory plugin is capped at 50fps, and most operation system has a roughly 15ms minimum sleep time, setting value less than `10` has no benefit, and extreme low value may result significant increase of CPU usage.

    idle_update_interval
This sets refresh rate for module while its idle for conserving resources.

    position_x, position_y
Defines widget position on screen (in pixels). Those values will be auto updated and saved.

    opacity
By default, all widgets have a 90% opacity setting, which equals value `0.9`. Lower value adds more transparency to widget. Acceptable value range in `0.0` to `1.0`.

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
Manually set font vertical offset. Default value is `0`. Negative value will offset font upward, and position value for downward. This option only takes effect when `enable_auto_font_offset` is set to `false`.

    bar_padding
Set widget edge padding value that multiplies & scales with `font_size`. Default is `0.2` for most widgets.

    color
Set color in hexadecimal color codes with alpha channel support (optional and can be omitted). The color code format starts with `#`, then follows by two-digit hexadecimal numbers for each channel in the order of alpha, red, green, blue. User can select a new color without manual editing, by double-clicking on color entry box in `Config` dialog.

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
Set grid size for grid move, value in pixel. Default value is `8` pixel. Minimum value is limited to `1`.


## Shared memory API
**Shared Memory API options can be accessed from `Config` menu in main window. Some options may only be relevant to certain API.**

    api_name
Set API name for accessing data from supported API.

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
Set character encoding for displaying text in correct encoding. Available encoding: `UTF-8`, `ISO-8859-1`. Default encoding is `UTF-8`, which works best in LMU game. Note, `UTF-8` may not work well for some Latin characters in RF2, try use "ISO-8859-1" instead.


## Units and symbols
**Units and symbols options can be accessed from `Config` menu in main window.**

    distance_unit
2 unit types are available: `"Meter"`, `"Feet"`.

    fuel_unit
2 unit types are available: `"Liter"`, `"Gallon"`.

    odometer_unit
3 unit types are available: `"Kilometer"`, `"Mile"`, `"Meter"`.

    speed_unit
3 unit types are available: `"KPH"`, `"MPH"`, `"m/s"`.

    temperature_unit
2 unit types are available: `"Celsius"`, `"Fahrenheit"`.

    turbo_pressure_unit
3 unit types are available: `"bar"`, `"psi"`, `"kPa"`.

    tyre_pressure_unit
3 unit types are available: `"kPa"`, `"psi"`, `"bar"`.

    tyre_compound_symbol
Set custom tire compound index letter. One letter corresponds to one compound index. Note: since most vehicle mods don't share a common tire compound types or list order, it is impossible to have a tyre compound letter list that matches every vehicle.


## Global font override
**Global font override options can be accessed from `Config` menu in main window, which allow changing font setting globally for all widgets.**

    Font Name
Select a font name to replace `font_name` setting of all widgets. Default selection is `no change`, which no changes will be applied.

    Font Size Addend
Set a value that will be added (or subtracted if negative) to `font_size` value of all widgets. Default value is `0`, which no changes will be applied.

    Font Weight
Set font weight to replace `font_weight` setting of all widgets. Default selection is `no change`, which no changes will be applied.


## Spectate mode
**Spectate mode can be accessed from `Spectate` tab in main window.**

Click `Enabled` or `Disabled` button to toggle spectate mode on & off. Note, spectate mode can also be enabled by setting `enable_player_index_override` option to `true` in `Shared Memory API` config.

While Spectate mode is enabled, `double-click` on a player name in the list to access telemetry data and overlay readings from selected player; alternatively, select a player name and click `Spectate` button. Current spectating player name is displayed on top of player name list.

Select `Anonymous` for unspecified player, which is equivalent to player index `-1` in JSON file.

Click `Refresh` button to manually refresh player name list.


# Modules
Modules provide important data that updated in real-time for other widgets. Widgets may stop updating or receiving readings if corresponding modules were turned off. Each module can be configured by accessing `Config` button from `Module` tab in main window.


## Delta
**This module provides deltabest & timing data.**

    module_delta
Enable delta module.


## Force
**This module provides vehicle g force and downforce data.**

    module_force
Enable force module.

    gravitational_acceleration
Set gravitational acceleration value (on earth).

    max_g_force_freeze_duration
Set freeze duration (seconds) for max g force reading.

    max_average_g_force_samples
Set amount samples for calculating max average g force. Minimum value is limited to `3`.

    max_average_g_force_difference
Set max average g force difference threshold which compares with the standard deviation calculated from max average g force samples. Default is `0.2` g.


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


## Sectors
**This module provides sectors timing data.**

    module_sectors
Enable sectors module.

    sector_info
Store last saved sector info string of current session, not for manual editing.


## Vehicles
**This module provides additional processed vehicles data.**

    module_vehicles
Enable vehicles module.

    lap_difference_ahead_threshold
Lap difference (percentage) threshold for tagging opponents as ahead. Default value is `0.9` lap.

    lap_difference_behind_threshold
Lap difference (percentage) threshold for tagging opponents as behind. Default value is `0.9` lap.


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
Set freeze duration (seconds) for previous lap drained/regenerated battery charge display. Default value is `10` seconds.


## Brake bias
**This widget displays brake bias info.**

    show_front_and_rear
Show both front and rear bias. Default is `false`.

    show_percentage_sign
Set `true` to show percentage sign for brake bias value.


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
Set duration (seconds) for highlighting average brake temperature from previous lap after crossing start/finish line. Default value is `5` seconds.


## Cruise
**This widget displays track clock, compass, elevation, odometer info.**

    show_track_clock
Show current in-game clock time of the circuit.

    track_clock_time_scale
Set time multiplier for time-scaled session. Default value is `1`, which matches `Time Scale: Normal` setting in-game.

    track_clock_format
Set track clock format string. To show seconds, add `%S`, such as `"%H:%M:%S %p"`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

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

    color_swap
Swap time gain & loss color between font & background color.

    show_delta_bar
Show visualized delta bar.

    bar_length, bar_height
Set delta bar length & height in pixels.

    bar_display_range
Set max display range (gain or loss) in seconds for delta bar, accepts decimal place. Default value is `2` seconds.

    delta_display_range
Set max display range (gain or loss) in seconds for delta reading, accepts decimal place. Default value is `99.999` seconds.

    show_animated_deltabest
Deltabest display follows delta bar progress.


## Deltabest extended
**This widget displays deltabest info against multiple lap time sources.**

    show_all_time_deltabest
Show deltabest against personal all time best lap time.

    show_session_deltabest
Show deltabest against current personal session best lap time. Note: session deltabest will be reset upon changing session, or reload preset/restart APP.

    show_stint_deltabest
Show deltabest against current personal stint best lap time. Note: stint deltabest will be reset upon entering pit.

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

    show_boost_motor_temp
Show boost motor temperature.

    show_boost_water_temp
Show boost motor cooler water temperature.

    show_boost_motor_rpm
Show boost motor RPM.

    show_boost_motor_torque
Show boost motor torque.

    overheat_threshold_motor, overheat_threshold_water
Set temperature threshold for boost motor & water overheat color indicator, unit in Celsius.


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
Show low fuel indicator when fuel level is below certain amount value.

    show_low_fuel_for_race_only
Only show low fuel indicator during race session.

    low_fuel_volume_threshold
Set fuel volume threshold to show low fuel indicator when total amount of remaining fuel is equal or less than this value. This value takes consideration from `fuel_unit` setting of Fuel Widget. For example, if `fuel_unit` is set to gallon, then this value should also be set using gallon unit. The purpose of this setting is to limit low fuel warning when racing on lengthy tracks, where fuel tank may only hold for a lap or two. Default value is `20`.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

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
Set display duration(seconds) for green flag text before it disappears. Default value is `3`.

    red_lights_text
Set custom text for red lights.

    green_flag_text
Set custom text for green flag.

    show_traffic
Show incoming on-track traffic indicator (time gap) while in pit lane or after pit-out.

    traffic_maximum_time_gap
Set maximum time gap (seconds) of incoming on-track traffic.

    traffic_pitout_duration
Set traffic indicator extended duration (seconds) after pit-out.

    show_pit_request
Show pit request state.

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
Set display orientation for longitudinal & lateral g force axis. Default value is `0`, which shows brake at top, acceleration at bottom, right-turn at left, left-turn at right. Set to `1` to inverted orientation.

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

    *mins
Estimated minutes reading that current fuel can last.

    *save
Estimated fuel consumption reading for one less pit stop.

    *pits
Estimate number of pit stop counts when making a pit stop at end of current stint. Any non-zero decimal places would be considered for an additional pit stop.

    bar_width
Set each column width, value in chars, such as 10 = 10 chars. Default value is `5`. Minimum width is limited to `3`.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

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


## Gear
**This widget displays gear, RPM, speed, battery info.**

    inner_gap
Set inner gap between gear & speed readings. Negative value reduces gap, while positive value increases gap. Default value is `0`.

    show_speed
Show speed reading.

    show_speed_below_gear
Show speed reading below gear.

    font_scale_speed
Set font scale for speed reading. This option only takes effect when `show_speed_below_gear` is enabled. Default value is `0.5`.

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
Set speed/time threshold value for neutral gear color warning, which activates color warning when speed & time-in-neutral is higher than threshold. Speed unit in meters per second, default value is `28`. Time unit in seconds, default value is `0.3` seconds.


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
Set percentage threshold for triggering wheel lock warning under braking. `0.2` means 20% of tyre slip ratio.

    wheel_slip_threshold
Set percentage threshold for triggering wheel slip warning. `0.1` means 10% of tyre slip ratio.

    last_wheel_radius_front, last_wheel_radius_rear
Set radius for front and rear wheels, which is used to calculate tyre slip ratio. Manual editing is not required, as this value will be automatically calculated during driving, and will be auto-saved to `JSON` file.

    minimum_speed
Set minimum speed threshold for calculating wheel radius samples. Default value is `16.5` (m/s),


## Lap time history
**This widget displays lap time history info.**

    layout
2 layouts are available: `0` = vertical layout, `1` = reversed vertical layout.

    lap_time_history_count
Set the number of lap time history display. Default is to show `10` most recent lap times.

    show_empty_history
Show empty lap time history. Default is `false`, which hides empty rows.


## Navigation
**This widget displays a zoomed navigation map that centered on player's vehicle. Note: at least one complete & valid lap is required to generate track map.**

    display_size
Set widget size in pixels.

    view_radius
Set viewable area by radius(unit meter). Default value is `500` meters. Minimum value is limited to `5`.

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
Sets global scale of radar display. Default value is `6`, which is 6 times of original size.

    radar_radius
Set the radar display area by radius(unit meter). Default value is `30` meters. Minimum value is limited to `5`.

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

    distance_circle_style
Set distance circle line style. `0` for dashed line, `1` for solid line.

    distance_circle_1_radius, distance_circle_2_radius
Set distance circle size by radius(unit meter). Circle will not be displayed if radius is bigger than `radar_radius`.

    distance_circle_1_width, distance_circle_2_width
Set distance circle line width in pixels.

    auto_hide
Auto hides radar display when no nearby vehicles.

    auto_hide_time_threshold
Set amount time(unit second) before triggering auto hide. Default value is `1` second.

    minimum_auto_hide_distance
Set minimum straight line distance(unit meter) before triggering auto hide. Set `-1` value to auto scale with `radar_radius` value. Default value is `-1`.


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

    driver_name_uppercase
Set driver name to uppercase.

    driver_name_width
Set drive name display width, value in chars, such as 10 = 10 chars.

    driver_name_align_center
Align driver name in the center when enabled. Default is left alignment when disabled.

    show_vehicle_name
Show vehicle name.

    show_vehicle_brand_as_name
Show vehicle brand name instead of vehicle name. If brand name does not exist, vehicle name will be displayed instead.

    vehicle_name_uppercase
Set vehicle name to uppercase.

    vehicle_name_width
Set vehicle name display width, value in chars, such as 10 = 10 chars.

    vehicle_name_align_center
Align vehicle name in the center when enabled. Default is left alignment when disabled.

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
Set additional players shown on relative list. Each value is limited to a maximum of 60 additional players (for a total of 120 additional players). Default value is `0`.


## Ride height
**This widget displays visualized ride height info.**

    ride_height_max_range
Set visualized maximum ride height range (millimeter).

    rideheight_offset*
Set ride height offset for bottoming indicator. Value in millimeters, but without decimal place.


## Sectors
**This widget displays sectors timing info.**

    layout
2 layouts are available: `0` = target & current sectors above deltabest sectors, `1` = deltabest sectors above target & current sectors.

    target_time_mode
Set mode for accumulated target sector time. Set `0` to show theoretical best sector time from session best sectors. Set `1` to show sector time from personal best lap time.

    freeze_duration
Set freeze duration (seconds) for previous sector time display. Default value is `5` seconds.

    always_show_laptime_gap
Set `true` to always show sector/lap time gap bar. Set `false` to show only in freeze duration.


## Session
**This widget displays system clock, session name, timing, lap number, overall position info.**

    show_session_name
Show current session name that includes testday, practice, qualify, warmup, race.

    session_text_*
Set custom session name text.

    show_system_clock
Show current system clock time.

    system_clock_format
Set clock format string. To show seconds, add `%S`, such as `"%H:%M:%S %p"`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

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
Set maximum amount vehicles to display, which takes effect when in multi-class session and `enable_multi_class_split_mode` is enabled. If total vehicle number is above this value, any extra vehicles will not be shown. Default value is `50`, which is sufficient in most case.

    min_top_vehicles
Set minimum amount top place vehicles to display. This value has higher priority than other `max_vehicles` settings. Default value is `3`, which always shows top 3 vehicles if present.

    enable_multi_class_split_mode
Enable multi-class split mode, which splits and displays each vehicle class in separated groups. This mode will only take effect when there is more than one vehicle class present in a session, otherwise it will automatically fall back to normal single class mode.

    max_vehicles_per_split_player
Set maximum amount vehicles to display for class where player is in. Default value is `7`. Note that, if player is not in first place, then at least one opponent ahead of player will always be displayed, even if this value sets lower.

    max_vehicles_per_split_others
Set maximum amount vehicles to display for classes where player is not in. Default value is `3`.

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
Show personal best lap time.

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


## Track map
**This widget displays track map and standings. Note: at least one complete & valid lap is required to generate track map.**

    show_background
Show widget background.

    show_map_background
Show background of the inner map area. This option only works for circular type tracks.

    area_size
Set area display size.

    area_margin
Set area margin size.

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

    show_reference_line
Show reference line.

    reference_line_*_style
Set reference line vertical offset relative to pedal, value in percentage.

    reference_line_*_style
Set reference line style. `0` for solid line, `1` for dashed line.

    reference_line_*_width
Set reference line width in pixels. Set value to `0` to hide line.


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
Set time interval (in seconds) for rate of change calculation. Default interval is `5` seconds. Minimum interval is limited to `1` second, maximum interval is limited to `60` seconds.

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
Set freeze duration (seconds) for previous lap tyre wear info if `show_live_wear_difference` is enabled.

    show_lifespan
Show estimated tyre lifespan in laps.

    warning_threshold_remaining
Set warning threshold for total remaining tyre in percentage. Default is `30` percent.

    warning_threshold_wear
Set warning threshold for total amount tyre wear of last lap in percentage. Default is `3` percent.

    warning_threshold_laps
Set warning threshold for estimated tyre lifespan in laps. Default is `5` laps.


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


## Wheel alignment
**This widget displays camber and toe-in info.**

    show_camber
Show camber in degree.

    show_toe_in
Show toe-in in degree.
