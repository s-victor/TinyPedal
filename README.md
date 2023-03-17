# TinyPedal

TinyPedal is an open-source overlay application for racing simulation.

Currently supports rFactor 2 and displays simulation info using The Iron Wolf’s [rF2 Shared Memory Map Plugin](https://github.com/TheIronWolfModding/rF2SharedMemoryMapPlugin) & Tony Whitley’s [pyRfactor2SharedMemory](https://github.com/TonyWhitley/pyRfactor2SharedMemory) Library.

`Borderless` or `Windowed` mode is required. `Fullscreen` mode is not supported.


## Feature
See [docs\features.md](./docs/features.md) for complete widgets & feature list.


## Requirements
TinyPedal requires The Iron Wolf’s rF2 Shared Memory Map Plugin, download it from here:  
https://forum.studio-397.com/index.php?threads/rf2-shared-memory-tools-for-developers.54282/

The plugin file `rFactor2SharedMemoryMapPlugin64.dll` should be placed in `rFactor 2\Bin64\Plugins` folder. This plugin also comes with some of the popular rF2 Apps, check `rFactor 2\Bin64\Plugins` folder first to see if it was installed already.


## Usage
1. Make sure The Iron Wolf’s `rF2 Shared Memory Map Plugin` is installed, as described above, and `Borderless` or `Windowed` mode is activated in game.

2. Download latest TinyPedal version from [Releases](https://github.com/s-victor/TinyPedal/releases) page, extract, and run `tinypedal.exe`. Alternatively, run TinyPedal from source, see **Run from source** section for details.

3. A tray icon will appear at system tray. If not shown, check hidden tray icon. `Right Click` on tray icon will bring up context menu.

4. Launch `rFactor 2`, overlay will appear once vehicle is on track, and auto-hide otherwise. Auto-hide can toggled ON or OFF by clicking `Auto Hide` from tray menu.

5. Click on overlay to drag around. Overlay can be Locked or Unlocked by clicking `Lock Overlay` from tray menu.

6. Widgets can be Enabled or Disabled by accessing `Widgets` menu from tray menu.

7. To quit APP, `Right Click` on tray icon and select `Quit`.


## Customization

TinyPedal offers a wide range of customization, see [Customization Guide](https://github.com/s-victor/TinyPedal/wiki) for editing guide.


## Run from source

### Dependencies:
* [Python](https://www.python.org/) 3.8 or higher
* pyRfactor2SharedMemory
    * psutil (sub-dependency)
* pystray
    * Pillow (sub-dependency)
    * six (sub-dependency)

### Steps:
1. Download source code from [Releases](https://github.com/s-victor/TinyPedal/releases) page; or click `Code` button at the top of repository and select `Download ZIP`; or use `Git` tool to clone this repository.

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
`python freeze_py2exe.py`

After building completed, executable file can be found in `dist\TinyPedal` folder.

Note: the build script only supports py2exe `v0.12.0.0` or higher.


## Running on Linux

The procedure is basically the same as the above procedure to run from source with the following differences.

The only required dependencies are `psutil` and `pyxdg`. They can be installed with the command:  
`pip3 install psutil pyxdg`

Alternatively, instead of using pip3, it is possible to use system's package manager to install the dependencies. The packages will be named with some prefix like `python3-psutil` and `python3-pyxdg`.

The Iron Wolf's rF2 Shared Memory Map Plugin has to be replaced with [this fork for Wine](https://github.com/schlegp/rF2SharedMemoryMapPlugin_Wine/blob/master/build).

Configuration and data files will be stored in the defined user-specific directories, usually at `$HOME/.config/TinyPedal/` and `$HOME/.local/share/TinyPedal/` respectively.


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
