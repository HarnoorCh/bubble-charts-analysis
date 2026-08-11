# Seamless Weekly Anomaly Report — 2026W32 (2026-08-03 – 2026-08-09) vs 2026W31

**Table 1 — Primary KPIs**

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 | WoW |
|---|---|---|---|---|---|---|---|---|---|
| Pandora | ph | 6.49 | +0.30⚠️ | 73.45 | -3.57⚠️ | 62.56 | -2.50⚠️ | 18.86 | +5.50⚠️ |
| Talabat | jo | 10.79📉 | +0.12 | 79.48📉 | +0.80 | 72.31📉 | +1.36 | 18.65📉 | +0.15 |
| Glovo | gv-ua | 6.26 | +0.70⚠️ | 65.69 | -8.94⚠️ | 60.38 | -7.67⚠️ | 21.53 | +9.04⚠️ |
| Pandora | tw | 4.74 | +0.31⚠️ | 83.34 | -2.40⚠️ | 76.55 | -2.75⚠️ | 8.38 | +3.16⚠️ |
| Pandora | sg | 7.57 | +0.45⚠️ | 63.72 | -2.40⚠️ | 61.95 | -1.65⚠️ | 36.08 | +5.11⚠️ |
| Glovo | gv-ge | 6.34 | +0.67⚠️ | 68.58 | -5.32⚠️ | 65.67 | -2.98⚠️ | 25.43 | +8.22⚠️ |
| Pandora | hu | 7.26 | +0.80⚠️ | 73.73 | -5.03⚠️ | 69.49 | -3.19⚠️ | 20.51 | +6.51⚠️ |

**Table 2 — Diagnostic KPIs**

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | double-stacked% | WoW | triple-stacked% | WoW | Rider late% | WoW | To cust. time | WoW | %w/ buffer | WoW |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Pandora | ph | 21.40 | +2.64 | 1.63 | -0.08 | 31.57 | +2.93 | 39.05 | +4.80 | 31.10 | +2.95 | 6.00 | +1.17 | 11.90 | +4.59 | 9.18 | +0.29 | 89.16 | -0.37 |
| Talabat | jo | 20.41 | +0.28 | 2.41 | -0.07 | 32.11 | +0.10 | 22.00 | -2.76 | 21.70 | -2.67 | 0.28 | -0.04 | 7.82 | -0.12 | 10.71 | -0.19 | 93.83 | +7.91 |
| Glovo | gv-ua | 26.36 | +4.96 | 1.92 | +0.27 | 34.25 | +5.40 | 25.98 | +9.49 | 24.99 | +8.98 | 0.86 | +0.45 | 17.74 | +6.82 | 6.91 | +0.45 | 92.01 | -1.43 |
| Pandora | tw | 16.39 | +1.84 | 0.99 | +0.01 | 24.45 | +1.69 | 32.39 | +0.24 | 25.49 | -0.02 | 5.74 | +0.08 | 8.85 | +2.36 | 7.07 | -0.15 | 42.29 | -0.09 |
| Pandora | sg | 27.01 | +2.14 | 1.65 | +0.10 | 40.29 | +2.19 | 54.23 | +1.86 | 37.55 | +0.49 | 14.50 | +1.06 | 19.72 | +2.91 | 12.29 | +0.05 | 81.11 | +0.32 |
| Glovo | gv-ge | 25.63 | +3.47 | 1.75 | +0.19 | 35.42 | +3.89 | 39.53 | +11.16 | 36.76 | +10.06 | 2.40 | +0.93 | 15.69 | +4.42 | 8.81 | +0.43 | 87.46 | +0.11 |
| Pandora | hu | 23.91 | +2.78 | 1.95 | +0.42 | 34.98 | +3.35 | 46.75 | +9.98 | 36.70 | +6.35 | 8.62 | +2.93 | 11.05 | +2.02 | 10.08 | +0.58 | 82.88 | -1.31 |

**Reasoning**

- Pandora ph and tw: realized slowdown from APAC weather — Habagat floods (Manila) and Typhoon Dolphin (north Taiwan); TTP, rider late%, stacking up, volume flat.
- Pandora hu and sg: demand-driven — hu volume +15.7% under Central-Europe heatwave, sg National Day (Aug 9) — forcing stacking (+10pp) and DT slowdown.
- Glovo gv-ua and gv-ge: sharp slowdown plus over-stacking (ge +11pp, ua +9pp) and rider lateness; ua amid Aug 8–9 strikes/grid strain; PDT widened in response.
- Talabat jo: Path-B persistent 4-week rollover (cumulative on-time down); this week flat and stabilizing, no single-week spike.

**Actions**

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| Pandora / ph | DT +2.93, rider late% +4.59, DT>45 +5.50 during Habagat floods | Rider / courier behaviour | Platform ops | dh-customer-ops-foodpanda | Expect monsoon-flood impact; reinforce rider supply until floods recede. |
| Talabat / jo | Path-B rollover; cumulative on-time down, this week flat | Vendor / demand | Field / vendor ops | dh-customer-ops-talabat | Monitor persistent slide; do not change PDT off <4wk. |
| Glovo / gv-ua | On-time -8.94, DT +5.40, stacking +9.49, rider late% +6.82 | Rider / courier behaviour | Platform ops | dh-customer-ops-glovo | Expect Aug 8–9 strike/grid disruption; watch rider supply. |
| Pandora / tw | On-time -2.40, DT +1.69, rider late% +2.36 during Typhoon Dolphin | Rider / courier behaviour | Platform ops | dh-customer-ops-foodpanda | Expect typhoon impact; reinforce rider staffing in the north. |
| Pandora / sg | DT +2.19, DT>45 +5.11, rider late% +2.91 on National Day | Vendor / demand | Field / vendor ops | dh-customer-ops-foodpanda | Expect National Day demand; bolster holiday rider staffing. |
| Glovo / gv-ge | Stacking +11.16, double +10.06, DT +3.89, on-time -5.32 | Rider / courier behaviour | Platform ops | dh-customer-ops-glovo | Review dispatch over-batching; reduce stacking aggressiveness. |
| Pandora / hu | Volume +15.7%, stacking +9.98, DT +3.35 under heatwave | Vendor / demand | Field / vendor ops | dh-customer-ops-foodpanda | Flag heatwave demand spike; add rider capacity. |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand's dh-customer-ops channel; PDT-range-test rows are expected, no action._

**Platform Health**

Platform deterioration share — Pandora 13/17 (76%) · Glovo 14/19 (74%) · Talabat 3/6 (50%) · Pedidosya 3/11 (27%) · Efood 0/1 (0%) · Hungerstation 0/1 (0%)
