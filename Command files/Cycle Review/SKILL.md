---
name: seamless-cycle-review
description: Post-meeting workflow for the monthly Seamless Domain Cycle Review. Drafts the stakeholder email AND schedules next month's Slack prep reminder. Trigger phrases - "run the Cycle Review workflow", "send the Cycle Review email", "post-CR follow-up". Do NOT use for Quarterly Updates (Apr, Jul, Oct, Jan) - those have a separate workflow.
---

# Seamless Cycle Review - post-meeting workflow

After each monthly Cycle Review (3rd Thursday of the month, except QU months), this skill:

1. **Drafts the post-meeting email** to stakeholders (Gmail draft - reviewer clicks Send).
2. **Schedules next month's Slack prep reminder** in `#log-customer-seamless-management` (Slack-native scheduled message, fires automatically on Monday of the week before).

## Before running - quick sanity checks

- It is NOT the first month of a quarter (April, July, October, January). Those are Quarterly Updates with a different workflow. Abort if so and tell the user.
- The Cycle Review meeting happened today (or recently). Find the most recent past event in primary calendar matching `Seamless Domain - Cycle Review`.

## Key references

- **Master deck:** `1gMZl8BDLSU8D7BXrykJT7qp1TbdcFFn8kLW9mTVLxfI`
- **Repository sheet (Templates tab cell A7 has the canonical email body):** `1Q88oJ_WPNLaHnC5cmOVQ7Zf-DJz4xXo9VRO7oJq1GRc`
- **Quarterly Roadmap sheet:** `1OwXaCizo32kCixGa9Nb6KHq20OkvGRAQ69QndwMrwO8` - find the tab named `Seamless Q# YYYY` for the current quarter
- **Slack channel for prep reminder:** `#log-customer-seamless-management` = `C01RQ7FRP6Y`
- **Email recipients:** To = `log-customer-seamless-stakeholders@deliveryhero.com`, Cc = `log-cpl-seamless-domain@deliveryhero.com`

## Stable Slack user IDs

- Uri Alarcon: `U03AY75DH5H`
- Harnoor Chahal: `U036E4LSTCP`
- Florian Marienfeld: `U02L96VHDHC`
- Ege Sözgen: `UPSV9R1DY`
- Shradha Jain: `U06C8C36751`
- Alina Kim: `U09D065SRT6`

## Authentication

The user's Google Workspace auth setup should already include Drive, Sheets, Slides, Calendar, and Gmail (compose/send/readonly) scopes. See the `SETUP.md` distributed with this skill for the exact gcloud command if a 403 / insufficient_scopes error shows up.

## Step 1 - Gather meeting info

1. **Calendar:** find the most recent past `Seamless Domain - Cycle Review` in `primary`. Capture meeting date, month name, year, ISO week number (CW), and the `video/mp4` recording attachment (Drive file ID + view URL).
2. **Deck:** locate this month's title slide by scanning slides for text matching `"<MONTH>: <YYYY-MM-DD>"`. Capture its `objectId`.
3. **Slide URL:** `https://docs.google.com/presentation/d/<DECK_ID>/edit?slide=id.<TITLE_SLIDE_OBJECTID>#slide=id.<TITLE_SLIDE_OBJECTID>`
4. **Recording on title slide:** check the title slide for a "Recording" text element with a link. If the link is missing, update the slide to set it to the recording's Drive URL.
5. **Focus topics:** read the agenda slide (typically title-slide-index + 2). Extract topic names, skipping any marked `[postponed]`, `[skipped]`, `[cancelled]`.
6. **Roadmap link:** read the Quarterly Roadmap sheet's metadata, find the tab whose title matches `Seamless Q<quarter> <year>` for the current quarter, and build the URL using its `sheetId` as the gid.

## Step 2 - Get the latest email signature

Pull the most recent sent email from the user's Gmail and extract the HTML signature block (from `<span class="gmail_signature_prefix">` to end) and the plain-text equivalent. This keeps the signature current if it ever changes.

## Step 3 - Compose the email draft

