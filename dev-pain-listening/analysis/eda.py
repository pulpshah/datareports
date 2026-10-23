"""Exploratory data analysis of the coded sample, top down (PROTOCOL.md sections 2, 8 and 9).

Usage: <analysis venv>/python -I analysis/eda.py

Reads data/sample/batch*.jsonl, data/coded/coded_batch*.jsonl, data/coded/rm_batch*.jsonl and, when present,
data/coded/claims_canonical.json. Writes reports/eda_numbers.json (every number the report cites),
reports/tables/*.csv and reports/fig/*.png. The written report (reports/EDA.md) is authored from these files.
"""

import json
import math
import re
from collections import Counter
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parent.parent
REP = ROOT / "reports"
TAB, FIG = REP / "tables", REP / "fig"
W = {"ethos": .14, "pathos": .10, "logos": .13, "kairos": .20, "style": .05, "clarity": .12, "focus": .18,
     "awareness": .08}
WINDOWS = ["W1", "W2", "W3", "W4"]
TESTS = []  # every inferential test, BH adjusted at the end


def wilson(k, n):
    if not n:
        return (None, None)
    lo, hi = proportion_confint(k, n, method="wilson")
    return round(lo, 4), round(hi, 4)


def test(name, stat, p, n, effect=None, note=""):
    TESTS.append({"test": name, "stat": None if stat is None else round(float(stat), 4),
                  "p": None if p is None else float(p), "n": int(n), "effect": effect, "note": note})


def load():
    items, coded, rm = [], [], []
    for f in sorted((ROOT / "data" / "sample").glob("batch*.jsonl")):
        items += [json.loads(l) for l in open(f)]
    for f in sorted((ROOT / "data" / "coded").glob("coded_batch*.jsonl")):
        coded += [json.loads(l) for l in open(f) if l.strip()]
    for f in sorted((ROOT / "data" / "coded").glob("rm_batch*.jsonl")):
        rm += [json.loads(l) for l in open(f)]
    it = pd.DataFrame(items).drop_duplicates("id").set_index("id")
    cd = pd.DataFrame(coded).drop_duplicates("id", keep="last").set_index("id")
    r = pd.DataFrame(rm).drop_duplicates("id", keep="last").set_index("id")[["rm_raw"]]
    df = it.join(cd, how="inner", rsuffix="_coded").join(r, how="left")
    for c in W:
        df["ch_" + c] = df["channels"].apply(lambda d: float((d or {}).get(c, 0.0)))
    df["pa"] = sum(W[c] * df["ch_" + c] for c in W)
    df["speed"] = np.sqrt(sum(W[c] * df["ch_" + c] ** 2 for c in W))
    df["text_chars"] = df["own_text"].str.len()
    return df


