import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from logfmter import Logfmter
from rich.logging import RichHandler
from logfmt import parse
from collections import defaultdict


def setup_logging(level=logging.DEBUG):
    """Setup structured logging with Logfmter for machine-readable output"""
    log_formatter = Logfmter()

    handlers = []

    # Detect if stdout is being piped
    is_piped = not sys.stdout.isatty()

    if is_piped:
        # When piped, use plain stream handler for clean logfmt output
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(level)
        stdout_handler.setFormatter(log_formatter)
        handlers.append(stdout_handler)
    else:
        # When not piped, use Rich handler for pretty output
        rich_handler = RichHandler(
            level=level,
            show_time=True,
            markup=False,
            rich_tracebacks=True,
            tracebacks_show_locals=False,
        )
        rich_handler.setFormatter(log_formatter)
        handlers.append(rich_handler)

    # File handler for logs directory
    # Get the directory of the executed script
    script_path = Path(sys.argv[0]).resolve()
    script_dir = script_path.parent
    script_name = script_path.stem

    # Create logs directory in the same directory as the executed script
    logs_dir = script_dir / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Generate log filename with PID, datetime, and script name
    pid = os.getpid()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{pid}_{timestamp}_{script_name}.log"
    log_filepath = logs_dir / log_filename

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(level)
    file_handler.setFormatter(log_formatter)
    handlers.append(file_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers
    )

def log_event(event):
    """Log a dataclass or object as structured data"""
    logging.info({
        "event_type": event.__class__.__qualname__,
        **event.__dict__
    })

def log_kw(msg, err=False, **kwargs):
    if err:
        logging.warning({
            "msg": msg,
            **kwargs
        })
    else:
        logging.info({
            "msg": msg,
            **kwargs
        })

def read_logs_from_stdin():
    """Read logfmt from stdin and organize deduplicated events by msg.

    Returns:
        dict: A dictionary where keys are msg values and values are lists of
              dicts containing the other key-value pairs from each log entry.
    """
    # Dictionary to hold msg -> set of event data (using set for deduplication)
    events_by_msg = defaultdict(set)

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        # Parse the logfmt line (parse expects a list of lines)
        for parsed in parse([line]):
            parsed = dict(parsed)

            # Extract msg and create frozenset of other properties
            if 'msg' in parsed:
                msg = parsed['msg']
                # Remove 'at' and 'msg' from the data, keep rest
                event_data = {k: v for k, v in parsed.items() if k not in ('at', 'msg')}
                # Convert to frozenset for hashing/deduplication
                event_frozenset = frozenset(event_data.items())
                events_by_msg[msg].add(event_frozenset)

    # Convert sets of frozensets to lists of dicts
    return {
        msg: [dict(event_frozenset) for event_frozenset in events]
        for msg, events in events_by_msg.items()
    }

def read_logs(logs_dir="logs"):
    """Read logfmt logs from stdin if piped, otherwise from log files.

    Automatically detects if data is being piped via stdin and switches modes.

    Returns:
        dict: A dictionary where keys are msg values and values are lists of
              dicts containing the other key-value pairs from each log entry.
    """
    # Check if stdin is being piped
    if not sys.stdin.isatty():
        return read_logs_from_stdin()

    # Otherwise, read from log files
    logs_path = Path(logs_dir)
    if not logs_path.exists():
        return {}

    # Get all .log files sorted by name (which includes timestamp)
    log_files = sorted(logs_path.glob("*.log"))

    # Dictionary to hold msg -> set of event data (using set for deduplication)
    events_by_msg = defaultdict(set)

    for log_file in log_files:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse the logfmt line (parse expects a list of lines)
                for parsed in parse([line]):
                    parsed = dict(parsed)

                    # Extract msg and create frozenset of other properties
                    if 'msg' in parsed:
                        msg = parsed['msg']
                        # Remove 'at' and 'msg' from the data, keep rest
                        event_data = {k: v for k, v in parsed.items() if k not in ('at', 'msg')}
                        # Convert to frozenset for hashing/deduplication
                        event_frozenset = frozenset(event_data.items())
                        events_by_msg[msg].add(event_frozenset)

    # Convert sets of frozensets to lists of dicts
    return {
        msg: [dict(event_frozenset) for event_frozenset in events]
        for msg, events in events_by_msg.items()
    }