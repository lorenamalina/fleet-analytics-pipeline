{{ config(materialized='table') }}

SELECT
    vehicle_id,
    COUNT(DISTINCT trip_id)          AS trips,
    COUNT(*)                         AS total_telemetry_points,
    ROUND(AVG(vehicle_speed_kmh), 2) AS avg_speed_kmh,
    MAX(vehicle_speed_kmh)           AS max_speed_kmh,
    MAX(engine_rpm)                  AS max_engine_rpm
FROM {{ ref('silver_telemetry') }}
GROUP BY vehicle_id
