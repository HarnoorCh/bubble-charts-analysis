import csv

def load(path, keyfields):
    rows = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            key = tuple(r[k] for k in keyfields)
            rows[key] = r
    return rows

q1 = load('tmp_q1_out.csv', ['country_code','report_week'])
q2 = load('tmp_q2_out.csv', ['country','week'])

# Build per-country WoW. cur=W21, prev=W20
CUR, PREV = '2026W21', '2026W20'
countries = sorted({k[0] for k in q1})

def fnum(v):
    try: return float(v)
    except: return None

def delta(cur, prev):
    if cur is None or prev is None: return None
    return round(cur-prev,2)

recs = []
for c in countries:
    cur1 = q1.get((c,CUR)); prev1 = q1.get((c,PREV))
    if not cur1 or not prev1: continue
    cur2 = q2.get((c,CUR)) or {}; prev2 = q2.get((c,PREV)) or {}
    rec = {'country': c, 'brand': cur1['brands'], 'vol': int(cur1['completed_orders']), 'vol_prev': int(prev1['completed_orders'])}
    rec['vol_wow_pct'] = round(100*(rec['vol']-rec['vol_prev'])/rec['vol_prev'],1) if rec['vol_prev'] else None
    # primary KPIs
    for m in ['PET','pct_on_time','pct_stacked_on_time','pct_dt45_qc']:
        rec[m] = fnum(cur1[m]); rec[m+'_p'] = fnum(prev1[m]); rec[m+'_d'] = delta(rec[m], rec[m+'_p'])
    # diagnostics from q1
    for m in ['TTP','AWT','DT','pct_stacked','rider_late_pct','to_cust_time','EPT','AVT']:
        rec[m] = fnum(cur1[m]); rec[m+'_p'] = fnum(prev1[m]); rec[m+'_d'] = delta(rec[m], rec[m+'_p'])
    # diagnostics from q2
    for m in ['AAPT','PDT','EPB','HBT','rider_late_min','at_customer_time','created_to_STV','pct_with_buffer','EPT']:
        cv=fnum(cur2.get(m)); pv=fnum(prev2.get(m))
        rec['q2_'+m]=cv; rec['q2_'+m+'_p']=pv; rec['q2_'+m+'_d']=delta(cv,pv)
    recs.append(rec)

# rank by volume
recs.sort(key=lambda r: -r['vol'])
print("TOP 20 MARKETS BY VOLUME (W21) with primary KPI WoW deltas")
print(f"{'cc':>5} {'brand':>12} {'vol':>9} {'volΔ%':>6} | {'PET':>5}{'Δ':>6} | {'on-time':>7}{'Δ':>6} | {'stk-ot':>6}{'Δ':>6} | {'DT45qc':>6}{'Δ':>6}")
for r in recs[:20]:
    def f(x,d=1):
        return '' if x is None else f"{x:.{d}f}"
    print(f"{r['country']:>5} {r['brand'] or '':>12} {r['vol']:>9} {f(r['vol_wow_pct']):>6} | {f(r['PET']):>5}{f(r['PET_d']):>6} | {f(r['pct_on_time']):>7}{f(r['pct_on_time_d']):>6} | {f(r['pct_stacked_on_time']):>6}{f(r['pct_stacked_on_time_d']):>6} | {f(r['pct_dt45_qc']):>6}{f(r['pct_dt45_qc_d']):>6}")

# Flagging logic: significant drift in either primary KPI among top-volume markets
# thresholds: PET +/-0.5min, on-time/stacked-on-time +/-1pp, dt45qc +/-1pp
def flagged(r):
    reasons=[]
    if r['PET_d'] is not None and abs(r['PET_d'])>=0.5: reasons.append(f"PET {r['PET_d']:+.2f}m")
    if r['pct_on_time_d'] is not None and abs(r['pct_on_time_d'])>=1.0: reasons.append(f"on-time {r['pct_on_time_d']:+.2f}pp")
    if r['pct_stacked_on_time_d'] is not None and abs(r['pct_stacked_on_time_d'])>=1.0: reasons.append(f"stk-ot {r['pct_stacked_on_time_d']:+.2f}pp")
    if r['pct_dt45_qc_d'] is not None and abs(r['pct_dt45_qc_d'])>=1.0: reasons.append(f"DT45qc {r['pct_dt45_qc_d']:+.2f}pp")
    return reasons

print("\n\nFLAGGED among TOP 25 volume markets:")
top = recs[:25]
for r in top:
    fl=flagged(r)
    if fl:
        ept_drift = r['EPT_d']
        print(f"{r['country']:>5} {r['brand']:>12} vol={r['vol']:>8} volΔ%={r['vol_wow_pct']:>6} EPTΔ={ept_drift:>6} :: {', '.join(fl)}")

# brands represented among flagged
import json
with open('analysis_recs.json','w') as f:
    json.dump(recs,f)
print("\nSaved analysis_recs.json")
