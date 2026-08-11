[scheduled-job test run]
*🛰️ Seamless Ops — Weekly Anomaly Scan*
🗓️ *W21 (May 18–24)* vs *W20 (May 11–17)* • completed, non-preorder orders • source: `cl.orders`

TL;DR: GCC Talabat (Oman, Jordan) and Glovo Morocco buckled under a demand surge + stacking spike, foodpanda Thailand has a pure rider-lateness problem (volume actually fell), and PedidosYa Chile is leaking on quick-commerce only. Meanwhile Argentina and Philippines are quietly flexing. EPT barely moved anywhere (<1 min WoW), so this is a dispatch/supply story, *not* a prep-time model story.

### 1) Countries That Need Focus

*Table 1 — Primary KPIs* (the source of truth for who needs attention)

| Brand | Market | PET (min) | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 QC % | WoW |
|---|---|---|---|---|---|---|---|---|---|
| PedidosYa | 🇦🇷 Argentina | 5.55 | 🚀 −0.37 | 82.22 | 🚀 +1.97 pp | 77.60 | 🚀 +2.19 pp | 12.85 | 🚀 **−6.28 pp** |
| foodpanda | 🇵🇭 Philippines | 6.83 | 🚀 −0.33 | 74.46 | 🚀 **+3.07 pp** | 65.44 | 🚀 +2.33 pp | 41.55 | −0.85 pp |
| foodpanda | 🇹🇭 Thailand | 5.32 | +0.14 | 77.48 | ⚠️ −1.30 pp | 73.41 | −0.30 pp | 13.32 | −0.59 pp |
| Talabat | 🇴🇲 Oman | 10.64 | ⚠️ +0.58 | 75.76 | ⚠️ −2.15 pp | 68.04 | ⚠️ −1.83 pp | 20.55 | ⚠️ +2.04 pp |
| PedidosYa | 🇨🇱 Chile | 7.43 | +0.03 | 73.96 | −0.33 pp | 69.04 | −0.08 pp | 11.02 | ⚠️ +1.45 pp |
| Glovo | 🇲🇦 Morocco | 5.32 | +0.26 | 78.74 | ⚠️ −1.75 pp | 78.37 | ⚠️ −2.09 pp | 7.58 | +0.81 pp |
| Talabat | 🇯🇴 Jordan | 8.83 | ⚠️ +0.50 | 86.10 | ⚠️ −2.36 pp | 74.96 | ⚠️ **−3.15 pp** | 10.24 | ⚠️ +1.90 pp |

*Table 2 — Diagnostic KPIs* (the "why" behind the table above)

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | Rider late% | WoW | To cust. | WoW | %w/ buffer | WoW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PedidosYa | 🇦🇷 Argentina | 16.67 | 🚀 −1.41 | 1.57 | −0.10 | 26.48 | 🚀 −1.52 | 43.42 | 🚀 −2.30 pp | 5.62 | 🚀 −0.91 pp | 8.83 | −0.10 | 69.52 | +1.02 pp |
| foodpanda | 🇵🇭 Philippines | 21.18 | 🚀 −1.82 | 1.96 | −0.04 | 30.92 | 🚀 −2.19 | 39.59 | 🚀 **−5.03 pp** | 8.87 | 🚀 −2.10 pp | 8.76 | −0.36 | 91.25 | −0.73 pp |
| foodpanda | 🇹🇭 Thailand | 17.64 | ⚠️ +1.12 | 1.53 | −0.03 | 28.01 | ⚠️ +1.01 | 54.83 | −0.22 pp | 15.07 | ⚠️ **+3.00 pp** | 9.38 | −0.12 | 58.09 | +0.30 pp |
| Talabat | 🇴🇲 Oman | 19.78 | ⚠️ +1.29 | 2.46 | ⚠️ +0.27 | 33.48 | ⚠️ **+1.69** | 42.36 | ⚠️ +3.07 pp | 6.45 | ⚠️ +1.27 pp | 12.71 | +0.40 | 91.63 | +0.01 pp |
| PedidosYa | 🇨🇱 Chile | 21.74 | −0.31 | 2.75 | +0.18 | 32.27 | −0.39 | 37.06 | ⚠️ +1.70 pp | 7.67 | +0.24 pp | 9.54 | −0.08 | 89.29 | 🚀 +5.22 pp |
| Glovo | 🇲🇦 Morocco | 18.21 | ⚠️ +1.08 | 1.49 | +0.17 | 26.46 | ⚠️ +1.32 | 30.91 | ⚠️ **+3.31 pp** | 5.57 | ⚠️ +0.78 pp | 7.26 | +0.24 | 95.39 | +0.28 pp |
| Talabat | 🇯🇴 Jordan | 15.64 | ⚠️ +1.04 | 2.16 | +0.15 | 27.01 | ⚠️ +1.56 | 8.04 | ⚠️ **+3.45 pp** | 2.31 | +0.61 pp | 10.38 | ⚠️ +0.52 | 75.86 | ⚠️ −3.40 pp |

