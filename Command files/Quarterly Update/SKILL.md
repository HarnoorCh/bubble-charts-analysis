---
name: seamless-domain-update
description: Pre-meeting prep workflow for the bi-weekly Seamless Domain Update with CPL leads. Creates the new Confluence Live doc by cloning the previous CW page, clears the "3/4 things" list, and posts the Slack topic-collection message to #log-seamless-domain-leads. Trigger when Uri says "run the Domain Update workflow", "prep the Domain Update", "send the Domain Update topics", or similar. Do NOT use for the monthly Seamless Cycle Review — that has a separate workflow.
---

# Seamless Domain Update — pre-meeting prep workflow

Run this the **day before** each bi-weekly Seamless Domain Update (with CPL leads: Daniel, Brad, Niccolò, Harnoor, Florian, Gayatri). It does two things:

1. **Create the new CW Confluence Live doc** by cloning the previous CW page and clearing the "3/4 things" numbered list.
2. **Post the Slack message** to `#log-seamless-domain-leads` asking for the day's topics, with the new Confluence page linked.

Background context is in memory: `[[Seamless Domain Update — Bi-Weekly Prep Workflow]]` (`project_domain_update_prep.md`).

The skill is shared with Harnoor and Florian so any of the three can run it. The shared copy + setup guide for new runners lives at: https://drive.google.com/drive/folders/1k72pYQpW7zgOxf-xBnPUlHEPUbsnmDSC

## Pre-conditions to verify

- The user has confirmed (or already stated) the **meeting date** so the page title (`YYYY-MM-DD (CWNN) Seamless Domain Update`) and the "Tomorrow we have…" message are correct. If unclear, ask.
- Today is the **day before** the meeting (the message says "tomorrow"). If asked to schedule for a future day, use `slack_schedule_message` instead of `slack_send_message`.

## Key references

- **Confluence parent page:** `36656082` (LOGCPL space — "Seamless Domain Updates" index)
- **Slack channel:** `#log-seamless-domain-leads` = `C077HP1EAP4`
- **Atlassian API token:** macOS Keychain entry `atlassian-api-token` for `uri.alarcon@deliveryhero.com`

## Stable Slack user IDs (cc list)

| Person | Slack ID |
|--------|----------|
| Daniel Rüdiger | U4QNW0MJ7 |
| Brad Moore | U0525U7Q1G8 |
| Niccolò Luti | U0710JS2BPZ |
| Harnoor Chahal | U036E4LSTCP |
| Florian Marienfeld | U02L96VHDHC |
| Gayatri Kanala | U02TTK7CEK1 |

## Step 1 — Find the previous CW page

Use `mcp__atlassian__confluence_get_page_children` with `parent_id=36656082`, `limit=5`, `include_content=false`. The first result (sorted newest first) is the page to clone. Note its `id`, `title`, and CW number for the new title.

## Step 2 — Fetch storage XML via curl

The MCP tool returns markdown, which loses the structure needed to surgically clear one list. Use the REST API:

```bash
TOKEN=$(security find-generic-password -s "atlassian-api-token" -w)
curl -s -u "uri.alarcon@deliveryhero.com:$TOKEN" \
  "https://deliveryhero.atlassian.net/wiki/rest/api/content/PREV_PAGE_ID?expand=body.storage,version" \
  -o /tmp/prev_cw_page.json
```

## Step 3 — Clear the "3/4 things" numbered list

**Important:** The `local-id` on the target `<ol>` **changes between pages**. Do NOT hard-code a local-id. Instead, locate the first `<ol>` opening tag that appears *after* the substring `"3/4 things"` in the storage XML, then walk forward with a balanced depth counter to find the matching `</ol>` (the list contains nested `<ol>` tags that break naive regex).

Replace the inner content with `<li><p /></li>` — Confluence drops a fully empty `<ol>`.

Reference Python:

