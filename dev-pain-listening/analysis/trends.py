"""Population volume trends from the full Reddit listings and the listed HN counts (Amendments 1 and 2).

Usage: <analysis venv>/python -I analysis/trends.py

Reddit: for each cluster and community, the weekly share of all posts that match each query family's frozen
regex. These are regex matches over every post, not coded relevance, and are labeled so. Quarter shares get a
chi-square test across windows and a Cochran-Armitage linear trend; weekly spikes are flagged where the share is
more than 3 robust z (median and MAD) above the community's own year. HN: weekly listed counts per keyword,
same spike rule. Writes reports/trends.json, reports/tables/trend_*.csv and reports/fig/trend_*.png.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "analysis"))
from eda import cochran_armitage  # noqa: E402

RAW, REP = ROOT / "data" / "raw", ROOT / "reports"
FAMS = ["BUILD", "AICOST", "AISTAB", "AISPEED", "UIDATA"]
WINDOWS = ["W1", "W2", "W3", "W4"]


def robust_spikes(s, label, thresh=3.0):
    med = s.median()
    mad = (s - med).abs().median() * 1.4826
    if not mad:
        return []
    z = (s - med) / mad
    return [{"series": label, "week": str(k), "value": round(float(v), 4), "robust_z": round(float(z[k]), 2)}
            for k, v in s.items() if z[k] > thresh]


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    (REP / "tables").mkdir(parents=True, exist_ok=True)
    (REP / "fig").mkdir(parents=True, exist_ok=True)
    rows = []
    files = list(RAW.glob("counts_reddit_posts*.jsonl")) + list(RAW.glob("counts_reddit_recount*.jsonl"))
    for f in files:
        for line in open(f):
            r = json.loads(line)
            if r.get("failed") or "n_text" not in r:
                continue  # Amendment 3: only weeks with text availability counts are used
            # Denominator = posts whose text survives in the archive; numerator = family matches among them.
            rows.append({"community": r["community"], "cluster": r["cluster"], "week": r["week_start"],
                         "window": r["window"], "all_posts": r["total"], "total": r["n_text"],
                         "removed": r["n_removed"],
                         **{fam: r["family_counts_text"].get(fam, 0) for fam in FAMS},
                         **{f"{fam}_title": r["family_counts_title"].get(fam, 0) for fam in FAMS}})
    rd = pd.DataFrame(rows).drop_duplicates(["community", "week"])
    rem = rd.groupby(["community", "window"])[["all_posts", "removed", "total"]].sum()
    rem["removed_share"] = (rem["removed"] / rem["all_posts"]).round(3)
    rem.reset_index().to_csv(REP / "tables" / "trend_reddit_removed.csv", index=False)
    removed_share = rem["removed_share"].unstack().to_dict(orient="index")
    out = {"reddit_weeks": int(len(rd)), "reddit_posts_total": int(rd["total"].sum()),
           "coverage": rd.groupby("community")["week"].nunique().to_dict(), "quarter": [], "spikes": [],
           "removed_share": removed_share}
    for level, keys in (("cluster", ["cluster"]), ("community", ["cluster", "community"])):
        q = rd.groupby(keys + ["window"])[["total", "all_posts"] + FAMS + [f"{f}_title" for f in FAMS]].sum().reset_index()
        for key, g in q.groupby(keys):
            g = g.set_index("window").reindex(WINDOWS)
            g = g[[c for c in g.columns if c not in keys]].fillna(0)
            totals = g["total"].astype(int).tolist()
            for fam in FAMS:
                cnt = g[fam].astype(int).tolist()
                if sum(cnt) < 20 or 0 in totals:
                    continue
                chi2, p, _, _ = stats.chi2_contingency(np.array([cnt, [t - c for t, c in zip(totals, cnt)]]))
                z, pz = cochran_armitage(cnt, totals)
                out["quarter"].append({"level": level, "key": key if isinstance(key, str) else "/".join(key),
                                       "family": fam, **{w: c for w, c in zip(WINDOWS, cnt)},
                                       **{f"{w}_total": t for w, t in zip(WINDOWS, totals)},
                                       **{f"{w}_share": round(c / t, 4) for w, c, t in zip(WINDOWS, cnt, totals)},
                                       "rel_change_W1_W4": round((cnt[3] / totals[3]) / (cnt[0] / totals[0]) - 1, 3) if cnt[0] else None,
                                       "chi2_p": p, "trend_z": None if z is None else round(z, 2), "trend_p": pz,
                                       **{f"{w}_title_share": round(g.loc[w, f"{fam}_title"] / g.loc[w, "all_posts"], 4)
                                          if g.loc[w, "all_posts"] else None for w in WINDOWS}})
    pd.DataFrame(out["quarter"]).to_csv(REP / "tables" / "trend_reddit_quarters.csv", index=False)
    wk = rd.groupby(["cluster", "week"])[["total"] + FAMS].sum().reset_index()
    fig, axes = plt.subplots(len(FAMS), 1, figsize=(9, 2.1 * len(FAMS)), sharex=True)
    for ax, fam in zip(axes, FAMS):
        for cl, g in wk.groupby("cluster"):
            g = g.sort_values("week")
            share = (g[fam] / g["total"]).rolling(3, center=True, min_periods=1).mean()
            ax.plot(pd.to_datetime(g["week"]), share, label=cl)
            out["spikes"] += robust_spikes((g.set_index("week")[fam] / g.set_index("week")["total"]), f"reddit:{cl}:{fam}")
        ax.set_ylabel(fam, fontsize=8)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(fontsize=7, frameon=False)
    axes[0].set_title("Reddit: weekly share of all posts matching each family (3 week mean)", fontsize=10)
    fig.tight_layout()
    fig.savefig(REP / "fig" / "trend_reddit_weekly.png", dpi=130)
    plt.close(fig)
    wk.to_csv(REP / "tables" / "trend_reddit_weekly.csv", index=False)

    hn = [json.loads(l) for l in open(RAW / "counts_hn_weekly_listed.jsonl")] if (RAW / "counts_hn_weekly_listed.jsonl").exists() else []
    if hn:
        h = pd.DataFrame(hn).drop_duplicates(["kw", "week_start"])
        h.to_csv(REP / "tables" / "trend_hn_weekly.csv", index=False)
        fig, ax = plt.subplots(figsize=(9, 4))
        for kw, g in h.groupby("kw"):
            g = g.sort_values("week_start")
            ax.plot(pd.to_datetime(g["week_start"]), g["count"], label=kw)
            out["spikes"] += robust_spikes(g.set_index("week_start")["count"].astype(float), f"hn:{kw}")
            h_w = g.assign(window=pd.cut(pd.to_datetime(g["week_start"]),
                                         pd.to_datetime(["2025-10-23", "2026-01-23", "2026-04-23", "2026-07-23", "2026-10-24"]),
                                         labels=WINDOWS, right=False))
            out.setdefault("hn_quarter", {})[kw] = h_w.groupby("window", observed=False)["count"].sum().astype(int).to_dict()
        ax.set_yscale("symlog")
        ax.legend(fontsize=7, frameon=False, ncol=2)
        ax.set_title("Hacker News: weekly listed stories and comments per keyword", fontsize=10)
        fig.tight_layout()
        fig.savefig(REP / "fig" / "trend_hn_weekly.png", dpi=130)
        plt.close(fig)
    (REP / "trends.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps({k: out[k] for k in ("reddit_weeks", "reddit_posts_total")}), len(out["spikes"]), "spikes")


if __name__ == "__main__":
    main()
