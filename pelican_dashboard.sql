--tochange
DECLARE start_date DATE DEFAULT '2026-06-10';
DECLARE end_date DATE DEFAULT current_date()-1;
DECLARE pre_experiment_days INT64 DEFAULT 14;
DECLARE allo STRING DEFAULT '%2026-06-10_PT_pelican_shops_global%';

WITH deliveries AS (
  SELECT ds.country_code,
  ds.order_id,
  d.rider_near_restaurant_at,
  d.rider_picked_up_at,
  d.rider_left_vendor_at,
  d.rider_dropped_off_at,
  d.auto_transition.pickup,
  FROM `fulfillment-dwh-production.cl._deliveries` ds LEFT JOIN UNNEST(ds.deliveries) d
  WHERE ds.created_date BETWEEN start_date-pre_experiment_days AND end_date
  AND d.is_primary
),

 woowa_order_id_mapping AS (
  SELECT * FROM fulfillment-dwh-production.curated_data_shared_woowa_korea.woowa_order_id_mapping
  WHERE TRUE
  AND partition_date BETWEEN start_date-pre_experiment_days AND end_date
),


shared_ds_orders AS (
  SELECT DISTINCT
      DATE(placed_at) AS created_date,
      CASE WHEN global_entity_id='BM_KR' THEN w.plain_order_id ELSE os.order_id END AS order_id,
      vendor_id,
      global_entity_id,
      value.order.gmv_eur,
      failure_owner,
      CASE WHEN (delivery_fee_option = 'PRIORITY' ) THEN 'PRIORITY'
      WHEN (delivery_fee_option = 'STANDARD' OR delivery_fee_option IS NULL) THEN 'STANDARD'
      WHEN (delivery_fee_option = 'SAVER') THEN 'SAVER'
      ELSE delivery_fee_option
      END AS delivery_fee_option
  FROM fulfillment-dwh-production.curated_data_shared_coredata_business.orders os
  LEFT JOIN woowa_order_id_mapping w ON os.order_id=w.order_id AND DATE(placed_at)=w.partition_date
  WHERE DATE(partition_date_local)BETWEEN start_date-pre_experiment_days AND end_date
  ),

  orders AS (
  SELECT
    o.entity.id AS global_entity_id,
    o.country_code,
    o.city_id,

    global_order_id,

    o.created_date,
    o.created_at,
    o.timezone,

    o.vendor.vendor_code,
    o.vendor.name AS vendor_name,
    o.items_count,
    o.vendor.vertical_type,
    `log-data-science-staging.hirbod.VERTICAL_CATEGORY`(o) AS vertical_category

    , estimated_prep_time
    , estimated_prep_buffer
    , o.timings.assumed_actual_preparation_time
    , o.timings.assumed_actual_preparation_time_source
    , o.sent_to_vendor_at
    , o.original_scheduled_pickup_at
    , ds.rider_near_restaurant_at
    , ds.rider_picked_up_at
    , ds.rider_left_vendor_at
    , ds.rider_dropped_off_at
    , ds.pickup
    , o.is_preorder
    , order_status
    , o.food_is_ready_at,
    r.stacked_deliveries_rank,


    ROUND(o.timings.actual_delivery_time / 60) AS DT,
    ROUND(o.timings.promised_delivery_time / 60) AS PDT,
    TIMESTAMP_DIFF(promised_delivery_time_upper_bound, order_placed_at, MINUTE) AS promised_delivery_time_upper_bound,
    TIMESTAMP_DIFF(promised_delivery_time_lower_bound, order_placed_at, MINUTE) AS promised_delivery_time_lower_bound,
    ROUND(o.timings.avoidable_wait_time / 60) AS AWT,
    -- ROUND(r.timings.at_vendor_time_cleaned_v2 / 60) AS avtc_v2,
    IF(ds.rider_near_restaurant_at IS NOT NULL, ROUND(o.timings.at_vendor_time/60), NULL) AS at_vendor_time_mins,
    IF(ds.rider_near_restaurant_at IS NOT NULL, ROUND(o.timings.at_vendor_time_cleaned/60), NULL) AS at_vendor_time_cleaned_mins,

    ROUND(r.timings.vendor_late / 60) AS vendor_late,
    ROUND(o.timings.rider_late / 60) AS rider_late,

    DATETIME_DIFF(ds.rider_picked_up_at,o.created_at,MINUTE) AS time_diff_rider_pickup


  FROM `fulfillment-dwh-production.cl.orders` o, UNNEST(deliveries) r
  LEFT JOIN deliveries ds ON ds.country_code = o.country_code
        AND ds.order_id = o.order_id

  WHERE o.created_date BETWEEN start_date-pre_experiment_days AND end_date
  --AND order_status = 'completed'
  AND r.is_primary
  GROUP BY ALL
),


    --Reading contacts data for seamless scope reasons
