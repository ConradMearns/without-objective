#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmter",
#     "logfmt",
#     "pandas",
#     "rich",
# ]
# ///

import os
from pathlib import Path
from slap import setup_logging, log_kw

setup_logging()

root_directory = Path("~/Pictures/").expanduser().as_posix()

for root, _, files in os.walk(root_directory):
    for file in files:
        file_path = os.path.join(root, file)
        log_kw("File Discovered", entry=file_path, root=root_directory)