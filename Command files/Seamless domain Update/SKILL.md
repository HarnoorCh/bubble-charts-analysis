---
name: seamless-domain-update
description: Pre-meeting prep workflow for the bi-weekly Seamless Domain Update with CPL leads. Creates the new Confluence Live doc by cloning the previous CW page, clears the "3/4 things" list, and posts the Slack topic-collection message to #log-seamless-domain-leads. Trigger when Uri says "run the Domain Update workflow", "prep the Domain Update", "send the Domain Update topics", or similar. Do NOT use for the monthly Seamless Cycle Review — that has a separate workflow.
---

# Seamless Domain Update — pre-meeting prep workflow

Run this the **day before** each bi-weekly Seamless Domain Update (with CPL leads: Daniel, Brad, Niccolò, Harnoor, Florian, Gayatri). It does two things:

1. **Create the new CW Confluence Live doc** by cloning the previous CW page and clearing the "3/4 things" numbered list.
2. **Post the Slack message** to `#log-seamless-domain-leads` asking for the day's topics, with the new Confluence page linked.

Background context is in memory: `[[Seamless Domain Update — Bi-Weekly Prep Workflow]]` (`project_domain_update_prep.md`).

The skill is shared with Harnoor and Florian so any of the three can run it. The shared copy + setup guide for new runners lives at: https://github.com/deliveryhero/seamless-ceremonies-skills

## Pre-conditions to verify

- The user has confirmed (or already stated) the **meeting date** so the page title (`YYYY-MM-DD (CWNN) Seamless Domain Update`) and the "Tomorrow we have…" message are correct. If unclear, ask.
- Today is the **day before** the meeting (the message says "tomorrow"). If asked to schedule for a future day, use `slack_schedule_message` instead of `slack_send_message`.

## Key references

- **Confluence parent page:** `36656082` (LOGCPL space — "Seamless Domain Updates" index)
- **Slack channel:** `#log-seamless-domain-leads` = `C077HP1EAP4`
- **Atlassian API token:** macOS Keychain entry `atlassian-api-token` (see SETUP.md § 3)
- **Atlassian user:** set `ATLASSIAN_USER=your@deliveryhero.com` before running (each runner uses their own email)

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

Query Confluence API to find the most recent Seamless Domain Update page under parent `36656082`. Note its page ID and extract CW number from title for the new page title.

**CRITICAL:** Use the Confluence REST API to fetch the page in **storage format** — this preserves ALL formatting, mentions, links, and structure exactly as-is.

## Step 2 — Fetch the previous page in storage format

Use the Confluence REST API to get the complete page content in storage XML format. This is the ONLY way to preserve formatting exactly:

```bash
TOKEN=$(security find-generic-password -s "atlassian-api-token" -w)
curl -s -u "$ATLASSIAN_USER:$TOKEN" \
  "https://deliveryhero.atlassian.net/wiki/rest/api/content/PREV_PAGE_ID?expand=body.storage" \
  -H "Accept: application/json" \
  -o /tmp/prev_cw_page.json
```

Verify the JSON contains `body.storage.value` with the complete page XML.

## Step 3 — Clear ONLY the "3/4 things" numbered list items

**CRITICAL RULE:** Preserve EVERY character except the numbered list items under the "What are the 3/4 things we really want to talk about today?" heading.

**Algorithm:**
1. Load the storage XML from `/tmp/prev_cw_page.json`
2. Find the heading `"3/4 things"` or `"What are the 3/4 things"`
3. After this heading, find the first `<ol>` tag (opening ordered list)
4. Replace ONLY the content BETWEEN the `<ol>` and `</ol>` tags with: `<li><p /></li>` (single empty list item)
5. **KEEP everything else 100% unchanged** — all other headings, sections, links, mentions, formatting

Reference Python (preserves all other content):

