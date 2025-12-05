#!/usr/bin/env -S uv run --script

# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "logfmter",
#     "pandas",
#     "rich",
# ]
# ///


from rich.logging import RichHandler
from dataclasses import dataclass
import logging
from logfmter import Logfmter

log_formatter = Logfmter()

rich_handler = RichHandler(
    level=logging.DEBUG,
    show_time=True,
)
rich_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[rich_handler]
)

handler = logging.StreamHandler()
handler.setFormatter(Logfmter())

logging.basicConfig(handlers=[handler])

logging.error("hello", extra={"alpha": 1}) # at=ERROR msg=hello alpha=1
logging.error({"token": "Hello, World!"}) # at=ERROR token="Hello, World!"


logging.debug("This is a debug message.")  # Will not be shown (level < INFO)
logging.info("This is an info message.")
logging.warning("This is a warning message.")
logging.error("This is an error message.")
logging.critical("This is a critical message.")


@dataclass
class AnEvent:
    data: str

logging.info(AnEvent("logging a dataclass directly"))

def log_event(event):
    logging.info({
        "event_type": event.__class__.__qualname__,
        **event.__dict__
    })


def log_kw(msg, **kwargs):
    logging.info({
        "msg": msg,
        **kwargs
    })

log_event(AnEvent("logging with a bit more finesse"))

log_kw("New Event", data=7, other_data=9.5)
