---
name: project_pelican_shops
description: "Pelican shops experiment (PT prefix) analysis; scan cost fixed by source reads; artifacts + cluster-aware significance test"
metadata:
  type: project
---

Experiment **`2026-06-10_PT_pelican_shops_global`** (PT = experiment prefix). 14-day pre-window, randomized by `split_unit` = country-city-hour, allowlist `%2026-06-10_PT_pelican_shops_global%`; config lived in project `logistics-customer-staging`. Read-outs grouped by vertical × {country|platform} × arm (Control/Treatment).

Key learning: **scan cost (~1.1 TB, ~$7) is fixed by source-table reads** (`cl.orders`, `cl._deliveries`, and especially `cl.tes_user_sessions` for allocation→arm) regardless of output grain — aggregating the output saves nothing; only reusing already-fetched data is free. Artifacts under `/Users/harnoor.chahal/ai/`: `pelican_stats_ready.sql` (cluster grain), `pelican_dashboard.sql` (order grain), `pelican_significance.py` (cluster-aware Welch t-test, p-value via regularized incomplete beta — no numpy/scipy). Related: [[reference_scheduled_query_extraction]].
