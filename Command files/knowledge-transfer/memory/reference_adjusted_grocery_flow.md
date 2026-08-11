---
name: reference-adjusted-grocery-flow
description: How to identify Adjusted Grocery Flow (AGF) / Wait-for-Assembled (WFA) orders in BigQuery cl.orders
metadata: 
  node_type: memory
  type: reference
  originSessionId: d1833b58-50dc-485f-af0e-98cc78e07976
---

**Adjusted Grocery Flow (AGF)** is internally called **Wait for Assembled (WFA)**. In AGF, Hurrier sends the order to the vendor immediately but waits to assign a rider until the vendor fires the `food_is_ready` (FIA) event.

**How to identify AGF orders in `fulfillment-dwh-production.cl.orders`:**

- Primary tag: `"wait_for_assembled" IN UNNEST(tags)` — the `tags` column is `ARRAY<STRING>` on `cl.orders`. This is the authoritative payload tag per Hurrier docs.
- Companion event: `food_is_ready_at` (TIMESTAMP) — populated when the FIA event arrives. ~99% of WFA orders have it; the rest are WFA orders that never fired FIA.

**Example filter:**
```sql
WHERE "wait_for_assembled" IN UNNEST(tags)
```

**Observed concentration (week of 2026-05-19):** supermarket 18.7%, hypermarket 35.3%, shop 99.7%, darkstores 2.1%, convenience 3.5%; near-zero in restaurants.

**Docs:**
- Hurrier - Wait for Assembled Orders: https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGSUPHC/pages/811892841
- Adjusted Grocery Flow - Hurrier V2: https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOG/pages/37696981
- New grocery flow (defines WFA=AGF, FIA terminology): https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOG/pages/37741379

Related: [[reference-basequery]].
