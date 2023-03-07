# Available Widgets & Features

## Brake
- Show brake temperature.
- Show average brake temperature.
- Available temperature unit: Celsius, Fahrenheit.
- Changes font color or background color based on heat map.

## Cruise
- Show current in-game clock time of the circuit.
- Show compass directions with three-figure bearings that matches game's cardinal directions.
- Show elevation difference in game's coordinate system, with meter or feet as display unit.
- Show odometer that displays total driven distance of local player, with km or mile as display unit.

## Delta best
- Show delta best based on personal best laptime.
- Show delta bar with customizable range, size and color.
- Record, save, and load player's best laptime data automatically.
- Best laptime file is saved in deltabest folder, and can be used by other players.

## DRS
- Show DRS color indicator.

## Engine
- Show oil & water temperature with overheating indicator.
- Show turbo pressure (bar, psi, kPa).
- Show engine RPM.

## Flag
- Show pit timer, and total amount time spent in pit after exit pit.
- Show low fuel indicator when fuel level is below certain amount value.
- Show speed limiter indicator.
- Show yellow flag indicator of current & next sectors.
- Show blue flag indicator with timer.
- Show race start lights indicator with light frame number for standing-type start.
- Show race start countdown timer for standing-type start. 

## Force
- Show longitudinal & lateral G force with direction indicator.
- Show downforce ratio (percentage).

## Fuel
- Show current remaining fuel, with liters or gallons as display unit.
- Show estimated total required fuel for finishing race, negative value indicates estimated extra fuel after race ends.
- Show estimated fuel consumption of current lap, which calculated from delta fuel consumption of last recorded lap.
- Show estimated laps & minutes that current remaining fuel can last.
- Show estimated number of required pit stop. Note, any decimal place should be considered for an additional full pit stops (or try save some fuel), as it is not possible to do 0.5 or 0.01 pit stops.
- Show caption descriptions (optional).

## Gear
- Show speed, with kph, mph, or m/s as display unit.
- Show speed limiter (optional) indicator while activated.
- Show RPM color indicator with customizable RPM range setting.
- Show neutral-gear color warning when vehicle speed is higher than threshold.
- Show RPM over-rev color warning.
- Show RPM bar animation (optional) ranged from safe RPM to max RPM.

## Instrument
- Show headlights state.
  When headlights on, icon turns white.
- Show ignition & starter state.
  When ignition on, icon turns white.
  When ignition on while engine off, icon background turns green (default color).
- Show auto-clutch state.
  When auto-clutch on, icon turns white.
  When clutch pressed, icon background turns cyan (default color).
- Show wheel lock state.
  When brake pressed and slip ratio reaches threshold, icon background flashes red (default color).
- Show wheel slip state.
  When slip ratio reaches threshold, icon background flashes yellow (default color).
- Include many customizable options.

## Pedal
- Show pedal input, both filtered & unfiltered input side by side, which helps distinguish car specific assists such as TC/ABS/Auto-clutch, etc.
- Show force feedback meter (optional), and clipping indicator.

## Pressure
- Show tyre pressure, with kPa, psi, or bar as display unit.
- Show tyre load (optional) in Newtons or percentage ratio.
- Show percentage brake pressure of each wheel.
- Show caption descriptions (optional).

## Radar
- Show car radar that displays relative position of player's vehicle against up 126 nearby vehicles.
- Vehicle changes color if is laps ahead or behind player.
- Fully customizable size & scale.
- Default refresh rate at 50 fps.
- Show center mark.

## Relative
- Show driver standings, relative position and time gap against up 126 nearby players.
- Show driver name, vehicle name.
- Show different text color based on laps ahead or behind you.
- Show driver's last laptime and pit timer.
- Show vehicle class categories with fully customizable class name and color.
- Show driver's position standing in class.
- Show tyre compound index, with customizable letter.
- Show pitstops count, pit request.
- Show pit status indicator whether driver is currently in pit, with customizable pit status text.
- Customizable column info display order.

## Sectors
- Show accumulated target sector time, with two available options:
    * Show theoretical best sector time from best sectors of current session.
    * Show sector time from personal best laptime of current session.
- Show accumulated current sector time.
- Show sector/laptime gap comparing to sector time from personal best laptime of current session.
- Show theoretical best sector time of each sector on 3 separated sector bars.
- Show sector time gap against session best sector time on sector bars.
- Show optional current lap vehicle fastest speed & session fastest speed.
- Show optional local driver position standing & current lap number.

## Session
- Show current system clock time, with customizable time format.
- Show session timer, accuracy is limited by 200ms refresh rate of rF2 API.
- Show driver's current lap number & max laps (if available), with customizable lap number description text.
- Displays warning color if driver is about to exceed max-lap in qualify (or indicates the last lap of a lap-type race). Note: if warning color appears in qualify, it means you have already reached max allowed laps. Do not attempt to across finish line, but ESC immediately to avoid DQ.
- Show driver's current place against all drivers in a session.

## Steering
- Show steering input.
- Show scale marks (optional), with customizable gap.

## Stint
- Show realtime stint data, as well as stint history.
- Show front & rear tire compound index, with customizable letter.
- Show total driven laps.
- Show total driven time (min:sec).
- Show total used fuel (in liters or gallons).
- Show total average tire wear (percentage).

## Suspension
- Show ride height (millimeter).
- Show car bottoming indicator with customizable offset.
- Show rake angle (degree) & rake (millimeter) with negative rake indicator and customizable wheelbase.
- Show caption descriptions (optional).

## Temperature
- Show "inner/center/outer" or average tyre surface temperature.
- Show tyre inner layer temperature.
- Show front & rear tire compound index, with customizable letter.
- Available temperature unit: Celsius, Fahrenheit.
- Changes font color or background color based on heat map.

## Timing
- Show session best, personal best, last, current, and delta estimated laptime.

## Wear
- Show total remaining tyre in percentage that changes color according to wear.
- Show total tyre wear difference of previous lap.
- Show realtime tyre wear difference of current lap.
- Show estimated tyre lifespan in laps.
- Show caption descriptions (optional).

## Weather
- Show track and ambient temperature.
- Available temperature unit: Celsius, Fahrenheit.
- Show rain percentage.
- Show surface condition, minimum, maximum, and average wetness.

## Wheel
- Show camber & toe in (degree).
- Show caption descriptions (optional).
