{{ config(materialized='table') }}

SELECT
    trip_id,
    vehicle_id,
    engine_run_time_s,
    dt_seconds,
    speed_kmh,
    rpm,
    accel_ms2,
    CASE
        WHEN speed_kmh < 1    THEN 'stationary'
        WHEN accel_ms2 >  0.5 THEN 'accelerating'
        WHEN accel_ms2 < -0.5 THEN 'decelerating'
        ELSE 'cruising'
    END AS phase
FROM {{ ref('gold_driving_behavior') }}
