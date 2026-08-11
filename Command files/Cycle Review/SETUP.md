# Seamless Cycle Review skill — setup guide

This skill drafts the post-meeting Cycle Review email and schedules next month's Slack prep reminder. It works on any laptop with Claude Code + Google + Slack access.

Estimated setup time: ~15 minutes.

---

## 1. Install Claude Code

If you don't have it yet, install the VS Code extension or CLI:
- VS Code: search "Claude Code" in the Extensions panel
- CLI: see https://docs.claude.com/claude-code

Make sure you can launch it and run a basic chat.

## 2. Install the skill file

Copy `SKILL.md` (shipped alongside this file) to:

```
~/.claude/skills/seamless-cycle-review/SKILL.md
```

Create the directory if it doesn't exist:

```bash
mkdir -p ~/.claude/skills/seamless-cycle-review
cp /path/to/SKILL.md ~/.claude/skills/seamless-cycle-review/SKILL.md
```

Restart Claude Code. You should see `seamless-cycle-review` in the available skills list.

## 3. Set up Google Workspace authentication

The skill talks to Gmail, Calendar, Drive, Sheets, and Slides via the `gws` CLI tool (or any equivalent). You need gcloud application-default credentials with the right scopes.

**Prerequisites:**
- `gcloud` CLI installed (`brew install --cask google-cloud-sdk` on macOS)
- `gws` CLI installed — `pip install google-workspace-cli` or follow your team's instructions

**One-time auth — run this exact command:**

```bash
gcloud auth application-default login \
  --scopes=openid,\
https://www.googleapis.com/auth/userinfo.email,\
https://www.googleapis.com/auth/cloud-platform,\
https://www.googleapis.com/auth/drive,\
https://www.googleapis.com/auth/spreadsheets,\
https://www.googleapis.com/auth/documents,\
https://www.googleapis.com/auth/presentations,\
https://www.googleapis.com/auth/calendar,\
https://www.googleapis.com/auth/gmail.compose,\
https://www.googleapis.com/auth/gmail.send,\
https://www.googleapis.com/auth/gmail.readonly
```

A browser opens → sign in with your `@deliveryhero.com` account → review and approve all permissions (you'll see Gmail, Calendar, Drive, etc. in the consent screen).

> **If consent fails with "Access blocked: This app's request is invalid"**, the org may restrict gcloud SDK from being granted Gmail scopes. Workaround: create a personal OAuth client in your own GCP project (Desktop app type) and use `gws auth login`. Ask Uri for the detailed steps if you hit this.

**Token refresh helper.** Each session, before running the skill, refresh the access token:

```bash
export GCLOUD_SDK_ROOT=$(gcloud info --format="value(installation.sdk_root)")
export PYTHONPATH="$GCLOUD_SDK_ROOT/lib/third_party:$GCLOUD_SDK_ROOT/lib"
export GOOGLE_WORKSPACE_CLI_TOKEN=$(python3 -c "import google.auth; from google.auth.transport.requests import Request; creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/gmail.compose', 'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']); creds.refresh(Request()); print(creds.token)")
```

Add this block to your CLAUDE.md or a "Google Workspace Protocol" section so Claude knows to run it whenever a 401/403 shows up.

## 4. Verify Google auth

```bash
# Should return your profile
gws gmail users getProfile --params '{"userId": "me"}'

# Should list your calendars
gws calendar calendarList list --params '{"maxResults": 5}'

# Should return file metadata for the master deck
gws drive files get --params '{"fileId": "1gMZl8BDLSU8D7BXrykJT7qp1TbdcFFn8kLW9mTVLxfI", "fields": "id,name"}'
```

If any of those fail with `403 insufficient scopes`, the auth in step 3 didn't include the right scope — re-run the gcloud command.

## 5. Set up Slack MCP connector

Claude Code needs the Slack MCP connector enabled to schedule messages and read channel history.

- Open Claude Code → Settings → MCP servers (or `claude mcp` in CLI).
- Add the Slack connector for the `deliveryhero` workspace.
- Authenticate when prompted.

**Verify Slack works** by asking Claude: *"What's the most recent message in #log-customer-seamless-management?"* — should return today's activity.

## 6. Run the skill

After the Cycle Review meeting ends, open Claude Code and say:

> **"run the Cycle Review workflow"**

Claude will:
1. Find today's meeting + recording
2. Build the email draft → ask you to review
3. After you confirm sent, schedule next month's Slack reminder

The full flow is ~5 minutes including review time.

---

## Things that will go wrong (and the fix)

| Symptom | Likely cause | Fix |
|---|---|---|
| `403 insufficient scopes` on gws calls | Token doesn't have the new scope | Re-run the auth refresh block from step 3 |
| Skill can't find today's meeting | Calendar event title doesn't exactly match `Seamless Domain - Cycle Review` | Make sure the event title hasn't been edited |
| "Slides for next month don't exist yet" | Expected — we don't pre-create them | Skip; the slide gets created during prep week |
| `slack_schedule_message` fails | Channel is externally shared, or post_at is <2 min in future | Channel should be internal; check post_at value |
| Email signature missing in draft | API-created drafts sometimes don't inject Gmail signature | Open draft in Gmail compose, signature usually auto-inserts; or paste manually |
| Recording attachment not on calendar event | Recording wasn't uploaded yet, or wasn't attached | Wait for Google Meet to finish processing (~10-15 min after meeting) and re-run |

---

## Who can run it

Anyone with the setup above. Currently:
- Uri Alarcon — set up
- Harnoor Chahal — needs setup
- Florian Marienfeld — needs setup

The skill is identical on any laptop. A monthly calendar reminder ("Run Cycle Review post-meeting workflow") goes to all three of you; first one to do it claims it.

## Questions

Ping Uri on Slack (`@U03AY75DH5H`) or in `#log-customer-seamless-management`.
