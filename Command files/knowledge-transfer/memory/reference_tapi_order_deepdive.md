---
name: reference-tapi-order-deepdive
description: "TAPI order deep-dive — pull every tracking-API snapshot for ONE order with stage + near_dropoff + delivered timestamps; reuse when user says \"TAPI order deepdive\""
metadata: 
  node_type: memory
  type: reference
  originSessionId: 17c4d0ae-2870-437a-a74f-5e6088cbc370
---

Single-order tracking-API deep dive. Returns every TAPI snapshot (one row per request, chronological) for one order, joined to `cl.orders` for the rider milestones, with derived `stage`, `near_dropoff_at` (= rider_near_customer_at), and `delivered_at` (= rider_dropped_off_at). Change the `order_id` (and country/date). Source table is the RAW logs `fulfillment-dwh-production.dl.tes_tracking_api_request_response_logs` (not the curated `cl.tracking_api_logs` used by the aggregate analysis). Stage logic matches the aggregate analysis (see [[reference_basequery]] / jump-station work [[project_talabat_jump_experiment]]).

```sql
WITH rider AS (
  SELECT
    a.global_order_id AS order_id,
    a.country_code,
    TIMESTAMP(r.rider_accepted_at)      AS rider_accepted_at,
    TIMESTAMP(r.rider_picked_up_at)     AS rider_picked_up_at,
    TIMESTAMP(r.rider_near_customer_at) AS near_dropoff_at,
    TIMESTAMP(r.rider_dropped_off_at)   AS delivered_at
  FROM `fulfillment-dwh-production.cl.orders` a, UNNEST(deliveries) r
  WHERE a.country_code = 'ae'
    AND a.created_date >= DATE '2026-06-11'
    AND r.is_primary
    AND a.global_order_id = '3697794516'
)
SELECT
  t.date, t.estimates_timestamp, t.order_id, t.vendor_name, t.country_code,
  t.promised_delivery_at, t.promised_delivery_at_lower_bound, t.promised_delivery_at_upper_bound,
  t.promised_delivery_at_lower_bound_rounded, t.promised_delivery_at_upper_bound_rounded,
  t.promised_delivery_time_lower_bound, t.promised_delivery_time_upper_bound,
  t.committed_pickup_at, t.requested_pickup_at, t.preparation_time,
  t.model_prediction_lower_bound_minutes, t.model_prediction_median_bound_minutes, t.model_prediction_upper_bound_minutes,
  t.customer_prediction_median_bound_minutes, t.customer_prediction_upper_bound_minutes, t.customer_prediction_lower_bound_minutes,
  t.delivery_time_status, t.eta_format_config_variant, t.eta_format_config_name,
  t.model_prediction_dispatch_remaining_time, t.created_at, t.pdt_within_bounds,
  r.near_dropoff_at,
  r.delivered_at,
  CASE
    WHEN t.created_at < COALESCE(r.rider_accepted_at, r.rider_picked_up_at, r.near_dropoff_at)
         OR COALESCE(r.rider_accepted_at, r.rider_picked_up_at, r.near_dropoff_at) IS NULL
      THEN '1.Before Rider Accepted'
    WHEN r.rider_accepted_at IS NOT NULL AND t.created_at >= r.rider_accepted_at
         AND (t.created_at < COALESCE(r.rider_picked_up_at, r.near_dropoff_at, r.delivered_at)
              OR COALESCE(r.rider_picked_up_at, r.near_dropoff_at, r.delivered_at) IS NULL)
      THEN '2.Between Rider Accepted and Pickup'
    WHEN r.rider_picked_up_at IS NOT NULL AND t.created_at >= r.rider_picked_up_at
         AND (t.created_at < COALESCE(r.near_dropoff_at, r.delivered_at)
              OR COALESCE(r.near_dropoff_at, r.delivered_at) IS NULL)
      THEN '3.Between Pickup and Near DO'
    WHEN r.near_dropoff_at IS NOT NULL AND t.created_at >= r.near_dropoff_at
         AND (t.created_at < r.delivered_at OR r.delivered_at IS NULL)
      THEN '4.Near DO'
    WHEN r.delivered_at IS NOT NULL AND t.created_at >= r.delivered_at
      THEN '5.Post Delivered'
  END AS stage
FROM `fulfillment-dwh-production.dl.tes_tracking_api_request_response_logs` t
LEFT JOIN rider r
  ON t.order_id = r.order_id AND t.country_code = r.country_code
WHERE t.country_code = 'ae'
  AND t.created_date >= '2026-06-11'
  AND t.order_id = '3697794516'
ORDER BY t.created_at;
```

For multiple orders: drop the single-id filters and use `order_id IN (...)` in both the `rider` CTE and the outer `WHERE` (join is keyed on order_id+country_code).
