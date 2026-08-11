---
name: reference_tracking_api_logs
description: "cl.tracking_api_logs = per-ping ETA history table (the ETA shown to customer over an order's lifetime); fields, timezone, and ETA-jump usage"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0cc6f9a2-04dd-4122-8fe3-3f0aa291c1b4
---

`fulfillment-dwh-production.cl.tracking_api_logs` is the **ETA-history / OTX tracking-session** table — one row per customer-app ETA poll, so **many rows per order** over its lifetime (vs `cl.orders.timings.promised_delivery_time`, which is one final value). Verified against live schema June 2026.

**Unique key:** `country_code` + `order_id` + `created_at`.

**Key fields:**
- `created_at` (TIMESTAMP, **UTC**), `created_date` (DATE, **UTC**, partition col — always filter on it).
- `order_id`, `country_code` — join back to `cl.orders` on `(country_code, order_id)`.
- `customer_prediction_median_bound_timestamp` / `_lower_` / `_upper_` — **the ETA actually shown to the customer** (median + range). Stored as **ISO-8601 STRINGS with local offset**, e.g. `2026-06-25T10:40:08.065-03:00`; wrap in `TIMESTAMP(...)` to compute diffs.
- `model_prediction_{median,lower,upper}_bound_timestamp` — raw Tracking Time Model (OTX DS) prediction before display formatting.
- `promised_delivery_at` (+ `_lower_bound`/`_upper_bound`, `_rounded`), `preparation_time` (min, TES), `delivery_time_status` (`ON_TIME`/`SLIGHT_DELAY`/`DELAY`).
- ETA A/B: `eta_format_config_allocation_id`, `eta_format_config_variant`, `eta_format_config_name` — this is the table for ETA-format experiment allocation (cl.orders has NO experiment column). See [[project_talabat_jump_experiment]].
- `metadata` STRUCT (perseus ids, global_entity_id, user_agent, originating_page…).

**ETA-jump usage:** order ETA timeline + jump via `LAG(TIMESTAMP(customer_prediction_median_bound_timestamp)) OVER (ORDER BY created_at)`; `jump_vs_prev_min > 0` = promised arrival moved later (ETA worsened). Source behind Talabat Jump `jump_rate`/`jump_magnitude`.

**Other useful cl.* tables (delivery timing / events):** `_orders_stream`, `_deliveries_stream` (raw Hurrier events, dedupe before use), `_live_orders_transitions` / `_live_deliveries_transitions` (realtime status transitions, last ~8 days), `_rider_delivery_times`, `acceptance_rate_deliveries`, `audit_logs` (Hurrier/Rooster/Porygon/TES/DPS). Note: for completed orders, status transitions are already in `cl.orders` nested `deliveries.transitions[]`.

**cl.orders freshness:** batch, not real-time — observed ~5h lag (June 2026); use stream/live tables for current-day. **Timezone:** `created_at`/`created_date` are UTC; convert with `DATETIME(created_at, timezone)`; local-day cols suffixed `_local` (e.g. `delivery_date_local`).

Related: [[reference-basequery]], [[reference-adjusted-grocery-flow]], [[project_talabat_jump_experiment]].
