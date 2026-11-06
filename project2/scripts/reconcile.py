"""Reconciliere CSV vs. Postgres: numara randurile active per cursa si le compara.

Cod de iesire: 0 = identic, 1 = diferente, 2 = eroare (conexiune, fara fisiere).
"""
import argparse
import glob
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from common.telemetry import natural  # noqa: E402
from common.trip_reader import read_trip, trip_name  # noqa: E402


def expected_counts(data_glob):
    """{trip_id: numar de randuri active} calculat direct din CSV-uri."""
    counts = {}
    for path in sorted(glob.glob(data_glob), key=natural):
        counts[trip_name(path)] = sum(1 for _ in read_trip(path))
    return counts


def db_counts(table):
    """{trip_id: numar de randuri} din Postgres. Credentialele vin din variabile de mediu."""
    import psycopg2
    conn = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DB"],
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT trip_id, COUNT(*) FROM {table} GROUP BY trip_id")
            return {t: int(n) for t, n in cur.fetchall()}
    finally:
        conn.close()


def compare(expected, got):
    """Returneaza {trip_id: (asteptat, gasit)} doar pentru cursele cu diferente.

    Include si cursele din baza care nu exista in CSV (asteptat = 0).
    """
    diffs = {}
    for trip in set(expected) | set(got):
        e, g = expected.get(trip, 0), got.get(trip, 0)
        if e != g:
            diffs[trip] = (e, g)
    return diffs


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glob", default="src/collector/dataset_obd/live*.csv")
    ap.add_argument("--table", default="obd_telemetry")
    args = ap.parse_args(argv)

    exp = expected_counts(args.glob)
    if not exp:
        print(f"Niciun fisier gasit pentru: {args.glob}")
        return 2
    try:
        got = db_counts(args.table)
    except Exception as e:
        print(f"Eroare la citirea din baza de date: {e}")
        return 2

    diffs = compare(exp, got)
    print(f"curse in CSV: {len(exp)} | curse in baza: {len(got)}")
    print(f"total asteptat: {sum(exp.values())} | total in baza: {sum(got.values())}")
    if diffs:
        print("diferente (asteptat, gasit):")
        for trip in sorted(diffs, key=natural):
            print(f"  {trip}: {diffs[trip]}")
        return 1
    print("diferente: niciuna")
    return 0


if __name__ == "__main__":
    sys.exit(main())
