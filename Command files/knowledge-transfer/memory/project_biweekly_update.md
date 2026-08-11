---
name: project_biweekly_update
description: "biweekly-update skill: odd week=KPI page, even=Initiatives; carry forward in LOGCPL; Slack notify #cpl-ops-perf-seamless"
metadata:
  type: project
---

**/biweekly-update** skill — bi-weekly CPL Seamless Confluence page. Get ISO week N (`python3 -c "from datetime import date; print(date.today().isocalendar()[1])"`), PREV = N-2. **N odd → KPI Update page; N even → Initiatives Update page.** Carry forward from the previous same-type page in Confluence space **LOGCPL** (cloudId `deliveryhero.atlassian.net`) via `searchConfluenceUsingCql`, replacing `W{PREV}` references. Post Slack notification to **#cpl-ops-perf-seamless** (`C051L8NRY69`). Known page IDs: W19 KPI 1567424618, W20 Initiatives 1619263928, W21 KPI 1640630636. Note: Initiatives cadence paused after W20 (W22/W24/W26 don't exist) — carried-forward statuses may be stale. Related: [[project_dart_workflow]].
