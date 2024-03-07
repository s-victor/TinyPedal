"""
py2exe build script

Args:
    -c, --clean: force remove old build folder before building.
"""

import re
import os
import shutil
import sys
from glob import glob
from py2exe import freeze

from tinypedal.const import APP_NAME, VERSION, PLATFORM, COPYRIGHT


PYTHON_PATH = sys.exec_prefix
DIST_FOLDER = "dist/"

EXECUTABLE_SETTING = [
    {
    "script": "run.py",
    "icon_resources": [(1, "images/icon.ico")],
    "dest_base": "tinypedal",
    }
]

EXCLUDE_MODULES = [
    "_ssl",
    "difflib",
    "email",
    "http",
    "pdb",
    "venv",
    "tkinter",
]

IMAGE_FILES = [
    "images/CC-BY-SA-4.0.txt",
    "images/icon_compass.png",
    "images/icon_instrument.png",
    "images/icon.png",
]

DOCUMENT_FILES = [
    "docs/changelog.txt",
    "docs/customization.md",
    "docs/contributors.md",
]

LICENSES_FILES = glob("docs/licenses/*")

QT_FILES = [
    f"{PYTHON_PATH}/Lib/site-packages/PySide2/plugins/platforms/qwindows.dll"
]

BUILD_DATA_FILES = [
    ("", ["LICENSE.txt", "README.md"]),
    ("docs", DOCUMENT_FILES),
    ("docs/licenses", LICENSES_FILES),
    ("deltabest", ["deltabest/README.txt"]),
    ("settings", []),
    ("images", IMAGE_FILES),
    ("platforms", QT_FILES),
]

BUILD_OPTIONS = {
    "dist_dir": f"{DIST_FOLDER}/{APP_NAME}",
    "excludes": EXCLUDE_MODULES,
    "dll_excludes": ["libcrypto-1_1.dll"],
    "optimize": 2,
    #"bundle_files": 2,
    "compressed": 1,
}

BUILD_VERSION = {
    "version": VERSION,
    "description": APP_NAME,
    "copyright": COPYRIGHT,
    "product_name": APP_NAME,
    "product_version": VERSION,
}


def check_dist(build_ready=False) -> bool:
    """Check whether dist folder exist"""
    if not os.path.exists(DIST_FOLDER):
        print("INFO:dist folder not found, creating")
        try:
            os.mkdir(DIST_FOLDER)
            build_ready = True
            print("INFO:dist folder created")
        except (PermissionError, FileExistsError):
            build_ready = False
            print("ERROR:Cannot create dist folder")

    if os.path.exists(DIST_FOLDER):
        build_ready = True
    return build_ready


def check_old_build(build_ready=False) -> bool:
    """Check whether old build folder exist"""
    if os.path.exists(f"{DIST_FOLDER}{APP_NAME}"):
        print("INFO:Found old build folder")

        for _arg in sys.argv:
            if re.match("^-c$|^--clean$", _arg):
                build_ready = delete_old_build()
                return build_ready

        is_remove = input("INFO:Remove old build folder before building? Yes/No/Quit \n")

        if re.match("y", is_remove, flags=re.IGNORECASE):
            build_ready = delete_old_build()
        elif re.match("q", is_remove, flags=re.IGNORECASE):
            build_ready = False
        else:
            build_ready = True
            print("WARNING:Building without removing old files")
    return build_ready


def delete_old_build() -> bool:
    """Delete old build folder"""
    try:
        shutil.rmtree(f"{DIST_FOLDER}{APP_NAME}/")
        print("INFO:Old build files removed")
        return True
    except (PermissionError, OSError):
        print("ERROR:Cannot delete build folder")
        return False


def build_exe() -> None:
    """Building executable file"""
    freeze(
        version_info = BUILD_VERSION,
        windows = EXECUTABLE_SETTING,
        options = BUILD_OPTIONS,
        data_files = BUILD_DATA_FILES,
        zipfile = "lib/library.zip",
    )


def build_start() -> None:
    """Start building"""
    print(f"INFO:version:{VERSION}")
    print(f"INFO:platform:{PLATFORM}")
    if PLATFORM == "Windows":
        if check_old_build(check_dist()):
            build_exe()
            print("INFO:Building finished")
        else:
            print("INFO:Building canceled")
    else:
        print("ERROR:Build script does not support none Windows platform")
        print("INFO:Building canceled")


build_start()
