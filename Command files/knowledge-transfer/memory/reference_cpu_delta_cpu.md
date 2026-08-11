---
name: reference_cpu_delta_cpu
description: "CPU = Committed Pick-Up time (not cost per unit); Delta CPU gap gates stacking at ~4 min; DTM sub-model feature"
metadata:
  type: reference
---

**CPU = Committed Pick-Up time** (NOT cost-per-unit). **Δ CPU** = the gap between two orders' committed pickup times. Dispatch stacks two orders only when **Δ CPU ≤ ~4 min** (Max Δ CPU threshold). It is a DTM (dispatch/delivery-time model) sub-model feature; in simulation it mainly cuts the **stacked-order late tail** (tested in the PDT hackathon — up to +5pp on-time in gv-hr). Related concept: "High Underestimation Penalty" Confluence page. See [[project_country_ranking_hackathon]].
