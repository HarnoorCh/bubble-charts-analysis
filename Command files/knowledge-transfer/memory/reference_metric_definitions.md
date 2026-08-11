---
name: reference_metric_definitions
description: "Exact SQL for Seamless timing metrics: EPT/EPB/AAPT/AWT/AVT/TTP/DT/PDT/OD, on-time +-10, stacked on-time, stacking depth, rider reaction time, PET decomposition"
metadata:
  type: reference
---

Seamless metric definitions (all `/60` = minutes; on `cl.orders o` + `UNNEST(deliveries) d ON is_primary`):

- **EPT** `o.estimated_prep_time/60` · **EPB** `o.estimated_prep_buffer/60`
- **AAPT/ATVC** `o.timings.at_vendor_time_cleaned/60` · **AWT** `o.timings.avoidable_wait_time/60` · AVT−AWT = unavoidable at-vendor
- **DT** `o.timings.actual_delivery_time/60` · **PDT** `o.timings.promised_delivery_time/60` (+ `_lower_bound`/`_upper_bound` timestamps)
- **OD** `o.timings.order_delay/60`. Verified identity: `order_delay ≡ actual − promised(median)` (≤1 min for 98.6% of orders). Late = OD>10, early = OD<−10, on-time = |OD|≤10.
- **TTP** = Δ(order_created → rider_picked_up). **To cust. time** = `TIMESTAMP_DIFF(rider_near_customer_at, rider_picked_up_at, MINUTE)` (or field `o.timings.to_customer_time/60`).
- **%on-time (±10)** = `|order_delay| ≤ 10` ÷ valid completed non-preorder. **%stacked on-time** = same, `d.stacked_deliveries > 0`.
- **Stacking %** = `d.stacked_deliveries >= 1`. `stacked_deliveries` counts ADDITIONAL deliveries (0=none, 1=double, 2=triple).
- **%w/ buffer** = % priced by the model (`estimated_prep_buffer > 0`; vs fixed OPS EPT).
- **Rider reaction time** (true notify→accept gap) = `d.timings.rider_reaction_time` (~5.8s). NOT `rider_accepting_time`/`dispatching_time` (~510s, broader queue measures).
- **PET** must be computed per-order then averaged (not from marginal AWT/AVT). Decomposition: PET = X·TTP + Y·ΔAWT + Z·Δ(AVT−AWT). Related: [[reference-basequery]], [[reference_dart_dt45_qc]].
