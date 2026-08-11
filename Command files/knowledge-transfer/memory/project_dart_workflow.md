---
name: project_dart_workflow
description: "DART /run-seamless-analysis full workflow (KPIs, determinism, sequence, delivery, scheduler, artifacts) + DART-v2 skill/repo"
metadata:
  type: project
---

**DART** = `/run-seamless-analysis`, the weekly Seamless anomaly-detection report. Spec: `/Users/harnoor.chahal/ai/Command files/DART-v1.md`. Reports → `/Users/harnoor.chahal/ai/seamless-reports/report-<ISO_WEEK>.md`; logs in `seamless-reports/logs/`.

- **Primary KPIs (Table 1):** PET, %on-time, %stacked on-time, DT>45. **Diagnostic (Table 2):** TTP, AWT, DT, %stacked, Rider late%, To cust. time, %w/ buffer. Thresholds: PET 0.3, %on-time 1.0pp, %stacked 1.5pp, DT>45 1.0pp; prune a column if all selected |WoW| ≤ 0.3.
- **Determinism (outside the model):** WoW = round each week to 2dp THEN subtract. Selection ≤4 markets/platform, ~7 total, deteriorations first. priority = severity × volume_weight × platform_factor; platform_factor = 1 + 0.5·(deteriorating_eligible/eligible); "eligible" = markets that fired a flag (not the 100k volume cutoff). Validate by reconstructing the prior week from the same snapshot and diffing the saved report.
- **Sequence:** Step 0 idempotency **BYPASSED** (always re-run live, overwrite — the "MBR-suspect" incident re-served a substituted report forever) → Query 1 (brand×country×week, **INTERVAL 35 DAY**/4-week window; ~56 GB/~$0.28) → Python engine → conditional Query 3 (EPT breakdown, only if a flagged market EPT WoW > +1 min) → optional Query 2 (PDT) → Step 2b external context (holidays via officeholidays.com WebFetch; WebSearch org-blocked; validity over completeness) → render → save → deliver.
- **Delivery:** verbatim to 3 Slack DMs — Harnoor `U036E4LSTCP`, Daniel Rüdiger `U4QNW0MJ7`, Nicolò Luti `U0710JS2BPZ` (personal copy may omit Platform Health). `@Claude` bot send path drops markdown tables.
- **Scheduler:** `scripts/run-seamless-analysis.sh` via launchd `com.harnoor.seamless-analysis.plist`, every 2h Mon 10:00→Wed 22:00 (sleep workaround — launchd doesn't wake the Mac; runs ONE coalesced catch-up on wake). Dedup is **provenance-based** (`seamless-reports/.state/done-<WEEK>.ok` written only after a live run + successful sends) — do NOT swap for an existence check on the report file; that skip IS the sleep deduplicator.
- **Freshness artifacts (don't misattribute):** Americas timezone settling on newest week; `%w/ buffer` ~15pp drop = `_ds_map_orders_to_preptime_code_versions` not backfilled yet.
- **Cost:** ~13M tokens / ~$50 per full weekly run (~$200/mo), overwhelmingly cache-read.

**DART-v2** = config-driven shareable skill at `/Users/harnoor.chahal/ai/dart/`, repo **github.com/deliveryhero/dart-seamless** (internal, `main`). Files: SKILL.md, engine.md, config.example.yaml, README.md/DART-v2.md. Axes: KPIs (keys pet/on_time/on_time_stacked/dt45), Frequency (daily/weekly/monthly), Audience (Slack DMs+channels). Confluence: https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/1729070069

Related: [[reference_dart_dt45_qc]], [[reference_metric_definitions]], [[feedback_slack_table_format]].
