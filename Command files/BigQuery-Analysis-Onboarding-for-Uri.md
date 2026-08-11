# BigQuery Data Analysis with Claude — Onboarding Pack

> **What this is.** A single hand-off doc so your Claude can do BigQuery data checks and analysis on Delivery Hero fulfillment data the same way Harnoor's does. Drop this whole file into your Claude (paste it, or save it in your project and point Claude at it). It covers (1) the setup/config you need, (2) the data model and key tables, (3) the reusable base query + metric glossary, (4) domain definitions and gotchas, and (5) house style for outputs.
>
> **Audience:** you're a PM, not a SQL person — that's fine. The point is to let Claude write/run the SQL while you ask questions in plain English. The sections below are mostly *for Claude to read*, but the "Prerequisites" and "What to ask your admin" parts are *for you*.

---

## 0. Prerequisites — things YOU need before Claude can help (one-time)

Claude can't grant itself data access. Make sure these exist on your machine first:

1. **BigQuery + gcloud access to DH data.** You need read access to the `fulfillment-dwh-production` project. If you don't have it, request DH BigQuery access through the usual data-access channel (same access Harnoor / analysts have).
2. **The `bq` and `gcloud` CLIs installed and authenticated.**
   - Install (Mac): `brew install --cask google-cloud-sdk`
   - Authenticate: `gcloud auth login` then `gcloud auth application-default login`
   - Set a billing/quota project (Harnoor uses `dhub-data-commune` — use whatever your data team gives you):
     `gcloud config set project <your-billing-project>`
   - Sanity check: `bq query --use_legacy_sql=false 'SELECT 1'` should return a row.
3. **Claude Code (CLI / IDE extension / desktop).** This is what runs `bq` for you and reads this doc.

Once `bq query 'SELECT 1'` works in your terminal, Claude can run real queries.

---

## 1. Recommended Claude configuration

These are the pieces that make the experience smooth. Roughly in priority order:

