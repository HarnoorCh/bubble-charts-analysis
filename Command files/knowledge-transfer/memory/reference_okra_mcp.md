---
name: reference_okra_mcp
description: "Okra MCP server setup for OKR data (--scope user, restart session); mcp add default-scope gotcha"
metadata:
  type: reference
---

**Okra** = OKR-data MCP server. Register in USER scope (default local scope ties it to the cwd it was run in):

```
claude mcp add --scope user --transport http okra https://okra.deliveryhero.io/api/mcp \
  --header "CF-Access-Client-Id: ..." --header "CF-Access-Client-Secret: ..." \
  --header "Authorization: Bearer okra_..."
```

MCP tools load only at session startup — **restart the session** after adding. General gotcha: `claude mcp add` without `--scope` defaults to local (directory-bound); use `--scope user` for cross-project availability. Okra tools (`mcp__okra__*`) cover OKR search/history/status/completion patterns. See [[project_okr_state]].
