---
name: reference-basequery
description: "User's base SQL query for orders/timings analysis on fulfillment-dwh-production.cl.orders. Triggered by /basequery shorthand."
metadata: 
  node_type: memory
  type: reference
  originSessionId: d64dad5e-3efa-40de-937c-601b59dc8b80
---

When the user writes `/basequery`, refer to this base query as the reference and pick/choose columns and filters as needed for the question.

**Source table:** `fulfillment-dwh-production.cl.orders` (with `unnest(deliveries)` joined on `is_primary`)

**Base query:**

```sql
with data as (
SELECT
  region
  , platform_order_id as order_id
  , o.country_code AS country
  , o.created_at as created_at
  , FORMAT_DATE('%GW%V', o.created_date) AS week
  , EXTRACT(HOUR FROM o.created_at) as hour
  , EXTRACT(DAYOFWEEK FROM o.created_at) as day
  , d.stacked_deliveries as stacks
  , ROUND( AVG( IF( is_preorder IS FALSE, estimated_prep_time/60, NULL ) ), 1) as EPT
  , ROUND( AVG( IF( is_preorder IS FALSE, estimated_prep_buffer/60, NULL ) ), 1) as EPB
  --, ROUND( AVG( IF( is_preorder IS FALSE, rider.timings.assumed_actual_preparation_time/60, NULL ) ), 1) as APT
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.at_vendor_time_cleaned/60, NULL ) ), 1) as ATVC
  --, ROUND( AVG( IF( is_preorder IS FALSE, rider.timings.estimated_driving_time/60, NULL ) ), 1) as EDT
  --, ROUND( AVG( IF( is_preorder IS FALSE, rider.timings.to_customer_time/60, NULL ) ), 1) as to_customer
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.actual_delivery_time/60, NULL ) ), 1) as DT
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.promised_delivery_time/60, NULL ) ), 1) as PDT
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.order_delay/60, NULL ) ), 1) as OD
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.estimated_courier_delay/60, NULL ) ), 1) as est_delay
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.vendor_late/60, NULL ) ), 1) AS vendor_late
  , ROUND( AVG( IF( order_status = 'completed' AND is_preorder IS FALSE, o.timings.hold_back_time/60, NULL ) ), 1) AS HBT
  , ROUND( AVG( IF( order_status = 'completed' AND is_preorder IS FALSE, o.timings.rider_late/60, NULL ) ), 1) AS rider_late
  , ROUND( AVG( IF( order_status = 'completed' AND is_preorder IS FALSE, o.timings.customer_walk_in_time/60, NULL ) ), 1) AS customer_walk_in_time
  , ROUND( AVG( IF( order_status = 'completed' AND is_preorder IS FALSE, o.timings.customer_walk_out_time/60, NULL ) ), 1) AS customer_walk_out_time
  , ROUND( AVG( IF( order_status = 'completed' AND is_preorder IS FALSE, o.timings.at_customer_time/60, NULL ) ), 1) AS at_customer_time
FROM `fulfillment-dwh-production.cl.orders` o
left join unnest(deliveries) d on is_primary
WHERE date(o.created_date) BETWEEN '2023-11-20' AND '2023-11-21'
  --and vendor.country_code = 'ph'
  and is_preorder is FALSE
  --and region = 'Asia'
  and order_status = 'completed'
group by 1,2,3,4,5,6,7,8
)
SELECT
  region, order_id, created_at, week, hour, day
  , EPT, EPB, ATVC, rider_late, HBT, vendor_late
  , DT, PDT, OD, est_delay
  , customer_walk_in_time, customer_walk_out_time, at_customer_time
  , (PDT - DT) as pdt_error
  , case when (DT >= 45) then "DT>=45" when (DT < 45) then "DT<45" else "other" end as DT_type
  , case when (vendor_late > 10) then "VL>10" else "vendor not late" end as VL_type
  , case when (rider_late > 10) then "rider_late>10" else "rider not late" end as rider_late_type
  , case when (OD > 10) then "order_late" when (OD < -10) then "order_early" else "on_time" end as order_type
  , case when (stacks >= 1) then "stacked" else "non-stacked" end as stacks_final
  , case when (EPT > DT) then "EPT>DT" else "EPT<DT" end as ept_dt_type
from data
```

**Key columns / metrics (all in minutes after `/60`):**
- `EPT` — estimated prep time
- `EPB` — estimated prep buffer
- `ATVC` — at-vendor time (cleaned)
- `DT` — actual delivery time
- `PDT` — promised delivery time
- `OD` — order delay
- `est_delay` — estimated courier delay
- `vendor_late`, `rider_late`, `HBT` (hold back time)
- `customer_walk_in_time`, `customer_walk_out_time`, `at_customer_time`
- `pdt_error` = PDT − DT
- `stacks` = `d.stacked_deliveries`

**Bucket / type columns:** `DT_type`, `VL_type`, `rider_late_type`, `order_type`, `stacks_final`, `ept_dt_type` — see CASE definitions above.

**Commented-out (available if asked):** APT, EDT, to_customer, drive_time_error, rider.* fields, `vendor.country_code`, `region` filters.

**Default filters in base:** `is_preorder = FALSE`, `order_status = 'completed'`, date range placeholder (replace per question).

**⚠️ Known issue:** `platform_order_id` is NULL for all CZ orders from ~2026W19 onward (confirmed 2026-05-27). When grouping at order grain, use `o.order_id` instead of `platform_order_id`, or all recent-week rows will collapse to a handful of groups (one per stacks value) and produce garbage aggregates.

When applying: adjust the date range, country/region filters, and metric selection per the user's specific question. Related: [[project-dt-analysis]].