```python
import json, re

# Load the previous page
d = json.load(open('/tmp/prev_cw_page.json'))
body = d['body']['storage']['value']
version = d['version']['number']

# Find the "3/4 things" heading
heading_patterns = [
    r"<h1>What are the 3/4 things we really want to talk about today\?</h1>",
    r"<p>.*?3/4 things.*?</p>",
    r"3/4 things"
]

heading_idx = body.lower().find('3/4 things')
if heading_idx == -1:
    raise ValueError("Cannot find '3/4 things' heading in page")

# Find the FIRST <ol> after this heading
m = re.search(r'<ol[^>]*>', body[heading_idx:])
if not m:
    raise ValueError("Cannot find ordered list after '3/4 things'")

ol_start = heading_idx + m.start()
ol_open_end = heading_idx + m.end()

# Find matching </ol> using balanced depth counting
i = ol_open_end
depth = 1
while depth > 0 and i < len(body):
    next_ol = body.find('<ol', i)
    next_close = body.find('</ol>', i)
    
    if next_ol != -1 and next_ol < next_close:
        # Found nested <ol>
        depth += 1
        i = next_ol + 3
    else:
        # Found </ol>
        depth -= 1
        if depth == 0:
            ol_close_start = next_close
            break
        i = next_close + 5

# Replace list content with single empty item
new_body = body[:ol_open_end] + '<li><p /></li>' + body[ol_close_start:]

# Verify the structure is still valid
if new_body.count('<ol') != body.count('<ol'):
    raise ValueError("Structure corruption: <ol> count mismatch")
if new_body.count('</ol>') != body.count('</ol>'):
    raise ValueError("Structure corruption: </ol> count mismatch")

open('/tmp/new_cw_body.xml', 'w').write(new_body)
print("✓ Cleared 3/4 things — all other content preserved")
```

## Step 4 — Create the new CW page as a Live doc with exact clone of content

Post to Confluence REST API with the modified storage XML. **Use `subtype: live`** to match the original page type:

```python
import json, urllib.request, base64, subprocess, os

# Read the modified content
new_body_xml = open('/tmp/new_cw_body.xml').read()

# Get auth token
token = subprocess.check_output(['security','find-generic-password','-s','atlassian-api-token','-w']).decode().strip()
auth = base64.b64encode(f"{os.environ['ATLASSIAN_USER']}:{token}".encode()).decode()

# Build payload with storage format
payload = {
    "type": "page",
    "subtype": "live",  # REQUIRED — must match original Live doc subtype
    "title": "2026-07-08 (CW28) Seamless Domain Update",  # Update date and CW number
    "space": {"key": "LOGCPL"},
    "ancestors": [{"id": "36656082"}],  # Parent page
    "body": {
        "storage": {
            "value": new_body_xml,  # Use the modified storage XML exactly
            "representation": "storage"
        }
    },
    "metadata": {"properties": {"editor": {"key": "editor", "value": "v2"}}}
}

# Create the page
req = urllib.request.Request(
    "https://deliveryhero.atlassian.net/wiki/rest/api/content",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/json"
    },
    method="POST"
)

response = urllib.request.urlopen(req)
result = json.loads(response.read())
new_page_id = result['id']

print(f"✓ Created new CW page: {new_page_id}")
print(f"✓ Subtype verified: {result.get('subtype')}")
print(f"✓ Parent verified: {result.get('ancestors', [{}])[0].get('id')}")

# Print the canonical URL
canonical_url = f"https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/{new_page_id}"
print(f"✓ Page URL: {canonical_url}")
```

**Verification:**
- Confirm the new page has `subtype: live`
- Confirm parent page is `36656082`
- Verify the page content matches the previous CW page exactly (all sections, links, mentions, formatting intact)
- Verify ONLY the "3/4 things" numbered items are empty

## Step 4.5 — Populate the OKR section

Run the OKR section generator on the new page immediately after it is created.

**Script:** `~/.claude/skills/seamless-domain-update/okr_section_generator.py` (co-located with this SKILL.md)

**Pre-conditions:** `ATLASSIAN_USER` and `GOOGLE_WORKSPACE_CLI_TOKEN` must be set (see SETUP.md §§ 3–4).