**Subject:** `CPL | Seamless domain Cycle Review CW## (MONTH) - YEAR`

**Body structure** (HTML preferred, plain-text alternative also):

```
Hi everyone,

Thank you for joining the <b>MONTH Seamless Cycle Review</b>.
We covered the following:

<b>Focus Topics</b>
1. <focus topic 1>
[2. <focus topic 2> - only if there were 2]

<b>CPL - Seamless OKRs</b>
N. OKRs Progress

<b>Seamless Experiments</b>
N+1. Summary

Here are the <a href="SLIDES_URL">slides</a> and <a href="RECORDING_URL">recording</a>.

For details on the non-OKR initiatives, you can refer to the <a href="ROADMAP_URL">Quarterly Roadmap</a>.

If you have any comments or questions, feel free to reach out to us.

Have a nice day!

<signature_html>
```

Numbering continues across sections (Focus Topics 1, then OKRs 2, Experiments 3, etc.). No manual sign-off line - the Gmail signature provides it. Do NOT include any "Remember" alternating-time block - that was removed in 2026-05.

**Create as Gmail draft.** Never send without explicit user confirmation. Always show the draft link.

> **Critical:** the slides link in the email points to the title slide of THIS month's CR. Don't run Step 4 (slide staging) before the email is confirmed sent — recipients could otherwise open a deck where this month's slides have been shifted or the title slide overwritten.

## Step 4 - Stage next month's slides (after email is sent)

**Skip** if next month is a Quarterly Update month (Apr/Jul/Oct/Jan) - QU slides live in a separate deck.

**Goal:** copy this month's section to the beginning of the deck so the team has a draft skeleton to populate before next month's CR.

### 4.1 Identify "this month's section"

Find the slide range for this month's CR. Two methods, fall back in order:

1. **Footer-based (new sections from Jun 2026 onwards):** scan for slides with a footer text element containing `CR <Month> <Year>` for this month.
2. **Title-slide based (legacy sections):** find the title slide matching `<MONTH>: <YYYY-MM-DD>`. Section runs from there to the slide just before the next title slide (or end of deck).

If both methods disagree or yield nothing sensible, abort and ask.

### 4.2 Duplicate the section at position 1

For each slide in the section, use `duplicateObject` via `presentations.batchUpdate`. Then use `updateSlidesPosition` to move the duplicates to indexes 0 through N-1 (deck stays most-recent-first).

### 4.3 Update the new title slide

In the duplicated title slide (now slide 1):
- Replace month name + date with next CR's date (e.g. `May: 2026-05-21` -> `June: 2026-06-18`).
- Update CW number to next month's ISO calendar week.
- Replace the Recording link text with plain `[to be added]` (remove the URL link).

### 4.4 Add "Pending Update" red text box

Add a red text box at the top of each non-header slide in the new section. Marker placement matches the canonical Jun 2026 layout:

- **Marker on (relative positions from title slide, 1-indexed):** 2, 3, 4, 7, 10, 11, 12, 14, 15, 16, 17, 19, 20, 21, 22, 23, 24.
- **No marker (header / generic slides):** 1 (title), 5, 6, 8, 9, 13, 18, 25 (goodbye).

If the section length differs from 25 slides, abort and ask - the structure changed and the placement map needs updating.

Text box styling: text `Pending update`, font Outfit, ~14pt, bold, red (`#cc0000`), top of slide.

### 4.5 Add month footer to every non-title slide

Add a small text box bottom-right of slides 2 through end-of-section with text `CR <Month> <Year>` (e.g. `CR Jun 2026`). Spec - canonical reference is the manually-tweaked footer on slide 2 of the Jun 2026 section:

- **size:** 3000000 x 3000000 EMU (square base shape; the visible size comes from the scale below)
- **transform:** `scaleX: 0.4796`, `scaleY: 0.0735`, `translateX: 7705150`, `translateY: 4923000`, `unit: EMU` - yields an effective rendered footer of ~1.57" x 0.24" anchored near the bottom-right corner of a 10" x 5.625" slide
- **text style:** font Outfit, 8pt, light grey (`rgb(0.6, 0.6, 0.6)`), `bold: false`, `italic: false`, `weightedFontFamily: {fontFamily: "Outfit", weight: 400}`
- **paragraph style:** `alignment: END` (right-aligned)
- **send to back** via `updatePageElementsZOrder` with `operation: SEND_TO_BACK` - one request per footer (the API requires all elements be on the same page per request). This prevents the footer from covering content drawn under the slide-number area.