*Per-market read:*
- 🇴🇲 *Oman (Talabat)* — the week's worst. All four primaries deteriorated. PET +0.58 is driven by TTP +1.29, not prep (EPT +0.16, AAPT +0.31). Orders +6.6% WoW, %stacked +3.1 pp, DT +1.7 min → on-time −2.15 pp. Classic supply-can't-keep-up-with-demand.
- 🇯🇴 *Jordan (Talabat)* — same shape, sharper on stacked on-time (−3.15 pp). Orders +8.8%, stacking +3.45 pp, DT +1.56, TTP +1.04. Buffer coverage also dropped −3.4 pp, so fewer orders had protective padding right as load rose.
- 🇲🇦 *Morocco (Glovo)* — biggest volume jump of the set (+9.9% WoW). Stacking +3.31 pp, TTP +1.08, DT +1.32 → on-time −1.75 and stacked on-time −2.09. Pure saturation.
- 🇹🇭 *Thailand (foodpanda)* — the odd one out: orders *fell* −5.3%, prep and AWT are flat, yet on-time slipped −1.30 pp. The smoking gun is rider late% +3.00 pp (now 15.1%) and TTP +1.12 — couriers, not kitchens.
- 🇨🇱 *Chile (PedidosYa)* — restaurants are fine (overall DT −0.39, EPT −0.67), but QC DT>45 rose +1.45 pp under +5.3% volume and +1.7 pp stacking. A quick-commerce-only leak.

### 2) Potential Reasons of the Shift

1. *Demand-surge + stacking saturation (Oman, Jordan, Morocco).* Order volume jumped +6.6% to +9.9% WoW while %stacked rose +3.1 to +3.5 pp, pushing TTP up ~1 min and DT up +1.3–1.7 min → on-time and stacked-on-time fell 1.8–3.2 pp. AAPT moved only marginally (+0.2–0.3) and EPT was flat, so this is a *fleet supply/dispatch* shortfall reacting to demand — matching the "%on-time → Delivery Time Increase" heuristic (DT↑ + volume↑ + stacking↑ ⇒ reduced rider availability), *not* a vendor-prep or EPT-model issue.
2. *Courier lateness, not capacity, in Thailand.* Volume dropped yet rider late% spiked +3.0 pp (to 15.1%) with TTP +1.1 min and STV +0.4, while prep/AWT held flat. This is the "Courier Delay" heuristic — riders reaching pickup late (traffic/dispatch radius/timing), pushing PDT +1.8 and on-time down.
3. *Quick-commerce-only stretch in Chile.* Restaurant DT actually improved; the deterioration is isolated to the QC/grocery vertical (DT>45 +1.45 pp) under +5.3% volume and rising stacking — a localized darkstore dispatch/density problem rather than a market-wide one.

*EPT note:* per the heuristic gate, Query 3 (EPT type/volume breakdown) is only run when avg EPT rises >1 min WoW. No flagged market crossed that bar (max ~+0.3 min), so EPT model-inflation is ruled out and Query 3 was correctly skipped.

### 3) Potential Solutions

*Oman / Jordan / Morocco (demand-surge + stacking)*
- *Right-size rider supply* via the Rooster forecast → UTR → shift flow, and trigger mid-week shift extensions for the surging zones — see [How to check if %On-Time change is operational](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/36656568) (saturation triage: UTR, rider hours, %stacked) and [Logistics – staffing/dispatch/surge overview](https://atlassian.cloud.deliveryhero.group/wiki/spaces/TLBTDTV2/pages/54525368).
- *Protect on-time under load* with stacking/distance levers (distance hard caps, lateDelivery vs WaitingAtPickup penalty balance) from [Solution Design: Stacking](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/110594314) and [Algo Penalties & Prioritization](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGAPAC/pages/42070305). ⚠️ *Guardrail:* any dispatch/penalty change goes **through the Rider Ops team**, not local config edits.

*Thailand (rider lateness)*
- *Escalate to Rider Ops* — rider late% +3.0 pp is squarely their court. Levers to discuss with them: LatePickupPenalty tuning and dispatch radius/timing from [Algo Penalties & Prioritization](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGAPAC/pages/42070305), plus an STV-latency check. Validate against the [Seamless Orders DT root-cause matrix](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGAPAC/pages/42070208).

*Chile (QC leak)*
- *Targeted QC dispatch/density review* — vendor/darkstore density and P-D distance / surge-for-distance levers from [Seamless Orders](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGAPAC/pages/42070208), scoped to grocery only since restaurants are healthy.

*Across the board:* 🚫 do **not** touch PDT ranges or buffers off a single week — only consider that lever if the same market shows the same KPI degradation for **4+ consecutive weeks**. This is week 1; we watch.

---
🎉 *Shoutouts:* 🇦🇷 *Argentina* quietly torched its QC DT>45 by −6.3 pp and lifted on-time +2.0 pp — chef's kiss. And 🇵🇭 *Philippines* cut stacking −5.0 pp and pushed on-time +3.1 pp while TTP dropped ~2 min. Whatever you two are doing, bottle it and ship it to Muscat. 🍾
