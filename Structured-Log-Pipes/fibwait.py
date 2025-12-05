#!/usr/bin/python3

import time
import json
import sys

from dataclasses import dataclass, asdict

@dataclass
class Event: pass # just for typing

@dataclass
class FibEvent(Event):
    a: int
    b: int

def emit(event: Event):
    print(json.dumps(asdict(event)))

def fibwait(a = 1, b = 1):
    time.sleep(a)

    emit(FibEvent(a=b, b=a+b))

def parse_events():
    for line in sys.stdin:
        try:
            data = json.loads(line.strip())
            event = FibEvent(**data)
            fibwait(event.a, event.b)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error parsing event: {e}", file=sys.stderr)

if __name__ == "__main__":
    if not sys.stdin.isatty():
        parse_events()
    else:
        fibwait()