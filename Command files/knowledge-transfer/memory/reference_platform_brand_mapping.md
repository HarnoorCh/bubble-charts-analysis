---
name: reference_platform_brand_mapping
description: "Canonical country_code+region -> brand/platform CASE, and country-code quirks (t3/t5=Turkey, kr2=Woowa, gv- =Glovo)"
metadata:
  type: reference
---

Canonical brand/platform derivation from `cl.orders` (used across DART + experiment queries):

```sql
CASE
  WHEN o.country_code IN ('at','cz','de2','dk','fi','hu','no','se','sk') OR o.region IN ('Asia') OR o.country_code IN ('t3','t5') THEN 'Pandora'
  WHEN o.country_code IN ('gr','cy')                               THEN 'Efood'
  WHEN o.country_code IN ('ae','bh','eg','iq','jo','kw','om','qa') THEN 'Talabat'
  WHEN o.country_code IN ('sa')                                   THEN 'Hungerstation'
  WHEN o.region IN ('Americas')                                   THEN 'Pedidosya'
  WHEN o.country_code IN ('kr2')                                  THEN 'Woowa'
  WHEN o.country_code LIKE '%gv-%'                                THEN 'Glovo'
END AS brand
```

Quirks: `t3`/`t5` = Yemeksepeti Turkey (normalize to `tr`); `kr2` = Woowa (exclude for non-Woowa cuts); Glovo countries carry a `gv-` prefix (gv-es, gv-ma, gv-hr…). `region` joins from `fulfillment-dwh-production.cl.countries` (values Asia/Americas/MENA/Europe). Related: [[reference_vertical_categories]], [[reference-basequery]].
