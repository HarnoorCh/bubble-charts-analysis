---
name: project-ar-darkstores-ept-tests
description: "AR darkstores EPT-inflation tests (P1: 2026-04-30 to 05-03, P2: 2026-05-10 to 05-13). P3 (2026-05-18 to 05-24) = no-testing baseline. User's interpretation of three adverse effects + bias caveat."
metadata: 
  node_type: memory
  type: project
  originSessionId: 6f244861-e4ac-4dbc-9dc3-b0738b878230
---

**Fact:** In AR darkstores, the elevated `PDT < EPT` cohort observed in P1 (Apr 30 – May 3) and P2 (May 10 – May 13) was caused by **deliberate EPT-inflation tests**, not a model regression. P3 (May 18 – May 24) is the no-testing baseline. The user's diagnosis of the three adverse effects of inflating EPT:

1. **More %late orders.** Inflated EPT pushes more orders into `EPT > PDT` because PDT doesn't adjust to the inflated EPT. The promise system isn't accounting for the test-inflated prep time, so orders look late vs PDT. Running the tests longer would let the model "learn" — but the user explicitly does NOT want to extend the tests, for the three reasons below.
2. **Artificially inflated DT.** Baseline AR darkstores DT is ~29 min (P3 PDT≥EPT cohort = 28.56 min). Tests pushed actual DT up (P1 PDT<EPT cohort DT = 59 min, P2 = 46 min). The DT inflation is test-induced, not real demand for longer delivery.
3. **Inflated pickup times + slower vendor prep.** Extra EPT inflates TTP (pickup time). AWT improvement under test is **misleading** — it's coming at the cost of over-estimated pickup times. Vendors actually click FIR earlier than the inflated EPT would suggest; and prior experimentation has shown that **increasing EPT causes vendors to slow down their prep** (i.e. EPT is partially self-fulfilling).

**Caveat the user calls out:** the P1 vs P2 vs P3 comparison spans different time periods and carries clear data bias (day-of-week mix, weather, demand patterns, vendor population drift). Treat directional findings as suggestive, not causal.

**Why:** Established 2026-05-29 after presenting a darkstores deep-dive (orders × on-time/late/early × EPT/PDT/DT/AWT/TTFIR/TTP × % fixed EPT) across the three periods. My initial framing called the P1 escalation a "model calibration regression that resolved by P3"; the user corrected this — P1/P2 were tests, P3 is the real baseline.

**How to apply:**
- When discussing AR darkstores PDT/EPT performance across these dates, frame P1 and P2 as **test windows**, not regressions, and use P3 as the steady-state reference.
- When the user (or stakeholders) ask whether to "run the tests longer for the model to learn", surface the three adverse effects above — extending tests inflates DT, TTP, and pushes vendors to slow down prep; AWT gains are illusory.
- Don't lean on cross-period quantitative comparisons as definitive — always add the cross-period bias caveat when summarizing.
- "Fixed EPT" (`OPS_TEMPORARY`/`OPS_PERMANENT` strategy in `cl._vendors_tes_prep_time_config`) is essentially unused in AR (<0.4% of orders in all periods). The COMPUTED model is what's being tested.

**Related:** [[reference-basequery]] for the underlying timings query shape. Fixed-vs-computed EPT lives in `fulfillment-dwh-production.cl._vendors_tes_prep_time_config` (`prep_time_config[].strategy` ∈ {COMPUTED, OPS_TEMPORARY, OPS_PERMANENT}).
