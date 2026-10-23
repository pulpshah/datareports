"""Agreement between the primary and the blind coder on the overlap (PROTOCOL.md section 9).

Usage: python3 -I analysis/agreement.py <primary coded jsonl> <blind coded jsonl> [out.json]

Cohen's kappa for single label fields, mean Jaccard for multi label fields, Spearman rho for each channel,
each with n. Rows are matched by id; only ids in both files count.
"""

import json
import sys
from collections import Counter

SINGLE = ["relevant", "stance", "tier", "icp", "severity", "argument_type", "evidence_level"]
MULTI = ["themes", "layers", "pain_types"]
CHANNELS = ["ethos", "pathos", "logos", "kairos", "style", "clarity", "focus", "awareness"]


def load(p):
    return {r["id"]: r for r in (json.loads(l) for l in open(p) if l.strip())}


def kappa(a, b):
    n = len(a)
    if not n:
        return None
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return round((po - pe) / (1 - pe), 3) if pe < 1 else 1.0


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = (sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb)) ** 0.5
    return round(num / den, 3) if den else None


def main():
    p, b = load(sys.argv[1]), load(sys.argv[2])
    ids = sorted(set(p) & set(b))
    out = {"n": len(ids), "single": {}, "multi": {}, "channels": {}, "pa_est": None}
    for f in SINGLE:
        out["single"][f] = {"kappa": kappa([str(p[i].get(f)) for i in ids], [str(b[i].get(f)) for i in ids]),
                            "raw_agreement": round(sum(str(p[i].get(f)) == str(b[i].get(f)) for i in ids) / len(ids), 3)}
    for f in MULTI:
        js = []
        for i in ids:
            x, y = set(p[i].get(f) or []), set(b[i].get(f) or [])
            js.append(len(x & y) / len(x | y) if x | y else 1.0)
        out["multi"][f] = {"mean_jaccard": round(sum(js) / len(js), 3)}
    rel = [i for i in ids if p[i].get("relevant") and b[i].get("relevant")]
    for c in CHANNELS:
        out["channels"][c] = {"spearman": spearman([p[i]["channels"][c] for i in rel], [b[i]["channels"][c] for i in rel]),
                              "n": len(rel)}
    w = {"ethos": .14, "pathos": .10, "logos": .13, "kairos": .20, "style": .05, "clarity": .12, "focus": .18,
         "awareness": .08}
    pa = lambda r: sum(w[c] * r["channels"][c] for c in w)  # noqa: E731
    out["pa_est"] = {"spearman": spearman([pa(p[i]) for i in rel], [pa(b[i]) for i in rel]), "n": len(rel)}
    out["disagreements"] = {f: [i for i in ids if str(p[i].get(f)) != str(b[i].get(f))] for f in ("relevant", "stance", "tier")}
    txt = json.dumps(out, indent=2)
    print(txt)
    if len(sys.argv) > 3:
        open(sys.argv[3], "w").write(txt)


if __name__ == "__main__":
    main()
