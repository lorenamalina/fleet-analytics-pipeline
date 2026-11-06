from common.trip_reader import read_trip, trip_name

HEADER = ("ENGINE_RUN_TIME (s),VEHICLE_SPEED (km/h),ENGINE_RPM (RPM),"
          "THROTTLE () (%),ENGINE_LOAD (%),COOLANT_TEMPERATURE (C)\n")


def write_csv(tmp_path, rows, name="live7.csv"):
    p = tmp_path / name
    p.write_text(HEADER + "".join(rows))
    return str(p)


def test_trip_name():
    assert trip_name("/data/live12.csv") == "live12"


def test_inactive_rows_are_skipped(tmp_path):
    path = write_csv(tmp_path, [
        "1,0,0,0,0,25\n",        # inactiv
        "2,10,900,5,30,26\n",    # activ
        "3,0,800,0,20,27\n",     # activ (RPM > 0)
    ])
    out = list(read_trip(path, now=lambda: "T"))
    assert len(out) == 2
    assert out[0]["trip_id"] == "live7"
    assert out[0]["vehicle_speed_kmh"] == 10.0
    assert out[1]["engine_rpm"] == 800.0
    assert out[0]["timestamp"] == "T"


def test_optional_values_missing_become_none(tmp_path):
    path = write_csv(tmp_path, ["5,20,1000,,,\n"])
    p = list(read_trip(path))[0]
    assert p["throttle_pct"] is None
    assert p["engine_load_pct"] is None
    assert p["coolant_temp_c"] is None


def test_missing_column_does_not_crash(tmp_path):
    f = tmp_path / "live1.csv"
    f.write_text("ENGINE_RUN_TIME (s),VEHICLE_SPEED (km/h),ENGINE_RPM (RPM)\n3,15,900\n")
    p = list(read_trip(str(f)))[0]
    assert p["coolant_temp_c"] is None