contacts AS (
  SELECT
    order_id,
    global_entity_id,
    LOWER(SPLIT(global_entity_id,'_')[OFFSET(1)]) country_code,
    created_date,
    COUNT(contact_id) AS contact_count
  FROM `fulfillment-dwh-production.cl.all_contacts`
  WHERE stakeholder = 'Customer'
    AND global_entity_id IS NOT NULL
    AND order_id IS NOT NULL
    AND created_date BETWEEN DATE(start_date-pre_experiment_days) AND DATE(end_date)
    AND global_cr_code IN ('1A.1', '1A.2', '1A.3', '1A.5', '1A.7', '1A.10', '1A.11', '1A.12', '1A.13', '1A.14', '1A.15', '1C.1', '1C.5', '2D.1', '2D.2', '2D.3', '2D.4', '2D.5', '2D.6')
    GROUP BY 1, 2, 3, 4
),

--Reading HCSR data for seamless scope leaves
hc_orders_sessions AS (
 SELECT
    created_date,
    global_entity_id,
    order_id,
    COUNT(session_id) AS hc_session_cnt
  FROM `fulfillment-dwh-production.cl.helpcenter_sessions` LEFT JOIN UNNEST(contacts_created) c
  WHERE global_entity_id IS NOT NULL
    AND order_id IS NOT NULL
    AND helpcenter = 'Customer'
   --Updated to new HCSR definition
    AND (last_ccr IN ('1A.1', '1A.2', '1A.3', '1A.5',  '1A.7', '1A.11', '1A.10', '1A.12', '1A.13', '1A.14',
    '1A.15', '1C.1', '1C.5', '2D.1', '2D.2', '2D.3', '2D.4', '2D.5', '2D.6')
    OR c.agent_ccr IN ('1A.1', '1A.2', '1A.3', '1A.5',  '1A.7', '1A.11', '1A.10', '1A.12', '1A.13', '1A.14',
    '1A.15', '1C.1', '1C.5', '2D.1', '2D.2', '2D.3', '2D.4', '2D.5', '2D.6'))
    AND created_date BETWEEN DATE(start_date-pre_experiment_days) AND DATE(end_date)
  GROUP BY 1, 2, 3
),



