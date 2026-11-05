SELECT * FROM {{ ref('gold_driving_behavior') }}
WHERE dt_seconds NOT BETWEEN 1 AND 2
