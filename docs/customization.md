# Customization Guide

TinyPedal offers a wide range of customization, which is currently available by editing `.JSON` setting file with text editor.

Starting from version 1.9.0, TinyPedal comes with a new `Preset Manager` that let user to load or create setting preset. All `.JSON` setting files are located in `TinyPedal\settings` folder. Preset can be switched or created via tray icon menu `Load Preset`, which opens `Preset Manager` window.

Note: for version older than 1.9.0, `.JSON` files are located in TinyPedal root folder.

TinyPedal will auto-save setting when user makes any changes to widget position, or has toggled widget visibility, auto-hide, overlay-lock. Due to this reason, to avoid losing changes, it is recommended to quit APP before editing or saving JSON file. Any changes will only take effect after reloading preset or restarting APP.


## Backup file 
TinyPedal will automatically create a backup file with time stamp suffix if old setting file is invalid, and a new default `.JSON` will be generated.

A newer released version will auto-update old setting and add new setting after loading. It is still recommended to manually create backups before updating.


## Editing Notes
To make changes, editing `values` on the right side of colon.

Do not modify anything (keys) on the left side of colon, any changes to those keys will be reverted back to default setting by APP.

If APP fails to launch after editing `.JSON`, check for typo error or invalid values; or delete `.JSON` to let APP generate a new default file.

If a value is surrounded by quotation marks, make sure not to remove those quotation marks, otherwise may cause error.

Any boolean type value (true or false) will only accept: `true`, which can be substituted with `1`. And `false`, which can be substituted with `0`. All words must be in `lowercase`, otherwise will have no effect.

Color value is in web colors format (hexadecimal color codes), which starts with `#` number sign. Various image editors or online tools can generate those color codes.

If a number (default value) does not contain any decimal place, that means it only accepts `integer`. Make sure not to add any decimal place, otherwise error will occur.


## Common Setting

    enable
This checks whether a widget will be loaded at startup. It can also be accessed and changed from tray icon `Widgets` submenu.

    update_delay
This sets widget refresh rate, value is in milliseconds. A value of `20` means refresh every 20ms, which equals 50fps. Since most data from sharedmemory plugin is capped at 50fps, setting any value less than `10` will not gain any benefit, and could result significant increase of CPU usage.

    position_x, position_y
Defines widget position on screen. Those values will be auto-saved by app, no need to manually set.

    opacity
By default, all widgets have a 90% opacity setting, which equals `0.9` value. Lower value adds more transparency to widget.

    bar_gap
Set gap (screen pixel) between elements in a widget, only accept integer, `1` = 1 pixel.

    font_name
Mono type font is highly recommended. To set custom font, write `full font name` inside quotation marks. If a font name is invalid, a default fallback font will be used by program.

    font_size
Set font size, increase or decrease font size will also apply to widget size. Value only accept `integer`, do not put any decimal place.

    font_weight
Acceptable value: `normal` or `bold` .

    font_color
Those are for font color.

    bkg_color
Those are for background color.

    column_index_*
Set order of each info column(or row). Must keep index number unique to each column, otherwise columns will overlap.


## Overlay

    fixed_position
Check whether widget is locked at startup. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.

    auto_hide
Check whether auto hide is enabled. This setting can be toggled from tray icon menu. Valid value: `true`, same as `1`. `false`, same as `0`.

    delta_module
Enable delta timing module. This module provides timing data for `Delta best` and `Timing` widgets, which returns value 0 if turned off.

    fuel_module
Enable fuel calculation module. This module provides vehicle fuel usage data for `Fuel` and other widgets, which returns nothing if turned off.

    relative_module
Enable relative calculation module. This module provides vehicle relative data for `Relative` and `Radar` widgets, which returns nothing if turned off.

    hover_color_1, hover_color_2
Define color of hover cover when mouse cursor is above widget (when not locked).

    transparent_color
Define global transparent background color. Default value is `"#000002"`. This setting is meant to be used by none-Windows platform where transparent background color is not supported, and user may customize a substitute color.


## Cruise
    show_track_clock
Show current in-game clock time of the circuit.

    track_clock_time_scale
Set time multiplier for time-scaled session. Default value is `1`, which matches "Time Scale: Normal" setting in-game.

    track_clock_format
Set track clock format string. To show seconds, add `%S`, such as `"%H:%M:%S %p"`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

    show_elevation
Show elevation difference in game's coordinate system.

    elevation_unit
2 unit types are available: `0` = meter, `1` = feet.

    show_odometer
Show odometer that displays total driven distance of local player. 

    odometer_unit