```bash
export ATLASSIAN_USER=your@deliveryhero.com   # skip if already exported

export GCLOUD_SDK_ROOT=$(gcloud info --format="value(installation.sdk_root)")
export PYTHONPATH="$GCLOUD_SDK_ROOT/lib/third_party:$GCLOUD_SDK_ROOT/lib"
export GOOGLE_WORKSPACE_CLI_TOKEN=$(python3 -c "
import google.auth; from google.auth.transport.requests import Request
creds, _ = google.auth.default(scopes=[
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/spreadsheets',
])
creds.refresh(Request()); print(creds.token)")

python3 ~/.claude/skills/seamless-domain-update/okr_section_generator.py NEW_PAGE_ID
```

**What the script does:**
1. Reads "Quarterly OKRs" tab of the CPL OKR sheet (values + cell notes + background colors)
2. Filters to Seamless/CPL-owned rows (Uri's initiative in O1 + all O3 rows + Seamless/CPL items in O4)
3. `latest_cw = current_cw − 1` (we update last week's data on Monday of current week)
4. Generates the OKR section:
   - **Screenshot placeholder** — paragraph tagging Uri with a link to the Slack action-items message
   - **Summary** — `KR#`/`I#` bullets with global sequential numbers matching the Details section; comparison window = `latest_cw − 2` (2-week meeting cadence); max 4 positives + 4 risks; if exceeded a tagging bullet prompts Uri to shortlist
   - **Details** — O# headers → KR# headings (bold) → I# bullets (bold+italic), each with completion % and colored status tag matching [CW12 convention](https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/1318551601)
5. Detects gaps (rows where `latest_cw` value or note is empty)
6. Prints two Slack drafts: one for gap owners, one for Uri's action items

**Color classification (Google Sheets RGB → Confluence status tag):**
- R ≤ 0.92 → green → `[on-track]` (rgb 211,241,167)
- R ≥ 0.93, G ≥ 0.86 → amber → `[recoverable]` (rgb 254,222,200)
- R ≥ 0.93, G < 0.86 → red → `[not recoverable]` (rgb 253,208,236)

**After running the script — three actions required:**

### 4.5a — Send gap owner reminder (if there are gaps)

**Always confirm with the runner before sending** — this message can feel intrusive; the runner decides whether it's worth sending for this cycle.

The script prints a draft. Before posting, prepend this intro and append the footer, substituting the correct weekday (the day before the meeting = prep day = today):

```
Hello team :wave:
I am preparing the Domain Update page for tomorrow [MEETING_WEEKDAY] and some OKRs are not updated yet.
Please update by today [TODAY_WEEKDAY] EOD so the Domain Update page can reflect the latest status.

[script draft lines — one bullet per owner]

_This message is auto-generated by the Domain Update prep skill._ :robot_face:
```

Post to channel `C01RQ7FRP6Y` (#log-customer-seamless-management).

### 4.5b — Send Uri's action items to the 3-leads channel

Post the `[SEND TO #log-seamless-3-leads]` draft to channel `C09QD5XGP5Y`. Note the URL of this message (`https://deliveryhero.slack.com/archives/C09QD5XGP5Y/p...`).

### 4.5c — Embed the Slack URL in the Confluence placeholder

Re-run the script with the Slack URL as the second argument. This replaces the `"see Slack for action items"` placeholder with a real link:

```bash
python3 ~/.claude/skills/seamless-domain-update/okr_section_generator.py NEW_PAGE_ID "https://deliveryhero.slack.com/archives/..."
```

**OKR source:** https://okra.deliveryhero.io/ → "Building customer trust through reliable delivery promises"

**Note:** OKRs have been migrated from Google Sheets to the okra system. Script should fetch data from the new okra platform.

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

If you change the local SKILL.md (new step, fixed bug, updated IDs), commit and push to the [GitHub repo](https://github.com/deliveryhero/seamless-ceremonies-skills). Harnoor and Florian update their local copies with `git -C ~/work/repos/seamless-ceremonies-skills pull`. If the change is non-trivial, drop a note in `#log-customer-seamless-management` so they know to pull.
