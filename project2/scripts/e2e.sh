#!/usr/bin/env bash
# Test end-to-end: CSV mic -> MQTT -> consumer -> tabela de test -> reconciliere.
set -euo pipefail
cd "$(dirname "$0")/../.."
set -a; source .env; set +a

export TARGET_TABLE=obd_telemetry_test
export MQTT_TOPIC=fleet/telemetry_test
export MQTT_CLIENT_ID=e2e_consumer
export DATA_GLOB="project2/tests/data/live*.csv"
export SLEEP_S=0.001
export PYTHONPATH=src

PSQL="docker exec project-postgres-1 psql -U $POSTGRES_USER -d $POSTGRES_DB -q"
$PSQL -c "DROP TABLE IF EXISTS $TARGET_TABLE"
$PSQL -c "CREATE TABLE $TARGET_TABLE (LIKE obd_telemetry INCLUDING DEFAULTS)"

python src/ingestion/consumer.py > /tmp/e2e_consumer.log 2>&1 &
CONSUMER_PID=$!
trap 'kill $CONSUMER_PID 2>/dev/null || true' EXIT
sleep 3

python src/collector/emulator.py
sleep 3

set +e
python project2/scripts/reconcile.py --glob "$DATA_GLOB" --table "$TARGET_TABLE"
CODE=$?
set -e

$PSQL -c "DROP TABLE IF EXISTS $TARGET_TABLE"
exit $CODE