2 unit types are available: `0` = kilometer, `1` = mile.

    meters_driven
This value holds the total distance(meters) that local player has driven. Accept manual editing.


## Deltabest
    layout
2 layouts are available: `0` = delta bar above deltabest text, `1` = delta bar below deltabest text.

    color_swap
Swap time gain & loss color between font & background color.

    show_delta_bar
Show visualized delta bar.

    bar_length_scale, bar_height_scale
Scale delta bar length & height, accepts decimal place.

    bar_display_range
Set max display range (gain or loss) for delta bar, accepts decimal place.


## DRS
    font_color_activated, bkg_color_activated
Set color when DRS is activated by player.

    font_color_allowed, bkg_color_allowed
Set color when DRS is allowed but not yet activated by player.

    font_color_available, bkg_color_available
Set color when DRS is available but current disallowed to use.

    font_color_not_available, bkg_color_not_available
Set color when DRS is unavailable for current track or car.


## Engine
    temp_unit
2 unit types are available: `0` = Celsius, `1` = Fahrenheit

    overheat_threshold_oil, overheat_threshold_water
Set temperature threshold for oil & water overheat color indicator, unit in Celsius.

    bkg_color_overheat
Set oil & water overheat color indicator.

    show_turbo_pressure
Show turbo pressure.

    turbo_pressure_unit
3 unit types are available: `0` = bar, `1` = psi, `2` = kPa.

    show_rpm
Show engine RPM.


## Force
    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_downforce_ratio
Show front vs rear downforce ratio. 50% means equal downforce; higher than 50% means front has more downforce.


## Fuel
    show_caption
Show short caption description besides each info block.

    bkg_color_low_fuel
Set low fuel color indicator, which changes widget background color when there is just 2 laps of fuel left.

    fuel_unit
2 unit types are available: `0` = liters, `1` = gallons. This setting affects all widgets that use fuel data.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

## Gear
    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    speed_unit
3 unit types are available: `0` = KPH, `1` = MPH, `2` = m/s.

    speed_limiter_text
Set custom pit speed limiter text which shows when speed limiter is engaged. 

    show_rpm_bar
Show a RPM bar at bottom of gear widget, which moves when RPM reaches range between safe & max RPM.

    rpm_bar_gap
The gap between RPM bar & gear widget, in pixel.

    rpm_bar_height
RPM bar height, in pixel.

    rpm_bar_edge_height
A visible thin edge line, in pixel, set `0` to hide this line.

    rpm_safe_multiplier
This value multiplies max RPM value, which sets a relative safe RPM range for RPM color indicator (changes gear widget background color upon reaching this RPM value).

    rpm_warn_multiplier
This value multiplies max RPM value, which sets a relative near-max RPM range for RPM color indicator.

    bkg_color_rpm_over_rev
This sets the color for over-rev warning indicator.

    show_startlights
Show race start lights indicator during countdown game phase for standing-type start only(includes formation/standing).

    red_lights_text
Set custom text for red lights. 

    green_flag_text
Set custom text for green flag. 

    green_flag_duration
Set display duration(seconds) for green flag text before it disappears. Default value is `3`.

    show_start_countdown
Show race start countdown timer during countdown game phase for standing-type start only(includes formation/standing). CHECK LEAGUE and RACE RULES first before enabling it! This option can potentially create unfair advantages against who doesn't use it! Disabled by Default, set `"THIS_MAY_CREATE_UNFAIR_ADVANTAGES"` to enable. 

    show_low_fuel
Show low fuel indicator when fuel level is below certain amount value.

    low_fuel_for_race_only
Only show low fuel indicator during race session.

    low_fuel_volume_threshold
Set fuel volume threshold to show low fuel indicator when total amount of remaining fuel is equal or less than this value. This value takes consideration from `fuel_unit` setting of Fuel Widget. For example, if `fuel_unit` is set to gallon, then this value should also be set using gallon unit. The purpose of this setting is to limit low fuel warning when racing on lengthy tracks, where fuel tank may only hold for a lap or two. Default value is `20`.

    low_fuel_lap_threshold
Set amount lap threshold to show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

    show_blue_flag
Show blue flag indicator.

    blue_flag_for_race_only
Only show blue flag indicator during race session.

    blue_flag_text
Set custom blue flag text. 

    show_yellow_flag
Show yellow flag indicator of each affected sector.

    yellow_flag_for_race_only
Only show yellow flag indicator during race session.


## Instrument
    icon_size
Set size of instrument icon in pixel. Minimum value is limited to `16`.

    layout
2 layouts are available: `0` = horizontal layout, `1` = vertical layout.

    warning_color_*
