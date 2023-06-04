*Note: the guide is for version 2.0 or higher.*

TinyPedal offers a wide range of customization options for widget & module controls, as well as preset management, which can be accessed from main window. Manual editing is also possible via `JSON` setting file with text editor.

All `JSON` setting files are located in `TinyPedal\settings` folder. Preset can be loaded or created via `Preset` tab in main window, and additional preset file management can be accessed from `Right-Click` context menu.

TinyPedal automatically saves setting when user makes any changes to widget position, or has toggled widget visibility, auto-hide, overlay-lock, etc. Any changes will only take effect after `Reload` preset, or clicked save button in `Config` dialog, or `Restart` APP.


## Backup file 
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


## Common Setting
    enable
This checks whether a widget or module will be loaded at startup.

    update_interval
This sets refresh rate for widget or module, value is in milliseconds. A value of `20` means refreshing every 20ms, which equals 50fps. Since most data from sharedmemory plugin is capped at 50fps, and most operation system has a roughtly 15ms minimum sleep time, setting value less than `10` will gain no benefit, and extreme low value could result significant increase of CPU usage.

    idle_update_interval
This sets refresh rate for module while its idle for conserving resources.

    position_x, position_y
Defines widget position on screen. Those values will be auto-saved.

    opacity
By default, all widgets have a 90% opacity setting, which equals value `0.9`. Lower value adds more transparency to widget. Acceptable value range is `0` to `1`.

    bar_gap, inner_gap
Set gap (screen pixel) between elements in a widget, only accept integer, `1` = 1 pixel.

    font_name
Mono type font is highly recommended. To set custom font, write `full font name` inside quotation marks. If a font name is invalid, a default fallback font will be used by program.

    font_size
Set font size, increase or decrease font size will also apply to widget size. Value only accept `integer`, do not put any decimal place.

    font_weight
Acceptable value: `normal` or `bold`.

    enable_auto_font_offset
Automatically adjust font vertical offset based on font geometry for better vertical alignment, and sould give good result in most case. This option is enabled by default. Set `false` to disable.

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


## Application
Application options can be accessed from `Window` menu in main window.

    show_at_startup
Show main window at startup, otherwise hides to tray icon.

    minimize_to_tray
Minimize to tray when user clicks `X` close button.

    remember_position
Remember last window position.


## Compatibility
Compatibility options can be accessed from `Config` menu in main window.

    enable_bypass_window_manager
Set `true` to bypass window manager on X11 system such as linux. This option may only be enabled if overlay widgets fail to stay on top of all windows. Also note that by enabling this option, OBS may not be able to capture overlay widgets in streaming. Default is `false`.


## Overlay
Overlay options can be accessed from `Overlay` menu in main window, or from tray icon menu.

    fixed_position
Check whether widget is locked at startup. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.

    auto_hide
Check whether auto hide is enabled. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.


## Display Units
Display units config dialog can be accessed from `Config` menu in main window.

    elevation_unit
2 unit types are available: `"Meter"`, `"Feet"`.

    fuel_unit
2 unit types are available: `"Liter"`, `"Gallon"`.

    odometer_unit
2 unit types are available: `"Kilometer"`, `"Mile"`, `"Meter"`.

    speed_unit
3 unit types are available: `"KPH"`, `"MPH"`, `"m/s"`.

    temperature_unit
2 unit types are available: `"Celsius"`, `"Fahrenheit"`.

    turbo_pressure_unit
3 unit types are available: `"bar"`, `"psi"`, `"kPa"`.

    tyre_pressure_unit
3 unit types are available: `"kPa"`, `"psi"`, `"bar"`.


## Global Font Override
Global font override config dialog can be accessed from `Config` menu in main window, which provides options to change font setting globally for all widgets.

    Font Name
Select a font name to replace `font_name` setting of all widgets. Default selection is `no change`, which no changes will be applied.

    Font Size Addend
Set a value that will be added (or subtracted if negative) to `font_size` value of all widgets. Default value is `0`, which no changes will be applied.

    Font Weight
Set font weight to replace `font_weight` setting of all widgets. Default selection is "no change", which no changes will be applied.


## Classes preset
Classes preset file is used for displaying name & color that matches specific vehicle classes.

