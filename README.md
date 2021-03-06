# TinyPedal

TinyPedal is an open-source overlay application for racing simulation.

It focuses on light weight, compact, minimalistic visual presentation, while provides important real-time info with detailed customization.

Currently supports rFactor 2 and displays simulation info using The Iron Wolf’s [rF2 Shared Memory Map Plugin](https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin) & Tony Whitley’s [pyRfactor2SharedMemory](https://github.com/TonyWhitley/pyRfactor2SharedMemory) Library.

`Borderless` or `Windowed Mode` is required. Full-screen mode is not supported.


## Feature
See [docs\features.md](./docs/features.md) for complete widgets & feature list.

All widgets are Customizable, see **Customization** section for details.

Note: some info, such as fuel usage, requires at least 1 or 2 completed laps to be shown correctly.


## Requirements
TinyPedal requires The Iron Wolf’s rF2 Shared Memory Map Plugin, download it from here:  
https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/

The plugin file `rFactor2SharedMemoryMapPlugin64.dll` should be placed in `rFactor 2\Bin64\Plugins` folder. This plugin also comes with some of the popular rF2 Apps, check `rFactor 2\Bin64\Plugins` folder first to see if it was installed already.

Note: if `Auto Hide` function does not correctly hide overlay while in garage screen (before clicked DRIVE), it's likely caused by an outdated version of `rFactor2SharedMemoryMapPlugin64.dll` that installed by other apps, please download newer version from above link. The oldest Plugin version that known to work with TinyPedal is `09/07/2020 - v3.7.14.2`.


## Usage
1. Make sure The Iron Wolf’s `rF2 Shared Memory Map Plugin` is installed, as described above, and `Borderless` or `Windowed Mode` is activated in game.

2. Download latest TinyPedal version from [Releases](https://github.com/s-victor/TinyPedal/releases) page, extract, and run `tinypedal.exe`. Alternatively, you can run TinyPedal from source, see **Run from source** section for details.

3. A tray icon will appear at system tray. If not shown, check hidden tray icon. `Right Click` on tray icon will bring up context menu.

4. Launch `rFactor 2`, overlay will appear once your vehicle is on track, and auto-hide otherwise. You can turn off auto-hide by `Right Click` on tray icon and select `Auto Hide`.

5. Click on overlay to drag around. You can Lock or Unlock overlay from tray menu.

6. Widgets can be Enabled or Disabled by accessing `Widgets` menu from tray menu.

7. To quit APP, `Right Click` on tray icon and select `Quit`.


## Performance

On default setting, current version of TinyPedal uses roughly 5% CPU & 20MB system memory on a 3.0Ghz CPU with all widgets enabled. All widgets will stop updating (0% CPU usage) when player is not on track.

In case of unlikely performance issue, turn off less-used widgets is advised (each widget contributes roughly 0.1-0.5% CPU usage alone); or set a higher `update delay` value for specific widget, see **Customization** section for details.

Generally, `update delay` value should not be set under 20ms, as most data from rF2 shared memory plugin capped at 50 refresh rate according to shared memory plugin documents. Lower `update delay` value will cause significantly increase of CPU usage. 


## Customization

TinyPedal offers a wide range of customization, which is currently available by editing `config.json` config file with text editor. This config file will be auto-generated after first launching.

See [Customization Guide](https://github.com/s-victor/TinyPedal/wiki) for editing guide.


## Run from source

### Dependencies:
* [Python](https://www.python.org/) 3.8 or higher
* pyRfactor2SharedMemory
    * psutil (sub-dependency)
* pystray
    * Pillow (sub-dependency)
    * six (sub-dependency)

### Steps:
1. Download source code from [Releases](https://github.com/s-victor/TinyPedal/releases) page; or click `Code` button at the top of repository and select `Download ZIP`. You can also use `Git` tool to clone this repository.

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
TinyPedal is created by Xiang (S.Victor), with helps from other contributors.

See [docs\contributors.md](./docs/contributors.md) file for full list of contributors.

### Special thanks to:  
The Iron Wolf for the permission to use rF2 Shared Memory Map Plugin in TinyPedal.  
Tony Whitley for pyRfactor2SharedMemory library.  


## License

TinyPedal is licensed under the GNU General Public License v3.0 or later. See [LICENSE.txt](./LICENSE.txt) for full text.

TinyPedal icon, as well as image files located in `images` folder, are licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).

Licenses and notices file for third-party software are located in `docs\licenses` folder, see [THIRDPARTYNOTICES.txt](./docs/licenses/THIRDPARTYNOTICES.txt) file for details.
