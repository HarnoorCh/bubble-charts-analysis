#!/usr/bin/env python3
"""
Build the Country-Ranking dashboard.

Assembles ONE combined per-country BigQuery scan from kpi_catalog.json (every
ratio/average signal becomes a column), runs it via the `bq` CLI, merges static
external signals (signals_external.json) and any custom history-derived signals,
then embeds the whole thing into a self-contained HTML file whose ranking is
re-computed client-side as you toggle signals / direction / weights.

    python3 build_dashboard.py              # full build -> country_ranking_dashboard.html
    python3 build_dashboard.py --dry-run    # print the assembled SQL + estimated bytes, no build
    python3 build_dashboard.py --add-history <id> --value-col <col> [--country-col country_code]
            [--dir lower|higher] [--weight 1] [--label "..."] [--group Custom] [--fmt pct2]
                                            # promote a past query (from query_history.json) into a
                                            # persistent custom ranking signal, then rebuild

Mirrors the build idiom in ../talabat_jump_build.py (TEMPLATE + placeholders,
bq --format=json via subprocess, string->float coercion, Chart.js from CDN).
"""

import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
CATALOG_PATH = HERE / "kpi_catalog.json"
EXTERNAL_PATH = HERE / "signals_external.json"
HISTORY_PATH = HERE / "query_history.json"
OUT = HERE / "country_ranking_dashboard.html"

WINDOW_DAYS = 30
MIN_THRESHOLD = 10000         # min valid orders for a country to be ranked
BASE_TABLE = "fulfillment-dwh-production.cl.orders"


# --------------------------------------------------------------------------- #
# SQL assembly
# --------------------------------------------------------------------------- #
def base_cte() -> str:
    """Row-level projection shared by every catalog expression (single scan)."""
    return f"""
WITH base AS (
  SELECT
    o.country_code,
    o.order_id,
    o.vendor.vertical_type                                    AS vertical_type,
    d.stacked_deliveries                                      AS stacks,
    o.timings.actual_delivery_time   / 60                     AS dt_min,
    o.timings.promised_delivery_time / 60                     AS pdt_min,
    o.timings.rider_late             / 60                     AS rider_late_min,
    o.estimated_prep_time            / 60                     AS ept_min,
    o.timings.avoidable_wait_time    / 60                     AS awt_min,
    o.timings.at_vendor_time         / 60                     AS avt_min,
    TIMESTAMP_DIFF(d.rider_picked_up_at, o.created_at, MINUTE) AS created_to_pu,
    d.timings.rider_reaction_time                            AS rider_reaction_time
  FROM `{BASE_TABLE}` o
  LEFT JOIN UNNEST(deliveries) d ON d.is_primary
  WHERE o.created_date BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL {WINDOW_DAYS} DAY)
                           AND DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    AND o.is_preorder IS FALSE
    AND o.order_status = 'completed'
    AND o.country_code != 'kr2'
)""".strip("\n")


# Fixed stacked-vs-non-stacked comparison columns (always computed in the same
# scan; feed the "Stacked vs non-stacked" tab). stacked = stacks>0, non-stacked = stacks=0.
COMPARE_COLS = """
  SAFE_DIVIDE(COUNTIF(stacks > 0 AND pdt_min IS NOT NULL AND ABS(dt_min - pdt_min) <= 10), COUNTIF(stacks > 0 AND pdt_min IS NOT NULL)) * 100 AS cmp_ot_stacked,
  SAFE_DIVIDE(COUNTIF(stacks = 0 AND pdt_min IS NOT NULL AND ABS(dt_min - pdt_min) <= 10), COUNTIF(stacks = 0 AND pdt_min IS NOT NULL)) * 100 AS cmp_ot_nonstacked,
  AVG(IF(stacks > 0, dt_min, NULL))  AS cmp_dt_stacked,
  AVG(IF(stacks = 0, dt_min, NULL))  AS cmp_dt_nonstacked,
  COUNTIF(stacks > 0) AS cmp_n_stacked,
  COUNTIF(stacks = 0) AS cmp_n_nonstacked""".rstrip()

COMPARE_KEYS = ["cmp_ot_stacked", "cmp_ot_nonstacked", "cmp_dt_stacked",
                "cmp_dt_nonstacked", "cmp_n_stacked", "cmp_n_nonstacked"]


