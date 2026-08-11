---
name: feedback-slack-table-format
description: "Default markdown table formatting style for all Slack messages — period-over-period comparison style with Δ column/row, emoji indicators on status deltas, and bold standout cells."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: ab9c9af7-4802-48d2-acda-fadc48620e60
---

**Rule:** When drafting any Slack message that includes tabular data, use the comparison-style table formatting documented below as the default.

**Why:** Established 2026-05-28 after the CZ W1-vs-W19 PDT/lateness Slack message in #cpl-sds-int. The user explicitly asked to apply this style to all Slack messages going forward. Originating context was DART-v1.md (`/Users/harnoor.chahal/ai/Command files/DART-v1.md`) — an anomaly-detection agent that produces period-over-period performance summaries.

**How to apply:** Default to this style for Slack messages with comparison tables (week-over-week, period-vs-period, KPI deltas, A/B vs control, etc.). When in doubt, use it. Only deviate if the user asks for something different or if the data isn't comparison-shaped.

## Message structure

1. **Opener** — 1-2 sentence headline framing the problem and the punchline (what changed, what's driving it).
2. **Context line** — single line: country flag emoji + period labels with date ranges + sample size.
   `🇨🇿 CZ • W1 (Dec 29–Jan 4) vs W19 (May 4–10) • 243k vs 260k completed orders`
3. **Tables** (see below)
4. **"What I'm seeing"** paragraph — interpretation of the tables.
5. **"Asks for the team:"** (when sending to a team channel) — bulleted, specific questions. Bold the verbs/topics.

## Table format

Each table gets a bold header with an inline qualitative tagline:

```
**Order delay buckets (OD)**

| Status | W1 | W19 | Δ |
|---|---|---|---|
| On-time (±10m) | 75.94% | 74.14% | 🔴 −1.80 pp |
| Late (OD > 10m) | 13.98% | 17.78% | 🔴 +3.80 pp |
| Early (OD < −10m) | 8.46% | 7.35% | ⚪ −1.11 pp |
```

```
**PDT percentiles (min)** — compressed sharply at the top

| | p25 | p50 | p75 | p90 | p95 |
|---|---|---|---|---|---|
| W1 | 22.58 | 28.93 | 37.93 | 47.90 | 54.40 |
| W19 | 22.60 | 28.93 | 36.92 | 44.63 | 49.57 |
| Δ | +0.02 | 0.00 | −1.01 | **−3.27** | **−4.83** |
```

## Conventions

- **Header tagline**: `**Metric name (units)** — short qualitative tagline` (e.g. "barely moved", "compressed sharply at the top"). Helps the reader scan.
- **Emoji indicators on deltas** (status/bucket tables only): `🔴` for bad change, `🟢` for good change, `⚪` for neutral/negligible. Skip on metric/percentile tables to avoid clutter.
- **Sign characters**: use real `−` (U+2212) not hyphen `-` for negative deltas — reads as a math sign, aligns better.
- **Bold standout values**: bold the two or three cells in a table that carry the story (e.g. the biggest deltas). Don't bold every changed cell.
- **Δ row at bottom** for percentile/metric tables; **Δ column on right** for status/bucket tables.
- **Units in the table title, not in cells** — `(min)` or `(%)` after the metric name; keep cells purely numeric.
- **Period labels as column headers** (W1 / W19, not the dates) — dates live in the context line.
- **First column header**: leave blank for percentile tables where row labels are period names.
- **Consistent decimals** per column for visual alignment.

## Slack rendering notes

- Slack renders markdown tables with `|` delimiters cleanly. Don't escape structural `|`.
- Emoji is the only way to add scannable color since Slack markdown tables can't color individual cells.
- Bold (`**...**`) works inside `|` table cells.
- For richer formatting (right-alignment, true table blocks), Block Kit `table` blocks are available but require the API or Workflow Builder — the standard `slack_send_message` tool only supports markdown.

Related: [[reference-basequery]], [[project-dt-analysis]]. Originating doc: `/Users/harnoor.chahal/ai/Command files/DART-v1.md`.