-- Have checked overall number of orders at this part and the numbers look good
orders_data AS (
   SELECT
    o.global_entity_id,
    o.country_code,
    city_id,

    global_order_id,

    o.created_date,
    DATE(DATETIME(o.created_at,o.timezone)) AS local_created_date,
    created_at,
    timezone,

    is_preorder,
    order_status,

    ROUND(estimated_prep_time / 60) AS EPT,
    CASE WHEN assumed_actual_preparation_time_source!='censored' THEN ROUND(assumed_actual_preparation_time / 60) ELSE NULL END AS AAPT,
    DT,
    PDT,
    AWT,
    --avtc_v2,
    at_vendor_time_mins,
    at_vendor_time_cleaned_mins,
    stacked_deliveries_rank,
    time_diff_rider_pickup,
    --tochange: sKPI commented out - not in scope for this test
    --0.3*(at_vendor_time_mins-AWT)+0.45*AWT+0.25*time_diff_rider_pickup AS sKPI,
    -- PET (Pickup Efficiency Time) - platform-specific weights
    CASE SPLIT(o.global_entity_id, '_')[OFFSET(0)]
      WHEN 'HS' THEN 0.70*time_diff_rider_pickup + 0.30*AWT + 0.00*(at_vendor_time_mins-AWT)
      WHEN 'TB' THEN 0.50*time_diff_rider_pickup + 0.40*AWT + 0.10*(at_vendor_time_mins-AWT)
      WHEN 'YS' THEN 0.50*time_diff_rider_pickup + 0.40*AWT + 0.10*(at_vendor_time_mins-AWT)
      WHEN 'GV' THEN 0.20*time_diff_rider_pickup + 0.40*AWT + 0.40*(at_vendor_time_mins-AWT)
      WHEN 'PY' THEN 0.25*time_diff_rider_pickup + 0.50*AWT + 0.25*(at_vendor_time_mins-AWT)
      WHEN 'EF' THEN 0.20*time_diff_rider_pickup + 0.40*AWT + 0.40*(at_vendor_time_mins-AWT)
      WHEN 'FY' THEN 0.20*time_diff_rider_pickup + 0.40*AWT + 0.40*(at_vendor_time_mins-AWT)
      ELSE 0.25*time_diff_rider_pickup + 0.45*AWT + 0.30*(at_vendor_time_mins-AWT)
    END AS PET,

    vendor_late,
    rider_late,
    co.contact_count,
    hc.hc_session_cnt,


    o.vertical_category vertical_group,
    o.vertical_type,
    o.vendor_name,
    o.items_count,
    s.gmv_eur,

    o.vendor_code,
    delivery_fee_option,
    CASE WHEN delivery_fee_option = 'PRIORITY' AND promised_delivery_time_upper_bound IS NOT NULL THEN promised_delivery_time_upper_bound ELSE NULL END AS priority_upper_limit,
      CASE WHEN delivery_fee_option = 'PRIORITY' AND promised_delivery_time_lower_bound IS NOT NULL THEN promised_delivery_time_lower_bound ELSE NULL END AS priority_lower_limit,
      CASE WHEN delivery_fee_option = 'PRIORITY' AND pdt IS NOT NULL THEN pdt ELSE NULL END AS priority_single_value,

      CASE WHEN delivery_fee_option = 'SAVER' AND promised_delivery_time_upper_bound IS NOT NULL THEN promised_delivery_time_upper_bound ELSE NULL END AS saver_upper_limit,
      CASE WHEN delivery_fee_option = 'SAVER' AND promised_delivery_time_lower_bound IS NOT NULL THEN promised_delivery_time_lower_bound ELSE NULL END AS saver_lower_limit,
      CASE WHEN delivery_fee_option = 'SAVER' AND pdt IS NOT NULL THEN pdt ELSE NULL END AS saver_single_value,

      CASE WHEN delivery_fee_option = 'STANDARD' AND promised_delivery_time_upper_bound IS NOT NULL THEN promised_delivery_time_upper_bound ELSE NULL END AS standard_upper_limit,
      CASE WHEN delivery_fee_option = 'STANDARD' AND promised_delivery_time_lower_bound IS NOT NULL THEN promised_delivery_time_lower_bound ELSE NULL END AS standard_lower_limit,
      CASE WHEN delivery_fee_option = 'STANDARD' AND pdt IS NOT NULL THEN pdt ELSE NULL END AS standard_single_value,

  FROM orders o
  LEFT JOIN contacts co
  ON co.global_entity_id = o.global_entity_id
    AND co.created_date = o.created_date
    AND co.order_id = o.global_order_id
LEFT JOIN hc_orders_sessions hc
  ON hc.global_entity_id = o.global_entity_id
    AND hc.created_date = o.created_date
    AND hc.order_id = o.global_order_id
 LEFT JOIN shared_ds_orders s
    ON o.created_date=s.created_date
    AND o.global_entity_id  = s.global_entity_id
    AND o.vendor_code = s.vendor_id
    AND o.global_order_id = s.order_id
WHERE TRUE
  ),

  joined AS (
  SELECT

    o.country_code AS unit,
    --old covariate unit used before oct 6th
    --o.global_entity_id || '-' || o.vendor_code AS covariate_unit,
    --new covariate unit used after oct 6th
    o.country_code || '-' || o.city_id || '-' || FORMAT_DATETIME('%H', DATETIME(o.created_at,timezone)) AS covariate_unit,



    o.country_code || '-' || o.city_id || '-' || FORMAT_DATETIME('%H', DATETIME(o.created_at,timezone)) AS split_unit,


    NULL AS min_date,

    global_order_id,

    o.country_code,
    o.city_id,

    created_date,
    created_at,
    local_created_date,

    is_preorder,
    order_status,

    EPT,
    AAPT AS AAPT_adjusted,
    DT,
    PDT,
    AWT,
    --avtc_v2,
    at_vendor_time_mins,
    at_vendor_time_cleaned_mins,
    stacked_deliveries_rank,
    contact_count,
    hc_session_cnt,
    time_diff_rider_pickup,
    PET,
    --tochange: sKPI commented out - not in scope for this test
    --sKPI,

    -- ps.ept_strategy,
    -- vendor_prep_time_adjustment,
    -- adj_grocery_flow,
    vertical_group,
    vertical_type,
    vendor_name,
    items_count,
    gmv_eur,

    vendor_code,

    CASE
      WHEN vendor_late > 10 THEN "vendor_late"
      ELSE "vendor_not_late"
    END AS vendor_late,
    CASE
      WHEN rider_late > 10 THEN "rider_late"
      ELSE "rider_not_late"
    END AS rider_late,
    CASE
        WHEN (DT - PDT) < -10 THEN "early"
        WHEN (DT - PDT) > 10 THEN "late"
        WHEN (DT - PDT) BETWEEN -10 AND 10 THEN "on-time"
    END AS on_time_sv,
    -- %Late > 15 mins
    CASE
        WHEN (order_status != 'completed' OR is_preorder IS TRUE) THEN NULL
        WHEN (DT - PDT) > 15 THEN 1
        ELSE 0
    END AS late_15,
    -- %Late > 20 mins
    CASE
        WHEN (order_status != 'completed' OR is_preorder IS TRUE) THEN NULL
        WHEN (DT - PDT) > 20 THEN 1
        ELSE 0
    END AS late_20,

  -- PRIORITY METRICS
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'PRIORITY' THEN NULL
      ELSE CAST(DT >= priority_lower_limit AND DT <= priority_upper_limit AS INT64)
    END AS dt_within_prio_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'PRIORITY' THEN NULL
      ELSE CAST(DT < priority_lower_limit AS INT64)
    END AS dt_below_lower_prio_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'PRIORITY' THEN NULL
      ELSE CAST(DT > priority_upper_limit AS INT64)
    END AS dt_greater_upper_prio_pdt,

    -- SAVER METRICS
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'SAVER' THEN NULL
      ELSE CAST(DT >= saver_lower_limit AND DT <= saver_upper_limit AS INT64)
    END AS dt_within_saver_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'SAVER' THEN NULL
      ELSE CAST(DT < saver_lower_limit AS INT64)
    END AS dt_below_lower_saver_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'SAVER' THEN NULL
      ELSE CAST(DT > saver_upper_limit AS INT64)
    END AS dt_greater_upper_saver_pdt,

    -- STANDARD METRICS
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'STANDARD' THEN NULL
      ELSE CAST(DT >= standard_lower_limit AND DT <= standard_upper_limit AS INT64)
    END AS dt_within_standard_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'STANDARD' THEN NULL
      ELSE CAST(DT < standard_lower_limit AS INT64)
    END AS dt_below_lower_standard_pdt,
    CASE
      WHEN (order_status != 'completed' OR is_preorder = TRUE) THEN NULL
      WHEN delivery_fee_option != 'STANDARD' THEN NULL
      ELSE CAST(DT > standard_upper_limit AS INT64)
    END AS dt_greater_upper_standard_pdt

  FROM orders_data o
  WHERE TRUE
 ),


