# Claude Knowledge Transfer — Harnoor Chahal (CPL / Seamless, Delivery Hero)

> **Purpose.** A portable knowledge base distilled from 47 Claude Code sessions (9 Jun – 9 Jul 2026) plus 13 curated memory files. Paste this into the new Claude co-work account's *project knowledge*, or keep it as a reference doc. It is organized by what matters most: **① data & query knowledge → ② business lingo → ③ business context → ④ preferences / things to remember → ⑤ tooling**.
>
> **Owner:** Harnoor Chahal · harnoor.chahal@deliveryhero.com · Slack `U036E4LSTCP`
> **Domain:** Customer Product & Logistics (CPL) — **Seamless** (prep-time / ETA / delivery-timing) at Delivery Hero.
> **Dates are point-in-time (mid-2026).** Verify field names / behaviors against the live schema before asserting as fact.

---

# ① DATA & QUERY KNOWLEDGE

## 1.1 Where the data lives (core tables)

| Table | What it is | Grain / key |
|---|---|---|
| `fulfillment-dwh-production.cl.orders` | Main orders + timings table. The workhorse. | 1 row/order; `deliveries` is a nested array — join `LEFT JOIN UNNEST(deliveries) d ON is_primary`. ~10.2B rows, partitioned by `created_date`, all timestamps **UTC**, batch-loaded (~5h lag). |
| `fulfillment-dwh-production.cl.tracking_api_logs` | **ETA-history / OTX tracking** — one row per customer-app ETA poll (many rows/order). The "30→38→42 min" ETA the customer sees over time. | key = `country_code` + `order_id` + `created_at`. |
| `fulfillment-dwh-production.dl.tes_tracking_api_request_response_logs` | **Raw** per-request TAPI logs (forensic, single-order timelines). | join to `cl.orders` on `order_id` + `country_code`. |
| `fulfillment-dwh-production.curated_data_shared.orders` | Curated KPI layer (`curated_data_shared_*` datasets: coredata_business, coredata, coredata_tracking). Use for standard KPIs. | Use raw `cl.orders` for timing deep-dives. |
| `fulfillment-dwh-production.cl._vendors_tes_prep_time_config` | Fixed-vs-computed EPT config. `prep_time_config[].strategy ∈ {COMPUTED, OPS_TEMPORARY, OPS_PERMANENT}`. | Fixed EPT = OPS_* = manual overwrites by platform teams. |
| `fulfillment-dwh-production.cl.countries` | `country_code → region` lookup (region ∈ Asia, Americas, MENA, Europe…). | |
| `log-data-science-staging.hirbod.VERTICAL_CATEGORY` | UDF/routine mapping raw `vertical_type` → `darkstores` / `shops` / `main`. | Read body: `bq show --routine --format=prettyjson log-data-science-staging:hirbod.VERTICAL_CATEGORY`. |

**cl.* companion tables:** `_orders_stream` / `_deliveries_stream` (raw Hurrier events, dedupe first), `_live_orders_transitions` / `_live_deliveries_transitions` (realtime status, ~8 days), `_rider_delivery_times`, `acceptance_rate_deliveries`, `audit_logs`. For completed orders, status transitions already sit in `cl.orders` nested `deliveries.transitions[]`. Experiment/curated analysis uses `curated_data_shared_experimentation`.

**⚠️ `cl.orders` has NO experiment / variant / allocation column.** Experiment arm for ETA analysis comes from `cl.tracking_api_logs.eta_format_config_allocation_id`. For cl.orders-based experiments you must join another source (e.g. `cl.tes_user_sessions`).

## 1.2 BigQuery access & ops

- Query with the **`bq` CLI**. Standard: `bq query --use_legacy_sql=false --format=csv --max_rows=<N> < query.sql`. Small comparisons → `--format=prettyjson`; large aggregations → CSV.
- **Billing project:** production `fulfillment-dwh-production` **denies job creation** (read-only). Run jobs with **`--project_id=dhub-data-commune`** (the default). Jobs execute in reservation `dh-gsre-finance:US.datacommune`, which is **frequently saturated** — a job can sit `PENDING` 10+ min waiting for slots (not a failure). Poll: `bq show --format=prettyjson -j <jobid>` → `status.state`. **macOS has no `timeout` command.**
- **Always dry-run to estimate cost:** `bq query --use_legacy_sql=false --dry_run < query.sql`. **Gotcha:** a query using `DECLARE … DEFAULT current_date()` variables makes dry-run report the *whole-table* scan (no partition pruning). Strip DECLAREs / inline literal dates to get the true cost.
- **Never run an expensive query without explicit OK** (see §④). Dry-run, report the estimate, wait.

## 1.3 The base query (`/basequery`)

When the user says **`/basequery`**, this is the reference — pick columns/filters per the question. Source: `cl.orders` + `UNNEST(deliveries) ON is_primary`. All timing metrics are `/60` → minutes.

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
  , ROUND( AVG( IF( is_preorder IS FALSE, o.timings.at_vendor_time_cleaned/60, NULL ) ), 1) as ATVC
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
  and is_preorder is FALSE
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

