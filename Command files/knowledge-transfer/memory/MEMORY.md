# Memory Index

Portable Claude memory for Harnoor Chahal (CPL / Seamless, Delivery Hero). Distilled from 47 Claude Code sessions (Jun–Jul 2026) + curated memories. One line per memory; open the file for the full fact. See `../CLAUDE_KNOWLEDGE.md` for the same knowledge as one consolidated doc.

## Reference — data, queries, tooling
- [Base query (/basequery)](reference_basequery.md) — reference orders/timings SQL on cl.orders; pick columns per question
- [Metric definitions](reference_metric_definitions.md) — exact SQL for EPT/EPB/AAPT/AWT/DT/PDT/OD, on-time ±10, stacking, PET
- [BigQuery ops](reference_bigquery_ops.md) — billing project dhub-data-commune, dry-run cost, slot contention, macOS notes
- [Platform/brand mapping](reference_platform_brand_mapping.md) — country_code+region → brand CASE; t3/t5=Turkey, kr2=Woowa, gv-=Glovo
- [Vertical categories](reference_vertical_categories.md) — vendor.vertical_type values; Food/Shops/Darkstores; VERTICAL_CATEGORY routine
- [DT>45 metric](reference_dart_dt45_qc.md) — DART primary KPI renamed "DT>45", now ALL verticals (was darkstores/QC)
- [Adjusted Grocery Flow](reference_adjusted_grocery_flow.md) — AGF=WFA; identify via `"wait_for_assembled" IN UNNEST(tags)`
- [tracking_api_logs](reference_tracking_api_logs.md) — per-ping ETA-history table; fields, timezone, ETA-jump usage
- [TAPI order deepdive](reference_tapi_order_deepdive.md) — single-order tracking SQL: every snapshot + stage + near_dropoff/delivered
- [CPU / Δ CPU](reference_cpu_delta_cpu.md) — Committed Pick-Up time; Δ CPU ≤ ~4 min gates stacking (DTM feature)
- [Scheduled query extraction](reference_scheduled_query_extraction.md) — pull SQL from a BigQuery Data Transfer config
- [gws CLI](reference_gws_cli.md) — Google Workspace read/write Sheets/Slides + auth token refresh block
- [Okra MCP](reference_okra_mcp.md) — OKR-data MCP server setup (--scope user, restart session)
- [LiteLLM budget](reference_litellm_budget.md) — request-budget-increase command, $200 cap, /budget skill
- [Dashboards & hosting](reference_dashboards_hosting.md) — self-contained HTML+Chart.js; GCS bucket sharing; ngrok
- [People & channels](reference_people_channels.md) — key Slack IDs & channels across CPL/Seamless

## Projects — experiments, workflows, findings
- [DART workflow](project_dart_workflow.md) — /run-seamless-analysis full pipeline + DART-v2 skill/repo
- [Talabat Jump experiment](project_talabat_jump_experiment.md) — Exp 538, 3-arm T1/T2/Control; T1 cuts jump_rate; Control-ID gotcha
- [Pelican shops experiment](project_pelican_shops.md) — PT-prefix experiment; scan cost fixed by source reads
- [AR darkstores EPT tests](project_ar_darkstores_ept_tests.md) — P1/P2 were deliberate EPT-inflation tests; P3 baseline
- [Country ranking + hackathon](project_country_ranking_hackathon.md) — 66-country rank dashboard + "PDTs are cool" (Δ CPU, GMV BOE)
- [Cycle Review](project_cycle_review.md) — monthly review workflow; QU-month skips; deck/sheet IDs
- [Seamless Domain Update prep](project_domain_update_prep.md) — bi-weekly page-history ledger + leads
- [Biweekly update](project_biweekly_update.md) — odd=KPI / even=Initiatives Confluence page; #cpl-ops-perf-seamless
- [EPT quantile switchback](project_ept_quantile_switchback.md) — Ege's process; Superset 480 + operational_config.yaml; OOO routing
- [OKR state](project_okr_state.md) — active quarter Q2 2026; Harnoor owns one KR; Rose-sync alerts
- [Insights report](project_insights_report.md) — latest /insights usage report (2026-06-17)
- [DT Analysis - Image with DT.png](project_dt_analysis.md) — weekly table; DT drop 2020W14-16 (COVID)

## Feedback — how to work
- [Working style](feedback_working_style.md) — no expensive queries w/o OK; "just the query"=verbatim SQL; honesty; "Mio"; mean+p50
- [Slack table format](feedback_slack_table_format.md) — default comparison-style tables (Δ column/row, emoji, bold standouts)
- [Presentation/MBR format](feedback_presentation_format.md) — Choice-model verdicts, trend columns, table-left/analysis-right
- [Folder creation restriction](feedback_folder_creation.md) — new folders only inside /Users/harnoor.chahal/ai/
