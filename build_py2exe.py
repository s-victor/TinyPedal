"""
py2exe build script
"""
from distutils.core import setup
from glob import glob
import py2exe

from tinypedal.__init__ import VERSION


app_setting = [{
    "script": "run.py",
    "icon_resources": [(1, "icon.ico")],
    "dest_base": "tinypedal",
    }
]

excludes = ["_ssl", "difflib", "email", "pdb", "venv", "http"]

data_files = [("", ["icon.ico", "LICENSE.txt", "README.md"]),
              ("docs", ["docs/changelog.txt", "docs/customizations.md"]),
              ("docs/licenses", glob("docs/licenses/*")),
              ]

options = {
    "py2exe":{
        "dist_dir": "dist/TinyPedal",
        "excludes": excludes,
        "optimize": 2,
        "bundle_files": 2,
        "compressed": 1,
    }
}

setup(
    name = "tinypedal",
    version = VERSION,
    description= "Open-source overlay application for racing simulation",
    author = "Xiang",
    windows = app_setting,
    options = options,
    data_files = data_files,
    zipfile = "lib/library.zip",
)