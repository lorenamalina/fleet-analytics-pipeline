import pytest
from common.telemetry import (
    to_float, natural, find_column, is_active, build_payload, parse_message,
)

COLS = {"time": "t", "speed": "v", "rpm": "r",
        "throttle": "th", "load": "ld", "coolant": "ct"}


def test_to_float_valid():
    assert to_float("12.5") == 12.5

@pytest.mark.parametrize("bad", ["", "  ", "abc", None])
def test_to_float_invalid_returns_none(bad):
    assert to_float(bad) is None

def test_natural_sorts_numerically():
    paths = ["live10.csv", "live2.csv", "live1.csv"]
    assert sorted(paths, key=natural) == ["live1.csv", "live2.csv", "live10.csv"]

def test_find_column_case_insensitive():
    assert find_column(["Time", "Vehicle_Speed (km/h)"], "VEHICLE_SPEED") == "Vehicle_Speed (km/h)"
    assert find_column(["a", "b"], "RPM") is None

def test_is_active():
    assert is_active(0.0, 800.0)
    assert is_active(10.0, 0.0)
    assert not is_active(0.0, 0.0)

def test_build_payload_valid_row():
    row = {"t": "5", "v": "30", "r": "1500", "th": "20", "ld": "35", "ct": "80"}
    p = build_payload(row, COLS, "live1", "2026-01-01T00:00:00")
    assert p["trip_id"] == "live1"
    assert p["vehicle_speed_kmh"] == 30.0
    assert p["coolant_temp_c"] == 80.0

def test_build_payload_inactive_row_is_skipped():
    row = {"t": "5", "v": "0", "r": "0"}
    assert build_payload(row, COLS, "live1", "x") is None

def test_build_payload_missing_optional_values_are_none():
    row = {"t": "5", "v": "10", "r": "900"}
    p = build_payload(row, COLS, "live1", "x")
    assert p["throttle_pct"] is None and p["engine_load_pct"] is None

def test_parse_message_valid():
    raw = b'{"vehicle_id":"V","timestamp":"t","vehicle_speed_kmh":1,"engine_rpm":2}'
    assert parse_message(raw)["vehicle_id"] == "V"

def test_parse_message_malformed_json():
    with pytest.raises(ValueError, match="JSON invalid"):
        parse_message(b"{not json")

def test_parse_message_missing_fields():
    with pytest.raises(ValueError, match="campuri lipsa"):
        parse_message(b'{"vehicle_id":"V"}')
