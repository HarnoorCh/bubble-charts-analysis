-- =====================================================================
-- FINAL: Country-level comparison — Control vs Treatment1 vs Treatment2
-- Metrics: % orders (traffic split), delay fail rate, HCSR, jump rate
--
-- Requires two upstream fixes in filtered_TAPI_logs:
--   1) allocation_id label:
--        REGEXP_EXTRACT(t.eta_format_config_allocation_id,
--                       r':(Control|Treatment\d+)$') AS model_version
--   2) allocation_id IN (...) filter must list all three arms, all under
--      the `tapi-config-variant` prefix:
--        'logistics-otx:tapi-config-variant:..._538:Control',
--        'logistics-otx:tapi-config-variant:..._538:Treatment1',
--        'logistics-otx:tapi-config-variant:..._538:Treatment2'
--
-- Replace the three `SELECT * FROM union_agg ... UNION ALL ...` blocks
-- with everything below. (Keep all CTEs through `union_agg` unchanged.)
-- =====================================================================

, country_level AS (
  SELECT
    region,
    entity,
    model_version,                                   -- 'Control' / 'Treatment1' / 'Treatment2'
    SUM(num_orders)                AS num_orders,
    SUM(delay_fail_rate_numerator) AS delay_fail_num,
    SUM(hcsr_numerator)            AS hcsr_num,
    SUM(jump_rate)                 AS jump_num
  FROM union_agg
  GROUP BY region, entity, model_version
),

-- Per-country rows AND an all-countries total (numerators summed per arm,
-- then divided -> a properly order-weighted total, not an average of rates)
arm_agg AS (
  SELECT
    entity,                                   -- NULL = total across all countries
    model_version,
    SUM(num_orders)     AS num_orders,
    SUM(delay_fail_num) AS delay_fail_num,
    SUM(hcsr_num)       AS hcsr_num,
    SUM(jump_num)       AS jump_num
  FROM country_level
  GROUP BY GROUPING SETS ((entity, model_version), (model_version))
)

SELECT
  COALESCE(entity, 'TOTAL') AS entity,

  -- % orders (traffic split across the three arms; sums to ~100%)
  ROUND(SAFE_DIVIDE(MAX(IF(model_version = 'Control',    num_orders, NULL)), SUM(num_orders)) * 100, 1) AS pct_orders_control,
  ROUND(SAFE_DIVIDE(MAX(IF(model_version = 'Treatment1', num_orders, NULL)), SUM(num_orders)) * 100, 1) AS pct_orders_t1,
  ROUND(SAFE_DIVIDE(MAX(IF(model_version = 'Treatment2', num_orders, NULL)), SUM(num_orders)) * 100, 1) AS pct_orders_t2,

  -- Delay fail rate
  ROUND(MAX(IF(model_version = 'Control',    SAFE_DIVIDE(delay_fail_num, num_orders), NULL)) * 100, 2) AS delay_fail_control,
  ROUND(MAX(IF(model_version = 'Treatment1', SAFE_DIVIDE(delay_fail_num, num_orders), NULL)) * 100, 2) AS delay_fail_t1,
  ROUND(MAX(IF(model_version = 'Treatment2', SAFE_DIVIDE(delay_fail_num, num_orders), NULL)) * 100, 2) AS delay_fail_t2,

  -- HC session rate (HCSR)
  ROUND(MAX(IF(model_version = 'Control',    SAFE_DIVIDE(hcsr_num, num_orders), NULL)) * 100, 2) AS hcsr_control,
  ROUND(MAX(IF(model_version = 'Treatment1', SAFE_DIVIDE(hcsr_num, num_orders), NULL)) * 100, 2) AS hcsr_t1,
  ROUND(MAX(IF(model_version = 'Treatment2', SAFE_DIVIDE(hcsr_num, num_orders), NULL)) * 100, 2) AS hcsr_t2,

  -- Jump rate
  ROUND(MAX(IF(model_version = 'Control',    SAFE_DIVIDE(jump_num, num_orders), NULL)) * 100, 2) AS jump_rate_control,
  ROUND(MAX(IF(model_version = 'Treatment1', SAFE_DIVIDE(jump_num, num_orders), NULL)) * 100, 2) AS jump_rate_t1,
  ROUND(MAX(IF(model_version = 'Treatment2', SAFE_DIVIDE(jump_num, num_orders), NULL)) * 100, 2) AS jump_rate_t2

FROM arm_agg
GROUP BY entity
ORDER BY (entity IS NULL), entity;   -- TOTAL row last
