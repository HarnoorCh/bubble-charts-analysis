---
name: Folder creation restriction
description: New folders must only be created inside /Users/harnoor.chahal/ai — never directly under /Users/harnoor.chahal/
type: feedback
originSessionId: bec61736-48ed-4700-b2ab-ae738b6290a1
---
Only create new folders inside `/Users/harnoor.chahal/ai/`. Do not create folders directly under `/Users/harnoor.chahal/`.

**Why:** User does not have permissions / does not want new folders cluttering the home directory.

**How to apply:** Before running `mkdir` or creating any new directory, check that the path is under `/Users/harnoor.chahal/ai/`. If a task requires a new folder elsewhere, ask the user where to put it.
