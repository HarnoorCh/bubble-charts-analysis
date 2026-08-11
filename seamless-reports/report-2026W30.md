# Seamless Weekly Anomaly Report — 2026W30 (2026-07-27 – 2026-07-26) vs 2026W29

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 | WoW |
|---|---|---|---|---|---|---|---|---|---|
| Glovo | gv-kz | 13.90 | +1.80 | 59.80 | -2.10⚠️ | n/a | n/a | 22.78 | +1.50⚠️ |
| Talabat | eg | 11.66 | +0.80 | 81.82 | +0.90 | n/a | n/a | 8.10 | +0.30 |
| Glovo | gv-ng | 10.34 | +1.20 | 61.76 | -1.80⚠️ | n/a | n/a | 12.71 | +0.90 |



**Diagnostic KPIs**

| Brand | Market | DT | WoW |
|---|---|---|---|
| Glovo | gv-kz | 35.48 | +1.80 |
| Talabat | eg | 25.77 | +0.80 |
| Glovo | gv-ng | 29.04 | +1.20 |


**Reasoning**

- Glovo KZ seeing DT inflation (+1.8 min) with on-time pct drop (-2.1pp) → demand spike or network congestion.
- Talabat EG and Glovo NG stable week-over-week, minor delivery time shifts within normal variance.
- Stacking rates flat across flagged markets.

**Actions**

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| Glovo / gv-kz | DT ↑ w/ on-time ↓ | Vendor / demand | Field ops | dh-customer-ops-glovo | Monitor vendor SLA; check order volume % YoY. |
| Talabat / eg | Flat w/ minor DT ↑ | Baseline | — | — | No action required. |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand's dh-customer-ops channel; PDT-range-test rows are expected, no action._

**Platform Health**

Talabat 0/5 (0%) · Hungerstation 0/1 (0%) · Pandora 0/8 (0%) · Glovo 1/16 (6%) · Pedidosya 0/9 (0%) · Efood 0/2 (0%)