Default filters: `is_preorder = FALSE`, `order_status = 'completed'`, date-range placeholder (replace). Commented-out extras available if asked: APT (`rider.timings.assumed_actual_preparation_time`), EDT (`estimated_driving_time`), `to_customer_time`, `vendor.country_code` / `region` filters.

**⚠️ CZ `platform_order_id` is NULL from ~2026W19 onward.** At order grain use `o.order_id`, not `platform_order_id`, or recent-week rows collapse into garbage aggregates.

## 1.4 Field & metric definitions (exact SQL)

All `/60` = minutes. On `cl.orders o` + `UNNEST(deliveries) d ON is_primary`.

| Metric | Definition |
|---|---|
| **EPT** — estimated prep time | `o.estimated_prep_time/60` |
| **EPB** — estimated prep buffer | `o.estimated_prep_buffer/60` |
| **AAPT / ATVC** — actual at-vendor prep time (cleaned) | `o.timings.at_vendor_time_cleaned/60` |
| **AWT** — avoidable wait time | `o.timings.avoidable_wait_time/60` |
| **AVT** — at-vendor time (total). AVT − AWT = unavoidable at-vendor | derived |
| **DT** — actual delivery time | `o.timings.actual_delivery_time/60` |
| **PDT** — promised delivery time | `o.timings.promised_delivery_time/60` (also `_lower_bound` / `_upper_bound` timestamps) |
| **OD** — order delay | `o.timings.order_delay/60`. **Verified identity:** `order_delay ≡ actual − promised (median)` (matches within 1 min for 98.6% of orders). |
| **TTP** — time-to-pickup | `Δ(order_created → rider_picked_up)` |
| **To cust. time** | pickup → near-customer. `TIMESTAMP_DIFF(rider_near_customer_at, rider_picked_up_at, MINUTE)`, or field `o.timings.to_customer_time/60`. |
| **rider_late / vendor_late / HBT (hold-back) / est_delay** | `o.timings.<field>/60` |
| **%on-time (±10 min)** | `ABS(actual_delivery_time − promised_delivery_time) ≤ 10 min` ÷ valid completed non-preorder. i.e. `\|order_delay\| ≤ 10`. |
| **%stacked on-time** | same, restricted to `d.stacked_deliveries > 0`. |
| **DT>45** (see §② — renamed from "DT>45 (QC)") | `COUNTIF(actual_delivery_time/60 > 45) / COUNT(completed non-preorder)`, **ALL verticals** (as of 2026-07-06). |
| **%w/ buffer** | % of orders priced by the model (vs fixed): `estimated_prep_buffer > 0`, i.e. `preptime_code_version_used_for_vendor` not OPS/NULL. |
| **Stacking %** | share of primary deliveries with `d.stacked_deliveries >= 1`. `stacked_deliveries` = # ADDITIONAL deliveries batched → 0 = not stacked, 1 = double, 2 = triple. |
| **Rider reaction time** (true notify→accept gap) | `d.timings.rider_reaction_time` (~5.8s avg). **NOT** `rider_accepting_time` / `dispatching_time` (~510s, broader queue measures). |

**PET** (a synthetic prep/est metric in DART) must be **computed per-order then averaged**, NOT from marginal AWT/AVT averages. Decomposition: **PET = X·Δ(created→picked_up) [TTP] + Y·ΔAWT + Z·Δ(AVT−AWT)**.

## 1.5 Platform / brand / vertical mappings

**Brand (platform) from `country_code` + `region`** — canonical CASE used across DART & experiment queries:

```sql
CASE
  WHEN o.country_code IN ('at','cz','de2','dk','fi','hu','no','se','sk') OR o.region IN ('Asia') OR o.country_code IN ('t3','t5') THEN 'Pandora'
  WHEN o.country_code IN ('gr','cy')                                    THEN 'Efood'
  WHEN o.country_code IN ('ae','bh','eg','iq','jo','kw','om','qa')      THEN 'Talabat'
  WHEN o.country_code IN ('sa')                                        THEN 'Hungerstation'
  WHEN o.region IN ('Americas')                                        THEN 'Pedidosya'
  WHEN o.country_code IN ('kr2')                                       THEN 'Woowa'
  WHEN o.country_code LIKE '%gv-%'                                     THEN 'Glovo'
END AS brand
```

Alt explicit `entity.id` grouping seen in decks: **FP APAC** = FP_BD/HK/KH/LA/MM/MY/PH/PK/SG/TH/TW; **PEYA** = PY_*; **Talabat** = TB_BH, HF_EG, TB_IQ/JO/KW/OM/QA/AE; **Hungerstation** = HS_SA; **Foodora/Turkey** = MJM_AT, PO_FI, FO_NO, OP_SE, YS_TR.

Country-code notes: **`t3`/`t5` = Yemeksepeti Turkey** (normalize to `tr`); **`kr2` = Woowa** (exclude for non-Woowa cuts); **Glovo codes carry a `gv-` prefix** (e.g. gv-es, gv-ma, gv-hr).

