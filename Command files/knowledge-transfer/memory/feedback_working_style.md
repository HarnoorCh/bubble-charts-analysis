---
name: feedback_working_style
description: "How the user wants Claude to work: never run expensive queries without OK, 'just the query'=verbatim SQL, honesty over fabrication, 'Mio' not 'm', mean+p50"
metadata:
  type: feedback
---

Working-style rules the user has stated repeatedly.

- **Never run expensive BigQuery queries without explicit OK.** Dry-run, report the cost estimate, wait. The user interrupts costly runs ("don't run", "too expensive").
- **"Just the query" = output the full SQL verbatim, no preamble.**
- **Honesty over fabrication.** Never invent data, a Slack send, a weather tie, or a label (past misses: fabricated "Q3 Markets" label, claimed a send that didn't happen). Use clearly-labeled placeholders (amber "Add…"/"Illustrative") when data is missing; flag sign-convention ambiguities and data caveats; verify schema before generating.
- **Write millions as "Mio"** (not "m").
- **Report both mean and p50** for right-skewed ETA-vs-reality durations.
- **Confluence:** prefer reversible edits — publish with a clear version message and explain how to revert via Page History (API can't save a true draft on a published page).
- Style: concise, scannable ("at a glance"/"one-minute version"), collapsible detail for secondary info. Related: [[feedback_folder_creation]], [[feedback_slack_table_format]], [[feedback_presentation_format]].