Classes preset can be customized by editing `classes.json` file in `TinyPedal\settings` folder. This file will be generated only once after first time launch of the APP.

To modify or add new class, first find full class name of a vehicle, this can be done by a few ways:
* Looking at laptime data file located in `deltabest` folder, see `README.txt` in `deltabest` folder.
* Looking at class section of a mod's VEH file in MAS

Then, replace `WriteMatchedNameHere` with the found class name, and change `ReplaceClassNameHere` text to a desired class short name (better keep name less than 4 chars).

Last, set `color code` for the class, save and restart app.

More classes can be added following the JSON format, make sure that second last bracket doesn't have a comma after.

In case of typo errors within `classes.json` file, user will need to manually correct those typo errors in `classes.json` file.

To restore all classes settings back to default, just delete `classes.json` file.


## Heatmap preset
Heatmap preset file `heatmap.json` is used for displaying color that matches specific value range of telemetry data, such as brake and tyre temperature.

Heatmap preset can be customized by editing `heatmap.json` file in `TinyPedal\settings` folder. This file will be generated only once after first time launch of the APP.

To assign a heatmap preset to a specific widget, set `heatmap_name` value of the widget to the corresponding name defined in `heatmap.json` file.

In case of typo errors within `heatmap.json` file, the APP will automatically fall back to use default heatmap preset. User will need to manually correct those typo errors in `heatmap.json` file.

To restore all heatmap settings back to default, just delete `heatmap.json` file.

## User files
TinyPedal generates & saves various user data in specific folders. To reset a data file, simply delete the file from corresponding folder.