### 1a. The `data-analyst` skill (highest value)
Harnoor has a Claude **skill** called `data-analyst` that encodes the whole "translate question → plan → verify schema → run SQL → explain" workflow, plus a `schema_reference.md` listing every available dataset/table. **Ask Harnoor to share the skill folder** (`data-analyst/SKILL.md` + `schema_reference.md`) and drop it into your `~/.claude/skills/` directory. This is the single biggest lever — it gives Claude the guardrails (don't invent columns, verify schemas first, prefer aggregated tables, filter to reporting-enabled entities, etc.) and the full table catalog.

If you can't get the skill, this doc reproduces the most important parts below so Claude can still work.

### 1b. Permissions (so Claude isn't prompting you constantly)
In `~/.claude/settings.json`, pre-allow the read-only/query commands you'll use a lot. The key one for data work:

```json
{
  "permissions": {
    "allow": [
      "Bash(bq query --use_legacy_sql=false --format=prettyjson ' *)",
      "Bash(bq query *)",
      "Bash(bq show *)",
      "Read(//Users/<you>/**)"
    ]
  }
}
```

`bq query` is read-only against these tables, so allow-listing it is safe. Tip: Claude Code has a `/fewer-permission-prompts` helper that scans your history and proposes an allow-list — run it after a few sessions.

### 1c. MCP servers (optional, but Harnoor uses these heavily)
- **Atlassian MCP** — lets Claude read/write Confluence pages and Jira (handy for posting analysis write-ups, reading domain docs). Connect via the Atlassian MCP server.
- **Slack** (official Claude plugin / MCP) — lets Claude search channels and post/draft messages with the analysis. Enable the `slack` plugin if you want Claude to drop results into Slack for you.

Neither is required to query data — they're for *sharing* the output. Start with just BigQuery; add these once you're comfortable.

### 1d. Memory
Turn on Claude's persistent memory. As you work, have Claude save domain facts (metric definitions, which experiment is which, data quirks) so it gets smarter over time — exactly how the knowledge in §4 below accumulated.

---

## 2. The data model — two paths into the data

There are **two** main ways into DH fulfillment data. Know which one a question needs.

### Path A — Curated / aggregated tables (`curated_data_shared_*`) — *start here for business KPIs*
Project `fulfillment-dwh-production`, datasets named `curated_data_shared_{domain}`. Clean, governed, pre-aggregated. Best for order counts, GMV, vendor KPIs, customer cohorts, etc.

Most-used domains:
| Domain | Dataset | Use for |
|---|---|---|
| coredata_business | `curated_data_shared_coredata_business` | Orders, vendors, products, customers, incentives (most common) |
| coredata | `curated_data_shared_coredata` | Reference: `global_entities`, FX rates, dates, holidays |
| coredata_tracking | `curated_data_shared_coredata_tracking` | User tracking / sessions (Perseus) |

Key tables (prefer the aggregated ones for historical data):
- `…coredata_business.agg_orders_daily` — **daily aggregated order metrics. Use this for historical order KPIs** (much faster than raw orders; not valid for *today*).
- `…coredata_business.agg_orders_city_daily` — same, per city.
- `…coredata_business.agg_vendor_kpis_{daily,weekly,monthly}` — vendor performance/GMV.
- `…coredata_business.vendors` — vendor master data.
- `…coredata_business.orders` — raw order-level; use ONLY for today's data or order-grain detail.
- `…coredata.global_entities` — **the entity/brand/country lookup. JOIN this whenever filtering by brand/country.**

**House rules for Path A:**
1. Always JOIN `global_entities` when filtering by brand/country/entity.
2. Always add `is_reporting_enabled IS TRUE` (drops discontinued brands) unless explicitly told otherwise.
3. Use `agg_*` tables for historical data; only hit `orders` for today or order-grain detail.
4. Default `LIMIT 10000`.

### Path B — Raw logistics table (`cl.orders`) — *the workhorse for delivery-timing deep dives*
`fulfillment-dwh-production.cl.orders` is the raw logistics order table with the rich **timings** struct (estimated prep time, delivery time, vendor lateness, rider lateness, etc.) and an array of `deliveries`. This is what Harnoor uses for ETA / prep-time / delivery-time analysis. See the base query in §3 — that's the canonical shape.

Rule of thumb: **business volume/GMV/cohort questions → Path A. "Why are deliveries late / how's our ETA accuracy / prep-time" questions → Path B (`cl.orders`).**

### The mandatory workflow (have Claude follow this every time)
1. **Clarify** missing info first: timeframe, filters (brand/country), metric, grouping.
2. **State a plan** (tables, filters, metrics, grouping, assumptions) before running anything.
3. **Verify the schema** of every table with `INFORMATION_SCHEMA.COLUMNS` *before* writing SQL — never assume column names.
4. **Run** via `bq query --use_legacy_sql=false --format=prettyjson '<SQL>'`; on error, read it, fix, retry.
5. **Explain** results in plain English + a markdown table.

Schema discovery snippet Claude should use:
```bash
bq query --use_legacy_sql=false --format=prettyjson '
SELECT column_name, data_type
FROM `fulfillment-dwh-production.<dataset>.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = "<table>"
ORDER BY ordinal_position'
```

---

## 3. The base query (`cl.orders`) + metric glossary

This is the reusable starting point for delivery-timing analysis. Claude should **pick/choose columns and filters** from it per question, and **always replace the date range**. All timings are divided by 60 → **minutes**.

```sql
with data as (
SELECT
  region
  , platform_order_id as order_id          -- ⚠️ see gotcha below; prefer o.order_id
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
WHERE date(o.created_date) BETWEEN '2023-11-20' AND '2023-11-21'   -- ← REPLACE
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

**Metric glossary (all in minutes):**
- **EPT** — estimated prep time · **EPB** — estimated prep buffer
- **ATVC** — at-vendor time (cleaned) · **HBT** — hold-back time
- **DT** — actual delivery time · **PDT** — promised delivery time
- **OD** — order delay (actual vs promised) · **est_delay** — estimated courier delay
- **vendor_late**, **rider_late** — lateness attributed to vendor / rider
- **customer_walk_in/out_time**, **at_customer_time** — last-leg timings
- **pdt_error** = PDT − DT (promise accuracy; ~0 is good)
- **stacks** = stacked deliveries on the primary delivery

**Bucket columns:** `DT_type` (≥45 vs <45), `VL_type`, `rider_late_type`, `order_type` (late/early/on-time at ±10 min), `stacks_final`, `ept_dt_type`.

**Available but commented out** (uncomment if asked): APT (assumed actual prep), EDT (estimated driving time), to_customer time, rider.* fields, `vendor.country_code` / `region` filters.

**Default filters:** `is_preorder = FALSE`, `order_status = 'completed'`.

---

## 4. Domain knowledge & gotchas (DH-specific — this is the hard-won stuff)

### Glossary of DH terms Claude will hit
- **Vertical types** (`o.vendor.vertical_type` on `cl.orders`): `restaurants`, `darkstores`, `supermarket`, `hypermarket`, `shop`, `convenience`. **"QC" / "quick commerce" = `darkstores`.**
- **Brands / regions:** Talabat (MENA), HungerStation (KSA), foodpanda (APAC), Glovo, PedidosYa (LatAm), Baemin/Woowa (Korea), Yemeksepeti (TR), foodora, efood (GR). Country codes are 2-letter (`ae`, `sa`, `ph`, `cz`, …).
- **EPT vs PDT vs DT:** EPT = how long we *think the vendor takes to prep*; PDT = the delivery time we *promise the customer*; DT = the *actual* delivery time. A lot of analysis is about the gaps between these.

### Adjusted Grocery Flow (AGF) = Wait-for-Assembled (WFA)
In AGF, Hurrier sends the order to the vendor immediately but **waits to assign a rider until the vendor fires `food_is_ready` (FIA)**. Identify these orders on `cl.orders` with:
```sql
WHERE "wait_for_assembled" IN UNNEST(tags)   -- tags is ARRAY<STRING>
```
Companion field `food_is_ready_at` (TIMESTAMP) is populated when FIA fires (~99% of WFA orders). Concentration is high in grocery verticals (shop ~99%, hypermarket ~35%, supermarket ~19%), near-zero in restaurants.

### "DT>45 (QC)" — the darkstores-only KPI
In the seamless/DART reporting, the headline **"DT>45 (QC)"** metric is computed over **`vendor.vertical_type = 'darkstores'` ONLY** (QC = darkstores). Other primary KPIs (PET, %on-time, %stacked-on-time) are over ALL completed non-preorder orders. Don't mix the scopes.

### Fixed vs computed EPT
Whether a vendor's EPT is model-computed or manually fixed lives in `fulfillment-dwh-production.cl._vendors_tes_prep_time_config` (`prep_time_config[].strategy` ∈ `COMPUTED`, `OPS_TEMPORARY`, `OPS_PERMANENT`). "Fixed EPT" = the OPS_* strategies. In many markets fixed EPT is <1% of orders — the COMPUTED model drives almost everything.

### ⚠️ Data gotchas (these will silently corrupt results if missed)
1. **`platform_order_id` is NULL for all CZ orders from ~2026W19 onward.** When grouping at order grain, use **`o.order_id`** instead of `platform_order_id`, or recent weeks collapse into a handful of garbage groups.
2. **`*_stream` tables** (in `curated_data_shared_data_stream`) must be **deduplicated before use**.
3. **Cross-period comparisons carry bias** (day-of-week mix, weather, demand, vendor drift). When comparing windows, always add the caveat that directional findings are suggestive, not causal — and watch for *deliberate experiments* running in a window (an "anomaly" may be an intentional test, not a regression).
4. **Experiment arm IDs are fiddly.** When splitting by A/B arm, always `SELECT DISTINCT` the allocation-id column first and verify the actual prefixes before filtering — assumed arm names silently return 0 rows for that arm.

---

## 5. House style for outputs (optional but nice)

When Claude presents comparison data (week-over-week, period-vs-period, A/B vs control), Harnoor's preferred format:
- **Opener** (1–2 sentences: what changed + what's driving it), then a **context line** with country flag + period labels + sample sizes.
- **Tables** with a `Δ` column (status/bucket tables) or a `Δ` row (percentile/metric tables).
- **Emoji on deltas:** 🔴 bad, 🟢 good, ⚪ neutral. Use the real minus sign `−` (U+2212) for negatives.
- **Bold the 2–3 cells that carry the story**, not every change. Units in the title (e.g. `(min)`), not in cells.
- Close with a **"What I'm seeing"** interpretation and, for team channels, specific **"Asks for the team."**

---

## 6. Example questions you can just ask Claude

- "How many completed orders did Talabat AE do last week, by day?" *(Path A)*
- "What's the average delivery time and % of orders over 45 min for darkstores in KSA, week over week for the last 6 weeks?" *(Path B / DT>45 QC)*
- "Compare EPT, PDT, and actual DT for AGF vs non-AGF orders in supermarket, last 2 weeks." *(WFA tag)*
- "Did our promise accuracy (PDT − DT) get worse in CZ between W1 and W19?" *(Path B, watch the `platform_order_id` gotcha)*
- "Pull vendor GMV for the top 20 vendors in PH last month." *(Path A, agg_vendor_kpis_monthly)*

Claude should always clarify timeframe/filters first if you leave them out — that's expected.

---

### One-paragraph TL;DR for Claude
> You help a PM run BigQuery analysis on Delivery Hero fulfillment data via the `bq` CLI. Two data paths: curated aggregated tables `fulfillment-dwh-production.curated_data_shared_*` (business KPIs — prefer `agg_*`, join `global_entities`, filter `is_reporting_enabled IS TRUE`) and the raw `fulfillment-dwh-production.cl.orders` with its `timings` struct + `deliveries` array (delivery-timing deep dives — use the base query in §3, all timings /60 = minutes). Always: clarify missing timeframe/filters, state a plan, verify column names via `INFORMATION_SCHEMA` before writing SQL, then run and explain with a markdown table. Know the domain terms (QC = darkstores; AGF = WFA, tag `"wait_for_assembled" IN UNNEST(tags)`; EPT/PDT/DT) and the gotchas (CZ `platform_order_id` NULL from 2026W19 → use `o.order_id`; dedup `_stream` tables; verify experiment arm IDs with SELECT DISTINCT; cross-period comparisons are biased).
