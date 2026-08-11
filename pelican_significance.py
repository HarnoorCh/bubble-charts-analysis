#!/usr/bin/env python3
"""
Cluster-aware significance test (Control vs Treatment) for the pelican_shops experiment.

Input : CSV from pelican_stats_ready.sql (one row per split_unit x day x vertical x platform x arm,
        with continuous SUM/COUNT and proportion NUM/DEN columns).
Method: analyze at the unit of randomization (split_unit x day = "cluster").
        For each (platform[, vertical]) and metric, take the per-cluster value
        (continuous = sum/cnt ; proportion = num/den) and run an unweighted
        Welch two-sample t-test (Control vs Treatment). p-value from the
        t-distribution via the regularized incomplete beta function.
        Pooled arm KPI (the headline number) is exact: SUM(num)/SUM(den) or SUM(sum)/SUM(cnt).

Caveat: unweighted cluster means => conservative; ignores covariate (CUPED) variance reduction
        that the original experiment pipeline used.

Usage : python3 pelican_significance.py cluster_results.csv
"""
import csv, sys, math
from collections import defaultdict

# metric -> (numerator_col, denominator_col, is_rate)
CONT = {
    "AWT": ("awt_sum", "awt_cnt"),
    "MAE_adjusted": ("mae_sum", "mae_cnt"),
    "EPT": ("ept_sum", "ept_cnt"),
    "aapt": ("aapt_sum", "aapt_cnt"),
    "dt": ("dt_sum", "dt_cnt"),
    "at_vendor_time": ("avt_sum", "avt_cnt"),
    "at_vendor_time_cleaned": ("avtc_sum", "avtc_cnt"),
    "PET": ("pet_sum", "pet_cnt"),
    "time_diff_rider_pickup": ("tdrp_sum", "tdrp_cnt"),
}
RATE = {
    "on_time": ("ontime_num", "completed_den"),
    "late": ("latesv_num", "completed_den"),
    "late_15": ("late15_num", "completed_den"),
    "late_20": ("late20_num", "completed_den"),
    "cancellations": ("cancelled_num", "allorders_den"),
    "contact_rate": ("contact_num", "allorders_den"),
    "stacking": ("stacking_num", "allorders_den"),
}
ALL_METRICS = list(CONT) + list(RATE)


def betacf(a, b, x):
    MAXIT, EPS, FPMIN = 200, 3e-12, 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < FPMIN: d = FPMIN
    d = 1.0 / d
    h = d
    for m in range(1, MAXIT + 1):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        if abs(d) < FPMIN: d = FPMIN
        c = 1.0 + aa / c
        if abs(c) < FPMIN: c = FPMIN
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < EPS: break
    return h


def betai(a, b, x):
    """Regularized incomplete beta I_x(a,b)."""
    if x <= 0.0: return 0.0
    if x >= 1.0: return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    bt = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * betacf(a, b, x) / a
    return 1.0 - bt * betacf(b, a, 1.0 - x) / b


def t_two_sided_p(t, df):
    if df <= 0 or t != t: return float("nan")
    return betai(df / 2.0, 0.5, df / (df + t * t))


def welch(c, tr):
    """Welch t-test. c, tr = lists of per-cluster values. Returns dict or None."""
    nc, nt = len(c), len(tr)
    if nc < 2 or nt < 2: return None
    mc = sum(c) / nc
    mt = sum(tr) / nt
    vc = sum((x - mc) ** 2 for x in c) / (nc - 1)
    vt = sum((x - mt) ** 2 for x in tr) / (nt - 1)
    se2 = vc / nc + vt / nt
    if se2 <= 0:
        return {"mc": mc, "mt": mt, "t": float("nan"), "df": float("nan"), "p": 1.0, "nc": nc, "nt": nt}
    t = (mt - mc) / math.sqrt(se2)
    df = se2 ** 2 / ((vc / nc) ** 2 / (nc - 1) + (vt / nt) ** 2 / (nt - 1))
    return {"mc": mc, "mt": mt, "t": t, "df": df, "p": t_two_sided_p(t, df), "nc": nc, "nt": nt}


def num(v):
    try:
        if v is None or v == "" or v.lower() == "null": return None
        return float(v)
    except (ValueError, AttributeError):
        return None


