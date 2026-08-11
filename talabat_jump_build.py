#!/usr/bin/env python3
"""
Build the Talabat Jump experiment dashboard.

Re-runs jump_station_3arm.sql via the `bq` CLI, embeds the fresh results into a
self-contained HTML file (talabat_jump_dashboard.html), and writes it next to
this script. Run it any time to refresh:

    python3 talabat_jump_build.py

The query emits both a daily time series (for the line charts) and window totals
(day='TOTAL', for the tables). The generated HTML has the data inlined (opens
offline), but pulls Chart.js from a CDN, so the first render needs internet.
"""

import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SQL = HERE / "jump_station_3arm.sql"
OUT = HERE / "talabat_jump_dashboard.html"
START_DATE = "2026-06-11"  # experiment start (mirrors DECLARE in the SQL)


def run_query():
    print(f"Running {SQL.name} via bq ...", file=sys.stderr)
    with open(SQL) as fh:
        proc = subprocess.run(
            ["bq", "query", "--use_legacy_sql=false", "--format=json", "--max_rows=100000"],
            stdin=fh,
            capture_output=True,
            text=True,
        )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(f"bq query failed (exit {proc.returncode})")
    rows = json.loads(proc.stdout)
    # bq may page results as a list-of-lists; flatten to a flat list of dicts.
    flat = []
    for item in rows:
        flat.extend(item) if isinstance(item, list) else flat.append(item)
    rows = flat
    # bq returns all values as strings; coerce numerics.
    num_cols = {
        "num_orders", "customers", "seamless_fail_rate_pct", "ccr_pct",
        "hcsr_pct", "order_per_customer", "jump_rate_pct", "jump_magnitude_avg",
    }
    for r in rows:
        for k in num_cols:
            if r.get(k) is not None:
                r[k] = float(r[k])
    print(f"  -> {len(rows)} rows", file=sys.stderr)
    return rows


def build(rows):
    window_end = (date.today() - timedelta(days=1)).isoformat()
    generated = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = (
        TEMPLATE
        .replace("/*DATA*/", json.dumps(rows))
        .replace("{{WINDOW}}", f"{START_DATE} → {window_end}")
        .replace("{{GENERATED}}", generated)
    )
    OUT.write_text(html)
    print(f"Wrote {OUT}", file=sys.stderr)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Talabat Jump Experiment (538)</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root{
    --bg:#ffffff; --panel:#ffffff; --panel2:#f8fafc; --ink:#131732; --muted:#6b7280;
    --line:#e5e7eb; --control:#131732; --t1:#d61f26; --t2:#f25259;
    --good:#15803d; --bad:#b91c1c;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
  .wrap{max-width:1200px;margin:0 auto;padding:28px 22px 60px;}
  header h1{margin:0 0 4px;font-size:22px;color:var(--control);}
  header .meta{color:var(--muted);font-size:13px;}
  header .meta b{color:var(--ink);}
  .note{margin-top:10px;display:inline-block;background:#fef3c7;border:1px solid #fde68a;
    color:#92400e;border-radius:8px;padding:8px 12px;font-size:12.5px;}
  .note b{color:#92400e;}
  .legend{display:flex;gap:18px;margin:16px 0 26px;flex-wrap:wrap;font-size:13px;}
  .legend .dot{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:6px;vertical-align:-1px;}
  h2{font-size:14px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);
    border-bottom:2px solid var(--line);padding-bottom:8px;margin:34px 0 18px;}
  .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:14px 16px;
    box-shadow:0 1px 2px rgba(19,23,50,.04);}
  .card h3{margin:0 0 10px;font-size:13px;color:var(--ink);font-weight:600;}
  .chartbox{position:relative;height:170px;}
  .countbox{position:relative;height:380px;}
  table{width:100%;border-collapse:collapse;font-size:13px;}
  th,td{padding:8px 10px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap;}
  th:first-child,td:first-child{text-align:left;}
  thead th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.03em;}
  tbody tr:hover{background:var(--panel2);}
  .delta{font-size:11px;display:block;margin-top:1px;}
  .good{color:var(--good);} .bad{color:var(--bad);} .flat{color:var(--muted);}
  .controls{display:flex;align-items:center;gap:14px;margin-bottom:14px;flex-wrap:wrap;}
  .controls label{color:var(--muted);font-size:13px;}
  select{background:var(--panel);color:var(--ink);border:1px solid var(--line);
    border-radius:8px;padding:7px 10px;font-size:13px;}
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;
    box-shadow:0 1px 2px rgba(19,23,50,.04);}
  .foot{color:var(--muted);font-size:12px;margin-top:30px;}
  code{background:var(--panel2);padding:1px 5px;border-radius:4px;}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>Talabat Jump Station v2 &mdash; Experiment 538</h1>
    <div class="meta">3-arm comparison &middot; window <b>{{WINDOW}}</b> &middot; generated <b>{{GENERATED}}</b></div>
    <div class="note">&#9888;&#65039; All values are <b>not</b> tested for statistical significance. Significance will be calculated at the end of the experiment period.</div>
  </header>

  <div class="legend">
    <span><span class="dot" style="background:var(--control)"></span>Control</span>
    <span><span class="dot" style="background:var(--t1)"></span>Treatment1</span>
    <span><span class="dot" style="background:var(--t2)"></span>Treatment2</span>
    <span style="color:var(--muted)">&nbsp;&nbsp;&Delta; shown vs Control &middot; <span class="good">green</span>=better, <span class="bad">red</span>=worse</span>
  </div>

  <h2>Global &mdash; window totals</h2>
  <div class="panel"><table id="globalTable"></table></div>

  <h2>Global &mdash; daily trend by arm</h2>
  <div class="grid" id="globalCharts"></div>

  <h2>Country breakdown</h2>
  <div class="controls">
    <span><label for="kpiSel">KPI:</label> <select id="kpiSel"></select></span>
    <span><label for="ctrySel">Country:</label> <select id="ctrySel"></select></span>
  </div>
  <div class="panel countbox"><canvas id="countryChart"></canvas></div>
  <div class="panel" style="margin-top:16px;">
    <div style="color:var(--muted);font-size:12px;margin-bottom:10px;">Window totals by country (selected KPI)</div>
    <table id="countryTable"></table>
  </div>

  <div class="foot">
    Source: <code>fulfillment-dwh-production.cl.tracking_api_logs</code> (allocation prefix
    <code>logistics-otx:tapi-config-variant:&hellip;:538:&lt;arm&gt;</code>).
    Refresh with <code>python3 talabat_jump_build.py</code>.
  </div>