--------------------------------------------------allocation mapping TES Hurrier calls to orders data : using split ID ---------------------------------
--------------------------------------------------remove duplicates: More details https://docs.google.com/document/d/17LW15GrhLTe0aT7GvMYg_4I5lcxpI_Voe1GcRrljLlc/edit?usp=sharing----------------------------------------


vendors AS (
  SELECT
    entity_id
    , vendor_code
    , vertical_type
    , (SELECT timezone FROM UNNEST(vendor) ORDER BY 1 LIMIT 1) AS timezone
  FROM `fulfillment-dwh-production.curated_data_shared_vendor.growth_vendors`
),

tes_hurrier_logs AS (SELECT
DISTINCT
date(datetime(t.created_at, v.timezone)) AS local_created_date,
t.created_date,
datetime(t.created_at, v.timezone) AS local_created_at,
t.created_at,
customer.city_id,
e.vendor.id AS vendor_id,
ffu.allocation_id,
t.country_code || '-' || customer.city_id || '-' || FORMAT_DATETIME('%H', DATETIME(t.created_at, v.timezone)) AS split_unit
FROM `fulfillment-dwh-production.cl.tes_user_sessions` t, UNNEST(feature_flag_usages) ffu
LEFT JOIN UNNEST(estimations) e
-- INNER JOIN
--     `fulfillment-dwh-production.cl.ingress_logs_customer_tribe_http_calls_hurrier` i
--     ON t.x_request_id = i.request_id
--       AND t.created_date = i.created_date
INNER JOIN vendors v ON  T.entity_id=v.entity_id AND e.vendor.id=v.vendor_code
WHERE endpoint IN ('single')
AND customer.session_id IS NULL
AND t.created_date BETWEEN start_date AND end_date
AND ffu.allocation_id LIKE allo
AND customer.city_id is not null and t.country_code is not null and t.created_at is not null and e.vendor.id is not null and t.created_date is not null),