```python
import json, re
d = json.load(open('/tmp/prev_cw_page.json'))
body = d['body']['storage']['value']

heading_idx = body.lower().find('3/4 things')
m = re.compile(r'<ol\b[^>]*>').search(body, pos=heading_idx)
ol_open_end = m.end()

i, depth = ol_open_end, 1
while depth > 0:
    no, nc = body.find('<ol', i), body.find('</ol>', i)
    if no >= 0 and no < nc:
        depth += 1; i = body.find('>', no) + 1
    else:
        depth -= 1; i = nc + len('</ol>')

new_body = body[:ol_open_end] + '<li><p /></li>' + body[i - len('</ol>'):]
open('/tmp/new_cw_body.html', 'w').write(new_body)
```

## Step 4 — Create the new CW page as a Live doc

POST to `/wiki/rest/api/content` with:
- `type: page`
- `subtype: live` (REQUIRED — must be a Live doc, not standard page)
- `title: YYYY-MM-DD (CWNN) Seamless Domain Update` (date = meeting date)
- `space.key: LOGCPL`
- `ancestors: [{ "id": "36656082" }]`
- `body.storage.value` = the modified XML
- `metadata.properties.editor.value: "v2"`

Reference Python (continues from Step 3):

```python
import json, urllib.request, base64, subprocess
token = subprocess.check_output(['security','find-generic-password','-s','atlassian-api-token','-w']).decode().strip()
auth = base64.b64encode(f"uri.alarcon@deliveryhero.com:{token}".encode()).decode()

payload = {
    "type": "page", "subtype": "live",
    "title": "YYYY-MM-DD (CWNN) Seamless Domain Update",
    "space": {"key": "LOGCPL"},
    "ancestors": [{"id": "36656082"}],
    "body": {"storage": {"value": open('/tmp/new_cw_body.html').read(), "representation": "storage"}},
    "metadata": {"properties": {"editor": {"key": "editor", "value": "v2"}}}
}
req = urllib.request.Request(
    "https://deliveryhero.atlassian.net/wiki/rest/api/content",
    data=json.dumps(payload).encode(),
    headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
    method="POST"
)
out = json.loads(urllib.request.urlopen(req).read())
print(out['id'], out.get('subtype'))
```

Construct the canonical URL as `https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/<NEW_PAGE_ID>` (the API may return the data-center base URL; use the `deliveryhero.atlassian.net` form for the Slack link).

## Step 5 — Post the Slack message

Channel: `C077HP1EAP4`. Use the new CW page URL from Step 4.

**Template:**

```
*Domain Update Topics*
Tomorrow we have the Domain Update — what are the 3/4 things we really want to talk about?
cc: <@U4QNW0MJ7> <@U0525U7Q1G8> <@U0710JS2BPZ> <@U036E4LSTCP> <@U02L96VHDHC> <@U02TTK7CEK1>

:page_facing_up: Confluence notes for tomorrow: NEW_CW_PAGE_URL
```

**Send rules:**
- Plain URL (no angle brackets) so unfurling works.
- Do NOT add "Sent using Claude" — the integration appends it automatically.
- **Send now if today is the day before the meeting.** If running earlier than that, use `slack_schedule_message` with `post_at` = the morning of the day-before (≈ 09:00 Europe/Berlin).

## Step 6 — Update the page-history table in memory

Append the new row to the page history table in `project_domain_update_prep.md`:

```
| CWNN | YYYY-MM-DD | NEW_PAGE_ID |
```

This keeps the running ledger of past meetings + lets future runs verify the previous CW page found in Step 1 is plausible.

## Step 7 — Summary back to Uri

Report:
- New CW Confluence page (title + URL) → verify it's a Live doc
- Slack message sent (link) or scheduled (fire time + ID)
- Anything skipped / requires manual decision

## What stays manual

- Confirming the meeting date if not stated.
- Populating the 3/4 topics during/before the meeting itself (the team replies in the Slack thread).
- Editing/cancelling the scheduled Slack message if needed (Slack → Drafts & Sent).

## Keeping the shared copy in sync

If you change the local SKILL.md (new step, fixed bug, updated IDs), upload the new version to the shared Drive folder (`1k72pYQpW7zgOxf-xBnPUlHEPUbsnmDSC`) so Harnoor and Florian get the same version next time they re-copy. If the change is non-trivial, drop a note in `#log-customer-seamless-management` so they know to update.
