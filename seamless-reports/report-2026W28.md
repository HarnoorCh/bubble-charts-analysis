# Seamless Weekly Anomaly Report — 2026W28 (Jun 30 – Jul 6) vs 2026W27

## Table 1: Primary KPIs

| Brand | Market | PET | PoP | %on-time | PoP | DT>45 | PoP |
|---|---|---|---|---|---|---|---|
| Hungerstation | sa | 12.35 | 🚀 -0.99 | 96.99 |  | 9.38 | 🚀 -3.02 |
| Pandora | bd | 10.15 | ⚠️ +1.47 | 93.68 |  | 46.68 | ⚠️ +13.07 |
| Glovo | gv-ro | 6.54 | 🚀 -0.49 | 97.49 |  | 15.35 | 🚀 -2.45 |
| Glovo | gv-ma | 6.35 |  | 98.32 |  | 6.95 | 🚀 -2.59 |
| Glovo | gv-it | 6.18 |  | 98.97 |  | 8.16 | 🚀 -1.55 |
| Pandora | hu | 7.08 | 🚀 -0.71 | 97.36 |  | 14.80 | 🚀 -7.02 |
| Glovo | gv-pt | 6.74 | 🚀 -0.38 | 97.41 |  | 14.24 | 🚀 -2.47 |
| Pandora | cz | 6.51 | 🚀 -0.41 | 97.87 |  | 12.27 | 🚀 -4.21 |
| Pandora | at | 5.97 | 🚀 -0.91 | 98.16 |  | 11.92 | 🚀 -6.96 |
| Pandora | mm | 7.56 |  | 97.22 |  | 26.28 | 🚀 -1.21 |

## Table 2: Diagnostic KPIs

| Brand | Market | TTP | PoP | DT | PoP | To cust. time | PoP |
|---|---|---|---|---|---|---|---|
| Pandora | bd | 23.45 | ⚠️ +3.21 | 40.82 | ⚠️ +2.15 | 18.45 | ⚠️ +1.29 |
| Hungerstation | sa | 20.12 | 🚀 -1.88 | 32.10 | 🚀 -2.56 | 14.23 | 🚀 -0.78 |
| Glovo | gv-ro | 16.78 | 🚀 -0.72 | 30.45 | 🚀 -1.95 | 16.12 | 🚀 -0.52 |

## Reasoning

- **Hungerstation SA** improved significantly: PET down 0.99 min (faster pickup), DT>45 down 3.02pp (fewer long deliveries). Both rider efficiency and vendor prep time tightened.
- **Pandora BD** degraded sharply: PET +1.47 min and DT>45 +13.07pp indicate vendor prep slowdown + longer delivery times. TTP and DT both worsened, suggesting demand surge or vendor capacity constraints.
- **Glovo & Pandora Core EU** show consistent improvement in DT>45 across multiple markets (Italy, Portugal, Romania) — tighter dispatch window and faster delivery cycles.
- **Pandora Asia** (MM) maintained high DT>45 baseline (~26%) but improved PoP — typical of restaurant-heavy markets with structural longer times.

## Actions

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| Pandora \| bd | PET +1.47 min, DT>45 +13.07pp; TTP ↑, DT ↑ | Vendor / demand | Field ops | dh-customer-ops-pandora | Investigate vendor BD prep-time spike; check for demand surge or staffing shortfall. |
| Hungerstation \| sa | PET -0.99 min, DT>45 -3.02pp (improvement) | — | — | — | _No action; improvement noted._ |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand's dh-customer-ops channel; PDT-range-test rows are expected, no action._

## Platform Health

**Deterioration share — Pandora 1/12 (8%) · Glovo 0/8 (0%) · Talabat 0/5 (0%) · Hungerstation 0/1 (0%) · Efood 0/2 (0%) · Pedidosya 0/6 (0%).**

---

**Report generated:** 2026-07-13  
**Data window:** 2026W27 → 2026W28 (primary); last 4 weeks in trend analysis
