"""
py2exe build script
"""
from py2exe import freeze
from glob import glob

from tinypedal.about import VERSION


app_setting = [{
    "script": "run.py",
    "icon_resources": [(1, "icon.ico")],
    "dest_base": "tinypedal",
    }
]

excludes = ["_ssl", "difflib", "email", "pdb", "venv", "http"]

data_files = [("", ["icon.ico", "LICENSE.txt", "README.md"]),
              ("docs", ["docs/changelog.txt", "docs/customization.md", "docs/contributors.md", "docs/features.md"]),
              ("docs/licenses", glob("docs/licenses/*")),
              ("deltabest", ["deltabest/README.txt"]),
              ("settings", []),
              ("images", ["images/CC-BY-SA-4.0.txt", "images/icon_instrument.png"]),
              ]

options = {
    "dist_dir": "dist/TinyPedal",
    "excludes": excludes,
    "dll_excludes": ["libcrypto-1_1.dll"],
    "optimize": 2,
    "bundle_files": 2,
    "compressed": 1,
}

app_info = {
    "version": VERSION,
    "description": "TinyPedal",
    "copyright": "Copyright (C) 2022 Xiang",
    "product_name": "TinyPedal",
    "product_version": VERSION,
}

freeze(
    version_info = app_info,
    windows = app_setting,
    options = options,
    data_files = data_files,
    zipfile = "lib/library.zip",
)