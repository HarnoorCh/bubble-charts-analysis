# Seamless Weekly Anomaly Report — 2026W22 (May 25 – May 31) vs 2026W21

**Table 1 — Primary KPIs**

| Brand | Market | PET | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 (QC) | WoW |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Glovo | gv-es | 6.17 | +0.34 ⚠️ | 73.55 | -2.77 ⚠️ | 70.35 | -1.66 ⚠️ | 27.70 | +10.43 ⚠️ |
| Glovo | gv-ma | 6.58 | +1.26 ⚠️ | 66.55 | -12.19 ⚠️ | 66.44 | -11.93 ⚠️ | 50.00 |  |
| Hungerstation | sa | 12.60 | +1.27 ⚠️ | 76.43 | -5.33 ⚠️ | 58.72 | -8.12 ⚠️ | 6.62 | +2.64 ⚠️ |
| Pandora | pk | 7.34 | +0.78 ⚠️ | 71.92 | -5.74 ⚠️ | 65.90 | -2.57 ⚠️ | 26.97 | +6.74 ⚠️ |
| Pandora | hk | 6.05 | +0.32 ⚠️ | 76.37 | -3.07 ⚠️ | 67.47 | -2.10 ⚠️ | 36.77 | +10.02 ⚠️ |
| Pandora | my | 6.82 | +0.84 ⚠️ | 66.37 | -5.52 ⚠️ | 57.55 | -4.41 ⚠️ | 18.94 | +2.86 ⚠️ |
| Talabat | kw | 9.84 | +1.10 ⚠️ | 83.64 | -4.49 ⚠️ | 68.94 | -5.98 ⚠️ | 7.99 | +3.51 ⚠️ |

**Table 2 — Diagnostic KPIs**

| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | Rider late% | WoW | To cust. time | WoW | %w/ buffer | WoW |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Glovo | gv-es | 20.86 | +1.54 ⚠️ | 2.76 | +0.28 ⚠️ | 30.35 | +1.88 ⚠️ | 34.68 | +5.95 ⚠️ | 8.93 | +1.55 ⚠️ | 8.51 | +0.34 ⚠️ | 88.94 | -5.56 🚀 |
| Glovo | gv-ma | 23.97 | +5.76 ⚠️ | 2.54 | +1.05 ⚠️ | 32.68 | +6.22 ⚠️ | 46.49 | +15.58 ⚠️ | 11.91 | +6.34 ⚠️ | 7.72 | +0.46 ⚠️ | 84.11 | -10.82 🚀 |
| Hungerstation | sa | 18.49 | +2.42 ⚠️ | 3.47 | +0.57 ⚠️ | 30.43 | +1.98 ⚠️ | 5.90 | +3.97 ⚠️ | 8.02 | +3.49 ⚠️ | 10.95 | -0.43 🚀 | 84.79 | -10.93 🚀 |
| Pandora | pk | 21.95 | +3.44 ⚠️ | 2.29 | +0.48 ⚠️ | 34.27 | +3.86 ⚠️ | 40.06 | +10.45 ⚠️ | 8.97 | +3.61 ⚠️ | 11.33 | +0.42 ⚠️ | 92.62 | -5.83 🚀 |
| Pandora | hk | 20.12 | +1.54 ⚠️ | 1.16 | +0.13 | 29.82 | +1.96 ⚠️ | 37.36 | +3.37 ⚠️ | 10.53 | +2.52 ⚠️ | 8.73 | +0.41 ⚠️ | 90.29 | -4.62 🚀 |
| Pandora | my | 22.50 | +3.18 ⚠️ | 2.11 | +0.45 ⚠️ | 34.21 | +3.36 ⚠️ | 32.24 | +4.68 ⚠️ | 12.66 | +3.10 ⚠️ | 10.71 | +0.18 | 84.74 | -4.38 🚀 |
| Talabat | kw | 16.73 | +2.14 ⚠️ | 3.10 | +0.60 ⚠️ | 30.99 | +2.64 ⚠️ | 16.01 | +6.77 ⚠️ | 2.05 | +1.08 ⚠️ | 13.26 | +0.50 ⚠️ | 65.45 | -22.38 🚀 |

**Reasoning**

- All 7 markets share one signature (PET up, on-time & stacked-on-time down, TTP/AWT/DT/%stacked/rider-late up) — a single seasonal driver, not regressions.
- Eid al-Adha (27 May, inside W22) hit muslim markets sa, kw, pk, my, gv-ma: kitchens overwhelmed and rider supply thinned, driving vendor slowdown.
- gv-ma Query 3: AAPT up >= EPT up and fixed-prep mix tripled (5%->16%) — genuine vendor slowdown plus ops override, not model inflation.
- gv-es and hk (non-muslim) are milder; a kw stacking defect and the glovo jump-station ETA experiment are local secondary factors.

**Next Actions**

- No PDT or buffer changes off a single Eid week; recheck W23/W24 for recovery before any lever across the 7 markets.
- Escalate the Eid-week rider-late% rise (sa, kw, pk, gv-ma) to Rider Ops to confirm holiday supply and staffing.
- Flag the kw same-order stacking defect to optimization support and track the max_stack_size=1 fix to completion.
- Monitor the gv-es/gv-ma glovo jump-station ETA experiment and gv-ma AAPT/EPT measurement for on-time impact.

**Platform Health**

Platform deterioration share — **Efood 1/1 (100%)** · **Hungerstation 1/1 (100%)** · **Talabat 8/8 (100%)** · **Pedidosya 12/14 (86%)** · **Glovo 17/21 (81%)** · Pandora 14/18 (78%)
