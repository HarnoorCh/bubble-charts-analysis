---
name: reference_dart_dt45_qc
description: "DART /run-seamless-analysis — primary KPI renamed \"DT>45\" (was \"DT>45 (QC)\"); now ALL verticals, no darkstores filter"
metadata: 
  node_type: memory
  type: reference
  originSessionId: afb84f0f-c7cf-43f5-8510-71350a6e2efb
---

In the DART-v1.md `/run-seamless-analysis` workflow, the primary KPI is **"DT>45"** (renamed from "DT>45 (QC)" on 2026-07-06). It is now `COUNTIF(actual_delivery_time/60 > 45) / COUNT(completed non-preorder)` across **ALL verticals** (QC + darkstores + restaurants) — no vertical filter. All four primaries (PET, %on-time, %stacked on-time, DT>45) are all-orders.

**Why the change:** the old metric scoped DT>45 to darkstores only, but that filter lived *downstream* in the synthesis layer (heuristic §4 + this note), not in Query 1 (whose `DT_45_numerator/denominator` were always all-vertical). User decided (2026-07-06) to make it a single blunt delivery-speed tail over every vertical and drop the "(QC)" label. Fix landed at source: comment in Query 1 forbids re-filtering; heuristic §4 rewritten to "all verticals"; read **WoW change, not absolute level** (restaurant-heavy markets sit structurally higher). This also killed the old gv-ma "50% from 2 darkstores orders" small-sample artifact (denominator is now all orders). See [[project_dt_analysis]].

Diagnostic reconstructions that aren't fully pinned in the SQL library: **"To cust. time"** = `TIMESTAMP_DIFF(rider_near_customer_at, rider_picked_up_at, MINUTE)` (pickup→near-customer); **"%w/ buffer"** = % of orders priced by the model (`preptime_code_version_used_for_vendor` not OPS/NULL). Also: Query 1 must use INTERVAL 35 DAY (not the SQL library's 14) per Determinism Rules to evaluate Path B over W-4..W. Related: [[project_domain_update_prep]].
