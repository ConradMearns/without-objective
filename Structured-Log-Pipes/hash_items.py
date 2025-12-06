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

import hashlib
from pathlib import Path
from slap import read_logs, setup_logging, log_kw

setup_logging()

log_snapshot = read_logs()

for discovery in log_snapshot.get('File Discovered', []):
    file_path = discovery['entry']
    root = discovery['root']

    # one way to pro-actively guard against duplicating work
    if 'File Hash Collected' in log_snapshot:
        already_hashed = any(hash_entry['entry'] == file_path for hash_entry in log_snapshot['File Hash Collected'])
        if already_hashed:
            continue

    try:
        # Use BLAKE2b for fast, secure hashing
        hasher = hashlib.blake2b()

        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files efficiently
            while chunk := f.read(8192):
                hasher.update(chunk)

        file_hash = hasher.hexdigest()

        log_kw(
            "File Hash Collected",
            entry=file_path,
            root=root,
            hash=file_hash,
            algorithm="blake2b",
        )
    except (OSError, PermissionError) as e:
        log_kw("File Hash Error", err=True, entry=file_path, error=str(e))