</div>

<script>
const DATA = /*DATA*/;
const ARMS = ["Control","Treatment1","Treatment2"];
const COLORS = {Control:"#131732", Treatment1:"#d61f26", Treatment2:"#f25259"};
const KPIS = [
  {key:"jump_rate_pct",        label:"Jump rate %",         dir:"lower",  fmt:v=>v.toFixed(2)+"%"},
  {key:"jump_magnitude_avg",   label:"Jump magnitude (avg)",dir:"lower",  fmt:v=>v.toFixed(2)},
  {key:"seamless_fail_rate_pct",label:"Seamless fail %",    dir:"lower",  fmt:v=>v.toFixed(3)+"%"},
  {key:"ccr_pct",              label:"CCR %",               dir:"lower",  fmt:v=>v.toFixed(3)+"%"},
  {key:"hcsr_pct",             label:"HCSR %",              dir:"lower",  fmt:v=>v.toFixed(3)+"%"},
  {key:"order_per_customer",   label:"Orders / customer",   dir:"higher", fmt:v=>v.toFixed(4)},
  {key:"num_orders",           label:"Orders",              dir:"neutral",fmt:v=>v.toLocaleString()},
];

Chart.defaults.color = "#6b7280";
Chart.defaults.font.family = getComputedStyle(document.body).fontFamily;
Chart.defaults.borderColor = "rgba(19,23,50,.07)";

// split daily vs window totals
const totalRows = DATA.filter(d=>d.day==="TOTAL");
const dailyRows = DATA.filter(d=>d.day!=="TOTAL");
const days = [...new Set(dailyRows.map(d=>d.day))].sort();
const dayLbl = d=>d.slice(5); // MM-DD

const gTotal = {};                       // gTotal[arm]
totalRows.filter(d=>d.level==="global").forEach(d=>gTotal[d.model_version]=d);
const gDaily = {};                       // gDaily[arm][day]
dailyRows.filter(d=>d.level==="global").forEach(d=>{(gDaily[d.model_version]=gDaily[d.model_version]||{})[d.day]=d;});

const countries = [...new Set(totalRows.filter(d=>d.level==="country").map(d=>d.entity))].sort();
const cTotal = {};                       // cTotal[entity][arm]
totalRows.filter(d=>d.level==="country").forEach(d=>{(cTotal[d.entity]=cTotal[d.entity]||{})[d.model_version]=d;});
const cDaily = {};                       // cDaily[entity][arm][day]
dailyRows.filter(d=>d.level==="country").forEach(d=>{
  cDaily[d.entity]=cDaily[d.entity]||{}; cDaily[d.entity][d.model_version]=cDaily[d.entity][d.model_version]||{};
  cDaily[d.entity][d.model_version][d.day]=d;
});