* Deltabest 
    Deltabest data is stored as `CSV` format (.csv extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.

* Fuel delta
    Fuel delta data is stored as `CSV` format (.fuel extension) under `TinyPedal\deltabest` folder. Those files can be opened in spreadsheet or notepad programs.

* Track map
    Track map is stored as `SVG` vector format (.svg extension) under `TinyPedal\trackmap` folder.

    The SVG vector map file contains two coordinate paths:
    * First is the global x,y position path, used for drawing track map.
    * Second is the corresponding track distance & elevation path, which is recorded for future use.

    Each sector position index is also stored in SVG file for finding sector coordinates.


# Modules
Modules here provide important data that updated in real-time for other widgets. Widgets may stop updating if corresponding modules were turned off. Module config dialog can be accessed by clicking `Config` button from `Module` tab in main window. 

## Delta
    module_delta
Enable delta module. This module provides deltabest & timing data.


## Force
    module_force
Enable force module. This module provides vehicle g force and downforce data.

    gravitational_acceleration
Set gravitational acceleration value (on earth).

    max_g_force_freeze_duration
Set freeze duration (seconds) for max g force reading.

    max_average_g_force_samples
Set amount samples for calculating max average g force.

    max_average_g_force_differece
Set g force differece threshold for calculating max average g force. Default is `0.2` g.


## Fuel
    module_fuel
Enable fuel module. This module provides vehicle fuel usage data.


## Hybrid
    module_hybrid
Enable hybrid module. This module provides vehicle battery usage & electric motor data.


## Mapping
    module_mapping
Enable mapping module. This module records and processes track map data.


## Relative
    module_relative
Enable relative module. This module provides vehicle relative data.


## Standings
    module_standings
Enable standings module. This module provides vehicle standings data.


# Widgets
Widget config dialog can be accessed by clicking `Config` button from `Widget` tab in main window.


## Battery
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
    decimal_places
Set amount decimal places to keep.

    show_front_and_rear
Show both front and rear bias. Default is `false`.

    show_percentage_sign
Set `true` to show percentage sign for brake bias value.


## Brake pressure
Show visualized percentage brake pressure of each wheel.


## Brake temperature
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


## Deltabest
    layout
2 layouts are available: `0` = delta bar above deltabest text, `1` = delta bar below deltabest text.

    color_swap
Swap time gain & loss color between font & background color.

    show_delta_bar
Show visualized delta bar.

    bar_length, bar_height
Set delta bar length & height in pixels.

    bar_display_range
Set max display range (gain or loss) for delta bar, accepts decimal place.

    show_animated_deltabest
Deltabest display follows delta bar progress.


## DRS
    font_color_activated, bkg_color_activated
Set color when DRS is activated by player.

    font_color_allowed, bkg_color_allowed
Set color when DRS is allowed but not yet activated by player.

    font_color_available, bkg_color_available
Set color when DRS is available but current disallowed to use.

    font_color_not_available, bkg_color_not_available
Set color when DRS is unavailable for current track or car.


## Electric motor
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


## Flag
    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    show_pit_timer
Show pit timer, and total amount time spent in pit after exit pit.

    pit_time_highlight_duration
Set highlight duration for total amount time spent in pit after exit pit.

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
Show yellow flag indicator and distance display which shows nearest yellow flag vehicle distance in meters.

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


## Force
    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_g_force
Show longitudinal & lateral G force with direction indicator.

    show_downforce_ratio
Show front vs rear downforce ratio. 50% means equal downforce; higher than 50% means front has more downforce.


## Friction circle
    display_size
Set widget size in pixels.

    display_radius_g
Set viewable g force range by radius(g).

    display_orientation
Set display orientation for longitudinal & lateral g force axis. Default value is `0`, which shows brake at top, acceleration at bottom, right-turn at left, left-turn at right. Set to `1` to inverted orientation.

    show_readings
Show values from g force reading. Value at top is current longitudinal g force, and value at bottom is max longitudinal g force. Value at left is max lateral g force, and value at right is current lateral g force.

    show_background
Show background color.

    background_style
Set background style. `0` for radial gradient style. `1` for solid style.

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
    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

    warning_color_low_fuel
Set low fuel color indicator, which changes widget background color when there is just 2 laps of fuel left.

    show_fuel_level_bar
Show visualized horizontal fuel level bar.

    fuel_level_bar_height
Set fuel level bar height in pixels.

    show_starting_fuel_level_mark
Show starting fuel level mark of current stint.

    starting_fuel_level_mark_width
Set starting fuel level mark width in pixels.


## Gear
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


## Instrument
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
    layout
2 layouts are available: `0` = vertical layout, `1` = reversed vertical layout.

    lap_time_history_count
Set the number of lap time history display. Default is to show `10` most recent lap times.

    show_empty_history
Show empty lap time history. Default is `false`, which hides empty rows.


## P2P
    show_battery_charge
Show percentage available battery charge.

    show_activation_timer
Show electric boost motor activation timer.

    activation_threshold_gear
Set minimum gear threshold for P2P ready indicator.

    activation_threshold_speed
Set minimum speed threshold for P2P ready indicator, unit in KPH.

    activation_threshold_throttle
Set minimum throttle input percentage threshold for P2P ready indicator, value range from `0.0` to `1.0`.

    minimum_activation_time_delay
Set minimum time delay between each P2P activation, unit in seconds.

    maximum_activation_time_per_lap
Set maximum P2P activation time per lap, unit in seconds.


## Pedal
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
    global_scale
Sets global scale of radar display. Default value is `6`, which is 6 times of original size.

    radar_radius
Set the radar display area by radius(unit meter). Default value is `30` meters. Minimum value is limited to `5`.

    vehicle_length, vehicle_width
Set vehicle overall size (length & width), value in meters.

    vehicle_border_radius
Set vehicle visual round border radius.

    vehicle_outline_width
Set vehicle visual outline width.

    show_overlap_indicator
Show overlap indicator when there is nearby side by side vehicle.

    overlap_detection_range_multiplier
Set overlap detection range multiplier that scales with vehicle width.

    indicator_size_multiplier
Set indicator visual size multiplier that scales with vehicle width.

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
    wheelbase
Set wheelbase in millimeters, for used in rake angle calculation.

    show_degree_sign
Set `true` to show degree sign for rake angle value.

    show_ride_height_difference
Show average front & rear ride height difference in millimeters.


## Relative
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

    show_vehicle_name
Show vehicle name.

    vehicle_name_uppercase
Set vehicle name to uppercase.

    vehicle_name_width
Set vehicle name display width, value in chars, such as 10 = 10 chars.

    show_time_gap
Show relative time gap between player and opponents. 

    time_gap_decimal_places
Set amount decimal places to keep.

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

    tyre_compound_list
Set custom tire compound index letter. One letter corresponds to one compound index. Note: since most vehicle mods don't share a common tire compound types or list order, it is impossible to have a tyre compound letter list that matches every car.

    show_pitstop_count
Show each driver's pitstop count.

    show_pit_request
Show pit request color indicator on pitstop count column.

    show_vehicle_in_garage_for_race
Show vehicles that are stored in garage stall during race (for example, DNF or DQ). Default is `false`.

    additional_players_front, additional_players_behind
Set additional players shown on relative list. Each value is limited to a maximum of 60 additional players (for a total of 120 additional players). Default value is `0`.


## Ride height
    ride_height_max_range
Set visualized maximum ride height range (millimeter).

    rideheight_offset*
Set ride height offset for bottoming indicator. Value in millimeters, but without decimal place.


## Sectors
    layout
2 layouts are available: `0` = target & current sectors above deltabest sectors, `1` = deltabest sectors above target & current sectors.

    target_time_mode
Set mode for accumulated target sector time. Set `0` to show theoretical best sector time from session best sectors. Set `1` to show sector time from personal best laptime.

    freeze_duration
Set freeze duration (seconds) for previous sector time display. Default value is `5` seconds.

    always_show_laptime_gap
Set `true` to always show sector/laptime gap bar. Set `false` to show only in freeze duration.

    show_speed
Show current lap fastest speed, and session fastest speed.

    speed_highlight_duration
Set duration (seconds) for highlighting new fastest speed. Default value is `5` seconds.

    last_sector_info
Store last saved sector info string of current session, not recommended for manual editing.


## Session
    show_system_clock
Show current system clock time.

    system_clock_format
Set clock format string. To show seconds, add `%S`, such as `"%H:%M:%S %p"`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

    show_session_timer
Show session timer, accuracy is limited by 200ms refresh rate of rF2 API.

    show_lapnumber
Show your current lap number & max laps (if available).

    bkg_color_maxlap_warn
Set warning color that shows 1 lap before exceeding max-lap in qualify (or indicates the last lap of a lap-type race).

    show_position
Show your current position against all drivers in a session.


## Standings
Most options are inherited from relative widget, with some additions noted below.

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

    time_gap_decimal_places
Set amount decimal places to keep.

    show_time_interval
Show time interval between each closest driver in order.

    time_interval_leader_text
Set text indicator for race leader in time interval column.

    show_laptime
For race session, this option shows driver's last lap time or pit timer if available. For other none race sessions, this option shows driver's session best lap time.


## Steering
    bar_width, bar_height
Set steering bar width & height in pixels.

    bar_edge_width
Set left and right edge boundary width.

    show_steering_angle
Show steering angle text in degree.

    show_scale_mark
This enables scale marks on steering bar.

    scale_mark_degree
Set gap between each scale mark in degree. Default is `90` degree. Minimum value is limited to `10` degree.


## Stint history
    layout
2 layouts are available: `0` = vertical layout, `1` = reversed vertical layout.

    stint_history_count
Set the number of stint history display. Default is to show `2` most recent stints.

    show_empty_history
Show empty stint history. Default is `false`, which hides empty rows.

    minimum_stint_threshold_minutes
Set the minimum stint time threshold in minutes for updating stint history. This only affects ESC.

    tyre_compound_list
Set custom tire compound index letter. One letter corresponds to one compound index.


## Timing
    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_session_best
Show current session best laptime from all vehicle classes.

    show_session_best_from_same_class_only
Show current session best laptime from same vehicle class only.

    show_best
Show personal best laptime.

    show_last
Show personal last laptime.

    show_current
Show personal current laptime.

    show_estimated
Show personal current estimated laptime.


## Track map
    show_background
Show track map background.

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
Show vehicle standings info on map.


## Tyre load
Show visualized tyre load display.

    show_tyre_load_ratio
Show percentage ratio of tyre load between each and total tyre load. Set `false` to show individual tyre load in Newtons.


## Tyre pressure
Show tyre pressure of each wheel.


## Tyre temperature
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

    tyre_compound_list
Set custom tire compound index letter. One letter corresponds to one compound index.


## Tyre wear
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
    show_percentage_sign
Set `true` to show percentage sign for rain & wetness display.

    show_temperature
Show track & ambient temperature.

    show_rain
Show rain percentage.

    show_wetness
Show surface condition, minimum, maximum, and average wetness.


## Wheel alignment
    show_camber
Show camber in degree.

    show_toe_in
Show toe-in in degree.
