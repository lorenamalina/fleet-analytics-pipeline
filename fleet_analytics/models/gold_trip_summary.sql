{{ config(materialized='table') }}

SELECT
    trip_id,
    vehicle_id,
    SUM(dt_seconds)                                               AS measured_seconds,
    ROUND(SUM(speed_kmh / 3.6 * dt_seconds) / 1000, 2)            AS distance_km,
    ROUND(AVG(speed_kmh) FILTER (WHERE phase <> 'stationary'), 1) AS avg_moving_speed_kmh,
    MAX(speed_kmh)                                                AS max_speed_kmh,
    ROUND(100.0 * SUM(dt_seconds) FILTER (WHERE phase = 'stationary')
          / NULLIF(SUM(dt_seconds), 0), 1)                        AS pct_time_stationary
FROM {{ ref('gold_trip_phases') }}
GROUP BY trip_id, vehicle_id