**Vertical** = `o.vendor.vertical_type` (nested under `vendor`, NOT top-level). Values: `restaurants`, `darkstores`, `courier` / `courier_business`, plus grocery/shops types (supermarket, hypermarket, pharmacies, convenience, beauty, electronics, flowers…) and NULL. Buckets used across analyses:
- **Food** = `restaurants` → routine value `main`
- **Shops / groceries** = vertical not in (restaurants, darkstores, courier, courier_business) and not NULL → routine value `shops`
- **Darkstores** = `darkstores` → routine value `darkstores`

## 1.6 Reusable query recipes

**Verify experiment allocation IDs first (Talabat Jump / any ETA experiment):**
```sql
SELECT eta_format_config_allocation_id AS tag, COUNT(DISTINCT order_id) AS num_orders,
  COUNT(DISTINCT customer_id) AS num_customers, COUNT(*) AS num_log_rows
FROM `fulfillment-dwh-production.cl.tracking_api_logs`
WHERE created_date BETWEEN '2026-06-11' AND CURRENT_DATE() - 1
  AND CONTAINS_SUBSTR(eta_format_config_allocation_id, '2026-06-11_TB_Jump_Station_v2_All_Countries:538')
GROUP BY tag ORDER BY num_orders DESC;
```
Bot filter for tracking logs: `metadata.user_agent NOT LIKE` any of `%Go-http-client%`, `%Ktor%`, `%Vert.x-WebClient%`, `%gfs-order-processing%`, `%PostmanRuntime%`, `%Faraday%`.

**Weekly DT/PDT split, stacked vs non-stacked (per country):**
```sql
SELECT FORMAT_DATE('%GW%V', o.created_date) AS Week,
  ROUND(AVG(IF(d.stacked_deliveries >= 1, o.timings.actual_delivery_time/60,  NULL)), 1) AS DT_stacked,
  ROUND(AVG(IF(d.stacked_deliveries >= 1, o.timings.promised_delivery_time/60, NULL)), 1) AS PDT_stacked,
  ROUND(AVG(IF(d.stacked_deliveries >= 1, NULL, o.timings.actual_delivery_time/60)),  1) AS DT_nonstacked,
  ROUND(AVG(IF(d.stacked_deliveries >= 1, NULL, o.timings.promised_delivery_time/60)), 1) AS PDT_nonstacked
FROM `fulfillment-dwh-production.cl.orders` o
LEFT JOIN UNNEST(deliveries) d ON is_primary
WHERE DATE(o.created_date) BETWEEN '2026-01-01' AND '2026-06-21'
  AND o.country_code = 'bh' AND is_preorder IS FALSE AND order_status = 'completed'
GROUP BY 1 ORDER BY 1
```

**EPT vs AAPT drift (per country/week) — DART Step 2 gate:**
```sql
SELECT o.country_code AS country,
  FORMAT_DATE('%GW%V', COALESCE(DATE(d.rider_dropped_off_at, o.timezone), DATE(d.created_at, o.timezone))) AS report_week,
  COUNT(o.order_id) AS orders,
  ROUND(AVG(o.estimated_prep_time/60), 3) AS avg_EPT,
  ROUND(AVG(o.timings.at_vendor_time_cleaned/60), 3) AS avg_AAPT
FROM `fulfillment-dwh-production.cl.orders` o
LEFT JOIN UNNEST(deliveries) d ON is_primary
WHERE o.created_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 21 DAY) AND CURRENT_DATE()
  AND o.is_preorder IS FALSE
GROUP BY 1,2
```

**AGF / Wait-for-Assembled filter:** `WHERE "wait_for_assembled" IN UNNEST(tags)` (see §②).

**TAPI single-order deep-dive** (`reference_tapi_order_deepdive`) — every tracking snapshot for one order + derived stage + near_dropoff + delivered, from raw `dl.tes_tracking_api_request_response_logs` joined to `cl.orders`:
```sql
WITH rider AS (
  SELECT a.global_order_id AS order_id, a.country_code,
    TIMESTAMP(r.rider_accepted_at) AS rider_accepted_at,
    TIMESTAMP(r.rider_picked_up_at) AS rider_picked_up_at,
    TIMESTAMP(r.rider_near_customer_at) AS near_dropoff_at,
    TIMESTAMP(r.rider_dropped_off_at) AS delivered_at
  FROM `fulfillment-dwh-production.cl.orders` a, UNNEST(deliveries) r
  WHERE a.country_code = 'ae' AND a.created_date >= DATE '2026-06-11'
    AND r.is_primary AND a.global_order_id = '3697794516'
)
SELECT t.date, t.estimates_timestamp, t.order_id, t.country_code,
  t.customer_prediction_median_bound_minutes, t.customer_prediction_lower_bound_minutes, t.customer_prediction_upper_bound_minutes,
  t.model_prediction_median_bound_minutes, t.eta_format_config_variant, t.created_at,
  r.near_dropoff_at, r.delivered_at,
  CASE
    WHEN t.created_at < COALESCE(r.rider_accepted_at, r.rider_picked_up_at, r.near_dropoff_at)
         OR COALESCE(r.rider_accepted_at, r.rider_picked_up_at, r.near_dropoff_at) IS NULL THEN '1.Before Rider Accepted'
    WHEN r.rider_accepted_at IS NOT NULL AND t.created_at >= r.rider_accepted_at
         AND (t.created_at < COALESCE(r.rider_picked_up_at, r.near_dropoff_at, r.delivered_at)
              OR COALESCE(r.rider_picked_up_at, r.near_dropoff_at, r.delivered_at) IS NULL) THEN '2.Between Rider Accepted and Pickup'
    WHEN r.rider_picked_up_at IS NOT NULL AND t.created_at >= r.rider_picked_up_at
         AND (t.created_at < COALESCE(r.near_dropoff_at, r.delivered_at)
              OR COALESCE(r.near_dropoff_at, r.delivered_at) IS NULL) THEN '3.Between Pickup and Near DO'
    WHEN r.near_dropoff_at IS NOT NULL AND t.created_at >= r.near_dropoff_at
         AND (t.created_at < r.delivered_at OR r.delivered_at IS NULL) THEN '4.Near DO'
    WHEN r.delivered_at IS NOT NULL AND t.created_at >= r.delivered_at THEN '5.Post Delivered'
  END AS stage
FROM `fulfillment-dwh-production.dl.tes_tracking_api_request_response_logs` t
LEFT JOIN rider r ON t.order_id = r.order_id AND t.country_code = r.country_code
WHERE t.country_code = 'ae' AND t.created_date >= '2026-06-11' AND t.order_id = '3697794516'
ORDER BY t.created_at;
```
For many orders: replace the single-id filters with `order_id IN (...)` in both the CTE and outer WHERE.