def build_combined_sql(signals) -> str:
    """Assemble the one per-country query from ratio/average catalog signals."""
    cols = []
    for s in signals:
        if s.get("type") not in ("ratio", "average"):
            continue
        expr = s.get("expr")
        if not expr:
            continue
        cols.append(f"  {expr} AS {s['key']}")
    parts = ["  COUNT(*) AS valid_orders"]
    if cols:
        parts.append(",\n".join(cols))
    parts.append(COMPARE_COLS.strip("\n"))
    select_body = ",\n".join(parts)
    return f"""{base_cte()}
SELECT
  country_code,
{select_body}
FROM base
GROUP BY country_code
HAVING valid_orders >= {MIN_THRESHOLD}
ORDER BY country_code
""".strip("\n")


# --------------------------------------------------------------------------- #
# bq helpers
# --------------------------------------------------------------------------- #
def run_bq(sql: str, dry_run: bool = False):
    """Run SQL via the bq CLI. Returns list-of-dicts (or prints dry-run info)."""
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=100000"]
    if dry_run:
        cmd.append("--dry_run")
    proc = subprocess.run(cmd, input=sql, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"bq query failed (exit {proc.returncode})")
    if dry_run:
        # bq prints a human "This query will process N bytes" line to stderr.
        sys.stderr.write(proc.stderr)
        return []
    rows = json.loads(proc.stdout) if proc.stdout.strip() else []
    flat = []
    for item in rows:
        flat.extend(item) if isinstance(item, list) else flat.append(item)
    return flat


def coerce(rows, keys):
    for r in rows:
        for k in keys:
            v = r.get(k)
            if v is not None and v != "":
                try:
                    r[k] = float(v)
                except (TypeError, ValueError):
                    r[k] = None
            else:
                r[k] = None
    return rows


