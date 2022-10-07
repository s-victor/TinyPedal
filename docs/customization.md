# Customization Guide

TinyPedal offers a wide range of customization, which is currently available by editing `config.json` file with text editor. This config file will be auto-generated after first launching.

This APP will auto-save setting when user makes any changes to widget position, or has toggled widget visibility, auto hide, lock overlay from tray icon. Due to this reason, to avoid losing changes, it is recommended to quit APP before editing or saving JSON file. Any changes will only take effect after restarting APP.

To make changes, editing `values` on the right side of colon.

Do not modify anything (keys) on the left side of colon, any changes to those keys will be reverted back to default setting by APP.

If APP fails to launch after editing config.json, check JSON file for typo error or invalid values; or delete `config.json` to let APP generate a new default file.


## Backup file 
TinyPedal will automatically create a backup file with time stamp suffix if old setting file is invalid, and a new default `config.json` will be generated.

A newer released version will auto-update old setting and add new setting. It is still recommended to manually create backup file before updating to new version.


## Editing Notes
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
Those are for background color. A value of `"#000002"` makes color fully transparent.


## Overlay

    fixed_position

Check whether widget is locked at startup. This setting can be toggled from tray icon menu.

Valid value: `true`, same as `1`. `false`, same as `0`.

    auto_hide
Check whether auto hide is enabled. This setting can be toggled from tray icon menu.

Valid value: `true`, same as `1`. `false`, same as `0`.

    delta_module
Enable delta timing module. This module provides timing data for `Delta best` and `Timing` widgets, which returns value 0 if turned off.

    fuel_module
Enable fuel calculation module. This module provides vehicle fuel usage data for `Fuel` and other widgets, which returns nothing if turned off.

    relative_module
Enable relative calculation module. This module provides vehicle relative data for `Relative` and `Radar` widgets, which returns nothing if turned off.

    hover_color_1, hover_color_2
Define color of hover cover when mouse cursor is above widget (when not locked).


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
    bkg_color_overheat
Set oil & water overheat color indicator.

    overheat_threshold_oil, overheat_threshold_water
Set temperature threshold for oil & water overheat color indicator, value in Celsius.

    show_rpm
Show engine RPM.

    show_turbo
Show turbo pressure in bar.


## Force
    show_downforce_ratio
Show front vs rear downforce ratio. 50% means equal downforce; higher than 50% means front has more downforce.


## Fuel
    show_caption
Show short caption description besides each info block.

    bkg_color_low_fuel
Set low fuel color indicator, which changes widget background color when there is just 2 laps of fuel left.

    fuel_unit
2 unit types are available: `0` = liters, `1` = gallons.

    fuel_consumption
This value holds the last recorded fuel consumption of the last lap, unit is liters. Accept manual editing, but will be overridden by any new lap done.


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
A visible thin edge line, in pixel, set to `0` to hide this line.

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
Set fuel volume threshold to only show low fuel indicator when total amount of remaining fuel is equal or less than this value. This value takes consideration from 'fuel_unit' setting of Fuel Widget. For example, if `fuel_unit` is set to gallon, then this value should also be set using gallon unit. The purpose of this setting is to limit low fuel warning when racing on lengthy tracks, where fuel tank may only hold for a lap or two. Default value is `20`.

    low_fuel_lap_threshold
Set amount lap threshold to only show low fuel indicator when total completable laps of remaining fuel is equal or less than this value. Default value is `2` laps before running out of fuel.

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

    column_index_*
Set display order of each icon. Must keep index number unique to each icon, otherwise icons will overlap.

    warning_color_*
Set warning color for each icon, which shows when conditions are met.

    wheel_lock_threshold
Set percentage threshold for triggering wheel lock warning under braking. `0.2` means 20% of tyre slip ratio.

    wheel_slip_threshold
Set percentage threshold for triggering wheel slip warning. `0.1` means 10% of tyre slip ratio.

    wheel_radius_front, wheel_radius_rear
Set radius for front and rear wheels, which is used to calculate tyre slip ratio. Manual editing is not required, as this value will be automatically calculated based on a special algorithm after player has completed a full lap, and will be auto-saved to `config.json` file.

    minimum_speed
Set minimum speed threshold before APP records and calculates wheel radius samples. Default value is `16.5` (m/s),

    minimum_samples
Set minimum number of radius samples that required for calculating average wheel radius. Default value is `400`. Minimum value is limited to `100`.


## Pedal
    bar_length_scale, bar_width_scale
Scale pedal bar length & width, accepts decimal place.

    full_pedal_height
This is the indicator height when pedal reaches 100% travel, value in pixel.

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
Show tyre load percentage ratio between left & right tyres of same axle. Set `false` to show individual tyre load in Newtons.


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

    column_index_*
Set order of each info column. Must keep index number unique to each column, otherwise columns will overlap.

    additional_players_front, additional_players_behind
Set additional players shown on relative list. The value is limited to a maximum of 3 additional players for each front & behind setting. Default value is `0`.


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
Set custom lap number description text. Set it to `""` to hide text.

    bkg_color_maxlap_warn
Set warning color that shows 1 lap before exceeding max-lap in qualify (or indicates the last lap of a lap-type race).


## Steering
    bar_length_scale, bar_height_scale
Scale steering bar length & height, accepts decimal place.

    bar_edge_width
Set left and right edge boundary width.

    show_scale_mark
This enables scale marks on steering bar, which is set 90 degrees apart from each other.


## Stint
    fuel_unit
2 unit types are available: `0` = liters, `1` = gallons.

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
3 layouts are available: `0` = vertical layout, `1` = double lines horizontal layout, `2` = single line horizontal layout.

    last_laptime
This value holds the last recorded laptime, which will be read by delta module, and used for fuel calculation. Accept manual editing, but will be updated & overridden by any new lap done.


## Wear
    layout
4 layouts are available: `0` = vertical layout, `1` = vertical swapped, `2` = horizontal layout, `3` = horizontal swapped.


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
