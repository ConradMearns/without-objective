#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmter",
#     "pandas",
#     "rich",
# ]
# ///


from dataclasses import dataclass
import logging
import os
from pathlib import Path
from slap import setup_logging, log_event

setup_logging()

@dataclass
class FileDiscovered:
    posix_path: str
    entry: str

count = 0

root_directory = Path("~/Pictures/").expanduser().as_posix()

all_files = []
for root, _, files in os.walk(root_directory):
    for file in files:
        file_path = os.path.join(root, file)
        log_event(FileDiscovered(file_path, root_directory))