**Extract SQL from a scheduled query** (BigQuery Data Transfer "transfer config" — lives in the project it was created in, not necessarily `dhub-data-commune`):
```bash
bq ls --transfer_config --project_id=PROJECT --transfer_location=us     # find it (loop projects/locations us,eu)
bq show --format=prettyjson --transfer_config <CONFIG_RESOURCE_NAME> \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['params']['query'])"
```
(e.g. `2026-06-10_PT_pelican_shops_global` lived in `logistics-customer-staging`, location `us`.)

## 1.7 Data gotchas & landmines

- **QC = darkstores** (Quick Commerce). **AGF = WFA** (Wait For Assembled). **Woowa = kr2.**
- **Fixed vs computed EPT:** % on fixed EPTs = manual model overwrites by platform teams (`OPS_TEMPORARY`/`OPS_PERMANENT`). Rising fixed-EPT share ⇒ ops intervention, not model drift.
- **CZ `platform_order_id` NULL** from ~2026W19 → use `order_id`.
- **cl.orders has no experiment column** → arm from `cl.tracking_api_logs.eta_format_config_allocation_id`.
- **`cl.orders` freshness** ~5h lag → use `_stream`/`_live_*` tables for current-day.
- **Timezone:** `created_at`/`created_date` are UTC; convert via `DATETIME(created_at, timezone)`; local-day cols suffixed `_local`.
- **`customer_prediction_*` in tracking_api_logs** are ISO-8601 STRINGS with local offset — wrap in `TIMESTAMP(...)` before diffing. The `_minutes` columns = predicted **remaining** time from the snapshot moment (rounded to 5-min steps), not from order creation.
- **ETA-vs-reality durations are right-skewed** → report **both mean and p50** (p50 < mean expected).
- schema reference file: `/Users/harnoor.chahal/Projects/data-platform-product/.claude/skills/data-analyst/schema_reference.md`.

---

# ② BUSINESS LINGO / GLOSSARY

