# Seamless Weekly Anomaly Report — 2026W22 (May 25 – May 31) vs 2026W21

**Table 1 — Primary KPIs**

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 (QC) | WoW |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Glovo | gv-es | 6.17 | +0.34 ⚠️ | 73.55 | -2.77 ⚠️ | 70.35 | -1.66 ⚠️ | 27.70 | +10.43 ⚠️ |
| Glovo | gv-ma | 6.58 | +1.26 ⚠️ | 66.55 | -12.19 ⚠️ | 66.44 | -11.93 ⚠️ |  |  |
| Hungerstation | sa | 12.60 | +1.27 ⚠️ | 76.43 | -5.33 ⚠️ | 58.72 | -8.12 ⚠️ | 6.62 | +2.64 ⚠️ |
| Pandora | pk | 7.34 | +0.78 ⚠️ | 71.92 | -5.74 ⚠️ | 65.90 | -2.57 ⚠️ | 26.97 | +6.74 ⚠️ |
| Pandora | hk | 6.05 | +0.32 ⚠️ | 76.37 | -3.07 ⚠️ | 67.47 | -2.10 ⚠️ | 36.77 | +10.02 ⚠️ |
| Pandora | my | 6.82 | +0.84 ⚠️ | 66.37 | -5.52 ⚠️ | 57.55 | -4.41 ⚠️ | 18.94 | +2.86 ⚠️ |
| Talabat | kw | 9.84 | +1.10 ⚠️ | 83.64 | -4.49 ⚠️ | 68.94 | -5.98 ⚠️ | 7.99 | +3.51 ⚠️ |

**Table 2 — Diagnostic KPIs**

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | Rider late% | WoW | To cust. time | WoW | %w/ buffer | WoW |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Glovo | gv-es | 20.86 | +1.54 ⚠️ | 2.76 | +0.28 ⚠️ | 30.35 | +1.88 ⚠️ | 34.68 | +5.95 ⚠️ | 8.93 | +1.55 ⚠️ | 8.99 | +0.34 ⚠️ | 79.41 | +1.64 ⚠️ |
| Glovo | gv-ma | 23.97 | +5.76 ⚠️ | 2.54 | +1.05 ⚠️ | 32.68 | +6.22 ⚠️ | 46.49 | +15.58 ⚠️ | 11.91 | +6.34 ⚠️ | 8.10 | +0.43 ⚠️ | 95.52 | +0.12 |
| Hungerstation | sa | 18.49 | +2.42 ⚠️ | 3.47 | +0.57 ⚠️ | 30.43 | +1.98 ⚠️ | 5.90 | +3.97 ⚠️ | 8.02 | +3.49 ⚠️ | 11.39 | -0.44 🚀 | 83.61 | +0.64 |
| Pandora | pk | 21.95 | +3.44 ⚠️ | 2.29 | +0.48 ⚠️ | 34.27 | +3.86 ⚠️ | 40.06 | +10.45 ⚠️ | 8.97 | +3.61 ⚠️ | 11.53 | +0.38 ⚠️ | 78.22 | +1.78 ⚠️ |
| Pandora | hk | 20.12 | +1.54 ⚠️ | 1.16 | +0.13 | 29.82 | +1.96 ⚠️ | 37.36 | +3.37 ⚠️ | 10.53 | +2.52 ⚠️ | 9.12 | +0.41 ⚠️ | 80.82 | +1.24 ⚠️ |
| Pandora | my | 22.50 | +3.18 ⚠️ | 2.11 | +0.45 ⚠️ | 34.21 | +3.36 ⚠️ | 32.24 | +4.68 ⚠️ | 12.66 | +3.10 ⚠️ | 9.23 | +0.27 | 79.21 | +1.15 ⚠️ |
| Talabat | kw | 16.73 | +2.14 ⚠️ | 3.10 | +0.60 ⚠️ | 30.99 | +2.64 ⚠️ | 16.01 | +6.77 ⚠️ | 2.05 | +1.08 ⚠️ | 13.71 | +0.49 ⚠️ | 72.36 | -0.36 |

**Reasoning**

- All seven markets share one syndrome: stacking +3.4–15.6pp lifting TTP and DT, pushing DT>45 up and on-time down 2.8–12.2pp.
- gv-ma is worst: AAPT +1.25 (model +1.12, fixed-override mix 5%→16%) confirms genuine vendor slowdown, not model inflation — Query 3 verified.
- Rider late% rose +1.1–6.3pp alongside higher AWT across every market, a dispatch/courier-capacity signal owned by Rider Ops, not vendor prep.
- Deterioration is platform-wide, not market-specific: Talabat and Hungerstation fully degraded, Pandora 14/16 and Glovo 14/17 close behind.

**Next Actions**

- Escalate the stacking surge and rising rider late% across gv-es, gv-ma, pk, hk, my, sa, kw to Rider Ops for dispatch and stacking-config review.
- Validate gv-ma vendor-side slowdown (AAPT +1.25) and fixed-override jump (5%→16%) with DS/ops; treat as field/ops issue, not model recalibration.
- Investigate QC darkstore capacity in gv-es, hk, pk where DT>45 jumped +6.7–10.4pp, breaching quick-commerce SLAs.
- Hold PDT and buffer settings — single-week signal only; revisit those levers solely if degradation persists 4+ consecutive weeks.

**Platform Health**

Platform deterioration share — **Hungerstation 1/1 (100%)** · **Talabat 8/8 (100%)** · **Pandora 14/16 (88%)** · **Glovo 14/17 (82%)** · **Pedidosya 12/15 (80%)** · Efood 1/2 (50%)