counts AS (
  SELECT
    local_created_date,
    vendor_id,
    split_unit,
    allocation_id,
    COUNT(*) AS allocation_count
  FROM
    tes_hurrier_logs
  GROUP BY
    local_created_date,
    vendor_id,
    split_unit,
    allocation_id
),

ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY local_created_date, vendor_id, split_unit
      ORDER BY allocation_count DESC
    ) AS row_num
  FROM
    counts
),

allocations AS (
SELECT
  local_created_date,
  vendor_id,
  split_unit,
  allocation_id,
  allocation_count
FROM
  ranked
WHERE
  row_num = 1),

  computed_prep_time  AS (
    SELECT
    created_date,
    country_code,
    global_order_id
  FROM `fulfillment-dwh-production.cl._ds_map_orders_to_preptime_code_versions` op
  WHERE created_date BETWEEN start_date-pre_experiment_days AND end_date
  AND preptime_code_version_used_for_vendor != 'null - OPS VALUE USED'
  GROUP BY ALL
  ),


-- count checked at this stage
-- there are 15% of orders globally which could not be mapped to any allocation ID: these have a fixed prep time
-- there are no orders mapped to two model versions
orders_allocation_data AS (
 SELECT DISTINCT e.*, a.allocation_id
  FROM joined e
  LEFT JOIN allocations a
  ON e.split_unit=a.split_unit
  AND e.local_created_date=a.local_created_date
  AND e.vendor_code=a.vendor_id
  INNER JOIN computed_prep_time f
  ON e.unit=f.country_code
  AND e.created_date=f.created_date
  AND e.global_order_id=f.global_order_id
  ),