| Term | Meaning |
|---|---|
| **Seamless** | The CPL domain covering prep-time, ETA/promise, and delivery-timing experience. Harnoor's area. |
| **PET** | Prep/est-time composite (per-order then averaged; decomposes into TTP + AWT + (AVT−AWT)). A DART primary KPI. |
| **EPT** | Estimated Prep Time (model's prediction of vendor prep). |
| **EPB** | Estimated Prep Buffer. `%w/ buffer` = share priced by the model. |
| **AAPT / ATVC / AVT** | Actual at-vendor prep time (`at_vendor_time_cleaned`). |
| **AWT** | Avoidable Wait Time (rider waiting at vendor that could be avoided). |
| **TTP** | Time-To-Pickup (order created → rider picked up). |
| **TTFIR / FIR / FIA** | "Food is ready" event (vendor fires it). `food_is_ready_at`. |
| **DT** | Delivery Time (actual, order → delivered). |
| **PDT** | Promised Delivery Time (the promise shown; has median + lower/upper bounds). |
| **OD** | Order Delay = actual − promised (median). Late = OD>10, early = OD<−10, on-time = \|OD\|≤10. |
| **DT>45** | Share of orders delivered in >45 min. Renamed 2026-07-06 from **"DT>45 (QC)"**; now **ALL verticals** (was darkstores-only). 45 min was the Quick-Commerce promise ceiling; unified to a blunt all-orders delivery-speed tail. Read **WoW change, not absolute level** (restaurant-heavy markets sit structurally higher). |
| **QC** | Quick Commerce = **darkstores** vertical. |
| **AGF / WFA** | Adjusted Grocery Flow = **Wait For Assembled**. Hurrier sends order to vendor immediately but delays rider assignment until the vendor fires `food_is_ready` (FIA). Identify: `"wait_for_assembled" IN UNNEST(tags)`. |
| **Stacking** | Batching multiple deliveries on one rider trip. `stacked_deliveries` counts ADDITIONAL deliveries (0=none, 1=double, 2=triple). ~20% of global orders; a profitability lever. |
| **CPU** | **Committed Pick-Up time** (NOT cost-per-unit). **Δ CPU** = gap between two orders' committed pickup times; dispatch stacks two orders only when **Δ CPU ≤ ~4 min** (Max Δ CPU threshold). A DTM sub-model feature; in simulation it mainly cuts the stacked-order late tail. |
| **DTM** | Delivery-Time Model / dispatch model (the simulation environment "Don and Shamal" own). |
| **jump_rate / jump_magnitude** | ETA "jump" = customer's shown arrival time moves later during the order (ETA worsens). `jump_vs_prev_min > 0` via `LAG` over `customer_prediction_median_bound_timestamp`. |
| **Quantile** | The prep-time model's output quantile (config in `operational_config.yaml`, `logistics-preptimes` repo). Switchback tests change it (see §③). |
| **VERTICAL_CATEGORY** | BQ routine mapping vertical_type → darkstores / shops / main. |
| **CCR / HCSR / seamless_fail_rate** | Experiment KPIs (cancellation / hard-cancel-and-support / seamless failure). |
| **MBR / QU / Cycle Review / Domain Update** | Monthly Business Review; Quarterly Update (Apr/Jul/Oct/Jan); the recurring Seamless meetings/decks (see §③). |
| **"Mio"** | The user writes millions as **"Mio"**, not "m". |

---

# ③ BUSINESS CONTEXT (projects, experiments, workflows)

## DART — `/run-seamless-analysis` (the flagship workflow)
Weekly Seamless anomaly-detection report. Spec: `/Users/harnoor.chahal/ai/Command files/DART-v1.md`. Reports saved to `/Users/harnoor.chahal/ai/seamless-reports/report-<ISO_WEEK>.md`; logs in `seamless-reports/logs/`.

- **Primary KPIs (Table 1):** PET, %on-time, %stacked on-time, DT>45. **Diagnostic KPIs (Table 2):** TTP, AWT, DT, %stacked, Rider late%, To cust. time, %w/ buffer.
- **Significance thresholds:** PET 0.3, %on-time 1.0pp, %stacked 1.5pp, DT>45 1.0pp. Column pruned if all selected markets |WoW| ≤ 0.3.
- **Determinism** lives outside the model: fixed SQL windows, numeric thresholds, priority formula. **WoW = round each week to 2dp THEN subtract.** Selection ≤4 markets/platform, ~7 total, deteriorations first. `priority = severity × volume_weight × platform_factor`; `platform_factor = 1 + 0.5·(deteriorating_eligible/eligible)`; "flagged-eligible" = markets that fired a flag (NOT the 100k volume cutoff, which only governs ranking).
- **Execution sequence:** Step 0 idempotency (**now BYPASSED — always re-run from live BQ and overwrite**; a cached/substituted report once got re-served forever, the "MBR-suspect" incident) → Query 1 (aggregate primary+diagnostic, brand×country×week, **35-DAY / 4-week window** so Path B trend has history; ~56 GB / ~$0.28) → Python determinism engine → conditional **Query 3** (EPT breakdown, **only if a flagged market's EPT WoW > +1 min**) → optional Query 2 (PDT) → **Step 2b external context** (holidays via officeholidays.com WebFetch — WebSearch is org-blocked; weather/news; *validity over completeness* — cite only if it credibly explains a move) → render → save → deliver.
- **Delivery:** verbatim to 3 Slack DMs — Harnoor `U036E4LSTCP`, **Daniel Rüdiger `U4QNW0MJ7`**, **Nicolò Luti `U0710JS2BPZ`**. Personal copy to self may omit the Platform Health section.
- **Scheduler:** `/Users/harnoor.chahal/ai/scripts/run-seamless-analysis.sh` via launchd `com.harnoor.seamless-analysis.plist`, every 2h Mon 10:00 → Wed 22:00. Dense schedule is a **sleep workaround** (launchd doesn't wake the Mac; on wake it runs ONE coalesced catch-up). Dedup is **provenance-based**: marker `seamless-reports/.state/done-<WEEK>.ok` written only after a live-SQL run + successful sends. *Do not replace with an existence check on the report file — that skip IS the sleep deduplicator.*
- **Freshness artifacts to NOT misattribute:** (1) Americas timezone settling on the newest week; (2) `%w/ buffer` uniform ~15pp drop in newest week = `_ds_map_orders_to_preptime_code_versions` not yet backfilled.
- **Root-cause routing:** model deviation (PDT tightened, DT flat) → `#log-sds-int`; PDT range test → read `#log-tes-int`; rider/courier → `dh-customer-ops-<platform>`; vendor/demand → brand ops; expansion → propose only. PET reference slides: https://docs.google.com/presentation/d/1SBhXR8CiV8qHb6IRWfZeJy-8aKRhd5q9t7hylU16c4M/edit
- **Cost:** ~13M tokens / ~$50 per full weekly run (overwhelmingly cache-read of the big spec); ~$200/month.

**DART-v2** — DART-v1 turned into a config-driven, shareable Claude Code skill. Lives at `/Users/harnoor.chahal/ai/dart/`; pushed to **https://github.com/deliveryhero/dart-seamless** (internal, default branch `main`). Files: `SKILL.md` (setup wizard), `engine.md` (v1 brain generalized), `config.example.yaml`, `README.md`/`DART-v2.md`. Three configurable axes: KPIs (config keys `pet`, `on_time`, `on_time_stacked`, `dt45`), Frequency (daily/weekly/monthly), Audience (Slack DMs + channels, no email). Confluence: https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/1729070069

## Talabat Jump Station v2 — Experiment 538
`2026-06-11_TB_Jump_Station_v2_All_Countries:538`, started 2026-06-11 13:59:22 UTC, 8 MENA countries (ae, bh, eg, iq, jo, kw, om, qa), 3 arms Control/T1/T2, ~33/33/33 split. Source: `cl.tracking_api_logs`. **Finding: Treatment1 is the clear winner** — global jump_rate ≈ −9pp (70.9%→62%), cuts jumps in every country (−5 to −11pp); **T2 ≈ Control**. Neutral on seamless_fail / CCR / HCSR / orders-per-customer. **GOTCHA:** all arms key off `eta_format_config_allocation_id` prefix `logistics-otx:tapi-config-variant:...:538:<arm>`; the example query wrongly used `tapi-split-by-customer-id:...:Control`, which silently drops Control (0 rows / 100% treatment). Always verify allocation IDs first. Sub-analysis: treatments show **sub-5-min ETAs far too early** (Stage 2/3), ~87% premature vs Control 56%. Query saved: `/Users/harnoor.chahal/ai/jump_station_3arm.sql`. **Dashboard:** `talabat_jump_build.py` → self-contained `talabat_jump_dashboard.html` (Chart.js, offline), hosted at `https://storage.cloud.google.com/dh-cpl-seamless-dashboards/talabat_jump_dashboard.html`; auto-refresh daily 09:00 Berlin via launchd `com.dh.talabat-jump-refresh`. Talabat contact: Malak Bedier (malak.bedier@talabat.com).

## Pelican shops — Experiment `2026-06-10_PT_pelican_shops_global`
PT = experiment prefix; 14-day pre-window; randomized by `split_unit` = country-city-hour; allowlist `%2026-06-10_PT_pelican_shops_global%`. Config lived in `logistics-customer-staging`. Key learning: **scan cost (~1.1 TB, ~$7) is fixed by source reads** (`cl.orders`, `cl._deliveries`, `cl.tes_user_sessions` for allocation→arm) — aggregating output saves nothing. Artifacts under `/Users/harnoor.chahal/ai/`: `pelican_stats_ready.sql`, `pelican_dashboard.sql`, `pelican_significance.py` (cluster-aware Welch t-test, no numpy/scipy).

## AR darkstores EPT-inflation tests
**P1 (Apr 30 – May 3)** and **P2 (May 10 – May 13)** were **deliberate EPT-inflation tests**, NOT model regressions. **P3 (May 18 – May 24) = no-testing baseline** (~29 min DT). Three adverse effects the user emphasizes when anyone proposes "run tests longer to let the model learn": (1) more %late (PDT doesn't adjust to inflated EPT); (2) artificially inflated DT (P1 cohort 59 min, P2 46 min vs ~29 baseline); (3) inflated TTP + AWT gains are illusory (over-estimated pickup) and **raising EPT makes vendors slow down prep** (self-fulfilling). Always add the cross-period bias caveat (day-of-week, weather, demand, vendor drift). Fixed EPT is <0.4% of AR orders (the COMPUTED model is what's tested).

## Country-ranking dashboard + PDT hackathon
- **Country-ranking dashboard** `/Users/harnoor.chahal/ai/country-ranking-dashboard/`: offline HTML + Chart.js ranking all 66 DH countries by weighted rank-sum over toggleable KPI signals (direction + weight editable live). `build_dashboard.py`, `kpi_catalog.json` (declarative signals), one combined single-scan `cl.orders` SQL, `MIN_THRESHOLD` 10,000 orders. Used to pick a stacking/dispatch testbed (5-criteria weighted rank-sum; winner **Georgia (gv-ge)**; alternates Kazakhstan, Croatia).
- **Hackathon "The next PDT model feature is…"**, team **"PDTs are cool"** (`#team-pdts-are-cool`, `C0BCHN98DPG`): Harnoor (analysis/presentation), Zhamal Toktamysova & Dongin Kim ("Don and Shamal" — DTM model owners), Asher Nehemiah (Talabat), Grigoris Xenikakis (e-food). Tested **Δ CPU** and **rider-acceptance** features on `cpl-hackathon` branch (Metaflow, 1-month window). **Δ CPU cut the stacked late tail** (up to +5pp on-time gv-hr); rider-acceptance showed no lift → dropped. BOE GMV uplift ≈ **€5–16 Mio/yr, central ~€14 Mio** (each 1% relative cut in CX cancellations ≈ €2.74 Mio/yr). Site: `/Users/harnoor.chahal/ai/hackathon-pdts-are-cool/index.html`.

## Recurring workflows (meetings & reporting)
- **Cycle Review** (monthly, 3rd Thursday): spec `/Users/harnoor.chahal/ai/Command files/Cycle Review/`. Steps: find meeting+recording → stakeholder email → fix title slide → stage next month's slides → Slack reminder → calendar reminder → validate next invite. Email subject `CPL | Seamless domain Cycle Review CW<NN> (<Month>) - <Year>`, To `log-customer-seamless-stakeholders@deliveryhero.com`, Cc `log-cpl-seamless-domain@deliveryhero.com`; **must be approved before sending**. **QU months (Apr/Jul/Oct/Jan):** skip staging/Slack/calendar steps. Deck `1gMZl8BDLSU8D7BXrykJT7qp1TbdcFFn8kLW9mTVLxfI`; Quarterly Roadmap sheet `1OwXaCizo32kCixGa9Nb6KHq20OkvGRAQ69QndwMrwO8`; Templates sheet `1Q88oJ_WPNLaHnC5cmOVQ7Zf-DJz4xXo9VRO7oJq1GRc`.
- **Seamless Domain Update** (bi-weekly, `seamless-domain-update` skill): leads = Daniel Rüdiger, Brad Moore, Niccolò Luti, Harnoor, Florian Marienfeld, Gayatri Kanala. Confluence Live doc cloned from previous CW page (clear the "3/4 things" list), topic message to `#log-seamless-domain-leads`. Parent LOGCPL page 36656082. Page ledger: CW14 1443463559, CW16 1500905705, CW18 1503297591, CW20 1631028099, CW22 1674281011, CW24 1687617662.
- **Biweekly Update** (`/biweekly-update` skill): ISO week N; N odd → KPI page, N even → Initiatives page. Carry forward from previous same-type page in space **LOGCPL** (cloudId `deliveryhero.atlassian.net`), replace `W{PREV}`. Slack notify **#cpl-ops-perf-seamless** (`C051L8NRY69`). (Initiatives cadence paused after W20.)
- **EPT quantile switchback tests** (process from **Ege Sözgen**, Product Ops, in `#cpl-sds-int` `C08P93C21FE`): current quantile in Superset dashboard 480 + Git `operational_config.yaml` in `deliveryhero/logistics-preptimes` (branch master/model-b). Change = edit YAML via PR (`gh repo clone deliveryhero/logistics-preptimes`). While Ege OOO route through: Hirbod Kamalinia (`U023ZA36ATT`, PR merge+training), Alper Duranel (`U08QHH5Q8V8`, deploy), Sudhanshu Nautiyal (`UJHSR4E8H`, model/test), Kaushik P Gaikwad (`U03N17AB220`, Airflow DAG), Alina Kim (`U09D065SRT6`, design/query).
- **OKR (Okra MCP):** active quarter **Q2 2026** (no Q3 open at last check); Harnoor owns **one** KR ("Increase increme…"). Verify against Okra tools before editing "Q3 OKR invites". Rose-sync drift alerts post to `#log-seamless-3-leads`.

## People & channels (quick reference)
- **Daniel Rüdiger** `U4QNW0MJ7`, **Nicolò/Niccolò Luti** `U0710JS2BPZ` — DART recipients / CPL leads. **Brad Moore, Florian Marienfeld, Gayatri Kanala** — Seamless domain leads.
- **Uri Alarcon** — Group PM; got the BigQuery onboarding pack (Canvas `F0BD9DQLS5B`; doc `/Users/harnoor.chahal/ai/Command files/BigQuery-Analysis-Onboarding-for-Uri.md`); DM `D046RP964S1`.
- **Ege Sözgen** — Product Ops, EPT quantile owner. **Hirbod Kamalinia / Alper Duranel / Sudhanshu Nautiyal / Kaushik Gaikwad / Alina Kim** — SDS/preptimes team.
- **Dongin Kim + Zhamal Toktamysova** — DTM model owners. **Malak Bedier** — Talabat (jump dashboard).
- **Channels:** `#cpl-sds-int` (C08P93C21FE, private, SDS), `#cpl-ops-perf-seamless` (C051L8NRY69), `#log-seamless-domain-leads`, `#log-seamless-3-leads`, `#team-pdts-are-cool` (C0BCHN98DPG), `#log-otx-talabat` (C065LJ7TDFF, private), `#log-sds-int`, `#log-tes-int`. `@Claude` bot user = `U09RNP2RWUF`.

---

# ④ PREFERENCES / THINGS TO REMEMBER

- **Folder rule:** create new folders/files ONLY inside `/Users/harnoor.chahal/ai/`. Never directly under the home dir. If a task needs a folder elsewhere, ask.
- **Never run expensive BigQuery queries without explicit OK.** Always dry-run, report the estimate, wait. The user interrupts costly runs.
- **"Just the query" = output the full SQL verbatim, no preamble.**
- **Honesty over fabrication.** Never invent data, a Slack send, a weather tie, or a label. Use clearly-labeled placeholders (amber "Add…" / "Illustrative") when numbers are missing. Flag sign-convention ambiguities and data caveats explicitly. Verify schema before generating.
- **Slack table format (default):** period-over-period comparison style — context line (flag emoji + period labels + sample size), tables with **Δ column** (status/bucket tables) or **Δ row** (percentile tables), emoji on status deltas (🔴 bad / 🟢 good / ⚪ neutral), real `−` (U+2212), **bold the 2–3 standout cells**, units in the title not the cells, header taglines ("compressed sharply at the top"). Established after the CZ W1-vs-W19 message; apply to all Slack comparison tables.
- **Write millions as "Mio"** (not "m").
- **Report both mean and p50** for ETA-vs-reality durations (right-skewed).
- **Presentation / MBR format** (from the "Choice" team model): standardized verdicts 🟢 On-track / 🟡 At risk / 🔴 Off-track; Trend as Q4/Q1/Q2 **columns not arrows**; `–` where no target; table (platforms + global + status) on the LEFT, Highlights/Lowlights/Crux on the RIGHT — keep numbers in the table, analysis in text; Crux as plain-language bullets; **avoid "faffy" words** ("the accelerating miss", "structural OKR gap"). Pale yellow status = on-track (not red).
- **Confluence edits:** prefer reversible — publish with a clear version message and explain how to revert via Page History (the API can't save a true unpublished draft on an already-published page).
- **Style:** concise, scannable ("at a glance" / "one-minute version"), collapsible detail for secondary info. Stays engaged and corrects the moment output drifts or fabricates.

---

# ⑤ TOOLING & ENVIRONMENT

- **BigQuery:** `bq` CLI, billing project `dhub-data-commune` (§1.2).
- **Google Workspace:** `gws` CLI (skill at `~/.claude/skills/google-workspace`). Read sheet: `gws sheets +read --spreadsheet <id> --range "<tab>" --format table`. Upload CSV as native Sheet: `gws drive files create --upload file.csv --upload-content-type text/csv --json '{"name":"...","mimeType":"application/vnd.google-apps.spreadsheet"}'` (upload from cwd, not /tmp). Read slides: `gws slides presentations get`. Filter `keyring` noise with `grep -v keyring`. **Auth refresh** when it fails:
  ```bash
  export GCLOUD_SDK_ROOT=$(gcloud info --format="value(installation.sdk_root)")
  export PYTHONPATH="$GCLOUD_SDK_ROOT/lib/third_party:$GCLOUD_SDK_ROOT/lib"
  export GOOGLE_WORKSPACE_CLI_TOKEN=$(python3 -c "import google.auth; from google.auth.transport.requests import Request; creds,_=google.auth.default(scopes=['https://www.googleapis.com/auth/spreadsheets']); creds.refresh(Request()); print(creds.token)")
  ```
  Full Gmail+Calendar scope needs `gcloud auth application-default login --scopes=openid,userinfo.email,cloud-platform,drive,spreadsheets,documents,presentations,calendar,gmail.compose,gmail.send,gmail.readonly`.
- **MCP servers:** **Okra** (OKR data) — `claude mcp add --scope user --transport http okra https://okra.deliveryhero.io/api/mcp --header "CF-Access-Client-Id: …" --header "CF-Access-Client-Secret: …" --header "Authorization: Bearer okra_…"` (use `--scope user`, restart session — MCP loads at startup). **Slack**: two integrations — `slack-message-fetcher` (read-only, headless, xoxc/xoxd token) and `plugin_slack_slack` (OAuth, send-capable, **interactive sessions only** — headless `claude --print` has no Slack send tool).
- **LiteLLM budget:** `dp-devinfra litellm request-budget-increase --amount 100 --days 30`; `/budget` skill; cap $200 → over-budget = `400 ExceededBudget`. Gateway at localhost:36253.
- **Dashboards / hosting:** self-contained HTML + Chart.js pattern (`bq query --format=json` → data inlined → offline file). GCS bucket `gs://dh-cpl-seamless-dashboards` (project `logistics-data-storage-staging`) has **Domain Restricted Sharing** — grant `user:<email>` individually (blanket `domain:` grants are silently stripped); browser URL is the `storage.cloud.google.com/...` form. Quick public share: `python3 -m http.server 8000` + `ngrok http 8000` (free tier = one tunnel; get URL from `curl -s http://localhost:4040/api/tunnels`).
- **Skills:** `data-analyst` / `coredata-analytics` (BQ), `dataviz` (read before any chart), `slides-from-data` (deliveryhero/ai PR #156; HTML preview → editable PPTX via `html2pptx.cjs`, needs Playwright Chromium), `google-workspace`, `biweekly-update`, `seamless-domain-update`, `Cycle Review`. `gh` authed as `HarnoorCh`; DH org default branch `main`.
- **Local env:** macOS, Europe/Berlin, Python 3.9.6 (no streamlit/pandas assumed), no `timeout` command. Convert HEIC: `sips -s format png IMG.HEIC --out out.png` (tile large images before Read).

---

*Generated 2026-07-09 from local Claude Code transcripts + curated memory. The companion `memory/` folder holds the same knowledge as individual file-per-fact memories for dropping into a Claude Code memory directory.*
