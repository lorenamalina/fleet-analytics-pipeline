SELECT *
FROM {{ ref('silver_telemetry') }}
WHERE vehicle_speed_kmh > 250
   OR engine_rpm > 8000
   OR (engine_load_pct IS NOT NULL AND engine_load_pct NOT BETWEEN 0 AND 100)
   OR (throttle_pct IS NOT NULL AND throttle_pct NOT BETWEEN 0 AND 100)
   OR (coolant_temp_c IS NOT NULL AND coolant_temp_c NOT BETWEEN -40 AND 130)
