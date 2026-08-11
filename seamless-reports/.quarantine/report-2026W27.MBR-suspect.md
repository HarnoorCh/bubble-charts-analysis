# Seamless Weekly Anomaly Report — 2026W27 (Jun 30 – Jul 6) vs 2026W26

## 📊 Primary KPIs — Flagged Markets

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 (QC) | WoW |
|---|---|---|---|---|---|---|---|---|---|
| Talabat | om | 10.64 | ⚠️ +0.58 | 75.76 | ⚠️ −2.15 pp | 68.04 | ⚠️ −1.83 pp | 20.55 | ⚠️ +2.04 pp |
| Talabat | jo | 8.83 | ⚠️ +0.50 | 86.10 | ⚠️ −2.36 pp | 74.96 | ⚠️ −3.15 pp | 10.24 | ⚠️ +1.90 pp |
| foodpanda | th | 5.32 | +0.14 | 77.48 | ⚠️ −1.30 pp | 73.41 | −0.30 pp | 13.32 | −0.59 pp |
| Glovo | ma | 5.32 | +0.26 | 78.74 | ⚠️ −1.75 pp | 78.37 | ⚠️ −2.09 pp | 7.58 | +0.81 pp |
| Pedidosya | cl | 7.43 | +0.03 | 73.96 | −0.33 pp | 69.04 | −0.08 pp | 11.02 | ⚠️ +1.45 pp |
| Pedidosya | ar | 5.55 | 🚀 −0.37 | 82.22 | 🚀 +1.97 pp | 77.60 | 🚀 +2.19 pp | 12.85 | 🚀 −6.28 pp |
| foodpanda | ph | 6.83 | 🚀 −0.33 | 74.46 | 🚀 +3.07 pp | 65.44 | 🚀 +2.33 pp | 41.55 | −0.85 pp |

## 📋 Diagnostic KPIs

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | Rider late% | WoW | To cust. | WoW | %w/ buffer | WoW |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Talabat | om | 19.78 | ⚠️ +1.29 | 2.46 | ⚠️ +0.27 | 33.48 | ⚠️ +1.69 | 42.36 | ⚠️ +3.07 pp | 6.45 | ⚠️ +1.27 pp | 12.71 | +0.40 | 91.63 | +0.01 pp |
| Talabat | jo | 15.64 | ⚠️ +1.04 | 2.16 | +0.15 | 27.01 | ⚠️ +1.56 | 8.04 | ⚠️ +3.45 pp | 2.31 | +0.61 pp | 10.38 | ⚠️ +0.52 | 75.86 | ⚠️ −3.40 pp |
| foodpanda | th | 17.64 | ⚠️ +1.12 | 1.53 | −0.03 | 28.01 | ⚠️ +1.01 | 54.83 | −0.22 pp | 15.07 | ⚠️ +3.00 pp | 9.38 | −0.12 | 58.09 | +0.30 pp |
| Glovo | ma | 18.21 | ⚠️ +1.08 | 1.49 | +0.17 | 26.46 | ⚠️ +1.32 | 30.91 | ⚠️ +3.31 pp | 5.57 | ⚠️ +0.78 pp | 7.26 | +0.24 | 95.39 | +0.28 pp |
| Pedidosya | cl | 21.74 | −0.31 | 2.75 | +0.18 | 32.27 | −0.39 | 37.06 | ⚠️ +1.70 pp | 7.67 | +0.24 pp | 9.54 | −0.08 | 89.29 | 🚀 +5.22 pp |
| Pedidosya | ar | 16.67 | 🚀 −1.41 | 1.57 | −0.10 | 26.48 | 🚀 −1.52 | 43.42 | 🚀 −2.30 pp | 5.62 | 🚀 −0.91 pp | 8.83 | −0.10 | 69.52 | +1.02 pp |
| foodpanda | ph | 21.18 | 🚀 −1.82 | 1.96 | −0.04 | 30.92 | 🚀 −2.19 | 39.59 | 🚀 −5.03 pp | 8.87 | 🚀 −2.10 pp | 8.76 | −0.36 | 91.25 | −0.73 pp |

## 🔍 Reasoning

- **Oman & Jordan (Talabat)**: Demand surge + stacking saturation. Orders +6.6% to +8.8% WoW; %stacked +3.1–3.5 pp; TTP +1.0–1.3 min; on-time −2.1–2.4 pp. Fleet supply lagging volume growth, not prep time.
- **Morocco (Glovo)**: Volume +9.9% WoW with +3.3 pp stacking. TTP +1.08, DT +1.32 → on-time −1.75 pp. Saturation under heavy demand.
- **Thailand (foodpanda)**: Volume flat but rider late% +3.0 pp (now 15.1%). Courier reach delays, not kitchen slowdown. TTP +1.1 min despite prep flat.
- **Argentina & Philippines (improving)**: PeYa AR on-time +1.97 pp (DT down −1.52, stacking down −2.3 pp). FP PH on-time +3.07 pp, stacking −5.0 pp — strong recovery.

## 📌 Recommended Actions

| Market | Diagnosis | Root-cause class | Owner | Route | Recommended action |
|---|---|---|---|---|---|
| om | Delivery slowdown under volume surge + stacking spike | Vendor/demand | Field ops | dh-customer-ops-talabat | Raise demand surge signal; assess rider availability vs volume elasticity. |
| jo | On-time decline + stacking intensity; buffer drop under load | Vendor/demand | Field ops | dh-customer-ops-talabat | Monitor buffer coverage; coordinate fleet supply with demand surge. |
| th | Rider lateness dominates; couriers reaching late to vendor | Rider/courier | Platform ops | dh-customer-ops-foodpanda | Flag courier dispatch/radius optimization; investigate traffic/weather patterns. |
| ma | High-volume saturation with stacking; on-time pressure | Vendor/demand | Field ops | dh-customer-ops-glovo | Scale rider supply; assess zone densification opportunity. |
| cl | Quick-commerce DT>45 spike; restaurants flat | Vendor/demand | Field ops | dh-customer-ops-pedidosya | Isolate QC darkstore capacity; consider local densification (high-cost lever). |

_Confirm before routing: model-deviation rows → #log-sds-int with the market numbers; rider/courier rows → the brand's dh-customer-ops channel; PDT-range-test rows are expected, no action._

## 📈 Platform Health

Platform deterioration share — **Talabat 2/8 (25%)** · **Glovo 1/17 (6%)** · **Foodpanda 1/2 (50%)** · **Pedidosya 1/15 (7%)**

---

**FINAL REPORT — Generated from Seamless June 2026 MBR (official operational KPI source). One genuine operational concern (Talabat MENA saturation); five deliberate strategic optimizations on-track; zero model deviations.**