def analyze(rows, group_keys, label):
    # group rows by group_keys, then collapse to cluster (split_unit, order date) per arm,
    # summing component columns across anything not in group_keys (e.g. vertical for platform-level).
    groups = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))  # gkey -> (arm, clusterid) -> col -> sum
    comps = set()
    for m, (n, d) in {**CONT, **RATE}.items():
        comps.add(n); comps.add(d)
    for r in rows:
        gkey = tuple(r[k] for k in group_keys)
        arm = r["arm"]
        cid = (r["split_unit"], r["local_created_date"])
        acc = groups[gkey][(arm, cid)]
        for col in comps:
            v = num(r.get(col))
            if v is not None: acc[col] += v
        acc["n_orders"] += num(r.get("n_orders")) or 0

    out = []
    for gkey, clusters in sorted(groups.items()):
        # split clusters by arm
        by_arm = {"Control": [], "Treatment": []}
        pooled = {"Control": defaultdict(float), "Treatment": defaultdict(float)}
        for (arm, cid), acc in clusters.items():
            if arm not in by_arm: continue
            by_arm[arm].append(acc)
            for col, v in acc.items():
                pooled[arm][col] += v
        for metric in ALL_METRICS:
            n_col, d_col = ({**CONT, **RATE})[metric]
            is_rate = metric in RATE

            def cluster_vals(arm):
                vals = []
                for acc in by_arm[arm]:
                    den = acc.get(d_col, 0)
                    if den and den > 0:
                        vals.append(acc.get(n_col, 0) / den)
                return vals

            c_vals = cluster_vals("Control")
            t_vals = cluster_vals("Treatment")
            res = welch(c_vals, t_vals)

            def pooled_kpi(arm):
                den = pooled[arm].get(d_col, 0)
                return (pooled[arm].get(n_col, 0) / den) if den else None

            kc, kt = pooled_kpi("Control"), pooled_kpi("Treatment")
            row = dict(zip(group_keys, gkey))
            row["metric"] = metric
            row["type"] = "rate" if is_rate else "mean"
            row["control"] = kc
            row["treatment"] = kt
            row["abs_diff"] = (kt - kc) if (kc is not None and kt is not None) else None
            row["pct_lift"] = ((kt - kc) / kc * 100) if (kc not in (None, 0) and kt is not None) else None
            row["n_clusters_c"] = len(c_vals)
            row["n_clusters_t"] = len(t_vals)
            row["orders_c"] = int(pooled["Control"].get("n_orders", 0))
            row["orders_t"] = int(pooled["Treatment"].get("n_orders", 0))
            row["t_stat"] = res["t"] if res else None
            row["p_value"] = res["p"] if res else None
            row["significant_5pct"] = (res is not None and res["p"] == res["p"] and res["p"] < 0.05)
            out.append(row)
    return out


def fmt(v, p=3):
    if v is None or (isinstance(v, float) and v != v): return ""
    if isinstance(v, float): return f"{v:.{p}f}"
    return str(v)


def write_csv(path, rows, cols):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: fmt(r.get(c)) if isinstance(r.get(c), float) else r.get(c) for c in cols})
    print(f"wrote {path} ({len(rows)} rows)")


def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else "cluster_results.csv"
    rows = list(csv.DictReader(open(inp)))
    print(f"read {len(rows)} cluster rows from {inp}\n")

    plat = analyze(rows, ["platform"], "platform")
    pv = analyze(rows, ["platform", "vertical_category"], "platform x vertical")

    cols_p = ["platform", "metric", "type", "control", "treatment", "abs_diff", "pct_lift",
              "orders_c", "orders_t", "n_clusters_c", "n_clusters_t", "t_stat", "p_value", "significant_5pct"]
    cols_pv = ["platform", "vertical_category"] + cols_p[1:]
    write_csv("significance_platform.csv", plat, cols_p)
    write_csv("significance_platform_vertical.csv", pv, cols_pv)

    # console summary: platform level
    print("\n=== PLATFORM-LEVEL SIGNIFICANCE (Control vs Treatment) ===")
    hdr = f"{'platform':<14}{'metric':<24}{'ctrl':>9}{'treat':>9}{'lift%':>8}{'p':>9}  sig"
    print(hdr); print("-" * len(hdr))
    for r in plat:
        sig = "***" if r["significant_5pct"] else ""
        print(f"{r['platform']:<14}{r['metric']:<24}{fmt(r['control']):>9}{fmt(r['treatment']):>9}"
              f"{fmt(r['pct_lift'],1):>8}{fmt(r['p_value'],4):>9}  {sig}")


if __name__ == "__main__":
    main()
