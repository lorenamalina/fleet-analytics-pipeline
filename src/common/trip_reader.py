import csv
import os
from datetime import datetime, timezone

from common.telemetry import find_column, build_payload

COLUMN_KEYS = {
    "time": "ENGINE_RUN",
    "speed": "VEHICLE_SPEED",
    "rpm": "ENGINE_RPM",
    "throttle": "THROTTLE ()",
    "load": "ENGINE_LOAD",
    "coolant": "COOLANT",
}


def trip_name(path):
    """live12.csv -> live12"""
    return os.path.basename(path).replace(".csv", "")


def now_iso():
    return datetime.now(timezone.utc).replace(tzinfo=None).isoformat()


def read_trip(path, now=now_iso):
    """Genereaza mesajele de telemetrie (dict) pentru randurile active dintr-un CSV."""
    trip = trip_name(path)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        cols = {name: find_column(reader.fieldnames, key)
                for name, key in COLUMN_KEYS.items()}
        for row in reader:
            payload = build_payload(row, cols, trip, now())
            if payload is not None:
                yield payload