Set warning color for each icon, which shows when conditions are met.

    wheel_lock_threshold
Set percentage threshold for triggering wheel lock warning under braking. `0.2` means 20% of tyre slip ratio.

    wheel_slip_threshold
Set percentage threshold for triggering wheel slip warning. `0.1` means 10% of tyre slip ratio.

    wheel_radius_front, wheel_radius_rear
Set radius for front and rear wheels, which is used to calculate tyre slip ratio. Manual editing is not required, as this value will be automatically calculated based on a special algorithm after player has completed a full lap, and will be auto-saved to `.JSON` file.

    minimum_speed
Set minimum speed threshold before APP records and calculates wheel radius samples. Default value is `16.5` (m/s),

    minimum_samples
Set minimum number of radius samples that required for calculating average wheel radius. Default value is `400`. Minimum value is limited to `100`.


## Pedal
    bar_length_scale, bar_width_scale
Scale pedal bar length & width, accepts decimal place.

    full_pedal_height
This is the indicator height when pedal reaches 100% travel, value in pixel.

    show_average_brake_pressure
Show average brake pressure changes applied on all wheels, which auto scales with max brake pressure and indicates average amount brake released by ABS on all wheels. This option is enabled by default, which replaces game's filtered brake input that cannot show ABS.

    show_ffb_meter
This enables Force Feedback meter.

    ffb_clipping_color
Set Force Feedback clipping color.


## Pressure
    pressure_unit
3 unit types are available: `0` = kPa, `1` = psi, `2` = bar.

    show_tyre_load
This enables Tyre Load display.

    show_tyre_load_ratio
Show percentage ratio of tyre load between each and total tyre load. Set `false` to show individual tyre load in Newtons.


## Radar
    area_scale
Set radar area size multiplier. Higher value extends widget size & visible area. This value does not change vehicle size. Minimum value is limited to `0.5`.

    vehicle_length, vehicle_width
Set vehicle overall size (length & width), value in meters.

    vehicle_scale
Set vehicle size scale for displaying, this affects both vehicle size and relative distance between other vehicles (like zoom). Default value is `0.6`, which is 60% of original scale.

    bkg_color
Set radar background color. Default value is `"#000002"`, which makes background fully transparent.

    player_color
Set player vehicle color. Default value is `"#000002"`, which makes background fully transparent.

    player_outline_color, player_outline_width
Set outline color & width of player vehicle.

    opponent_color
Set opponent vehicle color.

    opponent_color_laps_ahead, opponent_color_laps_behind
Set color for opponent vehicle that is laps ahead or behind player vehicle.

    show_center_mark
Show center mark on radar.

    additional_vehicles_front, additional_vehicles_behind
Set additional visible vehicles. The value is limited to a maximum of 9 additional vehicles for each front & behind setting. Default value is `4`.


## Relative
    font_color_laps_ahead, font_color_laps_behind
Set font color for opponent vehicle that is laps ahead or behind player vehicle.

    driver_name_mode
Set driver name display mode. Default value is `0`, which displays driver name. Set to `1` to display vehicle(livery) name. Set to `2` to display both driver name & vehicle name combined.

    bar_driver_name_width
Set drive name display width, value in chars, such as 18 = 18 chars.

    show_laptime
Show driver's last laptime.

    show_class
Show vehicle class categories. Class name & color are fully customizable, by editing `classes.json`.

First, find full class name of a vehicle, this can be done by a few ways:
* Looking at laptime data file located in `deltabest` folder, see `README.txt` in `deltabest` folder.
* Looking at class section of a mod's VEH file in MAS
* Increase `bar_class_name_width` value to reveal full class name.

Then, replace `WriteMatchedNameHere` with the found class name, and change `ReplaceClassNameHere` text to a desired class short name (better keep name less than 4 chars).

Last, set `color code` for the class, save and restart app.

You can add more classes following the JSON format, make sure that second last bracket doesn't have a comma after. Also note that, app will not verify, nor to edit `classes.json` after it was created, so you will have to make sure everything typed in the file is correct.

    bar_class_name_width
Set class name display width, value is in chars, 4 = 4 chars wide.

    bar_time_gap_width
Set time gap display width, value is in chars, 5 = 5 chars wide.

    show_position_in_class
Show driver's position standing in class.

    show_pit_status
Show indicator whether driver is currently in pit.

    pit_status_text
Set custom pit status text which shows when driver is in pit. 

    show_tyre_compound
Show tyre compound index (front/rear).

    tyre_compound_list
