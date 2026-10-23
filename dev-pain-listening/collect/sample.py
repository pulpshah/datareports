"""Draw the study sample from the candidate pool (PROTOCOL.md sections 4 to 6, Amendment 1).

Usage: python3 -I collect/sample.py

Reads data/raw/*.jsonl, writes data/sample/sample.jsonl (every drawn candidate, with its stratum, draw half
and batch number) and data/sample/draw_report.json (pool sizes, quotas, shortfalls).

The whole sample (about 500 candidates per window) is drawn once with fixed seeds, then split into 8
proportional batches, so each batch is a representative slice and later batches cannot change earlier ones.
"""

import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "collect"))
import collect  # noqa: E402  (match_families, WINDOWS)

RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "sample"
PER_WINDOW = 500
N_BATCHES = 8
AUTHOR_CAP = 3
MIN_CHARS = 60
_cp = RAW / "comment_pairs_complete.json"
COMPLETE_PAIRS = json.loads(_cp.read_text()) if _cp.exists() else []

# Section 5 quotas as shares of a window's 500.
QUOTAS = {
    ("reddit", "dev", "post"): 50, ("reddit", "dev", "comment"): 33,
    ("reddit", "learner", "post"): 50, ("reddit", "learner", "comment"): 33,
    ("reddit", "ai", "post"): 50, ("reddit", "ai", "comment"): 34,
    ("hn", "hn", "*"): 100,
    ("discourse", "forum.cursor.com", "*"): 50, ("discourse", "community.vercel.com", "*"): 25,
    ("devto", "devto", "*"): 50,
    ("stackoverflow", "so", "*"): 25,
}
assert sum(QUOTAS.values()) == PER_WINDOW


def cluster_for_match(r):
    if r["src"] == "reddit":
        return r["cluster"]
    if r["src"] == "discourse" and r["community"] == "forum.cursor.com":
        return "ai"
    return "general"


def stratum(r):
    if r["src"] == "reddit":
        return ("reddit", r["cluster"], r["kind"])
    if r["src"] == "discourse":
        return ("discourse", r["community"], "*")
    return (r["src"], {"hn": "hn", "devto": "devto", "stackoverflow": "so"}[r["src"]], "*")


def shingles(text, k=5):
    w = re.findall(r"\w+", text.lower())
    return {" ".join(w[i:i + k]) for i in range(max(1, len(w) - k + 1))}


def load_pool():
    pool = {}
    for f in sorted(RAW.glob("*.jsonl")):
        if f.name.startswith("counts_") or f.name == "hn_weekly.jsonl":
            continue
        for line in open(f):
            r = json.loads(line)
            if not r.get("window"):
                continue
            if r["src"] == "reddit" and r["kind"] == "comment" and [r["community"], r.get("kw")] not in COMPLETE_PAIRS:
                continue  # Amendment 4: only comment queries complete in every window enter the sample
            if r["src"] == "devto" and r.get("kw") not in ("vibecoding", "ai"):
                continue  # Amendment 3: only the fully crawled DEV.to tags enter the sample
            body = (r.get("title") or "") + "\n" + (r.get("text") or "")
            if r["src"] == "devto":
                body += "\n" + " ".join(r.get("tags") or [])
            if r.get("text", "").strip() in ("[removed]", "[deleted]"):
                r["text"] = ""
                body = r.get("title") or ""
            if len(body.strip()) < MIN_CHARS:
                continue
            fams = r.get("families") or collect.match_families(body, cluster_for_match(r))
            if not fams:
                continue
            if r["id"] in pool:
                pool[r["id"]]["kws"].add(r.get("kw") or "")
                continue
            r["families"] = fams
            r["kws"] = {r.get("kw") or ""}
            pool[r["id"]] = r
    for r in pool.values():
        r["kws"] = sorted(k for k in r["kws"] if k)
    return list(pool.values())


def engagement_percentiles(rows):
    by = defaultdict(list)
    for r in rows:
        by[(r["src"], r["window"])].append(r)
    for grp in by.values():
        grp.sort(key=lambda r: (r.get("score") or 0))
        n = len(grp)
        for i, r in enumerate(grp):
            r["engagement_pct"] = round((i + 0.5) / n, 4)


def main():
    pool = load_pool()
    engagement_percentiles(pool)
    report = {"pool_total": len(pool), "windows": {}}
    drawn = []
    author_n = Counter()
    for wi, (w, _, _) in enumerate(collect.WINDOWS):
        rng = random.Random(20261023 + wi + 1)
        rows = [r for r in pool if r["window"] == w]
        strata = defaultdict(list)
        for r in rows:
            strata[stratum(r)].append(r)
        # Shortfall moves first to sibling strata of the same source, then to every other stratum by quota.
        quota = dict(QUOTAS)
        for st in QUOTAS:
            short = quota[st] - len(strata.get(st, []))
            if short > 0:
                quota[st] = len(strata.get(st, []))
                # same source and cluster first (a missing comment quota goes to that cluster's posts)
                sibs = ([s for s in QUOTAS if s[:2] == st[:2] and s != st]
                        + [s for s in QUOTAS if s[0] == st[0] and s[:2] != st[:2]]
                        or [s for s in QUOTAS if s != st])
                spare = {s: len(strata.get(s, [])) - quota[s] for s in sibs}
                for s in sibs:
                    give = min(short, max(0, spare[s]))
                    quota[s] += give
                    short -= give
                    if not short:
                        break
        report["windows"][w] = {"pool": {"|".join(k): len(v) for k, v in strata.items()},
                                "quota": {"|".join(k): v for k, v in quota.items()}}
        kept_sh = []
        for st in QUOTAS:
            cand = strata.get(st, [])
            q = quota[st]
            if not q:
                continue
            picked, picked_ids = [], set()

            def try_take(r, half):
                if r["id"] in picked_ids:
                    return False
                if r.get("author_hash") and author_n[(w, r["author_hash"])] >= AUTHOR_CAP:
                    return False
                sh = shingles((r.get("title") or "") + " " + (r.get("text") or ""))
                for other in kept_sh:
                    if sh and len(sh & other) / len(sh | other) >= 0.8:
                        return False
                kept_sh.append(sh)
                picked_ids.add(r["id"])
                if r.get("author_hash"):
                    author_n[(w, r["author_hash"])] += 1
                picked.append(dict(r, stratum="|".join(st), draw_half=half))
                return True

            uniform_q = math.ceil(q / 2)
            order = cand[:]
            rng.shuffle(order)
            for r in order:
                if len(picked) >= uniform_q:
                    break
                try_take(r, "uniform")
            # Engagement weighted half: Efraimidis-Spirakis keys, weight = percentile.
            keyed = sorted(cand, key=lambda r: -(rng.random() ** (1.0 / (r["engagement_pct"] + 0.01))))
            for r in keyed:
                if len(picked) >= q:
                    break
                try_take(r, "engagement")
            for r in order:  # top up if the cap or dedupe left the stratum short
                if len(picked) >= q:
                    break
                try_take(r, "uniform_topup")
            rng.shuffle(picked)
            for i, r in enumerate(picked):
                r["batch"] = i % N_BATCHES + 1
            drawn.extend(picked)
        report["windows"][w]["drawn"] = sum(1 for r in drawn if r["window"] == w)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "sample.jsonl", "w") as f:
        for r in drawn:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    report["drawn_total"] = len(drawn)
    report["by_batch"] = dict(sorted(Counter(r["batch"] for r in drawn).items()))
    (OUT / "draw_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({k: report[k] for k in ("pool_total", "drawn_total", "by_batch")}))


if __name__ == "__main__":
    main()
