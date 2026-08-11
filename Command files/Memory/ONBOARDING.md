# Seamless Onboarding Context for AI agents (Claude)

This file is for feeding to Claude (Claude Code, claude.ai, etc.) when you join the Seamless domain at Delivery Hero — PM, engineering, ops, or data science. It's factual team context, not a personal working-style file. For the human onboarding checklist (people to meet, admin tasks, rider-shift signup), see the [Seamless Newbie Onboarding Guide](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/953221127/MAKE+A+COPY+Seamless+-+NEWBIE+Onboarding+Guide+-+Product+Management) instead.

**This file is generated, not the source of truth.** The editable source lives on Confluence: [Seamless Onboarding Context for AI agents (Claude)](https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/2028896385). Edit there (restricted to `log-cpl-seamless-leads`), then re-publish — see "Keeping this current" at the bottom of that page.

---

## What Seamless is

The Seamless domain owns the **delivery promise, end to end**: setting expectations before an order is placed (Promised Delivery Time, vendor prep time) and managing/explaining deviations after (order tracking — ETA, map, statuses, notifications). These are treated as one system, not separate features, because a good promise and a good explanation-when-things-change are two halves of the same trust problem.

The core challenge is **managing uncertainty at scale, not eliminating it**: predicting what will actually happen rather than just the typical case, encoding that uncertainty into the promise shown to the customer, and communicating deviations calmly rather than letting customers discover them on their own. Current strategic focus areas are the scenarios where this is structurally hardest — **stacked orders** and **shops/q-commerce** — both of which matter disproportionately for the business (fleet efficiency and cost-per-order for stacking; non-food GMV growth for shops) and both of which run noisier/less reliably than the median restaurant order today.

