"""
py2exe build script
"""
from glob import glob
from py2exe import freeze

from tinypedal.const import APP_NAME, VERSION
from tinypedal.about import COPYRIGHT


app_setting = [{
    "script": "run.py",
    "icon_resources": [(1, "icon.ico")],
    "dest_base": "tinypedal",
    }
]

excludes = ["_ssl", "difflib", "email", "pdb", "venv", "http"]

data_files = [("", ["icon.ico", "LICENSE.txt", "README.md"]),
              ("docs", ["docs/changelog.txt",
                        "docs/customization.md",
                        "docs/contributors.md",
                        "docs/features.md"
                        ]),
              ("docs/licenses", glob("docs/licenses/*")),
              ("deltabest", ["deltabest/README.txt"]),
              ("settings", []),
              ("images", ["images/CC-BY-SA-4.0.txt", "images/icon_instrument.png"]),
              ]

options = {
    "dist_dir": f"dist/{APP_NAME}",
    "excludes": excludes,
    "dll_excludes": ["libcrypto-1_1.dll"],
    "optimize": 2,
    "bundle_files": 2,
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
