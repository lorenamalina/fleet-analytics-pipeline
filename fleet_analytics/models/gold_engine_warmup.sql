{{ config(materialized='table') }}

WITH per_trip AS (
    SELECT trip_id, MIN(engine_run_time_s) AS t0
    FROM {{ ref('silver_telemetry') }}
    WHERE coolant_temp_c IS NOT NULL
    GROUP BY trip_id
),

temps AS (
    SELECT
        s.trip_id,
        s.engine_run_time_s - p.t0 AS t_rel_s,
        s.coolant_temp_c
    FROM {{ ref('silver_telemetry') }} s
    JOIN per_trip p USING (trip_id)
    WHERE s.coolant_temp_c IS NOT NULL
),

agg AS (
    SELECT
        trip_id,
        MIN(coolant_temp_c) FILTER (WHERE t_rel_s <= 30) AS start_temp_raw,
        MAX(coolant_temp_c)                              AS max_temp_raw,
        MIN(t_rel_s) FILTER (WHERE coolant_temp_c >= 80) AS t80_raw
    FROM temps
    GROUP BY trip_id
)

SELECT
    trip_id,
    ROUND(start_temp_raw, 1)                  AS start_temp_c,
    ROUND(max_temp_raw, 1)                    AS max_temp_c,
    ROUND(max_temp_raw - start_temp_raw, 1)   AS warmup_delta_c,
    CASE WHEN start_temp_raw < 60 THEN 'cold' ELSE 'warm' END AS start_type,
    CASE WHEN start_temp_raw < 60 THEN t80_raw END            AS seconds_to_80c
FROM agg
