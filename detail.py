import json
recs = {r['country']: r for r in json.load(open('analysis_recs.json'))}
sel = ['om','jo','gv-ma','t3','cl','ph','ar']
def f(x,d=2):
    return 'NA' if x is None else f"{x:+.{d}f}"
def v(x,d=2):
    return 'NA' if x is None else f"{x:.{d}f}"
for c in sel:
    r=recs[c]
    print(f"\n===== {c} ({r['brand']}) vol={r['vol']:,} volWoW={r['vol_wow_pct']:+.1f}% =====")
    print(" PRIMARY:")
    print(f"   PET        {v(r['PET'])}  (Δ {f(r['PET_d'])})")
    print(f"   %on-time   {v(r['pct_on_time'])}  (Δ {f(r['pct_on_time_d'])})")
    print(f"   %stk-ot    {v(r['pct_stacked_on_time'])}  (Δ {f(r['pct_stacked_on_time_d'])})")
    print(f"   %DT>45 QC  {v(r['pct_dt45_qc'])}  (Δ {f(r['pct_dt45_qc_d'])})")
    print(" DIAGNOSTIC:")
    print(f"   TTP(c->PU) {v(r['TTP'])}  (Δ {f(r['TTP_d'])})")
    print(f"   AWT        {v(r['AWT'])}  (Δ {f(r['AWT_d'])})")
    print(f"   AVT        {v(r['AVT'])}  (Δ {f(r['AVT_d'])})")
    print(f"   AAPT(q2)   {v(r['q2_AAPT'])}  (Δ {f(r['q2_AAPT_d'])})")
    print(f"   EPT        {v(r['EPT'])}  (Δ {f(r['EPT_d'])})")
    print(f"   DT         {v(r['DT'])}  (Δ {f(r['DT_d'])})")
    print(f"   PDT(q2)    {v(r['q2_PDT'])}  (Δ {f(r['q2_PDT_d'])})")
    print(f"   %stacked   {v(r['pct_stacked'])}  (Δ {f(r['pct_stacked_d'])})")
    print(f"   rider_late%{v(r['rider_late_pct'])}  (Δ {f(r['rider_late_pct_d'])})")
    print(f"   rider_late_min(q2) {v(r['q2_rider_late_min'])}  (Δ {f(r['q2_rider_late_min_d'])})")
    print(f"   to_cust_t  {v(r['to_cust_time'])}  (Δ {f(r['to_cust_time_d'])})")
    print(f"   STV(q2)    {v(r['q2_created_to_STV'])}  (Δ {f(r['q2_created_to_STV_d'])})")
    print(f"   HBT(q2)    {v(r['q2_HBT'])}  (Δ {f(r['q2_HBT_d'])})")
    print(f"   %w/buffer  {v(r['q2_pct_with_buffer'])}  (Δ {f(r['q2_pct_with_buffer_d'])})")
