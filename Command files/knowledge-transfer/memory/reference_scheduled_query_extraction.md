---
name: reference_scheduled_query_extraction
description: "Extract the SQL behind a BigQuery scheduled query (Data Transfer transfer config)"
metadata:
  type: reference
---

BigQuery scheduled queries are Data Transfer Service "transfer configs", stored in the project they were created in (NOT necessarily your default `dhub-data-commune`).

```bash
# find it (loop over candidate projects + locations us,eu)
bq ls --transfer_config --project_id=PROJECT --transfer_location=us
# extract the SQL
bq show --format=prettyjson --transfer_config <CONFIG_RESOURCE_NAME> \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['params']['query'])"
```

Example: `2026-06-10_PT_pelican_shops_global` lived in `logistics-customer-staging` (location `us`). Related: [[reference_bigquery_ops]].