function deltaCell(val, ctrl, dir){
  if(ctrl==null||val==null) return "";
  const d = val-ctrl;
  let cls="flat", arrow="";
  if(dir!=="neutral" && Math.abs(d)>1e-9){
    const good = dir==="lower" ? d<0 : d>0;
    cls = good?"good":"bad"; arrow = d>0?"▲":"▼";
  }
  const shown = Math.abs(d)>=1 ? (d>0?"+":"")+d.toFixed(2) : (d>0?"+":"")+d.toFixed(3);
  return `<span class="delta ${cls}">${arrow} ${shown}</span>`;
}
function dot(a){return `<span style="display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:7px;background:${COLORS[a]}"></span>`;}

function lineChart(canvas, seriesByArm, kpi){
  return new Chart(canvas,{
    type:"line",
    data:{labels:days.map(dayLbl), datasets:ARMS.map(a=>({
      label:a, borderColor:COLORS[a], backgroundColor:COLORS[a],
      data:days.map(d=>seriesByArm[a]&&seriesByArm[a][d]?seriesByArm[a][d][kpi.key]:null),
      tension:.25, borderWidth:2, pointRadius:3, pointHoverRadius:5, spanGaps:true, fill:false,
    }))},
    options:{
      plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.dataset.label}: ${c.parsed.y==null?"—":kpi.fmt(c.parsed.y)}`}}},
      scales:{y:{beginAtZero:false,ticks:{maxTicksLimit:5}},x:{grid:{display:false}}},
      interaction:{mode:"index",intersect:false},
      responsive:true,maintainAspectRatio:false,
    }
  });
}

// --- Global table (TOP) ---
(function(){
  let h="<thead><tr><th>Arm</th>";
  KPIS.forEach(k=>h+=`<th>${k.label}</th>`); h+="</tr></thead><tbody>";
  ARMS.forEach(a=>{
    h+=`<tr><td>${dot(a)}${a}</td>`;
    KPIS.forEach(k=>{
      const v=gTotal[a]?gTotal[a][k.key]:null;
      const ctrl=gTotal["Control"]?gTotal["Control"][k.key]:null;
      h+=`<td>${v==null?"&mdash;":k.fmt(v)}${a!=="Control"?deltaCell(v,ctrl,k.dir):""}</td>`;
    });
    h+="</tr>";
  });
  document.getElementById("globalTable").innerHTML=h+"</tbody>";
})();

// --- Global daily line charts ---
const gc = document.getElementById("globalCharts");
KPIS.forEach(kpi=>{
  const card=document.createElement("div"); card.className="card";
  card.innerHTML=`<h3>${kpi.label}</h3><div class="chartbox"><canvas></canvas></div>`;
  gc.appendChild(card);
  lineChart(card.querySelector("canvas"), gDaily, kpi);
});

// --- Country section ---
const kpiSel=document.getElementById("kpiSel");
KPIS.forEach((k,i)=>{const o=document.createElement("option");o.value=i;o.textContent=k.label;kpiSel.appendChild(o);});
const ctrySel=document.getElementById("ctrySel");
countries.forEach(c=>{const o=document.createElement("option");o.value=c;o.textContent=c.toUpperCase();ctrySel.appendChild(o);});

let countryChart;
function renderCountry(){
  const kpi=KPIS[+kpiSel.value], ctry=ctrySel.value;
  if(countryChart)countryChart.destroy();
  countryChart=lineChart(document.getElementById("countryChart"), cDaily[ctry]||{}, kpi);
  countryChart.options.plugins.legend.display=true;
  countryChart.options.plugins.legend.position="top";
  countryChart.options.scales.y.title={display:true,text:`${kpi.label} — ${ctry.toUpperCase()}`};
  countryChart.update();
  // table: window totals, all countries, arms as columns
  let h="<thead><tr><th>Country</th>";
  ARMS.forEach(a=>h+=`<th>${a}</th>`); h+="</tr></thead><tbody>";
  countries.forEach(c=>{
    h+=`<tr><td>${c.toUpperCase()}</td>`;
    const ctrl=cTotal[c]&&cTotal[c]["Control"]?cTotal[c]["Control"][kpi.key]:null;
    ARMS.forEach(a=>{
      const v=cTotal[c]&&cTotal[c][a]?cTotal[c][a][kpi.key]:null;
      h+=`<td>${v==null?"&mdash;":kpi.fmt(v)}${a!=="Control"?deltaCell(v,ctrl,kpi.dir):""}</td>`;
    });
    h+="</tr>";
  });
  document.getElementById("countryTable").innerHTML=h+"</tbody>";
}
kpiSel.addEventListener("change",renderCountry);
ctrySel.addEventListener("change",renderCountry);
renderCountry();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    build(run_query())
