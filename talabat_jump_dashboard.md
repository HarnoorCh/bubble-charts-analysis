# Talabat Jump Station v2 — Experiment 538 Dashboard

Self-refreshing web dashboard comparing **Treatment1 / Treatment2 / Control** for the
Talabat Jump Station v2 ETA experiment (`2026-06-11_TB_Jump_Station_v2_All_Countries:538`).

## Live URL
https://storage.cloud.google.com/dh-cpl-seamless-dashboards/talabat_jump_dashboard.html

Opens for anyone in the access list once signed into their Google account
(`@deliveryhero.com` / `@talabat.com` / `@glovoapp.com`).

## KPIs
`jump_rate_pct`, `jump_magnitude_avg`, `seamless_fail_rate_pct`, `ccr_pct`, `hcsr_pct`,
`order_per_customer`, `num_orders` — shown at **global** + **country** level, per arm,
with daily trend lines and Δ-vs-Control tables.

> ⚠️ Values are **not** tested for statistical significance. Significance is calculated at the end of the experiment period.

## Files (all in `/Users/harnoor.chahal/ai/`)
| File | Purpose |
|---|---|
| `jump_station_3arm.sql` | BigQuery query — emits daily series + window totals (`day='TOTAL'`) per arm, global + country |
| `talabat_jump_build.py` | Runs the query via `bq`, embeds results, writes the HTML (Chart.js from CDN) |
| `talabat_jump_dashboard.html` | The generated dashboard (data inlined → opens offline) |
| `talabat_jump_deploy.sh` | Rebuild from BQ + upload to the GCS bucket |
| `talabat_jump_refresh.log` | Refresh run log |

## Refresh
**Manual:**
```bash
cd /Users/harnoor.chahal/ai && ./talabat_jump_deploy.sh
```
**Automatic:** launchd job `~/Library/LaunchAgents/com.dh.talabat-jump-refresh.plist`
runs daily at **09:00 Europe/Berlin** (Mac is on Berlin time). If the Mac is asleep/off
at 09:00, it runs once on next wake/boot (never per-missed-day). Needs internet + valid
gcloud ADC at run time.

Reload after editing the plist:
```bash
launchctl unload ~/Library/LaunchAgents/com.dh.talabat-jump-refresh.plist
launchctl load   ~/Library/LaunchAgents/com.dh.talabat-jump-refresh.plist
```

## Hosting
- Bucket: `gs://dh-cpl-seamless-dashboards` (project `logistics-data-storage-staging`, EU).
- Uniform bucket-level access ON, public access prevention ON.
- The data is aggregated (no PII), but internal/commercial — **do not make public**.

## Access model
The bucket project enforces **Domain Restricted Sharing**, so:
- Blanket `domain:deliveryhero.com` / `domain:talabat.com` grants are **silently stripped**.
- Access must be granted per **user** (or a Google Group) — `deliveryhero.com`, `talabat.com`, `glovoapp.com` identities are allowed.

Add a viewer:
```bash
gcloud storage buckets add-iam-policy-binding gs://dh-cpl-seamless-dashboards \
  --member=user:NAME@deliveryhero.com --role=roles/storage.objectViewer
```
Remove: same command with `remove-iam-policy-binding`.
List current viewers:
```bash
gcloud storage buckets get-iam-policy gs://dh-cpl-seamless-dashboards --format=json \
  | python3 -c "import json,sys;[print(m) for b in json.load(sys.stdin)['bindings'] if b['role'].endswith('objectViewer') for m in b['members']]"
```

Currently granted: 30 named members from Slack `#log-otx-talabat` (Talabat + DH + 2 Glovo)
+ owner. Source list was scraped from channel history — **silent members may be missing**;
add them individually as needed.

## Known limitations
- Charts need internet on first load (Chart.js via CDN); data itself is inlined/offline-safe.
- Mac-dependent refresh (see Hosting note above) — for a Mac-independent guaranteed 09:00
  refresh you'd need a server-side scheduler (Cloud Scheduler + Cloud Run).
- 4 Slack members rejected as "user does not exist" (likely left): moatassim.alhoseiny,
  victor.da, yashwant.chawhan, omar.abdulaal (talabat.com).
- 2 members not granted (Slack masked their emails): Elena Mostovova, Shady Dawood.