def multi_freq(df, col, n):
    c = Counter(x for xs in df[col] for x in (xs or []))
    rows = []
    for k, v in c.most_common():
        lo, hi = wilson(v, n)
        rows.append({"value": k, "n": v, "share": round(v / n, 4), "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(rows)


def single_freq(s):
    n = len(s)
    rows = []
    for k, v in s.value_counts().items():
        lo, hi = wilson(v, n)
        rows.append({"value": k, "n": int(v), "share": round(v / n, 4), "ci_lo": lo, "ci_hi": hi})
    return pd.DataFrame(rows)


def cramers_v(table):
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.values.sum()
    k = min(table.shape) - 1
    return chi2, p, dof, (math.sqrt(chi2 / (n * k)) if n and k else None)


def cochran_armitage(counts, totals):
    """Linear trend in proportions across ordered windows (scores 1..k). Returns z, two sided p."""
    x = np.arange(1, len(counts) + 1)
    counts, totals = np.array(counts, float), np.array(totals, float)
    N, R = totals.sum(), counts.sum()
    if N == 0 or R in (0, N):
        return None, None
    p = R / N
    t = (x * (counts - totals * p)).sum()
    var = p * (1 - p) * ((totals * x ** 2).sum() - (totals * x).sum() ** 2 / N)
    if var <= 0:
        return None, None
    z = t / math.sqrt(var)
    return z, 2 * stats.norm.sf(abs(z))


def boot_median_ci(v, b=2000, seed=7):
    v = np.asarray([x for x in v if x is not None and not np.isnan(x)])
    if len(v) < 5:
        return (None, None)
    rng = np.random.default_rng(seed)
    meds = np.median(rng.choice(v, (b, len(v))), axis=1)
    return round(float(np.percentile(meds, 2.5)), 3), round(float(np.percentile(meds, 97.5)), 3)


def describe(v):
    v = pd.Series(v).dropna()
    if not len(v):
        return {}
    lo, hi = boot_median_ci(v.values)
    return {"n": int(len(v)), "mean": round(v.mean(), 3), "sd": round(v.std(), 3), "min": round(v.min(), 3),
            "p10": round(v.quantile(.1), 3), "q1": round(v.quantile(.25), 3), "median": round(v.median(), 3),
            "q3": round(v.quantile(.75), 3), "p90": round(v.quantile(.9), 3), "max": round(v.max(), 3),
            "median_ci": [lo, hi], "skew": round(float(stats.skew(v)), 3) if len(v) > 2 else None}


UNIT = [(r"\b(ms|millisecond)", "s", 0.001), (r"\b(s|sec|secs|second)", "s", 1), (r"\b(min|mins|minute|m)\b", "s", 60),
        (r"\b(h|hr|hrs|hour)", "s", 3600), (r"\b(day)", "s", 86400)]


def norm_quantity(q):
    """Map a coded quantity to (kind, value): build or wait seconds, dollars per month, or None."""
    try:
        v = float(q.get("value"))
    except (TypeError, ValueError):
        return None
    u = (q.get("unit") or "").lower()
    about = (q.get("about") or "").lower()
    if "$" in u or "usd" in u or "dollar" in u:
        per = 1.0
        if "year" in u or "annual" in u:
            per = 1 / 12
        elif "day" in u:
            per = 30
        elif "month" not in u and "/mo" not in u:
            return ("usd_once_or_unknown", v)
        return ("usd_per_month", v * per)
    for rx, kind, mult in UNIT:
        if re.search(rx, u):
            if any(k in about for k in ("build", "compile", "ci", "deploy", "typecheck", "test", "reload", "hmr",
                                         "dev server", "start", "cold")):
                return ("build_seconds", v * mult)
            return ("other_seconds", v * mult)
    if "token" in u:
        return ("tokens", v)
    if "%" in u or "percent" in u:
        return ("percent", v)
    return None


def save(df, name):
    TAB.mkdir(parents=True, exist_ok=True)
    df.to_csv(TAB / f"{name}.csv", index=False)
    return df


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    df = load()
    out = {"n_candidates": int(len(df))}
    rel = df[df["relevant"] == True].copy()  # noqa: E712
    out["n_relevant"] = int(len(rel))
    out["relevance_rate"] = [round(len(rel) / len(df), 4), *wilson(len(rel), len(df))]

    # k: median rm_raw of batch 1's relevant items (PROTOCOL.md section 8), frozen.
    b1 = rel[rel["batch"] == 1]["rm_raw"].dropna()
    k = float(b1.median()) if len(b1) else float(rel["rm_raw"].median())
    out["k_median_rm_batch1"] = round(k, 3)
    rel["pf"] = rel["pa"] * rel["rm_raw"]
    rel["pm"] = rel["speed"] * rel["rm_raw"]
    rel["pf_fair"] = rel["pf"] / (rel["rm_raw"] + k)
    rel["pm_fair"] = rel["pm"] / (rel["rm_raw"] + k)
    rel["rm_norm"] = rel["rm_raw"] / (rel["rm_raw"] + k)

    # 1. Sample
    out["by_window"] = df.groupby("window").size().to_dict()
    out["relevant_by_window"] = rel.groupby("window").size().to_dict()
    rr = df.groupby("src")["relevant"].agg(["sum", "count"]).reset_index()
    rr["rate"] = rr["sum"] / rr["count"]
    rr["ci"] = [wilson(int(a), int(b)) for a, b in zip(rr["sum"], rr["count"])]
    save(rr, "relevance_by_source")
    out["relevant_by_source"] = rel.groupby("src").size().to_dict()
    out["relevant_by_cluster"] = rel.groupby("cluster").size().to_dict()
    tab = pd.crosstab(df["src"], df["relevant"])
    chi2, p, dof, v = cramers_v(tab)
    test("relevance rate differs by source", chi2, p, len(df), {"cramers_v": round(v, 3)})

    n = len(rel)
    # 2. Who
    out["stance"] = save(single_freq(rel["stance"]), "stance").to_dict("records")
    out["tier"] = save(single_freq(rel["tier"]), "tier").to_dict("records")
    out["tier_confidence"] = rel.groupby(["tier", "tier_confidence"]).size().unstack(fill_value=0).to_dict()
    out["icp"] = save(single_freq(rel["icp"]), "icp").to_dict("records")
    out["severity"] = save(single_freq(rel["severity"]), "severity").to_dict("records")
    out["tier_by_cluster"] = pd.crosstab(rel["cluster"], rel["tier"]).to_dict()

    # 3. What
    for col in ("themes", "layers", "pain_types"):
        out[col] = save(multi_freq(rel, col, n), col).to_dict("records")
    # theme x layer co-occurrence
    tl = Counter((t, l) for ts, ls in zip(rel["themes"], rel["layers"]) for t in ts for l in ls)
    save(pd.DataFrame([{"theme": t, "layer": l, "n": c} for (t, l), c in tl.items()]), "theme_x_layer")
    tt = Counter(tuple(sorted(p)) for ts in rel["themes"] for p in combinations(set(ts), 2))
    out["theme_pairs"] = [{"pair": list(p), "n": c} for p, c in tt.most_common(12)]

    # Themes and pains by tier (known tiers only), with chi-square per theme
    known = rel[rel["tier"] != "unknown"]
    out["n_known_tier"] = int(len(known))
    rows = []
    for col in ("themes", "pain_types"):
        vals = sorted({x for xs in known[col] for x in xs})
        for val in vals:
            has = known[col].apply(lambda xs: val in xs)
            ct = pd.crosstab(known["tier"], has)
            if ct.shape[1] == 2 and ct.shape[0] > 1:
                chi2, p, dof, v = cramers_v(ct)
                test(f"{col}:{val} share differs by tier", chi2, p, len(known), {"cramers_v": round(v, 3)})
            for tier, g in known.groupby("tier"):
                kk = int(g[col].apply(lambda xs: val in xs).sum())
                rows.append({"field": col, "value": val, "tier": tier, "n": kk, "of": len(g),
                             "share": round(kk / len(g), 4), "ci": wilson(kk, len(g))})
    save(pd.DataFrame(rows), "by_tier")

    # ICP vs expert contrast, per theme and pain (Fisher exact)
    icp = rel[rel["icp"].isin(["high_end_vibe_coder", "entrant_fe"])]
    exp = rel[rel["tier"] == "expert"]
    out["n_icp"], out["n_expert"] = int(len(icp)), int(len(exp))
    rows = []
    for col in ("themes", "pain_types", "layers"):
        for val in sorted({x for xs in rel[col] for x in xs}):
            a = int(icp[col].apply(lambda xs: val in xs).sum())
            b = int(exp[col].apply(lambda xs: val in xs).sum())
            if len(icp) and len(exp) and (a + b) >= 5:
                odds, p = stats.fisher_exact([[a, len(icp) - a], [b, len(exp) - b]])
                test(f"ICP vs expert: {col}:{val}", odds if np.isfinite(odds) else None, p, len(icp) + len(exp),
                     {"icp_share": round(a / len(icp), 3), "expert_share": round(b / len(exp), 3)})
                rows.append({"field": col, "value": val, "icp_n": a, "icp_share": round(a / len(icp), 3),
                             "expert_n": b, "expert_share": round(b / len(exp), 3), "odds_ratio": odds, "p": p})
    save(pd.DataFrame(rows), "icp_vs_expert")

    # 4. Arguments and evidence
    out["argument_type"] = save(single_freq(rel["argument_type"]), "argument_type").to_dict("records")
    out["evidence_level"] = save(single_freq(rel["evidence_level"]), "evidence_level").to_dict("records")
    ct = pd.crosstab(rel["tier"], rel["evidence_level"])
    if ct.shape[0] > 1 and ct.shape[1] > 1:
        chi2, p, dof, v = cramers_v(ct)
        test("evidence level differs by tier", chi2, p, len(rel), {"cramers_v": round(v, 3)})
    save(ct.reset_index(), "tier_x_evidence")
    out["promo_share"] = [int(rel["suspected_promo"].astype(bool).sum()), *wilson(int(rel["suspected_promo"].astype(bool).sum()), n)]
    out["ai_written"] = rel["suspected_ai_written"].astype(str).value_counts().to_dict()

    # 5. Persuasion
    for m in ("rm_raw", "pa", "speed", "pf", "pm", "pf_fair", "pm_fair"):
        out[f"dist_{m}"] = describe(rel[m])
    out["channels_mean"] = {c: round(rel["ch_" + c].mean(), 3) for c in W}
    out["channels_by_tier"] = rel.groupby("tier")[["ch_" + c for c in W]].mean().round(3).to_dict()
    out["channels_by_stance"] = rel.groupby("stance")[["ch_" + c for c in W]].mean().round(3).to_dict()
    r_len, p_len = stats.spearmanr(rel["rm_raw"], rel["text_chars"], nan_policy="omit")
    out["rm_vs_length_spearman"] = round(float(r_len), 3)
    test("rm_raw tracks text length (Spearman)", r_len, p_len, n, note="ADR 0003 risk: mass as a length proxy")
    for m in ("pf_fair", "pm_fair", "pa", "speed"):
        rho, p = stats.spearmanr(rel[m], rel["engagement_pct"], nan_policy="omit")
        test(f"{m} vs uptake (engagement percentile)", rho, p, n)
        out[f"{m}_vs_uptake_rho"] = round(float(rho), 3)
        per_src = {}
        for s, g in rel.groupby("src"):
            if len(g) >= 20:
                rr_, pp = stats.spearmanr(g[m], g["engagement_pct"], nan_policy="omit")
                per_src[s] = {"rho": round(float(rr_), 3), "p": round(float(pp), 4), "n": len(g)}
        out[f"{m}_vs_uptake_by_source"] = per_src
    for m in ("pf_fair", "pm_fair"):
        groups = {a: g[m].dropna().values for a, g in rel.groupby("argument_type") if len(g) >= 8}
        if len(groups) > 1:
            h, p = stats.kruskal(*groups.values())
            test(f"{m} differs by argument type (Kruskal-Wallis)", h, p, sum(len(v) for v in groups.values()))
        out[f"{m}_by_argument"] = {a: describe(v) for a, v in groups.items()}
        groups = {a: g[m].dropna().values for a, g in rel.groupby("evidence_level") if len(g) >= 8}
        if len(groups) > 1:
            h, p = stats.kruskal(*groups.values())
            test(f"{m} differs by evidence level (Kruskal-Wallis)", h, p, sum(len(v) for v in groups.values()))
        out[f"{m}_by_evidence"] = {a: describe(v) for a, v in groups.items()}
        groups = {a: g[m].dropna().values for a, g in known.assign(**{m: rel[m]}).groupby("tier") if len(g) >= 8}
        if len(groups) > 1:
            h, p = stats.kruskal(*groups.values())
            test(f"{m} differs by tier (Kruskal-Wallis)", h, p, sum(len(v) for v in groups.values()))
        out[f"{m}_by_tier"] = {a: describe(v) for a, v in groups.items()}
    top_cols = ["src", "community", "window", "tier", "stance", "claim", "quote", "url", "rm_raw", "pa", "speed",
                "pf", "pm", "pf_fair", "pm_fair", "engagement_pct"]
    save(rel.sort_values("pf_fair", ascending=False)[top_cols].head(25).reset_index(), "top_pf_fair")
    save(rel.sort_values("pm_fair", ascending=False)[top_cols].head(25).reset_index(), "top_pm_fair")
    save(rel.sort_values("pf_fair")[top_cols].head(15).reset_index(), "bottom_pf_fair")

    # 6. Tools
    tools = Counter(t.strip() for ts in rel["tools"] for t in set(ts or []))
    norm = Counter()
    alias = {}
    for t, c in tools.items():
        key = t.lower().replace(".js", "js").replace(" ", "")
        alias.setdefault(key, t)
        norm[alias[key]] += c
    rows = []
    for t, c in norm.most_common(40):
        key = t.lower().replace(".js", "js").replace(" ", "")
        mask = rel["tools"].apply(lambda ts: any(x.lower().replace(".js", "js").replace(" ", "") == key for x in (ts or [])))
        g = rel[mask]
        comp = int((g["stance"] == "complaint").sum())
        praise = int((g["stance"] == "praise_or_fix").sum())
        rows.append({"tool": t, "n": c, "share": round(c / n, 4), "complaint": comp, "praise_or_fix": praise,
                     "net_complaint": round((comp - praise) / len(g), 3) if len(g) else None,
                     "median_pm_fair": round(g["pm_fair"].median(), 3), "top_theme": Counter(x for xs in g["themes"] for x in xs).most_common(1)[0][0]})
    out["tools"] = save(pd.DataFrame(rows), "tools").to_dict("records")

    # 7. Quantities
    q = [(i, *nq) for i, qs in zip(rel.index, rel["quantities"]) for qq in (qs or []) if isinstance(qq, dict)
         for nq in [norm_quantity(qq)] if nq]
    qdf = pd.DataFrame(q, columns=["id", "kind", "value"])
    save(qdf.merge(rel[["claim", "tier", "url"]], left_on="id", right_index=True), "quantities")
    out["quantities"] = {kd: describe(g["value"]) for kd, g in qdf.groupby("kind")} if len(qdf) else {}

    # 8. Time: theme and pain shares by window, chi-square and linear trend
    rows = []
    totals = [int((rel["window"] == w).sum()) for w in WINDOWS]
    for col in ("themes", "pain_types", "layers"):
        for val in sorted({x for xs in rel[col] for x in xs}):
            cnt = [int(rel[rel["window"] == w][col].apply(lambda xs: val in xs).sum()) for w in WINDOWS]
            if sum(cnt) < 10:
                continue
            ct = np.array([cnt, [t - c for t, c in zip(totals, cnt)]])
            chi2, p, dof, _ = stats.chi2_contingency(ct)
            z, pz = cochran_armitage(cnt, totals)
            test(f"time: {col}:{val} share changes across windows (chi-square)", chi2, p, sum(totals))
            if z is not None:
                test(f"time: {col}:{val} linear trend (Cochran-Armitage)", z, pz, sum(totals))
            rows.append({"field": col, "value": val, **{w: c for w, c in zip(WINDOWS, cnt)},
                         **{f"{w}_share": round(c / t, 4) if t else None for w, c, t in zip(WINDOWS, cnt, totals)},
                         "chi2_p": p, "trend_z": None if z is None else round(z, 3), "trend_p": pz})
    out["by_window_totals"] = dict(zip(WINDOWS, totals))
    save(pd.DataFrame(rows), "by_window")
    for m in ("pm_fair", "pf_fair"):
        groups = [rel[rel["window"] == w][m].dropna().values for w in WINDOWS]
        if all(len(g) > 5 for g in groups):
            h, p = stats.kruskal(*groups)
            test(f"time: {m} differs across windows", h, p, sum(len(g) for g in groups))
        out[f"{m}_by_window"] = {w: describe(g) for w, g in zip(WINDOWS, groups)}
    ev = Counter(e.strip() for es in rel["events"] for e in (es or []))
    out["events_named"] = ev.most_common(40)
    out["events_by_window"] = {w: Counter(e for es in rel[rel["window"] == w]["events"] for e in (es or [])).most_common(10) for w in WINDOWS}

    # 9. Canonical claims, when the claim map exists
    cp = ROOT / "data" / "coded" / "claims_canonical.json"
    if cp.exists():
        cmap = json.loads(cp.read_text())
        rows = []
        for c in cmap["claims"]:
            ids = [i for i in c["ids"] if i in rel.index]
            g = rel.loc[ids]
            if not len(g):
                continue
            tiers = g["tier"].value_counts()
            rows.append({"claim_id": c["id"], "claim": c["claim"], "n": len(g), "share": round(len(g) / n, 4),
                         "ci": wilson(len(g), n), "themes": "; ".join(f"{a}:{b}" for a, b in Counter(x for xs in g["themes"] for x in xs).most_common(3)),
                         "tiers": "; ".join(f"{a}:{b}" for a, b in tiers.items()),
                         "icp_n": int(g["icp"].isin(["high_end_vibe_coder", "entrant_fe"]).sum()),
                         "expert_n": int((g["tier"] == "expert").sum()),
                         "complaint_share": round((g["stance"] == "complaint").mean(), 3),
                         "median_pf_fair": round(g["pf_fair"].median(), 3), "median_pm_fair": round(g["pm_fair"].median(), 3),
                         "median_uptake": round(g["engagement_pct"].median(), 3),
                         "evidence_numbers_or_source": round(g["evidence_level"].isin(["numbers_given", "external_source"]).mean(), 3),
                         **{w: int((g["window"] == w).sum()) for w in WINDOWS},
                         "example_quote": g.sort_values("pm_fair", ascending=False)["quote"].iloc[0],
                         "example_url": g.sort_values("pm_fair", ascending=False)["url"].iloc[0]})
        out["claims"] = save(pd.DataFrame(rows).sort_values("n", ascending=False), "claims").to_dict("records")

    # Figures
    def bar(series, title, fname, ci=None):
        fig, ax = plt.subplots(figsize=(7, max(2.5, 0.32 * len(series))))
        ax.barh(series.index[::-1], series.values[::-1], color="#5B6CFF")
        if ci is not None:
            lo, hi = ci
            ax.errorbar(series.values[::-1], series.index[::-1], xerr=[series.values[::-1] - lo[::-1], hi[::-1] - series.values[::-1]],
                        fmt="none", ecolor="#333", capsize=2, lw=0.8)
        ax.set_title(title, fontsize=10)
        ax.spines[["top", "right"]].set_visible(False)
        fig.tight_layout()
        fig.savefig(FIG / fname, dpi=130)
        plt.close(fig)

    for col in ("themes", "pain_types", "layers"):
        t = pd.DataFrame(out[col]).set_index("value")
        bar(t["share"], f"{col} (share of {n} relevant items, 95% Wilson CI)", f"{col}.png",
            (t["ci_lo"].values, t["ci_hi"].values))
    t = pd.DataFrame(out["tools"]).set_index("tool").head(20)
    bar(t["share"], "Tools named (share of relevant items)", "tools.png")
    bw = pd.read_csv(TAB / "by_window.csv")
    th = bw[bw["field"] == "themes"]
    fig, ax = plt.subplots(figsize=(7, 4))
    for _, r in th.iterrows():
        ax.plot(WINDOWS, [r[f"{w}_share"] for w in WINDOWS], marker="o", label=r["value"])
    ax.set_title("Theme share by window (relevant items)", fontsize=10)
    ax.legend(fontsize=7, frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "themes_by_window.png", dpi=130)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.scatter(rel["pf_fair"], rel["pm_fair"], s=8, alpha=.5, c=rel["engagement_pct"], cmap="viridis")
    ax.set_xlabel("PF fair (signed)")
    ax.set_ylabel("PM fair (directionless)")
    ax.set_title("Persuasive Force vs Momentum (color = uptake percentile)", fontsize=10)
    fig.tight_layout()
    fig.savefig(FIG / "pf_vs_pm.png", dpi=130)
    plt.close(fig)

    # BH adjustment across every test
    ps = [t["p"] for t in TESTS]
    ok = [i for i, p in enumerate(ps) if p is not None and not np.isnan(p)]
    if ok:
        q = multipletests([ps[i] for i in ok], method="fdr_bh")[1]
        for i, qq in zip(ok, q):
            TESTS[i]["q_bh"] = float(qq)
    tests = pd.DataFrame(TESTS).sort_values("p")
    save(tests, "tests")
    out["n_tests"] = len(TESTS)
    out["tests_q_lt_05"] = tests[tests.get("q_bh", pd.Series(dtype=float)) < 0.05].to_dict("records")
    (REP / "eda_numbers.json").write_text(json.dumps(out, indent=1, default=str, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ("n_candidates", "n_relevant", "relevance_rate", "k_median_rm_batch1",
                                          "n_known_tier", "n_icp", "n_expert", "n_tests")}, default=str))


if __name__ == "__main__":
    main()
