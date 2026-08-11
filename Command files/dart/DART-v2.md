# DART v2 — Deviation Analysis & Resolution Tracker

**DART** is a self-driving logistics analyst for the Seamless domain. It pulls delivery KPIs straight from BigQuery, flags markets that deviated beyond significance thresholds, diagnoses the likely root cause with expert heuristics, recommends the routing/action, and delivers a strict, deterministic report to your Slack audience — on the cadence you choose.

📖 **Background & methodology:** [DART on Confluence (LOGCPL)](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/1729070069/DART+-+Deviation+Analysis+Resolution+Tracker)

What's new in **v2**: DART is now a **shareable Claude Code skill** with three things you configure once — **which KPIs**, **how often**, and **who receives it**.

---

## 📥 Download & install

DART is packaged as a Claude Code skill. "The DART file" is this whole folder:

```
dart/
├── SKILL.md              ← skill entry (wizard + run paths)
├── DART-v2.md            ← this page
├── engine.md             ← the analysis brain (the KPI/SQL/heuristics engine)
├── config.example.yaml   ← the config schema, documented
└── dart.config.yaml      ← YOUR settings (created by the setup wizard; not shipped)
```

**Install** (pick one):
1. **Copy** the `dart/` folder into your skills directory: `~/.claude/skills/dart/` (global) or `<project>/.claude/skills/dart/`.
2. **Symlink** it (how `data-analyst` and `google-workspace` are installed here):
   ```bash
   ln -s /Users/harnoor.chahal/ai/dart ~/.claude/skills/dart
   ```

Restart / reload Claude Code so the `dart` skill registers.

**Prerequisites**
- **BigQuery access** to `fulfillment-dwh-production` (DART uses the `data-analyst` skill / `bq`).
- **Slack MCP connected** (the report is delivered via `slack_send_message`). Only needed if you configure a Slack audience.

---

## 🚀 Use it

1. **Set up once** — say **“set up DART”**. The wizard asks three questions and writes `dart.config.yaml`.
2. **Run it** — say **“run DART”**. DART computes the current period's report, saves it, previews it, and (on your OK) sends it to your audience.
3. **Reconfigure anytime** — say **“reconfigure DART”** to change any of the three settings.

---

## ⚙️ The three configurable items

### 1. Choose KPIs
Pick any subset of the four **Table-1 primary KPIs**. Each has a fixed significance threshold and its own set of diagnostic (Table-2) columns.

| KPI | Config key | Significance threshold | Notes |
|---|---|---|---|
| PET — Pickup Efficiency Time | `pet` | \|Δ\| ≥ 0.3 min | Triggers the EPT fixed-vs-model breakdown (Query 3) on >1 min drift |
| %on-time (±10 min) | `on_time` | \|Δ\| ≥ 1.0 pp | Realized vs promised delivery |
| %on-time for stacked orders | `on_time_stacked` | \|Δ\| ≥ 1.5 pp | Adds stacking-depth diagnostics |
| %orders delivered in over 45 min (DT>45) | `dt45` | \|Δ\| ≥ 1.0 pp | **All verticals** (QC + darkstores + restaurants); read the PoP move, not the absolute level |

Only selected KPIs are computed, flagged, and rendered. Table 2 is pruned to diagnostics relevant to your selection.

### 2. Choose Frequency
The cadence sets the comparison grain (the "period") and the report's date labels.

| Frequency | Compares | Trend window | Period label | Delta wording |
|---|---|---|---|---|
| `daily` | last complete day vs prior day | last 4 days | `2026-07-05` | PoP |
| `weekly` | last complete ISO week vs prior | last 4 weeks | `2026W27` | WoW |
| `monthly` | last complete month vs prior | last 4 months | `2026-07` | PoP |

*"PoP" = period-over-period, the general form of "WoW". Weekly is the default and matches the legacy report exactly.*

### 3. Choose Audience — **yes, this is possible** ✅
Where the finished report is delivered:

| Target | Config | Status |
|---|---|---|
| **Just you** (Slack DM to self) | your Slack user ID in `slack_user_ids` | ✅ Works today |
| **Specific people** (Slack DMs) | their Slack user IDs in `slack_user_ids` | ✅ Works today |
| **Slack channel(s)** | channel IDs in `slack_channel_ids` | ✅ Works today (a channel is already used for the bi-weekly automation) |
| **Email** | — | ⏳ **Not wired in v2.** Feasible, but needs an email sender (SMTP or an email API) + a stored secret. Documented as the next extension. |

Delivery uses the Slack MCP `slack_send_message` (by `channel_id` for channels, by user ID for DMs) — the same mechanism DART v1 already uses to DM three people. Get a **user ID** from a Slack profile → "Copy member ID"; a **channel ID** starts with `C`/`G` (or let DART resolve a `#channel-name` for you).

> **Answer to “wdyt, is this possible?”** — Slack DMs (to yourself and others) and Slack channels are fully doable today and are wired in v2. Email is technically possible but deferred: it's the only target needing extra infrastructure (a mail transport + credential), so v2 ships Slack-first and leaves a documented hook for email later.

---

## Example config

```yaml
kpis: [pet, on_time, on_time_stacked, dt45]
frequency: weekly
audience:
  slack_user_ids: ["U036E4LSTCP"]      # self + others
  slack_channel_ids: ["C051L8NRY69"]   # optional channel
autonomous: false                      # true = send without confirmation (headless)
report_dir: "/Users/harnoor.chahal/ai/seamless-reports"
```

See [config.example.yaml](config.example.yaml) for the fully-commented schema.

---

## 🕒 Run it on a schedule (headless)

For unattended runs, set `autonomous: true` and drive the skill from a scheduler. The reference pattern is `scripts/run-seamless-analysis.sh` + macOS launchd (used for the weekly send), which calls `claude --print` with a prompt that runs the skill; a provenance marker dedups repeated fires. Align the scheduler's cadence with your `frequency` (a daily config wants a daily trigger). For CI, the `cpl-seamless-automation` repo's GitHub Actions `cron` + Slack-webhook workflow is the analogous headless model.

---

## What DART produces (report structure)

A single, strict Markdown report:
- **Table 1 — Primary KPIs** (flagged markets, selected KPIs + their PoP deltas, with 🚀/⚠️/📉 markers)
- **Table 2 — Diagnostic KPIs** (auto-pruned to what moved materially)
- **Reasoning** (≤ 4 bullets, root-cause driven, folds in holiday/weather context for deteriorating markets)
- **Actions** (one row per market: diagnosis, root-cause class, owner, routing channel, recommended action)
- **Platform Health** (one-line deterioration share per brand)

The full determinism rules, priority scoring, root-cause heuristics, action routing, and SQL live in [engine.md](engine.md).