If the master deck layout ever changes (slide aspect ratio, brand fonts), re-derive this spec by reading the current footer on slide 2 of the most recent month's section.

### 4.6 Flag postponed content

After staging, scan the new section for any slide containing the text `[postponed]`. In the final report (Step 8), list each one with a line like:

> WARNING: Slide N (`<short title>`) was carried over from last month with `[postponed]`. Confirm whether to keep (will be covered now) or delete (will be deferred again).

Never delete automatically.

## Step 5 - Schedule next month's Slack prep reminder

**Compute next month's Cycle Review** (3rd Thursday of next month) and **reminder Monday** (meeting_date - 10 days):

```python
from datetime import date, timedelta
import calendar
nxt_year = year if month != 12 else year + 1
nxt_month = month + 1 if month != 12 else 1
thursdays = [d for d in calendar.Calendar().itermonthdates(nxt_year, nxt_month)
             if d.month == nxt_month and d.weekday() == 3]
next_meeting = thursdays[2]
reminder_monday = next_meeting - timedelta(days=10)
# Schedule for 09:30 Europe/Berlin
```

**Skip scheduling** if next month is a Quarterly Update month (Apr/Jul/Oct/Jan) - tell the user the QU workflow will handle it.

**Check OOO for Uri + Harnoor on meeting date** via Google Calendar free/busy for `uri.alarcon@deliveryhero.com` and `harnoor.chahal@deliveryhero.com`. OOO = all-day busy block. Normal meetings don't count.

**Assign owners using the alternation rule:**

- Host/Intro alternates between Uri and Harnoor monthly.
- OKRs = whoever is NOT hosting.
- **To determine who hosted last month:** read the most recent reminder message in `#log-customer-seamless-management` matching `:mega: Cycle Review NEXT week :mega:` and parse the Host/Intro line. The Slack record is the source of truth; do NOT guess from memory.
- If host is OOO: the other person does BOTH host and OKRs.
- If OKRs person is OOO: leave OKRs blank and add a line like `(OKRs owner to be confirmed in thread - <name> is OOO)`.
- Experiments owners are stable: Ege, Shradha, Alina. Always include all three.

**Slack reminder template:**

```
:mega: *Cycle Review NEXT week* :mega:

Hello team!
<DECK_URL|Slides> for *<NEXT_MONTH>'s* *Cycle Review next week (Thursday, <NEXT_MEETING_DATE>)* are ready to be populated.

Please reply on thread if you have a proposed *Focus Topic.*

For all sections, please aim to have it *ready by Tuesday EOD* so we have Wednesday to review and make changes where needed.

Proposed owners (ie present and responsible of slides being ready):
1. Host/Intro: <@HOST_USER_ID>
2. OKRs: <@OKRS_USER_ID>
3. Experiments: <@UPSV9R1DY> <@U06C8C36751> <@U09D065SRT6>

Please :+1:, or mention in the thread if anyone should change.
```

