# Available Widgets & Features

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
- 2 different layouts.

## DRS
- Show DRS color indicator.

## Engine
- Show Oil & Water temperature with overheating indicator.
- Show Turbo pressure (bar).
- Show Engine RPM.

## Force
- Show longitudinal & lateral G force with direction indicator.
- Show downforce ratio (percentage).

## Fuel
- Show current remaining fuel, with liters or gallons as display unit.
- Show estimated total required fuel for finishing race, negative value indicates estimated extra fuel after race ends.
- Show fuel consumption from last lap.
- Show estimated laps & minutes that current remaining fuel can last.
- Show estimated number of required pit stop. Note, any decimal place should be considered for an additional full pit stops (or try save some fuel), as it is not possible to do 0.5 or 0.01 pit stops.
- Show caption descriptions (optional).

## Gear
- Show Gear in 2 layouts.
- Show Speed, with kph, mph, or m/s as display unit.
- Show Speed Limiter sign while activated.
- Show RPM color indicator with customizable RPM range setting.
- Show RPM over-rev color warning.
- Show RPM bar animation (optional) ranged from safe RPM to max RPM.
- Show Startlights indicator.
- Show Low Fuel indicator.
- Show Blue Flag indicator.
- Show Yellow Flag indicator.

## Instrument
- Show Headlights state.
  When Headlights on, icon turns white.
- Show Ignition & Starter state.
  When Ignition on, icon turns white.
  When Ignition on while Engine off, icon background turns green (default color).
- Show Auto-Clutch state.
  When Auto-Clutch on, icon turns white.
  When Clutch pressed, icon background turns cyan (default color).
- Show Wheel Lock state.
  When Brake pressed and Slip Ratio reaches threshold, icon background flashes red (default color).
- Show Wheel Slip state.
  When Slip Ratio reaches threshold, icon background flashes yellow (default color).
- Include many customizable options.

## Pedal
- Show Pedal input, both Filtered & Unfiltered input side by side, which helps distinguish car specific assists such as TC/ABS/Auto-clutch, etc.
- Show Force Feedback meter (optional), and clipping indicator.

## Pressure
- Show Tyre pressure, with kPa, psi, or bar as display unit.
- Show Tyre load (optional) in Newtons or percentage ratio.
- 4 different layouts.

## Radar
- Show car radar that displays relative position of player's vehicle against up 6 nearby vehicles.
- Vehicle changes color if is laps ahead or behind player.
- Fully customizable size & scale.
- Default refresh rate at 50 fps.
- Show center mark.

## Relative
- Show driver standings, relative position and time gap.
- Show different text color based on laps ahead or behind you.
- Show driver's last laptime (optional).
- Show vehicle class categories (optional) with fully customizable class name and color.
- Show driver's position standing in class.
- Show tyre compound index, with customizable letter.
- Show pit status indicator whether driver is currently in pit, with customizable pit status text.
- Customizable column info display order.

## Session
- Show current system clock time, with customizable time format.
- Show session timer, accuracy is limited by 200ms refresh rate of rF2 API.
- Show driver's current lap number & max laps (if available), with customizable lap number description text.
- Displays warning color if driver is about to exceed max-lap in qualify (or indicates the last lap of a lap-type race). Note: if warning color appears in qualify, it means you have already reached max allowed laps. Do not attempt to across finish line, but ESC immediately to avoid DQ.
- Show driver's current place against all drivers in a session.

## Steering
- Show Steering input.
- Show Scale Marks (optional), each with 90 degrees gap.

## Stint
- Show realtime stint data, as well as last stint data.
- Show front & rear tire compound index, with customizable letter.
- Show total driven laps.
- Show total driven time (min:sec).
- Show total used fuel (in liters or gallons).
- Show total average tire wear.

## Temperature
- Show average Tyre surface temperature.
- Show Brake temperature of front and rear.
- Available temperature unit: Celsius, Fahrenheit.
- Changes font color or background color based on heat map.
- 4 different layouts.

## Timing
- Show personal best, last, current, and delta estimated laptime.
- 3 different layouts.

## Wear
- Show total remaining tyre in percentage that changes color according to wear.
- Show total tyre wear from last lap.
- Show realtime tyre wear of current lap.
- Show estimated tyre lifespan in laps.
- 2 different layouts with customizable placement order.

## Weather
- Show surface condition (dry or wet).
- Show Track & Ambient temperature.
- Available temperature unit: Celsius, Fahrenheit.
- Show rain percentage, min, max, average wetness.

## Wheel
- Show Camber & Toe in (degree).
- Show Ride Height (millimeter).
- Show car bottoming indicator with customizable offset.
- Show Rake (millimeter) & Rake angle (degree) with negative rake indicator. Wheelbase can be defined in config.
- Show caption descriptions (optional).