# --------------------------------------------------------------------------- #
# data assembly
# --------------------------------------------------------------------------- #
def load_json(path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def load_history():
    hist = load_json(HISTORY_PATH, [])
    return {h["id"]: h for h in hist}


def merge_external(by_country, signals, external):
    """Merge type=external signal columns into per-country rows."""
    for s in signals:
        if s.get("type") != "external":
            continue
        table = external.get(s["key"], {})
        for cc, val in table.items():
            if cc not in by_country:
                continue  # don't reintroduce sub-threshold / non-ranked countries
            try:
                by_country[cc][s["key"]] = float(val)
            except (TypeError, ValueError):
                by_country[cc][s["key"]] = None


def merge_custom(by_country, signals, history):
    """Run each type=custom signal's history query as a separate bq job, join by country."""
    for s in signals:
        if s.get("type") != "custom":
            continue
        src = s.get("source", {})
        hid, ccol, vcol = src.get("history_id"), src.get("country_col", "country_code"), src.get("value_col")
        h = history.get(hid)
        if not h or not h.get("sql") or not vcol:
            print(f"  ! skipping custom signal {s['key']}: missing history/sql/value_col", file=sys.stderr)
            continue
        print(f"  running custom signal {s['key']} (history {hid}) ...", file=sys.stderr)
        rows = coerce(run_bq(h["sql"]), [vcol])
        for r in rows:
            cc = r.get(ccol)
            if cc is None:
                continue
            by_country.setdefault(cc, {"country_code": cc, "valid_orders": None})[s["key"]] = r.get(vcol)


def assemble_rows(signals, external, history):
    sql = build_combined_sql(signals)
    print("Running combined per-country scan via bq ...", file=sys.stderr)
    rows = run_bq(sql)
    numeric_keys = ["valid_orders"] + COMPARE_KEYS + [s["key"] for s in signals if s.get("type") in ("ratio", "average")]
    rows = coerce(rows, numeric_keys)
    by_country = {r["country_code"]: r for r in rows}
    print(f"  -> {len(by_country)} countries from main scan", file=sys.stderr)
    merge_external(by_country, signals, external)
    merge_custom(by_country, signals, history)
    return list(by_country.values())


# --------------------------------------------------------------------------- #
# HTML build
# --------------------------------------------------------------------------- #
def build(signals, rows, history_list):
    window_start = (date.today() - timedelta(days=WINDOW_DAYS)).isoformat()
    window_end = (date.today() - timedelta(days=1)).isoformat()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = (
        TEMPLATE
        .replace("/*CATALOG*/", json.dumps(signals))
        .replace("/*ROWS*/", json.dumps(rows))
        .replace("/*HISTORY*/", json.dumps(history_list))
        .replace("{{WINDOW}}", f"{window_start} → {window_end}")
        .replace("{{GENERATED}}", generated)
        .replace("{{THRESHOLD}}", f"{MIN_THRESHOLD:,}")
    )
    OUT.write_text(html)
    print(f"Wrote {OUT}", file=sys.stderr)


# --------------------------------------------------------------------------- #
# --add-history
# --------------------------------------------------------------------------- #
def add_history_signal(args):
    catalog = load_json(CATALOG_PATH, {"signals": []})
    history = load_history()
    h = history.get(args.add_history)
    if not h:
        raise SystemExit(f"history id '{args.add_history}' not found in {HISTORY_PATH.name} "
                         f"(run extract_history.py first)")
    if not h.get("sql"):
        raise SystemExit(f"history id '{args.add_history}' has no runnable SQL "
                         f"(stored verbatim / non-inline) — cannot promote to a signal")
    key = "hist_" + (args.value_col or "metric")
    # de-dupe key
    existing = {s["key"] for s in catalog["signals"]}
    base_key = key
    i = 2
    while key in existing:
        key = f"{base_key}_{i}"
        i += 1
    entry = {
        "key": key,
        "label": args.label or f"{args.value_col} (history)",
        "group": args.group or "Custom",
        "dir": args.dir,
        "fmt": args.fmt,
        "default_weight": args.weight,
        "type": "custom",
        "active": True,
        "source": {"history_id": args.add_history, "country_col": args.country_col, "value_col": args.value_col},
    }
    catalog["signals"].append(entry)
    CATALOG_PATH.write_text(json.dumps(catalog, indent=2) + "\n")
    print(f"Added custom signal '{key}' from history {args.add_history}. Rebuilding ...", file=sys.stderr)


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description="Build the country-ranking dashboard")
    ap.add_argument("--dry-run", action="store_true", help="print assembled SQL + estimated bytes, then exit")
    ap.add_argument("--add-history", metavar="ID", help="promote a query_history.json entry into a custom signal")
    ap.add_argument("--value-col", help="(with --add-history) result column holding the per-country value")
    ap.add_argument("--country-col", default="country_code", help="(with --add-history) result country column")
    ap.add_argument("--dir", choices=["higher", "lower"], default="lower", help="(with --add-history) better direction")
    ap.add_argument("--weight", type=float, default=1, help="(with --add-history) default weight")
    ap.add_argument("--label", help="(with --add-history) UI label")
    ap.add_argument("--group", help="(with --add-history) UI group")
    ap.add_argument("--fmt", default="pct2", help="(with --add-history) formatter (pct2|pct1|pct3|min2|sec0|int)")
    args = ap.parse_args()

    if args.add_history:
        if not args.value_col:
            raise SystemExit("--add-history requires --value-col")
        add_history_signal(args)

    catalog = load_json(CATALOG_PATH, {"signals": []})
    signals = catalog["signals"]

    if args.dry_run:
        sql = build_combined_sql(signals)
        print("=" * 70)
        print(sql)
        print("=" * 70)
        run_bq(sql, dry_run=True)
        return

    external = load_json(EXTERNAL_PATH, {})
    history = load_history()
    rows = assemble_rows(signals, external, history)
    build(signals, rows, list(history.values()))


