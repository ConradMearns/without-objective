"""Structured Logging Utilities"""

import logging
import sys
from logfmter import Logfmter
from rich.logging import RichHandler


def setup_logging(level=logging.DEBUG):
    """Setup structured logging with Logfmter for machine-readable output"""
    log_formatter = Logfmter()

    rich_handler = RichHandler(
        level=level,
        show_time=True,
        markup=False,
        rich_tracebacks=True,
        tracebacks_show_locals=False,
    )
    rich_handler.setFormatter(log_formatter)

    logging.basicConfig(
        level=level,
        handlers=[rich_handler]
    )


def log_event(event):
    """Log a dataclass or object as structured data"""
    logging.info({
        "event_type": event.__class__.__qualname__,
        **event.__dict__
    })
