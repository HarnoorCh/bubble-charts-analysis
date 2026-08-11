---
name: project_insights_report
description: Latest /insights usage report (generated 2026-06-17); keep until /insights is run again
metadata: 
  node_type: memory
  type: project
  originSessionId: 1634235a-af3c-46c3-ab1b-24598e7cdf44
---

Latest Claude Code usage insights report, generated 2026-06-17. Keep this until the next time the user runs `/insights`, then overwrite with the new one.

- HTML: `/Users/harnoor.chahal/.claude/usage-data/report-2026-06-17-173038.html`
- Span: 53 sessions total (28 analyzed), 255 messages, 2026-05-07 to 2026-06-17.

**Key pattern:** User drives complex data-analysis-to-report workflows via rapid iterative refinement, staying engaged enough to interrupt and correct Claude the moment it drifts or fabricates.

**Top project areas:** BigQuery data analysis & experimentation (11), automated KPI/anomaly reporting pipelines (5), OKR & Confluence doc generation (5), Slack communication & knowledge lookup (4), workshop & strategy facilitation (3).

**What works:** End-to-end experiment dashboards (query → hosted, auto-refreshing artifact), iterative BigQuery deep-dives with schema verification + saved interpretation memory, analysis-to-Slack delivery loop (DMs to Alina Kim, Daniel Rüdiger).

**Friction (Claude side):** Acting on unverified assumptions / fabricated data (e.g. invented "Q3 Markets" label, missed Glovo on PDT wins slide), buggy first-pass outputs (all-NULL arms from filter bug, %stacked omitted, AND-ed prediction bounds), environmental blockers (Cloudflare auth on /budget, over-budget API, socket errors cutting sessions).

**Suggested CLAUDE.md additions:** data-integrity (verify before generating, never fabricate), BigQuery (verify schema, parse output carefully, per-dimension columns), confirm file/page location & scope before creating, persist reporting/formatting conventions (KR nesting, quarter scoping, status color classifier — pale yellow = on-track not red).

**Features to try:** Custom Skills (codify weekly KPI pipelines — relates to [[project_domain_update_prep]] and the DART workflow), Hooks (post-query validation), MCP servers (BigQuery/Sheets for grounded access).

Related: [[reference_dart_dt45_qc]], [[feedback_slack_table_format]], [[feedback_folder_creation]].