# --------------------------------------------------------------------------- #
# HTML template
# --------------------------------------------------------------------------- #
TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Country Ranking Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{
    --bg:#ffffff;--panel:#ffffff;--panel2:#f8fafc;--ink:#131732;--muted:#6b7280;
    --line:#e5e7eb;--brand:#131732;--accent:#d61f26;--good:#15803d;--bad:#b91c1c;--gold:#fde68a;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  .wrap{max-width:1280px;margin:0 auto;padding:26px 22px 70px;}
  header h1{margin:0 0 4px;font-size:22px;color:var(--brand);}
  header .meta{color:var(--muted);font-size:13px;}
  header .meta b{color:var(--ink);}
  h2{font-size:13px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);
    border-bottom:2px solid var(--line);padding-bottom:8px;margin:30px 0 16px;}
  .layout{display:grid;grid-template-columns:320px 1fr;gap:22px;align-items:start;}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;
    box-shadow:0 1px 2px rgba(19,23,50,.04);}
  .sig{border-bottom:1px solid var(--line);padding:9px 2px;}
  .sig:last-child{border-bottom:none;}
  .sig .top{display:flex;align-items:center;gap:8px;}
  .sig .top label{flex:1;font-size:13px;cursor:pointer;}
  .sig .grp{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em;}
  .sig .row2{display:flex;gap:8px;margin-top:6px;padding-left:24px;}
  .sig.off{opacity:.5;}
  select,input[type=number]{background:var(--panel);color:var(--ink);border:1px solid var(--line);
    border-radius:7px;padding:5px 8px;font-size:12px;}
  input[type=number]{width:62px;}
  .ctrlbar{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin-bottom:14px;font-size:13px;color:var(--muted);}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th,td{padding:7px 9px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap;}
  th:first-child,td:first-child,th:nth-child(2),td:nth-child(2){text-align:left;}
  thead th{color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;letter-spacing:.03em;cursor:pointer;}
  tbody tr:hover{background:var(--panel2);}
  tr.win{background:#fffbeb;}
  tr.win td:first-child{font-weight:700;}
  .sub{font-size:10.5px;color:var(--muted);display:block;margin-top:1px;}
  .badge{display:inline-block;background:var(--brand);color:#fff;border-radius:6px;padding:1px 7px;font-size:11px;}
  .chartbox{position:relative;height:430px;}
  .foot{color:var(--muted);font-size:12px;margin-top:26px;}
  code{background:var(--panel2);padding:1px 5px;border-radius:4px;}
  .hist .item{border-bottom:1px solid var(--line);padding:10px 2px;}
  .hist .item h4{margin:0 0 3px;font-size:13px;font-weight:600;}
  .hist .item .m{font-size:11px;color:var(--muted);margin-bottom:5px;}
  .hist pre{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:8px;
    font-size:11px;max-height:160px;overflow:auto;white-space:pre-wrap;margin:5px 0;}
  .hist .cmd{font-size:11px;color:var(--good);background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;
    padding:6px 8px;white-space:pre-wrap;}
  button{background:var(--brand);color:#fff;border:none;border-radius:7px;padding:5px 10px;font-size:12px;cursor:pointer;}
  button.sec{background:var(--panel);color:var(--ink);border:1px solid var(--line);}
  input[type=text]{width:100%;padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:13px;}
  .tabs{display:flex;gap:8px;margin:30px 0 0;}
  .tabs button{background:var(--panel2);color:var(--ink);border:1px solid var(--line);}
  .tabs button.on{background:var(--brand);color:#fff;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Country Ranking Dashboard</h1>
    <div class="meta">window <b>{{WINDOW}}</b> &middot; generated <b>{{GENERATED}}</b>
      &middot; min orders <b>{{THRESHOLD}}</b> &middot; <span id="nctry"></span> countries
      &middot; lower score = better</div>
  </header>

  <div class="tabs">
    <button id="tabRank" class="on" onclick="showTab('rank')">Ranking</button>
    <button id="tabStack" onclick="showTab('stack')">Stacked vs non-stacked</button>
    <button id="tabHist" onclick="showTab('hist')">My query history</button>
  </div>

  <!-- RANKING TAB -->
  <div id="paneRank">
    <div class="layout" style="margin-top:16px;">
      <div class="panel">
        <h2 style="margin-top:0;">Signals</h2>
        <div id="signals"></div>
        <div style="margin-top:12px;">
          <button class="sec" onclick="resetSignals()">Reset to defaults</button>
        </div>
      </div>
      <div>
        <div class="ctrlbar">
          <span>Top-N chart:
            <select id="topn"><option>10</option><option selected>15</option><option>25</option><option>9999</option></select>
          </span>
          <span id="activeCount"></span>
        </div>
        <div class="panel chartbox"><canvas id="bar"></canvas></div>
        <div class="panel" style="margin-top:16px;overflow-x:auto;">
          <table id="rankTable"></table>
        </div>
      </div>
    </div>
  </div>

  <!-- STACKED VS NON-STACKED TAB -->
  <div id="paneStack" style="display:none;margin-top:16px;">
    <div class="ctrlbar"><span>Top <b id="stackN">10</b> countries by the <b>current ranking</b> &middot; stacked (<span style="color:var(--accent)">red</span>) vs non-stacked (<span style="color:var(--brand)">navy</span>). Change signals on the Ranking tab to update this set.</span></div>
    <div class="layout" style="grid-template-columns:1fr 1fr;">
      <div class="panel"><h2 style="margin-top:0;">% on-time (±10 min)</h2><div class="chartbox"><canvas id="cmpOt"></canvas></div></div>
      <div class="panel"><h2 style="margin-top:0;">Delivery time (min)</h2><div class="chartbox"><canvas id="cmpDt"></canvas></div></div>
    </div>
    <div class="panel" style="margin-top:16px;overflow-x:auto;"><table id="cmpTable"></table></div>
  </div>

  <!-- HISTORY TAB -->
  <div id="paneHist" style="display:none;margin-top:16px;">
    <div class="panel hist">
      <input type="text" id="histSearch" placeholder="Search past queries by intent, table, or text…">
      <div id="histList" style="margin-top:12px;"></div>
    </div>
  </div>

  <div class="foot">
    Source: <code>fulfillment-dwh-production.cl.orders</code> (primary deliveries, completed non-preorder).
    Rebuild: <code>python3 build_dashboard.py</code>. Add a history signal:
    <code>python3 build_dashboard.py --add-history &lt;id&gt; --value-col &lt;col&gt; --dir lower --weight 1</code>.
    Country codes shown raw (anonymized; not ISO).
  </div>
</div>

<script>
const CATALOG = /*CATALOG*/;
const ROWS    = /*ROWS*/;
const HISTORY = /*HISTORY*/;

const FMT = {
  pct2:v=>v.toFixed(2)+"%", pct1:v=>v.toFixed(1)+"%", pct3:v=>v.toFixed(3)+"%",
  min2:v=>v.toFixed(1)+"m", sec0:v=>Math.round(v)+"s", int:v=>v.toLocaleString(),
};
const fmt=(s,v)=> v==null?"—":(FMT[s.fmt]||(x=>x))(v);

// working signal state (cloned from catalog so Reset works)
let SIG = [];
function initSignals(){ SIG = CATALOG.map(s=>({...s, weight:s.default_weight, active:!!s.active})); }
initSignals();

document.getElementById("nctry").textContent = ROWS.length;

// ---- scoring: weighted rank-sum, lower = better ----
function rankSum(){
  const active = SIG.filter(s=>s.active && s.weight>0);
  const perRank = {};
  active.forEach(s=>{
    const present = ROWS.filter(r=>r[s.key]!=null);
    const missing = ROWS.filter(r=>r[s.key]==null);
    present.sort((a,b)=> s.dir==="higher" ? b[s.key]-a[s.key] : a[s.key]-b[s.key]);
    const ranks={}; present.forEach((r,i)=>ranks[r.country_code]=i+1);
    const worst=present.length+1; missing.forEach(r=>ranks[r.country_code]=worst);
    perRank[s.key]=ranks;
  });
  const scored = ROWS.map(r=>{
    let total=0;
    active.forEach(s=> total += perRank[s.key][r.country_code]*s.weight);
    return {...r, _score: active.length?total:null, _perRank:perRank};
  });
  scored.sort((a,b)=>(a._score??Infinity)-(b._score??Infinity));
  scored.forEach((r,i)=> r._rank = r._score==null?null:i+1);
  return {scored, active, perRank};
}

// ---- signal controls ----
function renderSignals(){
  const host=document.getElementById("signals"); host.innerHTML="";
  SIG.forEach((s,idx)=>{
    const div=document.createElement("div");
    div.className="sig"+(s.active?"":" off");
    div.innerHTML=`
      <div class="top">
        <input type="checkbox" ${s.active?"checked":""} data-i="${idx}" data-k="active">
        <label>${s.label} <span class="grp">${s.group}</span></label>
      </div>
      <div class="row2">
        <select data-i="${idx}" data-k="dir">
          <option value="higher" ${s.dir==="higher"?"selected":""}>higher = better</option>
          <option value="lower" ${s.dir==="lower"?"selected":""}>lower = better</option>
        </select>
        <input type="number" step="0.5" min="0" value="${s.weight}" data-i="${idx}" data-k="weight" title="weight">
      </div>`;
    host.appendChild(div);
  });
  host.querySelectorAll("[data-k]").forEach(el=>{
    el.addEventListener("change", e=>{
      const i=+e.target.dataset.i, k=e.target.dataset.k;
      if(k==="active") SIG[i].active=e.target.checked;
      else if(k==="weight") SIG[i].weight=parseFloat(e.target.value)||0;
      else SIG[i].dir=e.target.value;
      renderSignals(); render();
    });
  });
}
function resetSignals(){ initSignals(); renderSignals(); render(); }

// ---- render table + chart ----
let bar;
function render(){
  const {scored, active, perRank} = rankSum();
  document.getElementById("activeCount").textContent =
    active.length? `${active.length} active signal(s)` : "No active signals — pick at least one";

  // table
  let h="<thead><tr><th>#</th><th>Country</th><th>Score</th>";
  active.forEach(s=>h+=`<th>${s.label}</th>`); h+="</tr></thead><tbody>";
  if(!active.length){ h+=`<tr><td colspan="3" style="text-align:left;color:var(--muted)">Select a signal to rank.</td></tr>`; }
  scored.forEach(r=>{
    h+=`<tr class="${r._rank===1?"win":""}"><td>${r._rank??"—"}${r._rank===1?' <span class="badge">best</span>':""}</td>`+
       `<td>${r.country_code.toUpperCase()}</td>`+
       `<td><b>${r._score==null?"—":r._score.toFixed(1)}</b></td>`;
    active.forEach(s=>{
      h+=`<td>${fmt(s,r[s.key])}<span class="sub">rk ${perRank[s.key][r.country_code]}</span></td>`;
    });
    h+="</tr>";
  });
  document.getElementById("rankTable").innerHTML=h+"</tbody>";

  if(document.getElementById("paneStack").style.display!=="none") renderStack();

  // chart: top-N by score (lowest on top)
  const n=Math.min(+document.getElementById("topn").value, scored.length);
  const top=scored.filter(r=>r._score!=null).slice(0,n);
  const labels=top.map(r=>r.country_code.toUpperCase());
  const data=top.map(r=>r._score);
  if(bar) bar.destroy();
  bar=new Chart(document.getElementById("bar"),{
    type:"bar",
    data:{labels,datasets:[{label:"Score (lower=better)",data,
      backgroundColor:top.map((r,i)=>i===0?"#d61f26":"#131732")}]},
    options:{indexAxis:"y",responsive:true,maintainAspectRatio:false,
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`score ${c.parsed.x.toFixed(1)}`}}},
      scales:{x:{beginAtZero:true,title:{display:true,text:"weighted rank-sum"}},y:{grid:{display:false}}}}
  });
}
document.getElementById("topn").addEventListener("change",render);

// ---- stacked vs non-stacked (top 10 by current ranking) ----
let cmpOt, cmpDt;
function groupedBar(canvasId, top, sKey, nKey, yText, fmtSuffix){
  const labels=top.map(r=>r.country_code.toUpperCase());
  const cfg={type:"bar",
    data:{labels,datasets:[
      {label:"Stacked",     data:top.map(r=>r[sKey]??null), backgroundColor:"#d61f26"},
      {label:"Non-stacked", data:top.map(r=>r[nKey]??null), backgroundColor:"#131732"}]},
    options:{responsive:true,maintainAspectRatio:false,
      plugins:{legend:{position:"top"},
        tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.parsed.y==null?"—":c.parsed.y.toFixed(1)+fmtSuffix}`}}},
      scales:{y:{title:{display:true,text:yText}},x:{grid:{display:false}}}}};
  return new Chart(document.getElementById(canvasId), cfg);
}
function renderStack(){
  const {scored}=rankSum();
  const top=scored.filter(r=>r._score!=null).slice(0,10);
  document.getElementById("stackN").textContent=top.length;
  if(cmpOt)cmpOt.destroy(); if(cmpDt)cmpDt.destroy();
  cmpOt=groupedBar("cmpOt", top, "cmp_ot_stacked", "cmp_ot_nonstacked", "% on-time", "%");
  cmpDt=groupedBar("cmpDt", top, "cmp_dt_stacked", "cmp_dt_nonstacked", "minutes", "m");
  // table with deltas (stacked − non-stacked); "bad" = stacked performs worse
  const d=(a,b,higherBetter)=>{
    if(a==null||b==null) return "";
    const diff=a-b, worse = higherBetter ? diff<0 : diff>0;
    return `<span class="sub ${worse?"bad":"good"}">${diff>0?"+":""}${diff.toFixed(1)}</span>`;
  };
  let h="<thead><tr><th>#</th><th>Country</th>"+
        "<th>On-time stk</th><th>On-time non-stk</th><th>Δ</th>"+
        "<th>DT stk</th><th>DT non-stk</th><th>Δ</th></tr></thead><tbody>";
  top.forEach((r,i)=>{
    h+=`<tr><td>${i+1}</td><td>${r.country_code.toUpperCase()}</td>`+
       `<td>${r.cmp_ot_stacked==null?"—":r.cmp_ot_stacked.toFixed(1)+"%"}</td>`+
       `<td>${r.cmp_ot_nonstacked==null?"—":r.cmp_ot_nonstacked.toFixed(1)+"%"}</td>`+
       `<td>${d(r.cmp_ot_stacked,r.cmp_ot_nonstacked,true)}</td>`+
       `<td>${r.cmp_dt_stacked==null?"—":r.cmp_dt_stacked.toFixed(1)+"m"}</td>`+
       `<td>${r.cmp_dt_nonstacked==null?"—":r.cmp_dt_nonstacked.toFixed(1)+"m"}</td>`+
       `<td>${d(r.cmp_dt_stacked,r.cmp_dt_nonstacked,false)}</td></tr>`;
  });
  document.getElementById("cmpTable").innerHTML=h+"</tbody>";
}

// ---- history browser ----
function looksCountry(h){ return /country_code|\bcountry\b/i.test(h.sql||""); }
function renderHistory(filter){
  const host=document.getElementById("histList"); host.innerHTML="";
  const f=(filter||"").toLowerCase();
  const items=HISTORY.filter(h=>!f ||
    (h.title||"").toLowerCase().includes(f) ||
    (h.source||"").toLowerCase().includes(f) ||
    (h.sql||"").toLowerCase().includes(f) ||
    (h.tables||[]).join(" ").toLowerCase().includes(f));
  if(!items.length){ host.innerHTML='<div style="color:var(--muted)">No matching queries.</div>'; return; }
  items.slice(0,200).forEach(h=>{
    const div=document.createElement("div"); div.className="item";
    const compatible = h.runnable!==false && looksCountry(h);
    const cmd = `python3 build_dashboard.py --add-history ${h.id} --value-col <col> --dir lower --weight 1`;
    div.innerHTML=`
      <h4>${h.title||"(untitled query)"}</h4>
      <div class="m">${h.source||""} ${h.timestamp?("· "+h.timestamp):""} ${(h.tables||[]).length?("· "+h.tables.join(", ")):""} ${h.runnable===false?"· <i>non-runnable (SQL not inline)</i>":""}</div>
      <pre>${(h.sql||"(SQL not captured — command stored verbatim)").replace(/</g,"&lt;")}</pre>
      ${compatible?`<div class="cmd">add as signal:\n${cmd}</div>`:""}`;
    host.appendChild(div);
  });
}
document.getElementById("histSearch").addEventListener("input",e=>renderHistory(e.target.value));

function showTab(t){
  document.getElementById("paneRank").style.display  = t==="rank"?"":"none";
  document.getElementById("paneStack").style.display = t==="stack"?"":"none";
  document.getElementById("paneHist").style.display  = t==="hist"?"":"none";
  document.getElementById("tabRank").className  = t==="rank"?"on":"";
  document.getElementById("tabStack").className = t==="stack"?"on":"";
  document.getElementById("tabHist").className  = t==="hist"?"on":"";
  if(t==="hist") renderHistory("");
  if(t==="stack") renderStack();
}

renderSignals();
render();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
