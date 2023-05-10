"""
py2exe build script
"""
import os
import sys
from glob import glob
from py2exe import freeze

from tinypedal.const import APP_NAME, VERSION
from tinypedal.about import COPYRIGHT

PYTHON_PATH = sys.exec_prefix
DIST_FOLDER = "dist/"


if not os.path.exists(DIST_FOLDER):
    try:
        os.mkdir(DIST_FOLDER)
    except (PermissionError, FileExistsError):
        pass

app_setting = [
    {
    "script": "run.py",
    "icon_resources": [(1, "images/icon.ico")],
    "dest_base": "tinypedal",
    }
]

excludes = ["_ssl", "difflib", "email", "pdb", "venv", "http", "tkinter"]

image_files = [
    "images/CC-BY-SA-4.0.txt",
    "images/icon_instrument.png",
    "images/icon.png",
]

document_files = [
    "docs/changelog.txt",
    "docs/customization.md",
    "docs/contributors.md",
]

licenses_files = glob("docs/licenses/*")

qt_dll = [f"{PYTHON_PATH}/Lib/site-packages/PySide2/plugins/platforms/qwindows.dll"]

data_files = [
    ("", ["LICENSE.txt", "README.md"]),
    ("docs", document_files),
    ("docs/licenses", licenses_files),
    ("deltabest", ["deltabest/README.txt"]),
    ("settings", []),
    ("images", image_files),
    ("platforms", qt_dll),
]

options = {
    "dist_dir": f"{DIST_FOLDER}/{APP_NAME}",
    "excludes": excludes,
    "dll_excludes": ["libcrypto-1_1.dll"],
    "optimize": 2,
    #"bundle_files": 2,
    "compressed": 1,
}

app_info = {
    "version": VERSION,
    "description": APP_NAME,
    "copyright": COPYRIGHT,
    "product_name": APP_NAME,
    "product_version": VERSION,
}

freeze(
    version_info = app_info,
    windows = app_setting,
    options = options,
    data_files = data_files,
    zipfile = "lib/library.zip",
)
