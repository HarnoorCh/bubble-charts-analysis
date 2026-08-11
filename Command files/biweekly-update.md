Create the bi-weekly CPL Seamless Confluence page for the current week and post a Slack notification to #cpl-ops-perf-seamless.

## Steps
# CPL Seamless Automation Logic

**1. Environment Setup
Run this Python snippet to initialize dynamic variables:
```python
from datetime import date
d = date.today()
N = d.isocalendar()[1]
YEAR = d.year
PREV_1 = N - 2
PREV_2 = N - 4



**2. Determine page type**
PAGE_TYPE = "KPI" if N % 2 != 0 else "Initiatives"

**3. Check for already-existing pages (skip creation, just post Slack)**
- W19 KPI: https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/1567424618/
- W20 Initiatives: https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/1619263928/
If the current week is one of the above, skip to step 6 with that URL.

**4. Search for the previous same-type page to carry forward**

Use `searchConfluenceUsingCql` (cloudId: `deliveryhero.atlassian.net`):
- KPI:         `title = "W{PREV} {YEAR} - Bi-Weekly KPI Update" AND space = "LOGCPL"`
- Initiatives: `title ~ "W{PREV} {YEAR}" AND title ~ "Initiatives" AND space = "LOGCPL"`

If not found, try N-4 before the empty fallback:
- KPI:         `title = "W{N-4} {YEAR} - Bi-Weekly KPI Update" AND space = "LOGCPL"`
- Initiatives: `title ~ "W{N-4} {YEAR}" AND title ~ "Initiatives" AND space = "LOGCPL"`

If a previous page is found (either N-2 or N-4), fetch its content (`getConfluencePage`, contentFormat: markdown) and use it as the base with these transformations:
- Replace `W{PREV}` or `W{N-4}` column header references with `W{N}` (week numbers in table headers only)
- For KPI pages: clear the **Δ** and **Status** columns in all domain KPI tables (set cells to blank) so owners aren't misled by stale values from two weeks ago. Leave W{PREV} data column values intact as reference.
- Keep all experiment names, statuses, ETAs, and owners in Initiatives pages as-is.

If no previous page is found at all, use the fallback templates at the bottom of this file.

**5. Create the Confluence page**
Tool: `createConfluencePage`
- cloudId: `deliveryhero.atlassian.net`
- spaceId: `36634645`
- parentId: `1566834838` (Q2 2026 folder)
- contentFormat: `markdown`
- status: `current`
- title: `W{N} {YEAR} - Bi-Weekly KPI Update` or `W{N} {YEAR} - Bi-Weekly Initiatives Update`

Page URL = `https://deliveryhero.atlassian.net/wiki` + `response.links.webui`

**6. Post to Slack** (`mcp__plugin_slack_slack__slack_send_message`, channel: `C051L8NRY69`)

For KPI weeks:
> <!here> 👋 *W{N} {YEAR} - Bi-Weekly KPI Update* is ready for this week's call. Please fill in your sections before the meeting: {URL}
> Owners: TSDK & OTX → Shradha | PDT Ranges & PDT Model → Ege | EPTs → Alina

For Initiatives weeks:
> <!here> 👋 *W{N} {YEAR} - Bi-Weekly Initiatives Update* is ready for this week's call. Please update experiment statuses before the meeting: {URL}
> Owners: TSDK & OTX → Shradha | PDTs → Ege | EPTs → Alina

---

## Fallback: KPI Template

```markdown
## 🎯 Yearly OKR Progress

_Quarter Goal = {YEAR} milestone. Current = latest filled week. 🟢 On track · 🟡 At risk · 🔴 Off track_

| **Yearly Target** | **Metric** | **Q2 {YEAR} Goal** | **Current (W{N})** | **vs. Q2 Goal** | **Status** |
| --- | --- | --- | --- | --- | --- |
| Increase annualized GMV by optimizing time estimates | Annualized GMV uplift (m€) | 25 m€ |  |  |  |
| Increase on-time rate for stacked orders | % orders within ±10 min of PDT | 72.4% |  |  |  |
| Decrease late rate for shops | % orders >+15 min from PDT SV | 8.7% |  |  |  |
| Increase Pickup Efficiency Score (PES/PET) | PET improvement (ppt) | 4.4% |  |  |  |

---

## 📊 Key KPIs by Domain

### Tracking SDK \[TSDK\] - @Shradha Jain

| **KPI** | **W{PREV}** | **W{N}** | **Δ** | **Target** | **Status** |
| --- | --- | --- | --- | --- | --- |
| Map v2 adoption (% of eligible orders) |  |  |  |  |  |
| active A/B tests |  |  |  |  |  |
| A/B tests with positive outcome (QTD) |  |  |  |  |  |

### Order Tracking Experience \[OTX\] - @Shradha Jain

| **KPI** | **Q2** | **W{PREV}** | **W{N}** | **Δ** | **Target** | **Status** |
| --- | --- | --- | --- | --- | --- | --- |
| PDT-ETA alignment rate |  |  |  |  |  |  |
| Customer Contact Rate (CCR) from ETA/delay |  |  |  |  |  |  |
| CNS notification % |  |  |  |  |  |  |
| OTX Jump rate |  |  |  |  |  |  |

### PDT Ranges - @Ege Sözgen

| **KPI** | **Q2** | **W{PREV}** | **W{N}** | **Δ** | **Target** | **Status** |
| --- | --- | --- | --- | --- | --- | --- |
| Annualized GMV uplift from range experiments (m€) |  |  |  |  | 25 m€ (Q2) |  |
| #active range experiments |  |  |  |  |  |  |

### PDT Model - @Ege Sözgen

| **KPI** | **Q2** | **W{PREV}** | **W{N}** | **Δ** | **Target** | **Status** |
| --- | --- | --- | --- | --- | --- | --- |
| %on-time (+/-10mins) |  |  |  |  |  |  |
| On-time rate — stacked orders (±10 min from PDT) |  |  |  |  | 72.4% (Q2) |  |
| Late rate — shops (>+15 min from PDT SV) |  |  |  |  | ≤8.7% (Q2) |  |

### Estimated Preptimes \[EPTs\] - @Alina Kim

| **KPI** | **Q2** | **W{PREV}** | **W{N}** | **Δ** | **Target** | **Status** |
| --- | --- | --- | --- | --- | --- | --- |
| Pickup Efficiency Time / PET (ppt improvement) |  |  |  |  | 4.4% (Q2) |  |
| Vendor prep time adjustment (% within EPT adjustment) |  |  |  |  |  |  |
| %orders with fixed EPTs |  |  |  |  |  |  |
```

---

## Fallback: Initiatives Template

```markdown
## Tracking SDK \[TSDK\]

#### Things to look into:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Next Steps/Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

#### Experiments:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Next Steps/Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Order Tracking Experience \[OTX\]

#### Things to look into:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Next Steps/Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

#### Experiments:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Promised Delivery Time \[PDTs\]

#### Things to look into:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

#### Experiments:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

## Estimated Preptimes \[EPTs\]

#### Things to look into:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Next Steps/Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |

#### Experiments:
| **Problem Statement** | **Platform** | **Status** | **ETA** | **Outcome** | **Owner** |
| --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |
```
