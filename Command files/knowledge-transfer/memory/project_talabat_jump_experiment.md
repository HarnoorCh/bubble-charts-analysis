---
name: project-talabat-jump-experiment
description: "Talabat Jump Station v2 ETA experiment (538) — 3-arm T1/T2/Control comparison, KPIs, and the allocation-id prefix gotcha"
metadata: 
  node_type: memory
  type: project
  originSessionId: ffdbd1e7-94fc-4792-95d0-e99447956d43
---

**Talabat Jump experiment** = `2026-06-11_TB_Jump_Station_v2_All_Countries:538` (TB, MENA: ae, bh, eg, iq, jo, kw, om, qa). 3 arms compared on first run **2026-06-14** over window **2026-06-11 → 2026-06-13**.

Arms keyed off `eta_format_config_allocation_id` in `fulfillment-dwh-production.cl.tracking_api_logs`. **GOTCHA:** all three arms use the `logistics-otx:tapi-config-variant:...:538:<arm>` prefix — `Control`, `Treatment1`, `Treatment2`. The original example query had Control as `tapi-split-by-customer-id:...:Control`, which is wrong and silently drops the Control arm (returns 0 rows). Always verify with `SELECT DISTINCT eta_format_config_allocation_id ... WHERE CONTAINS_SUBSTR(..., '538')`.

KPIs analyzed: seamless_fail_rate, ccr, hcsr, num_orders, order_per_customer, jump_rate, jump_magnitude. Output rolled up to global + country level per arm.

**Finding:** T1 is the jump-reducer — global jump_rate −8.9pp (70.9% → 62.0%), reduces jumps in every country (−5 to −11pp), with neutral/slightly-better seamless fail and marginally higher CCR/HCSR. **T2 ≈ Control on every KPI** (jumps 70.8% vs 70.9%).

Working query saved at `/Users/harnoor.chahal/ai/jump_station_3arm.sql`. Related: [[reference_basequery]].
