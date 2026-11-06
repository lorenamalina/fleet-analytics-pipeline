from reconcile import compare, expected_counts


def test_identical_has_no_diffs():
    assert compare({"live1": 5, "live2": 7}, {"live1": 5, "live2": 7}) == {}


def test_lost_messages_detected():
    assert compare({"live1": 5}, {"live1": 3}) == {"live1": (5, 3)}


def test_duplicates_detected():
    assert compare({"live1": 5}, {"live1": 10}) == {"live1": (5, 10)}


def test_missing_trip_in_db():
    assert compare({"live1": 5}, {}) == {"live1": (5, 0)}


def test_unexpected_trip_in_db():
    assert compare({}, {"live9": 4}) == {"live9": (0, 4)}


def test_expected_counts_from_csv(tmp_path):
    header = "ENGINE_RUN_TIME (s),VEHICLE_SPEED (km/h),ENGINE_RPM (RPM)\n"
    (tmp_path / "live1.csv").write_text(header + "1,0,0\n2,10,900\n3,0,800\n")
    (tmp_path / "live2.csv").write_text(header + "1,0,0\n")
    got = expected_counts(str(tmp_path / "live*.csv"))
    assert got == {"live1": 2, "live2": 0}
