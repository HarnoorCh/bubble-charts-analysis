# -*- coding: utf-8 -*-
import json
recs = {r['country']: r for r in json.load(open('analysis_recs.json'))}

FLAG = {'sa':'\U0001F1F8\U0001F1E6','ae':'\U0001F1E6\U0001F1EA','om':'\U0001F1F4\U0001F1F2','jo':'\U0001F1EF\U0001F1F4',
        'cl':'\U0001F1E8\U0001F1F1','ar':'\U0001F1E6\U0001F1F7','ph':'\U0001F1F5\U0001F1ED','t3':'\U0001F1F9\U0001F1ED',
        'gv-ma':'\U0001F1F2\U0001F1E6'}
NAME = {'om':'Oman','jo':'Jordan','cl':'Chile','ar':'Argentina','ph':'Philippines','t3':'Thailand','gv-ma':'Morocco'}
BRAND = {'om':'Talabat','jo':'Talabat','cl':'PedidosYa','ar':'PedidosYa','ph':'foodpanda','t3':'foodpanda','gv-ma':'Glovo'}

MINUS = '−'
UP='⚠️'   # warning
GOOD='\U0001F680'   # rocket

def sd(x, dec=2):
    # signed delta with proper minus glyph
    if x is None: return 'NA'
    s = f"{abs(x):.{dec}f}"
    return ('+'+s) if x>=0 else (MINUS+s)

def cell(delta, good_when_up, thr, dec=2, unit=''):
    """Return WoW cell text with emoji when |delta|>=thr."""
    if delta is None: return 'NA'
    txt = sd(delta, dec)+unit
    if abs(delta) < thr:
        return txt
    improving = (delta>0) if good_when_up else (delta<0)
    return f"{GOOD} {txt}" if improving else f"{UP} {txt}"

def val(x, dec=2):
    return 'NA' if x is None else f"{x:.{dec}f}"

order = ['ar','ph','t3','om','cl','gv-ma','jo']

# ---- Table 1: Primary KPIs ----
print("TABLE 1 PRIMARY\n")
print("| Brand | Market | PET (min) | WoW | %on-time | WoW | %stacked on-time | WoW | DT>45 QC % | WoW |")
print("|---|---|---|---|---|---|---|---|---|---|")
for c in order:
    r=recs[c]
    row = [
        BRAND[c], f"{FLAG[c]} {NAME[c]}",
        val(r['PET']), cell(r['PET_d'], False, 0.30, 2),
        val(r['pct_on_time']), cell(r['pct_on_time_d'], True, 1.0, 2, ' pp'),
        val(r['pct_stacked_on_time']), cell(r['pct_stacked_on_time_d'], True, 1.0, 2, ' pp'),
        val(r['pct_dt45_qc']), cell(r['pct_dt45_qc_d'], False, 1.0, 2, ' pp'),
    ]
    print("| " + " | ".join(row) + " |")

# ---- Table 2: Diagnostics ----
print("\n\nTABLE 2 DIAGNOSTIC\n")
print("| Brand | Market | TTP | WoW | AWT | WoW | DT | WoW | %stacked | WoW | Rider late% | WoW | To cust. | WoW | %w/ buffer | WoW |")
print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
for c in order:
    r=recs[c]
    row = [
        BRAND[c], f"{FLAG[c]} {NAME[c]}",
        val(r['TTP']), cell(r['TTP_d'], False, 0.50, 2),
        val(r['AWT']), cell(r['AWT_d'], False, 0.25, 2),
        val(r['DT']), cell(r['DT_d'], False, 0.50, 2),
        val(r['pct_stacked']), cell(r['pct_stacked_d'], False, 1.5, 2, ' pp'),
        val(r['rider_late_pct']), cell(r['rider_late_pct_d'], False, 0.70, 2, ' pp'),
        val(r['to_cust_time']), cell(r['to_cust_time_d'], False, 0.50, 2),
        val(r['q2_pct_with_buffer']), cell(r['q2_pct_with_buffer_d'], True, 2.0, 2, ' pp'),
    ]
    print("| " + " | ".join(row) + " |")
