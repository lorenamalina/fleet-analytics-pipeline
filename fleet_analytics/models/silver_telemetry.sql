{{ config(materialized='table') }}

SELECT
    id,
    trip_id,
    vehicle_id,
    "timestamp" AS telemetry_timestamp,
    engine_run_time_s,
    vehicle_speed_kmh,
    engine_rpm,
    throttle_pct,
    engine_load_pct,
    coolant_temp_c
FROM {{ source('raw', 'obd_telemetry') }}
WHERE vehicle_speed_kmh IS NOT NULL
  AND engine_rpm IS NOT NULL
  AND vehicle_speed_kmh >= 0
