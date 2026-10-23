"""Check coded rows against the codebook and the source text (PROTOCOL.md sections 7 and 9).

Usage: python3 -I analysis/validate.py <batch file> <coded file> [<coded file> ...]

Reports, per coded file: missing or extra ids, bad enum values, channel values out of range, and quotes that
are not an exact substring of own_text (whitespace runs are compared collapsed; that is the only allowance).
Exit code 1 if any row fails.
"""

import json
import re
import sys

ENUMS = {
    "stance": {"complaint", "mixed", "praise_or_fix", "neutral_question", "irrelevant"},
    "tier": {"expert", "intermediate", "entrant", "vibe_coder", "unknown"},
    "tier_confidence": {"low", "medium", "high"},
    "icp": {"high_end_vibe_coder", "entrant_fe", "neither", "unknown"},
    "severity": {"annoyed", "blocked", "switched_or_quit", "none"},
    "argument_type": {"anecdote", "measurement", "benchmark_or_link", "authority", "generalization", "analogy",
                      "prediction", "venting", "question"},
    "evidence_level": {"none", "personal_experience", "numbers_given", "external_source"},
    "suspected_ai_written": {"true", "false", "unsure"},
}
MULTI = {
    "themes": {"build_time", "ai_cost", "ai_speed", "ai_stability", "ui_data_gap", "tool_fragmentation", "other"},
    "layers": {"fe", "data", "interactivity", "be", "ci_infra", "cross"},
    "pain_types": {"slow", "flaky", "costly", "wrong_output", "drift_inconsistency", "lock_in", "cant_debug",
                   "learning_curve", "context_limits", "review_burden", "debt_buildup", "scattered_tools", "none"},
}
CHANNELS = ["ethos", "pathos", "logos", "kairos", "style", "clarity", "focus", "awareness"]


def ws(s):
    return re.sub(r"\s+", " ", s or "").strip()


def check(src, coded_path):
    rows, problems = [], []
    for i, line in enumerate(open(coded_path)):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            problems.append(f"line {i + 1}: not JSON ({e})")
    ids = [r.get("id") for r in rows]
    for missing in [k for k in src if k not in ids]:
        problems.append(f"{missing}: missing")
    for r in rows:
        rid = r.get("id")
        if rid not in src:
            problems.append(f"{rid}: not in batch")
            continue
        for k, allowed in ENUMS.items():
            v = str(r.get(k)).lower() if isinstance(r.get(k), bool) else r.get(k)
            if v not in allowed:
                problems.append(f"{rid}: {k}={r.get(k)!r}")
        for k, allowed in MULTI.items():
            v = r.get(k)
            if not isinstance(v, list) or any(x not in allowed for x in v):
                problems.append(f"{rid}: {k}={v!r}")
        if not isinstance(r.get("relevant"), bool):
            problems.append(f"{rid}: relevant={r.get('relevant')!r}")
        ch = r.get("channels") or {}
        for c in CHANNELS:
            v = ch.get(c)
            if not isinstance(v, (int, float)) or not -1 <= v <= 1:
                problems.append(f"{rid}: channels.{c}={v!r}")
        q = r.get("quote") or ""
        if r.get("relevant") and (not q or ws(q) not in ws(src[rid]["own_text"]) or len(q) > 320):
            problems.append(f"{rid}: quote not an exact substring (or too long): {q[:80]!r}")
    return rows, problems


def main():
    src = {}
    for line in open(sys.argv[1]):
        r = json.loads(line)
        src[r["id"]] = r
    bad = False
    for path in sys.argv[2:]:
        rows, problems = check(src, path)
        print(f"{path}: {len(rows)} rows, {len(problems)} problems")
        for p in problems[:200]:
            print("  ", p)
        bad = bad or bool(problems)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
