# Seamless Weekly Anomaly Report — 2026W31 (2026-07-27 – 2026-08-02) vs 2026W30

**Table 1 — Primary KPIs**

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 | WoW |
|---|---|---|---|---|---|---|---|---|---|
| Hungerstation | sa | 11.56 | +0.64⚠️ | 81.35 | -2.04⚠️ | 67.70 | -5.19⚠️ | 10.87 | +3.20⚠️ |
| Pandora | sg | 7.12📉 | +0.02 | 66.12📉 | -0.31 | 63.60 | +0.60 | 30.97📉 | +0.36 |
| Glovo | gv-ma | 5.62 | +0.37⚠️ | 76.01 | -5.70⚠️ | 73.64 | -4.89⚠️ | 9.55 | +3.52⚠️ |
| Talabat | qa | 8.93 | +0.31⚠️ | 86.67 | -1.70⚠️ | 70.04 | -6.01⚠️ | 11.85 | +2.17⚠️ |
| Pandora | mm | 7.06 | +0.71⚠️ | 70.65 | -6.52⚠️ | 61.38 | -5.66⚠️ | 28.65 | +8.30⚠️ |
| Talabat | jo | 10.67 | +0.54⚠️ | 78.68 | -2.65⚠️ | 70.95 | -1.79⚠️ | 18.50 | +3.06⚠️ |
| Talabat | kw | 8.85 | -0.15 | 86.67 | -0.26 | 69.48 | -2.92⚠️ | 10.58 | -0.24 |

**Table 2 — Diagnostic KPIs**

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | double-stacked% | WoW | triple-stacked% | WoW | Rider late% | WoW | To cust. time | WoW | %w/ buffer | WoW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Hungerstation | sa | 16.75 | +1.39 | 3.04 | +0.27 | 29.29 | +1.72 | 6.36 | +1.99 | 5.73 | +1.51 | 0.62 | +0.48 | 5.57 | +2.11 | 11.56 | +0.33 | 85.66 | +0.32 |
| Pandora | sg | 24.87 | -0.16 | 1.55 | -0.02 | 38.10 | -0.09 | 52.37 | +1.43 | 37.06 | +0.72 | 13.44 | +0.50 | 16.81 | -0.18 | 12.24 | +0.08 | 80.79 | -0.36 |
| Glovo | gv-ma | 19.86 | +2.35 | 1.77 | +0.18 | 28.16 | +2.60 | 31.66 | +7.79 | 31.65 | +7.79 | 0.01 | +0.00 | 7.23 | +2.61 | 7.32 | +0.25 | 92.52 | -3.05 |
| Talabat | qa | 15.14 | +0.79 | 2.58 | +0.01 | 29.08 | +1.17 | 9.36 | +2.82 | 8.78 | +2.30 | 0.55 | +0.48 | 2.64 | +0.50 | 12.94 | +0.38 | 90.43 | -0.90 |
| Pandora | mm | 24.43 | +3.43 | 1.72 | +0.22 | 36.89 | +3.83 | 33.29 | +9.11 | 24.93 | +4.85 | 7.06 | +3.36 | 14.09 | +4.92 | 11.47 | +0.40 | 81.97 | +0.57 |
| Talabat | jo | 20.13 | +1.29 | 2.48 | +0.04 | 32.01 | +1.50 | 24.76 | +5.52 | 24.37 | +5.35 | 0.32 | +0.11 | 7.94 | +1.67 | 10.90 | +0.21 | 85.92 | -2.01 |
| Talabat | kw | 14.80 | -0.37 | 2.48 | -0.17 | 28.97 | -0.18 | 11.14 | +1.90 | 10.59 | +1.50 | 0.35 | +0.22 | 1.13 | -0.34 | 13.18 | +0.20 | 72.45 | -0.11 |

**Reasoning**

- Hungerstation sa and Talabat qa/jo: realized slowdown (DT, time-to-pickup up) with rising stacking and rider lateness dragging on-time; jo persistent 4 weeks.
- Glovo ma hit by Throne Day (Jul 30 long weekend); Pandora mm by Yangon monsoon floods — both show DT spikes, over-stacking, rider lateness.
- Talabat kw: only stacked on-time fell (-2.92pp) while overall DT stayed flat — dispatch over-batching delaying later legs of stacked chains.
- Pandora sg flagged on Path B only: slow 4-week rollover (on-time -4.06pp, DT>45 +9.03pp cumulatively) with no single-week spike.

**Actions**

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| Hungerstation / sa | DT +1.72, rider late% +2.11, stacking +1.99 → realized slowdown | Vendor / demand | Field / vendor ops | dh-customer-ops-hungerstation | Flag demand-driven slowdown; watch rider supply and vendor SLA. |
| Glovo / gv-ma | On-time -5.70, DT +2.60, stacking +7.79 on Throne Day | Vendor / demand | Field / vendor ops | dh-customer-ops-glovo | Expect Throne Day (Jul 30) impact; reinforce holiday rider staffing. |
| Talabat / qa | Stacked on-time -6.01, DT +1.17, stacking +2.82 | Vendor / demand | Field / vendor ops | dh-customer-ops-talabat | Flag realized slowdown; review batching on stacked orders. |
| Pandora / mm | DT +3.83, DT>45 +8.30, rider late% +4.92 (Yangon floods) | Rider / courier behaviour | Platform ops | dh-customer-ops-foodpanda | Expect flood impact; monitor rider supply until roads clear. |
| Talabat / jo | On-time -2.65 (cum -7.22), DT +1.54, stacking +5.52; persistent | Vendor / demand | Field / vendor ops | dh-customer-ops-talabat | Flag persistent slowdown; do not change PDT off <4wk. |
| Talabat / kw | Stacked on-time -2.92, DT flat, double-stacked +1.50 | Vendor / demand | Field / vendor ops | dh-customer-ops-talabat | Review dispatch batching aggressiveness on stacked orders. |
| Pandora / sg | Path-B rollover: on-time -4.06pp, DT>45 +9.03pp over 4 weeks | Vendor / demand | Field / vendor ops | dh-customer-ops-foodpanda | Monitor rollover; revisit PDT only if it persists 4+ weeks. |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand's dh-customer-ops channel; PDT-range-test rows are expected, no action._

**Platform Health**

Platform deterioration share — **Hungerstation 1/1 (100%)** · Talabat 6/8 (75%) · Pandora 7/15 (47%) · Glovo 6/13 (46%) · Pedidosya 5/13 (38%) · Efood 0/2 (0%)