- Deck URL = master deck without slide anchor (next month's slides may not exist yet).
- Do NOT include the ":new: Shared one week earlier than usual" line - that was one-time framing.
- Do NOT include section 4 ("Initiatives by Strategy Pillar") - removed in 2026-05.
- Do NOT include the "keep the Roadmap updated for the screenshot" bullet - same reason.

**Schedule via Slack scheduled message:**
- channel: `C01RQ7FRP6Y`
- post_at: unix timestamp for reminder_monday at 09:30 Europe/Berlin
- Max 120 days out - always fine for a ~3 week schedule.

After scheduling, return the scheduled message ID and tell the user it can be edited/cancelled via Slack > Drafts & Sent before fire time.

## Step 6 - Create the post-meeting calendar reminder for next month

Create a 15-minute event on the user's `primary` calendar so whoever is available picks up next month's workflow run. Friday-morning timing gives Google Meet a full evening to process and attach the recording to the event before anyone runs the skill.

**Skip** if next month is a Quarterly Update month (Apr/Jul/Oct/Jan) - same logic as Step 4.

**Event parameters:**

- **start:** `next_meeting + 1 day` (Friday after the 3rd Thursday) at 09:00 Europe/Berlin
- **end:** same date at 09:15 Europe/Berlin
- **summary:** `Run Cycle Review post-meeting workflow (Claude skill)`
- **attendees:** `uri.alarcon@deliveryhero.com`, `harnoor.chahal@deliveryhero.com`, `florian.marienfeld@deliveryhero.com`
- **sendUpdates:** `all`
- **description (HTML):** brief - what to do + link to the shared Drive folder. Template:

```html
<b>Purpose:</b> Run the Claude Code skill that finalises the Seamless Cycle Review (drafts stakeholder email + schedules next month's Slack prep reminder).
<br><br>
<b>Anyone of us can run it</b> - first to claim it on this invite, please go ahead.
<br><br>
<b>Quick steps:</b>
<ol>
<li>Open Claude Code on your laptop.</li>
<li>Say: <b>"run the Cycle Review workflow"</b>.</li>
<li>Confirm focus topics if asked.</li>
<li>Review the Gmail draft. Tell Claude <b>"send it"</b> or click Send in Gmail.</li>
<li>Confirm here once sent so the others know.</li>
</ol>
<b>Skill + setup files:</b> <a href="https://drive.google.com/drive/folders/1C7KwaQapn_XO2Ivxh13Ac0L5ZAbuLQY7">Seamless Cycle Review - Claude skill (Drive folder)</a>
```

Use the Google Calendar create-event tool with `calendarId: primary`. Conflicts on the date are expected (other people's OOO, all-day blocks) - they don't block creation.

## Step 7 - Validate next month's CR (or QU) calendar invite

Find the next CPL Seamless Cycle Review **or** Quarterly Update event on the user's calendar (whichever is next). Verify:

1. **Date:** is the 3rd Thursday of next month.
2. **Time:** alternates between **10:00-11:00 Europe/Berlin** and **16:00-17:00 Europe/Berlin** with the previous CR/QU. QU months count in the alternation.

**Alternation anchor (verified state):**
- May 2026 CR = 10:00
- Jun 2026 CR = 16:00
- Jul 2026 QU = 10:00 (expected)
- Aug 2026 CR = 16:00 (expected)
- Sep 2026 CR = 10:00 (expected)
- Oct 2026 QU = 16:00 (expected)
- ...

If anything is off (wrong date, wrong time, missing event), **flag and ask** the user whether to fix it manually, ask Claude to fix it, or leave as-is. If leave-as-is, ask why - there may be a reason the skill should learn about (update this section).

Never auto-fix the calendar invite without explicit confirmation.

## Step 8 - Summary back to user

Report:
- Email draft created (link) > status (sent / awaiting send)
- Title slide recording link status (added / already present)
- Next month's slides staged (section duplicated, title updated, Pending Update markers added, footer added) - and flag any `[postponed]` slides for review
- Next month's Slack reminder scheduled (channel, fire time, owners, OOO result)
- Next month's calendar reminder created (event link, date, attendees)
- Next CR/QU calendar invite check result (OK or list of mismatches)
- Anything skipped / requires manual decision

## What stays manual

- Reviewing the Gmail draft and clicking Send.
- Populating the staged slides with actual content (the markers and footer are placeholders).
- Editing the scheduled Slack message if owners change before it fires.
- Editing the calendar reminder event if timing / attendees need to change.
- Fixing the next CR/QU calendar invite if it's off (manual or with confirmed Claude help).
- Deciding whether to keep or delete `[postponed]` slides.
- The Cycle Review meeting, slides preparation, recording upload.
- Quarterly Updates (Apr/Jul/Oct/Jan) - separate workflow.
