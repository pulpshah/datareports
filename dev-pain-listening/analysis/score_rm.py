"""Real rhetorical mass (rm_raw) for each item, from pulp-lambdas rootwords, offline (PROTOCOL.md section 8).

Usage: <venv with spaCy and en_core_web_lg>/python -I analysis/score_rm.py <batch> [pulp-lambdas path]

Scores each item's own words (`own_text`: title plus body for posts, body for comments), never the parent
context. client=None: the mass engine is LLM-free; only the optional proposition axes abstain.
Writes data/coded/rm_batch<N>.jsonl.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAMBDAS = Path(sys.argv[2] if len(sys.argv) > 2 else "/home/user/pulp-lambdas")
sys.path[:0] = [str(LAMBDAS / "src"), str(LAMBDAS / "src" / "lambdas" / "shared")]

from scoring_functions.rootwords.rm.score import score  # noqa: E402
from scoring_functions.rootwords.spacy_loader import get_nlp  # noqa: E402


def main(batch):
    commit = subprocess.run(["git", "-C", str(LAMBDAS), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    nlp = get_nlp()
    out = ROOT / "data" / "coded" / f"rm_batch{batch}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = {json.loads(l)["id"] for l in open(out)} if out.exists() else set()
    t = time.time()
    with open(out, "a") as f:
        for line in open(ROOT / "data" / "sample" / f"batch{batch}.jsonl"):
            r = json.loads(line)
            if r["id"] in done:
                continue
            try:
                res = score(doc_id=r["id"], text=r["own_text"], nlp=nlp).model_dump(mode="json")
                rec = {"id": r["id"], "rm_raw": res["rm_raw"], "coverage": res["coverage"]["value"],
                       "pulp_lambdas": commit}
            except Exception as e:  # recorded, never silently dropped
                rec = {"id": r["id"], "rm_raw": None, "error": repr(e)[:300], "pulp_lambdas": commit}
            f.write(json.dumps(rec) + "\n")
            f.flush()
    print("done", out, round(time.time() - t, 1), "s")


if __name__ == "__main__":
    main(int(sys.argv[1]))
