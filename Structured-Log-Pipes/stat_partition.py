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
from slap import read_logs, setup_logging, log_kw
from datetime import datetime

setup_logging()

log_snapshot = read_logs()

print(len(log_snapshot['File Discovered']))

for discovery in log_snapshot['File Discovered']:
    file_path = discovery['entry']
    root = discovery['root']

    # one way to pro-actively guard against duplicating work
    if 'File Stat Collected' in log_snapshot:
        already_collected = any(stat['entry'] == file_path for stat in log_snapshot['File Stat Collected'])
        if already_collected:
            continue

    try:
        stat_info = os.stat(file_path)

        file_size = stat_info.st_size
        modified_time = datetime.fromtimestamp(stat_info.st_mtime).isoformat()
        created_time = datetime.fromtimestamp(stat_info.st_ctime).isoformat()
        file_ext = Path(file_path).suffix.lower()

        log_kw(
            "File Stat Collected",
            entry=file_path,
            root=root,
            size_bytes=file_size,
            extension=file_ext,
            modified=modified_time,
            created=created_time,
        )
    except (OSError, PermissionError) as e:
        log_kw("File Stat Error", entry=file_path, error=str(e))
