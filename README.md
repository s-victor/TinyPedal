# TinyPedal

TinyPedal is an open-source overlay application for racing simulation.

It focuses on light weight, compact, minimalistic visual presentation, while provides important real-time info with detailed customizations.

Currently supports rFactor 2 and displays simulation info using The Iron Wolf’s [rF2 Shared Memory Map Plugin](https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin) & Tony Whitley’s [pyRfactor2SharedMemory](https://github.com/TonyWhitley/pyRfactor2SharedMemory) Library.

`Borderless` or `Windowed Mode` is required. Full-screen mode is not supported.


## Available widgets & Features
- Pedal
    - Show Pedal input, both Filtered & Unfiltered input side by side, which helps distinguish car specific assists such as TC/ABS/Auto-clutch, etc.
    - Show optional Force Feedback meter, and clipping indicator.

- Steering
    - Show Steering input.
    - Show optional Scale Marks (90 degrees apart).

- Gear
    - Show Gear in 2 layouts.
    - Show Speed with 3 different unit display: kph, mph, or m/s.
    - Show Speed Limiter sign while activated.
    - Show RPM color indicator with customizable RPM range setting.
    - Show RPM over-rev color warning.
    - Show optional RPM bar animation ranged from safe RPM to max RPM.

- Fuel
    - Show current remaining fuel (liter).
    - Show estimated total required fuel for finishing race, negative value indicates estimated extra fuel after race ends.
    - Show fuel consumption from last lap.
    - Show estimated laps & minutes that current remaining fuel can last.
    - Show estimated number of required pit stop. Note, any decimal place should be considered for an additional full pit stops (or try save some fuel), as it is not possible to do 0.5 or 0.01 pit stops.
    - Show optional caption descriptions.

- Wheel (alignment)
    - Show Camber & Toe in (degree).
    - Show Ride Height (millimeter).
    - Show car bottoming indicator with customizable offset.
    - Show Rake (millimeter) & Rake angle (degree) with negative rake indicator. Wheelbase can be defined in config.
    - Show optional caption descriptions.

- Temperature (tyre & brake)
    - Show average Tyre surface temperature.
    - Show average Brake temperature of front and rear.
    - Changes color based on heat map.
    - 4 different layouts.

- Tyre Wear & Pressure
    - Show Tyre wear that changes color according to wear.
    - Show Tyre pressure with 2 different unit display: kPa or psi.
    - 4 different layouts.

- Relative
    - Show driver standings, relative position and time gap.
    - Show different text color based on laps ahead or behind you.
    - Show optional driver's last laptime.
    - Show optional vehicle class categories with fully customizable class name and color.

- Timing
    - Show personal best, last, and current lap time.

- Weather
    - Show surface condition (dry or wet).
    - Show Track & Ambient temperature.
    - Show rain percentage, min, max, average wetness.

- Engine
    - Show Oil & Water temperature with overheating indicator.
    - Show Turbo pressure (bar).
    - Show Engine RPM.

- Force
    - Show longitudinal & lateral G force with direction indicator.
    - Show downforce ratio (percentage).

- DRS
    - Show DRS color indicator.

All widgets are Customizable, see **Customization** section for details.

Note: some info, such as fuel usage or tyre wear, requires at least 1 or 2 completed laps to be shown correctly.


## Requirements
TinyPedal requires The Iron Wolf’s rF2 Shared Memory Map Plugin, download it from here:  
https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/

The plugin file `rFactor2SharedMemoryMapPlugin64.dll` should be placed in `rFactor 2\Bin64\Plugins` folder. This plugin also comes with some of the popular rF2 Apps, check `rFactor 2\Bin64\Plugins` folder first to see if it was installed already.

Note: if `Auto Hide` function does not correctly hide overlay while in garage screen (before clicked DRIVE), it's likely caused by an outdated version of `rFactor2SharedMemoryMapPlugin64.dll` that installed by other apps, please download newer version from above link. The oldest Plugin version that known to work with TinyPedal is `09/07/2020 - v3.7.14.2`.


## Usage
1. Make sure The Iron Wolf’s `rF2 Shared Memory Map Plugin` is installed, as described above, and `Borderless` or `Windowed Mode` is activated in game.

2. Download latest TinyPedal version from release page, extract, and run `tinypedal.exe`. Alternatively, you can run TinyPedal from source, see **Run from source** section for details.

3. A tray icon will appear at system tray. If not shown, check hidden tray icon. `Right Click` on tray icon will bring up context menu.

4. Launch `rFactor 2`, overlay will appear once your vehicle is on track, and auto-hide otherwise. You can turn off auto-hide by `Right Click` on tray icon and select `Auto Hide`.

5. Click on overlay to drag around. You can Lock or Unlock overlay from tray menu.

6. Widgets can be Enabled or Disabled by accessing `Widgets` menu from tray menu.

7. To quit APP, `Right Click` on tray icon and select `Quit`.


## Performance

On default setting, current version of TinyPedal uses roughly 5% CPU & 20MB system memory on a 3.0Ghz CPU with all widgets enabled.

In case of unlikely performance issue, turn off less-used widgets is advised (each widget contributes roughly 0.1-0.5% CPU usage alone); or set a higher `update delay` value for specific widget, see **Customization** section for details.

Generally, `update delay` value should not be set under 20ms, as most data from rF2 shared memory plugin capped at 50 refresh rate according to shared memory plugin documents. Lower `update delay` value will cause significantly increase of CPU usage. 


## Customization

TinyPedal offers a wide range of customization, which is currently available by editing `config.json` config file with text editor. This config file will be auto-generated after first launching.

See [docs\customizations.md](./docs/customizations.md) for editing guide.


## Run from source

### Dependencies:
* [Python](https://www.python.org/) 3.8 or higher
* pyRfactor2SharedMemory
    * psutil (sub-dependency)
* pystray
    * Pillow (sub-dependency)
    * six (sub-dependency)

### Steps:
1. Download source code from Release page; or click `Code` button at the top of repository and select `Download ZIP`. You can also use `Git` tool to clone this repository.

2. Download this forked version of pyRfactor2SharedMemory source code from:  
https://github.com/s-victor/pyRfactor2SharedMemory  
It includes a few required changes for TinyPedal.

3. Extract TinyPedal source code ZIP file. Then extract pyRfactor2SharedMemory ZIP file and put `pyRfactor2SharedMemory` folder in the root folder of TinyPedal.

4. Install additional dependencies by using command:  
`pip3 install pystray psutil`  
Note: sub-dependencies should be auto-installed alongside related packages.

5. To start TinyPedal, type command from root folder:  
`python run.py`  
(TinyPedal is currently tested and worked with Python 3.8 & 3.9)

Note: if using `Git` tool to clone this repository, run command with `--recursive` to also clone submodule, such as:  
`git clone --recursive https://github.com/s-victor/TinyPedal.git`


## Build executable
Executable file can be built with [py2exe](http://www.py2exe.org).

To install py2exe, run command:  
`pip3 install py2exe`

To build executable file, run command:  
`python build_py2exe.py py2exe`

After building completed, you can find executable file in `dist\TinyPedal` folder.


## Credits
### Author:
Xiang (S.Victor)

For full list of contributors to TinyPedal, see [contributors.md](./docs/contributors.md) file.

### Special thanks to:  
The Iron Wolf for the permission to use rF2 Shared Memory Map Plugin in TinyPedal.  
Tony Whitley for pyRfactor2SharedMemory library.  


## License

TinyPedal is licensed under the GNU General Public License v3.0 or later. See [LICENSE.txt](./LICENSE.txt) for full text.

TinyPedal icon is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Licenses and notices file for third-party software are located in `docs\licenses` folder, see [THIRDPARTYNOTICES.txt](./docs/licenses/THIRDPARTYNOTICES.txt) file for details.
