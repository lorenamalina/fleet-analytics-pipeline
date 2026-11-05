{{ config(materialized='table') }}

SELECT
    trip_id,
    ROUND(AVG(engine_load_pct), 1)                   AS avg_engine_load_pct,
    ROUND(AVG(throttle_pct), 1)                      AS avg_throttle_pct,
    ROUND(AVG(engine_rpm), 0)                        AS avg_rpm,
    ROUND(CORR(engine_load_pct, throttle_pct)::numeric, 2)      AS corr_load_throttle,
    ROUND(CORR(engine_load_pct, vehicle_speed_kmh)::numeric, 2) AS corr_load_speed,
    ROUND(CORR(engine_rpm, vehicle_speed_kmh)::numeric, 2)      AS corr_rpm_speed
FROM {{ ref('silver_telemetry') }}
WHERE engine_load_pct IS NOT NULL
  AND throttle_pct IS NOT NULL
GROUP BY trip_id
