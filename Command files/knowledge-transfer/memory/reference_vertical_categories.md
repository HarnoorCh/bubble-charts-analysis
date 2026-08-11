---
name: reference_vertical_categories
description: "vertical_type lives under vendor struct; values + Food/Shops/Darkstores buckets; VERTICAL_CATEGORY routine (main/shops/darkstores)"
metadata:
  type: reference
---

Vertical classification on `cl.orders`.

- Field is **`o.vendor.vertical_type`** (nested under `vendor`, NOT a top-level column).
- Raw values: `restaurants`, `darkstores`, `courier` / `courier_business`, plus grocery/shops types (supermarket, hypermarket, pharmacies, convenience, beauty, electronics, flowers…) and NULL.
- Buckets:
  - **Food** = `restaurants`
  - **Shops / groceries** = vertical not in (restaurants, darkstores, courier, courier_business) and not NULL
  - **Darkstores** = `darkstores` (= **QC / Quick Commerce**)
- BQ routine `log-data-science-staging.hirbod.VERTICAL_CATEGORY` maps raw → exactly `main` (restaurants) / `shops` (groceries) / `darkstores`. Read its body: `bq show --routine --format=prettyjson log-data-science-staging:hirbod.VERTICAL_CATEGORY`.
- Bangladesh (`bd`) does NOT run AGF/WFA (0 `wait_for_assembled` tags). Related: [[reference-adjusted-grocery-flow]], [[reference_platform_brand_mapping]].