countries_lookup AS (
  SELECT DISTINCT country_code, region
  FROM `fulfillment-dwh-production.cl.countries`
  WHERE country_code IS NOT NULL
)

, dashboard AS (
SELECT
  oad.vertical_group                                                 AS vertical_category,
  CASE
    WHEN oad.country_code IN ('at','cz','de2','dk','fi','hu','no','se','sk')
         OR cl.region = 'Asia'
         OR oad.country_code IN ('t3','t5')                           THEN 'Pandora'
    WHEN oad.country_code IN ('gr','cy')                              THEN 'Efood'
    WHEN oad.country_code IN ('ae','bh','eg','iq','jo','kw','om','qa') THEN 'Talabat'
    WHEN oad.country_code = 'sa'                                      THEN 'Hungerstation'
    WHEN cl.region = 'Americas'                                       THEN 'Pedidosya'
    WHEN oad.country_code LIKE '%gv-%'                                THEN 'Glovo'
  END                                                                AS platform,
  oad.country_code                                                   AS country,
  oad.vendor_code,
  oad.vendor_name,
  CASE WHEN oad.allocation_id LIKE '%Control%' THEN 'Control' ELSE 'Treatment' END AS arm,
  oad.local_created_date                                             AS order_date,
  EXTRACT(ISOWEEK FROM oad.local_created_date)                       AS week_number,
  FORMAT_DATE('%A', oad.local_created_date)                          AS day_of_week,
  oad.order_status,
  oad.is_preorder,

  -- segment raw values (let Looker Studio bin GMV/items; EPT also pre-bucketed at 1 min)
  oad.EPT                                                            AS ept_min,
  CAST(FLOOR(oad.EPT) AS INT64)                                      AS ept_bucket_1min,
  oad.gmv_eur,
  oad.items_count                                                    AS basket_items,

  -- continuous KPI values (per order)
  oad.AWT,
  oad.EPT,
  oad.AAPT_adjusted,
  ABS(oad.EPT - oad.AAPT_adjusted)                                   AS mae_adjusted,
  oad.DT,
  oad.at_vendor_time_mins                                            AS at_vendor_time,
  oad.at_vendor_time_cleaned_mins                                    AS at_vendor_time_cleaned,
  oad.PET,
  oad.time_diff_rider_pickup,

  -- rate KPI flags + denominators (SUM/COUNT these in Looker Studio)
  IF(oad.order_status='completed',1,0)                              AS is_completed,
  IF(oad.order_status='completed' AND oad.is_preorder=FALSE,1,0)     AS completed_nonpre,
  IF(oad.order_status='completed' AND oad.is_preorder=FALSE AND oad.on_time_sv='on-time',1,0) AS is_on_time,
  IF(oad.order_status='completed' AND oad.is_preorder=FALSE AND oad.on_time_sv='late',1,0)    AS is_late,
  oad.late_15,
  oad.late_20,
  IF(oad.order_status='cancelled',1,0)                              AS is_cancelled,
  IF(oad.contact_count > 0,1,0)                                      AS is_contact,
  IF(oad.stacked_deliveries_rank > 0,1,0)                          AS is_stacked
FROM orders_allocation_data oad
LEFT JOIN countries_lookup cl ON oad.country_code = cl.country_code
WHERE created_date BETWEEN start_date AND end_date
  AND allocation_id IS NOT NULL
)

-- ============================================================================
-- DASHBOARD dataset (order grain). Filterable by platform/country/week/day/vendor;
-- segments via ept_bucket_1min / gmv_eur / basket_items. No table created.
-- ============================================================================
SELECT * FROM dashboard WHERE platform IS NOT NULL;
