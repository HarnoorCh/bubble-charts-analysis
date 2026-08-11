---
name: reference_litellm_budget
description: "LiteLLM budget: request-budget-increase command, $200 cap -> ExceededBudget, /budget skill, gateway port"
metadata:
  type: reference
---

LiteLLM / inference budget. Increase: `dp-devinfra litellm request-budget-increase --amount 100 --days 30`. Check usage: `/budget` skill. Cap is $200 — when spend hits it, all model calls fail with `400 ExceededBudget`. Inference gateway runs at localhost:36253 (503/502 point there). Token counts for cost analysis live in the Claude Code session transcripts (`~/.claude/projects/-Users-harnoor-chahal-ai/*.jsonl`), not the text run logs.