Within the Customer Product Line (CPL), Seamless is one of three domains (alongside Choice and Pricing) — roughly, Seamless owns "fast and on time." CPL itself sits within Logistics, next to the Rider Product Line (RPL — riders, dispatch, fleet) and Service Product Line (SPL — customer service, HelpCenter, AI agents). See the [Logistics org chart](https://docs.google.com/presentation/d/1BB8SFblaGogbBYEliLUdKaEIxLzNMSpdk3oTBlgFr_E/edit) for the full picture across all three product lines.

Delivery Hero operates across 70+ countries under multiple brands (aka "platforms"): foodpanda, Foodora, and Yemeksepeti (together called **Pandora** internally — that's the name of the "platform"), Talabat, HungerStation, PedidosYa, Glovo, efood, and Woowa.

## Squads

| Squad | Jira | Location | Focus |
|---|---|---|---|
| Time Estimations (TES) | `LOGTES` | Berlin | ETA/PDT accuracy and predictions |
| Order Tracking Experience (OTX) | `LOGOTX` | Berlin | Customer-facing order tracking |
| Seamless Data Science (SDS) | `LOGSDS` | Berlin | ML/data science for the domain |
| Visual Motion Tracking (VMT) | `VMT` | Barcelona | Map, route, weather — the visual tracking experience, and the Flutter SDK |
| Trusted Lifecycle Tracking (TLT) | `TLT` | Barcelona | Order lifecycle: status, progression, notifications, on-time/late/slow |

VMT and TLT are the two focus areas Tracking UI (TUI) split into as of August 2026 — each now has its own PM/EM and its own Jira board (confirmed above), though people sometimes still say "TUI" out of habit.

**LPFR is not a squad.** It's the Jira board (`LPFR`) for inbound feature requests addressed to the Seamless domain — requests get routed from there to whichever squad actually owns the area.

Squad leadership (EMs, PMs) changes over time — check the [Seamless Domain Confluence space](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/36643272) or ask in `#log-seamless-domain` for the current roster rather than trusting a hardcoded name list here.

## Functions (cross-cutting, span all squads)

- **Product**
- **Design** (Product Design / UX Research)
- **Operations** — split into Product Performance and Product Analytics
- **Tech / Data Science**

## Product/service glossary (Seamless scope)

| Service | What it does |
|---|---|
| TES (Time Estimation Service) | Configures/serves prep time, PDT, EPT — the core time-estimation engine |
| TAPI (Tracking API) | Serves order lifecycle status and ETA to consumers (OTP, apps) |
| CNS (Customer Notification Service) | Delay/issue notifications to customers (formerly DNS) |
| Routes Service | Route/ETA computation feeding OTX |
| DTM (Delivery Time Model) | SDS model behind PDT |
| TTM (Tracking Time Model) | SDS model behind customer-facing ETA |
| Prep Time Model | SDS model for vendor estimated prep time |
| TSDK (Tracking SDK) | Embeddable tracking component, owned by component: VMT owns the Map Component, TLT owns the Order Status Component (OSC). Future components (e.g. rider-info widget, HelpCenter access) are TBD, including which squad will own them. |

Broader DH logistics services you'll hear referenced but that sit outside Seamless: **Hurrier** (the dispatcher's orchestration hub for Own Delivery — auto-dispatches orders, automates issue-handling workflows, and connects routing/ICE/TAPI; more than "just a dashboard"), **ICE** (issue rules), **Rooster** (fleet management), **DAS**/**DPS** (delivery areas/pricing), **Roadrunner** (rider app), **GoDroid** (vendor app). Full catalog: [Product Portal](https://product.deliveryhero.net/global-logistics/documentation/).

## Tools

| Tool | Use | Link |
|---|---|---|
| Slack | Primary day-to-day comms | Key channels: `#log-seamless-domain`, `#cpl-tes-int`, `#cpl-otx-int`, `#cpl-tui-int` (private); `#log-squad-timepred`, `#log-squad-otx`, `#log-squad-tracking-ui` (public) |
| Confluence | Documentation | [Seamless Domain space](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/36643272) |
| Jira | Sprint/ticket tracking | Boards per squad prefix above |
| GitHub | Code | [deliveryhero org](https://github.com/deliveryhero) — TES: `logistics-time-estimation-service` / `logistics-time-estimation-public`; TAPI: `logistics-tracking-api`; weather: `logistics-weather-service` |
| BigQuery | SQL analysis | Billing project `dhub-data-commune` or `logistics-customer-staging`; data in `fulfillment-dwh-production` — see BigQuery section below |
| Tableau | KPI dashboards | [Customer PL KPI Tracker](https://tableau.deliveryhero.net/#/site/GlobalStandardReporting/views/CustomerPLKPITracker/Seamless?:iid=2), [Data Dictionary](https://tableau.deliveryhero.net/#/site/GlobalStandardReporting/views/DataDictionary/Metrics?:iid=1) |
| Grafana | Real-time dashboards | [deliveryhero.grafana.net](https://deliveryhero.grafana.net/) (Data Science legacy: [dashboards.syslogistics.io](https://dashboards.syslogistics.io/)) |
| DataHub/Catalog | Table documentation | [catalog.fulfillment-dwh.com](https://catalog.fulfillment-dwh.com/) |

## Ways of working

- **Yearly**: [Logistics](https://docs.google.com/presentation/d/1rW9-yUi-cB5KMd2wXfYPsbdFiF8qM1WBZBorVF1iOzk/edit) and [CPL](https://docs.google.com/presentation/d/14UaT8uufmaEvNvvp-Zyg6BV4TUQdaT9C4-tHnGCi2FU/edit) strategy refresh, with Yearly Targets.
- **Quarterly**: CPL OKRs — [Okra](https://okra.deliveryhero.io/) is now the primary source of truth (the old OKR gsheet is frozen/read-only, kept only as a cross-check/fallback). Squad [Roadmaps](https://docs.google.com/spreadsheets/d/1OwXaCizo32kCixGa9Nb6KHq20OkvGRAQ69QndwMrwO8/edit?gid=1924645805#gid=1924645805) are a separate sheet, still actively used. Both feed the [Quarterly Update](https://docs.google.com/presentation/d/1hfEfiO4BkoZnvBOBM1afjzncj02VxXc1gMMaIdBAncE/edit) deck for regional stakeholders.
- **Monthly**: [Cycle Reviews](https://docs.google.com/presentation/d/1gMZl8BDLSU8D7BXrykJT7qp1TbdcFFn8kLW9mTVLxfI/edit) (stakeholder progress updates).
- **Sprints**: 2-week cycles per squad, with standard Agile ceremonies.
- **Recurring syncs**: Weekly Leads (Mondays), per-squad Product↔Ops syncs.

The Cycle Review and Quarterly Update links above are the 2026 decks — check whether a fresh one exists for 2027 before assuming these are current.

Don't hardcode current OKR/roadmap content here — it goes stale fast. Check Okra directly for OKRs, and the Roadmap sheet above for roadmaps.

## BigQuery conventions

> **⚠️ Not yet reviewed by Analytics.** These conventions are carried over from one PM's personal setup. Confirm with Gayatri Kanala and Tanmoy (Analytics) before treating this section as team-wide guidance.

- Data model has three layers: `dl` (raw), `cl` (curated — treat as the source of truth for most questions), `rl` (dashboard-serving). Prefer `cl` unless you have a specific reason to go lower.
- For order/delivery questions, the canonical table is `fulfillment-dwh-production.cl.orders`. It's batch, not real-time (~5hr lag) — fine for yesterday-and-earlier, unreliable for "today so far."
- Always filter on the partition column (`created_date`) — an unfiltered query scans the whole table.
- Never `SELECT *` on large tables. Use `INFORMATION_SCHEMA.COLUMNS` (near-zero cost) to check field names before writing a query, not a `LIMIT 1` on the full table.
- Standard lateness definition: `(actual_delivery_time - promised_delivery_time) > 600` seconds. `timings.order_delay` is **not** a lateness flag (it's a fleet-busyness proxy) — a common silent mistake.
- `*_stream` tables (e.g. `cl._orders_stream`) contain duplicates — dedupe before using them.
- Prefer aggregated tables (`curated_data_shared_*`, `agg_orders_daily`, etc.) over raw event tables when they exist — cheaper and usually sufficient.

## Key reference links

- [Seamless org chart](https://docs.google.com/presentation/d/1hYnZHNfgcKKb_ZUb2YpM372wskxDgS2AyHVR4RDEMY4/edit) — Rose Mullen keeps this current; treat it as the source of truth over any name list in this file.
- [Logistics org chart](https://docs.google.com/presentation/d/1BB8SFblaGogbBYEliLUdKaEIxLzNMSpdk3oTBlgFr_E/edit) — the wider picture: Rider, Customer (CPL), and Service product lines.
- [Glossary of DH abbreviations](https://deliveryhero.atlassian.net/wiki/display/GCC/Glossary)
- [Seamless experimentation home](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/36652978)
- [KPI & Dashboard Inventory](https://docs.google.com/spreadsheets/d/145vDyiPbZKXIuk7RVKU5P0_af63URRWLgC3-RciS0oo/edit#gid=505602169)
- Human onboarding checklist (people, admin tasks, ways of working — PM-focused but broadly useful): [Seamless Newbie Onboarding Guide](https://atlassian.cloud.deliveryhero.group/wiki/spaces/LOGCPL/pages/953221127/MAKE+A+COPY+Seamless+-+NEWBIE+Onboarding+Guide+-+Product+Management)
- [DH AI Skill Guideline](https://docs.google.com/document/d/12O_MuDEDZ1plkGrBjAM4YIqdhLhjAohw-IP6TGwoRhs/edit?tab=t.mu6ymar88ko4) — org-wide standard for writing/reviewing Claude Skills (structure, security, naming, review checklist). Relevant if you (the AI agent reading this) are asked to build a Skill for this domain.

---

## Keeping this current

**Editing:** this content is edit-restricted to `log-cpl-seamless-leads` on its [Confluence source page](https://deliveryhero.atlassian.net/wiki/spaces/LOGCPL/pages/2028896385). If you're a team lead, edit there directly — fix what's wrong, add what's missing (Ops/Design/Engineering/DS context is all welcome, not just PM).

**Publishing your edit (do this right after you save a change on Confluence):**

1. Open a Claude session that has access to that Confluence page (Claude Code with the Atlassian MCP connected, or claude.ai with the Atlassian connector).
2. Ask it: *"Read this Confluence page [paste the page URL], save its content as `ONBOARDING.md` in the current directory, then use the `ShareOnboardingGuide` tool to publish it."*
3. Claude will upload it to the existing shared org guide — same link as before, content refreshed. If your Claude doesn't have that tool available, or this doesn't match the Confluence page, ping Uri Alarcon.
