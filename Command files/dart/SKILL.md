---
name: dart
description: DART — Deviation Analysis & Resolution Tracker. Runs a configurable Seamless logistics anomaly report from BigQuery and delivers it to Slack. On first run (no dart.config.yaml) or when asked to "set up"/"reconfigure" DART, run the setup wizard to pick KPIs, frequency, and audience. Otherwise generate + deliver the report for the current period. Triggers: "run DART", "set up DART", "reconfigure DART", "DART report".
---

# DART — Deviation Analysis & Resolution Tracker

DART monitors Seamless delivery KPIs, diagnoses anomalies with expert heuristics, and delivers a strict, deterministic report to a Slack audience. It is configurable along three axes: **which KPIs**, **how often**, and **who receives it**.

This skill has two paths. Decide which one to run **before doing anything else**:

- **Setup path** → run when `dart.config.yaml` does NOT exist in this skill folder, OR the user's request is to *set up / configure / reconfigure / change* DART (e.g. "set up DART", "change DART frequency", "add someone to DART").
- **Run path** → run when `dart.config.yaml` exists AND the user wants a report (e.g. "run DART", "DART report", or a scheduled/headless invocation).

The config file lives at the **skill folder path** (the directory this `SKILL.md` is in), named `dart.config.yaml`. See `config.example.yaml` for the schema.

---

## Setup path — the configuration wizard

Goal: collect three answers and write `dart.config.yaml`. Use the `AskUserQuestion` tool (one call, three questions) so the user picks from options. If `AskUserQuestion` is unavailable (headless), ask in plain text and parse the reply.

**Question 1 — KPIs** (multi-select; at least one). Options map to config keys:
- `PET (Pickup Efficiency Time)` → `pet`
- `%on-time (±10 min)` → `on_time`
- `%on-time for stacked orders` → `on_time_stacked`
- `%orders delivered in over 45 min [DT>45], ALL verticals` → `dt45`

**Question 2 — Frequency** (single-select): `Daily` → `daily` · `Weekly` → `weekly` · `Monthly` → `monthly`.

**Question 3 — Audience** (multi-select intent; then collect the actual IDs):
- `Just me` → after selecting, ask for (or reuse) the user's own Slack user ID → `slack_user_ids`.
- `Specific people (Slack DMs)` → ask for each person's Slack user ID (from their Slack profile → "Copy member ID") → append to `slack_user_ids`.
- `Slack channel(s)` → ask for each channel ID (or name; resolve with `slack_search_channels`) → `slack_channel_ids`.
- `Email` → tell the user email is **not wired in v2** (needs an SMTP/email API + a stored secret) and record nothing; offer to note it as a future add.

After collecting answers:
1. Also ask (or default) **autonomous**: `false` unless the user says this is for scheduled/headless runs.
2. Echo the resulting config back to the user in a readable summary and **confirm** before writing.
3. Write `dart.config.yaml` to the skill folder, mirroring `config.example.yaml`'s schema. Keep `report_dir` default unless the user overrides.
4. Tell the user setup is done and how to run: "say *run DART*" (and point to `DART-v2.md` for scheduling).

Do NOT run the analysis automatically after setup unless the user asks.

---

## Run path — generate and deliver the report

1. **Load config.** Read `dart.config.yaml` from the skill folder. If it is missing, switch to the Setup path instead. Validate that `kpis` is non-empty and `audience` has at least one target; if not, tell the user and offer to reconfigure.
2. **Preconditions.** Confirm BigQuery access (via the `data-analyst` skill / `bq`) and, if any audience targets exist, that the Slack MCP is connected. If Slack is unavailable and `autonomous: false`, warn and offer to render-only.
3. **Execute the engine.** Read `engine.md` (same folder) and execute its Execution Sequence **end-to-end** with the loaded config:
   - restrict primary KPIs to `kpis`;
   - apply the `<frequency>` mapping (grain column, lookback INTERVAL, period label, "PoP" wording) for the configured `frequency`;
   - run Query 1/2 (and Query 3 when PET drift fires and `pet` is selected) against live BigQuery;
   - apply the Determinism Rules and Output Structure exactly.
4. **Persist.** Save the rendered report verbatim to `<report_dir>/report-<PERIOD>.md` (engine step 5).
5. **Deliver to audience.**
   - If `autonomous: false`: show the rendered report, then ask the user to confirm sending. On confirmation, send.
   - If `autonomous: true`: send without asking.
   - Send the report **verbatim** via `mcp__plugin_slack_slack__slack_send_message` — one call per entry in `audience.slack_user_ids` (as a DM: `channel_id` = user ID) and one per entry in `audience.slack_channel_ids` (`channel_id` = channel ID).
   - If any send fails (e.g. lapsed headless Slack token), report which targets failed and do NOT claim success for them.
6. **Report back.** Summarize: period covered, KPIs run, file path, and which Slack targets received it (and any failures).

---

## Notes

- **Engine parity:** with `kpis` = all four, `frequency: weekly`, and the three original DMs as audience, the Run path reproduces the legacy `/run-seamless-analysis` weekly report — `engine.md` is `DART-v1.md` generalized, not rewritten.
- **Scheduling / headless:** for unattended runs, set `autonomous: true` and drive this skill from a scheduler (see `DART-v2.md` → "Run it on a schedule"; the existing `scripts/run-seamless-analysis.sh` + launchd is the reference pattern).
- **Reconfigure anytime:** "reconfigure DART" re-runs the wizard and overwrites `dart.config.yaml`.
