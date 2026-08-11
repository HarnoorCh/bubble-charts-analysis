---
name: reference_bigquery_ops
description: "How to run bq jobs at DH: billing project dhub-data-commune, dry-run cost, slot contention, macOS notes"
metadata:
  type: reference
---

Running BigQuery at Delivery Hero.

- Query with the `bq` CLI: `bq query --use_legacy_sql=false --format=csv --max_rows=<N> < q.sql` (CSV for big aggregations, `--format=prettyjson` for small comparisons).
- **Billing project:** production `fulfillment-dwh-production` DENIES job creation (read-only). Run jobs with default **`--project_id=dhub-data-commune`**. Jobs run in reservation `dh-gsre-finance:US.datacommune`, frequently saturated — a job can sit `PENDING` 10+ min waiting for slots (not a failure). Poll `bq show --format=prettyjson -j <jobid>` → `status.state`. **macOS has no `timeout` command.**
- **Always dry-run:** `bq query --use_legacy_sql=false --dry_run < q.sql`. GOTCHA: `DECLARE … DEFAULT current_date()` variables defeat partition pruning in dry-run (reports whole-table scan) — strip DECLAREs / inline literal dates for a true estimate. Use regex word boundaries when substituting short tokens (`\ballo\b` so `allo` doesn't clobber `allocation`).
- Never run an expensive query without explicit OK — see [[feedback_working_style]].
- `cl.orders` schema reference: `/Users/harnoor.chahal/Projects/data-platform-product/.claude/skills/data-analyst/schema_reference.md`. Related: [[reference-basequery]].
