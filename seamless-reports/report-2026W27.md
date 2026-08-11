# Seamless Weekly Anomaly Report — 2026W27 (Jun 29 – Jul 5) vs 2026W26

**Table 1 — Primary KPIs**

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 (QC) | WoW |
|---|---|---|---|---|---|---|---|---|---|
| glovo | gv-ma | 5.96 | ⚠️ +0.74 | 76.05 | ⚠️ -7.52 | 73.99 | ⚠️ -6.19 | 50.00 | ⚠️ +50.00 |
| pedidosya | ar | 7.22 | ⚠️ +1.05 | 73.89 | ⚠️ -6.23 | 69.92 | ⚠️ -5.79 | 22.57 | ⚠️ +9.19 |
| glovo | gv-pt | 7.16 | ⚠️ +0.84 | 69.09 | ⚠️ -5.99 | 59.65 | ⚠️ -6.33 | 22.03 | ⚠️ +14.23 |
| glovo | gv-es | 6.76 📉 | +0.26 | 73.01 | ⚠️ -2.48 | 67.97 | ⚠️ -2.40 | 22.75 | 🚀 -1.44 |
| hungerstation | sa | 13.34 | ⚠️ +1.03 | 79.69 | ⚠️ -2.33 | 68.42 | -1.10 | 5.65 | ⚠️ +1.73 |
| pedidosya | cl | 8.87 | ⚠️ +0.60 | 71.11 | ⚠️ -2.69 | 64.75 | ⚠️ -2.51 | 19.81 | ⚠️ +4.40 |
| pandora | my | 6.69 | +0.08 | 71.80 | -0.56 | 63.77 | +0.55 | 19.30 📉 | +0.58 |

**Table 2 — Diagnostic KPIs**

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | double-stacked% | WoW | triple-stacked% | WoW | Rider late% | WoW | To cust. time | WoW | %w/ buffer | WoW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| glovo | gv-ma | 19.92 | ⚠️ +3.04 | 1.85 | ⚠️ +0.45 | 28.18 | ⚠️ +3.48 | 33.18 | ⚠️ +11.71 | 33.17 | ⚠️ +11.71 | 0.01 | +0.00 | 7.17 | ⚠️ +3.05 | 7.27 | ⚠️ +0.44 | 97.36 | +0.03 |
| pedidosya | ar | 21.67 | ⚠️ +3.85 | 2.12 | ⚠️ +0.29 | 32.12 | ⚠️ +4.16 | 55.61 | ⚠️ +7.60 | 29.67 | ⚠️ +1.81 | 23.58 | ⚠️ +6.52 | 8.69 | ⚠️ +2.84 | 9.47 | ⚠️ +0.31 | 96.84 | +0.18 |
| glovo | gv-pt | 21.90 | ⚠️ +3.44 | 2.99 | ⚠️ +0.54 | 31.85 | ⚠️ +3.50 | 13.57 | ⚠️ +2.08 | 13.50 | ⚠️ +2.07 | 0.07 | +0.01 | 17.79 | ⚠️ +5.06 | 8.97 | +0.06 | 81.06 | +0.05 |
| glovo | gv-es | 21.63 | ⚠️ +1.11 | 2.86 | +0.16 | 31.08 | ⚠️ +1.31 | 33.21 | ⚠️ +2.21 | 28.65 | ⚠️ +1.38 | 3.89 | ⚠️ +0.70 | 9.82 | ⚠️ +1.05 | 8.47 | +0.21 | 97.56 | +0.31 |
| hungerstation | sa | 17.70 | ⚠️ +1.34 | 3.18 | ⚠️ +0.29 | 30.29 | ⚠️ +1.67 | 5.79 | ⚠️ +2.33 | 5.35 | ⚠️ +2.05 | 0.44 | +0.28 | 6.83 | ⚠️ +1.70 | 11.60 | ⚠️ +0.33 | 97.78 | +0.06 |
| pedidosya | cl | 23.65 | ⚠️ +1.55 | 3.93 | ⚠️ +0.55 | 34.55 | ⚠️ +1.64 | 43.07 | ⚠️ +3.58 | 31.79 | ⚠️ +1.78 | 9.98 | ⚠️ +1.40 | 10.42 | ⚠️ +2.88 | 9.91 | +0.10 | 91.12 | -5.46 |
| pandora | my | 20.36 | +0.32 | 1.70 | +0.03 | 32.07 | ⚠️ +0.62 | 29.29 | ⚠️ +3.51 | 23.05 | ⚠️ +2.02 | 5.00 | ⚠️ +1.06 | 10.18 | +0.20 | 10.73 | ⚠️ +0.30 | 89.20 | -0.29 |

**Reasoning**

- Realized slowdown, not model: PET↑ from TTP/AWT with EPT flat; DT↑ outran a loosened PDT, dragging on-time down — an ops issue, not #log-sds-int.
- Supply-forced over-stacking is the shared thread: stacking% up in gv-ma (+11.7), ar (+7.6, triple +6.5), cl (+3.6), my (+3.5) — later legs breach the promise.
- Rider lateness compounds delays in gv-pt (+5.1pp) and gv-ma/ar/cl (+2.8–3.1pp); sa is a +9.8% WoW demand surge, not a lateness story.
- Iberia/Morocco (gv-es, gv-pt, gv-ma) caught the 2026 European heatwave tail + Jul-1 storms; gv-ma's +50 DT>45 QC is a 2-order artifact — ignore.

**Actions**

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| gv-ma | Over-stacking +11.7pp + rider late +3.1pp lift DT; QC +50 is a 2-order artifact | Rider / courier behaviour | Platform ops | dh-customer-ops-glovo | Flag Morocco stacking + rider-late surge to Glovo ops; note heatwave tail. |
| ar | Realized slowdown: DT +4.2 outran loosened PDT; triple-stacking +6.5pp, rider late +2.8pp | Rider / courier behaviour | Platform ops | dh-customer-ops-pedidosya | Raise AR over-stacking + rider lateness with PeYa ops. |
| gv-pt | Rider late% +5.1pp dominant; DT +3.5; darkstore QC +14.2 on solid base | Rider / courier behaviour | Platform ops | dh-customer-ops-glovo | Escalate Portugal rider lateness + QC breach to Glovo ops. |
| gv-es | Slow rollover (PET Path-B); DT +1.3, stacking +2.2; heatwave-tail supply thinning | Vendor / demand | Field / vendor ops | dh-customer-ops-glovo | Monitor Spain; flag heat-driven rider-supply thinning to Glovo ops. |
| sa | Demand surge +9.8% WoW lifts DT/PET; peak summer heat, no holiday overlap | Vendor / demand | Field / vendor ops | dh-customer-ops-hungerstation | Add rider capacity for KSA demand surge; watch vendor prep. |
| cl | DT +1.6 outran PDT; stacking +3.6pp, rider late +2.9pp; model coverage −5.5pp | Rider / courier behaviour | Platform ops | dh-customer-ops-pedidosya | Raise Chile stacking + rider lateness with PeYa ops; check EPT-config drop. |
| my | QC DT slow rollover (Path B) + stacking +3.5pp; DT>45 QC now 19.3% | Vendor / demand | Field / vendor ops | dh-customer-ops-foodpanda | Watch Malaysia darkstore QC; flag stacking to foodpanda ops if it persists. |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand’s dh-customer-ops channel; PDT-range-test rows are expected, no action._

Platform deterioration share — **Hungerstation 1/1 (100%)** · **Glovo 19/22 (86%)** · **Talabat 5/6 (83%)** · **Pedidosya 12/15 (80%)** · Pandora 10/18 (56%) · Efood 1/2 (50%)
