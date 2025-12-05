#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmt",
# ]
# ///

import sys
import re
from logfmt import parse

# Pattern to detect start of a new log entry with timestamp
# Matches: [12/03/25 16:44:26] INFO     at=INFO...
timestamp_pattern = re.compile(r'^\[(\d{2}/\d{2}/\d{2} \d{2}:\d{2}:\d{2})\]')

# Pattern to detect start of a new log entry without timestamp
# Matches: "                    INFO     at=INFO..." (whitespace, log level, whitespace, then content starting with key=)
new_entry_pattern = re.compile(r'^\s+(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+\w+=')

def parse_multiline_logs(lines):
    """Parse multi-line Rich-formatted logfmt entries"""
    current_entry = None
    current_timestamp = None

    for line in lines:
        # Check if this is the start of a new log entry with timestamp
        match = timestamp_pattern.match(line)
        is_new_entry = match or new_entry_pattern.match(line)

        if is_new_entry:
            # If we have a previous entry, yield it
            if current_entry is not None:
                yield current_timestamp, current_entry

            # Handle entry with timestamp
            if match:
                current_timestamp = match.group(1)
                rest = line[match.end():].strip()
            else:
                # Entry without timestamp - keep the previous timestamp
                rest = line.strip()

            # Remove the log level (INFO, DEBUG, etc.) and any extra spacing
            rest = re.sub(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+', '', rest)
            # Remove file location at the end (e.g., slap.py:30)
            rest = re.sub(r'\s+\S+\.py:\d+\s*$', '', rest)
            current_entry = rest
        else:
            # Continuation line
            if current_entry is not None:
                stripped = line.strip()
                # Remove log level prefix if present on continuation line
                stripped = re.sub(r'^(DEBUG|INFO|WARNING|ERROR|CRITICAL)\s+', '', stripped)
                # Remove file location if present
                stripped = re.sub(r'\s+\S+\.py:\d+\s*$', '', stripped)
                # Only add non-empty content
                if stripped:
                    # If the line doesn't start with key=value pattern, it's a wrapped value
                    # Don't add a space before it - just concatenate directly
                    if re.match(r'\w+=', stripped):
                        current_entry += ' ' + stripped
                    else:
                        # This is a continuation of the previous value
                        current_entry += stripped

    # Don't forget the last entry
    if current_entry is not None:
        yield current_timestamp, current_entry

# Read and parse the logs
for timestamp, logfmt_line in parse_multiline_logs(sys.stdin):
    # Parse the single-line logfmt
    for entry in parse([logfmt_line]):
        # Add timestamp to the entry
        entry['timestamp'] = timestamp
        print(entry)
