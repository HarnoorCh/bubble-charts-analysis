DECLARE start_date DATE DEFAULT '2026-06-11';
DECLARE start_timestamp TIMESTAMP DEFAULT '2026-06-11 13:59:22.710337 UTC';
DECLARE exp_name STRING DEFAULT '2026-06-11_TB_Jump_Station_v2_All_Countries:538';

WITH filtered_TAPI_logs AS (
  SELECT
    t.created_date,
    t.created_at,
    CASE WHEN t.country_code IN ('t3', 't5') THEN 'tr' ELSE t.country_code END AS country_code,
    t.order_id,
    t.customer_id,
    t.eta_format_config_allocation_id AS allocation_id,
    CASE
      WHEN CONTAINS_SUBSTR(t.eta_format_config_allocation_id, 'Control')    THEN 'Control'
      WHEN CONTAINS_SUBSTR(t.eta_format_config_allocation_id, 'Treatment2') THEN 'Treatment2'
      WHEN CONTAINS_SUBSTR(t.eta_format_config_allocation_id, 'Treatment1') THEN 'Treatment1'
      ELSE 'Treatment'
    END AS model_version
  FROM `fulfillment-dwh-production.cl.tracking_api_logs` t
  WHERE t.created_date BETWEEN DATE(start_date) AND CURRENT_DATE() - 1
    AND t.created_at >= CAST(start_timestamp AS TIMESTAMP)
    AND t.eta_format_config_allocation_id IN (
      'logistics-otx:tapi-config-variant:2026-06-11_TB_Jump_Station_v2_All_Countries:538:Treatment1',
      'logistics-otx:tapi-config-variant:2026-06-11_TB_Jump_Station_v2_All_Countries:538:Treatment2',
      'logistics-otx:tapi-config-variant:2026-06-11_TB_Jump_Station_v2_All_Countries:538:Control'
    )
    AND metadata.user_agent NOT LIKE '%Go-http-client%'
    AND metadata.user_agent NOT LIKE '%Ktor%'
    AND metadata.user_agent NOT LIKE '%Vert.x-WebClient%'
    AND metadata.user_agent NOT LIKE '%gfs-order-processing%'
    AND metadata.user_agent NOT LIKE '%PostmanRuntime%'
    AND metadata.user_agent NOT LIKE '%Faraday%'
    AND (t.customer_id IS NOT NULL AND t.customer_id != '')
    AND TIMESTAMP_TRUNC(TIMESTAMP(model_prediction_median_bound_timestamp), MINUTE) != '1970-01-01 00:00:00 UTC'
),

traffic_splitting AS (
  SELECT
    MIN(fl.created_date) AS created_date,
    fl.country_code,
    fl.order_id,
    fl.customer_id,
    fl.allocation_id,
    exp_name AS model_version_name,
    fl.model_version
  FROM filtered_TAPI_logs fl
  GROUP BY 2, 3, 4, 5, 6, 7
),

orders AS (
  SELECT
    created_date,
    CASE WHEN country_code IN ('t3', 't5') THEN 'tr' ELSE country_code END AS country_code,
    global_order_id,
    order_status
  FROM `fulfillment-dwh-production.cl.orders` AS a, UNNEST(deliveries) AS r
  WHERE a.created_date BETWEEN DATE(start_date) AND CURRENT_DATE() - 1
    AND r.is_primary
),

jump_data AS (
  SELECT
    country_code,
    order_id,
    MAX(CASE WHEN jump_pct_num = 1 THEN 1 ELSE 0 END) AS jump_pct_flag,
    SUM(jump_magnitude) AS jump_magnitude
  FROM `fulfillment-dwh-production.cl._otx_jumps_data`
  WHERE created_date BETWEEN DATE(start_date) AND CURRENT_DATE() - 1
    AND jump_pct_num != 100
  GROUP BY 1, 2
),

delay_based_contacts AS (
  SELECT
    CASE WHEN global_entity_id LIKE 'GV%'
      THEN CONCAT('gv', '-', LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]))
      ELSE LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]) END AS country_code,
    order_id
  FROM `fulfillment-dwh-production.cl.all_contacts`
  WHERE stakeholder = 'Customer'
    AND global_cr_code IN ('1A.1','1A.2','1A.3','1A.5','1A.10','1A.12','1A.13','1A.14','1A.15','1C.1','1C.5')
    AND order_id IS NOT NULL
    AND created_date BETWEEN start_date AND CURRENT_DATE() - 1
  GROUP BY 1, 2
),

live_order_hc_sessions AS (
  SELECT
    CASE WHEN global_entity_id LIKE 'GV%'
      THEN CONCAT('gv', '-', LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]))
      ELSE LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]) END AS country_code,
    order_id
  FROM `fulfillment-dwh-production.cl.cfx_conversations`
  WHERE stakeholder = 'Customer'
    AND order_id IS NOT NULL
    AND EXISTS (
      SELECT 1 FROM UNNEST(SPLIT(all_distinct_ccrs_visited, ',')) AS ccr
      WHERE TRIM(ccr) IN ('1A.1','1A.2','1A.3','1A.5','1A.10','1A.12','1A.13','1A.14','1A.15','1C.1','1C.5')
    )
    AND created_date BETWEEN start_date AND CURRENT_DATE() - 1
  GROUP BY 1, 2
  UNION DISTINCT
  SELECT
    CASE WHEN global_entity_id LIKE 'GV%'
      THEN CONCAT('gv', '-', LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]))
      ELSE LOWER(SPLIT(global_entity_id, '_')[SAFE_OFFSET(1)]) END AS country_code,
    order_id
  FROM `fulfillment-dwh-production.cl.helpcenter_sessions` AS a
  LEFT JOIN UNNEST(contacts_created) AS c
  WHERE order_id IS NOT NULL
    AND helpcenter = 'Customer'
    AND (last_ccr IN ('1A.1','1A.2','1A.3','1A.5','1A.10','1A.12','1A.13','1A.14','1A.15','1C.1','1C.5')
      OR c.agent_ccr IN ('1A.1','1A.2','1A.3','1A.5','1A.10','1A.12','1A.13','1A.14','1A.15','1C.1','1C.5'))
    AND created_date BETWEEN start_date AND CURRENT_DATE() - 1
  GROUP BY 1, 2
),

