---
name: project_country_ranking_hackathon
description: "Country-ranking dashboard (weighted rank-sum, 66 countries) + PDT hackathon team 'PDTs are cool' (Delta CPU + rider acceptance features, GMV BOE)"
metadata:
  type: project
---

**Country-ranking dashboard** `/Users/harnoor.chahal/ai/country-ranking-dashboard/`: offline HTML + Chart.js ranking all 66 DH countries by weighted rank-sum over toggleable KPI signals (direction + weight editable live client-side). `build_dashboard.py`, `kpi_catalog.json` (declarative signals: key/label/group/dir/fmt/default_weight/type/active/expr; type ratio→SAFE_DIVIDE(COUNTIF/COUNTIF), average→AVG(IF), external, custom), one combined single-scan `cl.orders` SQL, `MIN_THRESHOLD` 10,000 orders. Used to pick a stacking/dispatch testbed via 5-criteria weighted rank-sum → winner **Georgia (gv-ge)** (alternates Kazakhstan, Croatia).

**PDT hackathon** "The next PDT model feature is…", team **PDTs are cool** (`#team-pdts-are-cool` C0BCHN98DPG): Harnoor (analysis), Zhamal Toktamysova + Dongin Kim (DTM model owners = "Don and Shamal"), Asher Nehemiah (Talabat), Grigoris Xenikakis (e-food). On `cpl-hackathon` branch (Metaflow, 1-month window): **Δ CPU** cut the stacked late tail (up to +5pp on-time gv-hr); **rider-acceptance** feature showed no lift → dropped. BOE GMV uplift ≈ **€5–16 Mio/yr, central ~€14 Mio** (1% relative cut in CX cancellations ≈ €2.74 Mio/yr; 2025 base 2.28B orders, €13.36/order, 0.90% CX cancel). Site `/Users/harnoor.chahal/ai/hackathon-pdts-are-cool/index.html`. Related: [[reference_cpu_delta_cpu]].
