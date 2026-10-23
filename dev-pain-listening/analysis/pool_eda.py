"""Descriptive pass over the candidate pool, before coding (no model involved).

Usage: python3 -I analysis/pool_eda.py [src ...]

For each source: family matched items per window, tool mention shares per window with a chi-square test of
change across windows, and the most engaged items per family. Writes reports/pool_eda.json.
"""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "collect"))
import sample  # noqa: E402  (load_pool applies the frozen family regexes)

TOOLS = {
    "Cursor": r"\bcursor\b", "Claude Code": r"claude code", "Claude": r"\bclaude\b|anthropic|sonnet|opus",
    "Codex": r"\bcodex\b", "Copilot": r"copilot", "Windsurf": r"windsurf", "Gemini": r"gemini",
    "GPT": r"\bgpt|chatgpt|openai", "Lovable": r"lovable", "v0": r"\bv0\b", "Bolt": r"\bbolt(\.new)?\b",
    "Replit": r"replit", "Kiro": r"\bkiro\b", "Next.js": r"next\.?js|\bnext 1[56]", "Vite": r"\bvite\b",
    "Turbopack": r"turbopack", "Webpack": r"webpack", "Rspack": r"rspack", "Rolldown": r"rolldown",
    "Bun": r"\bbun\b", "TypeScript native (tsgo)": r"tsgo|typescript[ -]?7|typescript-go|native typescript",
    "Supabase": r"supabase", "Firebase": r"firebase", "Vercel": r"vercel", "Storybook": r"storybook",
    "Playwright": r"playwright", "Docker": r"docker", "MCP": r"\bmcp\b",
}
TOOL_RE = {k: re.compile(v, re.I) for k, v in TOOLS.items()}
WINDOWS = ["W1", "W2", "W3", "W4"]


def chi2_trend(counts, totals):
    """Chi-square test of equal shares across windows (df = k - 1), with its p value."""
    import math
    k = len(counts)
    p = sum(counts) / sum(totals) if sum(totals) else 0
    if p in (0, 1):
        return None, None
    x2 = sum((c - t * p) ** 2 / (t * p * (1 - p)) for c, t in zip(counts, totals) if t)
    df = k - 1
    # survival function of chi-square via the regularized gamma series
    a, xx = df / 2, x2 / 2
    s, term, n = 0.0, 1.0 / a, 0
    while term > 1e-12 and n < 500:
        s += term
        n += 1
        term *= xx / (a + n)
    pval = 1 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a)) if xx > 0 else 1.0
    return round(x2, 2), round(max(pval, 0.0), 6)


def main():
    srcs = set(sys.argv[1:]) or None
    pool = [r for r in sample.load_pool() if not srcs or r["src"] in srcs]
    sample.engagement_percentiles(pool)
    out = {}
    for src in sorted({r["src"] for r in pool}):
        rows = [r for r in pool if r["src"] == src]
        per_w = Counter(r["window"] for r in rows)
        fam_w = defaultdict(Counter)
        for r in rows:
            for f in r["families"]:
                fam_w[f][r["window"]] += 1
        tool_w = defaultdict(Counter)
        for r in rows:
            txt = (r.get("title") or "") + " " + (r.get("text") or "")
            for t, rx in TOOL_RE.items():
                if rx.search(txt):
                    tool_w[t][r["window"]] += 1
        tools = {}
        for t, c in tool_w.items():
            counts = [c[w] for w in WINDOWS]
            totals = [per_w[w] for w in WINDOWS]
            x2, p = chi2_trend(counts, totals)
            tools[t] = {"n": sum(counts), "share_by_window": [round(c / n, 4) if n else None for c, n in zip(counts, totals)],
                        "chi2": x2, "p": p}
        top = {}
        for f in fam_w:
            cand = sorted((r for r in rows if f in r["families"]), key=lambda r: -(r.get("score") or 0))[:8]
            top[f] = [{"window": r["window"], "score": r.get("score"), "title": (r.get("title") or "")[:140],
                       "text": (r.get("text") or "")[:220], "url": r["url"]} for r in cand]
        out[src] = {"n": len(rows), "by_window": {w: per_w[w] for w in WINDOWS},
                    "families_by_window": {f: {w: c[w] for w in WINDOWS} for f, c in fam_w.items()},
                    "tools": dict(sorted(tools.items(), key=lambda kv: -kv[1]["n"])), "top": top}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports" / "pool_eda.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    for src, o in out.items():
        print(f"\n== {src}: n={o['n']} by window {o['by_window']}")
        for f, c in o["families_by_window"].items():
            print(f"   {f:8s} {c}")
        print("   tools (n, share W1..W4, chi2 p):")
        for t, v in list(o["tools"].items())[:16]:
            print(f"     {t:24s} {v['n']:5d} {v['share_by_window']} p={v['p']}")


if __name__ == "__main__":
    main()
