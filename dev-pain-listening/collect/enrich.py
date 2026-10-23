"""Fetch full text and context for drawn items only (PROTOCOL.md section 6).

Usage: python3 -I collect/enrich.py <batch>

- Discourse: the post's raw text (search returns only a blurb).
- DEV.to: the article body (the list API returns only a description).
- Reddit comments: the parent post's title, as context for the coder.
Writes data/sample/batch<N>.jsonl. Items whose full text cannot be fetched keep their blurb and say so.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "collect"))
import collect  # noqa: E402

MAX_CHARS = 4000


def main(batch):
    rows = [json.loads(l) for l in open(ROOT / "data" / "sample" / "sample.jsonl")]
    rows = [r for r in rows if r["batch"] == batch]
    parents = sorted({r["parent_link"][3:] for r in rows if r.get("parent_link")})
    titles = {}
    for i in range(0, len(parents), 50):
        ids = ",".join(parents[i:i + 50])
        d = collect.get_json(f"{collect.ARCTIC}/posts/ids?ids={ids}&fields=id,title", gap=2.0) or {}
        for p in d.get("data") or []:
            titles[p["id"]] = p.get("title") or ""
    for r in rows:
        if r["src"] == "discourse":
            host = r["community"]
            d = collect.get_json(f"https://{host}/posts/{r['post_id']}.json", gap=1.5)
            if d and d.get("raw"):
                r["text"], r["text_is_blurb"] = d["raw"], False
        elif r["src"] == "devto":
            d = collect.get_json(f"https://dev.to/api/articles/{r['id'].split('_', 1)[1]}", gap=1.0)
            if d and d.get("body_markdown"):
                r["text"], r["text_is_blurb"] = d["body_markdown"], False
        elif r.get("parent_link"):
            r["parent_title"] = titles.get(r["parent_link"][3:], "")
        own = ((r.get("title") or "") + "\n\n" + (r.get("text") or "")).strip() if r["kind"] != "comment" \
            else (r.get("text") or "").strip()
        r["truncated"] = len(own) > MAX_CHARS
        r["own_text"] = own[:MAX_CHARS]
    out = ROOT / "data" / "sample" / f"batch{batch}.jsonl"
    with open(out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("wrote", out, len(rows), "blurbs left:", sum(1 for r in rows if r.get("text_is_blurb")))


if __name__ == "__main__":
    main(int(sys.argv[1]))