seamless_fail_rate AS (
  SELECT
    CASE WHEN o.country_code IN ('t3', 't5') THEN 'tr' ELSE o.country_code END AS country_code,
    o.global_order_id,
    MAX(CASE WHEN o.cancellation.reason IN ('DELIVERY_ETA_TOO_LONG', 'LATE_DELIVERY', 'MISTAKE_ERROR', 'NO_COURIER') THEN 1 ELSE 0 END) AS is_cancelled
  FROM `fulfillment-dwh-production.cl.orders` AS o, UNNEST(o.deliveries) AS d
  WHERE o.created_date BETWEEN start_date AND CURRENT_DATE() - 1
    AND d.is_primary
  GROUP BY 1, 2
),

final_agg AS (
  SELECT
    a.created_date AS day,
    a.country_code AS entity,
    a.order_id,
    a.customer_id,
    a.model_version,
    IF(b.order_status = 'completed', 1, 0) AS completed_order_id,
    IF(m.is_cancelled > 0, 1, 0) AS seamless_fail_rate,
    IF(d.order_id IS NOT NULL, 1, 0) AS contact_rate,
    IF(e.order_id IS NOT NULL, 1, 0) AS hc_session_rate,
    COALESCE(j.jump_pct_flag, 0) AS jump_rate,
    COALESCE(j.jump_magnitude, 0) AS jump_magnitude
  FROM traffic_splitting AS a
  LEFT JOIN orders AS b ON a.order_id = b.global_order_id AND a.country_code = b.country_code
  LEFT JOIN seamless_fail_rate AS m ON a.order_id = m.global_order_id AND a.country_code = m.country_code
  LEFT JOIN delay_based_contacts AS d ON a.order_id = d.order_id AND a.country_code = d.country_code
  LEFT JOIN live_order_hc_sessions AS e ON a.order_id = e.order_id AND a.country_code = e.country_code
  LEFT JOIN jump_data AS j ON a.order_id = j.order_id AND a.country_code = j.country_code
)

-- ============ DAILY: global ============
SELECT 'global' AS level, 'global' AS entity, CAST(day AS STRING) AS day, model_version,
  COUNT(DISTINCT order_id) AS num_orders,
  COUNT(DISTINCT customer_id) AS customers,
  ROUND(SAFE_DIVIDE(SUM(seamless_fail_rate), COUNT(DISTINCT order_id)) * 100, 3) AS seamless_fail_rate_pct,
  ROUND(SAFE_DIVIDE(SUM(contact_rate), COUNT(DISTINCT order_id)) * 100, 3) AS ccr_pct,
  ROUND(SAFE_DIVIDE(SUM(hc_session_rate), COUNT(DISTINCT order_id)) * 100, 3) AS hcsr_pct,
  ROUND(SAFE_DIVIDE(SUM(completed_order_id), COUNT(DISTINCT customer_id)), 4) AS order_per_customer,
  ROUND(SAFE_DIVIDE(SUM(jump_rate), COUNT(DISTINCT order_id)) * 100, 3) AS jump_rate_pct,
  ROUND(SAFE_DIVIDE(SUM(jump_magnitude), NULLIF(SUM(jump_rate),0)), 2) AS jump_magnitude_avg
FROM final_agg GROUP BY day, model_version

UNION ALL
-- ============ DAILY: country ============
SELECT 'country' AS level, entity, CAST(day AS STRING) AS day, model_version,
  COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id),
  ROUND(SAFE_DIVIDE(SUM(seamless_fail_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(contact_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(hc_session_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(completed_order_id), COUNT(DISTINCT customer_id)), 4),
  ROUND(SAFE_DIVIDE(SUM(jump_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(jump_magnitude), NULLIF(SUM(jump_rate),0)), 2)
FROM final_agg GROUP BY entity, day, model_version

UNION ALL
-- ============ TOTAL: global ============
SELECT 'global' AS level, 'global' AS entity, 'TOTAL' AS day, model_version,
  COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id),
  ROUND(SAFE_DIVIDE(SUM(seamless_fail_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(contact_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(hc_session_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(completed_order_id), COUNT(DISTINCT customer_id)), 4),
  ROUND(SAFE_DIVIDE(SUM(jump_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(jump_magnitude), NULLIF(SUM(jump_rate),0)), 2)
FROM final_agg GROUP BY model_version

UNION ALL
-- ============ TOTAL: country ============
SELECT 'country' AS level, entity, 'TOTAL' AS day, model_version,
  COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id),
  ROUND(SAFE_DIVIDE(SUM(seamless_fail_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(contact_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(hc_session_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(completed_order_id), COUNT(DISTINCT customer_id)), 4),
  ROUND(SAFE_DIVIDE(SUM(jump_rate), COUNT(DISTINCT order_id)) * 100, 3),
  ROUND(SAFE_DIVIDE(SUM(jump_magnitude), NULLIF(SUM(jump_rate),0)), 2)
FROM final_agg GROUP BY entity, model_version

ORDER BY level, entity, day, model_version
