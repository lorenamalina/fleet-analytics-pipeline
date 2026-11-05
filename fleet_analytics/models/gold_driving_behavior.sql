{{ config(materialized='table') }}

WITH per_second AS (
    SELECT
        trip_id,
        vehicle_id,
        engine_run_time_s,
        ROUND(AVG(vehicle_speed_kmh), 2) AS speed_kmh,
        ROUND(AVG(engine_rpm), 0)        AS rpm,
        MIN(id)                          AS first_id
    FROM {{ ref('silver_telemetry') }}
    GROUP BY trip_id, vehicle_id, engine_run_time_s
),

ordered AS (
    SELECT *,
        LAG(speed_kmh)         OVER w AS prev_speed_kmh,
        LAG(engine_run_time_s) OVER w AS prev_t
    FROM per_second
    WINDOW w AS (PARTITION BY trip_id ORDER BY first_id)
),

accel AS (
    SELECT *,
        engine_run_time_s - prev_t AS dt_seconds,
        ((speed_kmh - prev_speed_kmh) / 3.6)
            / NULLIF(engine_run_time_s - prev_t, 0) AS accel_ms2
    FROM ordered
    WHERE prev_t IS NOT NULL
      AND engine_run_time_s - prev_t BETWEEN 1 AND 2
)

SELECT
    trip_id,
    vehicle_id,
    engine_run_time_s,
    speed_kmh,
    rpm,
    dt_seconds,
    ROUND(accel_ms2::numeric, 2) AS accel_ms2,
    CASE
        WHEN accel_ms2 <= -2.5 THEN 'harsh_braking'
        WHEN accel_ms2 >=  2.5 THEN 'harsh_acceleration'
        ELSE 'normal'
    END AS driving_event
FROM accel
