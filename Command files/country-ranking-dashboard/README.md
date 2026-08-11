# Country Ranking Dashboard

Self-contained, offline HTML dashboard that ranks Delivery Hero countries by a
**weighted rank-sum** over KPI "signals" you toggle live. Every signal has a
direction (higher/lower = better) and a weight; lowest total score = best.
All re-ranking happens client-side — toggling never re-queries BigQuery.

Mirrors the build idiom in `../talabat_jump_build.py` (single `bq` scan →
data inlined into one HTML file → Chart.js from CDN).

## Quick start

```bash
cd /Users/harnoor.chahal/ai/country-ranking-dashboard
python3 extract_history.py        # (re)build the "my query history" index
python3 build_dashboard.py        # one BigQuery scan -> country_ranking_dashboard.html
open country_ranking_dashboard.html
```

In the browser:
- **Ranking tab** — tick/untick signals, flip direction, change weights, pick a
  Top-N for the bar chart. The table + chart re-rank instantly. Rank #1 is
  badged `best`.
- **My query history tab** — searchable list of your past `bq query` calls
  (from Claude transcripts, saved `.sql`, and memory references). Copy any SQL,
  or use the shown command to promote a per-country query into a ranking signal.

## Files

| File | Purpose |
|------|---------|
| `build_dashboard.py` | Assembles the combined per-country SQL from the catalog, runs it, merges external + custom signals, writes the HTML. |
| `kpi_catalog.json` | **The signal catalog** — single source of truth for both the SQL columns and the JS signals. Edit here to add/change built-in signals. |
| `signals_external.json` | Static per-country signals (currently `training_min` from the training-time sheet), merged by `country_code`. |
| `extract_history.py` | Scans transcripts / `.sql` / memory → `query_history.json`. |
| `query_history.json` | Generated history index for the browser + `--add-history`. |
| `country_ranking_dashboard.html` | The generated, shareable artifact. |

## Tuning

Constants at the top of `build_dashboard.py`:
- `WINDOW_DAYS` (default 30) — analysis window.
- `MIN_THRESHOLD` (default **1000**) — min valid orders for a country to be
  ranked. Raise to 10000 to drop small/test markets (e.g. `de2`, `t5`, `fi`),
  matching the original manual analysis. The active value is shown in the
  dashboard header.
- `BASE_TABLE` — `fulfillment-dwh-production.cl.orders`.

### Adding a built-in signal
Add an entry to `kpi_catalog.json`:
- `type:"ratio"` → `"expr":"SAFE_DIVIDE(COUNTIF(<num>), COUNTIF(<den>)) * 100"`
- `type:"average"` → `"expr":"AVG(<expr>)"`
The expression may reference any column projected in `base_cte()` (`dt_min`,
`pdt_min`, `stacks`, `rider_reaction_time`, `ept_min`, `awt_min`, `avt_min`,
`rider_late_min`, `created_to_pu`, `vertical_type`). Then rebuild.

KPI definitions follow DART-v1 (`../Command files/DART-v1.md`) and the base
query (`reference_basequery.md`). Signals needing extra joins (full PET,
`%w/buffer`, DT>45 QC darkstores-only, EPT model/fixed mix) are intentionally
deferred to keep v1 a single scan.

### Adding one of YOUR past queries as a signal
For a history query that returns `country_code` + one numeric column:

```bash
python3 build_dashboard.py --add-history <id> --value-col <col> \
    --dir lower --weight 1 --label "My metric" --group Custom --fmt pct2
```

This runs that query as a separate `bq` job, joins it by `country_code`,
persists it into `kpi_catalog.json` as a `type:"custom"` signal (so future
rebuilds keep it), and rebuilds. The exact command is shown next to each
compatible query in the history browser.

## Notes / caveats
- Country codes are shown raw (anonymized; `t3`, `gv-es`, `kr2`, … are not ISO).
  `kr2` (Woowa) is excluded in `base_cte()`, per DART.
- A country missing a value for an active signal is penalized to worst-rank for
  that signal (not dropped from the board).
- Scoring is **rank-sum**, so it's ordinal — it ignores the *magnitude* of gaps
  between countries. Good for robust shortlists, not for precise trade-offs.
- Refresh `signals_external.json` (training time) later via the google-workspace
  `gws` CLI against sheet `1dtFKiEqeuUGygOl2LSsQyHG3pzvsEd2nm1F9z1mI7_4`.
</content>
</invoke>
