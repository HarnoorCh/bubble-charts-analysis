# Seamless Domain Update skill — setup guide

This skill prepares the bi-weekly Seamless Domain Update with CPL leads: it creates the next CW Confluence Live doc by cloning the previous one, clears the "3/4 things" numbered list, and posts the topic-collection Slack message to `#log-seamless-domain-leads`.

Estimated setup time: ~10 minutes.

---

## 1. Install Claude Code

If you don't have it yet:
- VS Code: search "Claude Code" in the Extensions panel
- CLI: see https://docs.claude.com/claude-code

Make sure you can launch it and run a basic chat.

## 2. Install the skill file

Copy `SKILL.md` (shipped alongside this file) to:

```
~/.claude/skills/seamless-domain-update/SKILL.md
```

Create the directory first if needed:

```bash
mkdir -p ~/.claude/skills/seamless-domain-update
cp /path/to/SKILL.md ~/.claude/skills/seamless-domain-update/SKILL.md
```

Restart Claude Code. You should see `seamless-domain-update` in the available skills list.

## 3. Set up the Atlassian API token (for Confluence)

The skill creates the new CW page via the Confluence REST API and needs an API token stored in your macOS Keychain.

**Create the token:**
1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token** → label it `claude-code-domain-update` (or similar)
3. Copy the token immediately (it won't be shown again)

**Store it in Keychain (macOS):**

```bash
security add-generic-password -a "$USER" -s "atlassian-api-token" -w "<paste-token-here>"
```

**Verify:**

```bash
security find-generic-password -s "atlassian-api-token" -w | head -c 10
# Should print the first 10 chars of your token
```

> Windows / Linux users: store the token however your platform supports secrets, and update Step 2 of `SKILL.md` to use that retrieval method instead of `security find-generic-password`.

## 4. Set up the Slack MCP connector

Claude Code needs the Slack MCP connector enabled to post messages to `#log-seamless-domain-leads`.

- Open Claude Code → Settings → MCP servers (or `claude mcp` in CLI).
- Add the Slack connector for the `deliveryhero` workspace.
- Authenticate when prompted (browser flow with your DH SSO).

**Verify Slack works** by asking Claude: *"What's the most recent message in #log-seamless-domain-leads?"* — should return today's activity.

## 5. Set up the Atlassian MCP connector

The skill uses the Atlassian MCP connector to find the most recent CW page under the parent index. (The actual page creation goes through the REST API in Step 3 above, but finding the previous page is easier via MCP.)

- Same flow as Slack: Settings → MCP servers → add Atlassian, authenticate with your DH SSO.

**Verify** by asking Claude: *"List the children of Confluence page 36656082"* — should return the recent CW pages.

## 6. Run the skill

The day before the bi-weekly Domain Update meeting, open Claude Code and say:

> **"run the Domain Update workflow"** (or "prep the Domain Update", "send the Domain Update topics")

Claude will:
1. Find the previous CW page and confirm the meeting date with you
2. Create the new CW Live doc (cloned from the previous one, with the "3/4 things" list cleared)
3. Post the topic-collection Slack message to `#log-seamless-domain-leads` with the Confluence link and cc list (Daniel, Brad, Niccolò, Harnoor, Florian, Gayatri)

Full flow takes ~30 seconds.

---

## Things that will go wrong (and the fix)

| Symptom | Likely cause | Fix |
|---|---|---|
| `401 Unauthorized` from the Confluence API | Atlassian token expired or wrong | Recreate the token on id.atlassian.com, re-store in Keychain |
| New page isn't a Live doc | `subtype: live` missing from create payload | Re-check Step 4 of `SKILL.md` includes both `subtype: live` and the editor v2 metadata property |
| "Couldn't find the 3/4 things list" | Heading text in previous page changed | Open the previous CW page, confirm the heading still reads `What are the 3/4 things we really want to talk about today?` and update the substring match in `SKILL.md` if it changed |
| Slack message goes to wrong channel | Channel ID wrong | `#log-seamless-domain-leads` = `C077HP1EAP4` (always — don't let Claude guess) |
| Wrong people @mentioned | Slack user IDs changed (rare) | Update the cc table in `SKILL.md` |

---

## Who can run it

Anyone with the setup above. Currently:
- Uri Alarcon — set up
- Harnoor Chahal — needs setup
- Florian Marienfeld — needs setup

The skill is identical on any laptop. If Uri is OOO or unavailable the day before a Domain Update, either Harnoor or Florian can run it instead — first to claim it goes ahead.

## Questions

Ping Uri on Slack (`@U03AY75DH5H`) or in `#log-customer-seamless-management`.
