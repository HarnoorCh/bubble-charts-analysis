---
name: seamless-domain-update-prep
description: "Background context + page-history ledger for the bi-weekly Seamless Domain Update prep workflow. Used by the `seamless-domain-update` skill to verify the previous CW page found via the Confluence parent index."
metadata: 
  node_type: memory
  type: project
  originSessionId: 86ed2ed9-e026-47aa-9c05-7f87f56575d4
---

# Seamless Domain Update — Bi-Weekly Prep Workflow

The Seamless Domain Update is a bi-weekly meeting with CPL leads (Daniel Rüdiger, Brad Moore, Niccolò Luti, Harnoor Chahal, Florian Marienfeld, Gayatri Kanala). The day before each meeting, a Confluence Live doc is created (cloned from the previous CW page with the "3/4 things" list cleared) and a topic-collection message is posted to `#log-seamless-domain-leads`.

**Why:** Standardizes meeting prep across rotating runners (Uri / Harnoor / Florian) so no step is missed and the cc list / channel / parent page are never guessed.

**How to apply:** When running the workflow (see `seamless-domain-update` skill), use the table below to sanity-check that the previous CW page returned by the Confluence parent-page descendants call matches the most recent row here. If they diverge, investigate before cloning.

## Page history

| CW | Meeting date | Page ID |
|----|--------------|---------|
| CW14 | 2026-04-01 | 1443463559 |
| CW16 | 2026-04-15 | 1500905705 |
| CW18 | 2026-04-29 | 1503297591 |
| CW20 | 2026-05-13 | 1631028099 |
| CW22 | 2026-05-27 | 1674281011 |
| CW24 | 2026-06-10 | 1687617662 |