Set custom tire compound index letter. One letter for one compound index. Note: since most vehicle mods don't share a common tire compound types or list order, it is impossible to have a tyre compound letter list that matches every car.

    show_pitstop_count
Show each driver's pitstop count.

    additional_players_front, additional_players_behind
Set additional players shown on relative list. The value is limited to a maximum of 3 additional players for each front & behind setting. Default value is `0`.


## Sectors
    layout
2 layouts are available: `0` = target & current sectors above deltabest sectors, `1` = deltabest sectors above target & current sectors.

    target_time_mode
Set mode for accumulated target sector time. Set `0` to show theoretical best sector time from session best sectors. Set `1` to show sector time from personal best laptime.

    freeze_duration
Set auto-freeze duration (seconds) for previous sector time display. Default value is `5` seconds.

    always_show_laptime_gap
Set `true` to always show sector/laptime gap bar. Set `false` to show only in freeze duration.

    show_speed
Show speed and session fastest speed.

    speed_unit
3 unit types are available: `0` = KPH, `1` = MPH, `2` = m/s.

    speed_highlight_duration
Set duration (seconds) for highlighting new fastest speed. Default value is `5` seconds.

    show_position_lapnumber
Show local driver position standing & current lap number.

    last_saved_sector_data
Store last auto-saved sector data string of current session, not recommended for manual editing.


## Session
    show_clock
Show current system clock time.

    show_lapnumber
Show your current lap number & max laps (if available).

    show_place
Show your current place against all drivers in a session.

    clock_format
Set clock format string. To show seconds, add `%S`, such as `"%H:%M:%S %p"`. See [link](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes) for full list of format codes.

    lapnumber_text
Set custom lap number description text. Set `""` to hide text.

    bkg_color_maxlap_warn
Set warning color that shows 1 lap before exceeding max-lap in qualify (or indicates the last lap of a lap-type race).


## Steering
    bar_length_scale, bar_height_scale
Scale steering bar length & height, accepts decimal place.

    bar_edge_width
Set left and right edge boundary width.

    show_scale_mark
This enables scale marks on steering bar.

    scale_mark_degree
Set gap between each scale mark in degree. Default is `90` degree. Minimum value is limited to `10` degree.


## Stint
    tyre_compound_list
Set custom tire compound index letter. One letter for one compound index. Note: since most vehicle mods don't share a common tire compound types or list order, it is impossible to have a tyre compound letter list that matches every car.


## Temperature
    layout
4 layouts are available: `0` = vertical layout, `1` = vertical swapped, `2` = horizontal layout, `3` = horizontal swapped.

    color_swap_tyre, color_swap_brake
Swap heat map color between font & background color.

    temp_unit
2 unit types are available: `0` = Celsius, `1` = Fahrenheit


## Timing
    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    show_session_best
Show current session best laptime from all players.

    session_best_from_same_class_only
Show current session best laptime from same vehicle class only.

    show_best
Show personal best laptime.

    show_last
Show personal last laptime.

    show_estimated
Show personal current estimated laptime.

    prefix_*
Set prefix text that displayed beside laptime. Set to `""` to hide prefix text.


## Tyre wear
    layout
2 layouts are available: `0` = vertical layout, `1` = horizontal layout.

    font_color_remaining
Set font color for total remaining tyre.

    font_color_wear_difference
Set font color for tyre wear difference of previous lap.

    font_color_lifespan
Set font color for estimated tyre lifespan in laps.

    font_color_warning
Set warning font color when reaching user defined threshold.

    show_wear_difference
Show total tyre wear difference of previous lap.

    realtime_wear_difference
Show tyre wear difference of current lap that constantly updated in realtime.

    freeze_duration
Set freeze duration(seconds) for previous lap tyre wear info if `realtime_wear_difference` is enabled.

    show_lifespan
Show estimated tyre lifespan in laps.

    warning_threshold_remaining
Set warning threshold for total remaining tyre in percentage. Default is `30` percent.

    warning_threshold_wear
Set warning threshold for total amount tyre wear of last lap in percentage. Default is `3` percent.

    warning_threshold_laps
Set warning threshold for estimated tyre lifespan in laps. Default is `5` laps.


## Weather
    temp_unit
2 unit types are available: `0` = Celsius, `1` = Fahrenheit


## Wheel
    bkg_color_bottoming
Set color indicator when car bottoming.

    rideheight_offset_front, rideheight_offset_rear
Set front & rear ride height offset, for bottoming color indicator. Value in millimeters, but without decimal place.

    wheelbase
Set wheelbase in millimeters, for used in rake angle calculation.

    show_caption
Show short caption description besides each info block.
