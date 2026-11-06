import json
import re
import os


def to_float(v):
    """Converteste o valoare CSV in float, sau None daca e goala/invalida."""
    try:
        return float(v) if v is not None and v.strip() != "" else None
    except ValueError:
        return None


def natural(path):
    """Cheie de sortare naturala: live2 inaintea lui live10."""
    return int(re.findall(r"\d+", os.path.basename(path))[0])


def find_column(cols, key):
    """Prima coloana al carei nume (uppercase) contine key."""
    return next((c for c in cols if key in c.upper()), None)


def is_active(speed, rpm):
    """Un rand e activ daca viteza sau RPM sunt peste 0."""
    return not (speed == 0.0 and rpm == 0.0)


def build_payload(row, cols, trip, now_iso, vehicle_id="TOYOTA_ETIOS_01"):
    """Construieste mesajul de telemetrie dintr-un rand CSV, sau None daca nu e activ."""
    speed = to_float(row.get(cols["speed"])) or 0.0
    rpm = to_float(row.get(cols["rpm"])) or 0.0
    if not is_active(speed, rpm):
        return None
    return {
        "vehicle_id": vehicle_id,
        "trip_id": trip,
        "timestamp": now_iso,
        "engine_run_time_s": to_float(row.get(cols["time"])) or 0.0,
        "vehicle_speed_kmh": speed,
        "engine_rpm": rpm,
        "throttle_pct": to_float(row.get(cols["throttle"])),
        "engine_load_pct": to_float(row.get(cols["load"])),
        "coolant_temp_c": to_float(row.get(cols["coolant"])),
    }


REQUIRED = ("vehicle_id", "timestamp", "vehicle_speed_kmh", "engine_rpm")


def parse_message(raw_bytes):
    """Decodeaza un mesaj MQTT. Ridica ValueError daca JSON-ul e invalid sau lipsesc campuri."""
    try:
        data = json.loads(raw_bytes.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"JSON invalid: {e}")
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        raise ValueError(f"campuri lipsa: {missing}")
    return data
