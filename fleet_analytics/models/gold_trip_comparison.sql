{{ config(materialized='table') }}

WITH events AS (
    SELECT
        trip_id,
        COUNT(*) FILTER (WHERE driving_event = 'harsh_braking')      AS harsh_braking_n,
        COUNT(*) FILTER (WHERE driving_event = 'harsh_acceleration') AS harsh_accel_n
    FROM {{ ref('gold_driving_behavior') }}
    GROUP BY trip_id
),

stops AS (
    SELECT trip_id, COUNT(*) AS stationary_periods
    FROM {{ ref('gold_stops') }}
    WHERE phase = 'stationary'
    GROUP BY trip_id
),

combined AS (
    SELECT
        s.trip_id,
        s.vehicle_id,
        s.measured_seconds,
        s.distance_km,
        s.avg_moving_speed_kmh,
        s.max_speed_kmh,
        s.pct_time_stationary,
        COALESCE(st.stationary_periods, 0) AS stationary_periods,
        COALESCE(e.harsh_braking_n, 0)     AS harsh_braking_n,
        COALESCE(e.harsh_accel_n, 0)       AS harsh_accel_n,
        COALESCE(e.harsh_braking_n, 0) + COALESCE(e.harsh_accel_n, 0) AS harsh_events_total,
        ROUND(100 * (COALESCE(e.harsh_braking_n, 0) + COALESCE(e.harsh_accel_n, 0))
              / NULLIF(s.distance_km, 0), 2) AS harsh_events_per_100km,
        ROUND(1000.0 * (COALESCE(e.harsh_braking_n, 0) + COALESCE(e.harsh_accel_n, 0))
              / NULLIF(s.measured_seconds, 0), 2) AS harsh_events_per_1000s,
        (s.distance_km < 5) AS low_confidence
    FROM {{ ref('gold_trip_summary') }} s
    LEFT JOIN events e USING (trip_id)
    LEFT JOIN stops  st USING (trip_id)
)

SELECT *,
    ROUND((100 * PERCENT_RANK() OVER (ORDER BY harsh_events_per_1000s))::numeric, 0)
        AS aggressiveness_percentile
FROM combined
