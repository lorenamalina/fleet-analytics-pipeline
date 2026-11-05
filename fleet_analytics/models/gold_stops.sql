{{ config(materialized='table') }}

{% set max_bridge_gap_s = 9 %}

WITH flagged AS (
    SELECT *,
        LAG(phase) OVER w AS prev_phase,
        engine_run_time_s - LAG(engine_run_time_s) OVER w AS gap_s
    FROM {{ ref('gold_trip_phases') }}
    WINDOW w AS (PARTITION BY trip_id ORDER BY engine_run_time_s)
),

marked AS (
    SELECT *,
        CASE
            WHEN gap_s IS NULL THEN 1
            WHEN prev_phase IS DISTINCT FROM phase THEN 1
            WHEN gap_s <= 2 THEN 0
            WHEN phase = 'stationary' AND gap_s <= {{ max_bridge_gap_s }} THEN 0
            ELSE 1
        END AS new_island
    FROM flagged
),

islands AS (
    SELECT *,
        SUM(new_island) OVER (PARTITION BY trip_id ORDER BY engine_run_time_s) AS island_id
    FROM marked
)

SELECT
    trip_id,
    vehicle_id,
    island_id,
    phase,
    MIN(engine_run_time_s)                          AS start_s,
    MAX(engine_run_time_s)                          AS end_s,
    MAX(engine_run_time_s) - MIN(engine_run_time_s) AS span_s,
    SUM(dt_seconds)                                 AS duration_s,
    ROUND(AVG(rpm))                                 AS avg_rpm
FROM islands
GROUP BY trip_id, vehicle_id, island_id, phase
